"""
Drift Detection System
Monitors data drift (feature distribution changes) and model drift (performance degradation)
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy import stats

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import FeatureData, PredictionLog


class DriftDetector:
    """
    Detect data drift and model drift for MLOps monitoring

    Features:
    - Statistical tests for feature distribution changes (KS test)
    - Population Stability Index (PSI) for drift severity
    - Model performance degradation detection
    - Confidence calibration monitoring
    - Automated drift alerts
    """

    def __init__(self):
        self.logger = get_logger(__name__)

        # Drift thresholds
        self.ks_test_threshold = 0.05  # p-value threshold for KS test
        self.psi_threshold = 0.2  # PSI > 0.2 indicates significant drift
        self.accuracy_drop_threshold = 0.10  # 10% accuracy drop triggers alert

    def detect_feature_drift(
        self,
        feature_set: str,
        reference_days: int = 7,
        current_days: int = 1,
        target_db: str = "local",
    ) -> Dict[str, Any]:
        """
        Detect data drift by comparing feature distributions

        Args:
            feature_set: 'vader' or 'finbert'
            reference_days: Days to use as reference/baseline period
            current_days: Recent days to compare against baseline
            target_db: Database to query

        Returns:
            Drift detection results with statistical tests
        """
        db = SessionLocal()

        try:
            current_time = datetime.utcnow()
            reference_cutoff = current_time - timedelta(days=reference_days)
            current_cutoff = current_time - timedelta(days=current_days)

            # Get reference period features
            reference_features = (
                db.query(FeatureData)
                .filter(
                    FeatureData.feature_set_name == feature_set,
                    FeatureData.timestamp >= reference_cutoff,
                    FeatureData.timestamp < current_cutoff,
                )
                .all()
            )

            # Get current period features
            current_features = (
                db.query(FeatureData)
                .filter(
                    FeatureData.feature_set_name == feature_set,
                    FeatureData.timestamp >= current_cutoff,
                )
                .all()
            )

            if not reference_features:
                return {
                    "status": "insufficient_data",
                    "message": "No reference data available",
                    "feature_set": feature_set,
                }

            if not current_features:
                return {
                    "status": "insufficient_data",
                    "message": "No current data available",
                    "feature_set": feature_set,
                }

            # Convert to DataFrames
            reference_df = pd.DataFrame([r.features for r in reference_features])
            current_df = pd.DataFrame([c.features for c in current_features])

            # Find common numeric features
            common_features = list(set(reference_df.columns) & set(current_df.columns))
            numeric_features = [
                col for col in common_features if pd.api.types.is_numeric_dtype(reference_df[col])
            ]

            if not numeric_features:
                return {
                    "status": "no_numeric_features",
                    "message": "No numeric features found for drift detection",
                    "feature_set": feature_set,
                }

            # Run drift tests for each feature
            drift_results = []
            significant_drift_count = 0

            for feature in numeric_features:
                ref_values = reference_df[feature].dropna().values
                curr_values = current_df[feature].dropna().values

                if len(ref_values) < 5 or len(curr_values) < 5:
                    continue  # Skip features with insufficient data

                # Kolmogorov-Smirnov test
                ks_statistic, ks_pvalue = stats.ks_2samp(ref_values, curr_values)

                # Population Stability Index (PSI)
                psi_value = self._calculate_psi(ref_values, curr_values)

                # Determine if drift is significant
                drift_detected = (
                    ks_pvalue < self.ks_test_threshold or psi_value > self.psi_threshold
                )

                if drift_detected:
                    significant_drift_count += 1

                drift_results.append(
                    {
                        "feature": feature,
                        "ks_statistic": float(ks_statistic),
                        "ks_pvalue": float(ks_pvalue),
                        "psi": float(psi_value),
                        "drift_detected": drift_detected,
                        "reference_mean": float(np.mean(ref_values)),
                        "current_mean": float(np.mean(curr_values)),
                        "reference_std": float(np.std(ref_values)),
                        "current_std": float(np.std(curr_values)),
                    }
                )

            # Sort by PSI (most drift first)
            drift_results.sort(key=lambda x: x["psi"], reverse=True)

            # Overall drift assessment
            drift_severity = self._assess_drift_severity(drift_results)

            return {
                "status": "success",
                "feature_set": feature_set,
                "reference_period_days": reference_days,
                "current_period_days": current_days,
                "reference_samples": len(reference_features),
                "current_samples": len(current_features),
                "features_tested": len(drift_results),
                "significant_drift_count": significant_drift_count,
                "drift_severity": drift_severity,
                "drift_results": drift_results[:10],  # Top 10 drifted features
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Feature drift detection failed: {e}")
            return {"status": "error", "error": str(e), "feature_set": feature_set}

        finally:
            db.close()

    def detect_model_drift(
        self, feature_set: str, model_type: str, reference_days: int = 7, current_days: int = 1
    ) -> Dict[str, Any]:
        """
        Detect model performance drift

        Args:
            feature_set: 'vader' or 'finbert'
            model_type: Model type to analyze
            reference_days: Days for reference performance
            current_days: Recent days for current performance

        Returns:
            Model drift detection results
        """
        db = SessionLocal()

        try:
            current_time = datetime.utcnow()
            reference_cutoff = current_time - timedelta(days=reference_days)
            current_cutoff = current_time - timedelta(days=current_days)

            # Get reference period predictions (with outcomes)
            reference_predictions = (
                db.query(PredictionLog)
                .filter(
                    PredictionLog.feature_set == feature_set,
                    PredictionLog.model_type == model_type,
                    PredictionLog.predicted_at >= reference_cutoff,
                    PredictionLog.predicted_at < current_cutoff,
                    PredictionLog.prediction_correct.isnot(None),
                )
                .all()
            )

            # Get current period predictions (with outcomes)
            current_predictions = (
                db.query(PredictionLog)
                .filter(
                    PredictionLog.feature_set == feature_set,
                    PredictionLog.model_type == model_type,
                    PredictionLog.predicted_at >= current_cutoff,
                    PredictionLog.prediction_correct.isnot(None),
                )
                .all()
            )

            if not reference_predictions:
                return {
                    "status": "insufficient_data",
                    "message": "No reference predictions with outcomes",
                    "feature_set": feature_set,
                    "model_type": model_type,
                }

            if not current_predictions:
                return {
                    "status": "insufficient_data",
                    "message": "No current predictions with outcomes",
                    "feature_set": feature_set,
                    "model_type": model_type,
                }

            # Calculate reference metrics
            ref_accuracy = sum(1 for p in reference_predictions if p.prediction_correct) / len(
                reference_predictions
            )
            ref_confidence = np.mean([p.confidence for p in reference_predictions])

            # Calculate current metrics
            curr_accuracy = sum(1 for p in current_predictions if p.prediction_correct) / len(
                current_predictions
            )
            curr_confidence = np.mean([p.confidence for p in current_predictions])

            # Detect accuracy drift
            accuracy_drop = ref_accuracy - curr_accuracy
            accuracy_drift_detected = accuracy_drop > self.accuracy_drop_threshold

            # Confidence calibration check
            ref_correct_confidence = np.mean(
                [p.confidence for p in reference_predictions if p.prediction_correct]
            )
            ref_incorrect_confidence = np.mean(
                [p.confidence for p in reference_predictions if not p.prediction_correct]
            )

            curr_correct_confidence = (
                np.mean([p.confidence for p in current_predictions if p.prediction_correct])
                if any(p.prediction_correct for p in current_predictions)
                else 0
            )

            curr_incorrect_confidence = (
                np.mean([p.confidence for p in current_predictions if not p.prediction_correct])
                if any(not p.prediction_correct for p in current_predictions)
                else 0
            )

            # Calibration drift (confidence should be higher when correct)
            ref_calibration_gap = ref_correct_confidence - ref_incorrect_confidence
            curr_calibration_gap = curr_correct_confidence - curr_incorrect_confidence
            calibration_degradation = ref_calibration_gap - curr_calibration_gap

            # Overall drift severity
            if accuracy_drift_detected:
                drift_severity = "high"
            elif accuracy_drop > 0.05 or calibration_degradation > 0.1:
                drift_severity = "medium"
            elif accuracy_drop > 0 or calibration_degradation > 0:
                drift_severity = "low"
            else:
                drift_severity = "none"

            return {
                "status": "success",
                "feature_set": feature_set,
                "model_type": model_type,
                "reference_period_days": reference_days,
                "current_period_days": current_days,
                "reference_predictions": len(reference_predictions),
                "current_predictions": len(current_predictions),
                "accuracy": {
                    "reference": float(ref_accuracy),
                    "current": float(curr_accuracy),
                    "drop": float(accuracy_drop),
                    "drift_detected": accuracy_drift_detected,
                },
                "confidence": {
                    "reference_avg": float(ref_confidence),
                    "current_avg": float(curr_confidence),
                    "reference_calibration_gap": float(ref_calibration_gap),
                    "current_calibration_gap": float(curr_calibration_gap),
                    "calibration_degradation": float(calibration_degradation),
                },
                "drift_severity": drift_severity,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Model drift detection failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "feature_set": feature_set,
                "model_type": model_type,
            }

        finally:
            db.close()

    def _calculate_psi(self, reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
        """
        Calculate Population Stability Index (PSI)

        PSI ranges:
        - < 0.1: No significant change
        - 0.1 - 0.2: Moderate change
        - > 0.2: Significant change (drift detected)
        """
        try:
            # Create bins based on reference distribution
            min_val = min(reference.min(), current.min())
            max_val = max(reference.max(), current.max())

            # Handle edge case where all values are the same
            if min_val == max_val:
                return 0.0

            breakpoints = np.linspace(min_val, max_val, bins + 1)

            # Calculate distributions
            ref_counts, _ = np.histogram(reference, bins=breakpoints)
            curr_counts, _ = np.histogram(current, bins=breakpoints)

            # Convert to proportions (add small epsilon to avoid division by zero)
            epsilon = 1e-10
            ref_proportions = (ref_counts + epsilon) / (len(reference) + epsilon * bins)
            curr_proportions = (curr_counts + epsilon) / (len(current) + epsilon * bins)

            # Calculate PSI
            psi = np.sum(
                (curr_proportions - ref_proportions) * np.log(curr_proportions / ref_proportions)
            )

            return float(psi)

        except Exception as e:
            self.logger.error(f"PSI calculation failed: {e}")
            return 0.0

    def _assess_drift_severity(self, drift_results: List[Dict[str, Any]]) -> str:
        """
        Assess overall drift severity based on individual feature results
        """
        if not drift_results:
            return "unknown"

        # Count features with significant drift
        significant_count = sum(1 for r in drift_results if r["drift_detected"])
        total_features = len(drift_results)
        drift_percentage = significant_count / total_features

        # Get max PSI value
        max_psi = max(r["psi"] for r in drift_results)

        # Assess severity
        if drift_percentage > 0.5 or max_psi > 0.5:
            return "high"
        elif drift_percentage > 0.25 or max_psi > 0.3:
            return "medium"
        elif drift_percentage > 0.1 or max_psi > 0.2:
            return "low"
        else:
            return "none"

    def get_drift_summary(
        self, feature_set: str, model_type: str, reference_days: int = 30, current_days: int = 7
    ):
        """
        Get comprehensive drift summary combining data and model drift

        Args:
            feature_set: 'vader' or 'finbert'
            model_type: Model type to analyze

        Returns:
            Combined drift analysis
        """
        # Detect feature drift
        feature_drift = self.detect_feature_drift(
            feature_set=feature_set, reference_days=7, current_days=1
        )

        # Detect model drift
        model_drift = self.detect_model_drift(
            feature_set=feature_set, model_type=model_type, reference_days=7, current_days=1
        )

        # Determine overall drift status
        feature_severity = feature_drift.get("drift_severity", "unknown")
        model_severity = model_drift.get("drift_severity", "unknown")

        # Overall severity (take the more severe)
        severity_order = ["none", "low", "medium", "high", "unknown"]
        feature_idx = (
            severity_order.index(feature_severity) if feature_severity in severity_order else 0
        )
        model_idx = severity_order.index(model_severity) if model_severity in severity_order else 0
        overall_severity = severity_order[max(feature_idx, model_idx)]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            feature_drift, model_drift, overall_severity
        )

        return {
            "feature_set": feature_set,
            "model_type": model_type,
            "overall_severity": overall_severity,
            "feature_drift": feature_drift,
            "model_drift": model_drift,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _generate_recommendations(
        self, feature_drift: Dict[str, Any], model_drift: Dict[str, Any], overall_severity: str
    ) -> List[str]:
        """Generate actionable recommendations based on drift analysis"""
        recommendations = []

        # Feature drift recommendations
        if feature_drift.get("drift_severity") == "high":
            recommendations.append(
                "HIGH PRIORITY: Significant data drift detected - investigate feature distribution changes"
            )
            recommendations.append("Consider retraining models with recent data")

            # Identify most drifted features
            if feature_drift.get("drift_results"):
                top_drifted = feature_drift["drift_results"][0]
                recommendations.append(
                    f"Feature '{top_drifted['feature']}' shows highest drift (PSI: {top_drifted['psi']:.3f})"
                )

        elif feature_drift.get("drift_severity") == "medium":
            recommendations.append("MEDIUM: Moderate data drift detected - monitor closely")

        # Model drift recommendations
        if model_drift.get("drift_severity") == "high":
            recommendations.append("HIGH PRIORITY: Model performance degradation detected")

            if model_drift.get("accuracy", {}).get("drift_detected"):
                accuracy_drop = model_drift["accuracy"]["drop"]
                recommendations.append(
                    f"Accuracy dropped by {accuracy_drop:.1%} - immediate retraining recommended"
                )

        elif model_drift.get("drift_severity") == "medium":
            recommendations.append("MEDIUM: Model performance declining - schedule retraining soon")

        # General recommendations based on overall severity
        if overall_severity == "high":
            recommendations.append("ACTION REQUIRED: Trigger automated retraining workflow")
            recommendations.append("Alert MLOps team for manual review")
        elif overall_severity == "medium":
            recommendations.append("MONITOR: Continue monitoring, prepare for retraining")
        elif overall_severity == "low":
            recommendations.append(
                "STABLE: System operating normally, routine monitoring sufficient"
            )
        elif overall_severity == "none":
            recommendations.append("OPTIMAL: No drift detected, continue normal operations")

        return (
            recommendations if recommendations else ["No specific recommendations - system stable"]
        )
