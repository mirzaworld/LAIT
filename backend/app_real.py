#!/usr/bin/env python3
"""
LAIT Real Backend - Self-contained Flask application
Port 5003 with JWT auth, bcrypt, SQLAlchemy, PDF parsing
"""

import os
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import bcrypt
import jwt
import pdfplumber
from flask import Flask, request, jsonify, g, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
from io import BytesIO, StringIO
import csv
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields, validate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import pandas (only needed for ML)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  pandas not available - ML features will be limited")
    PANDAS_AVAILABLE = False

# Import ML service
try:
    from services.ml_service import score_lines as ml_score_lines, get_model_status
    ML_SERVICE_AVAILABLE = True
    logger.info("✅ ML service imported successfully")
except ImportError as e:
    logger.warning(f"⚠️  ML service not available: {e}")
    ML_SERVICE_AVAILABLE = False

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'lait-dev-secret-key-2025')

# Database configuration - prefer Postgres, fallback to SQLite
database_url = os.getenv('DATABASE_URL', 'sqlite:///lait.db')
if database_url.startswith('postgres://'):
    # Fix for Heroku Postgres URLs
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Enhanced CORS configuration - restrict to configured frontend origins
FRONTEND_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
logger.info(f"🔒 CORS enabled for origins: {FRONTEND_ORIGINS}")

# Rate limiting setup with enhanced user-based limiting
def get_user_id_for_rate_limit():
    """Extract user ID from JWT token for rate limiting"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return get_remote_address()
    
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return f"user_{payload['user_id']}"
    except Exception as e:
        # Log security events but don't expose details
        logger.warning(f"🔒 Rate limit token validation failed for {get_remote_address()}")
        return get_remote_address()

# Initialize limiter with Redis support if available
redis_url = os.getenv('REDIS_URL', os.getenv('RATE_LIMIT_STORAGE_URL', 'memory://'))
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per hour"],
    storage_uri=redis_url
)

# Enhanced CORS configuration with environment-based origins
CORS(app, 
     origins=FRONTEND_ORIGINS,
     resources={r"/api/*": {"origins": FRONTEND_ORIGINS}},
     supports_credentials=True)

# Database setup
db = SQLAlchemy(app)

# ============================================================================
# API DOCUMENTATION SETUP
# ============================================================================

# OpenAPI specification configuration
spec = APISpec(
    title="LAIT Legal Intelligence Platform API",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="""
        **LAIT (Legal AI Team) Platform API**
        
        A comprehensive legal intelligence platform for invoice processing, vendor management, 
        and legal spend optimization. This API provides endpoints for user authentication, 
        invoice upload and processing, dashboard metrics, and vendor analytics.
        
        ## Authentication
        All protected endpoints require a Bearer token in the Authorization header:
        ```
        Authorization: Bearer <your_jwt_token>
        ```
        
        ## Rate Limits
        - General API: 200 requests per hour
        - Login: 5 attempts per minute
        - Upload: 30 per minute per user, 5 per minute per token
        - Token refresh: 10 per minute
        
        ## File Upload Support
        Supported formats: PDF, TXT, CSV (max 10MB)
        """,
        contact=dict(name="LAIT Development Team", email="dev@lait.ai"),
        license=dict(name="MIT License")
    ),
    servers=[
        {"url": "http://localhost:5003", "description": "Development server"},
        {"url": "https://lait-api.onrender.com", "description": "Production server"}
    ],
    plugins=[MarshmallowPlugin(), FlaskPlugin()],
)

# Security scheme for JWT
jwt_security_scheme = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT",
    "description": "JWT token obtained from /api/auth/login or /api/auth/register"
}
spec.components.security_scheme("jwt", jwt_security_scheme)

# ============================================================================
# MARSHMALLOW SCHEMAS FOR API DOCUMENTATION
# ============================================================================

class UserSchema(Schema):
    """User model schema"""
    id = fields.Int(dump_only=True, description="User ID")
    email = fields.Email(required=True, description="User email address")
    first_name = fields.Str(description="User first name")
    last_name = fields.Str(description="User last name") 
    company = fields.Str(description="User company name")
    created_at = fields.DateTime(dump_only=True, description="Account creation timestamp")

class LoginSchema(Schema):
    """Login request schema"""
    email = fields.Email(required=True, description="User email address")
    password = fields.Str(required=True, validate=validate.Length(min=6), description="User password (min 6 characters)")

class RegisterSchema(Schema):
    """User registration schema"""
    email = fields.Email(required=True, description="User email address")
    password = fields.Str(required=True, validate=validate.Length(min=6), description="Password (min 6 characters)")
    first_name = fields.Str(description="First name")
    last_name = fields.Str(description="Last name")
    company = fields.Str(description="Company name")

class TokenResponseSchema(Schema):
    """Token response schema"""
    access_token = fields.Str(required=True, description="Short-lived access token (15 minutes)")
    refresh_token = fields.Str(required=True, description="Long-lived refresh token (7 days)")
    expires_in = fields.Int(required=True, description="Access token expiry in seconds")
    message = fields.Str(description="Success message")
    user = fields.Nested(UserSchema, description="User information")

class RefreshTokenSchema(Schema):
    """Token refresh request schema"""
    refresh_token = fields.Str(required=True, description="Valid refresh token")

class InvoiceSchema(Schema):
    """Invoice model schema"""
    id = fields.Int(dump_only=True, description="Invoice ID")
    filename = fields.Str(description="Original filename")
    vendor = fields.Str(description="Vendor/supplier name")
    amount = fields.Float(description="Total invoice amount")
    date_processed = fields.DateTime(dump_only=True, description="Processing timestamp")
    line_items_count = fields.Int(description="Number of line items")
    total_score = fields.Float(description="AI risk/relevance score")
    user_id = fields.Int(dump_only=True, description="Owner user ID")

class InvoiceUploadSchema(Schema):
    """Invoice upload response schema"""
    message = fields.Str(description="Upload success message")
    invoice_id = fields.Int(description="Created invoice ID")
    filename = fields.Str(description="Processed filename")
    line_items_processed = fields.Int(description="Number of line items processed")
    total_amount = fields.Float(description="Total amount extracted")

class DashboardMetricsSchema(Schema):
    """Dashboard metrics schema"""
    invoices_count = fields.Int(description="Total number of invoices")
    total_spend = fields.Float(description="Total spending amount")
    vendors_count = fields.Int(description="Number of unique vendors")
    avg_invoice_amount = fields.Float(description="Average invoice amount")
    recent_activity = fields.List(fields.Dict(), description="Recent activity feed")

class ErrorResponseSchema(Schema):
    """Error response schema"""
    error = fields.Str(required=True, description="Error message")
    hint = fields.Str(description="Helpful hint for resolution")
    code = fields.Int(description="Internal error code")

# Register schemas with APISpec
spec.components.schema("User", schema=UserSchema)
spec.components.schema("Login", schema=LoginSchema)
spec.components.schema("Register", schema=RegisterSchema)
spec.components.schema("TokenResponse", schema=TokenResponseSchema)
spec.components.schema("RefreshToken", schema=RefreshTokenSchema)
spec.components.schema("Invoice", schema=InvoiceSchema)
spec.components.schema("InvoiceUpload", schema=InvoiceUploadSchema)
spec.components.schema("DashboardMetrics", schema=DashboardMetricsSchema)
spec.components.schema("ErrorResponse", schema=ErrorResponseSchema)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password: str):
        """Hash and set password using bcrypt"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    invoice_number = db.Column(db.String(100))
    date = db.Column(db.Date)
    total_amount = db.Column(db.Float, default=0.0)
    lines_processed = db.Column(db.Integer, default=0)
    flagged_lines = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='processed')
    filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='invoices')
    vendor = db.relationship('Vendor', backref='invoices')
    lines = db.relationship('InvoiceLine', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')

class InvoiceLine(db.Model):
    __tablename__ = 'invoice_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    description = db.Column(db.String(500))
    hours = db.Column(db.Float)
    rate = db.Column(db.Float)
    line_total = db.Column(db.Float)
    anomaly_score = db.Column(db.Float)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================================
# AUTHENTICATION HELPERS
# ============================================================================

def generate_jwt_token(user_id: int) -> str:
    """Generate legacy JWT token for backward compatibility"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
        'type': 'legacy'
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def create_token_pair(user_id: int) -> Dict[str, str]:
    """Create access and refresh token pair for enhanced security"""
    now = datetime.utcnow()
    
    # Short-lived access token (15 minutes)
    access_payload = {
        'user_id': user_id,
        'exp': now + timedelta(minutes=15),
        'iat': now,
        'type': 'access'
    }
    access_token = jwt.encode(access_payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    # Longer-lived refresh token (7 days)  
    refresh_payload = {
        'user_id': user_id,
        'exp': now + timedelta(days=7),
        'iat': now,
        'type': 'refresh'
    }
    refresh_token = jwt.encode(refresh_payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': 900  # 15 minutes in seconds
    }

def decode_jwt_token(token: str) -> Optional[Dict]:
    """Decode and validate JWT token with enhanced error logging"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("🔒 Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"🔒 Invalid token: {type(e).__name__}")
        return None

