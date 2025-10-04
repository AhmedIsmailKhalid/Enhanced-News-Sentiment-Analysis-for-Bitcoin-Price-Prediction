# Phase 2 Implementation: Sentiment Analysis & Feature Engineering

**Status:** ✅ Complete  
**Date Completed:** October 3, 2025  
**Implementation Time:** ~4 days

---

## Overview

Phase 2 establishes the complete feature engineering pipeline for Bitcoin sentiment analysis. The system processes news articles with dual sentiment models (VADER + FinBERT) and creates two separate feature sets for model comparison, combining sentiment features with price-based technical indicators and temporal patterns.

---

## Phase 2A: Sentiment Analysis Implementation

### Core Components

#### **1. Base Sentiment Analyzer Framework**
- **File:** `src/data_processing/text_processing/base_sentiment.py`
- **Purpose:** Abstract base class for all sentiment analyzers
- **Key Methods:**
  - `analyze(text)` - Abstract method for sentiment analysis
  - `get_compound_score(text)` - Get single sentiment score
  - `categorize_sentiment(score)` - Categorize as positive/negative/neutral

#### **2. VADER Sentiment Analyzer**
- **File:** `src/data_processing/text_processing/vader_analyzer.py`
- **Model:** VADER (Valence Aware Dictionary and sEntiment Reasoner)
- **Characteristics:**
  - Rule-based lexicon approach
  - Fast inference (<10ms per article)
  - No model drift concerns
  - Optimized for social media and news text
- **Output Scores:**
  - `compound`: Overall sentiment (-1 to 1)
  - `positive`: Positive probability (0 to 1)
  - `neutral`: Neutral probability (0 to 1)
  - `negative`: Negative probability (0 to 1)

#### **3. FinBERT Sentiment Analyzer**
- **File:** `src/data_processing/text_processing/finbert_analyzer.py`
- **Model:** ProsusAI/finbert (BERT-base fine-tuned on financial data)
- **Characteristics:**
  - Transformer-based deep learning (110M parameters)
  - 50-100ms inference time
  - Financial domain-specific understanding
  - Trained on Reuters, Bloomberg financial text
- **Output Scores:**
  - `compound`: Overall sentiment (-1 to 1)
  - `positive`: Positive probability (0 to 1)
  - `neutral`: Neutral probability (0 to 1)
  - `negative`: Negative probability (0 to 1)
  - `confidence`: Model confidence (0 to 1)

#### **4. Unified Sentiment Processor**
- **File:** `src/data_processing/text_processing/sentiment_processor.py`
- **Purpose:** Orchestrate both analyzers and manage database storage
- **Key Features:**
  - Processes all articles with both VADER and FinBERT
  - Stores separate scores for each model
  - Calculates combined sentiment (average of both)
  - Batch processing with automatic commits
  - Multi-database support (local, NeonDB production, NeonDB backup)

### Database Schema Updates

#### **SentimentData Model Enhancements**
```python
class SentimentData(Base):
    # VADER scores
    vader_compound = Column(Float, nullable=False)
    vader_positive = Column(Float, nullable=False)
    vader_neutral = Column(Float, nullable=False)
    vader_negative = Column(Float, nullable=False)
    
    # FinBERT scores
    finbert_compound = Column(Float, nullable=True)
    finbert_positive = Column(Float, nullable=True)
    finbert_neutral = Column(Float, nullable=True)
    finbert_negative = Column(Float, nullable=True)
    finbert_confidence = Column(Float, nullable=True)
    
    # Combined metrics
    combined_sentiment = Column(Float, nullable=False)
    sentiment_category = Column(String(20), nullable=False)
    
    # Metadata
    processed_at = Column(DateTime(timezone=True))
    model_version = Column(String(100), nullable=True)
```

### Integration with Data Collection

#### **Updated Collection Scripts**
- `scripts/data_collection/collect_and_process_all.py` - Local pipeline with sentiment
- `scripts/data_collection/collect_and_process_neondb.py` - Production pipeline with sentiment

