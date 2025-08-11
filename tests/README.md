# LAIT End-to-End Tests

This directory contains comprehensive end-to-end tests for the LAIT (Legal AI Intelligence Tool) application.

## Overview

The E2E tests verify the complete user workflow:

1. **Health Check** - Verify API is running
2. **User Registration** - Create new user account  
3. **User Login** - Authenticate existing user
4. **Invoice Upload** - Upload and analyze invoice files
5. **Invoice List** - Retrieve user's invoices
6. **Analytics Summary** - Get dashboard metrics
7. **Data Consistency** - Verify data integrity across endpoints

## Test Files

### `test_e2e.py` (Standalone)
- Complete E2E test suite using pure `requests`
- Self-contained with detailed logging
- Can be run directly: `python3 test_e2e.py`

### `test_e2e_pytest.py` (Pytest Framework)  
- Structured tests using pytest framework
- Proper test isolation with fixtures
- Detailed assertions and error reporting
- Run with: `pytest test_e2e_pytest.py -v`

### `run_tests.sh` (Test Runner)
- Automated test runner script
- Checks prerequisites (backend running)
- Installs dependencies if needed
- Runs the tests and reports results

## Prerequisites

### 1. Backend Server Running
The tests require the LAIT backend API to be running on `localhost:5003`.

Start the backend:
```bash
cd backend
./venv_real/bin/python3 app_real.py
```

### 2. Install Test Dependencies
```bash
pip3 install -r tests/requirements.txt
```

Or let the test runner install them automatically.

## Running Tests

### Option 1: Automated Test Runner (Recommended)
```bash
./tests/run_tests.sh
```

### Option 2: Direct Execution
```bash
# Standalone version
python3 tests/test_e2e.py

# Pytest version  
pytest tests/test_e2e_pytest.py -v
```

### Option 3: Specific Test Categories
```bash
# Run only authentication tests
pytest tests/test_e2e_pytest.py -m auth -v

# Run only upload tests
pytest tests/test_e2e_pytest.py -m upload -v

# Run only analytics tests
pytest tests/test_e2e_pytest.py -m analytics -v
```

## Test Configuration

### API Configuration
- **Base URL**: `http://localhost:5003/api`
- **Timeout**: 30 seconds per request
- **Test User**: Unique email per test run

### Environment Variables
You can override defaults with environment variables:
```bash
export LAIT_API_BASE="http://localhost:5003/api"
export LAIT_TEST_EMAIL="test@example.com"  
export LAIT_TEST_PASSWORD="TestPassword123!"
```

## Test Data

### Sample Invoice
Tests use a realistic sample invoice:
- **Vendor**: Legal Services LLC
- **Amount**: $5,967.50 
- **Hours**: 15.5
- **Rate**: $350/hour
- **Format**: Plain text (.txt)

### User Data
Each test creates a unique user:
- **Email**: `test-{uuid}@lait.example.com`
- **Password**: `TestPassword123!`
- **Name**: `Test User-{uuid}`
- **Company**: `LAIT Test Company`

## Test Output

### Successful Test Run
```
🧪 Starting LAIT End-to-End Tests
==================================================

1. 🔍 Testing API Health Check...
✅ Health check passed

2. 👤 Testing User Registration...
✅ User registered successfully: test-abc123@lait.example.com

3. 🔐 Testing User Login...
✅ User logged in successfully: test-abc123@lait.example.com

4. 📄 Testing Invoice Upload...
✅ Invoice uploaded successfully: INV-001
   Vendor: Legal Services LLC
   Amount: $5967
   Risk Score: 25

5. 📋 Testing Invoice List...
✅ Invoice list retrieved: 1 invoice(s)
   Found uploaded invoice: INV-001

6. 📊 Testing Analytics Summary...
✅ Analytics retrieved successfully:
   Total Invoices: 1
   Total Amount: $5,967
   Total Vendors: 1
   Monthly Spending: $5,967

7. 🔍 Testing Data Consistency...
✅ Data consistency verified

==================================================
🎉 ALL TESTS PASSED!
==================================================
```

## Test Markers

Tests are organized with pytest markers:

- `@pytest.mark.e2e` - End-to-end integration tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.upload` - File upload tests  
- `@pytest.mark.analytics` - Analytics and metrics tests
- `@pytest.mark.integration` - Full workflow tests

## Troubleshooting

### Common Issues

1. **Backend Not Running**
   ```
   ❌ Cannot reach API: Connection refused
   💡 Make sure the backend server is running on localhost:5003
   ```
   
   **Solution**: Start the backend server first.

2. **Import Errors**
   ```
   ❌ Import "requests" could not be resolved
   ```
   
   **Solution**: Install test dependencies:
   ```bash
   pip3 install -r tests/requirements.txt
   ```

3. **Authentication Errors**
   ```
   ❌ Registration failed: 422 - Validation error
   ```
   
   **Solution**: Check that the database is clean and backend is configured correctly.

4. **Upload Errors**
   ```
   ❌ Upload failed: 401 - Unauthorized
   ```
   
   **Solution**: Ensure authentication is working and JWT tokens are valid.

### Debug Mode

Run tests with debug output:
```bash
# Standalone version with debug
python3 tests/test_e2e.py --debug

# Pytest with verbose output
pytest tests/test_e2e_pytest.py -v -s --tb=long
```

### Clean Database

For consistent test results, ensure a clean database state:
```bash
# Reset database (if using Docker)
docker-compose down -v
docker-compose up -d postgres
docker-compose run --rm migrate
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start Backend
        run: |
          cd backend
          python3 -m venv venv
          source venv/bin/activate
          pip install -r requirements_real.txt
          python app_real.py &
          sleep 10
      
      - name: Run E2E Tests
        run: ./tests/run_tests.sh
```

## Performance Considerations

- Tests create unique users to avoid conflicts
- Each test is independent and can run in parallel
- Database cleanup handled automatically
- Tests complete in ~30-60 seconds typically

## Extending Tests

### Adding New Test Cases
1. Follow the existing pattern in `test_e2e_pytest.py`
2. Use appropriate pytest markers
3. Add proper assertions and error messages
4. Update this README with new test descriptions

### Custom Test Data
Create custom fixtures for different test scenarios:
```python
@pytest.fixture
def large_invoice():
    return create_invoice_content(amount=50000, hours=100)

@pytest.fixture  
def multi_vendor_data():
    return [create_vendor_data(name) for name in vendor_names]
```

## Support

For issues with the test suite:
1. Check test output for specific error messages
2. Verify backend API is accessible at localhost:5003
3. Ensure all dependencies are installed
4. Review test configuration and environment variables
5. Check backend logs for server-side errors
