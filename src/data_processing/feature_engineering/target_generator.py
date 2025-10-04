"""
Generate target variable for price prediction
"""
import pandas as pd

from src.shared.logging import get_logger


class TargetGenerator:
    """Generate target variable for Bitcoin price prediction"""
    
    def __init__(self, prediction_horizon_hours: int = 1):
        """
        Initialize target generator
        
        Args:
            prediction_horizon_hours: How many hours ahead to predict (default: 1)
        """
        self.logger = get_logger(__name__)
        self.prediction_horizon = prediction_horizon_hours
    
    def create_target(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create binary target variable: 1 if price goes up, 0 if down
        
        Args:
            features_df: DataFrame with features including price_usd
            
        Returns:
            DataFrame with target column added
        """
        if features_df.empty:
            self.logger.warning("Empty features dataframe")
            return features_df
        
        df = features_df.copy()
        
        # Ensure we have price data
        if 'price_usd' not in df.columns:
            # Try to extract from JSON features
            if 'features' in df.columns:
                df['price_usd'] = df['features'].apply(
                    lambda x: x.get('price_usd') if isinstance(x, dict) else None
                )
        
        if 'price_usd' not in df.columns:
            raise ValueError("price_usd not found in features")
        
        # Calculate future price
        df['future_price'] = df['price_usd'].shift(-self.prediction_horizon)
        
        # Create binary target: 1 if price goes up, 0 if down
        df['target'] = (df['future_price'] > df['price_usd']).astype(int)
        
        # Calculate percentage change for analysis
        df['price_change_pct'] = (
            (df['future_price'] - df['price_usd']) / df['price_usd'] * 100
        )
        
        # Remove rows with no target (last N rows)
        df_with_target = df.dropna(subset=['target'])
        
        self.logger.info(
            f"Created target variable for {len(df_with_target)} samples "
            f"({self.prediction_horizon}h prediction horizon)"
        )
        
        # Log target distribution
        target_dist = df_with_target['target'].value_counts()
        self.logger.info(f"Target distribution: UP={target_dist.get(1, 0)}, DOWN={target_dist.get(0, 0)}")
        
        return df_with_target
    
    def get_target_statistics(self, df: pd.DataFrame) -> dict:
        """Get statistics about the target variable"""
        if 'target' not in df.columns:
            return {'error': 'No target variable found'}
        
        stats = {
            'total_samples': len(df),
            'up_samples': int(df['target'].sum()),
            'down_samples': int(len(df) - df['target'].sum()),
            'up_percentage': float(df['target'].mean() * 100),
            'avg_price_change_pct': float(df['price_change_pct'].mean()),
            'avg_up_change_pct': float(df[df['target'] == 1]['price_change_pct'].mean()),
            'avg_down_change_pct': float(df[df['target'] == 0]['price_change_pct'].mean()),
        }
        
        return stats