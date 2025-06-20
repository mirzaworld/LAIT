#!/bin/bash

# LAIT Integration Test Script
# Tests all major frontend-backend integration points

echo "🧪 LAIT Frontend-Backend Integration Test"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# JWT token for testing
JWT_TOKEN="mock-jwt-token-for-development"

# Function to test an endpoint
test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected_key="$3"
    
    echo -n "Testing $name... "
    
    response=$(curl -s -w "%{http_code}" -H "Content-Type: application/json" -H "Authorization: Bearer $JWT_TOKEN" "http://localhost:8000/api${endpoint}")
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | jq -e ".$expected_key" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ PASS${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}✗ FAIL (missing $expected_key)${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo -e "${RED}✗ FAIL (HTTP $http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to check if service is running
check_service() {
    local name="$1"
    local url="$2"
    
    echo -n "Checking $name... "
    
    if curl -s -f -H "Authorization: Bearer $JWT_TOKEN" "$url" > /dev/null; then
        echo -e "${GREEN}✓ RUNNING${NC}"
        return 0
    else
        echo -e "${RED}✗ NOT RUNNING${NC}"
        return 1
    fi
}

echo
echo "📋 Pre-flight Checks"
echo "--------------------"

# Check if services are running
check_service "Backend API" "http://localhost:8000/api/analytics/summary"
backend_running=$?

check_service "Frontend Dev Server" "http://localhost:5174"
frontend_running=$?

if [ $backend_running -ne 0 ] || [ $frontend_running -ne 0 ]; then
    echo -e "${RED}❌ Required services not running. Please start them first.${NC}"
    exit 1
fi

echo
echo "🔌 API Endpoint Tests"
echo "--------------------"

# Test all major endpoints
test_endpoint "Analytics Summary" "/analytics/summary" "total_spend"
test_endpoint "Spend Trends" "/analytics/spend-trends" "labels"
test_endpoint "Vendors List" "/vendors" "vendors"
test_endpoint "Invoices List" "/invoices" "invoices"

echo
echo "🌐 Frontend Integration Test"
echo "----------------------------"

# Test if frontend can load without JavaScript errors
echo -n "Testing frontend page load... "
if curl -s "http://localhost:5174" | grep -q "root"; then
    echo -e "${GREEN}✓ PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo
echo "📊 Results Summary"
echo "=================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Integration is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the issues above.${NC}"
    exit 1
fi
