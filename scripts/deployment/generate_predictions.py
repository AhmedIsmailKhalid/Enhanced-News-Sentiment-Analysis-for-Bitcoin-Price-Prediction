"""
Automated Prediction Generation
Generates predictions for new feature data automatically
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import and_, func

from src.serving.prediction_pipeline import PredictionPipeline
from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import FeatureData, PredictionLog

logger = get_logger(__name__)


def generate_predictions_for_new_data(
    target_db: str = "neondb_production",
    lookback_hours: int = 24
):
    """
    Generate predictions for feature data that doesn't have predictions yet
    
    Args:
        target_db: Database to use
        lookback_hours: How far back to check for unpredicted features
    """
    
    # Set active database
    os.environ['ACTIVE_DATABASE'] = target_db
    
    db = SessionLocal()
    pipeline = PredictionPipeline(target_db=target_db)
    
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        # Get feature data that doesn't have predictions yet
        # Check both VADER and FinBERT
        for feature_set in ['vader', 'finbert']:
            logger.info(f"Checking {feature_set} features for predictions...")
            
            # Get features without predictions
            unpredicted = db.query(FeatureData).outerjoin(
                PredictionLog,
                and_(
                    FeatureData.timestamp == PredictionLog.predicted_at,
                    PredictionLog.feature_set == feature_set
                )
            ).filter(
                FeatureData.feature_set_name == feature_set,
                FeatureData.timestamp >= cutoff_time,
                PredictionLog.id.is_(None)  # No prediction exists
            ).order_by(FeatureData.timestamp.asc()).all()
            
            logger.info(f"Found {len(unpredicted)} {feature_set} features without predictions")
            
            if len(unpredicted) == 0:
                logger.info(f"No new {feature_set} features to predict")
                continue
            
            # Generate predictions for unpredicted features
            for feature in unpredicted:
                try:
                    # Use the existing prediction pipeline
                    # Note: This uses cached features from the database
                    result = pipeline.predict(
                        feature_set=feature_set,
                        model_type='random_forest',
                        use_cached_features=True
                    )
                    
                    if result.get('success'):
                        logger.info(
                            f"Generated {feature_set} prediction for {feature.timestamp}: "
                            f"{result['prediction']['direction']} "
                            f"(confidence: {result['prediction']['confidence']:.2%})"
                        )
                    else:
                        logger.warning(f"Prediction failed for {feature.timestamp}: {result.get('error')}")
                
                except Exception as e:
                    logger.error(f"Failed to generate prediction for {feature.timestamp}: {e}")
                    continue
        
        logger.info("✅ Automated prediction generation completed")
        return True
        
    except Exception as e:
        logger.error(f"Automated prediction generation failed: {e}")
        return False
        
    finally:
        db.close()


def backfill_historical_predictions(
    target_db: str = "neondb_production",
    max_features: int = 500
):
    """
    Backfill predictions for historical feature data
    
    Args:
        target_db: Database to use
        max_features: Maximum features to process per feature set
    """
    
    os.environ['ACTIVE_DATABASE'] = target_db
    
    db = SessionLocal()
    pipeline = PredictionPipeline(target_db=target_db)
    
    try:
        logger.info("Starting historical prediction backfill...")
        
        for feature_set in ['vader', 'finbert']:
            logger.info(f"Processing {feature_set} historical features...")
            
            # Get all features without predictions
            unpredicted = db.query(FeatureData).outerjoin(
                PredictionLog,
                and_(
                    func.date(FeatureData.timestamp) == func.date(PredictionLog.predicted_at),
                    PredictionLog.feature_set == feature_set
                )
            ).filter(
                FeatureData.feature_set_name == feature_set,
                PredictionLog.id.is_(None)
            ).order_by(FeatureData.timestamp.desc()).limit(max_features).all()
            
            logger.info(f"Found {len(unpredicted)} historical {feature_set} features to predict")
            
            predicted_count = 0
            
            for idx, feature in enumerate(unpredicted, 1):
                try:
                    result = pipeline.predict(
                        feature_set=feature_set,
                        model_type='random_forest',
                        use_cached_features=True
                    )
                    
                    if result.get('success'):
                        predicted_count += 1
                        
                        if predicted_count % 10 == 0:
                            logger.info(f"Progress: {predicted_count}/{len(unpredicted)} predictions generated")
                    
                except Exception as e:
                    logger.error(f"Failed to backfill prediction for {feature.timestamp}: {e}")
                    continue
            
            logger.info(f"✅ Backfilled {predicted_count} {feature_set} predictions")
        
        logger.info("✅ Historical backfill completed")
        return True
        
    except Exception as e:
        logger.error(f"Historical backfill failed: {e}")
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate automated predictions')
    parser.add_argument(
        '--mode',
        choices=['auto', 'backfill'],
        default='auto',
        help='Mode: auto (recent data) or backfill (historical data)'
    )
    parser.add_argument(
        '--db',
        choices=['local', 'neondb_production', 'neondb_backup'],
        default='neondb_production',
        help='Database to use'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Lookback hours for auto mode (default: 24)'
    )
    parser.add_argument(
        '--max',
        type=int,
        default=500,
        help='Max features for backfill mode (default: 500)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'auto':
        logger.info(f"Running automated prediction generation (last {args.hours} hours)...")
        success = generate_predictions_for_new_data(
            target_db=args.db,
            lookback_hours=args.hours
        )
    else:
        logger.info(f"Running historical backfill (max {args.max} features)...")
        success = backfill_historical_predictions(
            target_db=args.db,
            max_features=args.max
        )
    
    sys.exit(0 if success else 1)