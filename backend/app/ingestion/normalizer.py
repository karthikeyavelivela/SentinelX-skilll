import logging
from typing import Optional


logger = logging.getLogger("vulnguard.normalizer")


def normalize_vendor(vendor: str) -> str:
    """Normalize vendor names to canonical form."""
    if not vendor:
        return ""
    vendor = vendor.lower().strip()
    aliases = {
        "microsoft corporation": "microsoft",
        "ms": "microsoft",
        "apache software foundation": "apache",
        "the apache software foundation": "apache",
        "google llc": "google",
        "google inc": "google",
        "google inc.": "google",
        "oracle corporation": "oracle",
        "red hat": "redhat",
        "red hat, inc.": "redhat",
        "canonical ltd.": "canonical",
        "debian project": "debian",
        "linux kernel organization": "linux",
        "apple inc.": "apple",
        "apple inc": "apple",
        "cisco systems": "cisco",
        "cisco systems, inc.": "cisco",
        "ibm corporation": "ibm",
        "vmware, inc.": "vmware",
        "vmware": "vmware",
        "sap se": "sap",
        "adobe systems": "adobe",
        "adobe inc.": "adobe",
        "adobe systems incorporated": "adobe",
        "fortinet, inc.": "fortinet",
        "palo alto networks": "paloalto",
    }
    return aliases.get(vendor, vendor)


from datetime import datetime

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO date string to datetime object."""
    if not dt_str:
        return None
    try:
        # Handle Z suffix for UTC
        if dt_str.endswith("Z"):
            dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


def normalize_cve_data(raw: dict) -> dict:
    """Normalize raw CVE data from NVD format."""
    cve_data = raw.get("cve", raw)
    cve_id = cve_data.get("id", "")
    
    # Description
    descriptions = cve_data.get("descriptions", [])
    desc = next(
        (d["value"] for d in descriptions if d.get("lang") == "en"),
        descriptions[0]["value"] if descriptions else "",
    )

    # CVSS v3
    metrics = cve_data.get("metrics", {})
    cvss_v31 = metrics.get("cvssMetricV31", [{}])
    cvss_v30 = metrics.get("cvssMetricV30", [{}])
    cvss_data = {}
    
    for metric_list in [cvss_v31, cvss_v30]:
        if metric_list:
            m = metric_list[0]
            cvss_inner = m.get("cvssData", {})
            if cvss_inner.get("baseScore"):
                cvss_data = {
                    "cvss_v3_score": cvss_inner.get("baseScore", 0.0),
                    "cvss_v3_vector": cvss_inner.get("vectorString", ""),
                    "cvss_v3_severity": cvss_inner.get("baseSeverity", ""),
                    "attack_vector": cvss_inner.get("attackVector", ""),
                    "attack_complexity": cvss_inner.get("attackComplexity", ""),
                    "privileges_required": cvss_inner.get("privilegesRequired", ""),
                    "user_interaction": cvss_inner.get("userInteraction", ""),
                    "scope": cvss_inner.get("scope", ""),
                }
                break

    # CPE
    configs = cve_data.get("configurations", [])
    cpes = []
    vendor = ""
    product = ""
    for config in configs:
        for node in config.get("nodes", []):
            for match in node.get("cpeMatch", []):
                cpe_str = match.get("criteria", "")
                cpes.append(cpe_str)
                if not vendor and cpe_str:
                    parts = cpe_str.split(":")
                    if len(parts) >= 5:
                        vendor = normalize_vendor(parts[3])
                        product = parts[4]

    # References
    refs = [r.get("url", "") for r in cve_data.get("references", [])]

    return {
        "cve_id": cve_id,
        "description": desc,
        "published_date": parse_datetime(cve_data.get("published")),
        "last_modified_date": parse_datetime(cve_data.get("lastModified")),
        **cvss_data,
        "affected_cpes": cpes,
        "vendor": vendor,
        "product": product,
        "references": refs,
    }


def deduplicate_cve_id(cve_id: str, existing_ids: set) -> bool:
    """Check if CVE already exists."""
    return cve_id in existing_ids
