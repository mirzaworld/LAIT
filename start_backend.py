#!/usr/bin/env python3
import os
import sys

# Add the project root to Python path
sys.path.insert(0, '/Users/mirza/Documents/GitHub/LAIT')

# Set environment variables
os.environ['PYTHONPATH'] = '/Users/mirza/Documents/GitHub/LAIT'
os.environ['FLASK_ENV'] = 'development'

from backend.enhanced_app import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting LAIT backend on http://127.0.0.1:5003")
    app.run(host='0.0.0.0', port=5003, debug=True)
