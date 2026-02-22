import asyncio
from app.database import async_session
from sqlalchemy import select
from app.assets.models import Asset

async def test():
    async with async_session() as db:
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
        print([{"business_unit": k, **v} for k, v in heatmap.items()])

asyncio.run(test())
