"""
SQLAlchemy database models
"""
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class CollectionMetadata(Base):
    """Track data collection runs"""
    __tablename__ = "collection_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    collector_name = Column(String(100), nullable=False)
    collection_type = Column(String(50), nullable=False)  # price, news, social
    status = Column(String(20), nullable=False)  # success, error, running
    
    records_collected = Column(Integer, default=0)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String(500), nullable=True)
    
    __table_args__ = (
        Index('idx_collection_type_time', 'collection_type', 'start_time'),
        Index('idx_collection_status', 'status'),
    )


class PriceData(Base):
    """Cryptocurrency price data"""
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Cryptocurrency identifier
    symbol = Column(String(10), nullable=False)  # BTC, ETH
    name = Column(String(50), nullable=False)  # Bitcoin, Ethereum
    
    # Price data
    price_usd = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    
    # Price changes
    change_1h = Column(Float, nullable=True)
    change_24h = Column(Float, nullable=True)
    change_7d = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(50), nullable=False)  # coingecko, cryptocompare
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_price_symbol_time', 'symbol', 'collected_at'),
        Index('idx_price_source', 'data_source'),
    )


class NewsData(Base):
    """News article data"""
    __tablename__ = "news_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Article identification
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    
    # Content
    content = Column(Text, nullable=False)
    summary = Column(String(1000), nullable=True)
    
    # Metadata
    author = Column(String(200), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    data_source = Column(String(50), nullable=False)  # coindesk, cointelegraph, decrypt
    
    # Processing metadata
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    word_count = Column(Integer, nullable=True)
    
    __table_args__ = (
        Index('idx_news_published', 'published_at'),
        Index('idx_news_source', 'data_source'),
        Index('idx_news_collected', 'collected_at'),
    )


class SentimentData(Base):
    """Sentiment analysis results"""
    __tablename__ = "sentiment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to news article
    news_data_id = Column(Integer, ForeignKey('news_data.id'), nullable=False)
    
    # VADER sentiment scores
    vader_compound = Column(Float, nullable=False)
    vader_positive = Column(Float, nullable=False)
    vader_neutral = Column(Float, nullable=False)
    vader_negative = Column(Float, nullable=False)
    
    # FinBERT sentiment scores (will be added later)
    finbert_compound = Column(Float, nullable=True)
    finbert_positive = Column(Float, nullable=True)
    finbert_neutral = Column(Float, nullable=True)
    finbert_negative = Column(Float, nullable=True)
    
    # Combined scores
    combined_sentiment = Column(Float, nullable=False)
    sentiment_category = Column(String(20), nullable=False)  # positive, negative, neutral
    
    # Processing metadata
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    model_version = Column(String(50), nullable=True)
    
    __table_args__ = (
        Index('idx_sentiment_news', 'news_data_id'),
        Index('idx_sentiment_category', 'sentiment_category'),
        Index('idx_sentiment_processed', 'processed_at'),
    )


class FeatureData(Base):
    """Engineered features for ML models"""
    __tablename__ = "feature_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time identifier
    timestamp = Column(DateTime(timezone=True), nullable=False, unique=True)
    
    # Price features
    price_btc = Column(Float, nullable=True)
    price_return_1h = Column(Float, nullable=True)
    price_return_24h = Column(Float, nullable=True)
    volatility_24h = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    
    # Sentiment features
    sentiment_mean = Column(Float, nullable=True)
    sentiment_std = Column(Float, nullable=True)
    sentiment_positive_ratio = Column(Float, nullable=True)
    news_volume = Column(Integer, nullable=True)
    
    # Technical indicators
    rsi_14 = Column(Float, nullable=True)
    sma_20 = Column(Float, nullable=True)
    ema_12 = Column(Float, nullable=True)
    
    # Target variable (for training)
    price_direction = Column(Integer, nullable=True)  # 1 for up, 0 for down
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_complete = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_feature_timestamp', 'timestamp'),
        Index('idx_feature_complete', 'is_complete'),
        Index('idx_feature_created', 'created_at'),
    )