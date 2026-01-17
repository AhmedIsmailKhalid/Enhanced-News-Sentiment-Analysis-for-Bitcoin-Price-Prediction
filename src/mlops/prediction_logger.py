"""
Prediction Logger - MLOps Component
Logs all predictions to database for monitoring, drift detection, and retraining triggers
"""

from datetime import datetime
from typing import Any, Dict, Optional

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import PredictionLog, PriceData  # noqa


class PredictionLogger:
    """
    Log all model predictions for MLOps monitoring and analysis

    Features:
    - Log prediction details with features snapshot
    - Track response times and performance
    - Update with actual outcomes for accuracy tracking
    - Query prediction history for monitoring
    """

    def __init__(self):
        self.logger = get_logger(__name__)

    def log_prediction(
        self,
        feature_set: str,
        model_type: str,
        model_version: str,
        prediction: int,
        probability_down: float,
        probability_up: float,
        confidence: float,
        features: Dict[str, Any],
        response_time_ms: float,
        cached_features: bool,
        bitcoin_price: Optional[float] = None,
    ) -> int:
        """
        Log a single prediction to database

        Args:
            feature_set: 'vader' or 'finbert'
            model_type: Model algorithm used
            model_version: Model version timestamp
            prediction: 0 (down) or 1 (up)
            probability_down: Probability of price going down
            probability_up: Probability of price going up
            confidence: Model confidence score
            features: Dictionary of all features used
            response_time_ms: API response time
            cached_features: Whether cached features were used
            bitcoin_price: Current Bitcoin price (optional)

        Returns:
            Prediction log ID
        """
        db = SessionLocal()

        try:
            # Create prediction log record
            prediction_log = PredictionLog(
                feature_set=feature_set,
                model_type=model_type,
                model_version=model_version,
                prediction=prediction,
                probability_down=probability_down,
                probability_up=probability_up,
                confidence=confidence,
                features_json=features,
                feature_count=len(features),
                bitcoin_price_at_prediction=bitcoin_price,
                response_time_ms=response_time_ms,
                cached_features=cached_features,
                predicted_at=datetime.utcnow(),
            )

            db.add(prediction_log)
            db.commit()
            db.refresh(prediction_log)

            self.logger.debug(
                f"Logged prediction: {feature_set}/{model_type} -> {prediction} "
                f"(confidence: {confidence:.3f})"
            )

            return prediction_log.id

        except Exception as e:
            self.logger.error(f"Failed to log prediction: {e}")
            db.rollback()
            return -1

        finally:
            db.close()

    def update_prediction_outcome(
        self, prediction_id: int, actual_direction: int, bitcoin_price_1h_later: float
    ) -> bool:
        """
        Update prediction log with actual outcome

        Args:
            prediction_id: ID of prediction log to update
            actual_direction: Actual price direction (0=down, 1=up)
            bitcoin_price_1h_later: Bitcoin price 1 hour after prediction

        Returns:
            Success status
        """
        db = SessionLocal()

        try:
            # Get prediction log
            prediction_log = (
                db.query(PredictionLog).filter(PredictionLog.id == prediction_id).first()
            )

            if not prediction_log:
                self.logger.warning(f"Prediction log {prediction_id} not found")
                return False

            # Calculate price change
            if prediction_log.bitcoin_price_at_prediction:
                price_change_pct = (
                    (bitcoin_price_1h_later - prediction_log.bitcoin_price_at_prediction)
                    / prediction_log.bitcoin_price_at_prediction
                ) * 100
            else:
                price_change_pct = None

            # Update with outcome
            prediction_log.actual_direction = actual_direction
            prediction_log.prediction_correct = prediction_log.prediction == actual_direction
            prediction_log.bitcoin_price_1h_later = bitcoin_price_1h_later
            prediction_log.price_change_pct = price_change_pct
            prediction_log.outcome_recorded_at = datetime.utcnow()

            db.commit()

            self.logger.debug(
                f"Updated prediction {prediction_id}: "
                f"predicted={prediction_log.prediction}, actual={actual_direction}, "
                f"correct={prediction_log.prediction_correct}"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to update prediction outcome: {e}")
            db.rollback()
            return False

        finally:
            db.close()

    def get_recent_predictions(
        self,
        feature_set: Optional[str] = None,
        model_type: Optional[str] = None,
        limit: int = 100,
        only_with_outcomes: bool = False,
    ) -> list:
        """
        Get recent predictions for monitoring

        Args:
            feature_set: Filter by feature set (optional)
            model_type: Filter by model type (optional)
            limit: Maximum number of predictions to return
            only_with_outcomes: Only return predictions with recorded outcomes

        Returns:
            List of prediction log dictionaries
        """
        db = SessionLocal()

        try:
            query = db.query(PredictionLog)

            # Apply filters
            if feature_set:
                query = query.filter(PredictionLog.feature_set == feature_set)

            if model_type:
                query = query.filter(PredictionLog.model_type == model_type)

            if only_with_outcomes:
                query = query.filter(PredictionLog.prediction_correct.isnot(None))

            # Order by most recent and limit
            predictions = query.order_by(PredictionLog.predicted_at.desc()).limit(limit).all()

            # Convert to dictionaries
            result = []
            for pred in predictions:
                result.append(
                    {
                        "id": pred.id,
                        "feature_set": pred.feature_set,
                        "model_type": pred.model_type,
                        "model_version": pred.model_version,
                        "prediction": pred.prediction,
                        "probability_down": pred.probability_down,
                        "probability_up": pred.probability_up,
                        "confidence": pred.confidence,
                        "actual_direction": pred.actual_direction,
                        "prediction_correct": pred.prediction_correct,
                        "bitcoin_price_at_prediction": pred.bitcoin_price_at_prediction,
                        "bitcoin_price_1h_later": pred.bitcoin_price_1h_later,
                        "price_change_pct": pred.price_change_pct,
                        "response_time_ms": pred.response_time_ms,
                        "predicted_at": pred.predicted_at.isoformat()
                        if pred.predicted_at
                        else None,
                        "outcome_recorded_at": pred.outcome_recorded_at.isoformat()
                        if pred.outcome_recorded_at
                        else None,
                    }
                )

            return result

        except Exception as e:
            self.logger.error(f"Failed to get recent predictions: {e}")
            return []

        finally:
            db.close()

    def get_model_accuracy(
        self, feature_set: str, model_type: str, days: int = 7
    ) -> Dict[str, Any]:
        """
        Calculate model accuracy over specified time period

        Args:
            feature_set: Feature set to analyze
            model_type: Model type to analyze
            days: Number of days to look back

        Returns:
            Dictionary with accuracy metrics
        """
        db = SessionLocal()

        try:
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Get predictions with outcomes
            predictions = (
                db.query(PredictionLog)
                .filter(
                    PredictionLog.feature_set == feature_set,
                    PredictionLog.model_type == model_type,
                    PredictionLog.predicted_at >= cutoff_date,
                    PredictionLog.prediction_correct.isnot(None),
                )
                .all()
            )

            if not predictions:
                return {
                    "feature_set": feature_set,
                    "model_type": model_type,
                    "total_predictions": 0,
                    "accuracy": None,
                    "message": "No predictions with outcomes in this period",
                }

            # Calculate metrics
            total = len(predictions)
            correct = sum(1 for p in predictions if p.prediction_correct)
            accuracy = correct / total if total > 0 else 0

            # Separate by prediction direction
            up_predictions = [p for p in predictions if p.prediction == 1]
            down_predictions = [p for p in predictions if p.prediction == 0]

            up_correct = sum(1 for p in up_predictions if p.prediction_correct)
            down_correct = sum(1 for p in down_predictions if p.prediction_correct)

            # Calculate average confidence
            avg_confidence = sum(p.confidence for p in predictions) / total
            avg_confidence_correct = (
                sum(p.confidence for p in predictions if p.prediction_correct) / correct
                if correct > 0
                else 0
            )
            avg_confidence_incorrect = (
                sum(p.confidence for p in predictions if not p.prediction_correct)
                / (total - correct)
                if (total - correct) > 0
                else 0
            )

            return {
                "feature_set": feature_set,
                "model_type": model_type,
                "period_days": days,
                "total_predictions": total,
                "correct_predictions": correct,
                "incorrect_predictions": total - correct,
                "accuracy": accuracy,
                "up_predictions": len(up_predictions),
                "up_correct": up_correct,
                "up_accuracy": up_correct / len(up_predictions) if up_predictions else 0,
                "down_predictions": len(down_predictions),
                "down_correct": down_correct,
                "down_accuracy": down_correct / len(down_predictions) if down_predictions else 0,
                "avg_confidence": avg_confidence,
                "avg_confidence_when_correct": avg_confidence_correct,
                "avg_confidence_when_incorrect": avg_confidence_incorrect,
            }

        except Exception as e:
            self.logger.error(f"Failed to calculate model accuracy: {e}")
            return {"error": str(e), "feature_set": feature_set, "model_type": model_type}

        finally:
            db.close()

    def get_prediction_statistics(self) -> Dict[str, Any]:
        """
        Get overall prediction statistics across all models

        Returns:
            Dictionary with overall statistics
        """
        db = SessionLocal()

        try:
            total_predictions = db.query(PredictionLog).count()

            predictions_with_outcomes = (
                db.query(PredictionLog).filter(PredictionLog.prediction_correct.isnot(None)).count()
            )

            correct_predictions = (
                db.query(PredictionLog).filter(PredictionLog.prediction_correct.is_(True)).count()
            )

            # Get statistics by feature set
            vader_total = (
                db.query(PredictionLog).filter(PredictionLog.feature_set == "vader").count()
            )

            finbert_total = (
                db.query(PredictionLog).filter(PredictionLog.feature_set == "finbert").count()
            )

            # Average response time
            avg_response_time = (
                db.query(PredictionLog.response_time_ms)
                .filter(PredictionLog.response_time_ms.isnot(None))
                .all()
            )

            if avg_response_time:
                avg_response_time = sum(r[0] for r in avg_response_time) / len(avg_response_time)
            else:
                avg_response_time = None

            return {
                "total_predictions": total_predictions,
                "predictions_with_outcomes": predictions_with_outcomes,
                "correct_predictions": correct_predictions,
                "overall_accuracy": (
                    correct_predictions / predictions_with_outcomes
                    if predictions_with_outcomes > 0
                    else None
                ),
                "vader_predictions": vader_total,
                "finbert_predictions": finbert_total,
                "avg_response_time_ms": avg_response_time,
                "pending_outcomes": total_predictions - predictions_with_outcomes,
            }

        except Exception as e:
            self.logger.error(f"Failed to get prediction statistics: {e}")
            return {"error": str(e)}

        finally:
            db.close()
