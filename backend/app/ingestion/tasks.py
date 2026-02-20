import logging
from datetime import datetime
from sqlalchemy import select
from app.celery_app import celery
from app.database import async_session
from app.ingestion.models import CVE, KEVEntry, EPSSScore, Exploit
from app.ingestion.connectors.nvd import NVDConnector
from app.ingestion.connectors.cisa_kev import CISAKEVConnector
from app.ingestion.connectors.epss import EPSSConnector
from app.ingestion.connectors.exploitdb import ExploitDBConnector
from app.ingestion.normalizer import normalize_cve_data, parse_datetime
import asyncio

logger = logging.getLogger("vulnguard.ingestion.tasks")


def run_async(coro):
    """Helper to run async functions in sync Celery tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery.task(name="app.ingestion.tasks.ingest_nvd_cves", bind=True, max_retries=3)
def ingest_nvd_cves(self, days_back: int = 7):
    """Ingest CVEs from NVD."""
    try:
        return run_async(_ingest_nvd(days_back))
    except Exception as exc:
        logger.error(f"NVD ingestion failed: {exc}")
        self.retry(countdown=60, exc=exc)


async def _ingest_nvd(days_back: int):
    connector = NVDConnector()
    raw_cves = await connector.fetch_recent_cves(days_back=days_back)

    async with async_session() as db:
        # Get existing CVE IDs
        result = await db.execute(select(CVE.cve_id))
        existing = {row[0] for row in result.fetchall()}

        created, updated = 0, 0
        for raw in raw_cves:
            normalized = normalize_cve_data(raw)
            cve_id = normalized["cve_id"]

            if cve_id in existing:
                # Update existing
                result = await db.execute(select(CVE).where(CVE.cve_id == cve_id))
                cve = result.scalar_one_or_none()
                if cve:
                    for k, v in normalized.items():
                        if v is not None and k != "cve_id":
                            setattr(cve, k, v)
                    updated += 1
            else:
                cve = CVE(**normalized)
                db.add(cve)
                existing.add(cve_id)
                created += 1

        await db.commit()

    msg = f"NVD ingestion complete: {created} created, {updated} updated"
    logger.info(msg)
    return {"source": "nvd", "created": created, "updated": updated}


@celery.task(name="app.ingestion.tasks.ingest_cisa_kev", bind=True, max_retries=3)
def ingest_cisa_kev(self):
    """Ingest CISA KEV catalog."""
    try:
        return run_async(_ingest_kev())
    except Exception as exc:
        logger.error(f"KEV ingestion failed: {exc}")
        self.retry(countdown=60, exc=exc)


async def _ingest_kev():
    connector = CISAKEVConnector()
    entries = await connector.fetch_kev_catalog()

    async with async_session() as db:
        result = await db.execute(select(KEVEntry.cve_id))
        existing = {row[0] for row in result.fetchall()}

        created = 0
        for entry in entries:
            # Parse dates
            entry["date_added"] = parse_datetime(entry.get("date_added"))
            entry["due_date"] = parse_datetime(entry.get("due_date"))

            if entry["cve_id"] not in existing:
                db.add(KEVEntry(**entry))
                existing.add(entry["cve_id"])
                created += 1

            # Also mark in CVE table
            cve_result = await db.execute(select(CVE).where(CVE.cve_id == entry["cve_id"]))
            cve = cve_result.scalar_one_or_none()
            if cve:
                cve.is_kev = True
                cve.kev_date_added = entry["date_added"]

        await db.commit()

    msg = f"KEV ingestion complete: {created} new entries"
    logger.info(msg)
    return {"source": "cisa_kev", "created": created}


@celery.task(name="app.ingestion.tasks.ingest_epss_scores", bind=True, max_retries=3)
def ingest_epss_scores(self):
    """Ingest EPSS scores from FIRST.org."""
    try:
        return run_async(_ingest_epss())
    except Exception as exc:
        logger.error(f"EPSS ingestion failed: {exc}")
        self.retry(countdown=60, exc=exc)


async def _ingest_epss():
    connector = EPSSConnector()

    async with async_session() as db:
        # Get CVE IDs that need EPSS scores
        result = await db.execute(select(CVE.cve_id))
        cve_ids = [row[0] for row in result.fetchall()]

    scores = await connector.fetch_epss_scores(cve_ids[:1000])

    async with async_session() as db:
        updated = 0
        for score_data in scores:
            cve_result = await db.execute(
                select(CVE).where(CVE.cve_id == score_data["cve_id"])
            )
            cve = cve_result.scalar_one_or_none()
            if cve:
                cve.epss_score = score_data["epss_score"]
                cve.epss_percentile = score_data["percentile"]
                updated += 1

            # Also store in EPSS table
            epss_entry = EPSSScore(
                cve_id=score_data["cve_id"],
                epss_score=score_data["epss_score"],
                percentile=score_data["percentile"],
                date=datetime.utcnow(),
            )
            db.add(epss_entry)

        await db.commit()

    msg = f"EPSS ingestion complete: {updated} CVEs updated"
    logger.info(msg)
    return {"source": "epss", "updated": updated}


@celery.task(name="app.ingestion.tasks.search_exploits")
def search_exploits(cve_ids: list):
    """Search for exploits for given CVE IDs."""
    return run_async(_search_exploits(cve_ids))


async def _search_exploits(cve_ids: list):
    connector = ExploitDBConnector()
    exploits = await connector.bulk_search_pocs(cve_ids)

    async with async_session() as db:
        created = 0
        for exploit_data in exploits:
            exploit_data["published_date"] = parse_datetime(exploit_data.get("published_date"))
            
            db.add(Exploit(**exploit_data))
            created += 1

            # Mark CVE as having public exploit
            cve_result = await db.execute(
                select(CVE).where(CVE.cve_id == exploit_data["cve_id"])
            )
            cve = cve_result.scalar_one_or_none()
            if cve:
                cve.has_public_exploit = True
                cve.exploit_maturity = exploit_data.get("maturity", "poc")

        await db.commit()

    return {"source": "exploitdb", "created": created}
