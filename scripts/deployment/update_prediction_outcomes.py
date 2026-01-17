"""
Update Prediction Outcomes - Standalone Script
Checks predictions made 1+ hours ago and updates their outcomes based on actual Bitcoin price movement
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import func

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import PredictionLog, PriceData

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


logger = get_logger(__name__)


def get_bitcoin_price_at_time(db, target_time: datetime) -> Optional[float]:
    """
    Get Bitcoin price closest to target time

    Args:
        db: Database session
        target_time: Target datetime (timezone-aware)

    Returns:
        Bitcoin price or None if not found
    """
    try:
        # Ensure target_time is timezone-aware (UTC)
        if target_time.tzinfo is None:
            target_time = target_time.replace(tzinfo=timezone.utc)

        # Find price data within ±10 minutes of target time
        time_buffer = timedelta(minutes=10)
        start_time = target_time - time_buffer
        end_time = target_time + time_buffer

        # Query using collected_at (not timestamp!)
        price_data = (
            db.query(PriceData)
            .filter(
                PriceData.symbol == "BTC",
                PriceData.collected_at >= start_time,
                PriceData.collected_at <= end_time,
            )
            .order_by(func.abs(func.extract("epoch", PriceData.collected_at - target_time)))
            .first()
        )

        if price_data:
            logger.debug(f"Found price {price_data.price_usd} at {price_data.collected_at}")
            return price_data.price_usd

        # If no match within window, get closest before
        closest_before = (
            db.query(PriceData)
            .filter(PriceData.symbol == "BTC", PriceData.collected_at <= target_time)
            .order_by(PriceData.collected_at.desc())
            .first()
        )

        if closest_before:
            time_diff = abs((target_time - closest_before.collected_at).total_seconds())
            # Only use if within 30 minutes
            if time_diff <= 1800:
                logger.debug(
                    f"Using closest before: {closest_before.price_usd} at {closest_before.collected_at} "
                    f"({time_diff/60:.1f} minutes away)"
                )
                return closest_before.price_usd

        # If no match before, get closest after
        closest_after = (
            db.query(PriceData)
            .filter(PriceData.symbol == "BTC", PriceData.collected_at >= target_time)
            .order_by(PriceData.collected_at.asc())
            .first()
        )

        if closest_after:
            time_diff = abs((closest_after.collected_at - target_time).total_seconds())
            # Only use if within 30 minutes
            if time_diff <= 1800:
                logger.debug(
                    f"Using closest after: {closest_after.price_usd} at {closest_after.collected_at} "
                    f"({time_diff/60:.1f} minutes away)"
                )
                return closest_after.price_usd

        logger.warning(f"No price data found within 30 minutes of {target_time}")
        return None

    except Exception as e:
        logger.error(f"Failed to get Bitcoin price at {target_time}: {e}")
        import traceback

        traceback.print_exc()
        return None


def update_prediction_outcome(db, prediction: PredictionLog) -> bool:
    """
    Update a single prediction with its actual outcome

    Args:
        db: Database session
        prediction: PredictionLog to update

    Returns:
        Success status
    """
    try:
        # Ensure predicted_at is timezone-aware
        predicted_at = prediction.predicted_at
        if predicted_at.tzinfo is None:
            predicted_at = predicted_at.replace(tzinfo=timezone.utc)

        # Calculate target time (1 hour after prediction)
        target_time = predicted_at + timedelta(hours=1)

        # Get Bitcoin price 1 hour later
        bitcoin_price_1h_later = get_bitcoin_price_at_time(db, target_time)

        if bitcoin_price_1h_later is None:
            logger.warning(
                f"No Bitcoin price data found for prediction {prediction.id} "
                f"at target time {target_time}"
            )
            return False

        # Get initial price
        initial_price = prediction.bitcoin_price_at_prediction

        if initial_price is None:
            logger.warning(f"Prediction {prediction.id} has no initial price")
            return False

        # Calculate actual direction
        price_change = bitcoin_price_1h_later - initial_price
        actual_direction = 1 if price_change > 0 else 0  # 1=UP, 0=DOWN

        # Calculate price change percentage
        price_change_pct = (price_change / initial_price) * 100

        # Determine if prediction was correct
        prediction_correct = prediction.prediction == actual_direction

        # Update prediction log
        prediction.actual_direction = actual_direction
        prediction.prediction_correct = prediction_correct
        prediction.bitcoin_price_1h_later = bitcoin_price_1h_later
        prediction.price_change_pct = price_change_pct
        prediction.outcome_recorded_at = datetime.now(timezone.utc)

        db.commit()

        result = "✓" if prediction_correct else "✗"
        logger.info(
            f"{result} Prediction {prediction.id}: "
            f"Predicted={'UP' if prediction.prediction == 1 else 'DOWN'}, "
            f"Actual={'UP' if actual_direction == 1 else 'DOWN'}, "
            f"Price: ${initial_price:.2f} → ${bitcoin_price_1h_later:.2f} "
            f"({price_change_pct:+.2f}%)"
        )

        return True

    except Exception as e:
        logger.error(f"Failed to update prediction {prediction.id}: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
        return False


def update_all_pending_outcomes(hours_threshold: int = 1):
    """
    Update all predictions that are older than threshold and don't have outcomes

    Args:
        hours_threshold: Minimum age in hours for predictions to update
    """
    db = SessionLocal()

    try:
        # Calculate cutoff time (timezone-aware UTC)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_threshold)

        logger.info(f"Searching for predictions made before {cutoff_time}")

        # Find predictions without outcomes that are old enough
        pending_predictions = (
            db.query(PredictionLog)
            .filter(
                PredictionLog.predicted_at < cutoff_time, PredictionLog.prediction_correct.is_(None)
            )
            .order_by(PredictionLog.predicted_at.desc())
            .all()
        )

        logger.info(f"Found {len(pending_predictions)} pending predictions to update")

        if not pending_predictions:
            logger.info("No pending predictions to update")
            return

        # Update each prediction
        success_count = 0
        skip_count = 0

        for i, prediction in enumerate(pending_predictions, 1):
            logger.info(f"\n[{i}/{len(pending_predictions)}] Processing Prediction {prediction.id}")
            logger.info(f"  Predicted at: {prediction.predicted_at}")
            logger.info(f"  Model: {prediction.feature_set}/{prediction.model_type}")
            logger.info(f"  Prediction: {'UP' if prediction.prediction == 1 else 'DOWN'}")

            if update_prediction_outcome(db, prediction):
                success_count += 1
            else:
                skip_count += 1

        logger.info("\n" + "=" * 60)
        logger.info("Summary:")
        logger.info(f"  Total processed: {len(pending_predictions)}")
        logger.info(f"  Successfully updated: {success_count}")
        logger.info(f"  Skipped (no data): {skip_count}")

        if success_count > 0:
            accuracy = (success_count / len(pending_predictions)) * 100
            logger.info(f"  Update success rate: {accuracy:.1f}%")

        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Failed to update pending outcomes: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Prediction Outcome Updater")
    logger.info("=" * 60)

    update_all_pending_outcomes(hours_threshold=1)

    logger.info("\nPrediction Outcome Updater Completed")
