"""
Price data collector using CoinGecko API
"""
# pyright: reportMissingImports=false

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.data_collection.collectors.base_collector import BaseCollector
from src.data_collection.validators.data_validator import DataValidator
from src.shared.models import PriceData

load_dotenv(".env.dev")


class PriceCollector(BaseCollector):
    """Collect cryptocurrency price data from CoinGecko"""

    def __init__(self, target_db: str = "local"):
        super().__init__(name="PriceCollector", collection_type="price", target_db=target_db)
        self.validator = DataValidator()

        # CoinGecko configuration
        self.base_url = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3")
        self.api_key = os.getenv("COINGECKO_API_KEY")

        # Supported cryptocurrencies
        self.supported_coins = {"bitcoin": "BTC"}

        # Request timeout
        self.timeout = 30

    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Collect price data from CoinGecko API

        Returns:
            List of price records
        """
        try:
            coin_ids = ",".join(self.supported_coins.keys())
            url = f"{self.base_url}/simple/price"

            params = {
                "ids": coin_ids,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true",
            }

            # Add API key if available
            if self.api_key:
                params["x_cg_demo_api_key"] = self.api_key

            self.logger.debug(f"Requesting: {url}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Transform to standard format
            price_records = []
            collection_time = datetime.utcnow()

            for coin_id, coin_data in data.items():
                if coin_id not in self.supported_coins:
                    continue

                record = {
                    "symbol": self.supported_coins[coin_id],
                    "name": coin_id.capitalize(),
                    "price_usd": float(coin_data.get("usd", 0)),
                    "market_cap": self._safe_float(coin_data.get("usd_market_cap")),
                    "volume_24h": self._safe_float(coin_data.get("usd_24h_vol")),
                    "change_1h": None,  # Not available in simple API
                    "change_24h": self._safe_percentage(coin_data.get("usd_24h_change")),
                    "change_7d": None,  # Not available in simple API
                    "data_source": "coingecko",
                    "collected_at": collection_time,
                }

                price_records.append(record)

            return price_records

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Data collection failed: {e}")
            raise

    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate price data using validator"""
        return self.validator.validate_price_data(data)

    def store_data(self, data: List[Dict[str, Any]], db: Session) -> int:
        """
        Store price data to database

        Args:
            data: List of validated price records
            db: Database session

        Returns:
            Number of records stored
        """
        stored_count = 0

        for record in data:
            price_data = PriceData(
                symbol=record["symbol"],
                name=record["name"],
                price_usd=record["price_usd"],
                market_cap=record["market_cap"],
                volume_24h=record["volume_24h"],
                change_1h=record["change_1h"],
                change_24h=record["change_24h"],
                change_7d=record["change_7d"],
                data_source=record["data_source"],
                collected_at=record["collected_at"],
            )

            db.add(price_data)
            stored_count += 1

        db.commit()
        return stored_count

    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None

    def _safe_percentage(self, value: Any) -> Optional[float]:
        """Safely convert percentage to decimal"""
        try:
            return float(value) / 100 if value is not None else None
        except (ValueError, TypeError):
            return None
