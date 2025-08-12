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

### Alternative Ways to Run

```bash
# From repo root
cd /path/to/LAIT
./scripts/smoke.sh

# From scripts directory  
cd scripts
./smoke.sh

# With bash explicitly
bash scripts/smoke.sh
```

## Expected Output

The script will show:
- 🟢 **SMOKE OK ✅** - All tests passed
- 🔴 **Error messages** - If any test fails

## Success Criteria

The test passes when all 5 steps complete successfully:
1. ✅ API health check responds with 200
2. ✅ User registration returns 201 with JWT token
3. ✅ User login returns 200 with valid token
4. ✅ Invoice upload returns 200/201 with analysis
5. ✅ Invoice list returns 200 with uploaded file
6. ✅ Dashboard metrics returns 200 with analytics

## Test Data

The script creates:
- **Test User**: `smoketest+[timestamp]@lait.com`
- **Password**: `TestPass123!`
- **Sample Invoice**: 8-line legal services invoice ($1,500)
- **Temporary Files**: Cleaned up automatically

## Troubleshooting

### API Not Running
```
[ERROR] API health check failed. HTTP code: 000
```
**Solution**: Start the backend server:
```bash
cd backend && python app_real.py
```

### Authentication Errors
```
[ERROR] Failed to extract JWT token
```
**Solution**: Check backend logs and ensure registration endpoint is working

### Upload Failures
```
[ERROR] Invoice upload failed
```
**Solution**: Verify file permissions and backend file handling

## Development Notes

- Uses timestamp-based test users to avoid conflicts
- Creates temporary files in `/tmp/lait_smoke_$$`
- Automatically cleans up on exit or interrupt
- Compatible with macOS and Linux
- Provides detailed error messages for debugging

## Script Features

- **Cross-platform compatibility** (macOS/Linux)
- **Automatic cleanup** of temporary files
- **Detailed logging** with timestamps
- **Error handling** with specific guidance
- **Signal handling** for clean interruption
- **JSON parsing** for response validation
- **Colorized output** for better readability
