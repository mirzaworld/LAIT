#!/bin/bash

# LAIT Platform Smoke Test
# Tests the complete end-to-end functionality of the LAIT platform
# Author: LAIT Development Team
# Version: 1.0.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE="http://localhost:5003"
HEALTH_ENDPOINT="$API_BASE/api/health"
REGISTER_ENDPOINT="$API_BASE/api/auth/register"
LOGIN_ENDPOINT="$API_BASE/api/auth/login"
UPLOAD_ENDPOINT="$API_BASE/api/invoices/upload"
LIST_ENDPOINT="$API_BASE/api/invoices"
METRICS_ENDPOINT="$API_BASE/api/dashboard/metrics"

# Test user credentials
TEST_EMAIL="smoketest+$(date +%s)@lait.com"
TEST_PASSWORD="TestPass123!"
TEST_FIRST_NAME="Smoke"
TEST_LAST_NAME="Tester"
TEST_COMPANY="LAIT Test Corp"

# Global variables
JWT_TOKEN=""
TEMP_DIR="/tmp/lait_smoke_$$"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${YELLOW}=== $1 ===${NC}"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR" 2>/dev/null || true
}

# Set trap for cleanup
trap cleanup EXIT

# Create temporary directory
mkdir -p "$TEMP_DIR"

# Test 0: Check if API is running
test_health_check() {
    log_step "STEP 0: Health Check"
    log_info "Testing API health at: $HEALTH_ENDPOINT"
    
    local response
    response=$(curl -s -w "\n%{http_code}" "$HEALTH_ENDPOINT" 2>/dev/null || echo -e "\n000")
    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "200" ]]; then
        log_success "API is healthy and responding"
        log_info "Response: $body"
    else
        log_error "API health check failed. HTTP code: $http_code"
        log_error "Make sure the API server is running on port 5003"
        log_error "Try: cd backend && python app_real.py"
        exit 1
    fi
}

# Test 1: User Registration
test_user_registration() {
    log_step "STEP 1: User Registration"
    log_info "Registering test user: $TEST_EMAIL"
    
    local payload
    payload=$(cat << EOF
{
    "email": "$TEST_EMAIL",
    "password": "$TEST_PASSWORD",
    "firstName": "$TEST_FIRST_NAME",
    "lastName": "$TEST_LAST_NAME",
    "company": "$TEST_COMPANY"
}
EOF
)
    
    local response
    response=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$REGISTER_ENDPOINT" 2>/dev/null || echo -e "\n000")
    
    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "201" ]]; then
        log_success "User registration successful"
        
        # Extract JWT token from response
        JWT_TOKEN=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    token = data.get('access_token') or data.get('token', '')
    print(token)
except:
    print('')
" 2>/dev/null)
        
        if [[ -n "$JWT_TOKEN" ]]; then
            log_success "JWT token captured: ${JWT_TOKEN:0:20}..."
        else
            log_error "Failed to extract JWT token from registration response"
            log_error "Response: $body"
            exit 1
        fi
    else
        log_error "User registration failed. HTTP code: $http_code"
        log_error "Response: $body"
        exit 1
    fi
}

# Test 2: User Login (alternative token acquisition)
test_user_login() {
    log_step "STEP 1.5: User Login Verification"
    log_info "Verifying login with registered user: $TEST_EMAIL"
    
    local payload
    payload=$(cat << EOF
{
    "email": "$TEST_EMAIL",
    "password": "$TEST_PASSWORD"
}
EOF
)
    
    local response
    response=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$LOGIN_ENDPOINT" 2>/dev/null || echo -e "\n000")
    
    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "200" ]]; then
        log_success "User login successful"
        
        # Update JWT token from login response (in case registration didn't provide one)
        local login_token
        login_token=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    token = data.get('access_token') or data.get('token', '')
    print(token)
except:
    print('')
" 2>/dev/null)
        
        if [[ -n "$login_token" ]]; then
            JWT_TOKEN="$login_token"
            log_success "JWT token updated from login: ${JWT_TOKEN:0:20}..."
        fi
    else
        log_warn "User login failed. HTTP code: $http_code (continuing with registration token)"
        log_info "Response: $body"
    fi
}