# ============================================================================
# ERROR HANDLING & LOGGING HELPERS  
# ============================================================================

def log_request():
    """Enhanced request logging with sensitive data masking"""
    if hasattr(request, 'user_id'):
        user_info = f"user_{request.user_id}"
    elif hasattr(g, 'current_user') and g.current_user:
        user_info = f"user_{g.current_user.id}"
    else:
        user_info = "anonymous"
    
    # Mask sensitive request data
    safe_data = {}
    if request.is_json and request.json:
        safe_data = mask_sensitive_data(request.json)
    
    logger.info(f"📝 {request.method} {request.path} - {user_info} - IP:{get_remote_address()} - Data: {safe_data}")

def create_error_response(error: str, hint: str = None, code: int = 400, status_code: int = None):
    """Create consistent JSON error response"""
    if status_code is None:
        status_code = code
    
    response_data = {
        "error": error,
        "code": code
    }
    
    if hint:
        response_data["hint"] = hint
        
    return jsonify(response_data), status_code

def mask_sensitive_data(data):
    """Mask sensitive information in logs and responses"""
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in ['password', 'token', 'secret', 'key', 'auth', 'authorization']:
                masked[key] = '***MASKED***'
            elif key.lower() == 'email' and isinstance(value, str):
                # Mask email but keep domain visible
                if '@' in value:
                    local, domain = value.split('@', 1)
                    masked[key] = f"{local[:2]}***@{domain}"
                else:
                    masked[key] = '***MASKED***'
            elif isinstance(value, (dict, list)):
                masked[key] = mask_sensitive_data(value)
            else:
                masked[key] = value
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data

