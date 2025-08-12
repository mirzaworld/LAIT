#!/bin/bash

# LAIT Backend Startup Script
cd /Users/mirza/Documents/GitHub/LAIT/backend

# Export environment variables for testing
export TESTING=true
export DATABASE_URL="sqlite:///lait_test.db"
export SECRET_KEY="test-secret-key"
export JWT_SECRET_KEY="test-jwt-key"

# Start Flask app
echo "🚀 Starting LAIT Backend API..."
echo "Using SQLite database for testing"
echo "API will be available at: http://localhost:5003"
echo ""

/Users/mirza/Documents/GitHub/LAIT/backend/venv_real/bin/python /Users/mirza/Documents/GitHub/LAIT/backend/app_real.py
