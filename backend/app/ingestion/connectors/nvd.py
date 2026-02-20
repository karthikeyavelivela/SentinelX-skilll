import httpx
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

logger = logging.getLogger("vulnguard.nvd")

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class NVDConnector:
    """Connector for NIST National Vulnerability Database API 2.0"""

    def __init__(self):
        self.api_key = settings.NVD_API_KEY
        self.rate_delay = 0.6 if self.api_key else 6.0  # NVD rate limits

    def _headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["apiKey"] = self.api_key
        return headers

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30))
    async def _fetch_page(self, client: httpx.AsyncClient, params: dict) -> dict:
        response = await client.get(
            NVD_BASE_URL, params=params, headers=self._headers(), timeout=60.0
        )
        response.raise_for_status()
        return response.json()

    async def fetch_recent_cves(self, days_back: int = 7, max_results: int = 2000) -> List[dict]:
        """Fetch CVEs modified in the last N days."""
        end = datetime.utcnow()
        start = end - timedelta(days=days_back)

        params = {
            "lastModStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "lastModEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "resultsPerPage": 100,
            "startIndex": 0,
        }

        all_cves = []
        async with httpx.AsyncClient() as client:
            while len(all_cves) < max_results:
                logger.info(f"Fetching NVD page at index {params['startIndex']}")
                data = await self._fetch_page(client, params)
                
                vulns = data.get("vulnerabilities", [])
                if not vulns:
                    break
                
                all_cves.extend(vulns)
                total = data.get("totalResults", 0)
                
                if len(all_cves) >= total:
                    break
                
                params["startIndex"] += len(vulns)
                await asyncio.sleep(self.rate_delay)

        logger.info(f"Fetched {len(all_cves)} CVEs from NVD")
        return all_cves

    async def fetch_cve_by_id(self, cve_id: str) -> Optional[dict]:
        """Fetch a single CVE by ID."""
        params = {"cveId": cve_id}
        async with httpx.AsyncClient() as client:
            data = await self._fetch_page(client, params)
            vulns = data.get("vulnerabilities", [])
            return vulns[0] if vulns else None
