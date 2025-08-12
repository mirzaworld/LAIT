#!/bin/bash
set -e

echo "🚀 Starting LAIT Backend with Gunicorn"
echo "======================================"

# Set production environment
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:/app/backend"

# Database initialization (if needed)
if [ "$DATABASE_URL" ]; then
    echo "📊 Database URL detected: ${DATABASE_URL:0:30}..."
    echo "🔧 Initializing database if needed..."
    python -c "
import os
import sys
sys.path.insert(0, '/app/backend')
try:
    from app_real import app, db
    with app.app_context():
        db.create_all()
        print('✅ Database tables initialized')
except Exception as e:
    print(f'⚠️  Database init warning: {e}')
"
fi

# Print configuration info
echo "🔧 Production Configuration:"
echo "   Workers: 2"
echo "   Thread model: gthread"
echo "   Bind address: 0.0.0.0:5003"
echo "   Application: app_real:app"

# Start Gunicorn with production settings
echo "🎯 Starting Gunicorn server..."
exec gunicorn \
    --workers 2 \
    --worker-class gthread \
    --threads 4 \
    --bind 0.0.0.0:5003 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    app_real:app
