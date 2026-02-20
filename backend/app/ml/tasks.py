import logging
from sqlalchemy import select
from app.celery_app import celery
from app.database import async_session
from app.ingestion.models import CVE
from app.ml.train import ExploitPredictor
import asyncio

logger = logging.getLogger("vulnguard.ml.tasks")


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery.task(name="app.ml.tasks.retrain_model", bind=True, max_retries=2)
def retrain_model(self):
    """Retrain the exploit prediction model."""
    try:
        return run_async(_retrain())
    except Exception as exc:
        logger.error(f"Retraining failed: {exc}")
        self.retry(countdown=300, exc=exc)


async def _retrain():
    async with async_session() as db:
        result = await db.execute(select(CVE))
        cves = result.scalars().all()

    cve_dicts = [
        {
            "cve_id": c.cve_id,
            "cvss_v3_score": c.cvss_v3_score,
            "epss_score": c.epss_score,
            "epss_percentile": c.epss_percentile,
            "is_kev": c.is_kev,
            "has_public_exploit": c.has_public_exploit,
            "attack_vector": c.attack_vector,
            "attack_complexity": c.attack_complexity,
            "privileges_required": c.privileges_required,
            "user_interaction": c.user_interaction,
            "scope": c.scope,
            "published_date": c.published_date,
            "exploit_maturity": c.exploit_maturity,
            "vendor": c.vendor,
            "references": c.references,
        }
        for c in cves
    ]

    predictor = ExploitPredictor()
    metrics = predictor.train(cve_dicts)

    # Update predictions in database
    if predictor.model is not None:
        async with async_session() as db:
            updated = 0
            for cve_dict in cve_dicts:
                prediction = predictor.predict(cve_dict)
                cve_result = await db.execute(
                    select(CVE).where(CVE.cve_id == cve_dict["cve_id"])
                )
                cve = cve_result.scalar_one_or_none()
                if cve:
                    cve.predicted_exploit_probability = prediction["exploit_probability"]
                    cve.prediction_confidence = prediction["confidence"]
                    updated += 1
            await db.commit()
            metrics["predictions_updated"] = updated

    return metrics


@celery.task(name="app.ml.tasks.predict_single")
def predict_single(cve_data: dict):
    """Predict exploit likelihood for a single CVE."""
    predictor = ExploitPredictor()
    return predictor.predict(cve_data)