#### **Automated Workflow**
1. Collect price data
2. Collect news articles
3. **Process sentiment with both VADER and FinBERT**
4. Store results to database

### Test Scripts

#### **VADER Analyzer Test**
- **File:** `scripts/data_processing/test_vader_analyzer.py`
- **Purpose:** Validate VADER with predefined test cases
- **Tests:** 5 different sentiment scenarios

#### **Sentiment Processor Test**
- **File:** `scripts/data_processing/test_sentiment_processor.py`
- **Purpose:** End-to-end sentiment processing with real articles
- **Validation:** Statistics, category distribution, sample results

#### **Model Comparison Test**
- **File:** `scripts/data_processing/compare_sentiment_methods.py`
- **Purpose:** Compare VADER vs FinBERT on real articles
- **Output:** Side-by-side scores, agreement analysis

---

## Phase 2B: Feature Engineering Implementation

### Architecture Overview

Two completely separate feature sets are created:
1. **VADER Feature Set:** VADER sentiment + Price features + Temporal features
2. **FinBERT Feature Set:** FinBERT sentiment + Price features + Temporal features

This enables independent model comparison without cross-contamination.

### Core Components

#### **1. Price Feature Engineering**
- **File:** `src/data_processing/feature_engineering/price_features.py`
- **Total Features:** 40+ price-based indicators

**Feature Categories:**

**Price Returns:**
- Simple returns: 1h, 6h, 24h, 7d
- Log returns: 1h, 24h (more stable for ML)

**Technical Indicators:**
- Simple Moving Averages (SMA): 7, 30, 90 periods
- Exponential Moving Averages (EMA): 7, 30 periods
- Relative Strength Index (RSI): 14 periods
- Bollinger Bands: upper, middle, lower, width, position
- MACD: line, signal, histogram

**Volatility Features:**
- Rolling volatility: 24h, 7d
- Average True Range (ATR): 14 periods

**Volume Features:**
- Volume moving averages: 7, 30 periods
- Volume ratios: current vs 7-day, 30-day average
- Volume change rate

#### **2. Sentiment Feature Engineering**
- **File:** `src/data_processing/feature_engineering/sentiment_features.py`
- **Separate Methods:**
  - `create_vader_features()` - VADER-specific features (48 features)
  - `create_finbert_features()` - FinBERT-specific features (53 features)

**VADER Features (48 total):**

**Hourly Aggregations:**
- Mean sentiment: 1h, 6h, 24h windows
- Standard deviation: 1h, 6h, 24h windows
- Min/Max sentiment: 1h, 6h, 24h windows
- Range: 1h, 6h, 24h windows

**Sentiment Changes:**
- Change: 1h, 6h, 24h periods
- Rate of change: 1h, 24h periods

**News Volume:**
- Article counts: 1h, 6h, 24h windows
- News velocity (change in article count)

**Sentiment Momentum:**
- Sentiment moving averages: 7, 30 periods
- Position above/below moving averages
- Sentiment streak (consecutive positive/negative)

**Extreme Sentiment:**
- Extreme positive flag (>0.5)
- Extreme negative flag (<-0.5)
- Extreme count: 6h, 24h windows

**FinBERT Features (53 total):**
- All VADER features (48)
- **Plus confidence-weighted features (5):**
  - Confidence-weighted sentiment
  - Weighted mean: 6h, 24h windows
  - Average confidence: 6h, 24h windows

#### **3. Temporal Feature Engineering**
- **File:** `src/data_processing/feature_engineering/temporal_features.py`
- **Total Features:** 23 temporal indicators

**Time Components:**
- Hour of day (0-23)
- Day of week (0-6)
- Day of month (1-31)
- Month (1-12)
- Week of year (1-52)
- Quarter (1-4)

**Cyclical Encodings (preserves cyclic nature):**
- Hour: sin/cos transformations
- Day of week: sin/cos transformations
- Day of month: sin/cos transformations
- Month: sin/cos transformations

