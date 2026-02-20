import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("vulnguard.ml.features")


class FeatureEngineer:
    """Extract ML features from CVE data for exploit prediction."""

    # Attack vector encoding
    ATTACK_VECTOR_MAP = {"NETWORK": 4, "ADJACENT_NETWORK": 3, "LOCAL": 2, "PHYSICAL": 1}
    COMPLEXITY_MAP = {"LOW": 2, "HIGH": 1}
    PRIVILEGES_MAP = {"NONE": 3, "LOW": 2, "HIGH": 1}
    INTERACTION_MAP = {"NONE": 2, "REQUIRED": 1}
    SCOPE_MAP = {"CHANGED": 2, "UNCHANGED": 1}

    POPULAR_VENDORS = {
        "microsoft", "google", "apple", "apache", "oracle", "cisco",
        "adobe", "linux", "redhat", "vmware", "sap", "ibm", "fortinet",
        "paloalto", "f5", "citrix", "atlassian", "wordpress", "php",
    }

    def extract_features(self, cve_data: Dict) -> Dict[str, float]:
        """Extract numerical features from a single CVE record."""
        features = {}

        # Base metrics
        features["cvss_score"] = float(cve_data.get("cvss_v3_score", 0))
        features["epss_score"] = float(cve_data.get("epss_score", 0))
        features["epss_percentile"] = float(cve_data.get("epss_percentile", 0))

        # Binary flags
        features["is_kev"] = 1.0 if cve_data.get("is_kev") else 0.0
        features["has_public_exploit"] = 1.0 if cve_data.get("has_public_exploit") else 0.0

        # Attack vector encoding
        features["attack_vector"] = self.ATTACK_VECTOR_MAP.get(
            (cve_data.get("attack_vector") or "").upper(), 0
        )
        features["attack_complexity"] = self.COMPLEXITY_MAP.get(
            (cve_data.get("attack_complexity") or "").upper(), 0
        )
        features["privileges_required"] = self.PRIVILEGES_MAP.get(
            (cve_data.get("privileges_required") or "").upper(), 0
        )
        features["user_interaction"] = self.INTERACTION_MAP.get(
            (cve_data.get("user_interaction") or "").upper(), 0
        )
        features["scope"] = self.SCOPE_MAP.get(
            (cve_data.get("scope") or "").upper(), 0
        )

        # Time-based features
        published = cve_data.get("published_date")
        if published:
            if isinstance(published, str):
                try:
                    published = datetime.fromisoformat(published.replace("Z", "+00:00"))
                except:
                    published = None
            if published:
                days_since = (datetime.utcnow() - published.replace(tzinfo=None)).days
                features["days_since_disclosure"] = float(max(days_since, 0))
                features["is_recent"] = 1.0 if days_since <= 30 else 0.0
            else:
                features["days_since_disclosure"] = 365.0
                features["is_recent"] = 0.0
        else:
            features["days_since_disclosure"] = 365.0
            features["is_recent"] = 0.0

        # Exploit maturity encoding
        maturity = (cve_data.get("exploit_maturity") or "none").lower()
        features["exploit_maturity"] = {"none": 0, "poc": 1, "functional": 2, "weaponized": 3}.get(maturity, 0)

        # Vendor popularity
        vendor = (cve_data.get("vendor") or "").lower()
        features["vendor_popularity"] = 1.0 if vendor in self.POPULAR_VENDORS else 0.0

        # Reference count (proxy for attention)
        refs = cve_data.get("references", [])
        features["reference_count"] = float(len(refs) if isinstance(refs, list) else 0)

        # Network exposure potential
        features["network_exploitable"] = 1.0 if features["attack_vector"] >= 3 else 0.0
        features["no_auth_required"] = 1.0 if features["privileges_required"] >= 3 else 0.0

        # Composite risk indicators
        features["ease_of_exploit"] = (
            features["attack_vector"] * 0.3 +
            features["attack_complexity"] * 0.2 +
            features["privileges_required"] * 0.2 +
            features["user_interaction"] * 0.15 +
            features["network_exploitable"] * 0.15
        )

        return features

    def build_dataframe(self, cve_records: List[Dict]) -> pd.DataFrame:
        """Build a feature DataFrame from CVE records."""
        rows = []
        for cve in cve_records:
            features = self.extract_features(cve)
            features["cve_id"] = cve.get("cve_id", "")
            features["label"] = 1.0 if cve.get("is_kev") else 0.0  # Ground truth
            rows.append(features)

        df = pd.DataFrame(rows)
        return df

    @staticmethod
    def get_feature_columns() -> List[str]:
        return [
            "cvss_score", "epss_score", "epss_percentile",
            "is_kev", "has_public_exploit",
            "attack_vector", "attack_complexity", "privileges_required",
            "user_interaction", "scope",
            "days_since_disclosure", "is_recent",
            "exploit_maturity", "vendor_popularity", "reference_count",
            "network_exploitable", "no_auth_required", "ease_of_exploit",
        ]
