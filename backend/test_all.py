import asyncio
from app.database import async_session
from sqlalchemy import select
from app.assets.models import Asset
from app.remediation.models import PatchJob
from app.remediation.schemas import PatchJobResponse
from app.risk.router import risk_heatmap
from app.ml.router import top_predictions

async def test_all():
    async with async_session() as db:
        print("--- Testing /api/remediation/jobs logic ---")
        jobs = (await db.execute(select(PatchJob).limit(1))).scalars().all()
        if jobs:
            try:
                print("Job Validates:", PatchJobResponse.model_validate(jobs[0]).model_dump()["id"])
            except Exception as e:
                print("Jobs Exception:", e)
        else:
            print("No jobs to validate")
        
        print("\n--- Testing /api/risk/heatmap logic ---")
        try:
            hm = await risk_heatmap(db=db, current_user=None)
            print("Heatmap records:", len(hm))
        except Exception as e:
            print("Heatmap Exception:", e)

        print("\n--- Testing /api/ml/predictions/top logic ---")
        try:
            preds = await top_predictions(limit=1, db=db, current_user=None)
            if preds:
                print("Predictions returned: Top Exploit Risk:", preds[0].get("exploit_probability"))
        except Exception as e:
            print("Predictions Exception:", e)

asyncio.run(test_all())
