# Deployment & Infrastructure Planning

## Core Philosophy
- **MLOps-first architecture** demonstrating production-grade ML operations capabilities
- **GitHub Actions-centric** orchestration showcasing automated ML pipeline management  
- **Cost-effective deployment** maximizing free-tier services for sustainable operation
- **Production-ready patterns** suitable for L3+ engineering roles (10+ years experience)
- **Career-focused portfolio** emphasizing MLOps Engineering and AI/ML Engineering skills

---

## Selected Deployment Architecture: Free-Tier MLOps Platform

### **Platform Distribution Strategy**

#### **MLOps Orchestration: GitHub Actions**
- **Purpose:** Central ML pipeline orchestration and automation
- **Services Managed:**
  - Data collection workflows with quality validation
  - Automated model training and hyperparameter optimization
  - Model deployment with A/B testing and rollback capabilities
  - Performance monitoring and drift detection
  - Automated retraining triggers based on performance degradation
- **Benefits:** Free compute, integrated version control, comprehensive ML workflow logging
- **Features:** Cron scheduling, webhook triggers, secure secrets management, parallel job execution
- **MLOps Value:** 2000 minutes/month sufficient for complete automated ML operations
- **Cost:** $0/month (unlimited for public repositories)

#### **AI/ML Engineering: Render Backend**
- **Purpose:** Production-grade FastAPI model serving with high-performance inference
- **Services Hosted:**
  - Bitcoin Sentiment Prediction API (VADER vs FinBERT model comparison)
  - Real-time model serving with sub-200ms latency requirements
  - Model performance monitoring endpoints
  - A/B testing framework for model comparison
  - Health monitoring and automated recovery
- **Benefits:** Docker support, automatic SSL, service health checks, auto-scaling
- **Features:** Built-in CI/CD from GitHub, environment variable management, persistent storage
- **Scaling:** Automatic scaling based on request volume and resource usage
- **Cost:** Free tier with 750 hours/month compute (sufficient for 24/7 operation)

#### **Frontend Dashboard: Vercel**
- **Purpose:** MLOps monitoring dashboard and model comparison interface
- **Components:**
  - Real-time model performance monitoring
  - Interactive Bitcoin sentiment analysis dashboard  
  - Model comparison visualization (VADER vs FinBERT)
  - System health and operational metrics
- **Benefits:** Global CDN, automatic HTTPS, Git integration, edge caching
- **Features:** Auto-deployment from GitHub, environment variable management, serverless functions
- **Scaling:** Automatic global distribution, unlimited bandwidth on free tier
- **Cost:** Free tier sufficient for portfolio project requirements

#### **Data Storage & Model Registry: Managed Services**
- **Database:** NeonDB PostgreSQL (512MB free tier) - all application data
- **Model Registry:** GitHub Releases with semantic versioning (v1.0.0, v1.1.0, etc.)
- **Cache Layer:** Redis for feature serving and prediction caching
- **Configuration:** Environment variables with GitHub Secrets for sensitive data
- **Purpose:** Leverage managed services to focus on MLOps capabilities rather than infrastructure management

### **Architecture Benefits**
- ✅ **Zero monthly costs:** All components run on generous free tiers
- ✅ **Production MLOps patterns:** Real automated ML pipeline with monitoring and deployment
- ✅ **Career demonstration value:** Shows L3+ MLOps Engineering and AI/ML Engineering skills
- ✅ **Sustainability:** Can run indefinitely without budget concerns
- ✅ **Scalability:** Architecture patterns ready for enterprise scaling

---

## GitHub Actions MLOps Workflow Architecture

### **Core ML Pipeline Categories**

#### **1. Data Collection Workflows**
```yaml
# Data collection with quality validation (runs every 15 minutes)
name: Data Collection Pipeline
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:

jobs:
  collect-validate-data:
    runs-on: ubuntu-latest
    steps:
      - name: Collect Bitcoin news with sentiment scoring
        run: python src/data_collection/collect_news_data.py
      - name: Collect price data with technical indicators
        run: python src/data_collection/collect_price_data.py
      - name: Validate data quality with Pandera schemas
        run: python src/data_processing/validate_data_quality.py
      - name: Store validated data in NeonDB
        run: python src/data_processing/store_processed_data.py
```

