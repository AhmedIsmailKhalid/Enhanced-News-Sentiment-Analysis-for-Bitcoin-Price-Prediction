"""
Feature combiner - creates two separate feature sets:
1. VADER + Price + Temporal features
2. FinBERT + Price + Temporal features
"""
from typing import Dict, Tuple

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import NewsData, PriceData, SentimentData  # noqa

from .price_features import PriceFeatureEngineer
from .sentiment_features import SentimentFeatureEngineer
from .temporal_features import TemporalFeatureEngineer


class FeatureCombiner:
    """Combine all features into two separate datasets for model comparison"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.price_engineer = PriceFeatureEngineer()
        self.sentiment_engineer = SentimentFeatureEngineer()
        self.temporal_engineer = TemporalFeatureEngineer()
    
    def create_feature_sets(self, target_db: str = "local") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create two complete feature sets
        
        Args:
            target_db: Target database (local, neondb_production, neondb_backup)
            
        Returns:
            Tuple of (vader_feature_set, finbert_feature_set)
        """
        self.logger.info("Starting feature set creation...")
        
        # Get session
        db = self._get_session(target_db)
        
        try:
            # Step 1: Load all data
            price_df = self._load_price_data(db)
            sentiment_df = self._load_sentiment_data(db)
            
            if price_df.empty or sentiment_df.empty:
                self.logger.error("No data available for feature engineering")
                return pd.DataFrame(), pd.DataFrame()
            
            # Step 2: Engineer price features (shared by both)
            self.logger.info("Engineering price features...")
            price_features = self.price_engineer.create_features(price_df)
            
            # Step 3: Engineer VADER sentiment features
            self.logger.info("Engineering VADER sentiment features...")
            vader_sentiment_features = self.sentiment_engineer.create_vader_features(sentiment_df)
            
            # Step 4: Engineer FinBERT sentiment features
            self.logger.info("Engineering FinBERT sentiment features...")
            finbert_sentiment_features = self.sentiment_engineer.create_finbert_features(sentiment_df)
            
            # Step 5: Engineer temporal features (shared by both)
            self.logger.info("Engineering temporal features...")
            temporal_features = self.temporal_engineer.create_features(
                price_df, 
                timestamp_col='collected_at'
            )
            
            # Step 6: Combine into two separate datasets
            self.logger.info("Combining features into two datasets...")
            
            # Dataset 1: VADER + Price + Temporal
            vader_dataset = self._merge_features(
                price_features,
                vader_sentiment_features,
                temporal_features,
                dataset_name="VADER"
            )
            
            # Dataset 2: FinBERT + Price + Temporal
            finbert_dataset = self._merge_features(
                price_features,
                finbert_sentiment_features,
                temporal_features,
                dataset_name="FinBERT"
            )
            
            self.logger.info(f"VADER dataset shape: {vader_dataset.shape}")
            self.logger.info(f"FinBERT dataset shape: {finbert_dataset.shape}")
            
            return vader_dataset, finbert_dataset
            
        finally:
            db.close()
    
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
    
    def _load_price_data(self, db: Session) -> pd.DataFrame:
        """Load price data from database"""
        query = text("""
            SELECT 
                symbol,
                price_usd,
                market_cap,
                volume_24h,
                change_24h,
                collected_at
            FROM price_data
            WHERE symbol = 'BTC'
            ORDER BY collected_at ASC
        """)
        
        df = pd.read_sql(query, db.bind)
        self.logger.info(f"Loaded {len(df)} price records")
        return df
    
    def _load_sentiment_data(self, db: Session) -> pd.DataFrame:
        """Load sentiment data with news metadata"""
        query = text("""
            SELECT 
                s.news_data_id,
                s.vader_compound,
                s.vader_positive,
                s.vader_neutral,
                s.vader_negative,
                s.finbert_compound,
                s.finbert_positive,
                s.finbert_neutral,
                s.finbert_negative,
                s.finbert_confidence,
                s.combined_sentiment,
                s.sentiment_category,
                s.processed_at,
                n.word_count,
                n.collected_at as article_collected_at
            FROM sentiment_data s
            JOIN news_data n ON s.news_data_id = n.id
            ORDER BY s.processed_at ASC
        """)
        
        df = pd.read_sql(query, db.bind)
        self.logger.info(f"Loaded {len(df)} sentiment records")
        return df
    
    def _merge_features(
        self,
        price_features: pd.DataFrame,
        sentiment_features: pd.DataFrame,
        temporal_features: pd.DataFrame,
        dataset_name: str
    ) -> pd.DataFrame:
        """
        Merge price, sentiment, and temporal features
        
        Args:
            price_features: Price-based features
            sentiment_features: Sentiment-based features (VADER or FinBERT)
            temporal_features: Temporal features
            dataset_name: Name for logging (VADER or FinBERT)
        """
        # Start with price features as base
        merged = price_features.copy()
        
        # Add sentiment features (matching on timestamp)
        if 'collected_at' in merged.columns and 'processed_at' in sentiment_features.columns:
            # Align timestamps (sentiment processed_at to price collected_at)
            sentiment_features['collected_at'] = sentiment_features['processed_at']
            
            # Merge on collected_at
            merged = pd.merge(
                merged,
                sentiment_features,
                on='collected_at',
                how='left',
                suffixes=('', '_sentiment')
            )
        
        # Add temporal features (already have collected_at)
        # Extract only temporal columns (not duplicates)
        temporal_cols = [col for col in temporal_features.columns 
                        if col.startswith(('hour', 'day', 'month', 'week', 'quarter', 
                                          'is_', 'year'))]
        
        if temporal_cols and 'collected_at' in temporal_features.columns:
            merged = pd.merge(
                merged,
                temporal_features[['collected_at'] + temporal_cols],
                on='collected_at',
                how='left',
                suffixes=('', '_temporal')
            )
        
        # Remove duplicates and clean up
        merged = merged.loc[:, ~merged.columns.duplicated()]
        
        self.logger.info(f"{dataset_name} dataset: {merged.shape[0]} rows, {merged.shape[1]} features")
        
        return merged
    
    def get_feature_summary(self, df: pd.DataFrame, dataset_name: str) -> Dict:
        """Get summary statistics of feature set"""
        if df.empty:
            return {'dataset': dataset_name, 'error': 'Empty dataset'}
        
        summary = {
            'dataset': dataset_name,
            'total_rows': len(df),
            'total_features': len(df.columns),
            'feature_categories': {},
            'missing_data': df.isnull().sum().to_dict(),
            'date_range': {
                'start': df['collected_at'].min() if 'collected_at' in df.columns else None,
                'end': df['collected_at'].max() if 'collected_at' in df.columns else None
            }
        }
        
        # Categorize features
        price_features = [col for col in df.columns if any(x in col for x in 
                         ['price', 'return', 'sma', 'ema', 'rsi', 'macd', 'bb_', 'volume', 'volatility', 'atr'])]
        
        sentiment_features = [col for col in df.columns if any(x in col for x in 
                             ['vader', 'finbert', 'sentiment', 'news_count'])]
        
        temporal_features = [col for col in df.columns if any(x in col for x in 
                            ['hour', 'day', 'month', 'week', 'quarter', 'is_'])]
        
        summary['feature_categories'] = {
            'price_features': len(price_features),
            'sentiment_features': len(sentiment_features),
            'temporal_features': len(temporal_features)
        }
        
        return summary