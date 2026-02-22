from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.assets.models import Asset
from app.ingestion.models import CVE
from app.matching.models import VulnerabilityMatch
from app.risk.engine import RiskScoringEngine
from app.risk.models import RiskScore
from typing import Optional

router = APIRouter(prefix="/api/risk", tags=["Risk Scoring"])

risk_engine = RiskScoringEngine()


@router.get("/scores")
async def get_risk_scores(
    business_unit: Optional[str] = None,
    min_score: float = Query(0, ge=0, le=100),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get risk scores ordered by severity."""
    query = select(RiskScore).where(RiskScore.risk_score >= min_score)
    query = query.order_by(RiskScore.risk_score.desc()).limit(limit)
    result = await db.execute(query)
    scores = result.scalars().all()
    
    return [
        {
            "asset_id": s.asset_id,
            "cve_id": s.cve_id,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "breakdown": s.breakdown_json,
            "calculated_at": s.calculated_at,
        }
        for s in scores
    ]


@router.get("/asset/{asset_id}")
async def asset_risk_detail(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed risk breakdown for an asset."""
    # Get asset
    asset_result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = asset_result.scalar_one_or_none()
    if not asset:
        from fastapi import HTTPException
        raise HTTPException(404, "Asset not found")

    # Get matched vulns
    matches = await db.execute(
        select(VulnerabilityMatch).where(VulnerabilityMatch.asset_id == asset_id)
    )
    match_list = matches.scalars().all()

    # Calculate risk for each match
    scored_vulns = []
    for m in match_list:
        cve_result = await db.execute(select(CVE).where(CVE.cve_id == m.cve_id))
        cve = cve_result.scalar_one_or_none()
        if cve:
            score = risk_engine.calculate_risk(
                exploit_probability=cve.predicted_exploit_probability or cve.epss_score or 0,
                cvss_score=cve.cvss_v3_score or 0,
                asset_criticality=(asset.criticality.value if hasattr(asset.criticality, 'value') else asset.criticality) if asset.criticality else "medium",
                network_zone=(asset.network_zone.value if hasattr(asset.network_zone, 'value') else asset.network_zone) if asset.network_zone else "internal",
                is_internet_facing=asset.is_internet_facing,
                business_unit=asset.business_unit or "unassigned",
                vulnerability_count=len(match_list),
                has_exploit=cve.has_public_exploit,
                is_kev=cve.is_kev,
            )
            score["cve_id"] = cve.cve_id
            score["cve_description"] = (cve.description or "")[:200]
            scored_vulns.append(score)

    scored_vulns.sort(key=lambda x: x["risk_score"], reverse=True)

    return {
        "asset_id": asset.id,
        "hostname": asset.hostname,
        "overall_risk_score": scored_vulns[0]["risk_score"] if scored_vulns else 0,
        "overall_risk_level": scored_vulns[0]["risk_level"] if scored_vulns else "MINIMAL",
        "vulnerability_risks": scored_vulns,
        "total_vulnerabilities": len(scored_vulns),
    }


@router.get("/heatmap")
async def risk_heatmap(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get risk heatmap data grouped by business unit."""
    result = await db.execute(select(Asset))
    assets = result.scalars().all()

    heatmap = {}
    for asset in assets:
        bu = asset.business_unit or "unassigned"
        if bu not in heatmap:
            heatmap[bu] = {"critical": 0, "high": 0, "medium": 0, "low": 0, "total_assets": 0}
        
        heatmap[bu]["total_assets"] += 1
        score = asset.risk_score or 0
        if score >= 80:
            heatmap[bu]["critical"] += 1
        elif score >= 60:
            heatmap[bu]["high"] += 1
        elif score >= 40:
            heatmap[bu]["medium"] += 1
        else:
            heatmap[bu]["low"] += 1

    return [{"business_unit": k, **v} for k, v in heatmap.items()]


@router.get("/calculate")
async def calculate_all_risks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recalculate all risk scores."""
    # Get all assets with their matches
    assets = (await db.execute(select(Asset))).scalars().all()
    total_calculated = 0

    for asset in assets:
        matches = (await db.execute(
            select(VulnerabilityMatch).where(VulnerabilityMatch.asset_id == asset.id)
        )).scalars().all()

        max_score = 0
        for m in matches:
            cve = (await db.execute(select(CVE).where(CVE.cve_id == m.cve_id))).scalar_one_or_none()
            if not cve:
                continue

            result = risk_engine.calculate_risk(
                exploit_probability=cve.predicted_exploit_probability or cve.epss_score or 0,
                cvss_score=cve.cvss_v3_score or 0,
                asset_criticality=(asset.criticality.value if hasattr(asset.criticality, 'value') else asset.criticality) if asset.criticality else "medium",
                network_zone=(asset.network_zone.value if hasattr(asset.network_zone, 'value') else asset.network_zone) if asset.network_zone else "internal",
                is_internet_facing=asset.is_internet_facing,
                business_unit=asset.business_unit or "unassigned",
                vulnerability_count=len(matches),
                has_exploit=cve.has_public_exploit,
                is_kev=cve.is_kev,
            )

            # Store individual risk score
            risk_entry = RiskScore(
                asset_id=asset.id,
                cve_id=cve.cve_id,
                risk_score=result["risk_score"],
                risk_level=result["risk_level"],
                breakdown_json=result["breakdown"],
            )
            db.add(risk_entry)
            max_score = max(max_score, result["risk_score"])
            total_calculated += 1

        asset.risk_score = max_score

    await db.commit()
    return {"total_calculated": total_calculated}