#### **2. Automated ML Training Workflows**
```yaml
# Model training with performance comparison (runs weekly)
name: Automated ML Training Pipeline
on:
  schedule:
    - cron: '0 2 * * 1'  # Monday 2 AM
  workflow_dispatch:

jobs:
  train-compare-models:
    runs-on: ubuntu-latest
    timeout-minutes: 300  # 5 hours max
    steps:
      - name: Prepare training data with feature engineering
        run: python src/data_processing/prepare_training_data.py
      - name: Train VADER sentiment model
        run: python src/models/train_vader_model.py
      - name: Train FinBERT sentiment model (CPU optimized)
        run: python src/models/train_finbert_model.py
      - name: Compare model performance and select best
        run: python src/models/compare_model_performance.py
      - name: Deploy winning model to production
        run: python src/mlops/deploy_best_model.py
      - name: Update model registry with metadata
        run: python src/mlops/update_model_registry.py
```

#### **3. MLOps Monitoring & Deployment Workflows**
```yaml
# Production monitoring and automated retraining
name: MLOps Monitoring Pipeline
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:

jobs:
  monitor-drift-retrain:
    runs-on: ubuntu-latest
    steps:
      - name: Monitor model performance drift
        run: python src/mlops/monitor_model_drift.py
      - name: Check prediction accuracy degradation
        run: python src/mlops/check_prediction_accuracy.py
      - name: Trigger retraining if thresholds exceeded
        run: python src/mlops/conditional_retrain.py
      - name: Update production deployment if retrained
        run: python src/mlops/automated_deployment.py
      - name: Send monitoring alerts
        run: python src/mlops/send_monitoring_alerts.py
```

### **MLOps Workflow Benefits**
- **Cost-effective:** All ML automation runs on free GitHub compute
- **Production-grade:** Complete automated ML lifecycle management
- **Integrated:** Version control, CI/CD, model registry, and deployment in one platform
- **Reliable:** GitHub's infrastructure handles complex ML workflow scheduling and execution
- **Observable:** All ML workflow logs visible, debuggable, and auditable
- **Scalable:** Handles complex multi-step ML pipelines with parallel execution

---

## Service Communication & ML Data Flow

### **MLOps Service Architecture**

#### **Service Communication Pattern**
```
GitHub Actions (ML Orchestration)
    ↓
NeonDB (Feature Store & Model Metadata)
    ↓
Render API (Model Serving & A/B Testing) ←→ Vercel Frontend (MLOps Dashboard)
    ↓
GitHub Releases (Model Registry & Versioning)
```

#### **ML Data Flow Patterns**
- **Training Pipeline:** GitHub Actions → Data Collection → Feature Engineering → Model Training → Model Registry
- **Serving Pipeline:** Model Registry → Render API → Feature Store → Real-time Predictions
- **Monitoring Pipeline:** Render API → Performance Metrics → GitHub Actions → Drift Detection → Automated Retraining
- **User Interface:** Vercel Frontend → Render API → Model Comparisons → Performance Dashboards

#### **Authentication & Security**
- **GitHub Secrets:** Secure storage for API keys, database URLs, and model registry access
- **Environment Variables:** Platform-specific ML configuration management
- **HTTPS Enforcement:** End-to-end encryption for all ML service communications
- **API Authentication:** Token-based authentication between ML services

#### **Service Discovery & Health**
- **Environment-based URLs:** Different ML service endpoints per environment
- **Health Checks:** Regular model serving availability and performance validation
- **Graceful Degradation:** Fallback to baseline models when advanced models unavailable
- **Circuit Breakers:** Automatic service protection during high error rates

---

## Data Architecture & ML Storage Strategy

### **MLOps-Focused Storage Strategy**

#### **Feature Store: NeonDB PostgreSQL**
- **Purpose:** All ML features, model metadata, and performance metrics
- **Tables:** raw_data, processed_features, model_performance, drift_metrics, prediction_logs
- **Features:** Automated backups, connection pooling, SQL-based feature engineering
- **Access:** Shared across all ML services via connection string
- **Scaling:** 512MB free tier sufficient for feature storage and model metadata

