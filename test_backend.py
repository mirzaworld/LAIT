#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "message": "Test backend working"})

@app.route('/api/test')
def test():
    return jsonify({"test": "success"})

if __name__ == '__main__':
    print("🚀 Starting Test Backend on port 5003")
    app.run(host='0.0.0.0', port=5003, debug=True)
