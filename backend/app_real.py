#!/usr/bin/env python3
"""
LAIT Real Backend - Self-contained Flask application
Port 5003 with JWT auth, bcrypt, SQLAlchemy, PDF parsing
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import bcrypt
import jwt
import pdfplumber
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc
from io import BytesIO, StringIO
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'lait-dev-secret-key-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///lait.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Rate limiting setup
def get_user_id_for_rate_limit():
    """Extract user ID from JWT token for rate limiting"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return get_remote_address()
    
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return f"user_{payload['user_id']}"
    except:
        return get_remote_address()

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per hour"],
    storage_uri="memory://"
)

# Enable CORS for /api/* routes
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'], 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True)

# Database setup
db = SQLAlchemy(app)

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
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def decode_jwt_token(token: str) -> Optional[Dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ============================================================================
# ERROR HANDLING & LOGGING HELPERS  
# ============================================================================

def log_request():
    """Log incoming requests with user info if available"""
    user_info = "anonymous"
    if hasattr(g, 'current_user') and g.current_user:
        user_info = f"user_{g.current_user.id}"
    
    logger.info(f"{request.method} {request.path} - {user_info} - IP:{get_remote_address()}")

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

def validate_file_upload(file):
    """Validate uploaded file size and type"""
    if not file or not file.filename:
        return create_error_response(
            "No file provided", 
            "Please select a file to upload", 
            code=1001
        )
    
    # Check file size (already handled by Flask MAX_CONTENT_LENGTH, but double-check)
    if hasattr(file, 'content_length') and file.content_length and file.content_length > 10 * 1024 * 1024:
        return create_error_response(
            "File too large", 
            "Maximum file size is 10MB", 
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
    
    return None  # No error

def jwt_required(f):
    """Decorator to require JWT authentication"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return create_error_response('Missing or invalid authorization header', 
                                       'Include "Authorization: Bearer <token>" header',
                                       code=2001, status_code=401)
        
        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)
        if not payload:
            return create_error_response('Invalid or expired token',
                                       'Please login again to get a new token',
                                       code=2002, status_code=401)
        
        # Add user_id to request context and g for logging
        request.user_id = payload['user_id']
        g.current_user = User.query.get(payload['user_id'])
        
        # Log the request with user info
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

def calculate_anomaly_score(hours: float, rate: float, line_total: float) -> tuple[float, bool, str]:
    """Calculate anomaly score and flagging for a line item"""
    anomaly_score = (rate / 1000) + (hours / 12) + (line_total / 5000)
    
    flag_reasons = []
    if rate > 900:
        flag_reasons.append(f"High rate: ${rate}/hr")
    if hours > 10:
        flag_reasons.append(f"Excessive hours: {hours}")
    if line_total > 3000:
        flag_reasons.append(f"High line total: ${line_total}")
    
    is_flagged = bool(flag_reasons)
    flag_reason = "; ".join(flag_reasons) if flag_reasons else None
    
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
    """Health check endpoint"""
    return jsonify({'ok': True, 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user with bcrypt password hashing"""
    try:
        # Log request for non-authenticated endpoint
        log_request()
        
        data = request.get_json()
        if not data:
            return create_error_response('Missing request body',
                                       'Send JSON data with email and password',
                                       code=3101)
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return create_error_response('Email and password are required',
                                       'Both email and password must be provided',
                                       code=3102)
        
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
        
        # Generate JWT token
        token = generate_jwt_token(user.id)
        
        logger.info(f"User registered: {email}")
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Login user with bcrypt password verification"""
    try:
        # Log request for non-authenticated endpoint
        log_request()
        
        data = request.get_json()
        if not data:
            return create_error_response('Missing request body', 
                                       'Send JSON data with email and password',
                                       code=3001)
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return create_error_response('Email and password are required',
                                       'Both email and password must be provided',
                                       code=3002)
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return create_error_response('Invalid credentials',
                                       'Check your email and password',
                                       code=3003, status_code=401)
        
        # Generate JWT token
        token = generate_jwt_token(user.id)
        
        logger.info(f"User logged in: {email} (ID: {user.id})")
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/invoices/upload', methods=['POST'])
@limiter.limit("60 per minute", key_func=get_user_id_for_rate_limit)
@jwt_required
def upload_invoice():
    """Upload and process invoice (file or JSON data)"""
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
        
        # Process and create line items
        total_amount = 0.0
        flagged_count = 0
        
        for line_data in lines_data:
            hours = float(line_data.get('hours', 0))
            rate = float(line_data.get('rate', 0))
            line_total = float(line_data.get('line_total', hours * rate))
            
            # Calculate anomaly score and flagging
            anomaly_score, is_flagged, flag_reason = calculate_anomaly_score(hours, rate, line_total)
            
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
        
        return jsonify({
            'invoice_id': invoice.id,
            'vendor': vendor_name,
            'total_amount': total_amount,
            'lines_processed': len(lines_data),
            'flagged': flagged_count,
            'invoice_number': invoice_number,
            'date': invoice_date.isoformat() if invoice_date else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/invoices', methods=['GET'])
@jwt_required
def get_invoices():
    """Get latest 100 invoices for current user"""
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

@app.route('/api/dashboard/metrics', methods=['GET'])
@jwt_required
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
    logger.info("  POST /api/auth/register")
    logger.info("  POST /api/auth/login")
    logger.info("  POST /api/invoices/upload")
    logger.info("  GET  /api/invoices")
    logger.info("  GET  /api/dashboard/metrics")
    logger.info("  GET  /api/health")
    
    app.run(host='0.0.0.0', port=5003, debug=True)
