"""
Price-based feature engineering
Technical indicators and price-derived features
"""
import numpy as np
import pandas as pd

from src.shared.logging import get_logger


class PriceFeatureEngineer:
    """Engineer features from price data"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_features(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all price-based features
        
        Args:
            price_df: DataFrame with price data (must have: price_usd, volume_24h, collected_at)
            
        Returns:
            DataFrame with engineered features
        """
        if price_df.empty:
            self.logger.warning("Empty price dataframe provided")
            return pd.DataFrame()
        
        df = price_df.copy()
        
        # Ensure datetime index
        if 'collected_at' in df.columns:
            df['collected_at'] = pd.to_datetime(df['collected_at'])
            df = df.sort_values('collected_at')
        
        self.logger.info(f"Engineering features from {len(df)} price records")
        
        # Price returns
        df = self._add_returns(df)
        
        # Technical indicators
        df = self._add_technical_indicators(df)
        
        # Volatility features
        df = self._add_volatility_features(df)
        
        # Volume features
        df = self._add_volume_features(df)
        
        self.logger.info(f"Created {len(df.columns)} total features")
        return df
    
    def _add_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate price returns over different periods"""
        if 'price_usd' not in df.columns:
            self.logger.warning("price_usd column not found, skipping returns")
            return df
        
        # Simple returns
        df['return_1h'] = df['price_usd'].pct_change(periods=1)
        df['return_6h'] = df['price_usd'].pct_change(periods=6)
        df['return_24h'] = df['price_usd'].pct_change(periods=24)
        df['return_7d'] = df['price_usd'].pct_change(periods=24*7)
        
        # Log returns (more stable for ML)
        df['log_return_1h'] = np.log(df['price_usd'] / df['price_usd'].shift(1))
        df['log_return_24h'] = np.log(df['price_usd'] / df['price_usd'].shift(24))
        
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators"""
        if 'price_usd' not in df.columns:
            return df
        
        price = df['price_usd']
        
        # Simple Moving Averages
        df['sma_7'] = price.rolling(window=7, min_periods=1).mean()
        df['sma_30'] = price.rolling(window=30, min_periods=1).mean()
        df['sma_90'] = price.rolling(window=90, min_periods=1).mean()
        
        # Exponential Moving Averages
        df['ema_7'] = price.ewm(span=7, adjust=False).mean()
        df['ema_30'] = price.ewm(span=30, adjust=False).mean()
        
        # Price position relative to moving averages
        df['price_to_sma_7'] = price / df['sma_7']
        df['price_to_sma_30'] = price / df['sma_30']
        
        # Relative Strength Index (RSI)
        df['rsi_14'] = self._calculate_rsi(price, period=14)
        
        # Bollinger Bands
        df = self._add_bollinger_bands(df, price, period=20, std_dev=2)
        
        # MACD
        df = self._add_macd(df, price)
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _add_bollinger_bands(self, df: pd.DataFrame, price: pd.Series, 
                            period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """Add Bollinger Bands indicators"""
        sma = price.rolling(window=period, min_periods=1).mean()
        std = price.rolling(window=period, min_periods=1).std()
        
        df['bb_upper'] = sma + (std * std_dev)
        df['bb_middle'] = sma
        df['bb_lower'] = sma - (std * std_dev)
        
        # Bollinger Band width
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # Price position within bands
        df['bb_position'] = (price - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df
    
    def _add_macd(self, df: pd.DataFrame, price: pd.Series) -> pd.DataFrame:
        """Add MACD (Moving Average Convergence Divergence)"""
        ema_12 = price.ewm(span=12, adjust=False).mean()
        ema_26 = price.ewm(span=26, adjust=False).mean()
        
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based features"""
        if 'price_usd' not in df.columns:
            return df
        
        # Rolling volatility (standard deviation of returns)
        returns = df['price_usd'].pct_change()
        
        df['volatility_24h'] = returns.rolling(window=24, min_periods=1).std()
        df['volatility_7d'] = returns.rolling(window=24*7, min_periods=1).std()
        
        # Average True Range (ATR) - proxy using simple range
        if 'price_usd' in df.columns:
            high_low = df['price_usd'].rolling(window=14, min_periods=1).max() - \
                       df['price_usd'].rolling(window=14, min_periods=1).min()
            df['atr_14'] = high_low.rolling(window=14, min_periods=1).mean()
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        if 'volume_24h' not in df.columns:
            self.logger.warning("volume_24h not found, skipping volume features")
            return df
        
        volume = df['volume_24h']
        
        # Volume moving averages
        df['volume_ma_7'] = volume.rolling(window=7, min_periods=1).mean()
        df['volume_ma_30'] = volume.rolling(window=30, min_periods=1).mean()
        
        # Volume ratio (current vs average)
        df['volume_ratio_7'] = volume / df['volume_ma_7']
        df['volume_ratio_30'] = volume / df['volume_ma_30']
        
        # Volume trend
        df['volume_change'] = volume.pct_change()
        
        return df