# Phase 1 Implementation: Data Collection Pipeline

**Status:** ✅ Complete  
**Date Completed:** September 30, 2025  
**Implementation Time:** ~6 hours

---

## Overview

Phase 1 establishes a production-ready data collection pipeline for Bitcoin sentiment analysis. The system collects cryptocurrency price data and news articles from multiple sources, validates data quality using Pandera schemas, and stores data in both local PostgreSQL and NeonDB (production/backup branches).

---

## Implemented Components

### 1. Core Infrastructure

#### **Centralized Logging System**
- **File:** `src/shared/logging.py`
- **Purpose:** Application-wide logging configuration
- **Features:**
  - Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Console and file output support
  - External library noise reduction
  - Structured log formatting with timestamps and function names

#### **Database Models & Schema**
- **File:** `src/shared/models.py`
- **Tables Created:**
  - `collection_metadata` - Tracks all collection runs with status and error messages
  - `price_data` - Cryptocurrency price, market cap, volume, percentage changes
  - `news_data` - Article content, metadata, source attribution
  - `sentiment_data` - Placeholder for future sentiment analysis results
  - `feature_data` - Placeholder for engineered ML features
- **Key Features:**
  - Foreign key relationships (sentiment_data → news_data)
  - Proper indexing for query performance
  - Unique constraints (news URL) to prevent duplicates
  - Server-default timestamps

#### **Multi-Database Support**
- **File:** `src/shared/database.py`
- **Supported Databases:**
  - Local PostgreSQL (Docker) for development
  - NeonDB Production branch for live data
  - NeonDB Backup branch for disaster recovery
- **Features:**
  - Connection pooling with `pool_pre_ping` for reliability
  - Session management with automatic cleanup
  - Environment-based configuration

---

### 2. Base Collector Framework

#### **Abstract BaseCollector Class**
- **File:** `src/data_collection/collectors/base_collector.py`
- **Purpose:** Standardized workflow for all data collectors
- **Key Features:**
  - Abstract methods enforcing consistent collector interface
  - Multi-database support via `target_db` parameter
  - Automatic metadata tracking for every collection run
  - Comprehensive error handling with graceful degradation
  - Transaction management with proper rollback

#### **Workflow Steps:**
1. Create metadata record (status: "running")
2. Collect data from external source
3. Validate collected data
4. Store validated data to database
5. Update metadata (status: "success" or "error")
6. Log comprehensive status information

---

### 3. Data Collectors

#### **PriceCollector**
- **File:** `src/data_collection/collectors/price_collector.py`
- **Data Source:** CoinGecko API
- **Collection Frequency:** Every 15 minutes (via GitHub Actions)
- **Data Points:**
  - Symbol (BTC)
  - Current price in USD
  - Market capitalization
  - 24-hour trading volume
  - 24-hour percentage change
- **Features:**
  - 30-second request timeout
  - Safe type conversion with null handling
  - Percentage normalization (API returns %, converts to decimal)
  - Support for API key (optional, not required for free tier)

#### **NewsCollector**
- **File:** `src/data_collection/collectors/news_collector.py`
- **Data Sources:**
  - CoinDesk RSS feed
  - Cointelegraph RSS feed
  - Decrypt RSS feed
- **Collection Strategy:**
  - Configurable articles per source (default: 5, GitHub Actions: 500)
  - Full article content extraction via BeautifulSoup
  - Multiple CSS selector fallbacks for content extraction
  - Duplicate URL detection and prevention
- **Features:**
  - Rate limiting: 3 seconds between sources, 0.5 seconds between articles
  - HTML tag and entity removal
  - Whitespace normalization
  - Word count calculation
  - Published date parsing with fallback
  - Content length validation (minimum 50 characters)
  - User-Agent header for respectful scraping

---

### 4. Data Validation System

#### **Pandera Schema Definitions**
- **File:** `src/data_processing/validation/schemas.py`
- **Purpose:** Strict, production-grade data validation

