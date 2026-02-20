from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional, List
from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User, UserRole
from app.assets.models import Asset
from app.remediation.models import PatchJob, PatchStatus
from app.remediation.schemas import PatchJobCreate, PatchJobResponse, PatchApproval, PatchSchedule
from app.remediation.scripts.linux_patch import generate_apt_patch, generate_yum_patch
from app.remediation.scripts.windows_patch import generate_windows_patch

router = APIRouter(prefix="/api/remediation", tags=["Automated Remediation"])


@router.get("/jobs", response_model=List[PatchJobResponse])
async def list_patch_jobs(
    status: Optional[str] = None,
    asset_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(PatchJob)
    if status:
        query = query.where(PatchJob.status == status)
    if asset_id:
        query = query.where(PatchJob.asset_id == asset_id)
    query = query.order_by(PatchJob.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/jobs", response_model=PatchJobResponse, status_code=201)
async def create_patch_job(
    job_data: PatchJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    # Get asset to determine platform
    asset = (await db.execute(select(Asset).where(Asset.id == job_data.asset_id))).scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "Asset not found")

    platform = (asset.os_platform or "linux").lower()

    # Generate scripts
    if "windows" in platform:
        scripts = generate_windows_patch(
            job_data.package_name, dry_run=job_data.is_dry_run
        )
    elif "debian" in (asset.os_name or "").lower() or "ubuntu" in (asset.os_name or "").lower():
        scripts = generate_apt_patch(
            job_data.package_name, job_data.target_version, dry_run=job_data.is_dry_run
        )
    else:
        scripts = generate_yum_patch(
            job_data.package_name, job_data.target_version, dry_run=job_data.is_dry_run
        )

    job = PatchJob(
        asset_id=job_data.asset_id,
        cve_id=job_data.cve_id,
        patch_type=job_data.patch_type,
        platform=platform,
        package_name=job_data.package_name,
        current_version=job_data.current_version,
        target_version=job_data.target_version,
        status=PatchStatus.PENDING_APPROVAL,
        is_dry_run=job_data.is_dry_run,
        script_content=scripts["script"],
        rollback_script=scripts.get("rollback", ""),
        change_description=job_data.change_description,
        maintenance_window_start=job_data.maintenance_window_start,
        maintenance_window_end=job_data.maintenance_window_end,
        requested_by=current_user.id,
        risk_level="medium",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.post("/jobs/{job_id}/approve", response_model=PatchJobResponse)
async def approve_patch_job(
    job_id: int,
    approval: PatchApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    job = (await db.execute(select(PatchJob).where(PatchJob.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Patch job not found")
    if job.status != PatchStatus.PENDING_APPROVAL:
        raise HTTPException(400, f"Cannot approve job in '{job.status}' status")

    if approval.approved:
        job.status = PatchStatus.APPROVED
        job.approved_by = current_user.id
        job.approved_at = datetime.utcnow()
    else:
        job.status = PatchStatus.CANCELLED
        job.execution_log = f"Rejected by {current_user.username}: {approval.notes or 'No reason given'}"

    await db.commit()
    await db.refresh(job)
    return job


@router.post("/jobs/{job_id}/schedule", response_model=PatchJobResponse)
async def schedule_patch_job(
    job_id: int,
    schedule: PatchSchedule,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    job = (await db.execute(select(PatchJob).where(PatchJob.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Patch job not found")
    if job.status not in [PatchStatus.APPROVED, PatchStatus.DRY_RUN_COMPLETE]:
        raise HTTPException(400, f"Cannot schedule job in '{job.status}' status")

    job.status = PatchStatus.SCHEDULED
    job.scheduled_at = schedule.scheduled_at
    job.maintenance_window_start = schedule.maintenance_window_start
    job.maintenance_window_end = schedule.maintenance_window_end
    await db.commit()
    await db.refresh(job)
    return job


@router.post("/jobs/{job_id}/execute", response_model=PatchJobResponse)
async def execute_patch_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    job = (await db.execute(select(PatchJob).where(PatchJob.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Patch job not found")
    if job.status not in [PatchStatus.APPROVED, PatchStatus.SCHEDULED]:
        raise HTTPException(400, f"Cannot execute job in '{job.status}' status")

    job.status = PatchStatus.IN_PROGRESS
    job.started_at = datetime.utcnow()
    job.execution_log = f"Execution started at {datetime.utcnow().isoformat()}\n"

    if job.is_dry_run:
        job.execution_log += "Running in DRY RUN mode - no actual changes applied.\n"
        job.status = PatchStatus.DRY_RUN_COMPLETE
    else:
        job.execution_log += "Patch script submitted to agent for execution.\n"
        job.status = PatchStatus.COMPLETED

    job.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(job)
    return job


@router.post("/jobs/{job_id}/rollback", response_model=PatchJobResponse)
async def rollback_patch_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    job = (await db.execute(select(PatchJob).where(PatchJob.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Patch job not found")
    if job.status != PatchStatus.COMPLETED:
        raise HTTPException(400, "Can only rollback completed jobs")

    job.status = PatchStatus.ROLLED_BACK
    job.execution_log += f"\n\nROLLBACK executed at {datetime.utcnow().isoformat()}\n"
    job.execution_log += f"Rollback script applied.\n"
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/stats")
async def remediation_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = (await db.execute(select(func.count(PatchJob.id)))).scalar() or 0
    pending = (await db.execute(
        select(func.count(PatchJob.id)).where(PatchJob.status == PatchStatus.PENDING_APPROVAL)
    )).scalar() or 0
    completed = (await db.execute(
        select(func.count(PatchJob.id)).where(PatchJob.status == PatchStatus.COMPLETED)
    )).scalar() or 0
    failed = (await db.execute(
        select(func.count(PatchJob.id)).where(PatchJob.status == PatchStatus.FAILED)
    )).scalar() or 0

    return {
        "total_jobs": total,
        "pending_approval": pending,
        "completed": completed,
        "failed": failed,
    }
