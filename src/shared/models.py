"""
SQLAlchemy database models
"""
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
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
        Index("idx_collection_type_time", "collection_type", "start_time"),
        Index("idx_collection_status", "status"),
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
        Index("idx_price_symbol_time", "symbol", "collected_at"),
        Index("idx_price_source", "data_source"),
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
    summary = Column(Text, nullable=True)

    # Metadata
    author = Column(String(200), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    data_source = Column(String(50), nullable=False)  # coindesk, cointelegraph, decrypt

    # Processing metadata
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    word_count = Column(Integer, nullable=True)

    __table_args__ = (
        Index("idx_news_published", "published_at"),
        Index("idx_news_source", "data_source"),
        Index("idx_news_collected", "collected_at"),
    )


class SentimentData(Base):
    __tablename__ = "sentiment_data"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to news article
    news_data_id = Column(Integer, ForeignKey("news_data.id"), nullable=False)

    # VADER sentiment scores
    vader_compound = Column(Float, nullable=False)
    vader_positive = Column(Float, nullable=False)
    vader_neutral = Column(Float, nullable=False)
    vader_negative = Column(Float, nullable=False)

    # FinBERT sentiment scores
    finbert_compound = Column(Float, nullable=True)
    finbert_positive = Column(Float, nullable=True)
    finbert_neutral = Column(Float, nullable=True)
    finbert_negative = Column(Float, nullable=True)
    finbert_confidence = Column(Float, nullable=True)  # Add this line

    # Combined scores
    combined_sentiment = Column(Float, nullable=False)
    sentiment_category = Column(String(20), nullable=False)

    # Processing metadata
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    model_version = Column(String(100), nullable=True)  # Add this line

    # Create indexes
    __table_args__ = (
        Index("idx_sentiment_article", "news_data_id"),
        Index("idx_sentiment_category", "sentiment_category"),
        Index("idx_sentiment_score", "combined_sentiment"),
    )


class FeatureData(Base):
    __tablename__ = "feature_data"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Feature set identifier
    feature_set_name = Column(String(50), nullable=False)  # 'vader' or 'finbert'
    feature_version = Column(String(50), nullable=False)  # version tracking

    # Timestamp for this feature row
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Store features as JSON for flexibility
    features = Column(JSON, nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_feature_set_timestamp", "feature_set_name", "timestamp"),
        Index("idx_feature_version", "feature_version"),
    )

    def __repr__(self):
        return f"<FeatureData(set={self.feature_set_name}, timestamp={self.timestamp})>"


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Prediction metadata
    feature_set = Column(String(50), nullable=False)  # 'vader' or 'finbert'
    model_type = Column(String(50), nullable=False)  # 'random_forest', 'logistic_regression', etc.
    model_version = Column(String(100), nullable=False)  # Timestamp from model filename

    # Prediction details
    prediction = Column(Integer, nullable=False)  # 0 (down) or 1 (up)
    probability_down = Column(Float, nullable=False)
    probability_up = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)

    # Features used (snapshot for reproducibility)
    features_json = Column(JSON, nullable=False)  # All features used for this prediction
    feature_count = Column(Integer, nullable=False)

    # Actual outcome (for performance tracking)
    actual_direction = Column(Integer, nullable=True)  # Filled in later when we know the outcome
    prediction_correct = Column(Boolean, nullable=True)  # True/False when outcome known

    # Bitcoin price context
    bitcoin_price_at_prediction = Column(Float, nullable=True)
    bitcoin_price_1h_later = Column(Float, nullable=True)
    price_change_pct = Column(Float, nullable=True)

    # Performance metrics
    response_time_ms = Column(Float, nullable=False)
    cached_features = Column(Boolean, nullable=False)

    # Timestamps
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    outcome_recorded_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index("idx_prediction_feature_set", "feature_set"),
        Index("idx_prediction_model_type", "model_type"),
        Index("idx_prediction_timestamp", "predicted_at"),
        Index("idx_prediction_correctness", "prediction_correct"),
    )

    def __repr__(self):
        return f"<PredictionLog(feature_set={self.feature_set}, model={self.model_type}, prediction={self.prediction}, correct={self.prediction_correct})>"
