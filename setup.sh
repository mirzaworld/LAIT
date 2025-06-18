#!/bin/bash

echo "Setting up AI Legal Spend Optimizer environment..."

# Check for Python and Node.js
echo "Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Node.js is required but not found."
    exit 1
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Set up PostgreSQL if it's installed
if command -v psql &> /dev/null; then
    echo "Setting up PostgreSQL database..."
    
    # Check if database exists, create if it doesn't
    if ! psql -lqt | cut -d \| -f 1 | grep -qw legalspend; then
        echo "Creating 'legalspend' database..."
        createdb legalspend
    else
        echo "Database 'legalspend' already exists."
    fi
else
    echo "PostgreSQL not found. Please create the 'legalspend' database manually."
fi

echo "Setup complete!"
echo ""
echo "To start the backend server:"
echo "  source venv/bin/activate"
echo "  cd backend"
echo "  flask run"
echo ""
echo "To start the frontend development server (in a separate terminal):"
echo "  npm run dev"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
