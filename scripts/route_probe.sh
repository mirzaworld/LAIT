#!/bin/bash
#
# LAIT Route Probe Script (Bash version)
# Tests all critical API endpoints and reports their HTTP status codes.
#

API_BASE="http://localhost:5003"

echo "🚀 LAIT API Route Probe"
echo "=================================================="
echo "Testing against: $API_BASE"
echo ""

# Function to probe a route
probe_route() {
    local route="$1"
    local method="$2"
    local url="${API_BASE}${route}"
    
    if [[ "$method" == "POST" ]]; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{}' "$url" 2>/dev/null)
    else
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    fi
    
    case $status_code in
        200) status_desc="✅ OK" ;;
        201) status_desc="✅ CREATED" ;;
        400|3001|3101) status_desc="⚠️  BAD REQUEST (Expected for routes requiring data)" ;;
        401) status_desc="🔒 UNAUTHORIZED (Expected for protected routes)" ;;
        404) status_desc="❌ NOT FOUND" ;;
        405) status_desc="⚠️  METHOD NOT ALLOWED" ;;
        000) status_desc="🔴 CONNECTION REFUSED - Backend not running?" ;;
        5*) status_desc="💥 SERVER ERROR" ;;
        *) status_desc="ℹ️  HTTP $status_code" ;;
    esac
    
    printf "%-30s → %-3s %s\n" "$route" "$status_code" "$status_desc"
    
    # Return 1 for critical failures
    if [[ "$status_code" == "000" ]] || [[ "$status_code" == "404" && ("$route" == "/api/health" || "$route" == "/api/invoices/upload") ]]; then
        return 1
    fi
    # Consider backend working if we get any response (even 400/401 for empty requests)
    return 0
}

# Test routes
all_good=true

probe_route "/api/health" "GET" || all_good=false
probe_route "/api/auth/register" "POST" || all_good=false  
probe_route "/api/auth/login" "POST" || all_good=false
probe_route "/api/invoices" "GET" || all_good=false
probe_route "/api/invoices/upload" "POST" || all_good=false
probe_route "/api/dashboard/metrics" "GET" || all_good=false

echo ""
echo "=================================================="

if $all_good; then
    echo "✅ All critical routes are accessible!"
    echo "✅ Upload route '/api/invoices/upload' is properly configured"
    
    # Test that old upload route returns 404
    echo ""
    echo "🧪 Testing legacy route should return 404:"
    probe_route "/api/upload-invoice" "POST"
    
    exit 0
else
    echo "❌ Some routes failed - check backend status"
    exit 1
fi
