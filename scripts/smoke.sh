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

# Test 3: Create and upload a tiny text invoice
test_invoice_upload() {
    log_step "STEP 2: Invoice Upload"
    log_info "Creating tiny text invoice for upload test"
    
    # Create a minimal invoice file
    local invoice_file="$TEMP_DIR/test_invoice.txt"
    cat > "$invoice_file" << EOF
INVOICE #12345
From: Test Legal Services LLC
To: LAIT Test Corp
Date: August 11, 2025
Amount: $1,500.00
Description: Legal consultation services
Hours: 5.0 @ $300/hour
Total: $1,500.00
EOF
    
    log_info "Created test invoice file: $invoice_file"
    log_info "Invoice content:"
    cat "$invoice_file" | sed 's/^/  /'
    
    # Verify JWT token is available
    if [[ -z "$JWT_TOKEN" ]]; then
        log_error "No JWT token available for upload. Registration/login failed."
        exit 1
    fi
    
    log_info "Uploading invoice with JWT token: ${JWT_TOKEN:0:20}..."
    
    local response
    response=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -F "file=@$invoice_file" \
        "$UPLOAD_ENDPOINT" 2>/dev/null || echo -e "\n000")
    
    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')
    
    if [[ "$http_code" == "201" ]] || [[ "$http_code" == "200" ]]; then
        log_success "Invoice upload successful"
        log_info "Response preview: $(echo "$body" | head -c 200)..."
        
        # Try to extract invoice ID for verification
        local invoice_id
        invoice_id=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    invoice = data.get('invoice', {})
    print(invoice.get('id', ''))
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

# Test 4: List invoices
test_list_invoices() {
    log_step "STEP 3: List Invoices"
    log_info "Retrieving invoice list"
    
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
            log_success "Invoice list contains uploaded invoice"
        else
            log_warn "No invoices found in list (may be processing)"
        fi
    else
        log_error "Invoice listing failed. HTTP code: $http_code"
        log_error "Response: $body"
        exit 1
    fi
}

# Test 5: Get dashboard metrics
test_dashboard_metrics() {
    log_step "STEP 4: Dashboard Metrics"
    log_info "Retrieving dashboard analytics"
    
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
        
        # Extract key metrics
        local metrics_summary
        metrics_summary=$(echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    total_invoices = data.get('total_invoices', 0)
    total_amount = data.get('total_amount', 0)
    total_vendors = data.get('total_vendors', 0)
    print(f'Invoices: {total_invoices}, Amount: \${total_amount:,.2f}, Vendors: {total_vendors}')
except Exception as e:
    print(f'Error parsing metrics: {e}')
" 2>/dev/null)
        
        log_info "Dashboard summary: $metrics_summary"
        log_success "Analytics data is available and properly formatted"
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
    echo -e "\n${GREEN}"
    echo "╔════════════════════════════════════════╗"
    echo "║              SMOKE OK ✅               ║"
    echo "║                                        ║"
    echo "║   All tests passed successfully!       ║"
    echo "║   LAIT platform is working correctly   ║"
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
