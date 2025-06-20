#!/bin/bash

echo "🚀 LAIT Complete System Test"
echo "=================================="

# Test backend is running
echo "📡 Testing Backend..."
BACKEND_HEALTH=$(curl -s http://localhost:5002/api/health | grep -o "healthy" | head -1)
if [ "$BACKEND_HEALTH" = "healthy" ]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
    exit 1
fi

# Test dashboard metrics
echo "📊 Testing Dashboard Metrics..."
METRICS_RESPONSE=$(curl -s http://localhost:5002/api/dashboard/metrics)
INVOICE_COUNT=$(echo $METRICS_RESPONSE | grep -o '"invoice_count": *[0-9]*' | cut -d':' -f2 | tr -d ' ')
TOTAL_SPEND=$(echo $METRICS_RESPONSE | grep -o '"total_spend": *[0-9]*' | cut -d':' -f2 | tr -d ' ')

if [ ! -z "$INVOICE_COUNT" ] && [ ! -z "$TOTAL_SPEND" ]; then
    echo "✅ Dashboard metrics: $INVOICE_COUNT invoices, \$$TOTAL_SPEND total"
else
    echo "❌ Dashboard metrics not working"
    echo "Response: $METRICS_RESPONSE"
    exit 1
fi

# Test invoices endpoint
echo "📋 Testing Invoices Endpoint..."
INVOICES_RESPONSE=$(curl -s http://localhost:5002/api/invoices)
INVOICES_ARRAY=$(echo $INVOICES_RESPONSE | grep -o '\[.*\]' | head -1)
if [ ! -z "$INVOICES_ARRAY" ]; then
    echo "✅ Invoices endpoint working"
else
    echo "❌ Invoices endpoint not working"
    exit 1
fi

# Test vendors endpoint
echo "🏢 Testing Vendors Endpoint..."
VENDORS_RESPONSE=$(curl -s http://localhost:5002/api/vendors)
VENDORS_ARRAY=$(echo $VENDORS_RESPONSE | grep -o '\[.*\]' | head -1)
if [ ! -z "$VENDORS_ARRAY" ]; then
    echo "✅ Vendors endpoint working"
else
    echo "❌ Vendors endpoint not working"
    exit 1
fi

# Test CORS for frontend
echo "🌐 Testing CORS Configuration..."
CORS_RESPONSE=$(curl -s -I -X OPTIONS -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: GET" http://localhost:5002/api/dashboard/metrics)
CORS_ALLOW=$(echo "$CORS_RESPONSE" | grep -i "access-control-allow-origin")
if [ ! -z "$CORS_ALLOW" ]; then
    echo "✅ CORS configured properly"
else
    echo "❌ CORS not configured"
    exit 1
fi

# Test frontend accessibility
echo "🎨 Testing Frontend Server..."
FRONTEND_RESPONSE=$(curl -s -I http://localhost:5173)
FRONTEND_STATUS=$(echo "$FRONTEND_RESPONSE" | head -1 | grep "200 OK")
if [ ! -z "$FRONTEND_STATUS" ]; then
    echo "✅ Frontend server accessible"
else
    echo "❌ Frontend server not accessible"
    exit 1
fi

echo ""
echo "🎉 All tests passed! LAIT system is working correctly."
echo ""
echo "Summary:"
echo "- Backend API: ✅ Running on http://localhost:5002"
echo "- Frontend: ✅ Running on http://localhost:5173"
echo "- Database: ✅ $INVOICE_COUNT invoices loaded"
echo "- Total Spend: ✅ \$$TOTAL_SPEND tracked"
echo "- CORS: ✅ Configured for frontend"
echo ""
echo "🔗 Open http://localhost:5173 to use the application"
