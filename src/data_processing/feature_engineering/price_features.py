"""
Price-based feature engineering
Technical indicators and price-derived features
"""

import pandas as pd

from src.shared.logging import get_logger


class PriceFeatureEngineer:
    """Engineer features from price data"""

    def __init__(self):
        self.logger = get_logger(__name__)

    def create_features(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create price-based features (6 features total)

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
        if "collected_at" in df.columns:
            df["collected_at"] = pd.to_datetime(df["collected_at"])
            df = df.sort_values("collected_at")

        self.logger.info(f"Engineering features from {len(df)} price records")

        # Feature 1: price_usd (already exists)

        # Feature 2: return_24h
        df["return_24h"] = df["price_usd"].pct_change(
            periods=1
        )  # Using 1 period for now (will be 24 with hourly data)

        # Feature 3: volatility_24h
        df["volatility_24h"] = df["price_usd"].pct_change().rolling(window=24, min_periods=1).std()

        # Feature 4: volume_24h (already exists)
        # Just rename if needed
        if "volume_24h" not in df.columns and "volume" in df.columns:
            df["volume_24h"] = df["volume"]

        # Feature 5: rsi_14
        df["rsi_14"] = self._calculate_rsi(df["price_usd"], period=14)

        # Feature 6: sma_7
        df["sma_7"] = df["price_usd"].rolling(window=7, min_periods=1).mean()

        # Keep only essential columns
        feature_cols = [
            "collected_at",
            "symbol",
            "price_usd",
            "return_24h",
            "volatility_24h",
            "volume_24h",
            "rsi_14",
            "sma_7",
        ]
        df = df[[col for col in feature_cols if col in df.columns]]

        self.logger.info(
            "Created 6 price features: price_usd, return_24h, volatility_24h, volume_24h, rsi_14, sma_7"
        )
        return df

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
