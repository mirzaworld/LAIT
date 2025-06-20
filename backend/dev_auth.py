"""
Development authentication helpers for LAIT
"""
import os
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import request

def development_jwt_required(f):
    """
    JWT wrapper that allows development bypass for easier testing
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In development, allow a mock token to bypass JWT
        if os.getenv('FLASK_ENV') == 'development' or os.getenv('ENVIRONMENT') == 'dev':
            auth_header = request.headers.get('Authorization')
            if auth_header and 'mock-jwt-token-for-development' in auth_header:
                # Mock a successful JWT verification for development
                return f(*args, **kwargs)
        
        # Otherwise, use normal JWT verification
        verify_jwt_in_request()
        return f(*args, **kwargs)
    
    return decorated_function
