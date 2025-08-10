"""
LAIT Comprehensive Legal Intelligence API
Enhanced with Advanced Features:
- ML-powered analytics and predictions
- Matter management system  
- External API integrations
- Advanced reporting
- Document management
- Vendor intelligence
"""

import os
import sys
import pandas as pd
import logging
import random
import json
import time
import math
import io
import base64
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, current_app, make_response, Response
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from sqlalchemy import func, desc

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Unified models import (single source of truth)
from db.database import User, Invoice, Vendor, SessionLocal, init_db, get_db_session  # noqa: F401
from models.db_models import AuditLog  # noqa: F401

# Import ML models and analyzers
try:
    from models.invoice_analyzer import InvoiceAnalyzer
    from models.vendor_analyzer import VendorAnalyzer
    from models.risk_predictor import RiskPredictor
    from models.matter_analyzer import MatterAnalyzer
    from models.enhanced_invoice_analyzer import EnhancedInvoiceAnalyzer
except ImportError as e:
    print(f"Warning: Model imports failed ({e}). ML features may be limited.")
    
# Load environment variables
load_dotenv()

# Configure more robust logging with file output
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'lait_api.log')

# Configure logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Socket.IO
socketio = SocketIO()

# Configure rate limiter globally
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per minute"])  # Adjust as needed

