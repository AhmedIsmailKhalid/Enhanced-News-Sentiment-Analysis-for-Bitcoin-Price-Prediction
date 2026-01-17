"""
Data validation for collected data
Simple validation without external dependencies
"""
from typing import Any, Dict, List

from src.shared.logging import get_logger


class DataValidator:
    """Simple data validator for collected data"""

    def __init__(self):
        self.logger = get_logger(__name__)

    def validate_price_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate price data records

        Args:
            data: List of price data records

        Returns:
            True if all records are valid
        """
        if not data:
            return False

        required_fields = ["symbol", "name", "price_usd", "data_source"]

        for i, record in enumerate(data):
            # Check required fields exist
            for field in required_fields:
                if field not in record:
                    self.logger.error(f"Record {i}: Missing required field '{field}'")
                    return False

            # Validate data types and ranges
            if not isinstance(record["price_usd"], (int, float)) or record["price_usd"] <= 0:
                self.logger.error(f"Record {i}: Invalid price_usd value")
                return False

            if record["market_cap"] is not None:
                if not isinstance(record["market_cap"], (int, float)) or record["market_cap"] < 0:
                    self.logger.error(f"Record {i}: Invalid market_cap value")
                    return False

            if record["volume_24h"] is not None:
                if not isinstance(record["volume_24h"], (int, float)) or record["volume_24h"] < 0:
                    self.logger.error(f"Record {i}: Invalid volume_24h value")
                    return False

        return True

    def validate_news_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate news data records

        Args:
            data: List of news data records

        Returns:
            True if all records are valid
        """
        if not data:
            return False

        required_fields = ["title", "url", "content", "data_source"]

        for i, record in enumerate(data):
            # Check required fields
            for field in required_fields:
                if field not in record:
                    self.logger.error(f"Record {i}: Missing required field '{field}'")
                    return False

            # Validate field values
            if not record["title"] or len(record["title"]) < 10:
                self.logger.error(f"Record {i}: Title too short")
                return False

            if not record["content"] or len(record["content"]) < 50:
                self.logger.error(f"Record {i}: Content too short")
                return False

            if not record["url"].startswith("http"):
                self.logger.error(f"Record {i}: Invalid URL")
                return False

        return True
