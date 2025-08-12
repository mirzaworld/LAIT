#!/bin/bash
echo "=== Testing LAIT Backend Rate Limiting ==="

# Test health endpoint first
echo "Testing health endpoint..."
curl -s -w "HTTP: %{http_code}\n" http://localhost:5003/api/health
echo ""

# Test login rate limiting (5 per minute)
echo "Testing login rate limiting (should get 429 after 5 attempts)..."
for i in {1..7}; do
    echo "Login attempt $i:"
    curl -s -w "HTTP: %{http_code}\n" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"wrongpassword"}' \
        http://localhost:5003/api/auth/login
    echo ""
    sleep 1
done

echo "=== Rate Limiting Test Complete ==="
