# Directory Structure

## Bitcoin Sentiment Analysis MLOps Showcase - Conformant Structure

```
Bitcoin Sentiment Analysis
├── .env.dev
├── .env.example
├── .gitignore
├── CREATE_DIRECTORY_STRUCTURE.bat
├── CREATE_INIT_FILES.bat
├── docker-compose.yml
├── poetry.lock
├── predictions.csv
├── pyproject.toml
├── README.md
├── tree.txt
├── VERIFY_STRUCTURE.bat
├── .github
│   └── workflows
│       └── data-collection.yml
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
│   │   └── types.ts
│   ├── node_modules
│   │   ├── .package-lock.json
│   │   ├── .bin
│   │   ├── @alloc
│   │   ├── @emnapi
│   │   ├── @eslint
│   │   ├── @eslint-community
│   │   ├── @humanfs
│   │   ├── @humanwhocodes
│   │   ├── @img
│   │   ├── @isaacs
│   │   ├── @jridgewell
│   │   ├── @napi-rs
│   │   ├── @next
│   │   ├── @nodelib
│   │   ├── @nolyfill
│   │   ├── @reduxjs
│   │   ├── @rtsao
│   │   ├── @rushstack
│   │   ├── @standard-schema
│   │   ├── @swc
│   │   ├── @tailwindcss
│   │   ├── @tanstack
│   │   ├── @tybys
│   │   ├── @types
│   │   ├── @typescript-eslint
│   │   ├── @unrs
│   │   ├── acorn
│   │   ├── acorn-jsx
│   │   ├── ajv
│   │   ├── ansi-styles
│   │   ├── argparse
│   │   ├── aria-query
│   │   ├── array.prototype.findlast
│   │   ├── array.prototype.findlastindex
│   │   ├── array.prototype.flat
│   │   ├── array.prototype.flatmap
│   │   ├── array.prototype.tosorted
│   │   ├── arraybuffer.prototype.slice
│   │   ├── array-buffer-byte-length
│   │   ├── array-includes
│   │   ├── ast-types-flow
│   │   ├── async-function
│   │   ├── available-typed-arrays
│   │   ├── axe-core
│   │   ├── axobject-query
│   │   ├── balanced-match
│   │   ├── brace-expansion
│   │   ├── braces
│   │   ├── call-bind
│   │   ├── call-bind-apply-helpers
│   │   ├── call-bound
│   │   ├── callsites
│   │   ├── caniuse-lite
│   │   ├── chalk
│   │   ├── chownr
│   │   ├── client-only
│   │   ├── clsx
│   │   ├── color-convert
│   │   ├── color-name
│   │   ├── concat-map
│   │   ├── cross-spawn
│   │   ├── csstype
│   │   ├── d3-array
│   │   ├── d3-color
│   │   ├── d3-ease
│   │   ├── d3-format
│   │   ├── d3-interpolate
│   │   ├── d3-path
│   │   ├── d3-scale
│   │   ├── d3-shape
│   │   ├── d3-time
│   │   ├── d3-time-format
│   │   ├── d3-timer
│   │   ├── damerau-levenshtein
│   │   ├── data-view-buffer
│   │   ├── data-view-byte-length
│   │   ├── data-view-byte-offset
│   │   ├── debug
│   │   ├── decimal.js-light
│   │   ├── deep-is
│   │   ├── define-data-property
│   │   ├── define-properties
│   │   ├── detect-libc
│   │   ├── doctrine
│   │   ├── dunder-proto
│   │   ├── emoji-regex
│   │   ├── enhanced-resolve
│   │   ├── es-abstract
│   │   ├── escape-string-regexp
│   │   ├── es-define-property
│   │   ├── es-errors
│   │   ├── es-iterator-helpers
│   │   ├── eslint
│   │   ├── eslint-config-next
│   │   ├── eslint-import-resolver-node
│   │   ├── eslint-import-resolver-typescript
│   │   ├── eslint-module-utils
│   │   ├── eslint-plugin-import
│   │   ├── eslint-plugin-jsx-a11y
│   │   ├── eslint-plugin-react
│   │   ├── eslint-plugin-react-hooks
│   │   ├── eslint-scope
│   │   ├── eslint-visitor-keys
│   │   ├── es-object-atoms
│   │   ├── espree
│   │   ├── esquery
│   │   ├── esrecurse
│   │   ├── es-set-tostringtag
│   │   ├── es-shim-unscopables
│   │   ├── es-toolkit
│   │   ├── es-to-primitive
│   │   ├── estraverse
│   │   ├── esutils
│   │   ├── eventemitter3
│   │   ├── fast-deep-equal
│   │   ├── fast-glob
│   │   ├── fast-json-stable-stringify
│   │   ├── fast-levenshtein
│   │   ├── fastq
│   │   ├── file-entry-cache
│   │   ├── fill-range
│   │   ├── find-up
│   │   ├── flat-cache
│   │   ├── flatted
│   │   ├── for-each
│   │   ├── function.prototype.name
│   │   ├── function-bind
│   │   ├── functions-have-names
│   │   ├── generator-function
│   │   ├── get-intrinsic
│   │   ├── get-proto
│   │   ├── get-symbol-description
│   │   ├── get-tsconfig
│   │   ├── globals
│   │   ├── globalthis
│   │   ├── glob-parent
│   │   ├── gopd
│   │   ├── graceful-fs
│   │   ├── graphemer
│   │   ├── has-bigints
│   │   ├── has-flag
│   │   ├── hasown
│   │   ├── has-property-descriptors
│   │   ├── has-proto
│   │   ├── has-symbols
│   │   ├── has-tostringtag
│   │   ├── ignore
│   │   ├── immer
│   │   ├── import-fresh
│   │   ├── imurmurhash
│   │   ├── internal-slot
│   │   ├── internmap
│   │   ├── isarray
│   │   ├── is-array-buffer
│   │   ├── is-async-function
│   │   ├── is-bigint
│   │   ├── is-boolean-object
│   │   ├── is-bun-module
│   │   ├── is-callable
│   │   ├── is-core-module
│   │   ├── is-data-view
│   │   ├── is-date-object
│   │   ├── isexe
│   │   ├── is-extglob
│   │   ├── is-finalizationregistry
│   │   ├── is-generator-function
│   │   ├── is-glob
│   │   ├── is-map
│   │   ├── is-negative-zero
│   │   ├── is-number
│   │   ├── is-number-object
│   │   ├── is-regex
│   │   ├── is-set
│   │   ├── is-shared-array-buffer
│   │   ├── is-string
│   │   ├── is-symbol
│   │   ├── is-typed-array
│   │   ├── is-weakmap
│   │   ├── is-weakref
│   │   ├── is-weakset
│   │   ├── iterator.prototype
│   │   ├── jiti
│   │   ├── json5
│   │   ├── json-buffer
│   │   ├── json-schema-traverse
│   │   ├── json-stable-stringify-without-jsonify
│   │   ├── js-tokens
│   │   ├── jsx-ast-utils
│   │   ├── js-yaml
│   │   ├── keyv
│   │   ├── language-subtag-registry
│   │   ├── language-tags
│   │   ├── levn
│   │   ├── lightningcss
│   │   ├── lightningcss-win32-x64-msvc
│   │   ├── locate-path
│   │   ├── lodash.merge
│   │   ├── loose-envify
│   │   ├── lucide-react
│   │   ├── magic-string
│   │   ├── math-intrinsics
│   │   ├── merge2
│   │   ├── micromatch
│   │   ├── minimatch
│   │   ├── minimist
│   │   ├── minipass
│   │   ├── minizlib
│   │   ├── ms
│   │   ├── nanoid
│   │   ├── napi-postinstall
│   │   ├── natural-compare
│   │   ├── next
│   │   ├── object.assign
│   │   ├── object.entries
│   │   ├── object.fromentries
│   │   ├── object.groupby
│   │   ├── object.values
│   │   ├── object-assign
│   │   ├── object-inspect
│   │   ├── object-keys
│   │   ├── optionator
│   │   ├── own-keys
│   │   ├── parent-module
│   │   ├── path-exists
│   │   ├── path-key
│   │   ├── path-parse
│   │   ├── picocolors
│   │   ├── picomatch
│   │   ├── p-limit
│   │   ├── p-locate
│   │   ├── possible-typed-array-names
│   │   ├── postcss
│   │   ├── prelude-ls
│   │   ├── prop-types
│   │   ├── punycode
│   │   ├── queue-microtask
│   │   ├── react
│   │   ├── react-dom
│   │   ├── react-is
│   │   ├── react-redux
│   │   ├── recharts
│   │   ├── redux
│   │   ├── redux-thunk
│   │   ├── reflect.getprototypeof
│   │   ├── regexp.prototype.flags
│   │   ├── reselect
│   │   ├── resolve
│   │   ├── resolve-from
│   │   ├── resolve-pkg-maps
│   │   ├── reusify
│   │   ├── run-parallel
│   │   ├── safe-array-concat
│   │   ├── safe-push-apply
│   │   ├── safe-regex-test
│   │   ├── scheduler
│   │   ├── semver
│   │   ├── set-function-length
│   │   ├── set-function-name
│   │   ├── set-proto
│   │   ├── sharp
│   │   ├── shebang-command
│   │   ├── shebang-regex
│   │   ├── side-channel
│   │   ├── side-channel-list
│   │   ├── side-channel-map
│   │   ├── side-channel-weakmap
│   │   ├── source-map-js
│   │   ├── stable-hash
│   │   ├── stop-iteration-iterator
│   │   ├── string.prototype.includes
│   │   ├── string.prototype.matchall
│   │   ├── string.prototype.repeat
│   │   ├── string.prototype.trim
│   │   ├── string.prototype.trimend
│   │   ├── string.prototype.trimstart
│   │   ├── strip-bom
│   │   ├── strip-json-comments
│   │   ├── styled-jsx
│   │   ├── supports-color
│   │   ├── supports-preserve-symlinks-flag
│   │   ├── tailwindcss
│   │   ├── tapable
│   │   ├── tar
│   │   ├── tinyglobby
│   │   ├── tiny-invariant
│   │   ├── to-regex-range
│   │   ├── ts-api-utils
│   │   ├── tsconfig-paths
│   │   ├── tslib
│   │   ├── type-check
│   │   ├── typed-array-buffer
│   │   ├── typed-array-byte-length
│   │   ├── typed-array-byte-offset
│   │   ├── typed-array-length
│   │   ├── typescript
│   │   ├── unbox-primitive
│   │   ├── undici-types
│   │   ├── unrs-resolver
│   │   ├── uri-js
│   │   ├── use-sync-external-store
│   │   ├── victory-vendor
│   │   ├── which
│   │   ├── which-boxed-primitive
│   │   ├── which-builtin-type
│   │   ├── which-collection
│   │   ├── which-typed-array
│   │   ├── word-wrap
│   │   ├── yallist
│   │   └── yocto-queue
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
│       ├── Ensemble
│       ├── FinBERT
│       └── VADER
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
│   │   ├── test_feature_engineering.py
│   │   ├── test_sentiment_processor.py
│   │   └── test_vader_analyzer.py
│   ├── deployment
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