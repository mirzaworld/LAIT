#!/bin/bash

# LAIT Application - Memory-Optimized Startup Script
# This script increases Node.js memory limits and starts the development server

echo "Starting LAIT application with increased memory allocation..."

# Set Node.js memory limits
export NODE_OPTIONS="--max-old-space-size=4096"

# Check if Python environment is activated, if not, try to activate it
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Python virtual environment not detected..."
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    elif [ -d "env" ]; then
        echo "Activating virtual environment..."
        source env/bin/activate
    else
        echo "Warning: No virtual environment found. Python backend may not run correctly."
    fi
fi

# Start backend server in the background
echo "Starting backend server..."
cd backend
python enhanced_app.py --allow-unsafe-werkzeug &
BACKEND_PID=$!
cd ..

# Wait for the backend to start
sleep 2

# Start frontend with increased memory
echo "Starting frontend with increased memory allocation (4GB)..."
npm run dev

# Cleanup when the script is terminated
function cleanup {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    echo "Cleanup complete."
}

# Register the cleanup function
trap cleanup EXIT

# Wait for the frontend process to finish
wait
