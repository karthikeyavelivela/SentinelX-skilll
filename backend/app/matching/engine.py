import logging
from typing import List, Dict, Optional, Tuple
from packaging.version import Version, InvalidVersion
from rapidfuzz import fuzz
from app.matching.cpe_parser import CPEParser
from app.matching.vendor_aliases import get_canonical_vendor, get_canonical_product

logger = logging.getLogger("vulnguard.matching.engine")


class VersionComparator:
    """Semantic version comparison with edge case handling."""

    @staticmethod
    def parse_version(version_str: str) -> Optional[Version]:
        """Parse a version string, handling various formats."""
        if not version_str or version_str == "*":
            return None
        
        # Clean version string
        clean = version_str.strip().lstrip("v").lstrip("V")
        
        # Handle common non-standard formats
        clean = clean.replace("_", ".").replace("-", ".")
        
        # Remove trailing non-numeric parts for comparison
        import re
        match = re.match(r"^(\d+(?:\.\d+)*)", clean)
        if match:
            clean = match.group(1)
        
        try:
            return Version(clean)
        except InvalidVersion:
            return None

    @staticmethod
    def is_vulnerable(installed_version: str, vuln_version_start: str = None,
                      vuln_version_end: str = None, exact_version: str = None) -> bool:
        """Check if installed version falls in vulnerable range."""
        installed = VersionComparator.parse_version(installed_version)
        if not installed:
            return False

        if exact_version:
            exact = VersionComparator.parse_version(exact_version)
            return exact is not None and installed == exact

        if vuln_version_start and vuln_version_end:
            start = VersionComparator.parse_version(vuln_version_start)
            end = VersionComparator.parse_version(vuln_version_end)
            if start and end:
                return start <= installed <= end

        if vuln_version_end:
            end = VersionComparator.parse_version(vuln_version_end)
            if end:
                return installed <= end

        return False


class VulnerabilityMatcher:
    """Matches installed software against known CVEs."""

    def __init__(self):
        self.cpe_parser = CPEParser()
        self.version_cmp = VersionComparator()
        self.fuzzy_threshold = 80

    def match_software_to_cves(
        self, software: Dict, cves: List[Dict]
    ) -> List[Dict]:
        """Match a single software item against a list of CVEs."""
        matches = []
        
        sw_vendor = get_canonical_vendor(software.get("vendor", ""))
        sw_product = get_canonical_product(software.get("name", ""))
        sw_version = software.get("version", "")
        sw_cpe = software.get("cpe", "")

        for cve in cves:
            match_result = self._check_match(
                sw_vendor, sw_product, sw_version, sw_cpe, cve
            )
            if match_result:
                matches.append({
                    "cve_id": cve.get("cve_id"),
                    "confidence": match_result["confidence"],
                    "match_type": match_result["match_type"],
                    "cvss_score": cve.get("cvss_v3_score", 0),
                })

        return sorted(matches, key=lambda x: x["confidence"], reverse=True)

    def _check_match(
        self, sw_vendor: str, sw_product: str, sw_version: str,
        sw_cpe: str, cve: Dict
    ) -> Optional[Dict]:
        """Check if software matches a CVE."""
        
        # 1. Exact CPE match
        if sw_cpe:
            for vuln_cpe_str in cve.get("affected_cpes", []):
                sw_parsed = self.cpe_parser.parse(sw_cpe)
                vuln_parsed = self.cpe_parser.parse(vuln_cpe_str)
                if self.cpe_parser.match_cpe(sw_parsed, vuln_parsed):
                    # Check version
                    vuln_ver = vuln_parsed.get("version")
                    if vuln_ver and vuln_ver != "*":
                        if self.version_cmp.is_vulnerable(sw_version, exact_version=vuln_ver):
                            return {"confidence": 0.98, "match_type": "exact_cpe"}
                    else:
                        return {"confidence": 0.85, "match_type": "cpe_no_version"}

        # 2. Vendor + Product match (normalized)
        cve_vendor = get_canonical_vendor(cve.get("vendor", ""))
        cve_product = get_canonical_product(cve.get("product", ""))

        if cve_vendor and cve_product:
            if sw_vendor == cve_vendor and sw_product == cve_product:
                return {"confidence": 0.80, "match_type": "vendor_product_exact"}

        # 3. Fuzzy matching
        if sw_product and cve_product:
            score = fuzz.ratio(sw_product, cve_product)
            if score >= self.fuzzy_threshold:
                vendor_score = fuzz.ratio(sw_vendor, cve_vendor) if sw_vendor and cve_vendor else 50
                combined = (score * 0.6 + vendor_score * 0.4) / 100
                if combined >= 0.7:
                    return {"confidence": round(combined, 2), "match_type": "fuzzy"}

        return None

    def bulk_match(
        self, software_list: List[Dict], cves: List[Dict]
    ) -> List[Dict]:
        """Match multiple software items against CVEs."""
        all_matches = []
        for sw in software_list:
            matches = self.match_software_to_cves(sw, cves)
            for m in matches:
                m["software_name"] = sw.get("name", "")
                m["software_version"] = sw.get("version", "")
                all_matches.append(m)
        
        return sorted(all_matches, key=lambda x: x["confidence"], reverse=True)
