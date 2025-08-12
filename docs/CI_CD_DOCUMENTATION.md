# 🚀 LAIT CI/CD Pipeline Documentation

## Overview

The LAIT project uses GitHub Actions for continuous integration and deployment. The CI/CD pipeline ensures code quality, runs comprehensive tests, and validates deployments.

## Pipeline Structure

### 🧪 Backend Testing (`backend-test`)

**Services:**
- **PostgreSQL 15**: Test database on port 5432
- **Redis 7**: Cache and session storage on port 6379

**Test Environment:**
```yaml
DATABASE_URL: postgresql://lait:lait_password@localhost:5432/lait_test
REDIS_URL: redis://localhost:6379/0
FLASK_ENV: testing
JWT_SECRET_KEY: test-secret-key-for-ci
AUTO_AUTH_BYPASS: true
```

**Test Steps:**
1. **Setup**: Python 3.11, cache dependencies, install system tools
2. **Dependencies**: Install Python packages and pytest extensions
3. **Service Readiness**: Wait for PostgreSQL and Redis to be healthy
4. **Database Init**: Create tables using SQLAlchemy models
5. **Unit Tests**: Run pytest with coverage reporting
6. **E2E Tests**: Start Flask app and run end-to-end workflow tests
7. **Artifacts**: Upload coverage reports and test results

### 🎨 Frontend Testing (`frontend-test`)

**Environment:**
- **Node.js 18**: JavaScript runtime
- **npm**: Package manager with dependency caching

**Test Steps:**
1. **Dependencies**: Install npm packages
2. **Linting**: ESLint code quality checks
3. **Unit Tests**: Jest test runner
4. **Build**: Production build verification

### 🔒 Security Scanning (`security-scan`)

**Tools:**
- **Trivy**: Vulnerability scanner for dependencies and filesystem
- **SARIF Upload**: Results integrated with GitHub Security tab

### 🐳 Docker Build (`docker-build`)

**Conditions:** Only runs on `main` branch after successful tests

**Build Targets:**
- **Backend Image**: `lait-backend:latest`
- **Frontend Image**: `lait-frontend:latest`
- **Build Cache**: GitHub Actions cache for faster builds

## Test Coverage

### Unit Tests
- **Backend Models**: User, Invoice, Authentication
- **API Endpoints**: Registration, Login, Upload, Analytics
- **Business Logic**: Risk scoring, PDF parsing, data validation
- **Database Operations**: CRUD operations and relationships

### E2E Tests
- **User Workflow**: Registration → Login → Upload → Dashboard
- **File Processing**: PDF and text invoice parsing
- **Analytics**: Dashboard metrics and KPI calculations
- **Data Integrity**: Cross-endpoint consistency validation

### Security Tests
- **Dependency Scanning**: Known vulnerability detection
- **Secret Detection**: Accidental credential exposure prevention
- **Container Security**: Docker image vulnerability scanning

## Environment Variables

### Required for CI
```bash
DATABASE_URL=postgresql://lait:lait_password@localhost:5432/lait_test
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=testing
JWT_SECRET_KEY=test-secret-key-for-ci
SECRET_KEY=test-secret-key-for-ci
AUTO_AUTH_BYPASS=true
TESTING=true
```

### Service Health Checks
```bash
# PostgreSQL readiness
pg_isready -h localhost -p 5432 -U lait

# Redis connectivity  
redis-cli -h localhost -p 6379 ping

# Flask API health
curl -f http://localhost:5003/api/health
```

## Local Testing

### Quick Start
```bash
# Run full CI pipeline locally
./scripts/run-ci-tests.sh
```

### Manual Steps
```bash
# 1. Start services
docker-compose up -d db redis

# 2. Set environment
export DATABASE_URL="postgresql://lait:lait_password@localhost:5432/lait_test"
export REDIS_URL="redis://localhost:6379/0"
export FLASK_ENV=testing

# 3. Install dependencies
cd backend
pip install -r requirements.txt
pip install -r ../tests/requirements.txt

# 4. Initialize database
python -c "from app_real import app, db; app.app_context().push(); db.create_all()"

# 5. Run tests
python -m pytest tests/ -v --cov=.
python -m pytest ../tests/test_e2e_pytest.py -v
```

## Artifacts and Reports

### Generated Outputs
- **Coverage Report**: `backend/htmlcov/index.html`
- **Coverage XML**: `backend/coverage.xml` (for external tools)
- **Test Results**: JUnit XML format for CI integration
- **Security Scan**: SARIF format uploaded to GitHub Security

### Download Links
- Test artifacts available in GitHub Actions run summary
- Coverage reports accessible via workflow artifacts
- Security scan results in repository Security tab

## Pipeline Triggers

### Automatic Triggers
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

### Manual Triggers
- Repository dispatch events
- Workflow dispatch (manual run from GitHub UI)
- Tag creation for release builds

## Performance Optimization

### Caching Strategy
- **pip dependencies**: `~/.cache/pip` cached by requirements.txt hash
- **npm packages**: `node_modules` cached by package-lock.json hash  
- **Docker layers**: GitHub Actions cache for faster image builds

### Parallel Execution
- Backend and frontend tests run in parallel
- Security scanning runs independently
- Docker builds only after successful tests

### Resource Limits
- **Test timeout**: 30 minutes per job
- **Artifact retention**: 90 days
- **Cache retention**: 7 days for unused entries

## Troubleshooting

### Common Issues

**Database Connection Failures:**
```bash
# Check PostgreSQL service status
pg_isready -h localhost -p 5432 -U lait

# Verify environment variables
echo $DATABASE_URL
```

**Redis Connection Issues:**
```bash
# Test Redis connectivity
redis-cli -h localhost -p 6379 ping

# Check Redis logs
docker logs <redis-container-id>
```

**Flask App Startup Problems:**
```bash
# Check Flask app health
curl -v http://localhost:5003/api/health

# Review Flask logs
python app_real.py  # Run in foreground to see errors
```

### Debug Commands
```bash
# Service status check
docker-compose ps

# View service logs
docker-compose logs db
docker-compose logs redis

# Database connection test
python -c "from app_real import app, db; app.app_context().push(); print(db.engine.url)"
```

## Deployment Pipeline

### Branch Strategy
- **`main`**: Production deployments
- **`develop`**: Staging deployments  
- **Feature branches**: PR validation only

### Release Process
1. **PR Review**: Code review and CI validation
2. **Merge to develop**: Staging deployment triggered
3. **Integration Testing**: Full system validation
4. **Merge to main**: Production deployment
5. **Tag Release**: Version tagging and release notes

## Monitoring and Alerting

### CI/CD Metrics
- **Test Success Rate**: Historical pass/fail trends
- **Build Duration**: Performance monitoring
- **Coverage Trends**: Code coverage over time
- **Security Findings**: Vulnerability tracking

### Notification Channels
- **GitHub**: PR comments with test results
- **Email**: Pipeline failure notifications
- **Slack**: Integration for team alerts (if configured)

---

🔧 **Need help?** Check the [troubleshooting section](#troubleshooting) or run `./scripts/run-ci-tests.sh` locally to debug issues.