# Test 3: Create sample.txt with two lines and upload
test_invoice_upload() {
    log_step "STEP 2: Invoice Upload"
    log_info "Creating sample.txt with two lines for upload test"
    
    # Create exactly what the requirements specify: sample.txt with two lines
    local invoice_file="$TEMP_DIR/sample.txt"
    cat > "$invoice_file" << EOF
Legal Services: Attorney John Smith, 450/hr, 8.5 hours, Total: $3825.00
Legal Research: Paralegal Sarah Johnson, 180/hr, 6.0 hours, Total: $1080.00
EOF
    
    log_info "Created sample.txt file: $invoice_file"
    log_info "File content (2 lines):"
    cat "$invoice_file" | sed 's/^/  /'
    
    # Verify JWT token is available
    if [[ -z "$JWT_TOKEN" ]]; then
        log_error "No JWT token available for upload. Registration/login failed."
        exit 1
    fi
    
    log_info "Uploading sample.txt with JWT token: ${JWT_TOKEN:0:20}..."
    
    local response
    response=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -F "file=@$invoice_file" \
        -F "client_name=Smoke Test Client" \
        -F "matter_id=SMOKE-001" \
        "$UPLOAD_ENDPOINT" 2>/dev/null || echo -e "\n000")
    
    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "201" ]] || [[ "$http_code" == "200" ]]; then
        log_success "Invoice upload successful"
        log_info "Upload response: $body"
        
        # Check that lines_processed >= 2
        local lines_processed
        lines_processed=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    lines = data.get('lines_processed', 0)
    print(lines)
except:
    print('0')
" 2>/dev/null)
        
        if [[ "$lines_processed" -ge "2" ]]; then
            log_success "Upload processed $lines_processed lines (expected >= 2) ✅"
        else
            log_error "Upload processed insufficient lines: $lines_processed (expected >= 2)"
            exit 1
        fi
        
        # Try to extract invoice ID for verification
        local invoice_id
        invoice_id=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    invoice = data.get('invoice', {})
    invoice_id = invoice.get('id') or data.get('invoice_id', '')
    print(invoice_id)
except:
    print('')
" 2>/dev/null)
        
        if [[ -n "$invoice_id" ]]; then
            log_success "Invoice ID captured: $invoice_id"
        fi
    else
        log_error "Invoice upload failed. HTTP code: $http_code"
        log_error "Response: $body"
        exit 1
    fi
}

# Test 4: List invoices (verify non-empty)
test_list_invoices() {
    log_step "STEP 3: List Invoices (verify non-empty)"
    log_info "Retrieving invoice list to verify persistence"
    
    if [[ -z "$JWT_TOKEN" ]]; then
        log_error "No JWT token available for listing invoices."
        exit 1
    fi
    
    local response
    response=$(curl -s -w "\n%{http_code}" \
        -X GET \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$LIST_ENDPOINT" 2>/dev/null || echo -e "\n000")
    
    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "200" ]]; then
        log_success "Invoice list retrieved successfully"
        
        # Count invoices in response
        local invoice_count
        invoice_count=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    invoices = data.get('invoices', [])
    print(len(invoices))
except:
    print('0')
" 2>/dev/null)
        
        log_info "Found $invoice_count invoice(s) in the list"
        if [[ "$invoice_count" -gt "0" ]]; then
            log_success "Invoice list is non-empty ✅"
        else
            log_error "Invoice list is empty - upload may have failed"
            exit 1
        fi
    else
        log_error "Invoice listing failed. HTTP code: $http_code"
        log_error "Response: $body"
        exit 1
    fi
}

