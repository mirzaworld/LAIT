#!/bin/bash

cd /app

# Set environment variables
export FLASK_APP=backend/wsgi.py
export PYTHONPATH=/app

# Create the migrations directory if it doesn't exist
mkdir -p migrations

# Run migrations
flask db upgrade

# Initialize the database if needed
python -c "
from backend.app import create_app
from backend.models import db
app = create_app()
with app.app_context():
    db.create_all()
"

echo "Database initialization complete."
