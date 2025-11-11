<!-- Archived README: scripts/README.md -->

````markdown
# LAIT Platform Smoke Test

## Overview
The `smoke.sh` script performs a comprehensive end-to-end test of the LAIT platform to ensure all components are working correctly.

## What it Tests

### 1. Health Check ✅
- Tests API availability at `http://localhost:5003/api/health`
- Verifies server is running and responding

### 2. User Registration ✅
- Creates a new test user with timestamp-based email
- Captures JWT authentication token
- Validates registration endpoint

### 3. User Login Verification ✅
- Logs in with the registered user credentials
- Updates JWT token from login response
- Validates login endpoint

### 4. Invoice Upload ✅
- Creates a sample text invoice file
- Uploads the invoice using multipart form data
- Tests file processing and AI analysis
- Validates upload endpoint and authentication

### 5. Invoice Listing ✅
- Retrieves list of user's invoices
- Verifies uploaded invoice appears in results
- Validates list endpoint and data retrieval

### 6. Dashboard Metrics ✅
- Fetches analytics and dashboard data
- Validates metrics endpoint
- Confirms analytics processing is working

## Usage

### Prerequisites
- LAIT backend running on port 5003
- `curl` command available
- `python3` command available

### Running the Test

```bash
# Make executable (first time only)
chmod +x scripts/smoke.sh

# Run the smoke test
./scripts/smoke.sh
```

... (archived)

````
