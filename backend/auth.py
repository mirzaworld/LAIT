from flask import request, jsonify, current_app
from functools import wraps
import jwt
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import datetime
from backend.db.database import get_db_session
from backend.models.db_models import User
from werkzeug.security import check_password_hash

# JWT Authentication is now handled by Flask-JWT-Extended
# This is kept as a comment for reference of the migration
# The @jwt_required() decorator from flask_jwt_extended is used instead

# Role-based access decorator
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user_id from JWT
            user_id = get_jwt_identity()
            
            # Get current user
            session = get_db_session()
            current_user = session.query(User).filter_by(id=user_id).first()
            session.close()
            
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
                
            if not current_user.role in roles:
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

def generate_token(user_id, role, expiration=24):
    """Generate a new JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiration),
        'iat': datetime.datetime.utcnow()
    }
    
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def refresh_token(token):
    """Refresh an existing token"""
    try:
        # Decode token
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        
        # Generate a new token
        new_token = generate_token(data['user_id'], data['role'])
        
        return new_token
    except:
        return None