**Time Flags:**
- Weekend indicator
- Business hours (9 AM - 5 PM UTC)
- US market hours (14:30 - 21:00 UTC)
- Asian market hours (0:00 - 8:00 UTC)
- European market hours (8:00 - 16:30 UTC)
- Month start/end indicators
- Quarter start/end indicators

#### **4. Feature Combiner**
- **File:** `src/data_processing/feature_engineering/feature_combiner.py`
- **Purpose:** Merge all features into two separate datasets

**Process:**
1. Load price data from database
2. Load sentiment data (with both VADER and FinBERT scores)
3. Engineer price features (shared by both datasets)
4. Engineer VADER sentiment features
5. Engineer FinBERT sentiment features
6. Engineer temporal features (shared by both datasets)
7. Merge into VADER dataset (VADER + Price + Temporal)
8. Merge into FinBERT dataset (FinBERT + Price + Temporal)

**Output:**
- VADER dataset: 107 features
- FinBERT dataset: 112 features

#### **5. Feature Storage Manager**
- **File:** `src/data_processing/feature_engineering/feature_storage.py`
- **Purpose:** Store features in database with JSON format

**Key Features:**
- Converts pandas NaN/NaT/inf to None for JSON serialization
- Handles numpy type conversion to Python native types
- Batch commits every 50 records
- Updates existing or inserts new based on timestamp
- Separate storage for VADER and FinBERT feature sets

### Database Schema

