# Development Environment Setup

## Core Philosophy
- **MLOps-first development approach** - local development optimized for ML pipeline iteration
- **Free-tier deployment preparation** - development environment mirrors Vercel + Render + GitHub Actions
- **Fast ML experimentation cycles** - optimized for rapid model development and testing
- **Production-like ML environment** - real services and data for comprehensive MLOps validation
- **Career-focused portfolio development** - emphasizing MLOps Engineering and AI/ML Engineering skills

---

## Local Development Requirements

### **Pre-installed Components (Confirmed)**
- **Python 3.11.6** with IDLE and VS Code debugger
- **Git CLI** for version control and MLOps workflows
- **Node.js v18.8.0** for MLOps dashboard development
- **npm v10.8.0** for frontend package management
- **NeonDB** (external, production database for feature store)

### **Additional Requirements for MLOps Development**
- **Docker Desktop** - containerized local ML services
- **Poetry** - Python dependency management for ML libraries
- **VS Code Extensions** - Python, TypeScript, Docker, MLOps-specific tools
- **Platform CLI Tools** - Vercel CLI, GitHub CLI (for MLOps automation testing)

---

## Development Architecture

### **MLOps-Focused Local Development Strategy**
- **Local Execution:** Python ML backend + Node.js MLOps dashboard (hot reload enabled)
- **Containerized ML Services:** PostgreSQL (feature store), Redis (model cache), Prometheus (metrics), Grafana (monitoring)
- **GitHub Actions Simulation:** Local testing of ML workflows before production
- **Service Communication:** Local services communicate via localhost networking (production patterns)

### **Service Distribution**
```
MLOps Development Environment:
├── MLOps Dashboard (localhost:3000) - React dev server
├── ML API Backend (localhost:8000) - Python FastAPI
└── Docker ML Services:
    ├── PostgreSQL Feature Store (localhost:5432)
    ├── Redis Model Cache (localhost:6379)
    ├── Prometheus ML Metrics (localhost:9090)
    └── Grafana ML Monitoring (localhost:3001)
```

---

## Package Management Strategy

### **Python ML Dependencies: Poetry**
- **Configuration:** Complete ML dependency management with lock files
- **ML Libraries:** scikit-learn, pandas, transformers, fastapi, prometheus-client
- **Virtual Environment:** Automatic ML environment creation and management
- **Development Dependencies:** Separate ML development and production dependencies
- **Platform Compatibility:** Ensures consistent ML dependencies across local and production

### **Node.js Dashboard Dependencies: npm**
- **Configuration:** Standard Node.js package management for MLOps dashboard
- **Dashboard Libraries:** React, recharts, @tanstack/react-query for real-time ML metrics
- **Lock Files:** package-lock.json for reproducible dashboard builds
- **Platform Integration:** Compatible with Vercel deployment requirements
- **Development Server:** Vite for fast development and hot reload

### **ML Dependency Conflict Resolution Strategy**
- **Poetry Conflicts:** Regenerate lock file and reinstall ML dependencies
- **npm Conflicts:** Remove lock file and node_modules, fresh install
- **Version Control:** Clear ML dependency conflict resolution procedures
- **ML Library Compatibility:** Standardized ML library version management

---

## Docker ML Services Configuration

### **Local MLOps Services**
- **Purpose:** Emulate production ML services locally while maintaining ML development speed
- **Health Checks:** Automated ML service health validation
- **Data Persistence:** Volume mounts for ML model and data persistence across restarts
- **Service Dependencies:** Proper startup order and ML service dependency management

### **ML Service Startup Strategy**
- **Staged Startup:** Feature store first, then model cache, then monitoring services
- **Health Validation:** Wait for ML service readiness before proceeding
- **Failure Handling:** Automatic retry and ML service recovery procedures
- **Resource Management:** Optimized resource allocation for ML development

### **Port Allocation Strategy**
```
MLOps Development Port Allocation:
├── 3000: MLOps Dashboard (npm dev server)
├── 8000: ML API Backend (local Python FastAPI)
├── 5432: PostgreSQL Feature Store
├── 6379: Redis Model Cache
├── 9090: Prometheus ML Metrics
└── 3001: Grafana ML Monitoring
```

---

## Environment Configuration Management

### **MLOps Development Environment Variables**
- **Local Configuration:** Development-specific feature store URLs, ML API endpoints, debug settings
- **External APIs:** Development API keys for CoinGecko, Reddit, news sources
- **ML Service URLs:** Local ML service endpoints for development testing
- **Debug Settings:** Enhanced logging, debug mode, ML pipeline development optimizations