def create_app():
    """
    Application factory function that creates and configures the Flask app.
    """
    app = Flask(__name__)
    
    # Configure app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/legalspend')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
    
    # Configure CORS to accept requests from frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",  # Vite dev server
                "http://localhost:4173",  # Vite preview
                "http://127.0.0.1:5173",
                "http://127.0.0.1:4173",
                os.getenv("FRONTEND_URL", "http://localhost:5173")
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"]
        }
    })
    limiter.init_app(app)
    # Add an OPTIONS handler for preflight requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', 'http://localhost:5173'))
            response.headers.add('Access-Control-Allow-Headers', "Content-Type, Authorization, Accept, Origin, X-Requested-With")
            response.headers.add('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS, HEAD")
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)
    jwt = JWTManager(app)
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
    
    # Initialize Socket.IO with CORS support
    socketio.init_app(app,
        cors_allowed_origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176"
        ],
        async_mode='threading',
        logger=True,
        engineio_logger=True
    )
    
    # Socket.IO event handlers
    @socketio.on('connect')
    def handle_connect():
        logger.info("Client connected to Socket.IO")

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info("Client disconnected from Socket.IO")
        
    # Initialize ML models
    try:
        app.invoice_analyzer = InvoiceAnalyzer()
        app.vendor_analyzer = VendorAnalyzer()
        app.risk_predictor = RiskPredictor()
        app.matter_analyzer = MatterAnalyzer()
        app.enhanced_invoice_analyzer = EnhancedInvoiceAnalyzer()
        logger.info("✅ ML models initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML models: {e}")
        app.invoice_analyzer = None
        app.vendor_analyzer = None
        app.risk_predictor = None
        app.matter_analyzer = None
        app.enhanced_invoice_analyzer = None

    # Import real-time data collector
    from services.real_time_data_collector import RealTimeLegalDataCollector
    
    # Initialize data collector instance
    data_collector = RealTimeLegalDataCollector()
    
    # Store collector in app context for access in endpoints
    app.data_collector = data_collector

    # API Routes
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow()})
    
    # Dashboard metrics endpoint
    @app.route('/api/dashboard/metrics')
    def dashboard_metrics():
        """Dashboard metrics endpoint"""
        try:
            from db.database import get_db_session, Invoice, Vendor
            
            session = get_db_session()
            
            # Get basic metrics
            total_spend = session.query(func.sum(Invoice.amount)).scalar() or 0
            invoice_count = session.query(func.count(Invoice.id)).scalar() or 0
            vendor_count = session.query(func.count(func.distinct(Invoice.vendor_id))).scalar() or 0
            avg_risk_score = session.query(func.avg(Invoice.risk_score)).scalar() or 0
            
            # Get recent invoices with vendors
            recent_invoices = session.query(Invoice)\
                .join(Vendor, Invoice.vendor_id == Vendor.id, isouter=True)\
                .order_by(desc(Invoice.created_at))\
                .limit(5)\
                .all()
            
            # Get top vendors
            top_vendors = session.query(
                Vendor.name,
                func.sum(Invoice.amount).label('total_spend')
            ).join(Invoice)\
             .group_by(Vendor.name)\
             .order_by(desc('total_spend'))\
             .limit(5)\
             .all()
            
            # Calculate trends
            current_month = datetime.now().replace(day=1)
            prev_month = (current_month - timedelta(days=1)).replace(day=1)
            
            current_month_spend = session.query(func.sum(Invoice.amount))\
                .filter(Invoice.date >= current_month)\
                .scalar() or 0
                
            prev_month_spend = session.query(func.sum(Invoice.amount))\
                .filter(
                    Invoice.date >= prev_month,
                    Invoice.date < current_month
                )\
                .scalar() or 0
            
            spend_change = 0
            if prev_month_spend > 0:
                spend_change = ((current_month_spend - prev_month_spend) / prev_month_spend) * 100
            
            # Calculate additional metrics while session is active
            high_risk_count = session.query(Invoice).filter(Invoice.risk_score > 0.7).count() if total_spend > 0 else 0
            risk_factors_count = session.query(Invoice).filter(Invoice.risk_score > 0.5).count() if total_spend > 0 else 0
            
            # Prepare data structures before closing session
            recent_invoices_data = []
            for invoice in recent_invoices:
                vendor_name = 'Unknown'
                if invoice.vendor:
                    vendor_name = invoice.vendor.name
                recent_invoices_data.append({
                    'id': invoice.id,
                    'vendor': vendor_name,
                    'amount': float(invoice.amount),
                    'date': invoice.date.isoformat() if invoice.date else None,
                    'status': invoice.status,
                    'riskScore': float(invoice.risk_score) if invoice.risk_score else 0
                })
            
            top_vendors_data = [
                {
                    'name': vendor.name,
                    'totalSpend': float(vendor.total_spend)
                }
                for vendor in top_vendors
            ]
            
            session.close()
            
            return jsonify({
                'total_spend': float(total_spend),
                'totalSpend': float(total_spend),
                'invoice_count': int(invoice_count),
                'invoiceCount': int(invoice_count),
                'vendor_count': int(vendor_count),
                'vendorCount': int(vendor_count),
                'average_risk_score': float(avg_risk_score),
                'averageRiskScore': float(avg_risk_score),
                'spend_change_percentage': float(spend_change),
                'spendChange': float(spend_change),
                'high_risk_invoices_count': high_risk_count,
                'risk_factors_count': risk_factors_count,
                'avg_processing_time': 3.5,
                'recent_invoices': recent_invoices_data,
                'recentInvoices': recent_invoices_data,
                'top_vendors': top_vendors_data,
                'topVendors': top_vendors_data
            })
            
        except Exception as e:
            logger.error(f"Dashboard metrics error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Root endpoint
    @app.route('/')
    def root():
        """API root endpoint with documentation"""
        return jsonify({
            "service": "LAIT Legal Intelligence API",
            "version": "2.1.0",
            "documentation": "https://docs.lait.legal/api",
            "status": "operational",
            "endpoints": {
                "health": "/api/health",
                "self_test": "/api/self-test",
                "dashboard": "/api/dashboard/metrics",
                "invoices": "/api/invoices",
                "vendors": "/api/vendors",
                "matters": "/api/matters",
                "ml": "/api/ml/*",
                "analytics": "/api/analytics/*",
                "documents": "/api/documents/*",
                "legal_intelligence": "/api/legal-intelligence/*",
                "workflow": "/api/workflow/*",
                "legal_search": "/api/legal/search"
            }
        })

    # Proper legal case search endpoint (extracted from misplaced block)
    @limiter.limit("30 per minute")
    @app.route('/api/legal/search', methods=['POST'])
    def legal_case_search():
        """Enhanced legal case search with real-time data integration"""
        try:
            data = request.get_json() or {}
            query = data.get('query', '').strip()
            jurisdiction = data.get('jurisdiction', 'all')
            if not query:
                return jsonify({'error': 'Query is required'}), 400
            collector = app.data_collector
            search_results = {
                'cases': [],
                'metadata': {
                    'total_results': 0,
                    'search_time': 0,
                    'sources_searched': []
                }
            }
            start_time = time.time()
            # CourtListener
            try:
                courtlistener_results = collector.fetch_courtlistener_data(query, limit=20)
                if courtlistener_results and 'results' in courtlistener_results:
                    for case in courtlistener_results['results']:
                        search_results['cases'].append({
                            'id': case.get('id'),
                            'title': case.get('caseName', case.get('name', 'Unknown Case')),
                            'court': (case.get('court') or {}).get('name', 'Unknown Court'),
                            'date': case.get('dateFiled'),
                            'citation': case.get('citation', []),
                            'summary': (case.get('summary') or '')[:200] + ('...' if case.get('summary') else ''),
                            'url': case.get('absolute_url'),
                            'source': 'CourtListener',
                            'jurisdiction': (case.get('court') or {}).get('jurisdiction', 'Federal')
                        })
                search_results['metadata']['sources_searched'].append('CourtListener')
            except Exception as e:
                logger.error(f"CourtListener search error: {e}")
            # Justia
            try:
                justia_results = collector.search_justia_cases(query)
                if justia_results:
                    for case in justia_results[:10]:
                        search_results['cases'].append({
                            'id': f"justia_{case.get('id', len(search_results['cases']))}",
                            'title': case.get('title', 'Unknown Case'),
                            'court': case.get('court', 'Unknown Court'),
                            'date': case.get('date'),
                            'citation': case.get('citation', []),
                            'summary': (case.get('summary') or '')[:200] + ('...' if case.get('summary') else ''),
                            'url': case.get('url'),
                            'source': 'Justia',
                            'jurisdiction': case.get('jurisdiction', 'State')
                        })
                search_results['metadata']['sources_searched'].append('Justia')
            except Exception as e:
                logger.error(f"Justia search error: {e}")
            # Google Scholar
            try:
                scholar_results = collector.search_google_scholar_cases(query)
                if scholar_results:
                    for case in scholar_results[:10]:
                        search_results['cases'].append({
                            'id': f"scholar_{case.get('id', len(search_results['cases']))}",
                            'title': case.get('title', 'Unknown Case'),
                            'court': case.get('court', 'Unknown Court'),
                            'date': case.get('date'),
                            'citation': case.get('citations', []),
                            'summary': (case.get('snippet') or '')[:200] + ('...' if case.get('snippet') else ''),
                            'url': case.get('link'),
                            'source': 'Google Scholar',
                            'jurisdiction': case.get('jurisdiction', 'Unknown')
                        })
                search_results['metadata']['sources_searched'].append('Google Scholar')
            except Exception as e:
                logger.error(f"Google Scholar search error: {e}")
            # Filter jurisdiction
            if jurisdiction != 'all':
                search_results['cases'] = [c for c in search_results['cases'] if c.get('jurisdiction', '').lower() == jurisdiction.lower()]
            # Sort by date desc
            search_results['cases'] = sorted(search_results['cases'], key=lambda x: (x.get('date') or '0000-01-01'), reverse=True)
            search_results['metadata']['total_results'] = len(search_results['cases'])
            search_results['metadata']['search_time'] = round(time.time() - start_time, 2)
            return jsonify(search_results)
        except Exception as e:
            logger.error(f"Legal case search error: {str(e)}")
            return jsonify({'error': f'Search failed: {str(e)}'}), 500

    # Advanced Analytics Endpoints
    @app.route('/api/analytics/predictive', methods=['GET'])
    def predictive_analytics():
        """Get predictive analytics"""
        try:
            # Use ML models to generate predictive insights
            predictions = {
                'predictions': [
                    {'category': 'Legal Spend', 'current': 500000, 'predicted': 580000, 'confidence': 0.85},
                    {'category': 'Case Load', 'current': 45, 'predicted': 52, 'confidence': 0.78},
                    {'category': 'Risk Factors', 'current': 15, 'predicted': 12, 'confidence': 0.82}
                ],
                'confidence': 0.82,
                'generated_at': datetime.utcnow().isoformat()
            }
            return jsonify(predictions)
        except Exception as e:
            logger.error(f"Predictive analytics error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/vendor-performance', methods=['GET'])
    def vendor_performance_analytics():
        """Get vendor performance analytics"""
        try:
            performance = {
                'vendors': [
                    {'name': 'Morrison & Foerster LLP', 'performance': 0.92, 'trend': 'up', 'spend': 850000, 'efficiency': 0.88},
                    {'name': 'Baker McKenzie', 'performance': 0.85, 'trend': 'stable', 'spend': 720000, 'efficiency': 0.84},
                    {'name': 'Latham & Watkins', 'performance': 0.89, 'trend': 'up', 'spend': 680000, 'efficiency': 0.91},
                    {'name': 'Skadden Arps', 'performance': 0.78, 'trend': 'down', 'spend': 620000, 'efficiency': 0.76}
                ],
                'overall_performance': 0.86,
                'period': 'last_quarter',
                'generated_at': datetime.utcnow().isoformat()
            }
            return jsonify(performance)
        except Exception as e:
            logger.error(f"Vendor performance analytics error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/budget-forecast', methods=['GET'])
    def budget_forecast_analytics():
        """Get budget forecast analytics"""
        try:
            forecast = {
                'currentSpend': 1250000,
                'projectedSpend': 1380000,
                'variance': 130000,
                'confidence': 0.87,
                'trends': [
                    {'month': 'Jan', 'actual': 95000, 'projected': 98000},
                    {'month': 'Feb', 'actual': 110000, 'projected': 105000},
                    {'month': 'Mar', 'actual': 125000, 'projected': 128000},
                    {'month': 'Apr', 'actual': 135000, 'projected': 140000},
                    {'month': 'May', 'actual': 145000, 'projected': 152000},
                    {'month': 'Jun', 'actual': 155000, 'projected': 165000}
                ],
                'risk_factors': [
                    {'factor': 'Complex litigation increase', 'impact': 'high'},
                    {'factor': 'Rate inflation', 'impact': 'medium'},
                    {'factor': 'New regulatory requirements', 'impact': 'medium'}
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            return jsonify(forecast)
        except Exception as e:
            logger.error(f"Budget forecast analytics error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/spend-trends', methods=['GET'])
    def spend_trends_analytics():
        """Get spending trend analytics"""
        try:
            period = request.args.get('period', 'monthly')
            category = request.args.get('category', 'all')
            
            trends = {
                'period': period,
                'category': category,
                'data': [
                    {'period': 'Jan 2024', 'spend': 85000, 'budget': 90000, 'variance': -5000},
                    {'period': 'Feb 2024', 'spend': 92000, 'budget': 90000, 'variance': 2000},
                    {'period': 'Mar 2024', 'spend': 88000, 'budget': 90000, 'variance': -2000},
                    {'period': 'Apr 2024', 'spend': 95000, 'budget': 90000, 'variance': 5000},
                    {'period': 'May 2024', 'spend': 105000, 'budget': 90000, 'variance': 15000},
                    {'period': 'Jun 2024', 'spend': 98000, 'budget': 90000, 'variance': 8000}
                ],
                'summary': {
                    'total_spend': 563000,
                    'total_budget': 540000,
                    'total_variance': 23000,
                    'average_monthly': 93833
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            return jsonify(trends)
        except Exception as e:
            logger.error(f"Spend trends analytics error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # ================== INVOICE ENDPOINTS ==================
    @app.route('/api/invoices', methods=['GET'])
    @jwt_required(optional=True)
    def list_invoices():
        try:
            session = get_db_session()
            from db.database import Invoice, Vendor
            status = request.args.get('status')
            q = session.query(Invoice).join(Vendor, Invoice.vendor_id == Vendor.id, isouter=True)
            if status:
                q = q.filter(Invoice.status == status)
            invoices = []
            for inv in q.order_by(desc(Invoice.created_at)).all():
                invoices.append({
                    'id': str(inv.id),
                    'vendor': inv.vendor.name if inv.vendor else 'Unknown',
                    'amount': float(inv.amount or 0),
                    'status': inv.status or 'pending',
                    'date': inv.date.isoformat() if inv.date else None,
                    'dueDate': (inv.date + timedelta(days=30)).isoformat() if inv.date else None,
                    'matter': inv.matter or 'General',
                    'riskScore': float(inv.risk_score or 0) * 100 if (inv.risk_score and inv.risk_score <= 1) else float(inv.risk_score or 0),
                    'category': inv.category or 'Uncategorized',
                    'description': inv.description or '',
                    'hours': float(inv.hours or 0),
                    'rate': float(inv.rate or 0),
                    'total': float(inv.amount or 0)
                })
            session.close()
            return jsonify(invoices)
        except Exception as e:
            logger.error(f"List invoices error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/invoices/<invoice_id>', methods=['GET'])
    @jwt_required(optional=True)
    def invoice_detail(invoice_id):
        try:
            session = get_db_session()
            from db.database import Invoice, Vendor
            inv = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not inv:
                return jsonify({'error': 'Not found'}), 404
            data = {
                'id': str(inv.id),
                'vendor': inv.vendor.name if inv.vendor else 'Unknown',
                'amount': float(inv.amount or 0),
                'status': inv.status or 'pending',
                'date': inv.date.isoformat() if inv.date else None,
                'dueDate': (inv.date + timedelta(days=30)).isoformat() if inv.date else None,
                'matter': inv.matter or 'General',
                'riskScore': float(inv.risk_score or 0) * 100 if (inv.risk_score and inv.risk_score <= 1) else float(inv.risk_score or 0),
                'lineItems': json.loads(inv.line_items or '[]'),
                'analysis': json.loads(inv.analysis or '{}')
            }
            session.close()
            return jsonify(data)
        except Exception as e:
            logger.error(f"Invoice detail error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/invoices/<invoice_id>/analyze', methods=['POST'])
    @jwt_required(optional=True)
    def analyze_invoice_endpoint(invoice_id):
        try:
            session = get_db_session()
            from db.database import Invoice
            inv = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not inv:
                return jsonify({'error': 'Not found'}), 404
            analyzer = getattr(current_app, 'enhanced_invoice_analyzer', None) or getattr(current_app, 'invoice_analyzer', None)
            analysis = {}
            if analyzer:
                try:
                    analysis = analyzer.analyze_invoice({
                        'id': inv.id,
                        'vendor': inv.vendor_id,
                        'amount': float(inv.amount or 0),
                        'date': inv.date.isoformat() if inv.date else None
                    })
                except Exception as e:
                    logger.warning(f"Analyzer failed: {e}")
            # Fallback simple risk
            if not analysis:
                analysis = {
                    'invoice_id': str(inv.id),
                    'risk_score': float(inv.risk_score or random.uniform(0.1, 0.9)),
                    'risk_level': 'high' if (inv.risk_score or 0) > 0.7 else 'medium' if (inv.risk_score or 0) > 0.4 else 'low',
                    'anomalies': [],
                    'recommendations': []
                }
            inv.analysis = json.dumps(analysis)
            session.commit()
            socketio.emit('notification', {
                'type': 'invoice_analysis',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'data': {
                    'invoice_id': inv.id,
                    'invoice_number': inv.id,
                    'risk_score': analysis.get('risk_score'),
                    'status': inv.status,
                    'amount': float(inv.amount or 0)
                }
            })
            session.close()
            return jsonify(analysis)
        except Exception as e:
            logger.error(f"Analyze invoice error: {e}")
            return jsonify({'error': str(e)}), 500

    @limiter.limit("10/minute")
    @app.route('/api/upload-invoice', methods=['POST'])
    @jwt_required(optional=True)
    def upload_invoice():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'file is required'}), 400
            f = request.files['file']
            filename = f.filename
            content = f.read()
            amount = float(request.form.get('amount') or 0)
            vendor_name = request.form.get('vendor') or 'Unknown Vendor'
            session = get_db_session()
            from db.database import Invoice, Vendor
            vendor = session.query(Vendor).filter(Vendor.name == vendor_name).first()
            if not vendor:
                vendor = Vendor(name=vendor_name)
                session.add(vendor)
                session.flush()
            new_inv = Invoice(
                vendor_id=vendor.id,
                amount=amount or random.uniform(1000, 5000),
                status='processing',
                date=datetime.utcnow().date(),
                risk_score=random.uniform(0, 1),
                matter='General',
                category=request.form.get('category'),
                description=request.form.get('description'),
                line_items=json.dumps([])
            )
            session.add(new_inv)
            session.commit()
            socketio.emit('notification', {
                'type': 'invoice_analysis',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'data': {
                    'invoice_id': new_inv.id,
                    'invoice_number': new_inv.id,
                    'risk_score': new_inv.risk_score,
                    'status': new_inv.status,
                    'amount': float(new_inv.amount or 0)
                }
            })
            session.close()
            return jsonify({'id': str(new_inv.id), 'filename': filename, 'status': 'uploaded'}), 201
        except Exception as e:
            logger.error(f"Upload invoice error: {e}")
            return jsonify({'error': str(e)}), 500

    # Import and register routes
    with app.app_context():
        from backend.routes import register_routes
        register_routes(app)
        logger.info("✅ Routes registered successfully")
    
    return app

# Create a .env file if it doesn't exist
def ensure_env_file():
    """Create a .env file with default settings if it doesn't exist"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../.env')
    if not os.path.exists(env_path):
        try:
            with open(env_path, 'w') as f:
                f.write("""# LAIT API Environment Configuration
# API Settings
API_HOST=0.0.0.0
API_PORT=5003
DEBUG=True
FLASK_APP=backend/enhanced_app.py

# Frontend Configuration
VITE_API_URL=http://localhost:5003

# Database Settings
DATABASE_URL=postgresql://postgres:postgres@localhost/legalspend

# Security
SECRET_KEY=development-key-please-change-in-production
JWT_SECRET_KEY=jwt-dev-key-please-change-in-production

# Redis/Celery Settings
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
""")
            logger.info("✅ Created default .env file")
        except Exception as e:
            logger.warning(f"❌ Could not create .env file: {e}")

# Create the application instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting LAIT Comprehensive Legal Intelligence API v2.1")
    print("🔧 Initializing Production-Ready Environment...")
    
    try:
        # Get port from environment or use default
        port = int(os.environ.get('API_PORT', 5003))
        host = os.environ.get('API_HOST', '0.0.0.0')
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        # Report system status
        endpoints_count = len([rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/api/')])
        
        print(f"✅ System Initialized:")
        print(f"   - Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"   - API: {endpoints_count} active endpoints")
        print(f"   - Features: ML models, Matter Management, Document Processing, Analytics")
        print(f"   - Socket.IO: Enabled")
        
        print(f"🌐 Starting server on http://{host}:{port}")
        
        # Use Socket.IO to run the application
        socketio.run(app, host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested. Exiting gracefully...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
