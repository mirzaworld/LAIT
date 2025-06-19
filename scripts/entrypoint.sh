#!/bin/bash
set -e

# Directory for the application
cd /app

# Set environment variables
export FLASK_APP=backend/wsgi.py
export PYTHONPATH=/app

echo "Waiting for database to be ready..."
sleep 5

# Run database migrations
echo "Running database migrations..."
cd /app
python -m flask db upgrade

# Initialize the database if needed
echo "Initializing database..."
python -c "
from backend.app import create_app
from backend.models import db
app = create_app()
with app.app_context():
    db.create_all()
"

echo "Database initialization complete."

# Start the Flask application
echo "Starting Flask application..."
exec flask run --host=0.0.0.0 --port=5000
