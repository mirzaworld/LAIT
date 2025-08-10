"""
Development authentication helpers for LAIT
"""
import os
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, create_access_token
from flask import request, current_app

def development_jwt_required(f):
    """
    JWT wrapper that allows development bypass for easier testing.
    In addition to dev environment variables, automatically bypasses when app TESTING flag is set.
    Also: if in TESTING mode and no Authorization header, auto-inject a temporary access token so
    that endpoint logic depending on get_jwt_identity() continues to work.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        testing = current_app and current_app.config.get('TESTING')
        if (
            os.getenv('FLASK_ENV') == 'development' or
            os.getenv('ENVIRONMENT') == 'dev' or
            testing
        ):
            auth_header = request.headers.get('Authorization')
            if auth_header and 'mock-jwt-token-for-development' in auth_header:
                return f(*args, **kwargs)
            if testing:
                # If no auth header provided, fabricate one-time token (identity=1)
                if not auth_header:
                    try:
                        token = create_access_token(identity=1)
                        request.headers.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'
                    except Exception:
                        pass
                return f(*args, **kwargs)
        # Otherwise enforce normal JWT
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated_function