#### **Model Registry: GitHub Releases**
- **Purpose:** Versioned model artifacts with comprehensive metadata
- **Storage:** GitHub Releases with semantic versioning (v1.0.0-vader, v1.1.0-finbert, etc.)
- **Features:** Version history, model performance metadata, automated downloads
- **Access:** Public releases downloadable via GitHub API for deployment
- **MLOps Integration:** Direct integration with training and deployment pipelines
- **Scaling:** Unlimited storage for model artifacts and metadata

#### **Performance Cache: Redis**
- **Purpose:** Real-time feature serving and prediction result caching
- **Implementation:** Redis for sub-50ms feature retrieval and prediction caching
- **Scope:** Cross-service caching for optimal model serving performance
- **Benefits:** Dramatically improved inference latency for production serving
- **TTL Management:** Intelligent cache invalidation based on data freshness requirements

#### **Configuration & Secrets: GitHub Ecosystem**
- **Development:** Local .env files with sample configurations
- **Production:** GitHub Secrets for sensitive ML configuration
- **Feature Flags:** Environment variables for A/B testing and model selection
- **Model Configuration:** Versioned model hyperparameters and serving configurations

### **ML Data Persistence Strategy**
- **Critical ML Data:** NeonDB with automatic backups and point-in-time recovery
- **Model Artifacts:** GitHub with full version history and metadata
- **Performance Data:** Redis with appropriate TTL for real-time serving
- **Configuration:** Environment variables with version-controlled templates

---

## Environment Strategy

### **Environment Definitions**

#### **Development Environment (Local ML Development)**
- **Location:** Local development with Docker Compose
- **Purpose:** ML model development, feature engineering, rapid experimentation
- **Services:** All ML services running locally with sample data
- **Data:** Curated sample datasets for development and testing
- **Configuration:** Development-specific settings, debug mode enabled, extended logging

#### **Production Environment (Live ML System)**
- **Location:** Multi-platform deployment (Vercel + Render)
- **Purpose:** Live ML system serving real predictions and demonstrating MLOps capabilities
- **Services:** Full ML service stack with comprehensive monitoring
- **Data:** Real-time data collection and historical ML datasets
- **Configuration:** Optimized production settings, security hardened, performance tuned

### **Environment Promotion Workflow**
```
Development (Local ML Development) → Production (Multi-platform ML System)
```

**MLOps-Focused Strategy Rationale:**
- **Two environments sufficient:** Dev and prod meet all needs for ML portfolio project
- **Cost optimization:** No staging environment to preserve resources for ML operations
- **Simple promotion:** Feature branch → main branch → automated production ML deployment
- **Risk mitigation:** Comprehensive ML testing in development before production deployment

---

## CI/CD Pipeline Strategy

### **Automated MLOps Deployment Workflow**

#### **GitHub Actions ML Integration**
- **Trigger Events:** Push to main branch, model performance degradation, scheduled retraining, manual dispatch
- **Pipeline Stages:** Data Quality → Model Training → Model Validation → Deployment → Performance Monitoring
- **Platform Coordination:** Parallel deployment to Vercel (dashboard) and Render (serving)
- **Quality Gates:** Model accuracy validation, A/B testing significance, performance benchmarking

#### **MLOps Deployment Orchestration Flow**
```
1. Model performance trigger or code push to main branch
2. GitHub Actions ML pipeline triggered
3. Run data quality checks and feature validation
4. Train and validate models with cross-validation
5. Compare model performance and select best performer
6. Deploy selected model to Render with health checks
7. Update MLOps dashboard on Vercel with new model metadata
8. Run integration tests for model serving endpoints
9. Monitor post-deployment model performance
10. Send deployment notifications with performance metrics
```

#### **ML Quality Gates & Validation**
- **Pre-deployment:** Model accuracy tests, feature validation, integration tests
- **Model Validation:** Cross-validation scores, A/B testing significance, performance benchmarks
- **Post-deployment:** Health checks, API response validation, model accuracy monitoring
- **Rollback Triggers:** Model accuracy below threshold, high error rates, performance degradation
- **Notification:** GitHub Issues for deployment failures, Slack/email for ML performance alerts

