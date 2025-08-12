#!/usr/bin/env python3
"""
Test rate limiting setup
"""

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Test rate limiter setup
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per hour"],
    storage_uri="memory://"
)

@app.route('/test')
@limiter.limit("3 per minute")
def test_rate_limit():
    return jsonify({"message": "Rate limit test", "ip": get_remote_address()})

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded",
        "hint": f"Try again in {e.retry_after} seconds",
        "code": 9001
    }), 429

if __name__ == '__main__':
    print("Starting test rate limit server on port 5005...")
    app.run(debug=True, host='0.0.0.0', port=5005)