def validate_file_upload(file):
    """Enhanced file validation with magic number checking and size limits"""
    if not file or not file.filename:
        return create_error_response(
            "No file provided", 
            "Please select a file to upload", 
            code=1001,
            status_code=400
        )
    
    # Read file content for magic number validation
    file_content = file.read()
    file.seek(0)  # Reset file pointer
    
    # Check file size (enforce 10MB limit)
    file_size = len(file_content)
    if file_size > 10 * 1024 * 1024:
        return create_error_response(
            "File too large", 
            f"File size {file_size / (1024*1024):.1f}MB exceeds 10MB limit", 
            code=1002,
            status_code=413
        )
    
    # Check file extension
    filename = secure_filename(file.filename.lower())
    allowed_extensions = {'.pdf', '.txt', '.csv'}
    file_ext = None
    
    for ext in allowed_extensions:
        if filename.endswith(ext):
            file_ext = ext
            break
    
    if not file_ext:
        return create_error_response(
            "Invalid file type", 
            "Only PDF, TXT, and CSV files are allowed", 
            code=1003,
            status_code=415
        )
    
    # Enhanced magic number validation
    if file_size > 0:
        magic_bytes = file_content[:16]  # First 16 bytes for magic detection
        
        if file_ext == '.pdf':
            # PDF files should start with %PDF
            if not magic_bytes.startswith(b'%PDF'):
                return create_error_response(
                    "Invalid PDF file",
                    "File extension is .pdf but content is not a valid PDF",
                    code=1004,
                    status_code=415
                )
        elif file_ext == '.csv':
            # CSV files should be text-based - check for binary content
            try:
                # Try to decode as UTF-8 text
                sample_text = file_content[:1024].decode('utf-8')
                # Check for common CSV patterns
                if not any(char in sample_text for char in [',', ';', '\t', '\n']):
                    return create_error_response(
                        "Invalid CSV file",
                        "File does not appear to contain comma-separated values",
                        code=1005,
                        status_code=415
                    )
            except UnicodeDecodeError:
                return create_error_response(
                    "Invalid CSV file",
                    "File contains binary data but has .csv extension",
                    code=1006,
                    status_code=415
                )
        elif file_ext == '.txt':
            # Text files should be decodable as UTF-8
            try:
                file_content.decode('utf-8')
            except UnicodeDecodeError:
                return create_error_response(
                    "Invalid text file",
                    "File contains binary data but has .txt extension",
                    code=1007,
                    status_code=415
                )
    
    return None  # No error

