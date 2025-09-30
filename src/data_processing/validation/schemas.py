"""
Pandera schemas for data validation
Defines strict validation rules for all data types
"""
from datetime import datetime

import pandera as pa # noqa
from pandera import Column, DataFrameSchema, Check


class ValidationSchemas:
    """Collection of Pandera schemas for data validation"""
    
    @staticmethod
    def price_schema() -> DataFrameSchema:
        """
        Schema for price data validation
        
        Returns:
            Pandera DataFrameSchema for price data
        """
        return DataFrameSchema(
            columns={
                "symbol": Column(
                    str,
                    checks=[
                        Check.str_length(min_value=2, max_value=10),
                        Check.isin(['BTC', 'ETH']),  # Only supported symbols
                    ],
                    nullable=False,
                    description="Cryptocurrency symbol"
                ),
                "name": Column(
                    str,
                    checks=[
                        Check.str_length(min_value=3, max_value=50),
                    ],
                    nullable=False,
                    description="Cryptocurrency name"
                ),
                "price_usd": Column(
                    float,
                    checks=[
                        Check.greater_than(0),
                        Check.less_than(1000000),  # Sanity check
                    ],
                    nullable=False,
                    description="Price in USD"
                ),
                "market_cap": Column(
                    float,
                    checks=[
                        Check.greater_than_or_equal_to(0),
                    ],
                    nullable=True,
                    description="Market capitalization"
                ),
                "volume_24h": Column(
                    float,
                    checks=[
                        Check.greater_than_or_equal_to(0),
                    ],
                    nullable=True,
                    description="24-hour trading volume"
                ),
                "change_1h": Column(
                    float,
                    checks=[
                        Check.in_range(-1.0, 1.0),  # -100% to +100%
                    ],
                    nullable=True,
                    description="1-hour price change"
                ),
                "change_24h": Column(
                    float,
                    checks=[
                        Check.in_range(-1.0, 1.0),
                    ],
                    nullable=True,
                    description="24-hour price change"
                ),
                "change_7d": Column(
                    float,
                    checks=[
                        Check.in_range(-1.0, 1.0),
                    ],
                    nullable=True,
                    description="7-day price change"
                ),
                "data_source": Column(
                    str,
                    checks=[
                        Check.isin(['coingecko', 'cryptocompare']),
                    ],
                    nullable=False,
                    description="Data source identifier"
                ),
                "collected_at": Column(
                    datetime,
                    nullable=False,
                    description="Collection timestamp"
                ),
            },
            strict=True,
            coerce=True,
        )
    
    @staticmethod
    def news_schema() -> DataFrameSchema:
        """
        Schema for news data validation
        
        Returns:
            Pandera DataFrameSchema for news data
        """
        return DataFrameSchema(
            columns={
                "title": Column(
                    str,
                    checks=[
                        Check.str_length(min_value=10, max_value=500),
                    ],
                    nullable=False,
                    description="Article title"
                ),
                "url": Column(
                    str,
                    checks=[
                        Check.str_startswith('http'),
                        Check.str_length(min_value=10, max_value=1000),
                    ],
                    nullable=False,
                    description="Article URL"
                ),
                "content": Column(
                    str,
                    checks=[
                        Check.str_length(min_value=50),
                    ],
                    nullable=False,
                    description="Article content"
                ),
                "summary": Column(
                    str,
                    nullable=True,
                    description="Article summary"
                ),
                "author": Column(
                    str,
                    nullable=True,
                    description="Article author"
                ),
                "published_at": Column(
                    datetime,
                    nullable=True,
                    description="Publication timestamp"
                ),
                "data_source": Column(
                    str,
                    checks=[
                        Check.isin(['coindesk', 'cointelegraph', 'decrypt']),
                    ],
                    nullable=False,
                    description="News source"
                ),
                "collected_at": Column(
                    datetime,
                    nullable=False,
                    description="Collection timestamp"
                ),
                "word_count": Column(
                    int,
                    checks=[
                        Check.greater_than_or_equal_to(0),
                    ],
                    nullable=True,
                    description="Word count"
                ),
            },
            strict=True,
            coerce=True,
        )


class DataValidator:
    """Validator class using Pandera schemas"""
    
    def __init__(self):
        self.schemas = ValidationSchemas()
    
    def validate_price_data(self, data: list) -> bool:
        """
        Validate price data against Pandera schema
        
        Args:
            data: List of price records
            
        Returns:
            True if validation passes
            
        Raises:
            pa.errors.SchemaError: If validation fails
        """
        import pandas as pd
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Validate against schema
        schema = self.schemas.price_schema()
        _ = schema.validate(df, lazy=False)
        
        return True
    
    def validate_news_data(self, data: list) -> bool:
        """
        Validate news data against Pandera schema
        
        Args:
            data: List of news records
            
        Returns:
            True if validation passes
            
        Raises:
            pa.errors.SchemaError: If validation fails
        """
        import pandas as pd
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Validate against schema
        schema = self.schemas.news_schema()
        _ = schema.validate(df, lazy=False)
        
        return True