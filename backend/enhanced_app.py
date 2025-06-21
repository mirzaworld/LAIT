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
from flask import Flask, request, jsonify, send_file, current_app
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from sqlalchemy import func, desc
from db.database import User, Invoice, Vendor, SessionLocal, init_db
from models.db_models import AuditLog

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
                os.getenv("FRONTEND_URL", "http://localhost:5173")
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
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
            from db.database import get_db_session
            from models.db_models import Invoice, Vendor
            
            session = get_db_session()
            
            # Get basic metrics
            total_spend = session.query(func.sum(Invoice.amount)).scalar() or 0
            invoice_count = session.query(func.count(Invoice.id)).scalar() or 0
            vendor_count = session.query(func.count(func.distinct(Invoice.vendor_id))).scalar() or 0
            avg_risk_score = session.query(func.avg(Invoice.risk_score)).scalar() or 0
            
            # Get recent invoices
            recent_invoices = session.query(Invoice)\
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
            
            session.close()
            
            return jsonify({
                'totalSpend': float(total_spend),
                'invoiceCount': int(invoice_count),
                'vendorCount': int(vendor_count),
                'averageRiskScore': float(avg_risk_score),
                'spendChange': float(spend_change),
                'recentInvoices': [
                    {
                        'id': invoice.id,
                        'vendor': invoice.vendor.name if invoice.vendor else 'Unknown',
                        'amount': float(invoice.amount),
                        'date': invoice.date.isoformat() if invoice.date else None,
                        'status': invoice.status,
                        'riskScore': float(invoice.risk_score) if invoice.risk_score else 0
                    }
                    for invoice in recent_invoices
                ],
                'topVendors': [
                    {
                        'name': vendor.name,
                        'totalSpend': float(vendor.total_spend)
                    }
                    for vendor in top_vendors
                ]
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
                "dashboard": "/api/dashboard/metrics",
                "invoices": "/api/invoices",
                "vendors": "/api/vendors",
                "matters": "/api/matters",
                "ml": "/api/ml/*",
                "analytics": "/api/analytics/*",
                "documents": "/api/documents/*",
                "legal_intelligence": "/api/legal-intelligence/*",
                "workflow": "/api/workflow/*"
            }
        })

    # Import and register routes
    with app.app_context():
        from routes import register_routes
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
