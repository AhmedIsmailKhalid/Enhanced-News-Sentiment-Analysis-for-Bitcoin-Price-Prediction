# Directory Structure

## Bitcoin Sentiment Analysis MLOps Showcase - Conformant Structure

```
bitcoin-sentiment-mlops-showcase/
├── .dockerignore
├── .env.dev
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── poetry.lock
├── pyproject.toml
├── pytest.ini
├── README.md
├── render.yaml
├── vercel.json
│
├── .github/
│   └── workflows/
│       ├── data-collection.yml
│       ├── model-training.yml
│       ├── model-deployment.yml
│       ├── monitoring.yml
│       └── ci-cd.yml
│
├── .pytest_cache/
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   └── v/
│       └── cache/
│           ├── lastfailed
│           ├── nodeids
│           └── stepwise
│
├── config/
│   ├── cache_config.yaml
│   ├── redis.conf
│   └── settings/
│       ├── base.yaml
│       ├── development.yaml
│       └── production.yaml
│
├── data/
│   ├── collected/
│   │   ├── news_[timestamp].csv
│   │   ├── prices_[timestamp].csv
│   │   └── social_[timestamp].csv
│   └── ml_datasets/
│       ├── bitcoin_prediction_dataset_[timestamp].csv
│       └── feature_metadata_[timestamp].json
│
├── docs/
│   ├── Data Sources Documentation.md
│   ├── Deployment & Infrastructure.md
│   ├── Development Environment Setup.md
│   ├── Implementation Plan & Roadmap.md
│   ├── Project Structure & Organization.md
│   ├── Redis Caching Guide.md
│   ├── System Design Decisions.md
│   ├── Technology Stack.md
│   └── Testing Strategy & Quality Assurance.md
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── vercel.json
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── index.html
│   │
│   └── src/
│       ├── components/
│       │   ├── Dashboard/
│       │   │   ├── ModelComparison.tsx
│       │   │   ├── PerformanceMetrics.tsx
│       │   │   └── PredictionInterface.tsx
│       │   ├── Charts/
│       │   │   ├── SentimentChart.tsx
│       │   │   ├── PriceChart.tsx
│       │   │   └── ModelAccuracyChart.tsx
│       │   └── Common/
│       │       ├── Header.tsx
│       │       ├── LoadingSpinner.tsx
│       │       └── ErrorBoundary.tsx
│       │
│       ├── hooks/
│       │   ├── useModelData.ts
│       │   ├── usePredictions.ts
│       │   └── useWebSocket.ts
│       │
│       ├── services/
│       │   ├── api.ts
│       │   ├── websocket.ts
│       │   └── types.ts
│       │
│       ├── styles/
│       │   ├── globals.css
│       │   └── components.css
│       │
│       ├── utils/
│       │   ├── formatters.ts
│       │   ├── validators.ts
│       │   └── constants.ts
│       │
│       ├── App.tsx
│       ├── main.tsx
│       └── index.css
│
├── logs/
│   ├── application.log
│   ├── model_training.log
│   └── data_collection.log
│
├── models/
│   ├── experiments/
│   │   └── experiment_[timestamp]/
│   │       ├── config.json
│   │       ├── metrics.json
│   │       └── artifacts/
│   └── saved_models/
│       ├── model_registry.json
│       ├── VADER/
│       │   └── [timestamp]/
│       │       ├── model.pkl
│       │       └── metadata.json
│       ├── FinBERT/
│       │   └── [timestamp]/
│       │       ├── model.pkl
│       │       └── metadata.json
│       └── Ensemble/
│           └── [timestamp]/
│               ├── model.pkl
│               └── metadata.json
│
├── monitoring/
│   ├── model_performance.db
│   ├── prometheus.yml
│   └── grafana_dashboards/
│       ├── model_performance.json
│       └── system_health.json
│
├── scripts/
│   ├── setup_dev.py
│   ├── setup_redis.sh
│   ├── start_dev.sh
│   │
│   ├── development/
│   │   ├── cache_management.py
│   │   ├── create_tables.py
│   │   ├── run_unified_tests.py
│   │   ├── standalone_redis_test.py
│   │   └── test_setup.py
│   │
│   ├── data_collection/
│   │   ├── collect_news_data.py
│   │   ├── collect_price_data.py
│   │   ├── collect_social_data.py
│   │   └── unified_collection.py
│   │
│   ├── model_training/
│   │   ├── train_vader_model.py
│   │   ├── train_finbert_model.py
│   │   ├── train_ensemble.py
│   │   └── compare_models.py
│   │
│   └── deployment/
│       ├── deploy_models.py
│       ├── health_check.py
│       └── rollback_model.py
│
├── src/
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── prediction_service.py
│   │
│   ├── caching/
│   │   ├── __init__.py
│   │   ├── cache_decorators.py
│   │   ├── cache_manager.py
│   │   ├── cache_strategies.py
│   │   ├── monitoring.py
│   │   └── redis_client.py
│   │
│   ├── data_collection/
│   │   ├── __init__.py
│   │   ├── unified_data_sync.py
│   │   │
│   │   ├── collectors/
│   │   │   ├── __init__.py
│   │   │   ├── base_collector.py
│   │   │   ├── news_collector.py
│   │   │   ├── price_collector.py
│   │   │   ├── social_collector.py
│   │   │   └── unified_collector.py
│   │   │
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   ├── news_processor.py
│   │   │   ├── price_processor.py
│   │   │   └── social_processor.py
│   │   │
│   │   └── validators/
│   │       ├── __init__.py
│   │       ├── quality_checker.py
│   │       └── schema_validator.py
│   │
│   ├── data_processing/
│   │   ├── __init__.py
│   │   │
│   │   ├── feature_engineering/
│   │   │   ├── __init__.py
│   │   │   ├── feature_combiner.py
│   │   │   ├── price_features.py
│   │   │   └── temporal_features.py
│   │   │
│   │   ├── text_processing/
│   │   │   ├── __init__.py
│   │   │   ├── preprocessor.py
│   │   │   └── sentiment_analyzer.py
│   │   │
│   │   └── validation/
│   │       ├── __init__.py
│   │       ├── dataset_exporter.py
│   │       ├── data_validator.py
│   │       ├── feature_selector.py
│   │       └── schemas.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── training_pipeline.py
│   │   │
│   │   ├── sentiment/
│   │   │   ├── __init__.py
│   │   │   ├── vader_model.py
│   │   │   └── finbert_model.py
│   │   │
│   │   ├── ensemble/
│   │   │   ├── __init__.py
│   │   │   └── model_ensemble.py
│   │   │
│   │   ├── evaluation/
│   │   │   ├── __init__.py
│   │   │   ├── financial_metrics.py
│   │   │   └── time_series_validator.py
│   │   │
│   │   └── persistence/
│   │       ├── __init__.py
│   │       └── model_manager.py
│   │
│   ├── serving/
│   │   ├── __init__.py
│   │   ├── model_server.py
│   │   ├── prediction_pipeline.py
│   │   └── feature_store.py
│   │
│   ├── mlops/
│   │   ├── __init__.py
│   │   ├── model_monitor.py
│   │   ├── drift_detector.py
│   │   ├── automated_retraining.py
│   │   ├── deployment_manager.py
│   │   └── performance_tracker.py
│   │
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── api_metrics.py
│   │   ├── model_monitor.py
│   │   └── production_monitor.py
│   │
│   └── shared/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py
│       ├── logging.py
│       ├── models.py
│       └── utils.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── factories.py
    │
    ├── unit/
    │   ├── __init__.py
    │   ├── test_collectors.py
    │   ├── test_processors.py
    │   ├── test_redis_cache.py
    │   ├── test_sentiment.py
    │   ├── test_models.py
    │   └── test_validators.py
    │
    ├── integration/
    │   ├── __init__.py
    │   ├── test_external_apis.py
    │   ├── test_model_pipeline.py
    │   └── test_cross_platform.py
    │
    └── performance/
        ├── __init__.py
        ├── test_load_performance.py
        └── test_latency.py
```

