import logging
import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from datetime import datetime
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
)
from sklearn.utils import class_weight
from xgboost import XGBClassifier

from app.ml.feature_engineering import FeatureEngineer

logger = logging.getLogger("vulnguard.ml.train")

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)


class ExploitPredictor:
    """Train and serve exploit likelihood prediction models."""

    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.model = None
        self.model_type = "xgboost"
        self.feature_columns = FeatureEngineer.get_feature_columns()
        self.model_path = os.path.join(MODEL_DIR, "exploit_predictor.joblib")
        self.metrics_path = os.path.join(MODEL_DIR, "model_metrics.json")
        self.metrics = {}
        self._load_model()

    def _load_model(self):
        """Load saved model if exists."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                if os.path.exists(self.metrics_path):
                    with open(self.metrics_path) as f:
                        self.metrics = json.load(f)
                logger.info("Loaded saved exploit prediction model")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")

    def train(self, cve_records: list) -> Dict:
        """Train the exploit prediction model."""
        logger.info(f"Training on {len(cve_records)} CVE records")

        df = self.feature_engineer.build_dataframe(cve_records)
        
        if len(df) < 50:
            logger.warning("Insufficient data for training")
            return {"status": "error", "message": "Need at least 50 records"}

        X = df[self.feature_columns].fillna(0)
        y = df["label"]

        # Handle class imbalance
        positive_count = y.sum()
        negative_count = len(y) - positive_count
        scale_pos_weight = max(negative_count / max(positive_count, 1), 1.0)

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if positive_count >= 5 else None
        )

        # Train XGBoost
        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            use_label_encoder=False,
            eval_metric="auc",
            random_state=42,
            reg_alpha=0.1,
            reg_lambda=1.0,
            min_child_weight=3,
        )

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )

        # Evaluate
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)

        self.metrics = {
            "roc_auc": round(roc_auc_score(y_test, y_pred_proba), 4) if len(np.unique(y_test)) > 1 else 0.0,
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_test, y_pred, zero_division=0), 4),
            "samples_total": len(df),
            "samples_positive": int(positive_count),
            "samples_negative": int(negative_count),
            "trained_at": datetime.utcnow().isoformat(),
            "model_type": self.model_type,
        }

        # Feature importance
        importances = dict(zip(self.feature_columns, self.model.feature_importances_.tolist()))
        self.metrics["feature_importance"] = dict(
            sorted(importances.items(), key=lambda x: x[1], reverse=True)
        )

        # Cross validation
        cv_scores = cross_val_score(self.model, X, y, cv=min(5, max(2, int(len(df) / 20))), scoring="roc_auc")
        self.metrics["cv_roc_auc_mean"] = round(cv_scores.mean(), 4)
        self.metrics["cv_roc_auc_std"] = round(cv_scores.std(), 4)

        # Save
        joblib.dump(self.model, self.model_path)
        with open(self.metrics_path, "w") as f:
            json.dump(self.metrics, f, indent=2)

        logger.info(f"Model trained. ROC-AUC: {self.metrics['roc_auc']}")
        return self.metrics

    def predict(self, cve_data: Dict) -> Dict:
        """Predict exploit likelihood for a single CVE."""
        if self.model is None:
            # Fallback heuristic scoring
            return self._heuristic_predict(cve_data)

        features = self.feature_engineer.extract_features(cve_data)
        X = pd.DataFrame([features])[self.feature_columns].fillna(0)
        
        proba = self.model.predict_proba(X)[0][1]
        
        return {
            "exploit_probability": round(float(proba), 4),
            "confidence": round(float(max(proba, 1 - proba)), 4),
            "risk_level": self._risk_level(proba),
            "model_type": self.model_type,
            "key_factors": self._explain_prediction(features),
        }

    def predict_batch(self, cve_records: list) -> list:
        """Predict for multiple CVEs."""
        results = []
        for cve in cve_records:
            prediction = self.predict(cve)
            prediction["cve_id"] = cve.get("cve_id", "")
            results.append(prediction)
        return sorted(results, key=lambda x: x["exploit_probability"], reverse=True)

    def _heuristic_predict(self, cve_data: Dict) -> Dict:
        """Fallback heuristic when no trained model is available."""
        score = 0.0
        factors = []

        if cve_data.get("is_kev"):
            score += 0.4
            factors.append("Listed in CISA KEV")
        if cve_data.get("has_public_exploit"):
            score += 0.25
            factors.append("Public exploit available")
        
        epss = float(cve_data.get("epss_score", 0))
        score += epss * 0.2
        if epss > 0.5:
            factors.append(f"High EPSS ({epss:.2f})")
        
        cvss = float(cve_data.get("cvss_v3_score", 0))
        score += (cvss / 10) * 0.15
        if cvss >= 9.0:
            factors.append(f"Critical CVSS ({cvss})")

        score = min(score, 1.0)
        
        return {
            "exploit_probability": round(score, 4),
            "confidence": 0.5,
            "risk_level": self._risk_level(score),
            "model_type": "heuristic",
            "key_factors": factors,
        }

    @staticmethod
    def _risk_level(probability: float) -> str:
        if probability >= 0.8:
            return "CRITICAL"
        elif probability >= 0.6:
            return "HIGH"
        elif probability >= 0.4:
            return "MEDIUM"
        elif probability >= 0.2:
            return "LOW"
        return "MINIMAL"

    def _explain_prediction(self, features: Dict) -> list:
        """Generate human-readable explanation of key factors."""
        factors = []
        if features.get("is_kev"):
            factors.append("Listed in CISA KEV catalog")
        if features.get("has_public_exploit"):
            factors.append("Public exploit code available")
        if features.get("epss_score", 0) > 0.5:
            factors.append(f"High EPSS score ({features['epss_score']:.3f})")
        if features.get("cvss_score", 0) >= 9.0:
            factors.append(f"Critical CVSS score ({features['cvss_score']})")
        if features.get("network_exploitable"):
            factors.append("Network-exploitable (no physical access needed)")
        if features.get("no_auth_required"):
            factors.append("No authentication required")
        if features.get("exploit_maturity", 0) >= 2:
            factors.append("Mature/weaponized exploit exists")
        if features.get("is_recent"):
            factors.append("Recently disclosed vulnerability")
        return factors[:5]

    def get_metrics(self) -> Dict:
        return self.metrics
