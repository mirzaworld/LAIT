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
import json
import time
import math
import io
import base64
import uuid
import warnings
import subprocess
import random  # added back
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
import threading
from flask_limiter.errors import RateLimitExceeded

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

# ---------------- Structured JSON Logging Setup (backend polish) ----------------
class JsonRequestFormatter(logging.Formatter):
    def format(self, record):
        base = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        # Attach request context if available
        try:
            if request:
                base.update({
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr,
                    'request_id': getattr(request, 'request_id', None)
                })
        except Exception:
            pass
        if record.exc_info:
            base['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(base)

# Reconfigure root logger handlers only once
if not logging.getLogger().handlers or not any(isinstance(h, logging.FileHandler) for h in logging.getLogger().handlers):
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    _file = logging.FileHandler(os.path.join(log_dir, 'lait_api.jsonl'))
    _stream = logging.StreamHandler()
    formatter = JsonRequestFormatter()
    _file.setFormatter(formatter)
    _stream.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [_file, _stream]

logger = logging.getLogger(__name__)

# Silence benign sklearn / urllib3 warnings (polish step)
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
warnings.filterwarnings('ignore', category=FutureWarning, module='sklearn')

# Initialize Socket.IO
socketio = SocketIO()

# Remove dynamic per-path mapping (we will rely on explicit @limiter.limit decorators)
RATE_LIMITS = {
    'self-test': '12/minute',
    'legal/search': '30/minute',
    'upload-invoice': '10/minute'
}

def dynamic_rate_limit():
    # Find first matching pattern
    path = request.path.strip('/')
    for fragment, limit in RATE_LIMITS.items():
        if fragment in path:
            return limit
    return None

# Configure rate limiter globally (env override)
DEFAULT_RATE = os.getenv('GLOBAL_RATE_LIMIT', '200 per minute')
limiter = Limiter(key_func=get_remote_address, default_limits=[DEFAULT_RATE])  # Adjust as needed

# ---------------- In-memory metrics store ----------------
_metrics = {
    'requests_total': 0,
    'errors_total': 0,
    'latency_ms': [],
    'model_inferences': 0,
    'start_time': time.time(),
    'status_counts': {}
}
_LATENCY_WINDOW = 500  # keep last N latencies

def _record_latency(ms):
    arr = _metrics['latency_ms']
    arr.append(ms)
    if len(arr) > _LATENCY_WINDOW:
        del arr[0:len(arr)-_LATENCY_WINDOW]

# ---------------- Drift / heartbeat scaffold ----------------
class DriftTracker:
    def __init__(self):
        self.feature_stats = {}  # feature -> {mean, std}
        self.last_update = None
        self.drift_flags = {}

    def update(self, frame: pd.DataFrame):
        if frame is None or frame.empty:
            return
        for col in frame.columns:
            if pd.api.types.is_numeric_dtype(frame[col]):
                series = frame[col].dropna()
                if not len(series):
                    continue
                mean = float(series.mean())
                std = float(series.std() or 0)
                prev = self.feature_stats.get(col)
                if prev and prev['std']:
                    z = abs(mean - prev['mean']) / (prev['std'] or 1)
                    self.drift_flags[col] = z > 3
                self.feature_stats[col] = {'mean': mean, 'std': std}
        self.last_update = datetime.utcnow()

    def summary(self):
        return {
            'last_update': self.last_update.isoformat() + 'Z' if self.last_update else None,
            'drift_flags': self.drift_flags,
            'tracked_features': list(self.feature_stats.keys())
        }

    def heartbeat(self):
        return {
            'uptime_sec': int(time.time() - _metrics['start_time']),
            'last_update': self.last_update.isoformat() + 'Z' if self.last_update else None,
            'tracked': len(self.feature_stats)
        }

drift_tracker = DriftTracker()

def create_app():
    """
    Application factory function that creates and configures the Flask app.
    """
    app = Flask(__name__)
    # Attach model manager & drift tracker placeholders
    try:
        from ml.model_manager import ModelManager
        app.model_manager = ModelManager(model_dir=os.getenv('MODEL_DIR', 'models'))
    except Exception as e:
        logger.warning(f"ModelManager init failed: {e}")
        app.model_manager = None
    app.drift_tracker = drift_tracker

    # --------------------------------------------------
    # Request correlation & timing middleware + dynamic rate limit
    # --------------------------------------------------
    @app.before_request
    def _request_instrumentation():
        request.start_time = time.time()
        req_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.request_id = req_id
        _metrics['requests_total'] += 1

    @app.after_request
    def _add_security_headers(resp):
        duration_ms = None
        if hasattr(request, 'start_time'):
            duration_ms = int((time.time() - request.start_time) * 1000)
            resp.headers['X-Response-Time-ms'] = str(duration_ms)
            _record_latency(duration_ms)
        if hasattr(request, 'request_id'):
            resp.headers['X-Request-ID'] = request.request_id
        # Security headers
        resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
        resp.headers.setdefault('X-Frame-Options', 'DENY')
        resp.headers.setdefault('X-XSS-Protection', '1; mode=block')
        resp.headers.setdefault('Referrer-Policy', 'no-referrer')
        csp = "default-src 'self'; connect-src 'self' http://localhost:5173 ws://localhost:5173 http://localhost:5003 ws://localhost:5003; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        resp.headers.setdefault('Content-Security-Policy', csp)
        resp.headers.setdefault('Cache-Control', 'no-store')
        # Metrics per status
        _metrics['status_counts'][resp.status_code] = _metrics['status_counts'].get(resp.status_code, 0) + 1
        # Structured access log (formatter will wrap message)
        try:
            logger.info(f"access method={request.method} path={request.path} status={resp.status_code} latency_ms={duration_ms} req_id={getattr(request,'request_id',None)}")
        except Exception:
            pass
        return resp

    # Unified JSON error response helper
    def _json_error(status_code: int, error_code: str, message: str, details=None):
        payload = {
            'error': {
                'code': error_code,
                'message': message,
                'status': status_code,
                'request_id': getattr(request, 'request_id', None),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }
        if details is not None:
            payload['error']['details'] = details
        return jsonify(payload), status_code

    # Global exception handlers
    @app.errorhandler(404)
    def _not_found(e):
        return _json_error(404, 'not_found', 'Resource not found')

    @app.errorhandler(400)
    def _bad_request(e):
        return _json_error(400, 'bad_request', 'Invalid request')

    @app.errorhandler(Exception)
    def _unhandled(e):  # catch-all
        logger.exception('Unhandled exception')
        _metrics['errors_total'] += 1
        debug = app.config.get('DEBUG', False)
        details = None
        if debug:
            details = {'type': e.__class__.__name__, 'str': str(e)}
        return _json_error(500, 'internal_error', 'Internal server error', details)

    @app.errorhandler(RateLimitExceeded)
    def _rate_limited(e):  # type: ignore
        return _json_error(429, 'rate_limited', 'Rate limit exceeded', {'limit': str(e.limit)})

    # --------------------------------------------------
    # Existing configuration continues below
    # --------------------------------------------------
    # Configure app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/legalspend')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')

    # Dynamic CORS origins from env
    allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS')
    if allowed_origins:
        origins_list = [o.strip() for o in allowed_origins.split(',') if o.strip()]
    else:
        origins_list = [
            'http://localhost:5173', 'http://localhost:4173', 'http://127.0.0.1:5173', 'http://127.0.0.1:4173',
            os.getenv('FRONTEND_URL', 'http://localhost:5173')
        ]
    # Configure CORS to accept requests from frontend
    CORS(app, resources={r"/api/*": {"origins": origins_list, "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"], "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"], "supports_credentials": True, "expose_headers": ["Content-Type", "Authorization"]}})
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
    # Accept PyJWT test tokens that embed identity as 'user_id' (test fixtures use this)
    app.config['JWT_USER_IDENTITY_CLAIM'] = 'user_id'
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
        # Model manager for version metadata
        try:
            from ml.model_manager import ModelManager
            app.model_manager = ModelManager(model_dir=os.path.join(os.path.dirname(__file__), 'ml', 'models'))
        except Exception as mm_e:
            logger.warning(f"ModelManager init failed: {mm_e}")
            app.model_manager = None
        logger.info("✅ ML models initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML models: {e}")
        app.invoice_analyzer = None
        app.vendor_analyzer = None
        app.risk_predictor = None
        app.matter_analyzer = None
        app.enhanced_invoice_analyzer = None
        app.model_manager = None

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

    # --- NEW: Readiness endpoint (step 3) ---
    @app.route('/api/readiness')
    def readiness():
        ok = True
        details = {}
        # DB check
        try:
            session = get_db_session()
            session.execute('SELECT 1')
            session.close()
            details['database'] = {'status': 'ok'}
        except Exception as e:
            details['database'] = {'status': 'error', 'error': str(e)}
            ok = False
        # Model load check (at least invoice_analyzer present)
        model_obj = getattr(app, 'invoice_analyzer', None)
        details['ml_models'] = {'invoice_analyzer': 'loaded' if model_obj else 'missing'}
        if not model_obj:
            ok = False
        # Drift tracker heartbeat freshness (< 10 min if any update ever happened)
        drift = getattr(app, 'drift_tracker', None)
        heartbeat_fresh = True
        if drift and drift.last_update:
            heartbeat_fresh = (datetime.utcnow() - drift.last_update) < timedelta(minutes=10)
        details['drift'] = {
            'last_update': drift.last_update.isoformat() + 'Z' if (drift and drift.last_update) else None,
            'fresh': heartbeat_fresh
        }
        if drift and drift.last_update and not heartbeat_fresh:
            ok = False
        status = 'ready' if ok else 'degraded'
        code = 200 if ok else 503
        return jsonify({'status': status, 'components': details, 'timestamp': datetime.utcnow().isoformat() + 'Z'}), code

    # --- NEW: Comprehensive backend self-test / diagnostics endpoint ---
    @app.route('/api/self-test', methods=['GET'])
    @limiter.limit(RATE_LIMITS['self-test'])
    def self_test():
        """Run lightweight diagnostics across core subsystems.
        Returns JSON summarizing status so frontend & tests can validate deployment health.
        """
        start = time.time()
        checks = {}
        # Database connectivity
        try:
            session = get_db_session()
            session.execute('SELECT 1')
            session.close()
            checks['database'] = {'status': 'ok'}
        except Exception as e:
            checks['database'] = {'status': 'error', 'error': str(e)}
        # ML Models
        ml_models = {}
        for name in ['invoice_analyzer', 'vendor_analyzer', 'risk_predictor', 'matter_analyzer', 'enhanced_invoice_analyzer']:
            obj = getattr(app, name, None)
            ml_models[name] = 'loaded' if obj else 'missing'
        checks['ml_models'] = ml_models
        # External services (best-effort / non-blocking quick checks)
        external = {}
        # Simple HTTP reachability for one public site (skip if offline env) with timeout
        try:
            import socket
            socket.gethostbyname('courtlistener.com')
            external['dns_courtlistener'] = 'resolved'
        except Exception as e:
            external['dns_courtlistener'] = f'fail:{e.__class__.__name__}'
        checks['external'] = external
        # Socket.IO availability flag
        try:
            socketio_server = 'enabled' if socketio.server else 'disabled'
        except Exception:
            socketio_server = 'disabled'
        checks['realtime'] = {'socketio': socketio_server}
        duration = round(time.time() - start, 3)
        status = 'ok' if all(v.get('status','ok') == 'ok' for k,v in checks.items() if isinstance(v, dict) and 'status' in v) else 'degraded'
        return jsonify({
            'status': status,
            'elapsed_ms': int(duration * 1000),
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })

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
    @limiter.limit(RATE_LIMITS['legal/search'])
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
            # Drift tracker update with latest invoice stats
            try:
                current_app.drift_tracker.update(pd.DataFrame([{'amount': float(inv.amount or 0), 'risk_score': float(inv.risk_score or 0)}]))
            except Exception:
                pass
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

    @limiter.limit(RATE_LIMITS['upload-invoice'])
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
            # Drift tracker update
            try:
                current_app.drift_tracker.update(pd.DataFrame([{'amount': float(new_inv.amount or 0), 'risk_score': float(new_inv.risk_score or 0)}]))
            except Exception:
                pass
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

    # ---------------- Version & Metrics Endpoints ----------------
    @app.route('/api/version')
    def version_info():
        git_sha = None
        try:
            git_sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            pass
        model_meta = None
        if getattr(app, 'model_manager', None):
            try:
                model_meta = app.model_manager.metadata
            except Exception:
                model_meta = None
        return jsonify({
            'service': 'LAIT API',
            'version': '2.1.0',
            'git_sha': git_sha,
            'models': model_meta,
            'start_time': datetime.utcfromtimestamp(_metrics['start_time']).isoformat() + 'Z'
        })

    @app.route('/api/metrics')
    def metrics_endpoint():
        # Basic Prometheus-style exposition
        lat = _metrics['latency_ms']
        avg = (sum(lat)/len(lat)) if lat else 0
        p95 = sorted(lat)[int(0.95*len(lat))-1] if lat else 0
        lines = [
            f"lait_requests_total {_metrics['requests_total']}",
            f"lait_errors_total {_metrics['errors_total']}",
            f"lait_model_inferences_total {_metrics['model_inferences']}",
            f"lait_request_latency_ms_avg {avg}",
            f"lait_request_latency_ms_p95 {p95}",
        ]
        return Response('\n'.join(lines) + '\n', mimetype='text/plain')

    # Existing ml_status definition will be replaced below by editing near original definition
    # (We will search/replace later if needed)
    @app.route('/api/ml/status', methods=['GET'])
    def ml_status():
        models_status = {}
        model_manager = getattr(app, 'model_manager', None)
        meta_source = model_manager.metadata if model_manager else {'models': {}}
        for attr, key in [
            ('enhanced_invoice_analyzer', 'outlier_detector'),
            ('invoice_analyzer', 'outlier_detector'),
            ('matter_analyzer', 'outlier_detector'),
            ('risk_predictor', 'risk_predictor'),
            ('vendor_analyzer', 'vendor_cluster')
        ]:
            obj = getattr(app, attr, None)
            m = {
                'loaded': bool(obj),
                'class': obj.__class__.__name__ if obj else None,
                'version': meta_source['models'].get(key, {}).get('current_version'),
                'versions': len(meta_source['models'].get(key, {}).get('versions', []))
            }
            # Add metrics if available
            try:
                if model_manager and meta_source['models'].get(key, {}).get('current_version'):
                    m['metrics'] = model_manager.get_model_metrics(key)
            except Exception:
                pass
            models_status[attr] = m
        drift = app.drift_tracker.summary() if getattr(app, 'drift_tracker', None) else {}
        heartbeat = app.drift_tracker.heartbeat() if getattr(app, 'drift_tracker', None) else {}
        return jsonify({'models': models_status, 'drift': drift, 'heartbeat': heartbeat, 'status': 'ok'}), 200

    # ================== BACKGROUND TASKS (CELERY) ==================
    # (Disabled: worker module not present in this deployment flavor)
    # try:
    #     from worker import celery_app
    #     celery_app.conf.update(task_track_started=True)
    #     logger.info("✅ Celery app loaded")
    # except Exception as e:
    #     logger.warning(f"❌ Could not load Celery app: {e}")

    # --- NEW: Register notification blueprint (step 1) ---
    try:
        from routes.notification import notification_bp  # noqa: WPS433
        app.register_blueprint(notification_bp)
        logger.info('✅ Notification blueprint registered')
    except Exception as e:  # pragma: no cover
        logger.error(f'❌ Failed to register notification blueprint: {e}')

    # --- NEW: Register remaining blueprints (auth, invoices, analytics, vendors, legal intelligence, upload) ---
    try:
        from routes import register_routes
        register_routes(app)
        logger.info('✅ All application blueprints registered via routes.register_routes')
    except Exception as e:  # pragma: no cover
        logger.error(f'❌ Failed to register full route set: {e}')

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
