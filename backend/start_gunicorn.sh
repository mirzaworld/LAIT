#!/bin/bash

# LAIT Backend Production Startup Script
# =====================================
# 
# Launches the LAIT backend using Gunicorn with production-optimized settings:
# - 2 worker processes for handling concurrent requests
# - gthread worker class for handling blocking I/O operations
# - Binding to all interfaces (0.0.0.0) on port 5003
# - Graceful shutdown handling and health check readiness

set -e

echo "🚀 Starting LAIT Backend with Gunicorn..."
echo "==========================================="

# Set production environment variables
export FLASK_ENV=production
export FLASK_DEBUG=false
export PYTHONPATH="${PYTHONPATH}:/app/backend:/app"

# Validate application exists
if [ ! -f "app_real.py" ] && [ ! -f "/app/backend/app_real.py" ]; then
    echo "❌ Error: app_real.py not found"
    echo "   Expected in current directory or /app/backend/"
    exit 1
fi

# Database initialization with enhanced error handling
echo "🔧 Initializing database..."
python -c "
import sys, os
# Add both potential paths for imports
sys.path.insert(0, '/app/backend')
sys.path.insert(0, '/app')
sys.path.insert(0, '.')

try:
    from app_real import app, db
    print('✅ Successfully imported app_real module')
    
    with app.app_context():
        db.create_all()
        print('✅ Database tables created/verified')
        
        # Quick health check
        from flask import current_app
        print(f'✅ App configured with {len(current_app.url_map._rules)} routes')
        
except Exception as e:
    print(f'⚠️  Database init error: {e}')
    print('   Will attempt to continue - manual DB setup may be required')
    import traceback
    traceback.print_exc()
"

# Gunicorn production configuration
WORKERS=2
WORKER_CLASS=gthread  
THREADS=4
BIND_ADDRESS="0.0.0.0:5003"
TIMEOUT=120
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100

echo ""
echo "🎯 Production Configuration:"
echo "   Workers: $WORKERS ($WORKER_CLASS)"
echo "   Threads per worker: $THREADS" 
echo "   Binding: $BIND_ADDRESS"
echo "   Timeout: ${TIMEOUT}s"
echo "   Max requests: $MAX_REQUESTS (±$MAX_REQUESTS_JITTER)"
echo "   Health check: http://0.0.0.0:5003/api/health"
echo ""

# Launch Gunicorn with optimized production settings
echo "🚀 Launching Gunicorn server..."
exec gunicorn \
    --workers $WORKERS \
    --worker-class $WORKER_CLASS \
    --threads $THREADS \
    --bind $BIND_ADDRESS \
    --timeout $TIMEOUT \
    --keep-alive 5 \
    --max-requests $MAX_REQUESTS \
    --max-requests-jitter $MAX_REQUESTS_JITTER \
    --worker-connections 1000 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    "app_real:app"
