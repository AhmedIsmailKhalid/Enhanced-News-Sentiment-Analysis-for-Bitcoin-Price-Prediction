"""
Real-time feature computation for predictions
Generates features from current data for model serving
"""
from typing import Optional

import pandas as pd
from sqlalchemy import text

from src.data_processing.feature_engineering.price_features import PriceFeatureEngineer
from src.data_processing.feature_engineering.sentiment_features import SentimentFeatureEngineer
from src.data_processing.feature_engineering.temporal_features import TemporalFeatureEngineer
from src.shared.database import SessionLocal
from src.shared.logging import get_logger


class FeatureServer:
    """Generate features in real-time for predictions"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.price_engineer = PriceFeatureEngineer()
        self.sentiment_engineer = SentimentFeatureEngineer()
        self.temporal_engineer = TemporalFeatureEngineer()
    
    def get_latest_features(
        self, 
        feature_set: str,
        target_db: str = "local"
    ) -> Optional[pd.Series]:
        """
        Get latest features for prediction
        
        Args:
            feature_set: 'vader' or 'finbert'
            target_db: Database to query
            
        Returns:
            Series with feature values, or None if insufficient data
        """
        db = self._get_session(target_db)
        
        try:
            # Query latest feature record
            query = text("""
                SELECT features, timestamp
                FROM feature_data
                WHERE feature_set_name = :feature_set
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            result = db.execute(query, {'feature_set': feature_set}).fetchone()
            
            if not result:
                self.logger.warning(f"No features found for {feature_set}")
                return None
            
            # Convert to Series
            features = pd.Series(result.features)
            features['timestamp'] = result.timestamp
            
            self.logger.info(f"Retrieved latest features for {feature_set}")
            return features
            
        finally:
            db.close()
    
    def compute_features_on_demand(
        self,
        feature_set: str,
        target_db: str = "local",
        lookback_hours: int = 24
    ) -> Optional[pd.Series]:
        """
        Compute features on-demand from recent data
        Use when pre-computed features are stale
        
        Args:
            feature_set: 'vader' or 'finbert'
            target_db: Database to query
            lookback_hours: Hours of data to use
            
        Returns:
            Series with computed features
        """
        db = self._get_session(target_db)
        
        try:
            # Get recent price data
            price_query = text("""
                SELECT 
                    price_usd,
                    volume_24h,
                    change_24h,
                    collected_at
                FROM price_data
                WHERE collected_at >= NOW() - INTERVAL ':hours hours'
                ORDER BY collected_at ASC
            """)
            
            price_df = pd.read_sql(
                price_query, 
                db.bind,
                params={'hours': lookback_hours}
            )
            
            if price_df.empty:
                self.logger.warning("No recent price data")
                return None
            
            # Get recent sentiment data
            sentiment_query = text("""
                SELECT 
                    vader_compound,
                    vader_positive,
                    vader_neutral,
                    vader_negative,
                    finbert_compound,
                    finbert_positive,
                    finbert_neutral,
                    finbert_negative,
                    finbert_confidence,
                    processed_at
                FROM sentiment_data
                WHERE processed_at >= NOW() - INTERVAL ':hours hours'
                ORDER BY processed_at ASC
            """)
            
            sentiment_df = pd.read_sql(
                sentiment_query,
                db.bind,
                params={'hours': lookback_hours}
            )
            
            if sentiment_df.empty:
                self.logger.warning("No recent sentiment data")
                return None
            
            # Engineer features
            price_features = self.price_engineer.create_features(price_df)
            
            if feature_set == 'vader':
                sentiment_features = self.sentiment_engineer.create_vader_features(sentiment_df)
            else:
                sentiment_features = self.sentiment_engineer.create_finbert_features(sentiment_df)
            
            temporal_features = self.temporal_engineer.create_features(
                price_df, 
                timestamp_col='collected_at'
            )
            
            # Get latest row from each
            latest_features = {}
            
            if not price_features.empty:
                latest_features.update(price_features.iloc[-1].to_dict())
            
            if not sentiment_features.empty:
                latest_features.update(sentiment_features.iloc[-1].to_dict())
            
            if not temporal_features.empty:
                latest_features.update(temporal_features.iloc[-1].to_dict())
            
            features_series = pd.Series(latest_features)
            
            self.logger.info(f"Computed {len(features_series)} features on-demand")
            return features_series
            
        except Exception as e:
            self.logger.error(f"Feature computation failed: {e}")
            return None
            
        finally:
            db.close()
    
    def _get_session(self, target_db: str):
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