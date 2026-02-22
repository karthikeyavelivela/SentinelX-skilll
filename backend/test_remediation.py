import asyncio
from app.database import async_session
from sqlalchemy import select
from app.remediation.models import PatchJob
from app.remediation.schemas import PatchJobResponse

async def test():
    async with async_session() as db:
        result = await db.execute(select(PatchJob).limit(1))
        job = result.scalars().first()
        if job:
            try:
                print(PatchJobResponse.model_validate(job).model_dump())
            except Exception as e:
                print("ValidationError:", e)
        else:
            print("No jobs found")

asyncio.run(test())