def jwt_required(f):
    """Enhanced decorator to require JWT authentication with security logging"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning(f"🔒 Missing auth header from {get_remote_address()}")
            return create_error_response('Missing or invalid authorization header', 
                                       'Include "Authorization: Bearer <token>" header',
                                       code=2001, status_code=401)
        
        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)
        if not payload:
            logger.warning(f"🔒 Invalid token attempt from {get_remote_address()}")
            return create_error_response('Invalid or expired token',
                                       'Please login again to get a new token',
                                       code=2002, status_code=401)
        
        # Add user_id to request context and g for logging
        request.user_id = payload['user_id']
        g.current_user = User.query.get(payload['user_id'])
        
        # Log the request with masked user info
        log_request()
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_current_user() -> Optional[User]:
    """Get current authenticated user"""
    if not hasattr(request, 'user_id'):
        return None
    return User.query.get(request.user_id)

# ============================================================================
# FILE PARSING UTILITIES
# ============================================================================

def parse_pdf_content(file_content: bytes) -> List[Dict[str, Any]]:
    """Parse PDF content using pdfplumber to extract line items"""
    lines = []
    
    try:
        with pdfplumber.open(BytesIO(file_content)) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            # Simple parsing logic - look for patterns that might be line items
            text_lines = full_text.split('\n')
            
            for line in text_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to extract hours, rate, and description from common patterns
                # Pattern 1: "Description 10.5 hours @ $450/hr = $4,725"
                # Pattern 2: "Legal research, 5.0, 500.00, 2500.00"
                # Pattern 3: Simple comma-separated values
                
                # Basic parsing - split by common separators and look for numbers
                parts = line.replace(',', '').replace('$', '').split()
                numbers = []
                description_parts = []
                
                for part in parts:
                    try:
                        num = float(part)
                        numbers.append(num)
                    except ValueError:
                        description_parts.append(part)
                
                # If we found numbers, try to map them to hours, rate, total
                if len(numbers) >= 2:
                    description = ' '.join(description_parts) or f"Line item from {line[:50]}"
                    
                    if len(numbers) >= 3:
                        # Assume: hours, rate, total
                        hours, rate, total = numbers[0], numbers[1], numbers[2]
                    else:
                        # Assume: hours, rate (calculate total)
                        hours, rate = numbers[0], numbers[1]
                        total = hours * rate
                    
                    # Only add if values seem reasonable
                    if 0.1 <= hours <= 100 and 50 <= rate <= 2000:
                        lines.append({
                            'description': description,
                            'hours': hours,
                            'rate': rate,
                            'line_total': total
                        })
            
            # If no structured data found, create a single line item from filename
            if not lines:
                lines.append({
                    'description': 'PDF Invoice Processing',
                    'hours': 1.0,
                    'rate': 500.0,
                    'line_total': 500.0
                })
                
    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        # Fallback line item
        lines.append({
            'description': 'PDF Processing Error - Manual Review Required',
            'hours': 1.0,
            'rate': 250.0,
            'line_total': 250.0
        })
    
    return lines

def parse_text_content(content: str) -> List[Dict[str, Any]]:
    """Parse plain text content to extract line items"""
    lines = []
    text_lines = content.split('\n')
    
    for line in text_lines:
        line = line.strip()
        if not line:
            continue
        
        # Try CSV format first
        try:
            reader = csv.reader([line])
            row = next(reader)
            if len(row) >= 3:
                description = row[0].strip()
                hours = float(row[1].strip())
                rate = float(row[2].strip())
                line_total = hours * rate
                
                if len(row) >= 4:
                    try:
                        line_total = float(row[3].strip())
                    except ValueError:
                        pass
                
                lines.append({
                    'description': description,
                    'hours': hours,
                    'rate': rate,
                    'line_total': line_total
                })
                continue
        except (ValueError, csv.Error):
            pass
        
        # Try to parse free-form text
        parts = line.replace(',', '').replace('$', '').split()
        numbers = []
        description_parts = []
        
        for part in parts:
            try:
                num = float(part)
                numbers.append(num)
            except ValueError:
                description_parts.append(part)
        
        if len(numbers) >= 2:
            description = ' '.join(description_parts) or f"Text line: {line[:30]}"
            
            if len(numbers) >= 3:
                hours, rate, total = numbers[0], numbers[1], numbers[2]
            else:
                hours, rate = numbers[0], numbers[1]
                total = hours * rate
            
            if 0.1 <= hours <= 100 and 50 <= rate <= 2000:
                lines.append({
                    'description': description,
                    'hours': hours,
                    'rate': rate,
                    'line_total': total
                })
    
    # If no structured data found, create a default line item
    if not lines:
        lines.append({
            'description': 'Text file processing - Manual review required',
            'hours': 1.0,
            'rate': 300.0,
            'line_total': 300.0
        })
    
    return lines

def score_invoice_lines(lines_data: List[Dict]) -> tuple[List[Dict], Dict[str, Any]]:
    """
    Score invoice lines using ML service with fallback to deterministic scoring
    
    Args:
        lines_data: List of dictionaries containing line item data
        
    Returns:
        Tuple of (scored_lines_data, scoring_metadata)
    """
    if not lines_data:
        return [], {"method": "no_data", "note": "No lines to score"}
    
    try:
        if ML_SERVICE_AVAILABLE:
            if PANDAS_AVAILABLE:
                # Convert to DataFrame for ML service
                df = pd.DataFrame(lines_data)
                
                # Use ML service - now returns DataFrame directly
                scored_df = ml_score_lines(df)
                
                # Convert back to list of dicts and merge with original data
                for i, (_, row) in enumerate(scored_df.iterrows()):
                    if i < len(lines_data):
                        lines_data[i]['anomaly_score'] = float(row['anomaly_score'])
                        lines_data[i]['is_flagged'] = bool(row['is_flagged'])
                        lines_data[i]['flag_reason'] = "ML scoring applied" if not row['is_flagged'] else "ML detected anomaly"
            else:
                # ML service available but pandas is not - use fallback mode
                scored_data = ml_score_lines(lines_data)  # This will use fallback mode
                
                # Merge scored data back to original
                for i, scored_item in enumerate(scored_data):
                    if i < len(lines_data):
                        lines_data[i]['anomaly_score'] = scored_item['anomaly_score']
                        lines_data[i]['is_flagged'] = scored_item['is_flagged']
                        lines_data[i]['flag_reason'] = "ML fallback applied" if not scored_item['is_flagged'] else "ML fallback detected anomaly"
            
            metadata = {
                "method": "ml",
                "note": "ML service used successfully",
                "pandas_available": PANDAS_AVAILABLE,
                "lines_scored": len(lines_data)
            }
            
            logger.info(f"ML scoring completed: {len(lines_data)} lines scored")
            return lines_data, metadata
        
        else:
            # Fallback to deterministic scoring
            reason = "ML service not available"
            if ML_SERVICE_AVAILABLE and not PANDAS_AVAILABLE:
                reason = "pandas not available for ML"
            elif not ML_SERVICE_AVAILABLE:
                reason = "ML service import failed"
                
            metadata = {
                "method": "deterministic_fallback",
                "note": "model_fallback",
                "reason": reason,
                "lines_scored": len(lines_data)
            }
            
            for line in lines_data:
                score, is_flagged, flag_reason = calculate_anomaly_score_legacy(
                    float(line.get('billable_hours', 0)),
                    float(line.get('rate', 0)),
                    float(line.get('amount', 0))
                )
                line['anomaly_score'] = score
                line['is_flagged'] = is_flagged
                line['flag_reason'] = flag_reason
            
            logger.info(f"Deterministic fallback scoring completed: {len(lines_data)} lines scored")
            return lines_data, metadata
            
    except Exception as e:
        logger.error(f"Error in score_invoice_lines: {e}")
        # Emergency fallback
        metadata = {
            "method": "emergency_fallback", 
            "note": "model_fallback",
            "error": str(e),
            "lines_scored": len(lines_data)
        }
        
        for line in lines_data:
            line['anomaly_score'] = 0.1
            line['is_flagged'] = False
            line['flag_reason'] = f"Emergency fallback - error in scoring"
        
        return lines_data, metadata

def calculate_anomaly_score_legacy(hours: float, rate: float, line_total: float) -> tuple[float, bool, str]:
    """Legacy deterministic anomaly scoring (renamed from calculate_anomaly_score)"""
    anomaly_score = (rate / 1000) + (hours / 12) + (line_total / 5000)
    
    flag_reasons = []
    if rate > 900:
        flag_reasons.append(f"High rate: ${rate}/hr")
    if hours > 10:
        flag_reasons.append(f"Excessive hours: {hours}")
    if line_total > 3000:
        flag_reasons.append(f"High line total: ${line_total}")
    
    is_flagged = bool(flag_reasons)
    flag_reason = "; ".join(flag_reasons) if flag_reasons else "Normal billing pattern"
    
    return anomaly_score, is_flagged, flag_reason

# ============================================================================
# ERROR HANDLERS & MIDDLEWARE  
# ============================================================================

# Rate limit error handler
@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limiting errors with consistent JSON response"""
    return create_error_response(
        "Rate limit exceeded",
        f"Too many requests. Try again in {e.retry_after} seconds",
        code=9001,
        status_code=429
    )

