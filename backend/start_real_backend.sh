#!/bin/bash
# LAIT Real Backend Startup Script

echo "🚀 Starting LAIT Real Production Backend Setup"
echo "=============================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv_real" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv_real
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv_real/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements_real.txt

# Check if PostgreSQL is available
echo "🗃️ Checking database availability..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL found - will use PostgreSQL"
    DATABASE_TYPE="postgresql"
else
    echo "⚠️ PostgreSQL not found - will use SQLite fallback"
    DATABASE_TYPE="sqlite"
fi

# Setup database
echo "🔧 Setting up database..."
python setup_database.py

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env configuration file..."
    cat > .env << EOF
# LAIT Real Backend Configuration
FLASK_ENV=development
JWT_SECRET_KEY=lait-real-jwt-secret-$(date +%s)
SECRET_KEY=lait-real-secret-key-$(date +%s)

# Database Configuration
EOF
    
    if [ "$DATABASE_TYPE" = "postgresql" ]; then
        echo "DATABASE_URL=postgresql://lait_user:lait_secure_password_2024@localhost:5432/lait_production" >> .env
    else
        echo "DATABASE_URL=sqlite:///lait_real.db" >> .env
    fi
    
    cat >> .env << EOF

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Logging
LOG_LEVEL=INFO
LOG_FILE=lait_backend.log

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:5174
EOF

    echo "✅ Created .env configuration file"
fi

# Create uploads directory
mkdir -p uploads

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo ""
echo "🎯 Setup Complete!"
echo "=================="
echo "✅ Virtual environment: venv_real"
echo "✅ Dependencies installed"
echo "✅ Database configured"
echo "✅ Environment variables set"
echo "✅ Upload directory created"
echo ""

# Ask if user wants to start the server
read -p "🚀 Start the backend server now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting LAIT Real Backend on port 5003..."
    echo "🌐 Backend API: http://localhost:5003"
    echo "🔍 Health Check: http://localhost:5003/api/health"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the backend
    python app_real.py
else
    echo ""
    echo "🔧 To start the backend manually:"
    echo "   source venv_real/bin/activate"
    echo "   python app_real.py"
    echo ""
    echo "📚 API Documentation:"
    echo "   POST /api/auth/register - User registration"
    echo "   POST /api/auth/login - User login"
    echo "   POST /api/invoices/upload - Upload & analyze invoice"
    echo "   GET /api/dashboard/metrics - Dashboard analytics"
    echo "   GET /api/analytics/vendors - Vendor analytics"
    echo ""
fi
