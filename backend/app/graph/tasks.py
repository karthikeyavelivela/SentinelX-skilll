import logging
from sqlalchemy import select
from app.celery_app import celery
from app.database import async_session
from app.assets.models import Asset
from app.ingestion.models import CVE
from app.matching.models import VulnerabilityMatch
from app.graph.builder import GraphBuilder
import asyncio

logger = logging.getLogger("vulnguard.graph.tasks")


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery.task(name="app.graph.tasks.rebuild_graph", bind=True, max_retries=2)
def rebuild_graph(self):
    """Rebuild the full attack graph."""
    try:
        return run_async(_rebuild_graph())
    except Exception as exc:
        logger.error(f"Graph rebuild failed: {exc}")
        self.retry(countdown=120, exc=exc)


async def _rebuild_graph():
    async with async_session() as db:
        # Get assets
        result = await db.execute(select(Asset))
        assets = [
            {
                "id": a.id, "hostname": a.hostname, "ip_address": a.ip_address,
                "os_platform": a.os_platform, "criticality": a.criticality.value if a.criticality else "medium",
                "network_zone": a.network_zone.value if a.network_zone else "internal",
                "is_internet_facing": a.is_internet_facing, "risk_score": a.risk_score or 0,
                "business_unit": a.business_unit or "unassigned",
            }
            for a in result.scalars().all()
        ]

        # Get CVEs
        result = await db.execute(select(CVE))
        vulns = [
            {
                "cve_id": c.cve_id, "cvss_score": c.cvss_v3_score or 0,
                "epss_score": c.epss_score or 0, "is_kev": c.is_kev,
                "exploit_probability": c.predicted_exploit_probability or 0,
                "attack_vector": c.attack_vector, "has_exploit": c.has_public_exploit,
                "severity": c.cvss_v3_severity or "MEDIUM",
            }
            for c in result.scalars().all()
        ]

        # Get matches
        result = await db.execute(select(VulnerabilityMatch))
        matches = [
            {
                "asset_id": m.asset_id, "cve_id": m.cve_id,
                "confidence": m.match_confidence, "software_name": m.software_name or "",
            }
            for m in result.scalars().all()
        ]

    builder = GraphBuilder()
    await builder.build_full_graph(assets, vulns, matches)

    return {"assets": len(assets), "vulnerabilities": len(vulns), "matches": len(matches)}
