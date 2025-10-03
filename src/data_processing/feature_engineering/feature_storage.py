"""
Store engineered features to database
"""
from datetime import datetime
from typing import Dict

import pandas as pd
from sqlalchemy.orm import Session

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import FeatureData


class FeatureStorageManager:
    """Manage feature storage to database"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.feature_version = "v1.0.0"  # Update when feature engineering changes
    
    def store_feature_sets(
        self, 
        vader_df: pd.DataFrame, 
        finbert_df: pd.DataFrame,
        target_db: str = "local"
    ) -> Dict[str, int]:
        """
        Store both feature sets to database
        
        Args:
            vader_df: VADER feature set
            finbert_df: FinBERT feature set
            target_db: Target database
            
        Returns:
            Dictionary with counts of stored records
        """
        db = self._get_session(target_db)
        
        try:
            results = {
                'vader_stored': 0,
                'finbert_stored': 0
            }
            
            # Store VADER features
            if not vader_df.empty:
                vader_count = self._store_feature_set(
                    db, vader_df, feature_set_name='vader'
                )
                results['vader_stored'] = vader_count
                self.logger.info(f"Stored {vader_count} VADER feature records")
            
            # Store FinBERT features
            if not finbert_df.empty:
                finbert_count = self._store_feature_set(
                    db, finbert_df, feature_set_name='finbert'
                )
                results['finbert_stored'] = finbert_count
                self.logger.info(f"Stored {finbert_count} FinBERT feature records")
            
            db.commit()
            return results
            
        except Exception as e:
            self.logger.error(f"Feature storage failed: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def _store_feature_set(
        self, 
        db: Session, 
        df: pd.DataFrame, 
        feature_set_name: str
    ) -> int:
        """Store a single feature set"""
        import numpy as np
        
        stored_count = 0
        
        for idx, row in df.iterrows():
            # Get timestamp
            if 'collected_at' in row:
                timestamp = pd.to_datetime(row['collected_at'])
            else:
                timestamp = datetime.utcnow()
            
            # Convert row to dict, excluding timestamp columns
            features_dict = row.to_dict()
            if 'collected_at' in features_dict:
                del features_dict['collected_at']
            if 'processed_at' in features_dict:
                del features_dict['processed_at']
            
            # Replace NaN/NaT/inf values with None for JSON serialization
            features_dict = {
                k: (None if pd.isna(v) or (isinstance(v, float) and np.isinf(v)) else 
                    (float(v) if isinstance(v, (np.integer, np.floating)) else v))
                for k, v in features_dict.items()
            }
            
            # Check if this timestamp already exists for this feature set
            existing = db.query(FeatureData).filter_by(
                feature_set_name=feature_set_name,
                timestamp=timestamp
            ).first()
            
            if existing:
                # Update existing
                existing.features = features_dict
                existing.feature_version = self.feature_version
            else:
                # Create new
                feature_record = FeatureData(
                    feature_set_name=feature_set_name,
                    feature_version=self.feature_version,
                    timestamp=timestamp,
                    features=features_dict
                )
                db.add(feature_record)
            
            stored_count += 1
            
            # Commit in batches
            if stored_count % 50 == 0:
                db.commit()
        
        return stored_count
    
    def _get_session(self, target_db: str) -> Session:
        """Get database session"""
        if target_db == "local":
            return SessionLocal()
        elif target_db == "neondb_production":
            import os

            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            db_url = os.getenv('NEONDB_PRODUCTION_URL')
            engine = create_engine(db_url)
            SessionFactory = sessionmaker(bind=engine)
            return SessionFactory()
        else:
            raise ValueError(f"Unknown target_db: {target_db}")