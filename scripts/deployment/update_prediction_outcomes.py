"""
Update prediction outcomes by checking actual price movements
Runs periodically to evaluate predictions made 1+ hour ago
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import and_

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import PredictionLog, PriceData

logger = get_logger(__name__)


def update_prediction_outcomes(target_db: str = "neondb_production"):
    """
    Update outcomes for predictions made 1+ hour ago
    
    Args:
        target_db: Database to use (local, neondb_production, neondb_backup)
    """
    
    # Temporarily set active database
    original_db = os.getenv('ACTIVE_DATABASE')
    os.environ['ACTIVE_DATABASE'] = target_db
    
    db = SessionLocal()
    
    try:
        # Get predictions without outcomes that are 1+ hour old
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        pending_predictions = db.query(PredictionLog).filter(
            and_(
                PredictionLog.actual_direction.is_(None),
                PredictionLog.predicted_at <= cutoff_time
            )
        ).all()
        
        logger.info(f"Found {len(pending_predictions)} predictions to evaluate")
        
        if len(pending_predictions) == 0:
            logger.info("No pending predictions to update")
            return 0
        
        updated_count = 0
        
        for pred in pending_predictions:
            try:
                # Get price at prediction time (±5 minutes window)
                pred_price = db.query(PriceData).filter(
                    and_(
                        PriceData.symbol == 'BTC',
                        PriceData.collected_at >= pred.predicted_at - timedelta(minutes=5),
                        PriceData.collected_at <= pred.predicted_at + timedelta(minutes=5)
                    )
                ).order_by(PriceData.collected_at).first()
                
                if not pred_price:
                    logger.warning(f"No price data found for prediction {pred.id} at {pred.predicted_at}")
                    continue
                
                # Get price 1 hour later (±5 minutes window)
                future_time = pred.predicted_at + timedelta(hours=1)
                future_price = db.query(PriceData).filter(
                    and_(
                        PriceData.symbol == 'BTC',
                        PriceData.collected_at >= future_time - timedelta(minutes=5),
                        PriceData.collected_at <= future_time + timedelta(minutes=5)
                    )
                ).order_by(PriceData.collected_at).first()
                
                if not future_price:
                    logger.debug(f"Future price not yet available for prediction {pred.id}")
                    continue
                
                # Calculate actual direction
                price_change = future_price.price_usd - pred_price.price_usd
                actual_direction = 1 if price_change > 0 else 0
                
                # Update prediction record
                pred.actual_direction = actual_direction
                pred.actual_price = future_price.price_usd
                pred.prediction_correct = (pred.prediction == actual_direction)
                
                updated_count += 1
                
                logger.info(
                    f"Updated prediction {pred.id}: "
                    f"Predicted {pred.prediction} ({'UP' if pred.prediction == 1 else 'DOWN'}), "
                    f"Actual {actual_direction} ({'UP' if actual_direction == 1 else 'DOWN'}), "
                    f"{'✓ CORRECT' if pred.prediction_correct else '✗ WRONG'}"
                )
                
                # Commit every 10 predictions
                if updated_count % 10 == 0:
                    db.commit()
                    logger.info(f"Committed {updated_count} updates...")
            
            except Exception as e:
                logger.error(f"Failed to update prediction {pred.id}: {e}")
                continue
        
        # Final commit
        db.commit()
        logger.info(f"✅ Successfully updated {updated_count} prediction outcomes")
        
        return updated_count
        
    except Exception as e:
        logger.error(f"Failed to update outcomes: {e}")
        db.rollback()
        return 0
        
    finally:
        # Restore original database setting
        if original_db:
            os.environ['ACTIVE_DATABASE'] = original_db
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update prediction outcomes')
    parser.add_argument(
        '--db',
        choices=['local', 'neondb_production', 'neondb_backup'],
        default='local',
        help='Database to update (default: local)'
    )
    args = parser.parse_args()
    
    logger.info(f"Starting prediction outcome update for {args.db} database...")
    count = update_prediction_outcomes(target_db=args.db)
    logger.info(f"Completed. Updated {count} predictions.")
    sys.exit(0)