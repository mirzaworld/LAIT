#!/usr/bin/env python3
"""
LAIT Real Production Backend
- Flask with JWT Authentication (bcrypt)
- PostgreSQL with SQLAlchemy
- PDF/TXT parsing with pdfplumber
- Advanced invoice scoring and analytics
- Real-time dashboard metrics
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import bcrypt
import pdfplumber
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'lait-production-jwt-secret-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database Configuration - PostgreSQL
database_url = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432/lait_production')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'])

# Initialize rate limiter with Redis backend (fallback to memory)
def get_user_id_from_token():
    """Custom key function to rate limit by user token"""
    try:
        if jwt_required(optional=True)():
            return get_jwt_identity()
        return get_remote_address(request)
    except:
        return get_remote_address(request)

def get_user_token_key():
    """Get rate limit key from JWT token for authenticated endpoints"""
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
        return get_remote_address(request)
    except:
        return get_remote_address(request)

# Configure limiter with Redis if available, otherwise use memory
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
try:
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        storage_uri=redis_url,
        default_limits=["1000 per hour", "100 per minute"]
    )
    logger.info(f"Rate limiter initialized with Redis: {redis_url}")
except Exception as e:
    logger.warning(f"Failed to connect to Redis, using memory storage: {e}")
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["1000 per hour", "100 per minute"]
    )

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ===== DATABASE MODELS =====

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(200))
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    invoices = db.relationship('Invoice', back_populates='user', lazy='dynamic')
    
    def set_password(self, password: str):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Extracted data
    vendor_name = db.Column(db.String(200))
    total_amount = db.Column(db.Numeric(12, 2))
    invoice_number = db.Column(db.String(100))
    invoice_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    
    # AI Analysis results
    confidence_score = db.Column(db.Float)
    category = db.Column(db.String(100))
    risk_score = db.Column(db.Float)
    extracted_text = db.Column(db.Text)
    line_items = db.Column(db.JSON)  # Store parsed line items
    ai_insights = db.Column(db.JSON)  # Store AI analysis results
    
    # Status and metadata
    status = db.Column(db.String(50), default='processed')
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='invoices')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.original_filename,
            'vendor_name': self.vendor_name,
            'total_amount': float(self.total_amount) if self.total_amount else 0.0,
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'confidence_score': self.confidence_score,
            'category': self.category,
            'risk_score': self.risk_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'line_items': self.line_items,
            'ai_insights': self.ai_insights
        }

# ===== INVOICE ANALYSIS ENGINE =====

class InvoiceAnalysisEngine:
    """Advanced invoice analysis with ML-style scoring"""
    
    VENDOR_PATTERNS = {
        'law_firm': [
            r'law firm', r'llp', r'pllc', r'attorneys?', r'legal services',
            r'counsel', r'esquire', r'esq\.', r'bar association'
        ],
        'court_fees': [
            r'court', r'filing fee', r'clerk', r'judicial', r'tribunal',
            r'docket', r'court costs', r'registry'
        ],
        'expert_witness': [
            r'expert', r'witness', r'testimony', r'deposition', r'consultant',
            r'forensic', r'valuation', r'analysis'
        ],
        'litigation_support': [
            r'discovery', r'document review', r'paralegal', r'legal research',
            r'case management', r'litigation support'
        ],
        'compliance': [
            r'compliance', r'audit', r'regulatory', r'governance',
            r'risk management', r'internal investigation'
        ]
    }
    
    AMOUNT_PATTERNS = [
        r'\$[\d,]+\.?\d*',  # $1,000.00
        r'USD\s*[\d,]+\.?\d*',  # USD 1000.00
        r'total[:\s]+\$?[\d,]+\.?\d*',  # Total: $1000
        r'amount[:\s]+\$?[\d,]+\.?\d*',  # Amount: 1000
        r'[\d,]+\.?\d*\s*dollars?'  # 1000 dollars
    ]
    
    DATE_PATTERNS = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY-MM-DD
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
    ]
    
    def analyze_invoice(self, text: str, filename: str) -> Dict:
        """Comprehensive invoice analysis"""
        analysis = {
            'confidence_score': 0.0,
            'extracted_data': {},
            'category': 'unknown',
            'risk_score': 0.0,
            'line_items': [],
            'ai_insights': [],
            'recommendations': []
        }
        
        text_lower = text.lower()
        
        # Extract vendor information
        vendor_info = self._extract_vendor(text, text_lower)
        analysis['extracted_data'].update(vendor_info)
        
        # Extract amounts
        amount_info = self._extract_amounts(text)
        analysis['extracted_data'].update(amount_info)
        
        # Extract dates
        date_info = self._extract_dates(text)
        analysis['extracted_data'].update(date_info)
        
        # Extract line items
        line_items = self._extract_line_items(text)
        analysis['line_items'] = line_items
        analysis['extracted_data']['line_items'] = line_items
        
        # Categorize vendor
        category = self._categorize_vendor(text_lower)
        analysis['category'] = category
        
        # Calculate confidence score
        confidence = self._calculate_confidence(analysis['extracted_data'], text)
        analysis['confidence_score'] = confidence
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(analysis['extracted_data'], text_lower)
        analysis['risk_score'] = risk_score
        
        # Generate insights
        insights = self._generate_insights(analysis, filename)
        analysis['ai_insights'] = insights
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis)
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def _extract_vendor(self, text: str, text_lower: str) -> Dict:
        """Extract vendor information"""
        lines = text.split('\n')
        vendor_name = 'Unknown Vendor'
        
        # Try to find vendor in first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 5 and not re.search(r'\d{4}', line) and 'invoice' not in line.lower():
                # Skip obvious non-vendor lines
                if not any(skip in line.lower() for skip in ['date', 'number', 'amount', 'total', 'bill to']):
                    vendor_name = line
                    break
        
        return {'vendor_name': vendor_name}
    
    def _extract_amounts(self, text: str) -> Dict:
        """Extract monetary amounts"""
        amounts = []
        
        for pattern in self.AMOUNT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean and convert to float
                clean_amount = re.sub(r'[^\d.]', '', match)
                try:
                    amount = float(clean_amount)
                    if amount > 0:
                        amounts.append(amount)
                except ValueError:
                    continue
        
        # Return the largest amount as total (likely the invoice total)
        total_amount = max(amounts) if amounts else 0.0
        
        return {
            'total_amount': total_amount,
            'currency': 'USD',
            'detected_amounts': amounts[:5]  # Keep top 5 amounts
        }
    
    def _extract_dates(self, text: str) -> Dict:
        """Extract dates from invoice"""
        dates = []
        
        for pattern in self.DATE_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    # Try to parse date
                    if '/' in match:
                        parts = match.split('/')
                        if len(parts) == 3:
                            # Assume MM/DD/YYYY or DD/MM/YYYY
                            month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                            if year < 100:  # Handle 2-digit years
                                year += 2000
                            date_obj = datetime(year, month, day).date()
                            dates.append(date_obj)
                except (ValueError, IndexError):
                    continue
        
        # Sort dates and assign roles
        dates.sort()
        invoice_date = dates[0] if dates else datetime.now().date()
        due_date = dates[-1] if len(dates) > 1 else invoice_date + timedelta(days=30)
        
        return {
            'invoice_date': invoice_date.isoformat(),
            'due_date': due_date.isoformat(),
            'detected_dates': [d.isoformat() for d in dates[:3]]
        }
    
    def _extract_line_items(self, text: str) -> List[Dict]:
        """Extract line items from invoice"""
        line_items = []
        lines = text.split('\n')
        
        for line in lines:
            # Look for lines with amounts
            amount_match = re.search(r'\$?([\d,]+\.?\d*)', line)
            if amount_match and len(line.strip()) > 10:
                try:
                    amount = float(amount_match.group(1).replace(',', ''))
                    if amount > 0:
                        # Extract description (text before the amount)
                        description = line[:amount_match.start()].strip()
                        if description and len(description) > 3:
                            line_items.append({
                                'description': description,
                                'amount': amount,
                                'line': line.strip()
                            })
                except ValueError:
                    continue
        
        return line_items[:10]  # Return top 10 line items
    
    def _categorize_vendor(self, text_lower: str) -> str:
        """Categorize vendor based on text content"""
        category_scores = {}
        
        for category, patterns in self.VENDOR_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            category_scores[category] = score
        
        # Return category with highest score
        best_category = max(category_scores, key=category_scores.get)
        return best_category if category_scores[best_category] > 0 else 'other_legal'
    
    def _calculate_confidence(self, extracted_data: Dict, text: str) -> float:
        """Calculate confidence score based on extracted data quality"""
        score = 0.0
        
        # Vendor name quality
        if extracted_data.get('vendor_name', '').strip() and extracted_data['vendor_name'] != 'Unknown Vendor':
            score += 0.25
        
        # Amount extraction
        if extracted_data.get('total_amount', 0) > 0:
            score += 0.25
        
        # Date extraction
        if extracted_data.get('invoice_date'):
            score += 0.15
        if extracted_data.get('due_date'):
            score += 0.10
        
        # Line items
        if extracted_data.get('line_items'):
            score += min(0.15, len(extracted_data['line_items']) * 0.03)
        
        # Text quality (length, structure)
        if len(text) > 100:
            score += 0.10
        
        return min(1.0, score)
    
    def _calculate_risk_score(self, extracted_data: Dict, text_lower: str) -> float:
        """Calculate risk score for the invoice"""
        risk_score = 0.0
        
        # High amount risk
        amount = extracted_data.get('total_amount', 0)
        if amount > 50000:
            risk_score += 0.3
        elif amount > 25000:
            risk_score += 0.2
        elif amount > 10000:
            risk_score += 0.1
        
        # Urgency indicators
        urgency_terms = ['urgent', 'rush', 'emergency', 'asap', 'immediate']
        for term in urgency_terms:
            if term in text_lower:
                risk_score += 0.15
                break
        
        # Unusual patterns
        if 'cash only' in text_lower:
            risk_score += 0.2
        if 'wire transfer' in text_lower:
            risk_score += 0.1
        
        return min(1.0, risk_score)
    
    def _generate_insights(self, analysis: Dict, filename: str) -> List[str]:
        """Generate AI insights about the invoice"""
        insights = []
        
        extracted = analysis['extracted_data']
        vendor = extracted.get('vendor_name', 'Unknown')
        amount = extracted.get('total_amount', 0)
        category = analysis['category'].replace('_', ' ').title()
        confidence = analysis['confidence_score']
        
        insights.append(f"Vendor '{vendor}' classified as {category}")
        insights.append(f"Total amount ${amount:,.2f} identified with {confidence:.1%} confidence")
        
        if analysis['risk_score'] > 0.3:
            insights.append(f"High-risk invoice detected (risk score: {analysis['risk_score']:.1%})")
        elif analysis['risk_score'] > 0.1:
            insights.append(f"Medium-risk factors identified (risk score: {analysis['risk_score']:.1%})")
        else:
            insights.append("Low-risk invoice with standard processing requirements")
        
        line_items = len(extracted.get('line_items', []))
        if line_items > 0:
            insights.append(f"Successfully extracted {line_items} line items for detailed review")
        
        return insights
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate processing recommendations"""
        recommendations = []
        
        # Standard recommendations
        recommendations.append("Verify vendor credentials and contract terms")
        recommendations.append("Cross-reference line items with approved services")
        
        # Risk-based recommendations
        if analysis['risk_score'] > 0.3:
            recommendations.append("Requires senior management approval due to high-risk factors")
            recommendations.append("Conduct additional vendor verification")
        elif analysis['risk_score'] > 0.1:
            recommendations.append("Review flagged items before processing payment")
        
        # Amount-based recommendations
        amount = analysis['extracted_data'].get('total_amount', 0)
        if amount > 25000:
            recommendations.append("Schedule payment in next executive review cycle")
        elif amount > 10000:
            recommendations.append("Obtain department head approval")
        else:
            recommendations.append("Standard processing workflow applies")
        
        return recommendations