## Key Directory Explanations

### **Root Level Files**
- **render.yaml** - Render deployment configuration for backend services
- **vercel.json** - Vercel deployment configuration for frontend dashboard
- **docker-compose.yml** - Local development environment orchestration
- **pyproject.toml** - Python dependency management with Poetry

### **GitHub Actions Workflows (.github/workflows/)**
- **data-collection.yml** - Automated data collection every 15 minutes
- **model-training.yml** - Weekly model training and comparison
- **model-deployment.yml** - Automated model deployment after training
- **monitoring.yml** - Continuous monitoring and drift detection
- **ci-cd.yml** - Continuous integration and deployment pipeline

### **Source Code Structure (src/)**

#### **Data Collection (src/data_collection/)**
- **Purpose:** External API data collection and initial processing
- **Focus:** CoinGecko prices, news RSS feeds, Reddit API data
- **Components:** Collectors, processors, validators
- **Career Value:** Demonstrates data acquisition and quality validation skills

#### **Data Processing (src/data_processing/)**  
- **Purpose:** Feature engineering and ML data preparation
- **Focus:** Technical indicators, sentiment analysis, feature combination
- **Components:** Feature engineering, text processing, validation
- **Career Value:** Shows data science and feature engineering expertise

#### **Models (src/models/)**
- **Purpose:** Data Science components - model development and training
- **Focus:** VADER vs FinBERT sentiment analysis, ensemble methods
- **Components:** Sentiment models, ensembles, evaluation, persistence
- **Career Value:** Demonstrates data science and ML modeling capabilities

