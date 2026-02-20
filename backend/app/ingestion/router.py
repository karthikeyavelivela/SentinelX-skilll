from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User, UserRole
from app.ingestion.models import CVE, Exploit, KEVEntry
from app.ingestion.schemas import (
    CVEResponse, CVEListResponse, ExploitResponse, IngestionStatusResponse,
)
from app.ingestion.tasks import ingest_nvd_cves, ingest_cisa_kev, ingest_epss_scores, search_exploits

router = APIRouter(prefix="/api/cves", tags=["Vulnerability Intelligence"])


@router.get("", response_model=CVEListResponse)
async def list_cves(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    keyword: Optional[str] = None,
    vendor: Optional[str] = None,
    severity: Optional[str] = None,
    min_cvss: Optional[float] = None,
    is_kev: Optional[bool] = None,
    has_exploit: Optional[bool] = None,
    sort_by: str = Query("epss_score", enum=["epss_score", "cvss_v3_score", "predicted_exploit_probability", "published_date"]),
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),
):
    query = select(CVE)

    if keyword:
        query = query.where(
            or_(CVE.cve_id.ilike(f"%{keyword}%"), CVE.description.ilike(f"%{keyword}%"))
        )
    if vendor:
        query = query.where(CVE.vendor.ilike(f"%{vendor}%"))
    if severity:
        query = query.where(CVE.cvss_v3_severity == severity.upper())
    if min_cvss is not None:
        query = query.where(CVE.cvss_v3_score >= min_cvss)
    if is_kev is not None:
        query = query.where(CVE.is_kev == is_kev)
    if has_exploit is not None:
        query = query.where(CVE.has_public_exploit == has_exploit)

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Sort & paginate
    sort_col = getattr(CVE, sort_by, CVE.epss_score)
    query = query.order_by(sort_col.desc()).offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    items = result.scalars().all()

    return CVEListResponse(total=total, page=page, per_page=per_page, items=items)


@router.get("/top-exploitable", response_model=list[CVEResponse])
async def top_exploitable(
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get CVEs most likely to be exploited based on ML prediction."""
    query = (
        select(CVE)
        .order_by(CVE.predicted_exploit_probability.desc(), CVE.epss_score.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{cve_id}", response_model=CVEResponse)
async def get_cve(
    cve_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CVE).where(CVE.cve_id == cve_id))
    cve = result.scalar_one_or_none()
    if not cve:
        from fastapi import HTTPException
        raise HTTPException(404, detail="CVE not found")
    return cve


@router.get("/{cve_id}/exploits", response_model=list[ExploitResponse])
async def get_exploits(
    cve_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Exploit).where(Exploit.cve_id == cve_id))
    return result.scalars().all()


@router.post("/ingest/nvd", response_model=IngestionStatusResponse)
async def trigger_nvd_ingestion(
    days_back: int = Query(7, ge=1, le=90),
    # current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    task = ingest_nvd_cves.delay(days_back=days_back)
    return IngestionStatusResponse(
        source="nvd", status="queued", records_processed=0,
        last_ingested=None, message=f"Task {task.id} queued"
    )


@router.post("/ingest/kev", response_model=IngestionStatusResponse)
async def trigger_kev_ingestion(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    task = ingest_cisa_kev.delay()
    return IngestionStatusResponse(
        source="cisa_kev", status="queued", records_processed=0,
        last_ingested=None, message=f"Task {task.id} queued"
    )


@router.post("/ingest/epss", response_model=IngestionStatusResponse)
async def trigger_epss_ingestion(
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.ANALYST)),
):
    task = ingest_epss_scores.delay()
    return IngestionStatusResponse(
        source="epss", status="queued", records_processed=0,
        last_ingested=None, message=f"Task {task.id} queued"
    )
