"""
Unified Prediction Generation Script

Generates predictions for features without predictions.
Supports both backfill (all historical) and real-time (recent) modes.

Usage:
    # Backfill all historical features
    python generate_predictions.py --mode all --db neondb_production
    
    # Generate predictions for recent features (workflow)
    python generate_predictions.py --mode recent --hours 1 --db neondb_production
"""

"""
Unified Prediction Generation Script

Generates predictions for features without predictions.
Supports both backfill (all historical) and real-time (recent) modes.

Usage:
    # Backfill all historical features
    python generate_predictions.py --mode all --db neondb_production
    
    # Generate predictions for recent features (workflow)
    python generate_predictions.py --mode recent --hours 1 --db neondb_production
"""
# ruff: noqa: E402

import argparse
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.serving.model_manager import ModelManager
from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import FeatureData, PredictionLog


class UnifiedPredictionGenerator:
    """Generate predictions for features without predictions"""
    
    def __init__(self, target_db: str = 'neondb_production'):
        self.logger = get_logger(__name__)
        self.target_db = target_db
        self.model_manager = ModelManager()
        
        # Load models
        self.vader_model = None
        self.finbert_model = None
        self._load_models()
    
    def _get_session(self, target_db: str):
        """Get database session"""
        if target_db == "local":
            return SessionLocal()
        elif target_db == "neondb_production":
            db_url = os.getenv('NEONDB_PRODUCTION_URL')
            if not db_url:
                raise ValueError("NEONDB_PRODUCTION_URL environment variable not set")
            engine = create_engine(db_url)
            SessionFactory = sessionmaker(bind=engine)
            return SessionFactory()
        else:
            raise ValueError(f"Unknown target_db: {target_db}")
    
    def _load_models(self):
        """Load both VADER and FinBERT models - automatically select best available"""
        try:
            # Get best model for VADER
            vader_best = self._get_best_model('vader')
            self.vader_model = self.model_manager.load_model('vader', vader_best)
            self.logger.info(f"Loaded VADER model: {vader_best} (version: {self.vader_model['version']})")
            
            # Get best model for FinBERT
            finbert_best = self._get_best_model('finbert')
            self.finbert_model = self.model_manager.load_model('finbert', finbert_best)
            self.logger.info(f"Loaded FinBERT model: {finbert_best} (version: {self.finbert_model['version']})")
            
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
            raise

    def _get_best_model(self, feature_set: str) -> str:
        """
        Automatically detect the best available model for a feature set
        by finding the most recent model with best validation accuracy
        """
        import json
        from pathlib import Path
        
        models_dir = Path(f"models/saved_models/{feature_set}")
        
        if not models_dir.exists():
            raise FileNotFoundError(f"Models directory not found: {models_dir}")
        
        best_model_type = None
        best_accuracy = -1
        best_timestamp = None
        
        # Iterate through all model type directories
        for model_type_dir in models_dir.iterdir():
            if not model_type_dir.is_dir():
                continue
            
            model_type = model_type_dir.name
            
            # Find all metadata files in this model type directory
            metadata_files = list(model_type_dir.glob("metadata_*.json"))
            
            if not metadata_files:
                continue
            
            # Get the most recent metadata file
            latest_metadata = max(metadata_files, key=lambda p: p.stem.split('_')[1])
            
            try:
                with open(latest_metadata, 'r') as f:
                    metadata = json.load(f)
                
                # Get validation accuracy (or test accuracy as fallback)
                val_accuracy = metadata.get('validation_metrics', {}).get('accuracy')
                if val_accuracy is None:
                    val_accuracy = metadata.get('test_metrics', {}).get('accuracy', 0)
                
                # Extract timestamp from filename
                timestamp_str = latest_metadata.stem.split('_', 1)[1]
                
                # Update best model if this one is better
                if val_accuracy > best_accuracy or (val_accuracy == best_accuracy and timestamp_str > best_timestamp):
                    best_accuracy = val_accuracy
                    best_model_type = model_type
                    best_timestamp = timestamp_str
                    
            except Exception as e:
                self.logger.warning(f"Could not read metadata for {model_type}: {e}")
                continue
        
        if best_model_type is None:
            raise FileNotFoundError(f"No valid models found for {feature_set}")
        
        self.logger.info(
            f"Selected best model for {feature_set}: {best_model_type} "
            f"(val_accuracy: {best_accuracy:.4f}, timestamp: {best_timestamp})"
        )
        
        return best_model_type
    
    def get_features_without_predictions(
        self, 
        mode: str = 'recent',
        hours: int = 1
    ) -> List[FeatureData]:
        """
        Query features that don't have predictions yet
        
        Args:
            mode: 'all' for backfill, 'recent' for last N hours
            hours: For 'recent' mode, how far back to look
        
        Returns:
            List of FeatureData records
        """
        db = self._get_session(self.target_db)
        
        try:
            # Base query for VADER features without predictions
            query = db.query(FeatureData).outerjoin(
                PredictionLog,
                (FeatureData.timestamp == PredictionLog.predicted_at) &
                (PredictionLog.feature_set == 'vader')
            ).filter(
                FeatureData.feature_set_name == 'vader',
                PredictionLog.id.is_(None)
            )
            
            # Add time filter for 'recent' mode
            if mode == 'recent':
                cutoff = datetime.utcnow() - timedelta(hours=hours)
                query = query.filter(FeatureData.timestamp >= cutoff)
            
            features = query.order_by(FeatureData.timestamp.asc()).all()
            
            self.logger.info(
                f"Found {len(features)} features without predictions "
                f"(mode: {mode})"
            )
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to query features: {e}")
            return []
        finally:
            db.close()
    
    def generate_prediction(
        self,
        features: pd.Series,
        feature_set: str,
        model_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a single prediction
        
        Args:
            features: Feature values as pandas Series
            feature_set: 'vader' or 'finbert'
            model_info: Model metadata
        
        Returns:
            Prediction result dict
        """
        try:
            model = model_info['model']
            
            # Try to get feature columns from metadata, fallback to model's feature_names_in_
            expected_features = model_info['metadata'].get('feature_columns')
            if not expected_features and hasattr(model, 'feature_names_in_'):
                expected_features = list(model.feature_names_in_)
            
            if not expected_features:
                self.logger.error("Could not determine expected features for model")
                return None
            
            # Prepare features in correct order
            X = self._prepare_features(features, expected_features)
            if X is None:
                return None
            
            # Make prediction
            prediction = int(model.predict([X])[0])
            proba = model.predict_proba([X])[0]
            
            return {
                'prediction': prediction,
                'probability_down': float(proba[0]),
                'probability_up': float(proba[1]),
                'confidence': float(max(proba)),
                'model_version': model_info['version']
            }
            
        except Exception as e:
            self.logger.error(f"Prediction generation failed: {e}")
            return None
    
    def _prepare_features(
        self,
        features: pd.Series,
        expected_columns: List[str]
    ) -> List[float]:
        """
        Prepare features for model input
        
        Args:
            features: Raw feature values
            expected_columns: Expected feature names in order
        
        Returns:
            List of feature values in correct order
        """
        try:
            X = []
            for col in expected_columns:
                if col in features:
                    val = features[col]
                    # Convert to float, use 0 if None/NaN
                    X.append(float(val) if pd.notna(val) else 0.0)
                else:
                    self.logger.warning(f"Missing feature: {col}, using 0")
                    X.append(0.0)
            
            return X
            
        except Exception as e:
            self.logger.error(f"Feature preparation failed: {e}")
            return None
    
    def store_prediction(
        self,
        feature_set: str,
        timestamp: datetime,
        prediction_result: Dict[str, Any],
        bitcoin_price: float
    ) -> bool:
        """
        Store prediction in database
        
        Args:
            feature_set: 'vader' or 'finbert'
            timestamp: When the prediction was made (feature timestamp)
            prediction_result: Prediction details
            bitcoin_price: Bitcoin price at prediction time
        
        Returns:
            Success status
        """
        db = self._get_session(self.target_db)
        
        try:
            prediction_log = PredictionLog(
                feature_set=feature_set,
                model_type='random_forest',
                model_version=prediction_result['model_version'],
                prediction=prediction_result['prediction'],
                probability_down=prediction_result['probability_down'],
                probability_up=prediction_result['probability_up'],
                confidence=prediction_result['confidence'],
                features_json={},  # Not storing features to save space
                feature_count=0,
                bitcoin_price_at_prediction=bitcoin_price,
                response_time_ms=0,
                cached_features=False,
                predicted_at=timestamp  # Use feature timestamp, not now()
            )
            
            db.add(prediction_log)
            db.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store prediction: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def process_features(
        self,
        features_list: List[FeatureData],
        batch_size: int = 50
    ) -> Dict[str, int]:
        """
        Process features and generate predictions
        
        Args:
            features_list: List of features to process
            batch_size: Number of features per batch
        
        Returns:
            Statistics dict
        """
        total = len(features_list)
        processed = 0
        vader_success = 0
        finbert_success = 0
        
        self.logger.info(f"Processing {total} features in batches of {batch_size}")
        
        # Get corresponding FinBERT features
        db = self._get_session(self.target_db)
        
        for i in range(0, total, batch_size):
            batch = features_list[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            self.logger.info(
                f"\nBatch {batch_num}/{total_batches}: "
                f"Processing features {i+1}-{min(i+batch_size, total)}..."
            )
            
            for vader_feature in batch:
                try:
                    # Parse VADER features
                    vader_features = pd.Series(vader_feature.features)
                    timestamp = vader_feature.timestamp
                    bitcoin_price = vader_features.get('price_usd', 0.0)
                    
                    # Generate VADER prediction
                    vader_result = self.generate_prediction(
                        vader_features,
                        'vader',
                        self.vader_model
                    )
                    
                    if vader_result:
                        if self.store_prediction('vader', timestamp, vader_result, bitcoin_price):
                            vader_success += 1
                    
                    # Get corresponding FinBERT features
                    finbert_feature = db.query(FeatureData).filter(
                        FeatureData.feature_set_name == 'finbert',
                        FeatureData.timestamp == timestamp
                    ).first()
                    
                    if finbert_feature:
                        finbert_features = pd.Series(finbert_feature.features)
                        
                        # Generate FinBERT prediction
                        finbert_result = self.generate_prediction(
                            finbert_features,
                            'finbert',
                            self.finbert_model
                        )
                        
                        if finbert_result:
                            if self.store_prediction('finbert', timestamp, finbert_result, bitcoin_price):
                                finbert_success += 1
                    
                    processed += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to process feature at {timestamp}: {e}")
                    continue
            
            self.logger.info(
                f"✓ Batch {batch_num} complete: "
                f"{vader_success} VADER + {finbert_success} FinBERT predictions"
            )
            
            # Refresh connection every batch to avoid timeout
            db.close()
            db = self._get_session(self.target_db)
        
        db.close()
        
        return {
            'total_features': total,
            'processed': processed,
            'vader_predictions': vader_success,
            'finbert_predictions': finbert_success,
            'total_predictions': vader_success + finbert_success
        }


def main():
    parser = argparse.ArgumentParser(
        description='Generate predictions for features without predictions'
    )
    parser.add_argument(
        '--mode',
        choices=['all', 'recent'],
        default='recent',
        help='Generation mode: all (backfill) or recent (workflow)'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=1,
        help='For recent mode: how far back to look (hours)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Number of features to process per batch'
    )
    parser.add_argument(
        '--db',
        default='neondb_production',
        help='Target database'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Unified Prediction Generation")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Database: {args.db}")
    if args.mode == 'recent':
        print(f"Time window: Last {args.hours} hour(s)")
    print(f"Batch size: {args.batch_size}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Initialize generator
        generator = UnifiedPredictionGenerator(target_db=args.db)
        
        # Get features without predictions
        features = generator.get_features_without_predictions(
            mode=args.mode,
            hours=args.hours
        )
        
        if not features:
            print("\n✓ No features to process")
            return 0
        
        # Process features
        stats = generator.process_features(
            features,
            batch_size=args.batch_size
        )
        
        # Report results
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("Generation Complete")
        print("=" * 60)
        print(f"Features processed: {stats['processed']}/{stats['total_features']}")
        print(f"VADER predictions: {stats['vader_predictions']}")
        print(f"FinBERT predictions: {stats['finbert_predictions']}")
        print(f"Total predictions: {stats['total_predictions']}")
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Prediction generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())