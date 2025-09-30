"""
Data validation for collected data using Pandera
"""
from typing import Any, Dict, List

from src.shared.logging import get_logger

# Import Pandera validator
try:
    from src.data_processing.validation.schemas import DataValidator as PanderaValidator
    PANDERA_AVAILABLE = True
except ImportError:
    PANDERA_AVAILABLE = False


class DataValidator:
    """Data validator with Pandera integration"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        if PANDERA_AVAILABLE:
            self.pandera_validator = PanderaValidator()
            self.logger.info("Pandera validation enabled")
        else:
            self.pandera_validator = None
            self.logger.warning("Pandera not available, using basic validation")
    
    def validate_price_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate price data
        
        Args:
            data: List of price data records
            
        Returns:
            True if all records are valid
        """
        if not data:
            self.logger.error("No data to validate")
            return False
        
        # Use Pandera if available
        if PANDERA_AVAILABLE and self.pandera_validator:
            try:
                self.pandera_validator.validate_price_data(data)
                self.logger.info(f"Pandera validation passed for {len(data)} price records")
                return True
            except Exception as e:
                self.logger.error(f"Pandera validation failed: {e}")
                return False
        
        # Fallback to basic validation
        return self._basic_price_validation(data)
    
    def validate_news_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate news data
        
        Args:
            data: List of news data records
            
        Returns:
            True if all records are valid
        """
        if not data:
            self.logger.error("No data to validate")
            return False
        
        # Use Pandera if available
        if PANDERA_AVAILABLE and self.pandera_validator:
            try:
                self.pandera_validator.validate_news_data(data)
                self.logger.info(f"Pandera validation passed for {len(data)} news records")
                return True
            except Exception as e:
                self.logger.error(f"Pandera validation failed: {e}")
                return False
        
        # Fallback to basic validation
        return self._basic_news_validation(data)
    
    def _basic_price_validation(self, data: List[Dict[str, Any]]) -> bool:
        """Basic price validation (fallback)"""
        required_fields = ['symbol', 'name', 'price_usd', 'data_source']
        
        for i, record in enumerate(data):
            for field in required_fields:
                if field not in record:
                    self.logger.error(f"Record {i}: Missing field '{field}'")
                    return False
            
            if not isinstance(record['price_usd'], (int, float)) or record['price_usd'] <= 0:
                self.logger.error(f"Record {i}: Invalid price_usd")
                return False
        
        self.logger.info(f"Basic validation passed for {len(data)} price records")
        return True
    
    def _basic_news_validation(self, data: List[Dict[str, Any]]) -> bool:
        """Basic news validation (fallback)"""
        required_fields = ['title', 'url', 'content', 'data_source']
        
        for i, record in enumerate(data):
            for field in required_fields:
                if field not in record:
                    self.logger.error(f"Record {i}: Missing field '{field}'")
                    return False
            
            if len(record['title']) < 10:
                self.logger.error(f"Record {i}: Title too short")
                return False
            
            if len(record['content']) < 50:
                self.logger.error(f"Record {i}: Content too short")
                return False
        
        self.logger.info(f"Basic validation passed for {len(data)} news records")
        return True