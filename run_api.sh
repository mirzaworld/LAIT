#!/bin/bash
# LAIT API Starter Script

echo "🔍 Checking environment..."
# Ensure we're in the right directory
cd "$(dirname "$0")"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3 to run this application."
    exit 1
fi

# Check for requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Checking dependencies..."
    if ! python3 -c "import pandas, flask, flask_cors" 2>/dev/null; then
        echo "⚠️  Required packages not found. Installing dependencies..."
        pip install -r requirements.txt
    fi
fi

# Set environment variable for Flask
export FLASK_APP=backend/enhanced_app.py

# Run Alembic migrations (auto-upgrade)
if [ -d "backend/migrations" ]; then
  echo "🗄  Applying database migrations..."
  if command -v alembic &> /dev/null; then
    alembic -c backend/migrations/alembic.ini upgrade head || echo "⚠️  Alembic upgrade failed (continuing)"
  else
    echo "ℹ️  Alembic not installed, installing..." && pip install alembic && alembic -c backend/migrations/alembic.ini upgrade head || echo "⚠️  Alembic upgrade failed"
  fi
fi

echo "🚀 Starting LAIT API server..."
echo "🔗 API will be available at http://localhost:5003"

# Start the Flask application
python3 backend/enhanced_app.py "$@"
