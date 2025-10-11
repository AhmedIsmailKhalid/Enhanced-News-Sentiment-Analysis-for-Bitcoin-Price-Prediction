"""
Sentiment-based feature engineering (Simplified)
VADER and FinBERT raw sentiment scores only
"""
import pandas as pd

from src.shared.logging import get_logger


class SentimentFeatureEngineer:
    """Engineer features from sentiment data"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_vader_features(self, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create VADER sentiment features (4 features total)
        
        Args:
            sentiment_df: DataFrame with sentiment data
            
        Returns:
            DataFrame with VADER features
        """
        if sentiment_df.empty:
            self.logger.warning("Empty sentiment dataframe provided")
            return pd.DataFrame()
        
        df = sentiment_df.copy()
        
        # Ensure datetime
        if 'processed_at' in df.columns:
            df['processed_at'] = pd.to_datetime(df['processed_at'])
            df = df.sort_values('processed_at')
        
        self.logger.info(f"Creating VADER features from {len(df)} sentiment records")
        
        # Select only VADER features (4 features)
        vader_cols = ['processed_at', 'vader_compound', 'vader_positive', 
                      'vader_neutral', 'vader_negative']
        
        vader_features = df[[col for col in vader_cols if col in df.columns]].copy()
        
        self.logger.info("Created 4 VADER features: compound, positive, neutral, negative")
        return vader_features
    
    def create_finbert_features(self, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create FinBERT sentiment features (4 features total)
        
        Args:
            sentiment_df: DataFrame with sentiment data
            
        Returns:
            DataFrame with FinBERT features
        """
        if sentiment_df.empty:
            self.logger.warning("Empty sentiment dataframe provided")
            return pd.DataFrame()
        
        df = sentiment_df.copy()
        
        # Ensure datetime
        if 'processed_at' in df.columns:
            df['processed_at'] = pd.to_datetime(df['processed_at'])
            df = df.sort_values('processed_at')
        
        self.logger.info(f"Creating FinBERT features from {len(df)} sentiment records")
        
        # Select only FinBERT features (4 features)
        finbert_cols = ['processed_at', 'finbert_compound', 'finbert_positive', 
                        'finbert_neutral', 'finbert_negative']
        
        finbert_features = df[[col for col in finbert_cols if col in df.columns]].copy()
        
        self.logger.info("Created 4 FinBERT features: compound, positive, neutral, negative")
        return finbert_features