#### **FeatureData Model**
```python
class FeatureData(Base):
    __tablename__ = "feature_data"
    
    id = Column(Integer, primary_key=True)
    feature_set_name = Column(String(50), nullable=False)  # 'vader' or 'finbert'
    feature_version = Column(String(50), nullable=False)   # 'v1.0.0'
    timestamp = Column(DateTime(timezone=True), nullable=False)
    features = Column(JSON, nullable=False)  # All features as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Benefits of JSON Storage:**
- Flexible schema (no column limit)
- Easy to add/remove features
- Maintains feature separation (VADER vs FinBERT)
- Version tracking for reproducibility

### Integration with Data Collection Pipeline

#### **Updated Pipeline Steps**
1. **Price Collection** - CoinGecko API data
2. **News Collection** - Multi-source RSS feeds
3. **Sentiment Processing** - VADER + FinBERT analysis
4. **Feature Engineering** - Create and store feature sets

#### **Collection Scripts Updated**
- `scripts/data_collection/collect_and_process_all.py` - Added Step 4
- `scripts/data_collection/collect_and_process_neondb.py` - Added Step 4

#### **GitHub Actions Workflow**
- Automatically runs complete 4-step pipeline every 15 minutes
- Features accumulate in NeonDB production database
- No manual intervention required

### Test Scripts

#### **Feature Engineering Test**
- **File:** `scripts/data_processing/test_feature_engineering.py`
- **Purpose:** Validate complete feature engineering pipeline
- **Output:**
  - Feature set shapes and statistics
  - Sample features from each category
  - Data quality metrics
  - Sample CSV exports

---

## Challenges & Solutions

### Challenge 1: Model Integration Strategy

**Problem:** How to integrate both VADER and FinBERT without mixing their outputs?

**Solution:**
- Store scores in completely separate columns
- Create separate feature engineering methods
- Maintain two distinct feature sets throughout pipeline
- Use `feature_set_name` column to distinguish datasets

---

### Challenge 2: JSON Serialization Errors

**Problem:** Pandas NaN, NaT, and numpy types not JSON-serializable for database storage.

**Error:**
```
TypeError: Object of type NaTType is not JSON serializable
```

**Solution:**
```python
# Convert all problematic types before JSON storage
features_dict = {
    k: (None if pd.isna(v) or (isinstance(v, float) and np.isinf(v)) else 
        (float(v) if isinstance(v, (np.integer, np.floating)) else v))
    for k, v in features_dict.items()
}
```

**Lesson:** Always sanitize pandas/numpy data types before JSON serialization.

---

### Challenge 3: Feature Set Alignment

**Problem:** Price data, sentiment data, and temporal features on different timestamps.

**Solution:**
- Use `collected_at` as primary timestamp across all data
- Merge dataframes on timestamp with left join
- Handle missing values appropriately (forward-fill or None)
- Document alignment strategy for reproducibility

---

### Challenge 4: FinBERT Processing Speed

**Problem:** FinBERT takes 50-100ms per article, too slow for 500 articles in GitHub Actions.

**Initial Concern:** Workflow timeout with large article volumes.

**Solution:**
- Both models process successfully in batch mode
- Batch commits every 10 articles for reliability
- Total processing time acceptable (~2 minutes for 100 articles)
- No optimization needed at current scale

---

## Production Statistics

### Data Collection Performance

**As of Phase 2 Completion:**

**NeonDB Production:**
- Price Records: 69
- News Articles: 185
- Sentiment Records: 185 (both VADER and FinBERT)
- Feature Records: 138 (69 VADER + 69 FinBERT)

**GitHub Actions:**
- Workflow runs: Every 15 minutes
- Success rate: 100% (after Phase 2A/2B integration)
- Average execution time: ~3-4 minutes per run

**Feature Engineering:**
- VADER features per record: 107
- FinBERT features per record: 112
- Feature version: v1.0.0
- Date range: 2025-10-03 03:23 to 2025-10-03 23:51 (20 hours)

### Model Performance Characteristics

**VADER:**
- Average compound score: ~0.466 (positive bias observed)
- Processing speed: <10ms per article
- Categories: 12 positive, 3 neutral, 2 negative (from test sample)

**FinBERT:**
- More conservative scoring (closer to neutral)
- Processing speed: 50-100ms per article
- Better financial domain understanding
- Confidence scores average: 0.7-0.9

**Agreement Rate:**
- VADER vs FinBERT agreement: ~40% (2 out of 5 in comparison test)
- Shows models capture different aspects
- Validates dual-model approach for comprehensive sentiment

---

## Test Files & Usage

### Sentiment Analysis Tests

#### **Test VADER Analyzer**
```bash
poetry run python scripts/data_processing/test_vader_analyzer.py
```
**Validates:** VADER sentiment on predefined test cases

#### **Test Sentiment Processor**
```bash
poetry run python scripts/data_processing/test_sentiment_processor.py
```
**Validates:** End-to-end sentiment processing with database storage

#### **Compare Sentiment Methods**
```bash
poetry run python scripts/data_processing/compare_sentiment_methods.py
```
**Validates:** VADER vs FinBERT comparison on real articles

### Feature Engineering Tests

#### **Test Complete Feature Pipeline**
```bash
poetry run python scripts/data_processing/test_feature_engineering.py
```
**Validates:**
- Price feature engineering
- VADER sentiment feature engineering
- FinBERT sentiment feature engineering
- Temporal feature engineering
- Feature combining and storage
- Exports sample CSV files

### Production Pipeline Tests

#### **Test Local Pipeline**
```bash
poetry run python scripts/data_collection/collect_and_process_all.py
```
**Steps:** Price → News → Sentiment → Features (local database)

#### **Test NeonDB Pipeline**
```bash
poetry run python scripts/data_collection/collect_and_process_neondb.py
```
**Steps:** Price → News → Sentiment → Features (NeonDB production)

---

## Verification Queries

### Check Sentiment Processing

**Local PostgreSQL:**
```bash
docker exec -it bitcoin_sentiment_postgres psql -U bitcoin_user -d bitcoin_sentiment_dev -c "
SELECT 
    COUNT(*) as total_articles,
    COUNT(DISTINCT s.id) as with_sentiment
FROM news_data n 
LEFT JOIN sentiment_data s ON n.id = s.news_data_id;
"
```

**View Sample Results:**
```bash
docker exec -it bitcoin_sentiment_postgres psql -U bitcoin_user -d bitcoin_sentiment_dev -c "
SELECT 
    n.title, 
    s.vader_compound, 
    s.finbert_compound, 
    s.finbert_confidence,
    s.sentiment_category 
