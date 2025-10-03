"""
Temporal feature engineering
Time-based features for capturing market cycles and patterns
"""
import numpy as np
import pandas as pd

from src.shared.logging import get_logger


class TemporalFeatureEngineer:
    """Engineer time-based features"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_features(self, df: pd.DataFrame, timestamp_col: str = 'collected_at') -> pd.DataFrame:
        """
        Create temporal features from timestamp column
        
        Args:
            df: DataFrame with timestamp column
            timestamp_col: Name of timestamp column
            
        Returns:
            DataFrame with temporal features added
        """
        if df.empty:
            self.logger.warning("Empty dataframe provided")
            return pd.DataFrame()
        
        if timestamp_col not in df.columns:
            self.logger.error(f"Timestamp column '{timestamp_col}' not found")
            return df
        
        result_df = df.copy()
        
        # Ensure datetime type
        result_df[timestamp_col] = pd.to_datetime(result_df[timestamp_col])
        
        self.logger.info(f"Engineering temporal features from {timestamp_col}")
        
        # Extract basic time components
        result_df = self._add_time_components(result_df, timestamp_col)
        
        # Add cyclical encodings
        result_df = self._add_cyclical_features(result_df)
        
        # Add time-based flags
        result_df = self._add_time_flags(result_df, timestamp_col)
        
        self.logger.info(f"Created temporal features, total columns: {len(result_df.columns)}")
        return result_df
    
    def _add_time_components(self, df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
        """Extract basic time components"""
        dt = df[timestamp_col]
        
        # Hour of day (0-23)
        df['hour'] = dt.dt.hour
        
        # Day of week (0=Monday, 6=Sunday)
        df['day_of_week'] = dt.dt.dayofweek
        
        # Day of month (1-31)
        df['day_of_month'] = dt.dt.day
        
        # Month (1-12)
        df['month'] = dt.dt.month
        
        # Week of year (1-52)
        df['week_of_year'] = dt.dt.isocalendar().week
        
        # Quarter (1-4)
        df['quarter'] = dt.dt.quarter
        
        return df
    
    def _add_cyclical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add cyclical encodings using sin/cos transformations
        This preserves the cyclic nature of time (e.g., hour 23 is close to hour 0)
        """
        # Hour of day (24-hour cycle)
        if 'hour' in df.columns:
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Day of week (7-day cycle)
        if 'day_of_week' in df.columns:
            df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Day of month (approximately 30-day cycle)
        if 'day_of_month' in df.columns:
            df['day_of_month_sin'] = np.sin(2 * np.pi * df['day_of_month'] / 30)
            df['day_of_month_cos'] = np.cos(2 * np.pi * df['day_of_month'] / 30)
        
        # Month (12-month cycle)
        if 'month' in df.columns:
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def _add_time_flags(self, df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
        """Add binary flags for specific time periods"""
        dt = df[timestamp_col]
        
        # Weekend flag
        df['is_weekend'] = (dt.dt.dayofweek >= 5).astype(int)
        
        # Business hours (9 AM - 5 PM UTC)
        df['is_business_hours'] = (
            (dt.dt.hour >= 9) & (dt.dt.hour < 17)
        ).astype(int)
        
        # US market hours (roughly 14:30 - 21:00 UTC)
        df['is_us_market_hours'] = (
            (dt.dt.hour >= 14) & (dt.dt.hour < 21) & (dt.dt.dayofweek < 5)
        ).astype(int)
        
        # Asian market hours (roughly 0:00 - 8:00 UTC)
        df['is_asian_market_hours'] = (
            (dt.dt.hour >= 0) & (dt.dt.hour < 8) & (dt.dt.dayofweek < 5)
        ).astype(int)
        
        # European market hours (roughly 8:00 - 16:30 UTC)
        df['is_european_market_hours'] = (
            (dt.dt.hour >= 8) & (dt.dt.hour < 17) & (dt.dt.dayofweek < 5)
        ).astype(int)
        
        # Month start/end (first/last 3 days)
        df['is_month_start'] = (dt.dt.day <= 3).astype(int)
        df['is_month_end'] = (dt.dt.day >= 28).astype(int)
        
        # Quarter start/end
        df['is_quarter_start'] = (
            (dt.dt.month.isin([1, 4, 7, 10])) & (dt.dt.day <= 5)
        ).astype(int)
        df['is_quarter_end'] = (
            (dt.dt.month.isin([3, 6, 9, 12])) & (dt.dt.day >= 25)
        ).astype(int)
        
        return df