from flask import request, jsonify, current_app
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
import datetime
from db.database import get_db_session
from models.db_models import User
from werkzeug.security import check_password_hash

# Role-based access decorator
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            
            # Get user claims from JWT
            claims = get_jwt()
            if 'role' not in claims or claims['role'] not in roles:
                return jsonify({'message': 'Unauthorized access'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# User authentication functions
def authenticate_user(email, password):
    """Authenticate a user by email and password"""
    session = get_db_session()
    try:
        user = session.query(User).filter_by(email=email).first()
        
        if not user:
            return None
            
        if not check_password_hash(user.password_hash, password):
            return None
            
        return user
    finally:
        session.close()