#### **MLOps Branch Strategy**
- **Main Branch:** Production-ready ML models, triggers production deployment
- **Feature Branches:** Individual ML experiment development with pull request validation
- **Model Branches:** Dedicated branches for major model architecture changes
- **Hotfix Strategy:** Direct commits to main for critical ML fixes with immediate deployment

---

## Monitoring & Observability Architecture

### **MLOps-Focused Monitoring Stack**

#### **Model Performance Monitoring**
- **Implementation:** Comprehensive ML metrics collection in FastAPI with automated analysis
- **Storage:** Model performance metrics stored in NeonDB with time-series analysis
- **Metrics Tracked:**
  - Model prediction accuracy and confidence scores
  - VADER vs FinBERT performance comparison
  - Feature importance drift and data distribution changes
  - Prediction latency and throughput metrics
  - A/B testing results and statistical significance

#### **Infrastructure Monitoring**
- **GitHub Actions:** ML workflow success/failure tracking with performance metrics
- **Render:** Model serving performance, resource usage, auto-scaling events
- **Vercel:** Dashboard performance, user interaction analytics
- **NeonDB:** Database performance, feature store query optimization

#### **MLOps Business Metrics Monitoring**
- **Model Effectiveness:** Real-time sentiment prediction accuracy vs market movements
- **User Engagement:** Model selection preferences and confidence in predictions
- **System Performance:** End-to-end prediction pipeline latency and success rates
- **Data Quality:** Collection success rates, feature completeness, validation failures

#### **Automated Alerting Strategy**
- **Critical Alerts:** Model accuracy below threshold, system downtime, deployment failures
- **Performance Alerts:** Model drift detection, high prediction latency, resource exhaustion
- **ML-Specific Alerts:** Feature distribution drift, data quality issues, model degradation
- **Notification Channels:** GitHub Issues, email notifications, dashboard alerts
- **Response:** Automated GitHub Actions workflows for ML pipeline recovery and retraining

### **MLOps Dashboard & Reporting**
- **Implementation:** Real-time MLOps dashboard in Next.js frontend
- **Content:** Model performance comparison, drift detection visualizations, system health metrics
- **Updates:** Real-time API calls to backend for current ML performance metrics
- **Historical Analysis:** Time-series charts showing model performance trends and improvements

---

## Security & Configuration Management

### **Security Strategy**

#### **ML System Security**
- **API Security:** Rate limiting, input validation, model serving endpoint protection
- **Data Security:** Parameterized queries, feature data sanitization, PII protection
- **Model Security:** Model artifact integrity validation, secure model loading
- **Transport Security:** HTTPS enforced on all platforms, encrypted model transfers

#### **Infrastructure Security**
- **Access Control:** GitHub repository access control with branch protection
- **Secret Management:** GitHub Secrets for all ML-sensitive data (API keys, model configs)
- **Network Security:** Platform-native security (Vercel, Render) with secure communication
- **Database Security:** NeonDB connection encryption, access controls, query monitoring

#### **ML Configuration Management**
- **Environment-based:** Different ML configurations per environment
- **Version Controlled:** All ML configuration templates in Git with model metadata
- **Secret Separation:** Sensitive ML data in platform secret management
- **Validation:** ML configuration validation in deployment pipeline

### **Backup & Recovery Strategy**

#### **ML Data Backup**
- **Database:** NeonDB automatic backups with point-in-time recovery
- **Model Registry:** Git version control with GitHub backup and model artifact storage
- **Feature Store:** Multiple model versions stored in GitHub Releases
- **Configuration:** Infrastructure-as-code in version control with ML pipeline definitions

#### **ML Recovery Procedures**
- **Service Recovery:** Platform-native auto-restart with model serving health checks
- **Model Recovery:** Deploy previous model version from GitHub Releases with automated rollback
- **Data Recovery:** Database restore from NeonDB backups with feature reconstruction
- **Configuration Recovery:** Redeploy ML pipeline from version control with configuration validation

---

## Cost Management & Resource Optimization

### **Free Tier Resource Allocation**

#### **GitHub Actions (2000 minutes/month)**
- **Data Collection:** ~200 minutes/month (15min jobs, 4x/hour)
- **Model Training:** ~400 minutes/month (weekly 6-hour ML training jobs)
- **MLOps Monitoring:** ~300 minutes/month (drift detection, retraining triggers)
- **Deployment & Testing:** ~200 minutes/month (multiple ML deployments and validation)
- **Buffer:** ~900 minutes/month remaining for development and experimentation

