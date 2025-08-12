#!/bin/bash

# LAIT CI Local Test Runner
# This script simulates the CI environment locally for testing

set -e

echo "🧪 LAIT CI Local Test Runner"
echo "============================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🐳 Starting PostgreSQL and Redis containers..."

# Start services using docker-compose
docker-compose -f docker-compose.yml up -d db redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Set environment variables
export DATABASE_URL="postgresql://lait:lait_password@localhost:5432/lait_test"
export REDIS_URL="redis://localhost:6379/0"
export FLASK_ENV=testing
export JWT_SECRET_KEY=test-secret-key-for-ci
export SECRET_KEY=test-secret-key-for-ci
export AUTO_AUTH_BYPASS=true
export TESTING=true

echo "📦 Installing dependencies..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv_real" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv_real
fi

# Activate virtual environment
source venv_real/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r ../tests/requirements.txt
pip install pytest pytest-cov pytest-html

echo "🗄️ Initializing database..."
python -c "
import sys
sys.path.append('.')
from app_real import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

echo "🧪 Running unit tests..."
python -m pytest tests/ -v --tb=short --cov=. --cov-report=xml --cov-report=html

echo "🚀 Starting Flask app for E2E tests..."
python app_real.py &
FLASK_PID=$!

# Wait for Flask to start
echo "⏳ Waiting for Flask app to start..."
sleep 5

# Check if app is running
if curl -f http://localhost:5003/api/health > /dev/null 2>&1; then
    echo "✅ Flask app is running"
else
    echo "❌ Flask app failed to start"
    kill $FLASK_PID || true
    exit 1
fi

echo "🧪 Running E2E tests..."
cd ..
python -m pytest tests/test_e2e_pytest.py -v --tb=short

# Clean up
echo "🧹 Cleaning up..."
kill $FLASK_PID || true

echo "🐳 Stopping containers..."
docker-compose -f docker-compose.yml down

echo "✅ All tests completed successfully!"
echo ""
echo "📊 Test results:"
echo "   - Unit test coverage: backend/htmlcov/index.html"
echo "   - Coverage XML: backend/coverage.xml"