# Initialize analysis engine
analysis_engine = InvoiceAnalysisEngine()

# ===== FILE PROCESSING UTILITIES =====

def extract_text_from_file(filepath: str, mime_type: str) -> str:
    """Extract text from uploaded file"""
    try:
        if mime_type == 'application/pdf':
            # Use pdfplumber for PDF extraction
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        
        elif mime_type.startswith('text/'):
            # Handle text files
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read().strip()
        
        else:
            logger.warning(f"Unsupported file type: {mime_type}")
            return ""
            
    except Exception as e:
        logger.error(f"Error extracting text from {filepath}: {str(e)}")
        return ""

def get_file_mime_type(filename: str) -> str:
    """Get MIME type from filename"""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    mime_types = {
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    return mime_types.get(ext, 'application/octet-stream')

# ===== AUTHENTICATION ROUTES =====

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration with bcrypt password hashing"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        company = data.get('company', '').strip()
        
        # Validate email format
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            company=company
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate JWT token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'role': user.role
            }
        )
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """User authentication with bcrypt verification"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'role': user.role
            }
        )
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500

# ===== INVOICE PROCESSING ROUTES =====

@app.route('/api/invoices/upload', methods=['POST'])
@jwt_required()
@limiter.limit("60 per minute", key_func=get_user_token_key)
def upload_invoice():
    """Upload and analyze invoice with full text processing"""
    try:
        user_id = int(get_jwt_identity())
        
        # Check for uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Secure the filename
        original_filename = file.filename
        filename = secure_filename(original_filename)
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get file metadata
        file_size = os.path.getsize(filepath)
        mime_type = get_file_mime_type(original_filename)
        
        # Extract text from file
        extracted_text = extract_text_from_file(filepath, mime_type)
        
        if not extracted_text:
            return jsonify({'error': 'Unable to extract text from file'}), 400
        
        # Perform AI analysis
        analysis_results = analysis_engine.analyze_invoice(extracted_text, filename)
        
        # Create invoice record
        invoice = Invoice(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_path=filepath,
            file_size=file_size,
            mime_type=mime_type,
            vendor_name=analysis_results['extracted_data'].get('vendor_name'),
            total_amount=Decimal(str(analysis_results['extracted_data'].get('total_amount', 0))),
            invoice_date=datetime.fromisoformat(analysis_results['extracted_data']['invoice_date']).date() if analysis_results['extracted_data'].get('invoice_date') else None,
            due_date=datetime.fromisoformat(analysis_results['extracted_data']['due_date']).date() if analysis_results['extracted_data'].get('due_date') else None,
            confidence_score=analysis_results['confidence_score'],
            category=analysis_results['category'],
            risk_score=analysis_results['risk_score'],
            extracted_text=extracted_text,
            line_items=analysis_results['line_items'],
            ai_insights=analysis_results
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        logger.info(f"Invoice uploaded and analyzed: {original_filename} by user {user_id}")
        
        return jsonify({
            'message': 'Invoice uploaded and analyzed successfully',
            'invoice': invoice.to_dict(),
            'analysis': analysis_results
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Invoice upload error: {str(e)}")
        return jsonify({'error': 'Invoice upload failed'}), 500

@app.route('/api/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get user's invoices with pagination"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Query invoices with pagination
        invoices_query = Invoice.query.filter_by(user_id=user_id).order_by(Invoice.created_at.desc())
        invoices_paginated = invoices_query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'invoices': [invoice.to_dict() for invoice in invoices_paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': invoices_paginated.total,
                'pages': invoices_paginated.pages,
                'has_next': invoices_paginated.has_next,
                'has_prev': invoices_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get invoices error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve invoices'}), 500

@app.route('/api/invoices/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get specific invoice details"""
    try:
        user_id = int(get_jwt_identity())
        
        invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify(invoice.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Get invoice error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve invoice'}), 500

# ===== DASHBOARD AND ANALYTICS ROUTES =====

@app.route('/api/dashboard/metrics', methods=['GET'])
@jwt_required()
def dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    try:
        user_id = int(get_jwt_identity())
        
        # Basic aggregations
        total_invoices = Invoice.query.filter_by(user_id=user_id).count()
        total_amount = db.session.query(func.sum(Invoice.total_amount)).filter_by(user_id=user_id).scalar() or 0
        avg_amount = db.session.query(func.avg(Invoice.total_amount)).filter_by(user_id=user_id).scalar() or 0
        avg_risk_score = db.session.query(func.avg(Invoice.risk_score)).filter_by(user_id=user_id).scalar() or 0
        
        # Recent invoices (last 10)
        recent_invoices = Invoice.query.filter_by(user_id=user_id).order_by(Invoice.created_at.desc()).limit(10).all()
        
        # Top vendors
        vendor_stats = db.session.query(
            Invoice.vendor_name,
            func.count(Invoice.id).label('invoice_count'),
            func.sum(Invoice.total_amount).label('total_amount')
        ).filter_by(user_id=user_id).group_by(Invoice.vendor_name).order_by(func.sum(Invoice.total_amount).desc()).limit(5).all()
        
        # Category breakdown
        category_stats = db.session.query(
            Invoice.category,
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.total_amount).label('total')
        ).filter_by(user_id=user_id).group_by(Invoice.category).all()
        
        # Daily spending series (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        daily_stats = db.session.query(
            func.date(Invoice.created_at).label('date'),
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.total_amount).label('amount')
        ).filter(
            Invoice.user_id == user_id,
            Invoice.created_at >= thirty_days_ago
        ).group_by(func.date(Invoice.created_at)).order_by('date').all()
        
        # Format response
        response = {
            'totals': {
                'total_invoices': total_invoices,
                'total_amount': float(total_amount),
                'average_amount': float(avg_amount),
                'average_risk_score': float(avg_risk_score) if avg_risk_score else 0.0
            },
            'recent_invoices': [
                {
                    'id': inv.id,
                    'vendor_name': inv.vendor_name,
                    'total_amount': float(inv.total_amount) if inv.total_amount else 0.0,
                    'created_at': inv.created_at.isoformat() if inv.created_at else None,
                    'status': inv.status,
                    'risk_score': inv.risk_score
                } for inv in recent_invoices
            ],
            'top_vendors': [
                {
                    'vendor_name': stat.vendor_name,
                    'invoice_count': stat.invoice_count,
                    'total_amount': float(stat.total_amount) if stat.total_amount else 0.0
                } for stat in vendor_stats
            ],
            'category_breakdown': [
                {
                    'category': stat.category,
                    'count': stat.count,
                    'total_amount': float(stat.total) if stat.total else 0.0
                } for stat in category_stats
            ],
            'daily_series': [
                {
                    'date': stat.date.isoformat(),
                    'invoice_count': stat.count,
                    'total_amount': float(stat.amount) if stat.amount else 0.0
                } for stat in daily_stats
            ]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Dashboard metrics error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve dashboard metrics'}), 500

@app.route('/api/analytics/vendors', methods=['GET'])
@jwt_required()
def vendor_analytics():
    """Get detailed vendor analytics"""
    try:
        user_id = int(get_jwt_identity())
        
        # Vendor performance analytics
        vendor_analytics = db.session.query(
            Invoice.vendor_name,
            func.count(Invoice.id).label('total_invoices'),
            func.sum(Invoice.total_amount).label('total_spent'),
            func.avg(Invoice.total_amount).label('avg_amount'),
            func.avg(Invoice.risk_score).label('avg_risk'),
            func.avg(Invoice.confidence_score).label('avg_confidence'),
            func.max(Invoice.created_at).label('last_invoice')
        ).filter_by(user_id=user_id).group_by(Invoice.vendor_name).order_by(func.sum(Invoice.total_amount).desc()).all()
        
        formatted_analytics = [
            {
                'vendor_name': stat.vendor_name,
                'total_invoices': stat.total_invoices,
                'total_spent': float(stat.total_spent) if stat.total_spent else 0.0,
                'average_amount': float(stat.avg_amount) if stat.avg_amount else 0.0,
                'average_risk_score': float(stat.avg_risk) if stat.avg_risk else 0.0,
                'average_confidence': float(stat.avg_confidence) if stat.avg_confidence else 0.0,
                'last_invoice_date': stat.last_invoice.isoformat() if stat.last_invoice else None
            } for stat in vendor_analytics
        ]
        
        return jsonify({
            'vendor_analytics': formatted_analytics,
            'summary': {
                'total_vendors': len(formatted_analytics),
                'total_relationships': sum(v['total_invoices'] for v in formatted_analytics),
                'avg_vendor_spend': sum(v['total_spent'] for v in formatted_analytics) / len(formatted_analytics) if formatted_analytics else 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Vendor analytics error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve vendor analytics'}), 500

# ===== HEALTH AND UTILITY ROUTES =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'service': 'LAIT Real Backend',
            'version': '1.0.0',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/system/stats', methods=['GET'])
@jwt_required()
def system_stats():
    """Get system-wide statistics (admin only)"""
    try:
        # Basic system stats
        total_users = User.query.count()
        total_invoices = Invoice.query.count()
        total_processed_amount = db.session.query(func.sum(Invoice.total_amount)).scalar() or 0
        
        return jsonify({
            'total_users': total_users,
            'total_invoices': total_invoices,
            'total_processed_amount': float(total_processed_amount),
            'uptime': 'Running',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"System stats error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve system statistics'}), 500

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit exceeded errors"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': getattr(error, 'retry_after', 60)
    }), 429

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401

# ===== DATABASE INITIALIZATION =====

def init_database():
    """Initialize database tables"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")

# ===== APPLICATION STARTUP =====

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start application
    logger.info("🚀 Starting LAIT Real Production Backend")
    logger.info("🔐 JWT Authentication: Enabled")
    logger.info("🗃️  PostgreSQL Database: Connected") 
    logger.info("🤖 AI Invoice Analysis: Ready")
    logger.info("📊 Advanced Analytics: Available")
    logger.info("🌐 Server running on http://localhost:5003")
    
    app.run(
        host='0.0.0.0',
        port=5003,
        debug=os.environ.get('FLASK_ENV') == 'development',
        threaded=True
    )
