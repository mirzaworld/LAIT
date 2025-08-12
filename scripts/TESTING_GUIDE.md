# 🧪 LAIT Testing Scripts Usage Guide

This directory contains comprehensive testing scripts for the LAIT platform.

## 📋 Available Scripts

### 1. Route Probe Script (`route_probe.py`)
**Purpose**: Tests API endpoint accessibility and validates HTTP response codes

**Features**:
- Tests all critical LAIT API endpoints
- Validates expected vs actual HTTP status codes
- Checks authentication-protected routes
- Verifies legacy route handling
- Provides colored terminal output with detailed status

**Usage**:
```bash
# Make sure the backend is running first
cd backend && python app_real.py &

# Then run the route probe
python scripts/route_probe.py

# OR run it directly (it's executable)
./scripts/route_probe.py
```

**What it tests**:
- ✅ `/api/health` → Should return 200 OK
- ⚠️ `/api/auth/register` → Should return 400/422 (bad request without data)
- ⚠️ `/api/auth/login` → Should return 400/422 (bad request without data)  
- 🔒 `/api/invoices` → Should return 401 (unauthorized without JWT)
- 🔒 `/api/invoices/upload` → Should return 401 (unauthorized without JWT)
- 🔒 `/api/dashboard/metrics` → Should return 401 (unauthorized without JWT)
- ✅ `/api/ml/status` → Should return 200 OK
- ❌ `/api/upload-invoice` → Should return 404 (legacy route)

### 2. Smoke Test Script (`smoke.sh`)
**Purpose**: End-to-end functional testing of the complete LAIT workflow

**Features**:
- Complete user registration and authentication flow
- File upload and processing validation
- Data persistence verification
- Dashboard metrics validation
- Comprehensive error handling and reporting

**Usage**:
```bash
# Make sure the backend is running first
cd backend && python app_real.py &

# Run the smoke test
./scripts/smoke.sh

# Or run with bash explicitly
bash scripts/smoke.sh
```

**Test Flow**:
1. **Health Check** → Verifies backend is running and responsive
2. **User Registration** → Creates test user and captures JWT token
3. **User Login** → Verifies authentication flow
4. **File Upload** → Creates `sample.txt` with 2 lines and uploads it
5. **Data Verification** → Confirms `lines_processed >= 2` 
6. **Persistence Check** → Lists invoices and verifies non-empty result
7. **Metrics Validation** → Checks `invoices_count >= 1` and `total_spend > 0`
8. **Success Report** → Displays "SMOKE OK" if all tests pass

## 🚀 Quick Start

### Prerequisites
```bash
# Install required tools
brew install curl jq  # macOS
# OR
apt-get install curl jq  # Ubuntu/Debian

# Make sure Python 3 is available
python3 --version
```

### Running Both Scripts
```bash
# 1. Start the LAIT backend
cd /Users/mirza/Documents/GitHub/LAIT/backend
python app_real.py &

# 2. Wait a moment for startup, then test routes
cd /Users/mirza/Documents/GitHub/LAIT
./scripts/route_probe.py

# 3. Run comprehensive smoke test
./scripts/smoke.sh
```

## 📊 Expected Output

### Route Probe Success Example:
```
🚀 LAIT API Route Probe
==================================================
Testing against: http://localhost:5003

/api/health               → GET  200 ✅ OK ✅
/api/auth/register        → POST 400 ⚠️  BAD REQUEST (Expected for routes requiring data) ✅
/api/auth/login           → POST 400 ⚠️  BAD REQUEST (Expected for routes requiring data) ✅
/api/invoices             → GET  401 🔒 UNAUTHORIZED (Expected for protected routes) ✅
/api/invoices/upload      → POST 401 🔒 UNAUTHORIZED (Expected for protected routes) ✅
/api/dashboard/metrics    → GET  401 🔒 UNAUTHORIZED (Expected for protected routes) ✅
/api/ml/status            → GET  200 ✅ OK ✅

🧪 Testing legacy route (should be 404):
/api/upload-invoice       → POST 404 ❌ NOT FOUND ✅

==================================================
✅ All critical routes behave as expected!
✅ Authentication routes properly reject empty requests
✅ Protected routes require JWT tokens
✅ Health and ML status endpoints are accessible
```

