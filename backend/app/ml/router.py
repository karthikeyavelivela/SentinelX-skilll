from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User, UserRole
from app.ingestion.models import CVE
from app.ml.train import ExploitPredictor
from app.ml.tasks import retrain_model
from pydantic import BaseModel
from typing import Dict, List, Optional

router = APIRouter(prefix="/api/ml", tags=["ML Prediction"])

predictor = ExploitPredictor()


class PredictionResponse(BaseModel):
    cve_id: str
    exploit_probability: float
    confidence: float
    risk_level: str
    model_type: str
    key_factors: List[str]


@router.get("/predict/{cve_id}", response_model=PredictionResponse)
async def predict_cve(
    cve_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CVE).where(CVE.cve_id == cve_id))
    cve = result.scalar_one_or_none()
    if not cve:
        from fastapi import HTTPException
        raise HTTPException(404, "CVE not found")

    cve_data = {
        "cve_id": cve.cve_id,
        "cvss_v3_score": cve.cvss_v3_score,
        "epss_score": cve.epss_score,
        "epss_percentile": cve.epss_percentile,
        "is_kev": cve.is_kev,
        "has_public_exploit": cve.has_public_exploit,
        "attack_vector": cve.attack_vector,
        "attack_complexity": cve.attack_complexity,
        "privileges_required": cve.privileges_required,
        "user_interaction": cve.user_interaction,
        "scope": cve.scope,
        "published_date": cve.published_date,
        "exploit_maturity": cve.exploit_maturity,
        "vendor": cve.vendor,
        "references": cve.references,
    }
    prediction = predictor.predict(cve_data)
    prediction["cve_id"] = cve_id
    return prediction


@router.get("/model/metrics")
async def model_metrics(current_user: User = Depends(get_current_user)):
    """Get current model performance metrics."""
    metrics = predictor.get_metrics()
    if not metrics:
        return {
            "status": "no_model",
            "message": "No trained model available. Using heuristic scoring.",
        }
    return metrics


@router.get("/model/feature-importance")
async def feature_importance(current_user: User = Depends(get_current_user)):
    """Get feature importance from the trained model."""
    metrics = predictor.get_metrics()
    return metrics.get("feature_importance", {})


@router.post("/model/retrain")
async def trigger_retrain(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Trigger model retraining."""
    task = retrain_model.delay()
    return {"status": "queued", "task_id": task.id}


@router.get("/predictions/top", response_model=List[PredictionResponse])
async def top_predictions(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get top predicted exploit probabilities."""
    result = await db.execute(
        select(CVE)
        .order_by(CVE.predicted_exploit_probability.desc())
        .limit(limit)
    )
    cves = result.scalars().all()

    predictions = []
    for cve in cves:
        cve_data = {
            "cve_id": cve.cve_id,
            "cvss_v3_score": cve.cvss_v3_score,
            "epss_score": cve.epss_score,
            "is_kev": cve.is_kev,
            "has_public_exploit": cve.has_public_exploit,
            "attack_vector": cve.attack_vector,
            "attack_complexity": cve.attack_complexity,
            "privileges_required": cve.privileges_required,
            "user_interaction": cve.user_interaction,
            "scope": cve.scope,
            "exploit_maturity": cve.exploit_maturity,
            "vendor": cve.vendor,
        }
        pred = predictor.predict(cve_data)
        pred["cve_id"] = cve.cve_id
        predictions.append(pred)

    return sorted(predictions, key=lambda x: x["exploit_probability"], reverse=True)
