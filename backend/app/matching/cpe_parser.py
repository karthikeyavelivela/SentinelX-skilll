import re
import logging
from typing import Optional, Tuple
from packaging.version import Version, InvalidVersion

logger = logging.getLogger("vulnguard.cpe_parser")


class CPEParser:
    """Parse CPE 2.3 formatted strings.
    
    CPE format: cpe:2.3:part:vendor:product:version:update:edition:language:sw_edition:target_sw:target_hw:other
    """

    @staticmethod
    def parse(cpe_string: str) -> dict:
        """Parse a CPE 2.3 string into components."""
        if not cpe_string or not cpe_string.startswith("cpe:"):
            return {}

        parts = cpe_string.split(":")
        if len(parts) < 5:
            return {}

        # Pad to 13 elements
        while len(parts) < 13:
            parts.append("*")

        return {
            "part": parts[2],         # a=application, o=OS, h=hardware
            "vendor": parts[3] if parts[3] != "*" else None,
            "product": parts[4] if parts[4] != "*" else None,
            "version": parts[5] if parts[5] != "*" else None,
            "update": parts[6] if parts[6] != "*" else None,
            "edition": parts[7] if parts[7] != "*" else None,
            "language": parts[8] if parts[8] != "*" else None,
            "sw_edition": parts[9] if parts[9] != "*" else None,
            "target_sw": parts[10] if parts[10] != "*" else None,
            "target_hw": parts[11] if parts[11] != "*" else None,
            "other": parts[12] if parts[12] != "*" else None,
            "raw": cpe_string,
        }

    @staticmethod
    def build_cpe(vendor: str, product: str, version: str = "*", part: str = "a") -> str:
        """Build a CPE 2.3 string from components."""
        vendor = vendor.lower().replace(" ", "_").replace("-", "_")
        product = product.lower().replace(" ", "_").replace("-", "_")
        return f"cpe:2.3:{part}:{vendor}:{product}:{version}:*:*:*:*:*:*:*"

    @staticmethod
    def match_cpe(asset_cpe: dict, vuln_cpe: dict) -> bool:
        """Check if an asset CPE matches a vulnerability CPE."""
        if not asset_cpe or not vuln_cpe:
            return False

        # Check part, vendor, product
        for field in ["part", "vendor", "product"]:
            asset_val = (asset_cpe.get(field) or "").lower()
            vuln_val = (vuln_cpe.get(field) or "").lower()
            if vuln_val and vuln_val != "*" and asset_val != vuln_val:
                return False

        return True