### Smoke Test Success Example:
```
╔════════════════════════════════════════╗
║        LAIT PLATFORM SMOKE TEST        ║
║                                        ║
║  Testing complete end-to-end workflow  ║
╚════════════════════════════════════════╝

=== STEP 0: Health Check ===
[SUCCESS] API is healthy and responding

=== STEP 1: User Registration ===
[SUCCESS] User registration successful
[SUCCESS] JWT token captured: eyJ0eXAiOiJKV1QiLCJ...

=== STEP 2: Invoice Upload ===
[SUCCESS] Upload processed 2 lines (expected >= 2) ✅
[SUCCESS] Invoice ID captured: 12345

=== STEP 3: List Invoices (verify non-empty) ===
[SUCCESS] Invoice list is non-empty ✅

=== STEP 4: Dashboard Metrics (verify invoices_count>=1 and total_spend>0) ===
[SUCCESS] invoices_count >= 1 ✅
[SUCCESS] total_spend > 0 ✅

╔════════════════════════════════════════╗
║              SMOKE OK ✅               ║
║                                        ║
║   All requirements validated:          ║
║   ✅ User registration & JWT           ║
║   ✅ sample.txt with 2 lines created   ║
║   ✅ Upload → lines_processed >= 2     ║
║   ✅ List invoices → non-empty         ║
║   ✅ Metrics → invoices_count >= 1     ║
║   ✅ Metrics → total_spend > 0         ║
╚════════════════════════════════════════╝
```

## 🔧 Troubleshooting

### Common Issues

**1. Connection Refused**
```
🔴 CONNECTION REFUSED - Backend not running?
```
**Solution**: Start the backend server:
```bash
cd backend && python app_real.py
```

**2. Missing Dependencies**
```
curl: command not found
jq: command not found
```
**Solution**: Install required tools:
```bash
# macOS
brew install curl jq

# Ubuntu/Debian  
sudo apt-get install curl jq
```

**3. Permission Denied**
```
Permission denied: ./scripts/smoke.sh
```
**Solution**: Make scripts executable:
```bash
chmod +x scripts/*.sh scripts/*.py
```

**4. Python Not Found**
```
python3: command not found
```
**Solution**: Install Python 3 or use system Python:
```bash
# Try different Python commands
python --version
python3 --version
/usr/bin/python3 --version
```

### Debug Mode
For more detailed output, you can modify the scripts:

```bash
# Add debug output to smoke.sh
export DEBUG=1
./scripts/smoke.sh

# Run route probe with verbose curl
# Edit route_probe.py and add -v flag to curl commands
```

## 📝 Script Customization

### Modifying Test Data
Edit the sample file content in `smoke.sh`:
```bash
# Change this section in smoke.sh
cat > "$invoice_file" << EOF
Your custom invoice line 1
Your custom invoice line 2
EOF
```

### Adding New Endpoints
Edit `route_probe.py` to add new routes:
```python
ROUTES_TO_TEST = [
    # Add your new route here
    ("/api/your-new-endpoint", "GET", [200]),
]
```

### Changing API Base URL
Update the API_BASE variable in both scripts:
```bash
# For different environments
API_BASE="https://your-production-api.com"  # Production
API_BASE="http://localhost:3000"            # Different port
API_BASE="http://api.lait.local:5003"       # Custom domain
```

## 🎯 Integration with CI/CD

These scripts are designed to be CI/CD friendly:

```bash
# In your CI pipeline
./scripts/route_probe.py || exit 1
./scripts/smoke.sh || exit 1
echo "All tests passed - ready for deployment"
```

Both scripts return appropriate exit codes:
- `0` = Success (all tests passed)
- `1` = Failure (one or more tests failed)

---

**Note**: These scripts are part of PROMPT 6 implementation and provide comprehensive validation of the LAIT platform's API functionality and end-to-end workflows.