### **Free-Tier Platform Preparation**
- **Platform Credentials:** Vercel and Render account setup for free-tier deployment
- **External Service Credentials:** Production credentials for NeonDB, Redis cloud services
- **Environment Templates:** Platform-specific ML environment variable templates
- **Migration Scripts:** Convert development ML configs to production configs

### **ML Configuration Validation**
- **Startup Validation:** Verify all required ML environment variables are present
- **Service Connectivity:** Validate connections to all external ML services
- **API Key Validation:** Test external API connectivity and rate limits
- **Platform Readiness:** Verify MLOps deployment prerequisites

---

## Real Data Collection Strategy

### **Historical ML Data Download**
- **Automated Collection:** Scripts to download 6 months of historical Bitcoin and sentiment data
- **Data Sources:** CoinGecko price data, news articles with sentiment, Reddit posts
- **Data Validation:** Automated validation of downloaded ML training data quality
- **Storage Strategy:** Local storage for development, NeonDB for production feature store

### **MLOps Development Data Management**
- **Sample ML Datasets:** Curated datasets for different ML development scenarios
- **Data Refresh:** Periodic refresh of development data from production sources
- **Synthetic Data:** Generated test data for specific ML testing scenarios
- **Feature Store Testing:** Real feature engineering pipeline testing with sample data

### **ML Data Pipeline Testing**
- **End-to-End Testing:** Complete ML pipeline from data collection to model prediction
- **Service Integration:** Test ML data flow between all services
- **Performance Testing:** Validate ML data processing performance
- **Error Handling:** Test ML pipeline error scenarios and recovery

---

## Testing Strategy

### **Testing Against Real ML Services**
- **Integration Testing:** Test against real PostgreSQL feature store, Redis model cache, external APIs
- **Service Dependencies:** Validate ML service-to-service communication
- **External API Testing:** Test real API integrations with rate limiting
- **Performance Testing:** Test ML pipelines under realistic load conditions

### **ML Test Environment Management**
- **Test Feature Store:** Separate test database with automated ML setup/teardown
- **Test Data:** Isolated ML test data that doesn't affect development data
- **Service Mocking:** Strategic mocking for unreliable external ML services
- **Test Isolation:** Ensure ML tests don't interfere with each other

### **Cross-Platform MLOps Testing**
- **Local-to-Platform:** Test MLOps deployment pipeline before production
- **Service Communication:** Validate cross-platform ML service communication
- **Configuration Testing:** Test platform-specific ML configurations
- **Performance Validation:** Compare local vs platform ML performance

---

## VS Code Configuration

### **MLOps Development Workspace Setup**
- **Python ML Integration:** Proper Python interpreter, linting, formatting for ML code
- **TypeScript Dashboard:** TypeScript support, React development, Tailwind CSS for MLOps dashboard
- **Docker Integration:** ML container management, service monitoring, log viewing
- **Platform Integration:** GitHub Actions workflow testing and monitoring

### **ML Debugging Configuration**
- **Backend Debugging:** Python FastAPI ML API debugging with breakpoints
- **Frontend Debugging:** React MLOps dashboard component debugging and browser integration
- **Service Debugging:** ML container log monitoring and debugging
- **Cross-Service Debugging:** Multi-service ML debugging scenarios

### **Code Quality Tools**
- **Python ML Tools:** Black formatting, isort imports, flake8 linting, mypy type checking for ML code
- **TypeScript Tools:** ESLint, Prettier, TypeScript compiler integration for dashboard
- **Git Integration:** Pre-commit hooks for ML code, GitLens for enhanced Git functionality
- **Testing Integration:** Test runner integration for both Python ML and TypeScript dashboard code

---

## Platform Deployment Preparation

### **Vercel MLOps Dashboard Preparation**
- **Build Configuration:** Optimized build settings for MLOps dashboard production deployment
- **Environment Variables:** MLOps dashboard environment variable setup and validation
- **Performance Optimization:** Build optimization, caching, CDN configuration for dashboard
- **ML API Integration:** Configuration for connecting to Render-hosted ML API

### **Render ML Backend Preparation**
- **Service Configuration:** ML API service deployment configuration
- **Container Optimization:** Docker container optimization for Render ML deployment
- **Resource Allocation:** ML service resource requirements and scaling configuration
- **Health Checks:** ML service health check configuration and monitoring

### **External ML Service Integration**
- **NeonDB Feature Store:** Database schema deployment and migration procedures for ML features
- **Redis Cloud:** Model cache configuration and connection optimization
- **Service Authentication:** Cross-service authentication and security setup for ML services

---

## Development Workflow Scripts

### **MLOps Environment Setup Automation**
- **Initial Setup:** Complete MLOps development environment setup from scratch
- **ML Service Management:** Start, stop, restart individual or all ML services
- **Data Management:** Download, validate, refresh ML development data
- **Platform Preparation:** Setup platform accounts and MLOps deployment prerequisites

