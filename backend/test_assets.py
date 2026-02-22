import asyncio
from app.database import async_session
from sqlalchemy import select
from app.assets.models import Asset

async def test():
    async with async_session() as db:
        result = await db.execute(select(Asset).limit(2))
        assets = result.scalars().all()
        for a in assets:
            print(f"Asset ID: {a.id}, Criticality: {a.criticality}")

asyncio.run(test())
