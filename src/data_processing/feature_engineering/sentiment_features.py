"""
Sentiment-based feature engineering
Creates separate VADER and FinBERT feature sets
"""
import pandas as pd

from src.shared.logging import get_logger


class SentimentFeatureEngineer:
    """Engineer features from sentiment data - separate VADER and FinBERT"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_vader_features(self, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create VADER-specific sentiment features
        
        Args:
            sentiment_df: DataFrame with sentiment data including vader_* columns
            
        Returns:
            DataFrame with VADER feature set
        """
        if sentiment_df.empty:
            self.logger.warning("Empty sentiment dataframe provided for VADER")
            return pd.DataFrame()
        
        df = sentiment_df.copy()
        
        self.logger.info(f"Engineering VADER features from {len(df)} sentiment records")
        
        # Hourly aggregations
        df = self._add_hourly_aggregations(df, model_prefix='vader')
        
        # Sentiment change rates
        df = self._add_sentiment_changes(df, model_prefix='vader')
        
        # News volume features
        df = self._add_news_volume_features(df)
        
        # Sentiment momentum
        df = self._add_sentiment_momentum(df, model_prefix='vader')
        
        # Extreme sentiment detection
        df = self._add_extreme_sentiment_flags(df, model_prefix='vader')
        
        self.logger.info(f"Created {len(df.columns)} VADER features")
        return df
    
    def create_finbert_features(self, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create FinBERT-specific sentiment features
        
        Args:
            sentiment_df: DataFrame with sentiment data including finbert_* columns
            
        Returns:
            DataFrame with FinBERT feature set
        """
        if sentiment_df.empty:
            self.logger.warning("Empty sentiment dataframe provided for FinBERT")
            return pd.DataFrame()
        
        df = sentiment_df.copy()
        
        self.logger.info(f"Engineering FinBERT features from {len(df)} sentiment records")
        
        # Hourly aggregations
        df = self._add_hourly_aggregations(df, model_prefix='finbert')
        
        # Sentiment change rates
        df = self._add_sentiment_changes(df, model_prefix='finbert')
        
        # News volume features
        df = self._add_news_volume_features(df)
        
        # Sentiment momentum
        df = self._add_sentiment_momentum(df, model_prefix='finbert')
        
        # Extreme sentiment detection
        df = self._add_extreme_sentiment_flags(df, model_prefix='finbert')
        
        # FinBERT-specific: confidence-weighted sentiment
        df = self._add_confidence_weighted_features(df)
        
        self.logger.info(f"Created {len(df.columns)} FinBERT features")
        return df
    
    def _add_hourly_aggregations(self, df: pd.DataFrame, model_prefix: str) -> pd.DataFrame:
        """
        Aggregate sentiment by hour
        
        Args:
            df: Sentiment dataframe
            model_prefix: 'vader' or 'finbert'
        """
        compound_col = f'{model_prefix}_compound'
        
        if compound_col not in df.columns:
            self.logger.warning(f"{compound_col} not found")
            return df
        
        # Ensure datetime
        if 'processed_at' in df.columns:
            df['processed_at'] = pd.to_datetime(df['processed_at'])
            df = df.sort_values('processed_at')
        
        # Rolling window aggregations (last N hours)
        for window in [1, 6, 24]:
            # Mean sentiment
            df[f'{model_prefix}_mean_{window}h'] = (
                df[compound_col].rolling(window=window, min_periods=1).mean()
            )
            
            # Standard deviation (volatility)
            df[f'{model_prefix}_std_{window}h'] = (
                df[compound_col].rolling(window=window, min_periods=1).std()
            )
            
            # Min/Max
            df[f'{model_prefix}_min_{window}h'] = (
                df[compound_col].rolling(window=window, min_periods=1).min()
            )
            df[f'{model_prefix}_max_{window}h'] = (
                df[compound_col].rolling(window=window, min_periods=1).max()
            )
            
            # Range
            df[f'{model_prefix}_range_{window}h'] = (
                df[f'{model_prefix}_max_{window}h'] - df[f'{model_prefix}_min_{window}h']
            )
        
        return df
    
    def _add_sentiment_changes(self, df: pd.DataFrame, model_prefix: str) -> pd.DataFrame:
        """Add sentiment change rate features"""
        compound_col = f'{model_prefix}_compound'
        
        if compound_col not in df.columns:
            return df
        
        # Sentiment changes over different periods
        df[f'{model_prefix}_change_1h'] = df[compound_col].diff(periods=1)
        df[f'{model_prefix}_change_6h'] = df[compound_col].diff(periods=6)
        df[f'{model_prefix}_change_24h'] = df[compound_col].diff(periods=24)
        
        # Rate of change
        df[f'{model_prefix}_roc_1h'] = df[compound_col].pct_change(periods=1)
        df[f'{model_prefix}_roc_24h'] = df[compound_col].pct_change(periods=24)
        
        return df
    
    def _add_news_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add news article volume features"""
        if 'processed_at' not in df.columns:
            return df
        
        # Count articles in rolling windows
        for window in [1, 6, 24]:
            df[f'news_count_{window}h'] = (
                df['processed_at'].rolling(window=window, min_periods=1).count()
            )
        
        # News velocity (change in article count)
        df['news_velocity'] = df['news_count_24h'].diff()
        
        return df
    
    def _add_sentiment_momentum(self, df: pd.DataFrame, model_prefix: str) -> pd.DataFrame:
        """
        Add momentum indicators for sentiment
        Similar to price momentum but for sentiment
        """
        compound_col = f'{model_prefix}_compound'
        
        if compound_col not in df.columns:
            return df
        
        # Sentiment moving averages
        df[f'{model_prefix}_sma_7'] = (
            df[compound_col].rolling(window=7, min_periods=1).mean()
        )
        df[f'{model_prefix}_sma_30'] = (
            df[compound_col].rolling(window=30, min_periods=1).mean()
        )
        
        # Sentiment position relative to moving averages
        df[f'{model_prefix}_above_sma_7'] = (
            (df[compound_col] > df[f'{model_prefix}_sma_7']).astype(int)
        )
        df[f'{model_prefix}_above_sma_30'] = (
            (df[compound_col] > df[f'{model_prefix}_sma_30']).astype(int)
        )
        
        # Sentiment trend (positive/negative/neutral streak)
        df[f'{model_prefix}_streak'] = self._calculate_sentiment_streak(df[compound_col])
        
        return df
    
    def _calculate_sentiment_streak(self, sentiment: pd.Series) -> pd.Series:
        """Calculate consecutive positive/negative sentiment streak"""
        # Convert to direction: 1 (positive), -1 (negative), 0 (neutral)
        direction = sentiment.apply(
            lambda x: 1 if x > 0.05 else (-1 if x < -0.05 else 0)
        )
        
        # Calculate streak
        streak = direction.groupby((direction != direction.shift()).cumsum()).cumsum()
        
        return streak
    
    def _add_extreme_sentiment_flags(self, df: pd.DataFrame, model_prefix: str) -> pd.DataFrame:
        """Flag extreme sentiment readings"""
        compound_col = f'{model_prefix}_compound'
        
        if compound_col not in df.columns:
            return df
        
        # Extreme positive (>0.5)
        df[f'{model_prefix}_extreme_positive'] = (df[compound_col] > 0.5).astype(int)
        
        # Extreme negative (<-0.5)
        df[f'{model_prefix}_extreme_negative'] = (df[compound_col] < -0.5).astype(int)
        
        # Count extreme readings in window
        for window in [6, 24]:
            df[f'{model_prefix}_extreme_count_{window}h'] = (
                df[f'{model_prefix}_extreme_positive'].rolling(window=window).sum() +
                df[f'{model_prefix}_extreme_negative'].rolling(window=window).sum()
            )
        
        return df
    
    def _add_confidence_weighted_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        FinBERT-specific: weight sentiment by model confidence
        Only applicable to FinBERT which has confidence scores
        """
        if 'finbert_compound' not in df.columns or 'finbert_confidence' not in df.columns:
            return df
        
        # Confidence-weighted sentiment
        df['finbert_weighted_sentiment'] = (
            df['finbert_compound'] * df['finbert_confidence']
        )
        
        # Rolling weighted averages
        for window in [6, 24]:
            df[f'finbert_weighted_mean_{window}h'] = (
                df['finbert_weighted_sentiment'].rolling(window=window, min_periods=1).mean()
            )
        
        # Average confidence over time
        for window in [6, 24]:
            df[f'finbert_avg_confidence_{window}h'] = (
                df['finbert_confidence'].rolling(window=window, min_periods=1).mean()
            )
        
        return df