# Directory Structure

## Bitcoin Sentiment Analysis MLOps Showcase - Conformant Structure

```
Bitcoin Sentiment Analysis
├── .env.dev
├── .env.example
├── .gitignore
├── CREATE_DIRECTORY_STRUCTURE.bat
├── CREATE_INIT_FILES.bat
├── Diagram.png
├── docker-compose.yml
├── LINKS.txt
├── poetry.lock
├── pyproject.toml
├── README.md
├── render.yaml
├── VERIFY_STRUCTURE.bat
├── Version History.md
├── .github
│   └── workflows
│       └── data-collection.yml
├── assets
│   ├── Bitcoin_Architecture_diagram.drawio
│   ├── fastapi_docs.png
│   ├── frontend_drift_detection.png
│   ├── frontend_overview.png
│   ├── frontend_predictions.png
│   ├── frontend_retraining.png
│   └── frontend_system_health.png
├── config
│   ├── redis.conf
│   └── settings
├── data
│   ├── collected
│   └── ml_datasets
│       ├── finbert_features_sample.csv
│       └── vader_features_sample.csv
├── docs
│   ├── Data Sources Documentation.md
│   ├── Deployment & Infrastructure.md
│   ├── Development Environment Setup.md
│   ├── Directory Structure.md
│   ├── Implementation Plan & Roadmap.md
│   ├── Phase 1 Implementation - Data Collection.md
│   ├── Phase 2 Implementation - Sentiment Analysis & Feature Engineering.md
│   ├── Phase 3 Implementation - Model Training & Evaluation.md
│   ├── Phase 4 Implementation - Production Model Serving.md
│   ├── Phase 5 Implementation - MLOps Engineering.md
│   ├── Phase 6 Implementation - Frontend.md
│   ├── System Design Decisions.md
│   └── Technology Stack.md
├── frontend
│   ├── .gitignore
│   ├── eslint.config.mjs
│   ├── next.config.js
│   ├── next.config.ts
│   ├── next-env.d.ts
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.mjs
│   ├── README.md
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── .next
│   │   ├── app-build-manifest.json
│   │   ├── build-manifest.json
│   │   ├── fallback-build-manifest.json
│   │   ├── package.json
│   │   ├── postcss.js
│   │   ├── postcss.js.map
│   │   ├── prerender-manifest.json
│   │   ├── routes-manifest.json
│   │   ├── tmp_file_io_benchmark_5aef01b7c252eb0d1e20cd4fd3697850
│   │   ├── trace
│   │   ├── build
│   │   ├── cache
│   │   ├── server
│   │   ├── static
│   │   └── types
│   ├── app
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── drift
│   │   ├── health
│   │   ├── predictions
│   │   └── retraining
│   ├── components
│   │   ├── dashboard
│   │   ├── drift
│   │   ├── health
│   │   ├── layout
│   │   ├── predictions
│   │   └── retraining
│   ├── lib
│   │   ├── api.ts
│   │   ├── cache.ts
│   │   └── types.ts
│   └── public
│       ├── file.svg
│       ├── globe.svg
│       ├── next.svg
│       ├── vercel.svg
│       └── window.svg
├── logs
├── models
│   ├── experiments
│   └── saved_models
│       ├── finbert
│       └── vader
├── monitoring
│   └── grafana_dashboards
├── scripts
│   ├── data_collection
│   │   ├── __init__.py
│   │   ├── collect_all_data.py
│   │   ├── collect_and_process_all.py
│   │   ├── collect_and_process_neondb.py
│   │   ├── collect_to_neondb.py
│   │   ├── test_news_collector.py
│   │   ├── test_pandera_validation.py
│   │   ├── test_price_collector.py
│   │   └── verify_collections.py
│   ├── data_processing
│   │   ├── compare_sentiment_methods.py
│   │   ├── reprocess_sentiment_neondb.py
│   │   ├── test_feature_engineering.py
│   │   ├── test_sentiment_processor.py
│   │   └── test_vader_analyzer.py
│   ├── deployment
│   │   ├── generate_predictions.py
│   │   ├── run_api.py
│   │   ├── test_api.py
│   │   ├── test_api_performance.py
│   │   ├── test_api_with_logging.py
│   │   ├── test_automated_retraining.py
│   │   ├── test_drift_detection.py
│   │   ├── test_prediction_logging.py
│   │   └── update_prediction_outcomes.py
│   ├── development
│   │   ├── create_neondb_tables.py
│   │   ├── create_tables.py
│   │   ├── init_db.sql
│   │   ├── run_all_tests.py
│   │   ├── test_connections.py
│   │   ├── test_redis.py
│   │   ├── verify_setup.py
│   │   └── wait_for_services.py
│   └── model_training
│       ├── test_neondb_training.py
│       └── train_and_compare_models.py
├── src
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   └── main.py
│   ├── caching
│   │   └── __init__.py
│   ├── data_collection
│   │   ├── __init__.py
│   │   ├── collectors
│   │   ├── processors
│   │   └── validators
│   ├── data_processing
│   │   ├── __init__.py
│   │   ├── feature_engineering
│   │   ├── text_processing
│   │   └── validation
│   ├── mlops
│   │   ├── __init__.py
│   │   ├── automated_retraining.py
│   │   ├── drift_detector.py
│   │   └── prediction_logger.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── ensemble
│   │   ├── evaluation
│   │   ├── persistence
│   │   ├── sentiment
│   │   └── training_pipeline
│   ├── monitoring
│   │   └── __init__.py
│   ├── serving
│   │   ├── __init__.py
│   │   ├── feature_server.py
│   │   ├── model_manager.py
│   │   └── prediction_pipeline.py
│   └── shared
│       ├── __init__.py
│       ├── database.py
│       ├── logging.py
│       └── models.py
└── tests
    ├── __init__.py
    ├── integration
    │   └── __init__.py
    ├── performance
    │   └── __init__.py
    └── unit
        └── __init__.py
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