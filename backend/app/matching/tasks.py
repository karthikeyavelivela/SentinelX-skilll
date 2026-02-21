import logging
from sqlalchemy import select
from app.celery_app import celery
from app.database import async_session
from app.assets.models import Asset, InstalledSoftware
from app.ingestion.models import CVE
from app.matching.models import VulnerabilityMatch
from app.matching.engine import VulnerabilityMatcher
import asyncio

logger = logging.getLogger("vulnguard.matching.tasks")


import threading

def run_async(coro):
    """Helper to run async functions in sync Celery tasks."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        result = None
        error = None
        def target():
            nonlocal result, error
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                result = new_loop.run_until_complete(coro)
            except Exception as e:
                error = e
            finally:
                new_loop.close()

        t = threading.Thread(target=target)
        t.start()
        t.join()
        if error:
            raise error
        return result
    else:
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
@celery.task(name="app.matching.tasks.run_matching", bind=True, max_retries=2)
def run_matching(self, asset_id: int = None):
    """Run vulnerability matching for all or specific assets."""
    try:
        return run_async(_run_matching(asset_id))
    except Exception as exc:
        logger.error(f"Matching failed: {exc}")
        self.retry(countdown=120, exc=exc)


async def _run_matching(asset_id: int = None):
    matcher = VulnerabilityMatcher()

    async with async_session() as db:
        # Get assets
        query = select(Asset)
        if asset_id:
            query = query.where(Asset.id == asset_id)
        assets = (await db.execute(query)).scalars().all()

        # Get all CVEs
        cves_result = await db.execute(select(CVE))
        cves = cves_result.scalars().all()
        cve_dicts = [
            {
                "cve_id": c.cve_id,
                "vendor": c.vendor,
                "product": c.product,
                "affected_cpes": c.affected_cpes or [],
                "cvss_v3_score": c.cvss_v3_score,
            }
            for c in cves
        ]

        total_matches = 0
        for asset in assets:
            # Get installed software for this asset
            sw_result = await db.execute(
                select(InstalledSoftware).where(InstalledSoftware.asset_id == asset.id)
            )
            software = sw_result.scalars().all()
            sw_dicts = [
                {"name": s.name, "vendor": s.vendor, "version": s.version, "cpe": s.cpe}
                for s in software
            ]

            if not sw_dicts:
                continue

            matches = matcher.bulk_match(sw_dicts, cve_dicts)

            for match in matches:
                # Check for existing match
                existing = await db.execute(
                    select(VulnerabilityMatch).where(
                        VulnerabilityMatch.asset_id == asset.id,
                        VulnerabilityMatch.cve_id == match["cve_id"],
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                db.add(VulnerabilityMatch(
                    asset_id=asset.id,
                    cve_id=match["cve_id"],
                    software_name=match.get("software_name", ""),
                    software_version=match.get("software_version", ""),
                    match_confidence=match["confidence"],
                    match_type=match["match_type"],
                    cvss_score=match.get("cvss_score", 0),
                ))
                total_matches += 1

            # Update asset vuln count
            asset.vulnerability_count = len(matches)
            
        await db.commit()

    logger.info(f"Matching complete: {total_matches} new matches found")
    return {"total_matches": total_matches}
