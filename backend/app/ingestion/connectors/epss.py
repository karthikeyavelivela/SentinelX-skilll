import httpx
import csv
import io
import logging
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("vulnguard.epss")

EPSS_URL = "https://epss.cyentia.com/epss_scores-current.csv.gz"
EPSS_API_URL = "https://api.first.org/data/v1/epss"


class EPSSConnector:
    """Connector for FIRST.org EPSS (Exploit Prediction Scoring System)."""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30))
    async def fetch_epss_scores(self, cve_ids: List[str] = None) -> List[Dict]:
        """Fetch EPSS scores. If cve_ids provided, fetch for specific CVEs; else fetch all."""
        results = []

        async with httpx.AsyncClient() as client:
            if cve_ids:
                # Batch query specific CVEs
                for i in range(0, len(cve_ids), 100):
                    batch = cve_ids[i : i + 100]
                    params = {"cve": ",".join(batch)}
                    response = await client.get(EPSS_API_URL, params=params, timeout=30.0)
                    response.raise_for_status()
                    data = response.json()
                    for entry in data.get("data", []):
                        results.append({
                            "cve_id": entry.get("cve", ""),
                            "epss_score": float(entry.get("epss", 0)),
                            "percentile": float(entry.get("percentile", 0)),
                        })
            else:
                # Fetch top scores
                params = {"order": "!epss", "limit": 1000}
                response = await client.get(EPSS_API_URL, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                for entry in data.get("data", []):
                    results.append({
                        "cve_id": entry.get("cve", ""),
                        "epss_score": float(entry.get("epss", 0)),
                        "percentile": float(entry.get("percentile", 0)),
                    })

        logger.info(f"Fetched {len(results)} EPSS scores")
        return results
