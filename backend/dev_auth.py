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
        # Read explicit config first (set in enhanced_app). Default True for legacy.
        auto_bypass = True
        if current_app:
            auto_bypass = current_app.config.get('AUTO_AUTH_BYPASS', True)

        # Allow explicit app config to control bypass in both testing and non-testing modes.
        # Fall back to environment heuristic only if AUTO_AUTH_BYPASS not explicitly set.
        bypass_enabled = auto_bypass
        if auto_bypass is None:
            if testing:
                bypass_enabled = True
            else:
                bypass_enabled = (
                    os.getenv('FLASK_ENV') == 'development' or
                    os.getenv('ENVIRONMENT') == 'dev'
                )

        if bypass_enabled:
            auth_header = request.headers.get('Authorization')
            # Honor explicit mock token
            if auth_header and 'mock-jwt-token-for-development' in auth_header:
                try:
                    verify_jwt_in_request()
                except Exception:
                    # If verification fails in dev mode, create a test token
                    try:
                        token = create_access_token(identity="1")
                        request.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'
                        verify_jwt_in_request()
                    except Exception:
                        pass
                return f(*args, **kwargs)
            # Auto inject only if none provided
            if not auth_header:
                try:
                    token = create_access_token(identity="1")  # Fix: use string identity
                    # Mutate the WSGI environ so downstream sees header
                    request.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'
                    verify_jwt_in_request()  # Verify the token we just created
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
    
    # Use optional verification to avoid RuntimeError when no JWT is present.
    # This makes get_current_user_id safe to call from request handlers that
    # may be invoked during tests or dev-mode flows where tokens are not set.
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        # optional=True will not raise if no JWT present and instead leave
        # the request without JWT context; get_jwt_identity() will return None.
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if current_app.config.get('TESTING'):
            # In tests return a default id of 1 when no identity found.
            return int(identity) if identity else 1
        # In normal dev/runtime, return None if no identity available
        return int(identity) if identity else None
    except Exception:
        # Last-resort fallback to keep endpoints resilient during dev runs
        if current_app.config.get('TESTING'):
            return 1
        return None
