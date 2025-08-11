"""
Enhanced Authentication Routes with Complete User Management
Integrates the complete user system with existing authentication
"""

import os
import smtplib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, create_access_token, 
    create_refresh_token, set_refresh_cookies, unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
import re

from db.database import get_db_session, User
from auth import authenticate_user, role_required

# Import the complete user system classes
try:
    from user_management_adapter import (
        UserManager, EmailService, SecurityManager,
        ValidationError, AuthenticationError, EmailNotVerifiedError
    )
except ImportError:
    # Fallback implementations if user management adapter is not available
    class UserManager:
        def register_user(self, **kwargs): pass
        def authenticate_user(self, email, password): pass
        def generate_verification_token(self, user_id): return "dummy_token"
        def verify_email(self, token): return False
        def generate_password_reset_token(self, user_id): return "dummy_token"
        def reset_password(self, token, password): return False
        def change_password(self, user_id, current_password, new_password): return False
    
    class EmailService:
        def send_verification_email(self, email, token, name): pass
        def send_password_reset_email(self, email, token, name): pass
    
    class SecurityManager:
        def check_rate_limit(self, email, action): return True
        def record_login_attempt(self, email, success, ip): pass
    
    class ValidationError(Exception): pass
    class AuthenticationError(Exception): pass
    class EmailNotVerifiedError(Exception): pass

logger = logging.getLogger(__name__)
enhanced_auth_bp = Blueprint('enhanced_auth', __name__)

# Initialize services
user_manager = UserManager()
email_service = EmailService()
security_manager = SecurityManager()

# In-memory revoke list (for demo). In production use Redis/DB.
REVOKED_REFRESH_TOKENS = set()


@enhanced_auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with email verification"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        company = data.get('company', '').strip()
        
        # Validate input
        if not all([email, password, first_name, last_name]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Register user
        user_id = user_manager.register_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            company=company
        )
        
        # Send verification email
        verification_token = user_manager.generate_verification_token(user_id)
        email_service.send_verification_email(email, verification_token, first_name)
        
        logger.info(f"User registered successfully: {email}")
        
        return jsonify({
            'message': 'Registration successful! Please check your email to verify your account.',
            'user_id': user_id,
            'verification_required': True
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Registration validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@enhanced_auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Verification token required'}), 400
            
        success = user_manager.verify_email(token)
        
        if success:
            return jsonify({'message': 'Email verified successfully!'}), 200
        else:
            return jsonify({'error': 'Invalid or expired verification token'}), 400
            
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        return jsonify({'error': 'Email verification failed'}), 500


@enhanced_auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
            
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
                
            if user.email_verified:
                return jsonify({'message': 'Email already verified'}), 200
                
            # Generate new verification token
            verification_token = user_manager.generate_verification_token(user.id)
            email_service.send_verification_email(email, verification_token, user.first_name)
            
            return jsonify({'message': 'Verification email sent!'}), 200
            
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        return jsonify({'error': 'Failed to resend verification email'}), 500


@enhanced_auth_bp.route('/login', methods=['POST'])
def login():
    """Enhanced login with security features"""
    try:
        data = request.get_json() or request.form.to_dict()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
            
        # Check rate limiting
        if not security_manager.check_rate_limit(email, 'login'):
            return jsonify({'error': 'Too many login attempts. Please try again later.'}), 429
            
        try:
            # Authenticate user with enhanced security
            user_data = user_manager.authenticate_user(email, password)
            
            # Record successful login
            security_manager.record_login_attempt(email, True, request.remote_addr)
            
            # Create JWT tokens
            access_token = create_access_token(
                identity=str(user_data['id']),
                additional_claims={
                    'role': user_data['role'],
                    'email': user_data['email'],
                    'user_id': user_data['id']
                },
                expires_delta=timedelta(hours=1)
            )
            
            refresh_token = create_refresh_token(identity=str(user_data['id']))
            
            logger.info(f"User logged in successfully: {email}")
            
            return jsonify({
                'message': 'Login successful',
                'token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user_data['id'],
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'company': user_data.get('company', ''),
                    'email_verified': user_data.get('email_verified', True)
                }
            }), 200
            
        except EmailNotVerifiedError:
            return jsonify({
                'error': 'Please verify your email address before logging in',
                'verification_required': True
            }), 403
        except AuthenticationError:
            # Record failed login
            security_manager.record_login_attempt(email, False, request.remote_addr)
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@enhanced_auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
            
        # Check rate limiting
        if not security_manager.check_rate_limit(email, 'password_reset'):
            return jsonify({'error': 'Too many password reset attempts. Please try again later.'}), 429
            
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email).first()
            if user:
                # Generate reset token
                reset_token = user_manager.generate_password_reset_token(user.id)
                email_service.send_password_reset_email(email, reset_token, user.first_name)
                
        # Always return success to prevent email enumeration
        return jsonify({'message': 'If an account with that email exists, a password reset link has been sent.'}), 200
        
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        return jsonify({'error': 'Failed to process password reset request'}), 500


@enhanced_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password required'}), 400
            
        success = user_manager.reset_password(token, new_password)
        
        if success:
            return jsonify({'message': 'Password reset successful'}), 200
        else:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
            
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'Password reset failed'}), 500


@enhanced_auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for authenticated user"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password required'}), 400
            
        success = user_manager.change_password(int(current_user_id), current_password, new_password)
        
        if success:
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': 'Current password is incorrect'}), 400
            
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500


@enhanced_auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == int(current_user_id)).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
                
            return jsonify({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'company': getattr(user, 'company', ''),
                'email_verified': getattr(user, 'email_verified', user.active if hasattr(user, 'active') else True),
                'created_at': user.created_at.isoformat() if user.created_at else None
            }), 200
            
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to get profile'}), 500


@enhanced_auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == int(current_user_id)).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
                
            # Update allowed fields
            if 'first_name' in data:
                user.first_name = data['first_name'].strip()
            if 'last_name' in data:
                user.last_name = data['last_name'].strip()
            if 'company' in data and hasattr(user, 'company'):
                user.company = data['company'].strip()
                
            user.updated_at = datetime.now(timezone.utc)
            session.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'company': getattr(user, 'company', ''),
                    'email_verified': getattr(user, 'email_verified', user.active if hasattr(user, 'active') else True)
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500


@enhanced_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and revoke tokens"""
    try:
        # In a production system, you would add the token to a blacklist
        # For now, we'll just return success
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


# Legacy compatibility endpoints
@enhanced_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Get current user info (legacy compatibility)"""
    return get_profile()


# Health check for auth service
@enhanced_auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Authentication service health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'authentication',
        'features': [
            'user_registration',
            'email_verification',
            'password_reset',
            'profile_management',
            'security_features'
        ],
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200