#### **Serving (src/serving/)**
- **Purpose:** AI/ML Engineering components - production model serving
- **Focus:** High-performance inference, feature store, prediction pipeline
- **Components:** Model server, prediction pipeline, feature store
- **Career Value:** Shows AI/ML Engineering and production deployment skills

#### **MLOps (src/mlops/)**
- **Purpose:** MLOps Engineering components - automation and monitoring
- **Focus:** Model monitoring, drift detection, automated retraining
- **Components:** Monitoring, drift detection, deployment automation
- **Career Value:** Demonstrates MLOps Engineering and automation expertise

#### **Caching (src/caching/)**
- **Purpose:** Performance optimization and feature serving
- **Focus:** Redis-based caching for model predictions and features
- **Components:** Cache management, strategies, monitoring
- **Career Value:** Shows performance optimization and system design skills

### **Frontend Structure (frontend/)**
- **Purpose:** MLOps monitoring dashboard and model comparison interface
- **Technology:** React + TypeScript + Tailwind CSS
- **Components:** Dashboard components, charts, real-time features
- **Deployment:** Vercel with optimized build configuration

### **Model Registry (models/)**
- **Purpose:** Local model storage with version management
- **Structure:** Organized by model type and timestamp
- **Integration:** Synced with GitHub Releases for production deployment
- **Metadata:** Complete model metadata and performance tracking

### **Configuration & Scripts**
- **config/:** Environment-specific configuration management
- **scripts/:** Development utilities, data collection, and deployment scripts
- **monitoring/:** Prometheus configuration and performance tracking

### **Testing Strategy (tests/)**
- **unit/:** Individual component testing
- **integration/:** Cross-service and external API testing  
- **performance/:** Load and latency testing for production readiness

## Architecture Benefits

### **MLOps-First Organization**
- **Clear separation** of MLOps Engineering, AI/ML Engineering, Data Science, and Data Collection
- **Production-ready patterns** suitable for enterprise deployment
- **Automated workflows** using GitHub Actions instead of complex orchestration tools
- **Scalable structure** that supports growth while maintaining organization

### **Career-Focused Design**
- **Portfolio demonstration:** Each directory showcases specific technical capabilities
- **Industry patterns:** Structure follows modern ML engineering best practices
- **Interview talking points:** Clear examples of MLOps, AI/ML Engineering, and Data Science work
- **Production readiness:** Architecture suitable for real-world deployment scenarios

### **Free-Tier Optimization**
- **Simplified deployment:** Two-platform architecture (Vercel + Render)
- **Cost-effective:** No complex infrastructure requirements
- **Sustainable:** Can run indefinitely on free tiers
- **Practical:** Demonstrates real-world constraints and optimization

This directory structure supports our finalized Bitcoin Sentiment Analysis MLOps Showcase specifications while maintaining clear separation of concerns and demonstrating production-grade ML engineering capabilities.