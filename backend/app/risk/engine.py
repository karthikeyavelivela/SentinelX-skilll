import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("vulnguard.risk.engine")


class RiskScoringEngine:
    """
    Composite Risk Score = 
        Exploit Probability × Asset Criticality × Attack Path Weight × 
        Exposure Factor × Business Impact

    All factors normalized to [0, 1] range, final score on [0, 100].
    """

    CRITICALITY_WEIGHTS = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.5,
        "low": 0.2,
    }

    ZONE_EXPOSURE = {
        "external": 1.0,
        "dmz": 0.85,
        "cloud": 0.75,
        "internal": 0.4,
        "restricted": 0.2,
    }

    BUSINESS_IMPACT = {
        "finance": 1.0,
        "engineering": 0.9,
        "executive": 0.95,
        "hr": 0.7,
        "marketing": 0.5,
        "operations": 0.8,
        "it": 0.75,
        "unassigned": 0.3,
    }

    def calculate_risk(
        self,
        exploit_probability: float,
        cvss_score: float,
        asset_criticality: str,
        network_zone: str,
        is_internet_facing: bool,
        business_unit: str,
        vulnerability_count: int = 1,
        has_exploit: bool = False,
        is_kev: bool = False,
    ) -> Dict:
        """Calculate composite risk score with full explainability."""
        
        # Factor 1: Exploit Probability (from ML model or EPSS)
        exploit_factor = min(exploit_probability, 1.0)

        # Factor 2: Asset Criticality
        criticality_factor = self.CRITICALITY_WEIGHTS.get(asset_criticality, 0.5)

        # Factor 3: Attack Path Weight (based on CVSS and vuln count)
        attack_path_factor = (cvss_score / 10) * min(1.0 + (vulnerability_count - 1) * 0.05, 2.0)
        attack_path_factor = min(attack_path_factor, 1.0)

        # Factor 4: Exposure Factor
        base_exposure = self.ZONE_EXPOSURE.get(network_zone, 0.4)
        if is_internet_facing:
            base_exposure = max(base_exposure, 0.9)
        exposure_factor = base_exposure

        # Factor 5: Business Impact
        business_factor = self.BUSINESS_IMPACT.get(business_unit.lower(), 0.3)

        # Bonus: KEV / Exploit availability boost
        urgency_boost = 1.0
        if is_kev:
            urgency_boost += 0.3
        if has_exploit:
            urgency_boost += 0.2
        urgency_boost = min(urgency_boost, 1.5)

        # Composite Score
        raw_score = (
            exploit_factor * 0.30 +
            criticality_factor * 0.20 +
            attack_path_factor * 0.20 +
            exposure_factor * 0.15 +
            business_factor * 0.15
        ) * urgency_boost

        final_score = round(min(raw_score * 100, 100), 2)

        # Risk Level
        if final_score >= 80:
            risk_level = "CRITICAL"
        elif final_score >= 60:
            risk_level = "HIGH"
        elif final_score >= 40:
            risk_level = "MEDIUM"
        elif final_score >= 20:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "breakdown": {
                "exploit_probability": {
                    "value": round(exploit_factor, 4),
                    "weight": 0.30,
                    "contribution": round(exploit_factor * 0.30 * 100, 2),
                },
                "asset_criticality": {
                    "value": round(criticality_factor, 4),
                    "weight": 0.20,
                    "input": asset_criticality,
                    "contribution": round(criticality_factor * 0.20 * 100, 2),
                },
                "attack_path_weight": {
                    "value": round(attack_path_factor, 4),
                    "weight": 0.20,
                    "cvss_score": cvss_score,
                    "vulnerability_count": vulnerability_count,
                    "contribution": round(attack_path_factor * 0.20 * 100, 2),
                },
                "exposure_factor": {
                    "value": round(exposure_factor, 4),
                    "weight": 0.15,
                    "network_zone": network_zone,
                    "is_internet_facing": is_internet_facing,
                    "contribution": round(exposure_factor * 0.15 * 100, 2),
                },
                "business_impact": {
                    "value": round(business_factor, 4),
                    "weight": 0.15,
                    "business_unit": business_unit,
                    "contribution": round(business_factor * 0.15 * 100, 2),
                },
                "urgency_boost": round(urgency_boost, 2),
            },
            "calculated_at": datetime.utcnow().isoformat(),
        }

    def calculate_batch(self, items: List[Dict]) -> List[Dict]:
        """Calculate risk for multiple asset-vulnerability pairs."""
        results = []
        for item in items:
            score = self.calculate_risk(
                exploit_probability=item.get("exploit_probability", 0),
                cvss_score=item.get("cvss_score", 0),
                asset_criticality=item.get("asset_criticality", "medium"),
                network_zone=item.get("network_zone", "internal"),
                is_internet_facing=item.get("is_internet_facing", False),
                business_unit=item.get("business_unit", "unassigned"),
                vulnerability_count=item.get("vulnerability_count", 1),
                has_exploit=item.get("has_exploit", False),
                is_kev=item.get("is_kev", False),
            )
            score["asset_id"] = item.get("asset_id")
            score["cve_id"] = item.get("cve_id")
            results.append(score)
        
        return sorted(results, key=lambda x: x["risk_score"], reverse=True)