# Update before_request to actually log
@app.before_request
def log_public_requests_updated():
    """Log requests to public endpoints (JWT endpoints handle their own logging)"""
    public_endpoints = ['/api/health', '/api/auth/register', '/api/auth/login']
    if request.path in public_endpoints and not hasattr(g, 'logged'):
        log_request()
        g.logged = True

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint
    ---
    get:
      tags:
        - Health
      summary: API health check
      description: Check if the API is running and responsive
      responses:
        200:
          description: API is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  ok:
                    type: boolean
                    example: true
                  timestamp:
                    type: string
                    format: date-time
                    example: "2025-08-12T15:30:00.123456"
    """
    return jsonify({'ok': True, 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/openapi.json', methods=['GET'])
def get_openapi_spec():
    """Get OpenAPI specification
    ---
    get:
      tags:
        - Documentation
      summary: Get OpenAPI specification
      description: Returns the complete OpenAPI 3.0 specification for this API
      responses:
        200:
          description: OpenAPI specification
          content:
            application/json:
              schema:
                type: object
    """
    # Add all routes to spec
    with app.app_context():
        # Register paths from docstrings
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                view_function = app.view_functions[rule.endpoint]
                if hasattr(view_function, '__doc__') and view_function.__doc__ and '---' in view_function.__doc__:
                    spec.path(path=rule.rule, operations={}, view_function=view_function)
    
    return jsonify(spec.to_dict())

@app.route('/api/docs')
def swagger_ui():
    """Swagger UI documentation interface
    ---
    get:
      tags:
        - Documentation  
      summary: Interactive API documentation
      description: Swagger UI interface for testing API endpoints
      responses:
        200:
          description: HTML page with Swagger UI
          content:
            text/html:
              schema:
                type: string
    """
    swagger_ui_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LAIT API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
            *, *:before, *:after { box-sizing: inherit; }
            body { margin:0; background: #fafafa; }
            .swagger-ui .topbar { display: none; }
            .swagger-ui .info { margin: 20px 0; }
            .swagger-ui .info .title { color: #2c3e50; font-size: 2.5em; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
        <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: '/api/openapi.json',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout",
                    defaultModelsExpandDepth: 1,
                    defaultModelExpandDepth: 1,
                    docExpansion: "list",
                    filter: false,
                    showExtensions: true,
                    showCommonExtensions: true,
                    tryItOutEnabled: true
                });
            };
        </script>
    </body>
    </html>
    '''
    return render_template_string(swagger_ui_html)

@app.route('/api/ml/status', methods=['GET'])
def ml_status():
    """Get ML model status"""
    if ML_SERVICE_AVAILABLE:
        status = get_model_status()
        return jsonify({
            "fallback_mode": status.get('fallback_mode', True),
            "service_available": True
        })
    else:
        return jsonify({
            "fallback_mode": True,
            "service_available": False
        })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user with bcrypt password hashing
    ---
    post:
      tags:
        - Authentication
      summary: Register new user account
      description: Create a new user account with email and password. Returns access and refresh tokens.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Register'
            example:
              email: "user@example.com"
              password: "securepassword123"
              first_name: "John"
              last_name: "Doe"
              company: "Acme Legal"
      responses:
        201:
          description: User registered successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenResponse'
        400:
          description: Invalid request data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        409:
          description: Email already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    """
    try:
        # Log request for non-authenticated endpoint
        log_request()
        
        data = request.get_json()
        if not data:
            return create_error_response('Missing request body',
                                       'Send JSON data with email and password',
                                       code=3101, status_code=400)
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return create_error_response('Email and password are required',
                                       'Both email and password must be provided',
                                       code=3102, status_code=400)
        
        if len(password) < 6:
            return create_error_response('Password must be at least 6 characters',
                                       'Choose a stronger password',
                                       code=3103)
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return create_error_response('User already exists',
                                       'Try logging in or use a different email',
                                       code=3104, status_code=409)
        
        # Create new user
        user = User(
            email=email,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            company=data.get('company', '')
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create token pair for enhanced security
        tokens = create_token_pair(user.id)
        
        # Log successful registration with masked data
        safe_user_data = mask_sensitive_data(user.to_dict())
        logger.info(f"✅ User registered: {safe_user_data['email']} (ID: {user.id})")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            **tokens
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Login user with bcrypt password verification
    ---
    post:
      tags:
        - Authentication
      summary: User login
      description: Authenticate user with email and password. Returns access and refresh tokens.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Login'
            example:
              email: "user@example.com"
              password: "securepassword123"
      responses:
        200:
          description: Login successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenResponse'
        400:
          description: Missing or invalid request data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        401:
          description: Invalid credentials
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        429:
          description: Too many login attempts
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    """
    try:
        # Log request for non-authenticated endpoint
        log_request()
        
        data = request.get_json()
        if not data:
            return create_error_response('Missing request body', 
                                       'Send JSON data with email and password',
                                       code=3001, status_code=400)
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return create_error_response('Email and password are required',
                                       'Both email and password must be provided',
                                       code=3002)
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            # Log failed login attempt with masked email
            masked_email = mask_sensitive_data({'email': email})['email']
            logger.warning(f"🔒 Failed login attempt: {masked_email} from {get_remote_address()}")
            return create_error_response('Invalid credentials',
                                       'Check your email and password',
                                       code=3003, status_code=401)
        
        # Create token pair for enhanced security
        tokens = create_token_pair(user.id)
        
        # Log successful login with masked user data
        safe_user_data = mask_sensitive_data(user.to_dict())
        logger.info(f"✅ User logged in: {safe_user_data['email']} (ID: {user.id})")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            **tokens
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required
def get_current_user_info():
    """Get current user information
    ---
    get:
      tags:
        - Authentication
      summary: Get current user profile
      description: Retrieve the authenticated user's profile information
      security:
        - jwt: []
      responses:
        200:
          description: User profile retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  user:
                    $ref: '#/components/schemas/User'
        401:
          description: Authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        404:
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        return jsonify({'error': 'Failed to get user info'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@limiter.limit("10 per minute")
def refresh_token():
    """Refresh access token using refresh token
    ---
    post:
      tags:
        - Authentication
      summary: Refresh access token
      description: Use a valid refresh token to obtain a new access/refresh token pair
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RefreshToken'
            example:
              refresh_token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      responses:
        200:
          description: Token refreshed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TokenResponse'
        400:
          description: Missing refresh token
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        401:
          description: Invalid or expired refresh token
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        404:
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        429:
          description: Too many refresh attempts
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    """
    try:
        data = request.get_json()
        if not data or 'refresh_token' not in data:
            return create_error_response(
                "Missing refresh token",
                "Include refresh_token in request body",
                code=2101,
                status_code=400
            )
        
        refresh_token = data['refresh_token']
        payload = decode_jwt_token(refresh_token)
        
        if not payload:
            return create_error_response(
                "Invalid refresh token",
                "Refresh token is expired or invalid",
                code=2102,
                status_code=401
            )
        
        if payload.get('type') != 'refresh':
            return create_error_response(
                "Invalid token type",
                "Expected refresh token",
                code=2103,
                status_code=401
            )
        
        user = User.query.get(payload['user_id'])
        if not user:
            return create_error_response(
                "User not found",
                "User associated with token no longer exists",
                code=2104,
                status_code=404
            )
        
        # Create new token pair
        tokens = create_token_pair(user.id)
        
        logger.info(f"🔄 Token refresh successful for user {user.id}")
        
        return jsonify({
            'message': 'Token refreshed successfully',
            **tokens
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return create_error_response(
            "Token refresh failed",
            "Internal server error during token refresh",
            code=2105,
            status_code=500
        )

@app.route('/api/invoices/upload', methods=['POST'])
@limiter.limit("30 per minute", key_func=get_user_id_for_rate_limit)
@limiter.limit("5 per minute", key_func=lambda: request.headers.get('Authorization', '').replace('Bearer ', '')[:20])
@jwt_required
def upload_invoice():
    """Enhanced upload with per-token rate limiting and strict validation
    ---
    post:
      tags:
        - Invoices
      summary: Upload and process invoice
      description: |
        Upload an invoice file (PDF, TXT, CSV) or JSON data for processing. 
        The system will extract line items, vendor information, and calculate risk scores.
        
        **File Upload**: Send as multipart/form-data with 'file' field  
        **JSON Upload**: Send structured invoice data as application/json
        
        **Rate Limits**: 30 per minute per user, 5 per minute per token
      security:
        - jwt: []
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                  description: Invoice file (PDF, TXT, CSV, max 10MB)
                vendor:
                  type: string
                  description: Override vendor name (optional)
            example:
              vendor: "Acme Legal Services"
          application/json:
            schema:
              type: object
              properties:
                vendor:
                  type: string
                  description: Vendor name
                  example: "Legal Associates LLC"
                amount:
                  type: number
                  description: Total amount
                  example: 2500.00
                line_items:
                  type: array
                  items:
                    type: object
                    properties:
                      description:
                        type: string
                        example: "Legal research services"
                      amount:
                        type: number
                        example: 500.00
                      rate:
                        type: number
                        example: 350.00
                      hours:
                        type: number
                        example: 1.43
      responses:
        200:
          description: Invoice uploaded and processed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InvoiceUpload'
        400:
          description: Invalid request or file format
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        401:
          description: Authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        413:
          description: File too large (>10MB)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        415:
          description: Unsupported file type
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        429:
          description: Rate limit exceeded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    """
    try:
        user = get_current_user()
        if not user:
            return create_error_response('User not found', 
                                       'Please login again',
                                       code=4001, status_code=404)
        
        lines_data = []
        vendor_name = "Unknown Vendor"
        invoice_number = None
        invoice_date = datetime.utcnow().date()
        filename = None
        
        # Handle multipart file upload
        if 'file' in request.files:
            file = request.files['file']
            
            # Validate file upload
            validation_error = validate_file_upload(file)
            if validation_error:
                return validation_error
            
            filename = secure_filename(file.filename)
            
            # Read file content safely (don't log content)
            try:
                file_content = file.read()
                logger.info(f"Processing file upload: {filename} ({len(file_content)} bytes) for user {user.id}")
            except Exception as e:
                return create_error_response('Failed to read file',
                                           'File may be corrupted or too large',
                                           code=4002, status_code=400)
            
            # Parse based on file type
            if filename.lower().endswith('.pdf'):
                lines_data = parse_pdf_content(file_content)
            elif filename.lower().endswith(('.txt', '.csv')):
                try:
                    content = file_content.decode('utf-8', errors='ignore')
                    lines_data = parse_text_content(content)
                except UnicodeDecodeError:
                    return create_error_response('Invalid file encoding',
                                               'File must be valid UTF-8 text',
                                               code=4003, status_code=400)
            
            # Extract vendor from form data if provided
            vendor_name = request.form.get('vendor', filename.split('.')[0].title())
            invoice_number = request.form.get('invoice_number')
            date_str = request.form.get('date')
            if date_str:
                try:
                    invoice_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
        
        # Handle JSON data
        elif request.is_json:
            data = request.get_json()
            vendor_name = data.get('vendor', 'JSON Vendor')
            invoice_number = data.get('invoice_number')
            
            date_str = data.get('date')
            if date_str:
                try:
                    invoice_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            # Extract lines from JSON
            json_lines = data.get('lines', [])
            for line in json_lines:
                if isinstance(line, dict):
                    description = line.get('description', 'JSON Line Item')
                    hours = float(line.get('hours', 1.0))
                    rate = float(line.get('rate', 250.0))
                    line_total = hours * rate
                    
                    lines_data.append({
                        'description': description,
                        'hours': hours,
                        'rate': rate,
                        'line_total': line_total
                    })
        
        else:
            return jsonify({'error': 'No file or JSON data provided'}), 400
        
        if not lines_data:
            return jsonify({'error': 'No line items found to process'}), 400
        
        # Get or create vendor
        vendor = Vendor.query.filter_by(name=vendor_name).first()
        if not vendor:
            vendor = Vendor(name=vendor_name)
            db.session.add(vendor)
            db.session.flush()  # Get vendor ID
        
        # Create invoice
        invoice = Invoice(
            user_id=user.id,
            vendor_id=vendor.id,
            invoice_number=invoice_number,
            date=invoice_date,
            filename=filename,
            lines_processed=len(lines_data),
            total_amount=0.0,
            flagged_lines=0
        )
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Score all lines using ML service (with fallback to deterministic)
        scored_lines_data, scoring_metadata = score_invoice_lines(lines_data)
        
        # Process and create line items
        total_amount = 0.0
        flagged_count = 0
        
        for line_data in scored_lines_data:
            hours = float(line_data.get('hours', 0))
            rate = float(line_data.get('rate', 0))
            line_total = float(line_data.get('line_total', hours * rate))
            
            # Get ML scoring results
            anomaly_score = line_data.get('anomaly_score', 0.0)
            is_flagged = line_data.get('is_flagged', False)
            flag_reason = line_data.get('flag_reason', 'No scoring applied')
            
            if is_flagged:
                flagged_count += 1
            
            # Create line item
            line_item = InvoiceLine(
                invoice_id=invoice.id,
                description=line_data.get('description', 'Line Item'),
                hours=hours,
                rate=rate,
                line_total=line_total,
                anomaly_score=anomaly_score,
                is_flagged=is_flagged,
                flag_reason=flag_reason
            )
            db.session.add(line_item)
            total_amount += line_total
        
        # Update invoice totals
        invoice.total_amount = total_amount
        invoice.flagged_lines = flagged_count
        
        db.session.commit()
        
        logger.info(f"Invoice processed: ID={invoice.id}, Lines={len(lines_data)}, Flagged={flagged_count}")
        logger.info(f"Scoring method: {scoring_metadata.get('method', 'unknown')}")
        
        response_data = {
            'invoice_id': invoice.id,
            'vendor': vendor_name,
            'total_amount': total_amount,
            'lines_processed': len(lines_data),
            'flagged': flagged_count,
            'invoice_number': invoice_number,
            'date': invoice_date.isoformat() if invoice_date else None,
            'scoring_method': scoring_metadata.get('method', 'unknown')
        }
        
        # Add model fallback note if applicable
        if scoring_metadata.get('note') == 'model_fallback':
            response_data['note'] = 'model_fallback'
            response_data['scoring_info'] = scoring_metadata.get('reason', 'ML models not available')
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/invoices', methods=['GET'])
@jwt_required
def get_invoices():
    """Get latest 100 invoices for current user
    ---
    get:
      tags:
        - Invoices
      summary: List user invoices
      description: Retrieve the latest 100 invoices for the authenticated user, ordered by processing date
      security:
        - jwt: []
      responses:
        200:
          description: Invoices retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  invoices:
                    type: array
                    items:
                      $ref: '#/components/schemas/Invoice'
                  count:
                    type: integer
                    description: Number of invoices returned
                    example: 15
        401:
          description: Authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        404:
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        invoices = Invoice.query.filter_by(user_id=user.id)\
            .join(Vendor)\
            .order_by(desc(Invoice.created_at))\
            .limit(100)\
            .all()
        
        result = []
        for invoice in invoices:
            result.append({
                'id': invoice.id,
                'vendor': invoice.vendor.name,
                'invoice_number': invoice.invoice_number,
                'date': invoice.date.isoformat() if invoice.date else None,
                'total_amount': invoice.total_amount,
                'lines_processed': invoice.lines_processed,
                'flagged_lines': invoice.flagged_lines,
                'status': invoice.status,
                'filename': invoice.filename,
                'created_at': invoice.created_at.isoformat()
            })
        
        return jsonify({'invoices': result}), 200
        
    except Exception as e:
        logger.error(f"Get invoices error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve invoices'}), 500

@app.route('/api/invoices/<int:invoice_id>', methods=['GET'])
@jwt_required
def get_invoice(invoice_id):
    """Get individual invoice by ID"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        invoice = Invoice.query.filter_by(id=invoice_id, user_id=user.id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        result = {
            'id': invoice.id,
            'vendor_name': invoice.vendor.name if invoice.vendor else 'Unknown',
            'invoice_number': invoice.invoice_number,
            'date': invoice.date.isoformat() if invoice.date else None,
            'total_amount': invoice.total_amount,
            'lines_processed': invoice.lines_processed,
            'flagged_lines': invoice.flagged_lines,
            'status': invoice.status,
            'filename': invoice.filename,
            'created_at': invoice.created_at.isoformat(),
            'ml_risk_score': getattr(invoice, 'ml_risk_score', None),
            'compliance_flags': getattr(invoice, 'compliance_flags', [])
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get invoice error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve invoice'}), 500

@app.route('/api/dashboard/metrics', methods=['GET'])
@jwt_required
def get_dashboard_metrics():
    """Get dashboard metrics and analytics for current user
    ---
    get:
      tags:
        - Dashboard
      summary: Get dashboard metrics
      description: |
        Retrieve comprehensive dashboard metrics including:
        - Total invoice count and spending
        - Unique vendor count
        - Average invoice amount
        - Recent activity feed
        - Spending trends and analytics
      security:
        - jwt: []
      responses:
        200:
          description: Dashboard metrics retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DashboardMetrics'
        401:
          description: Authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        404:
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
    """
def dashboard_metrics():
    """Get dashboard metrics for current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Total spend and invoice count
        totals = db.session.query(
            func.sum(Invoice.total_amount).label('total_spend'),
            func.count(Invoice.id).label('invoices_count')
        ).filter_by(user_id=user.id).first()
        
        total_spend = float(totals.total_spend) if totals.total_spend else 0.0
        invoices_count = totals.invoices_count or 0
        
        # Flagged lines count
        flagged_lines = db.session.query(func.sum(Invoice.flagged_lines))\
            .filter_by(user_id=user.id).scalar() or 0
        
        # Daily spending data (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_data = db.session.query(
            func.date(Invoice.created_at).label('date'),
            func.sum(Invoice.total_amount).label('amount')
        ).filter(
            Invoice.user_id == user.id,
            Invoice.created_at >= thirty_days_ago
        ).group_by(func.date(Invoice.created_at))\
         .order_by(func.date(Invoice.created_at))\
         .all()
        
        daily_spending = []
        for row in daily_data:
            # Handle both date objects and strings
            date_str = None
            if row.date:
                if hasattr(row.date, 'isoformat'):
                    date_str = row.date.isoformat()
                else:
                    date_str = str(row.date)
            
            daily_spending.append({
                'date': date_str,
                'amount': float(row.amount) if row.amount else 0.0
            })
        
        return jsonify({
            'total_spend': total_spend,
            'invoices_count': invoices_count,
            'flagged_lines': int(flagged_lines),
            'daily': daily_spending
        }), 200
        
    except Exception as e:
        logger.error(f"Dashboard metrics error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve metrics'}), 500

@app.route('/api/analytics/summary', methods=['GET'])
@jwt_required
def analytics_summary():
    """Get analytics summary for current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Total spend and invoice count
        totals = db.session.query(
            func.sum(Invoice.total_amount).label('total_spend'),
            func.count(Invoice.id).label('invoices_count')
        ).filter_by(user_id=user.id).first()
        
        total_spend = float(totals.total_spend) if totals.total_spend else 0.0
        invoices_count = totals.invoices_count or 0
        
        return jsonify({
            'totalSpend': total_spend,
            'totalInvoices': invoices_count,
            'avgInvoiceAmount': total_spend / invoices_count if invoices_count > 0 else 0
        }), 200
        
    except Exception as e:
        logger.error(f"Analytics summary error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve analytics summary'}), 500

@app.route('/api/analytics/spending', methods=['GET'])
@jwt_required  
def analytics_spending():
    """Get spending analytics by timeframe"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        timeframe = request.args.get('timeframe', 'month')
        
        # Calculate date range based on timeframe
        if timeframe == 'week':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif timeframe == 'year':
            start_date = datetime.utcnow() - timedelta(days=365)
        else:  # default to month
            start_date = datetime.utcnow() - timedelta(days=30)
            
        # Get spending data for the timeframe
        spending_data = db.session.query(
            func.date(Invoice.created_at).label('date'),
            func.sum(Invoice.total_amount).label('amount')
        ).filter(
            Invoice.user_id == user.id,
            Invoice.created_at >= start_date
        ).group_by(func.date(Invoice.created_at)).all()
        
        # Format the data
        formatted_data = []
        for row in spending_data:
            date_str = row.date.strftime('%Y-%m-%d') if row.date else 'Unknown'
            formatted_data.append({
                'date': date_str,
                'amount': float(row.amount) if row.amount else 0.0
            })
        
        return jsonify({'spending': formatted_data}), 200
        
    except Exception as e:
        logger.error(f"Analytics spending error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve spending analytics'}), 500

@app.route('/api/analytics/vendors', methods=['GET'])
@jwt_required
def analytics_vendors():
    """Get vendor analytics for current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get vendor spending data
        vendor_data = db.session.query(
            Vendor.name,
            func.sum(Invoice.total_amount).label('total_spend'),
            func.count(Invoice.id).label('invoice_count')
        ).join(Invoice).filter(Invoice.user_id == user.id).group_by(Vendor.name).all()
        
        # Format vendor data
        vendors = []
        for row in vendor_data:
            vendors.append({
                'name': row.name or 'Unknown Vendor',
                'totalSpend': float(row.total_spend) if row.total_spend else 0.0,
                'invoiceCount': row.invoice_count or 0
            })
        
        # Sort by total spend descending
        vendors.sort(key=lambda x: x['totalSpend'], reverse=True)
        
        return jsonify({'vendors': vendors}), 200
        
    except Exception as e:
        logger.error(f"Analytics vendors error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve vendor analytics'}), 500

@app.route('/api/notifications', methods=['GET'])
@jwt_required
def get_notifications():
    """Get notifications for current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For now, return sample notifications based on user's invoices
        notifications = []
        
        # Check for recent uploads
        recent_invoices = db.session.query(Invoice)\
            .filter_by(user_id=user.id)\
            .order_by(desc(Invoice.created_at))\
            .limit(3).all()
            
        for invoice in recent_invoices:
            notifications.append({
                'id': f"upload_{invoice.id}",
                'type': 'upload_success',
                'title': 'Invoice Processed',
                'message': f'Invoice from {invoice.vendor.name if invoice.vendor else "Unknown"} has been processed',
                'timestamp': invoice.created_at.isoformat(),
                'read': False
            })
        
        return jsonify({'notifications': notifications}), 200
        
    except Exception as e:
        logger.error(f"Get notifications error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve notifications'}), 500

@app.route('/api/notifications/unread-count', methods=['GET'])
@jwt_required
def get_unread_count():
    """Get unread notification count"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For now, return count based on recent activity
        recent_count = db.session.query(func.count(Invoice.id))\
            .filter(
                Invoice.user_id == user.id,
                Invoice.created_at >= datetime.utcnow() - timedelta(days=1)
            ).scalar() or 0
            
        return jsonify({'count': recent_count}), 200
        
    except Exception as e:
        logger.error(f"Get unread count error: {str(e)}")
        return jsonify({'error': 'Failed to get unread count'}), 500

@app.route('/api/notifications/<notification_id>/ack', methods=['POST'])
@jwt_required
def acknowledge_notification(notification_id):
    """Acknowledge a notification"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For now, just return success
        return jsonify({'message': 'Notification acknowledged'}), 200
        
    except Exception as e:
        logger.error(f"Acknowledge notification error: {str(e)}")
        return jsonify({'error': 'Failed to acknowledge notification'}), 500

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@jwt_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For now, just return success
        return jsonify({'message': 'All notifications marked as read'}), 200
        
    except Exception as e:
        logger.error(f"Mark all read error: {str(e)}")
        return jsonify({'error': 'Failed to mark notifications as read'}), 500

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

# Initialize database on import
init_db()

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting LAIT Real Backend on port 5003")
    logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    logger.info("Available endpoints:")
    logger.info("  GET  /api/health")
    logger.info("  GET  /api/ml/status")
    logger.info("  POST /api/auth/register")
    logger.info("  POST /api/auth/login")
    logger.info("  GET  /api/auth/me")
    logger.info("  POST /api/invoices/upload")
    logger.info("  GET  /api/invoices")
    logger.info("  GET  /api/invoices/{id}")
    logger.info("  GET  /api/dashboard/metrics")
    logger.info("  GET  /api/analytics/summary")
    logger.info("  GET  /api/analytics/spending")
    logger.info("  GET  /api/analytics/vendors")
    logger.info("  GET  /api/notifications")
    logger.info("  GET  /api/notifications/unread-count")
    logger.info("  POST /api/notifications/{id}/ack")
    logger.info("  POST /api/notifications/mark-all-read")
    
    app.run(host='0.0.0.0', port=5003, debug=False)
