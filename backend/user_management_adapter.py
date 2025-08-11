"""
User Management Adapter
Provides the interface needed for the enhanced authentication system
"""

import logging
from datetime import datetime, timedelta, timezone
from werkzeug.security import check_password_hash
from db.database import get_db_session, User

logger = logging.getLogger(__name__)

# Custom exception classes
class ValidationError(Exception):
    """Raised when validation fails"""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class EmailNotVerifiedError(Exception):
    """Raised when email is not verified"""
    pass


class UserManager:
    """User management operations"""
    
    def __init__(self):
        from complete_user_system import CompleteUserSystem
        self.user_system = CompleteUserSystem(None)  # App will be set later
    
    def register_user(self, email, password, first_name, last_name, company=None):
        """Register a new user"""
        registration_data = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'company': company or ''
        }
        
        result = self.user_system.register_user(registration_data)
        
        if not result.get('success'):
            raise ValidationError(result.get('error', 'Registration failed'))
        
        return result['user']['id']
    
    def authenticate_user(self, email, password):
        """Authenticate user and return user data"""
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email.lower()).first()
            
            if not user:
                raise AuthenticationError('Invalid credentials')
            
            if not check_password_hash(user.password_hash, password):
                raise AuthenticationError('Invalid credentials')
            
            # Check if email is verified (if applicable)
            if hasattr(user, 'active') and not user.active:
                raise EmailNotVerifiedError('Email not verified')
            
            # Check if account is locked
            if hasattr(user, 'failed_login_attempts') and user.failed_login_attempts >= 5:
                raise AuthenticationError('Account temporarily locked due to too many failed attempts')
            
            return {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'company': getattr(user, 'company', ''),
                'email_verified': getattr(user, 'active', True)
            }
    
    def generate_verification_token(self, user_id):
        """Generate email verification token"""
        import secrets
        token = secrets.token_urlsafe(32)
        
        # Store token in database
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.verification_token = token
                session.commit()
        
        return token
    
    def verify_email(self, token):
        """Verify email using token"""
        result = self.user_system.verify_email(token)
        return result.get('success', False)
    
    def generate_password_reset_token(self, user_id):
        """Generate password reset token"""
        import secrets
        token = secrets.token_urlsafe(32)
        
        # Store token in database with expiration
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.password_reset_token = token
                user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
                session.commit()
        
        return token
    
    def reset_password(self, token, new_password):
        """Reset password using token"""
        result = self.user_system.reset_password(token, new_password)
        return result.get('success', False)
    
    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            if not check_password_hash(user.password_hash, current_password):
                return False
            
            # Validate new password
            if len(new_password) < 8:
                raise ValidationError('Password must be at least 8 characters long')
            
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(new_password)
            user.updated_at = datetime.now(timezone.utc)
            session.commit()
            
            return True


class EmailService:
    """Email service operations"""
    
    def __init__(self):
        from complete_user_system import CompleteUserSystem
        self.user_system = CompleteUserSystem(None)
    
    def send_verification_email(self, email, token, first_name):
        """Send verification email"""
        return self.user_system.send_verification_email(email, first_name, token)
    
    def send_password_reset_email(self, email, token, first_name):
        """Send password reset email"""
        return self.user_system.send_password_reset_email(email, first_name, token)


class SecurityManager:
    """Security operations like rate limiting"""
    
    def __init__(self):
        # Simple in-memory rate limiting (use Redis in production)
        self.rate_limits = {}
    
    def check_rate_limit(self, identifier, action_type, max_attempts=5, time_window=300):
        """Check if action is rate limited"""
        key = f"{identifier}:{action_type}"
        now = datetime.now()
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Remove old attempts outside time window
        cutoff = now - timedelta(seconds=time_window)
        self.rate_limits[key] = [
            attempt for attempt in self.rate_limits[key] 
            if attempt > cutoff
        ]
        
        # Check if under limit
        return len(self.rate_limits[key]) < max_attempts
    
    def record_login_attempt(self, email, success, ip_address):
        """Record login attempt"""
        if not success:
            # Record failed attempt for rate limiting
            key = f"{email}:login"
            now = datetime.now()
            
            if key not in self.rate_limits:
                self.rate_limits[key] = []
            
            self.rate_limits[key].append(now)
            
            # Also increment database counter if user exists
            with get_db_session() as session:
                user = session.query(User).filter(User.email == email.lower()).first()
                if user and hasattr(user, 'failed_login_attempts'):
                    user.failed_login_attempts = getattr(user, 'failed_login_attempts', 0) + 1
                    session.commit()
        else:
            # Reset failed attempts on successful login
            with get_db_session() as session:
                user = session.query(User).filter(User.email == email.lower()).first()
                if user and hasattr(user, 'failed_login_attempts'):
                    user.failed_login_attempts = 0
                    session.commit()
