#!/bin/bash

# LAIT E2E Test Runner
set -e

echo "🧪 LAIT End-to-End Test Runner"
echo "=============================="

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if backend is running
echo "🔍 Checking if backend is running..."
if ! curl -f http://localhost:5003/api/health > /dev/null 2>&1; then
    echo "❌ Backend not running on localhost:5003"
    echo "💡 Start the backend first:"
    echo "   cd backend && ./venv_real/bin/python3 app_real.py"
    exit 1
fi

echo "✅ Backend is running"

# Install test dependencies if needed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installing test dependencies..."
    pip3 install -r tests/requirements.txt
fi

# Run the E2E tests
echo "🚀 Running E2E tests..."
echo ""

python3 tests/test_e2e.py

echo ""
echo "🎯 E2E tests completed!"
