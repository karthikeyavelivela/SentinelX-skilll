from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User, UserRole
from app.matching.models import VulnerabilityMatch
from app.matching.tasks import run_matching
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/matching", tags=["Vulnerability Matching"])


class MatchResponse(BaseModel):
    id: int
    asset_id: int
    cve_id: str
    software_name: str
    software_version: str
    match_confidence: float
    match_type: str
    cvss_score: float
    status: str

    class Config:
        from_attributes = True


@router.get("/results", response_model=List[MatchResponse])
async def get_match_results(
    asset_id: Optional[int] = None,
    status: Optional[str] = None,
    min_confidence: float = Query(0.5, ge=0, le=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(VulnerabilityMatch).where(
        VulnerabilityMatch.match_confidence >= min_confidence
    )
    if asset_id:
        query = query.where(VulnerabilityMatch.asset_id == asset_id)
    if status:
        query = query.where(VulnerabilityMatch.status == status)
    
    query = query.order_by(VulnerabilityMatch.cvss_score.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/trigger")
async def trigger_matching(
    asset_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    task = run_matching.delay(asset_id=asset_id)
    return {"status": "queued", "task_id": task.id}


@router.get("/stats")
async def matching_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total = (await db.execute(select(func.count(VulnerabilityMatch.id)))).scalar() or 0
    open_count = (await db.execute(
        select(func.count(VulnerabilityMatch.id)).where(VulnerabilityMatch.status == "open")
    )).scalar() or 0
    critical = (await db.execute(
        select(func.count(VulnerabilityMatch.id)).where(VulnerabilityMatch.cvss_score >= 9.0)
    )).scalar() or 0

    return {
        "total_matches": total,
        "open_vulnerabilities": open_count,
        "critical_vulnerabilities": critical,
    }
