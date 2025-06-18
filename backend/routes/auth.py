from flask import Blueprint, request, jsonify
from db.database import get_db_session, User
from werkzeug.security import generate_password_hash, check_password_hash
from auth import generate_token, authenticate_user, jwt_required, role_required
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    user = authenticate_user(email, password)
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
        
    token = generate_token(user.id, user.role)
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }
    })
    
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing required fields'}), 400

    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    role = data.get('role', 'user')
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Invalid email format'}), 400
        
    # Check password strength
    if len(password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters'}), 400
    
    session = get_db_session()
    try:
        # Check if user already exists
        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409
        
        # Create new user
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=role  # Note: In production, this should validate role or restrict to 'user' only
        )
        
        session.add(new_user)
        session.commit()
        
        # Generate token for immediate login
        token = generate_token(new_user.id, new_user.role)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        session.rollback()
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500
    finally:
        session.close()

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required
def refresh(current_user):
    """Refresh JWT token"""
    token = generate_token(current_user.id, current_user.role)
    
    return jsonify({
        'token': token,
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'role': current_user.role
        }
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_user(current_user):
    """Get current user information"""
    return jsonify({
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'role': current_user.role
        }
    })

@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required
@role_required(['admin'])
def get_all_users(current_user):
    """Admin only: Get all users"""
    session = get_db_session()
    try:
        users = session.query(User).all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'active': user.active,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({'users': users_data})
    finally:
        session.close()

@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required
@role_required(['admin'])
def update_user(current_user, user_id):
    """Admin only: Update user information"""
    data = request.json
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
        
    session = get_db_session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        # Update user fields
        if 'email' in data:
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'role' in data:
            user.role = data['role']
        if 'active' in data:
            user.active = data['active']
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
            
        session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'active': user.active
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({'message': f'Error updating user: {str(e)}'}), 500
    finally:
        session.close()

@auth_bp.route('/password', methods=['PUT'])
@jwt_required
def change_password(current_user):
    """Change user's password"""
    data = request.json
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({'message': 'Missing current or new password'}), 400
        
    current_password = data['current_password']
    new_password = data['new_password']
    
    # Check current password
    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({'message': 'Current password is incorrect'}), 401
        
    # Validate new password
    if len(new_password) < 8:
        return jsonify({'message': 'New password must be at least 8 characters'}), 400
        
    session = get_db_session()
    try:
        user = session.query(User).filter_by(id=current_user.id).first()
        user.password_hash = generate_password_hash(new_password)
        session.commit()
        
        return jsonify({'message': 'Password changed successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'message': f'Error changing password: {str(e)}'}), 500
    finally:
        session.close()
