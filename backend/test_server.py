#!/usr/bin/env python3
"""
Simple test server to verify basic functionality
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return jsonify({
        "service": "LAIT Test Server",
        "status": "operational",
        "message": "Basic server test"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "server": "test_server"
    })

@app.route('/api/test')
def test():
    return jsonify({
        "test": "success",
        "message": "Test endpoint working"
    })

if __name__ == '__main__':
    port = int(os.environ.get('API_PORT', 5004))
    print(f"Starting test server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