**Price Data Schema:**
- Symbol: Must be 2-10 characters, only BTC or ETH allowed
- Price: Must be > 0 and < $1,000,000 (sanity check)
- Market Cap: Must be ≥ 0 if present
- Volume: Must be ≥ 0 if present
- Percentage Changes: Must be between -100% and +100% (-1.0 to 1.0)
- Data Source: Must be 'coingecko' or 'cryptocompare'
- Timestamps: Must be valid datetime objects

**News Data Schema:**
- Title: 10-500 characters
- URL: Must start with 'http', 10-1000 characters
- Content: Minimum 50 characters
- Data Source: Must be 'coindesk', 'cointelegraph', or 'decrypt'
- Word Count: Must be ≥ 0
- Timestamps: Valid datetime objects

#### **DataValidator with Fallback**
- **File:** `src/data_collection/validators/data_validator.py`
- **Strategy:** Pandera validation with basic validation fallback
- **Benefits:**
  - Production-grade validation when Pandera available
  - Graceful degradation to basic checks if Pandera fails to import
  - Comprehensive error logging for debugging

---

### 5. Collection Scripts

#### **Unified Collection Script**
- **File:** `scripts/data_collection/collect_all_data.py`
- **Purpose:** Run all collectors in sequence
- **Features:**
  - Sequential execution: Price → News
  - Individual success/failure tracking
  - Comprehensive summary reporting
  - Non-zero exit code if any collector fails

#### **NeonDB Collection Script**
- **File:** `scripts/data_collection/collect_to_neondb.py`
- **Purpose:** Direct collection to NeonDB production
- **Usage:** Primarily used by GitHub Actions for scheduled collection

#### **Individual Collector Tests**
- **Files:**
  - `scripts/data_collection/test_price_collector.py`
  - `scripts/data_collection/test_news_collector.py`
- **Purpose:** Test individual collectors in isolation
- **Tests:**
  1. Connection test to external API
  2. Full collection workflow (collect → validate → store)

#### **Pandera Validation Test**
- **File:** `scripts/data_collection/test_pandera_validation.py`
- **Purpose:** Verify Pandera schema validation is working
- **Tests:** Both price and news data validation with real collected data

---

### 6. Automated Scheduled Collection

#### **GitHub Actions Workflow**
- **File:** `.github/workflows/data-collection.yml`
- **Schedule:** Every 15 minutes (`cron: '*/15 * * * *'`)
- **Manual Trigger:** Available via workflow_dispatch
- **Steps:**
  1. Checkout code
  2. Set up Python 3.11
  3. Install Poetry
  4. Install dependencies
  5. Run NeonDB collection script
  6. Report failure status if collection fails

#### **Environment Variables:**
- `NEONDB_PRODUCTION_URL` - From GitHub Secrets
- `NEONDB_BACKUP_URL` - From GitHub Secrets
- `COINGECKO_API_URL` - Hardcoded in workflow
- `MAX_ARTICLES_PER_SOURCE` - Set to 500 in workflow

---

## Challenges & Solutions

### Challenge 1: Schema Inconsistency Between Databases

**Problem:** Initial table creation resulted in different schemas between local PostgreSQL and NeonDB branches. The `sentiment_data` table had `news_article_id` in some databases and `news_data_id` in others.

**Root Cause:** Using existing code files without ensuring they matched the project's schema requirements. Previous iterations had different column names.

**Solution:**
1. Dropped all tables in NeonDB (both production and backup branches)
2. Dropped and recreated local PostgreSQL tables
3. Used single source of truth (`src/shared/models.py`) to create all tables
4. Verified schema consistency across all three databases with `\d+` commands

**Prevention:** Always create fresh tables from the canonical models file, never reuse old schemas.

---

### Challenge 2: PostgreSQL Authentication Failures

**Problem:** Docker container showed "password authentication failed for user bitcoin_user" repeatedly.

**Root Cause:** Old PostgreSQL data volume contained database initialized with different credentials.

**Solution:**
```bash
docker-compose down
docker volume ls  # Find actual volume name
docker volume rm [volume_name]
docker-compose up -d