FROM news_data n 
JOIN sentiment_data s ON n.id = s.news_data_id 
ORDER BY s.processed_at DESC 
LIMIT 5;
"
```

### Check Feature Engineering

**NeonDB SQL Editor:**
```sql
SELECT 
    feature_set_name,
    feature_version,
    COUNT(*) as record_count,
    MIN(timestamp) as earliest,
    MAX(timestamp) as latest
FROM feature_data
GROUP BY feature_set_name, feature_version;
```

**Expected Output:**
- vader: v1.0.0, 69 records
- finbert: v1.0.0, 69 records

**View Sample Features:**
```sql
SELECT 
    feature_set_name,
    timestamp,
    features->>'price_usd' as price,
    features->>'vader_compound' as vader_sentiment,
    features->>'finbert_compound' as finbert_sentiment
FROM feature_data
WHERE feature_set_name = 'vader'
ORDER BY timestamp DESC
LIMIT 5;
```

---

## Architecture Decisions

### 1. Dual-Model Strategy

**Decision:** Process every article with both VADER and FinBERT

**Rationale:**
- VADER captures social media/news style sentiment (rule-based)
- FinBERT captures financial domain-specific sentiment (deep learning)
- Different approaches provide complementary insights
- Enables direct model comparison
- Combined score leverages strengths of both

**Alternative Considered:** Use only one model
**Why Rejected:** Single model misses nuances; dual approach provides richer features

---

### 2. Separate Feature Sets

**Decision:** Create two completely independent feature sets

**Rationale:**
- Enable fair model comparison (VADER vs FinBERT)
- No cross-contamination between sentiment approaches
- Share price and temporal features (identical baseline)
- Measure pure impact of sentiment model choice

**Alternative Considered:** Single feature set with all sentiment scores
**Why Rejected:** Would prevent clean model comparison; mixing creates confounding

---

### 3. JSON Feature Storage

**Decision:** Store features as JSON instead of individual columns

**Rationale:**
- Schema flexibility (no column limit)
- Easy to add/remove features without migrations
- Maintain feature versioning
- Simplify feature set separation
- No performance penalty for our use case

**Alternative Considered:** Individual columns for each feature
**Why Rejected:** Would need 100+ columns; schema changes for new features; harder to maintain

---

### 4. Feature Engineering Frequency

**Decision:** Run feature engineering on every collection cycle (15 minutes)

**Rationale:**
- Keep features fresh and up-to-date
- Minimal computational overhead (3-4 seconds)
- Enables real-time ML applications
- Automated accumulation of training data

**Alternative Considered:** Batch feature engineering daily
**Why Rejected:** Would delay ML readiness; real-time value lost

---

## Key Takeaways

✅ **Dual Sentiment Models:** VADER and FinBERT provide complementary sentiment analysis

✅ **Separate Feature Sets:** Two independent datasets enable clean model comparison

✅ **Comprehensive Features:** 107-112 features per dataset (price + sentiment + temporal)

✅ **Automated Pipeline:** Complete 4-step pipeline runs every 15 minutes automatically

✅ **Production Ready:** Features accumulating in NeonDB for model training

✅ **Flexible Storage:** JSON-based feature storage enables easy schema evolution

✅ **Well Tested:** Comprehensive test suite validates all components

✅ **Scalable Design:** Architecture supports growth without major refactoring

---

## Next Steps (Phase 3)

With Phase 2 complete, the foundation is ready for:

1. **ML Model Training**
   - Train models on VADER feature set
   - Train models on FinBERT feature set
   - Compare performance metrics

2. **Model Selection**
   - Evaluate which sentiment approach performs better
   - Determine optimal feature combinations
   - Select best model for production

3. **Model Deployment**
   - Deploy winning model to production API
   - Set up prediction endpoints
   - Implement model versioning

4. **MLOps Automation**
   - Automated model retraining
   - Performance monitoring
   - Drift detection

---

**Phase 2 Status: ✅ Complete and Production-Ready**

The sentiment analysis and feature engineering pipeline is fully automated, collecting data every 15 minutes, processing sentiment with both models, and engineering features for ML model training. Both VADER and FinBERT feature sets are accumulating in production, ready for Phase 3 model development.