### **ML Development Utilities**
- **Code Quality:** Automated formatting, linting, and type checking for ML code
- **Testing Utilities:** Run specific ML test suites, generate test reports
- **Service Monitoring:** Monitor ML service health and performance
- **Deployment Testing:** Test MLOps deployment pipeline in staging environment

### **MLOps Troubleshooting Tools**
- **Service Diagnostics:** Diagnose ML service connectivity and health issues
- **Log Aggregation:** Collect and analyze logs from all ML services
- **Performance Monitoring:** Monitor ML resource usage and performance bottlenecks
- **Configuration Validation:** Validate ML configuration across all environments

---

## Development-to-Production MLOps Pipeline

### **Local MLOps Development Workflow**
- **ML Code Development:** Local development with hot reload and debugging for ML components
- **Service Testing:** Test against local Docker ML services
- **Integration Testing:** Test complete MLOps workflows end-to-end
- **Quality Validation:** Automated ML code quality and test validation

### **Platform Testing Workflow**
- **Staging Deployment:** Deploy to staging environment on production platforms
- **Integration Validation:** Test cross-platform ML service communication
- **Performance Testing:** Validate ML performance on production platforms
- **User Acceptance Testing:** End-to-end MLOps workflow validation

### **Production MLOps Deployment Workflow**
- **Automated Deployment:** GitHub Actions triggered MLOps deployment
- **Health Validation:** Automated ML health checks and smoke tests
- **Performance Monitoring:** Real-time ML performance and error monitoring
- **Rollback Procedures:** Automated rollback on MLOps deployment failures

---

## Service Communication Testing

### **Local ML Service Integration**
- **API Communication:** Test FastAPI ML backend with dashboard integration
- **Feature Store Integration:** Test PostgreSQL connectivity and ML query performance
- **Cache Integration:** Test Redis model caching and session management
- **External API Integration:** Test real external API connectivity for ML data

### **Cross-Platform MLOps Communication**
- **Dashboard-Backend:** Test Vercel MLOps dashboard with Render ML backend communication
- **Service-to-Service:** Test Render ML service intercommunication
- **External Service Integration:** Test connections to NeonDB feature store, Redis cloud
- **Authentication Testing:** Test cross-platform ML authentication and authorization

### **Performance and Reliability Testing**
- **Load Testing:** Test ML system performance under realistic load
- **Failover Testing:** Test ML service failover and recovery scenarios
- **Network Testing:** Test network latency and reliability between ML platforms
- **Security Testing:** Test authentication, authorization, and ML data security

---

## Expected Development Workflow

### **Daily MLOps Development Cycle**
1. **Environment Startup:** Automated startup of all required ML services
2. **ML Code Development:** Local ML changes with immediate hot reload
3. **Service Testing:** Continuous testing against real ML services
4. **Integration Validation:** Regular end-to-end MLOps testing
5. **Platform Testing:** Periodic deployment to staging for ML validation
6. **Quality Assurance:** Automated ML code quality and test execution

### **ML Service Management**
- **Selective Service Startup:** Start only required ML services for specific development tasks
- **Service Health Monitoring:** Continuous monitoring of ML service health and performance
- **Data Management:** Regular ML data refresh and validation procedures
- **Performance Optimization:** Continuous ML performance monitoring and optimization

### **Platform Integration**
- **Configuration Synchronization:** Keep local and platform ML configurations synchronized
- **Deployment Testing:** Regular testing of MLOps deployment pipeline
- **Service Validation:** Validate ML service functionality across platforms
- **Performance Comparison:** Compare local vs platform ML performance

---

## Success Metrics

### **Development Efficiency**
- **Setup Time:** Complete MLOps environment setup in under 30 minutes
- **Iteration Speed:** ML code changes reflected in under 10 seconds
- **Test Execution:** Complete ML test suite execution in under 5 minutes
- **Service Startup:** All ML services ready in under 2 minutes

### **Service Reliability**
- **Service Uptime:** 99%+ uptime for all local ML development services
- **Data Consistency:** 100% ML data consistency across service restarts
- **External API Success:** 95%+ success rate for external ML API calls
- **Platform Deployment:** 100% successful MLOps staging deployments

### **Development Quality**
- **Code Quality:** 100% compliance with formatting and linting standards for ML code
- **Test Coverage:** 90%+ test coverage for all critical ML components
- **Documentation:** Complete documentation for all MLOps development procedures
- **Platform Readiness:** 100% successful production MLOps deployments

---

**This MLOps-focused development environment setup provides a comprehensive foundation for efficient ML development while preparing for free-tier multi-platform deployment. The development approach maximizes ML experimentation speed while ensuring production readiness through real ML service integration and comprehensive MLOps testing.**