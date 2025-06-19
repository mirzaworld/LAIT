# LAIT System Testing Guide

## Testing Overview

The LAIT system uses multiple layers of testing to ensure reliability:

1. Unit Tests
2. Integration Tests
3. End-to-End Tests
4. Performance Tests
5. Security Tests

## Running Tests

### Backend Tests

1. Install test dependencies:
```bash
pip install -r backend/requirements-test.txt
```

2. Run unit tests:
```bash
cd backend
pytest tests/unit/
```

3. Run integration tests:
```bash
pytest tests/integration/
```

4. Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Frontend Tests

1. Install dependencies:
```bash
npm install
```

2. Run unit tests:
```bash
npm run test
```

3. Run E2E tests:
```bash
npm run test:e2e
```

## Test Descriptions

### Backend Tests

#### Unit Tests

1. ML Pipeline Tests
- Synthetic data generation
- Outlier detection
- Risk prediction
- Vendor analysis

2. API Tests
- Authentication endpoints
- Invoice processing
- Analytics calculations
- User management

3. Service Tests
- PDF parsing
- S3 file handling
- Audit logging
- Email notifications

#### Integration Tests

1. Database Tests
- Model relationships
- Query performance
- Migration testing
- Data integrity

2. External Service Tests
- S3 integration
- Redis caching
- PDF processing
- Email sending

### Frontend Tests

#### Component Tests

1. UI Components
- AlertsPanel
- MetricCard
- SpendChart
- TopVendors

2. Pages
- Dashboard
- Analytics
- Invoices
- Settings

#### E2E Tests

1. User Flows
- Login/Logout
- Invoice Upload
- Report Generation
- Settings Management

## Performance Testing

### Load Testing

1. Setup:
```bash
pip install locust
```

2. Run tests:
```bash
locust -f tests/performance/locustfile.py
```

### API Response Times

Test endpoints with:
```bash
ab -n 1000 -c 10 http://localhost:8000/api/health
```

## Security Testing

### Static Analysis

1. Run security scan:
```bash
bandit -r backend/
```

2. Check dependencies:
```bash
safety check
```

### Authentication Tests

1. Token validation
2. Permission checks
3. Rate limiting
4. Session management

## Test Coverage Requirements

- Backend: Minimum 80% coverage
- Frontend: Minimum 70% coverage
- Critical paths: 100% coverage

## Continuous Integration

Tests run automatically on:
1. Pull requests
2. Main branch commits
3. Release tags

### GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          docker-compose -f docker-compose.test.yml up --build --exit-code-from tests
```

## Test Data Management

### Fixtures

1. Database fixtures
2. S3 test files
3. Mock API responses

### Environment Setup

```bash
# Test environment variables
export FLASK_ENV=testing
export DATABASE_URL=postgresql://test:test@localhost:5432/test_db
export REDIS_URL=redis://localhost:6379/0
```

## Testing Best Practices

1. Test Independence
   - Each test should be independent
   - Clean up after each test
   - Use fresh fixtures

2. Test Organization
   - Group related tests
   - Clear test names
   - Comprehensive assertions

3. Mocking
   - Mock external services
   - Use dependency injection
   - Consistent mock data

4. Error Cases
   - Test edge cases
   - Error handling
   - Invalid inputs

## Troubleshooting Tests

### Common Issues

1. Database connection errors
   - Check test database URL
   - Verify permissions
   - Clean up connections

2. Asynchronous tests
   - Use proper wait conditions
   - Handle timeouts
   - Clean up resources

3. Mock issues
   - Verify mock setup
   - Check mock returns
   - Reset mocks properly

### Debug Tools

```bash
# Debug prints
pytest -vv

# Debug with pdb
pytest --pdb

# Show slow tests
pytest --durations=10
```