# Test 5: Get dashboard metrics (verify invoices_count>=1 and total_spend>0)
test_dashboard_metrics() {
    log_step "STEP 4: Dashboard Metrics (verify invoices_count>=1 and total_spend>0)"
    log_info "Retrieving dashboard analytics for validation"
    
    if [[ -z "$JWT_TOKEN" ]]; then
        log_error "No JWT token available for dashboard metrics."
        exit 1
    fi
    
    local response
    response=$(curl -s -w "\n%{http_code}" \
        -X GET \
        -H "Authorization: Bearer $JWT_TOKEN" \
        "$METRICS_ENDPOINT" 2>/dev/null || echo -e "\n000")
    
    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "200" ]]; then
        log_success "Dashboard metrics retrieved successfully"
        log_info "Metrics response: $body"
        
        # Extract and validate key metrics
        local validation_result
        validation_result=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Try different possible field names
    invoices_count = data.get('invoices_count', data.get('total_invoices', 0))
    total_spend = data.get('total_spend', data.get('total_amount', 0))
    
    print(f'invoices_count={invoices_count}')
    print(f'total_spend={total_spend}')
    
    # Validation
    if invoices_count >= 1:
        print('invoices_count_valid=true')
    else:
        print('invoices_count_valid=false')
    
    if float(total_spend) > 0:
        print('total_spend_valid=true')
    else:
        print('total_spend_valid=false')
        
except Exception as e:
    print(f'error={e}')
    print('invoices_count_valid=false')
    print('total_spend_valid=false')
" 2>/dev/null)
        
        log_info "Validation results: $validation_result"
        
        # Check validation results
        local invoices_valid=$(echo "$validation_result" | grep "invoices_count_valid=true" || echo "false")
        local spend_valid=$(echo "$validation_result" | grep "total_spend_valid=true" || echo "false")
        
        if [[ "$invoices_valid" == *"true"* ]]; then
            log_success "invoices_count >= 1 ✅"
        else
            log_error "invoices_count < 1 - dashboard metrics validation failed"
            exit 1
        fi
        
        if [[ "$spend_valid" == *"true"* ]]; then
            log_success "total_spend > 0 ✅"
        else
            log_error "total_spend <= 0 - dashboard metrics validation failed"
            exit 1
        fi
        
        log_success "Dashboard metrics validation passed ✅"
    else
        log_error "Dashboard metrics failed. HTTP code: $http_code"
        log_error "Response: $body"
        exit 1
    fi
}

# Main execution
main() {
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════╗"
    echo "║        LAIT PLATFORM SMOKE TEST        ║"
    echo "║                                        ║"
    echo "║  Testing complete end-to-end workflow  ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    log_info "Starting smoke test at $(date)"
    log_info "API Base URL: $API_BASE"
    log_info "Test User: $TEST_EMAIL"
    
    # Run all tests in sequence
    test_health_check
    test_user_registration  
    test_user_login
    test_invoice_upload
    test_list_invoices
    test_dashboard_metrics
    
    # Success message
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════╗"
    echo "║              SMOKE OK ✅               ║"
    echo "║                                        ║"
    echo "║   All requirements validated:          ║"
    echo "║   ✅ User registration & JWT           ║"
    echo "║   ✅ sample.txt with 2 lines created   ║"
    echo "║   ✅ Upload → lines_processed >= 2     ║"
    echo "║   ✅ List invoices → non-empty         ║"
    echo "║   ✅ Metrics → invoices_count >= 1     ║"
    echo "║   ✅ Metrics → total_spend > 0         ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    log_success "Smoke test completed successfully at $(date)"
    log_info "Test user created: $TEST_EMAIL"
    log_info "JWT token: ${JWT_TOKEN:0:30}..."
    log_info "All API endpoints are functioning correctly"
    
    echo -e "\n${BLUE}Next steps:${NC}"
    echo "  • Open http://localhost:5173 to test the frontend"
    echo "  • Login with: $TEST_EMAIL / $TEST_PASSWORD"
    echo "  • Upload more invoices and explore the dashboard"
    echo ""
}

# Handle script interruption
handle_interrupt() {
    echo -e "\n${YELLOW}[INTERRUPTED]${NC} Smoke test was interrupted"
    cleanup
    exit 130
}

trap handle_interrupt SIGINT SIGTERM

# Check if curl is available
if ! command -v curl &> /dev/null; then
    log_error "curl is required but not installed. Please install curl first."
    exit 1
fi

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    log_error "python3 is required but not installed. Please install python3 first."
    exit 1
fi

# Run the main function
main "$@"
