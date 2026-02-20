import httpx
import logging
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("vulnguard.cisa_kev")

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


class CISAKEVConnector:
    """Connector for CISA Known Exploited Vulnerabilities catalog."""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30))
    async def fetch_kev_catalog(self) -> List[dict]:
        """Fetch the full KEV catalog."""
        async with httpx.AsyncClient() as client:
            response = await client.get(KEV_URL, timeout=30.0)
            response.raise_for_status()
            data = response.json()

        vulnerabilities = data.get("vulnerabilities", [])
        logger.info(f"Fetched {len(vulnerabilities)} KEV entries from CISA")

        results = []
        for v in vulnerabilities:
            results.append({
                "cve_id": v.get("cveID", ""),
                "vendor_project": v.get("vendorProject", ""),
                "product": v.get("product", ""),
                "vulnerability_name": v.get("vulnerabilityName", ""),
                "date_added": v.get("dateAdded"),
                "short_description": v.get("shortDescription", ""),
                "required_action": v.get("requiredAction", ""),
                "due_date": v.get("dueDate"),
                "known_ransomware_use": v.get("knownRansomwareCampaignUse", "Unknown"),
                "notes": v.get("notes", ""),
            })
        
        return results
