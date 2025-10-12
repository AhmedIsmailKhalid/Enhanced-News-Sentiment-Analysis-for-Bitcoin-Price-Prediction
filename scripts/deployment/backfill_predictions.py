"""
Backfill predictions for all existing feature sets
Generates predictions for historical feature data
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import text

from src.mlops.prediction_logger import PredictionLogger
from src.serving.prediction_pipeline import PredictionPipeline
from src.shared.database import SessionLocal
from src.shared.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

def backfill_predictions(target_db: str = "neondb_production"):
    """
    Generate predictions for all existing feature records
    """
    
    logger.info("=" * 60)
    logger.info("Backfilling Predictions for All Feature Sets")
    logger.info("=" * 60)
    
    # Initialize components
    pipeline = PredictionPipeline(target_db=target_db)
    pred_logger = PredictionLogger()
    
    # Get all feature timestamps
    db = SessionLocal() if target_db == "local" else get_neondb_session()
    
    try:
        # Get all VADER feature timestamps
        logger.info("\n→ Loading VADER feature timestamps...")
        vader_query = text("""
            SELECT timestamp, features
            FROM feature_data
            WHERE feature_set_name = 'vader'
            ORDER BY timestamp ASC
        """)
        vader_features = db.execute(vader_query).fetchall()
        logger.info(f"Found {len(vader_features)} VADER feature records")
        
        # Get all FinBERT feature timestamps
        logger.info("\n→ Loading FinBERT feature timestamps...")
        finbert_query = text("""
            SELECT timestamp, features
            FROM feature_data
            WHERE feature_set_name = 'finbert'
            ORDER BY timestamp ASC
        """)
        finbert_features = db.execute(finbert_query).fetchall()
        logger.info(f"Found {len(finbert_features)} FinBERT feature records")
        
        # Generate VADER predictions
        logger.info("\n→ Generating VADER predictions...")
        vader_count = 0
        vader_errors = 0
        
        for i, (timestamp, features) in enumerate(vader_features, 1):
            try:
                # Make prediction
                result = pipeline.predict(
                    feature_set='vader',
                    model_type='random_forest',
                    use_cached_features=True
                )
                
                if result['success']:
                    # Log prediction
                    pred_logger.log_prediction(
                        feature_set='vader',
                        model_type='random_forest',
                        model_version=result['model_info']['model_version'],
                        prediction=result['prediction']['direction_numeric'],
                        probability_down=result['prediction']['probability']['down'],
                        probability_up=result['prediction']['probability']['up'],
                        confidence=result['prediction']['confidence'],
                        features=features,
                        response_time_ms=0,  # Backfilled
                        cached_features=True,
                        bitcoin_price=features.get('price_usd'),
                        timestamp_override=timestamp  # Use feature timestamp
                    )
                    vader_count += 1
                    
                    if i % 50 == 0:
                        logger.info(f"  Generated {i}/{len(vader_features)} VADER predictions")
                else:
                    vader_errors += 1
                    logger.warning(f"  Failed to generate prediction for timestamp {timestamp}")
                    
            except Exception as e:
                vader_errors += 1
                logger.error(f"  Error at {timestamp}: {e}")
        
        logger.info(f"✓ VADER: {vader_count} predictions generated, {vader_errors} errors")
        
        # Generate FinBERT predictions
        logger.info("\n→ Generating FinBERT predictions...")
        finbert_count = 0
        finbert_errors = 0
        
        for i, (timestamp, features) in enumerate(finbert_features, 1):
            try:
                # Make prediction
                result = pipeline.predict(
                    feature_set='finbert',
                    model_type='random_forest',
                    use_cached_features=True
                )
                
                if result['success']:
                    # Log prediction
                    pred_logger.log_prediction(
                        feature_set='finbert',
                        model_type='random_forest',
                        model_version=result['model_info']['model_version'],
                        prediction=result['prediction']['direction_numeric'],
                        probability_down=result['prediction']['probability']['down'],
                        probability_up=result['prediction']['probability']['up'],
                        confidence=result['prediction']['confidence'],
                        features=features,
                        response_time_ms=0,  # Backfilled
                        cached_features=True,
                        bitcoin_price=features.get('price_usd'),
                        timestamp_override=timestamp  # Use feature timestamp
                    )
                    finbert_count += 1
                    
                    if i % 50 == 0:
                        logger.info(f"  Generated {i}/{len(finbert_features)} FinBERT predictions")
                else:
                    finbert_errors += 1
                    logger.warning(f"  Failed to generate prediction for timestamp {timestamp}")
                    
            except Exception as e:
                finbert_errors += 1
                logger.error(f"  Error at {timestamp}: {e}")
        
        logger.info(f"✓ FinBERT: {finbert_count} predictions generated, {finbert_errors} errors")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Backfill Complete!")
        logger.info("=" * 60)
        logger.info(f"VADER:   {vader_count} predictions")
        logger.info(f"FinBERT: {finbert_count} predictions")
        logger.info(f"Total:   {vader_count + finbert_count} predictions")
        logger.info(f"Errors:  {vader_errors + finbert_errors}")
        logger.info("=" * 60)
        
    finally:
        db.close()

def get_neondb_session():
    """Get NeonDB session"""
    import os

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    db_url = os.getenv('NEONDB_PRODUCTION_URL')
    if not db_url:
        raise ValueError("NEONDB_PRODUCTION_URL not configured")
    
    engine = create_engine(db_url)
    SessionFactory = sessionmaker(bind=engine)
    return SessionFactory()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill predictions for all feature sets')
    parser.add_argument(
        '--db',
        choices=['local', 'neondb_production'],
        default='neondb_production',
        help='Target database'
    )
    
    args = parser.parse_args()
    
    backfill_predictions(target_db=args.db)