#### **Render (750 hours/month)**
- **FastAPI ML Backend:** 24/7 operation = 720 hours/month
- **Model Serving:** Continuous operation for real-time predictions
- **Buffer:** 30 hours/month for overages or additional ML services

#### **Vercel (Unlimited)**
- **MLOps Dashboard:** No limits on free tier for portfolio projects
- **Bandwidth:** 100GB/month limit (more than sufficient for dashboard traffic)

#### **NeonDB (512MB Storage)**
- **Estimated Usage:** ~150-250MB for feature store and model metadata
- **Buffer:** 250MB+ remaining for historical ML data and growth

### **Resource Optimization Strategies**
- **Efficient ML Data Storage:** Automated cleanup of old features, compressed historical ML data
- **Smart ML Scheduling:** Optimize GitHub Actions timing for ML training during off-peak hours
- **Intelligent Caching:** Reduce inference latency through Redis-based feature caching
- **Performance Monitoring:** Track ML resource usage to optimize within limits

### **MLOps Scaling Strategy**
- **Immediate:** All ML components designed to maximize free tier usage
- **Short-term:** Optimize ML workflows to handle more data and models within limits
- **Long-term:** Clear upgrade paths if ML project needs to scale beyond free tiers
- **Alternative:** Migration strategy to cloud ML platforms (AWS SageMaker, GCP Vertex AI) if needed

---

## Implementation Timeline & Phases

### **Phase 1: Core MLOps Infrastructure (Week 1)**
- GitHub repository setup with comprehensive ML workflow templates
- NeonDB feature store schema and ML metadata tables
- Basic GitHub Actions workflows for data collection and quality validation
- Development environment with Docker Compose for ML development

### **Phase 2: Model Training & Registry (Week 2)**
- Automated model training workflows for VADER and FinBERT
- Model performance comparison and selection automation
- GitHub Releases model registry with metadata and versioning
- Cross-validation and model evaluation framework

### **Phase 3: AI/ML Engineering & Serving (Week 3)**
- FastAPI backend deployment to Render with model serving endpoints
- Real-time prediction API with sub-200ms latency requirements
- A/B testing framework for model comparison in production
- Redis integration for feature serving and prediction caching

### **Phase 4: MLOps Production Monitoring (Week 4)**
- Comprehensive MLOps monitoring and drift detection
- Automated retraining triggers based on performance degradation
- MLOps dashboard deployment to Vercel with real-time metrics
- Production security hardening and performance validation

---

## Success Metrics & Portfolio Value

### **Technical Success Criteria**
- **System Availability:** >99.5% uptime for all ML services
- **ML Automation Success:** >95% successful automated ML workflows
- **Model Performance:** Consistent model accuracy with automated A/B testing
- **Response Performance:** <200ms API response times for model predictions
- **Cost Management:** Operation within all free tier limits with room for growth

### **MLOps Portfolio Demonstration Value**
- **MLOps Engineering Skills:** Complete automated ML pipeline with monitoring and deployment
- **AI/ML Engineering Capabilities:** High-performance model serving with A/B testing framework
- **Data Science Expertise:** Model comparison, feature engineering, and performance optimization
- **Cost Optimization:** Production ML system with zero monthly operational costs
- **System Integration:** Multi-platform MLOps deployment with comprehensive automation

### **Career-Focused Interview Talking Points**
- **"Built production-grade MLOps pipeline with automated retraining and drift detection"**
- **"Implemented high-performance model serving API with sub-200ms latency requirements"**
- **"Created automated A/B testing framework for model comparison in production"**
- **"Designed cost-effective MLOps architecture serving real traffic with zero operational costs"**
- **"Demonstrated L3+ MLOps Engineering capabilities with automated ML lifecycle management"**

---

**This deployment strategy provides a practical, cost-effective MLOps architecture that demonstrates professional MLOps Engineering and AI/ML Engineering capabilities while remaining sustainable for long-term operation. The GitHub Actions-centric approach showcases modern automated ML pipeline practices while the multi-platform deployment demonstrates system integration skills essential for senior MLOps roles.**