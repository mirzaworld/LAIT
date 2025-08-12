#!/bin/bash
# Simple test script for LAIT Real Backend

echo "Testing LAIT Real Backend on port 5003"
echo "======================================="

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -s -w "Status: %{http_code}\n" http://localhost:5003/api/health
echo ""

# Test 2: Register user
echo "2. Testing user registration..."
curl -s -w "Status: %{http_code}\n" -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}' \
  http://localhost:5003/api/auth/register | head -c 200
echo ""

# Test 3: Login user
echo "3. Testing user login..."
TOKEN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  http://localhost:5003/api/auth/login)
echo $TOKEN_RESPONSE | head -c 200
echo ""

# Extract token for subsequent requests
TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")

if [ ! -z "$TOKEN" ]; then
    echo "4. Testing invoice upload with JSON..."
    curl -s -w "\nStatus: %{http_code}\n" -X POST \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"vendor":"Test Firm","lines":[{"description":"Legal work","hours":5,"rate":450}]}' \
      http://localhost:5003/api/invoices/upload | head -c 200
    echo ""
    
    echo "5. Testing invoice list..."
    curl -s -w "\nStatus: %{http_code}\n" \
      -H "Authorization: Bearer $TOKEN" \
      http://localhost:5003/api/invoices | head -c 200
    echo ""
    
    echo "6. Testing dashboard metrics..."
    curl -s -w "\nStatus: %{http_code}\n" \
      -H "Authorization: Bearer $TOKEN" \
      http://localhost:5003/api/dashboard/metrics | head -c 200
    echo ""
else
    echo "Could not extract token, skipping authenticated tests"
fi

echo "Test complete!"
