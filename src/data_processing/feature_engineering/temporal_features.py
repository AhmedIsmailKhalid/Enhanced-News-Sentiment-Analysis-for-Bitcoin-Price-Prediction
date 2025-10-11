"""
Temporal feature engineering
Time-based features for capturing market cycles and patterns
"""
import pandas as pd

from src.shared.logging import get_logger


class TemporalFeatureEngineer:
    """Engineer time-based features"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_features(self, df: pd.DataFrame, timestamp_col: str = 'collected_at') -> pd.DataFrame:
        """
        Create simplified temporal features (3 features total)
        
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
        
        self.logger.info(f"Engineering simplified temporal features from {timestamp_col}")
        
        # Feature 1: hour (0-23)
        result_df['hour'] = result_df[timestamp_col].dt.hour
        
        # Feature 2: day_of_week (0-6, Monday=0)
        result_df['day_of_week'] = result_df[timestamp_col].dt.dayofweek
        
        # Feature 3: is_weekend (0 or 1)
        result_df['is_weekend'] = (result_df['day_of_week'] >= 5).astype(int)
        
        self.logger.info("Created 3 temporal features: hour, day_of_week, is_weekend")
        return result_df