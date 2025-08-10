"""
Development authentication helpers for LAIT
"""
import os
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, create_access_token
from flask import request, current_app


def development_jwt_required(f):
    """
    JWT wrapper that allows development/testing bypass for easier local work.
    Behaviour:
      - In dev environments (FLASK_ENV=development or ENVIRONMENT=dev) always bypass normal JWT verification.
      - In TESTING mode, bypass is controlled by app.config['AUTO_AUTH_BYPASS'] (default True).
      - When bypassing and no Authorization header is present, tries to fabricate a temporary token (identity=1)
        so downstream code depending on get_jwt_identity() still works. Fails silently if JWT not initialized.
      - When NOT bypassing, performs normal verify_jwt_in_request(). Any failure returns a clean 401 JSON instead
        of bubbling up as a 500 to keep tests deterministic (some tests expect 401/422 on missing token).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        testing = bool(current_app) and current_app.config.get('TESTING')
        auto_bypass = True
        if current_app:
            auto_bypass = current_app.config.get('AUTO_AUTH_BYPASS', True)
        bypass_enabled = False
        if testing:
            # In testing mode, only bypass if explicitly allowed
            bypass_enabled = auto_bypass
        else:
            # In non-testing mode, use development environment checks
            bypass_enabled = (
                os.getenv('FLASK_ENV') == 'development' or
                os.getenv('ENVIRONMENT') == 'dev'
            )

        if bypass_enabled:
            auth_header = request.headers.get('Authorization')
            # Honor explicit mock token
            if auth_header and 'mock-jwt-token-for-development' in auth_header:
                return f(*args, **kwargs)
            # Auto inject only if none provided
            if not auth_header:
                try:
                    token = create_access_token(identity="1")  # Fix: use string identity
                    # Mutate the WSGI environ so downstream sees header
                    request.headers.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'
                except Exception:
                    # If JWT not initialized yet, just proceed without token
                    pass
            return f(*args, **kwargs)

        # Normal enforcement path
        try:
            verify_jwt_in_request()
        except Exception as e:  # Return a controlled 401 instead of 500
            return {
                "error": "authorization_required",
                "message": "Missing or invalid access token.",
                "detail": str(e),
            }, 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id():
    """
    Get the current user ID from JWT token, with fallback for test mode.
    In test mode, return user ID 1 if no valid JWT context.
    """
    from flask import current_app
    
    if current_app.config.get('TESTING'):
        try:
            from flask_jwt_extended import get_jwt_identity
            identity = get_jwt_identity()
            # JWT identity is now a string, convert to int for database lookup
            return int(identity) if identity else 1
        except:
            # Fallback to test user ID
            return 1
    else:
        from flask_jwt_extended import get_jwt_identity
        identity = get_jwt_identity()
        # Convert string identity to int for database lookup
        return int(identity) if identity else None
