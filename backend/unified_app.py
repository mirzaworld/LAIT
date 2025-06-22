"""
LAIT Unified Legal Intelligence API
Consolidated from multiple app versions with consistent imports and authentication
"""

import os
import sys
import logging
import json
import time
import io
import base64
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, make_response, Response
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, desc

# Load environment variables first
load_dotenv()

# Add current directory to Python path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'lait_unified.log')

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
    Unified application factory function
    """
    app = Flask(__name__)
    
    # Configure app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/legalspend')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)
    
    # Configure CORS for all environments
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",  # Vite dev server
                "http://localhost:4173",  # Vite preview
                "http://127.0.0.1:5173",
                "http://127.0.0.1:4173",
                "http://localhost:3000",  # Create React App
                "http://localhost:8080",  # Alternative dev port
                os.getenv("FRONTEND_URL", "http://localhost:5173")
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Add preflight handler
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', 'http://localhost:5173'))
            response.headers.add('Access-Control-Allow-Headers', "Content-Type, Authorization, Accept, Origin, X-Requested-With")
            response.headers.add('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS, HEAD")
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize database
    try:
        from db.database import init_db, get_db_session, User, Invoice, Vendor
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        # Create fallback database models
        User = None
        Invoice = None
        Vendor = None
    
    # Initialize Socket.IO
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    @socketio.on('connect')
    def handle_connect():
        logger.info("Client connected to Socket.IO")

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info("Client disconnected from Socket.IO")
    
    # Initialize ML models (optional)
    try:
        from models.invoice_analyzer import InvoiceAnalyzer
        from models.vendor_analyzer import VendorAnalyzer
        from models.risk_predictor import RiskPredictor
        app.invoice_analyzer = InvoiceAnalyzer()
        app.vendor_analyzer = VendorAnalyzer()
        app.risk_predictor = RiskPredictor()
        logger.info("✅ ML models initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ ML models not available: {e}")
        app.invoice_analyzer = None
        app.vendor_analyzer = None
        app.risk_predictor = None
    
    # ============ API ROUTES ============
    
    @app.route('/')
    def root():
        """API root endpoint"""
        return jsonify({
            "service": "LAIT Legal Intelligence API",
            "version": "3.0.0-unified",
            "status": "operational",
            "features": [
                "Authentication & Authorization",
                "Invoice Management",
                "Vendor Analytics", 
                "ML-Powered Risk Assessment",
                "Legal Intelligence Search",
                "Dashboard Analytics",
                "Document Processing"
            ],
            "endpoints": {
                "health": "/api/health",
                "auth": "/api/auth/*",
                "dashboard": "/api/dashboard/metrics",
                "invoices": "/api/invoices",
                "vendors": "/api/vendors",
                "analytics": "/api/analytics/*"
            }
        })
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy", 
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected" if User else "disconnected",
            "ml_models": "loaded" if app.invoice_analyzer else "unavailable"
        })
    
    # ============ AUTHENTICATION ROUTES ============
    
    def authenticate_user(email, password):
        """Authenticate user by email and password"""
        # Development fallback authentication - always available
        demo_credentials = [
            ('admin@lait.com', 'admin123'),
            ('demo@lait.com', 'demo123'),
            ('admin@lait.demo', 'demo'),
            ('demo', 'demo')
        ]
        
        for demo_email, demo_pass in demo_credentials:
            if email == demo_email and password == demo_pass:
                return {
                    'id': 1,
                    'email': email,
                    'first_name': 'Demo',
                    'last_name': 'User',
                    'role': 'admin'
                }
        
        # Try database authentication if available
        if not User:
            return None
        
        try:
            session = get_db_session()
            user = session.query(User).filter_by(email=email).first()
            
            if not user:
                return None
                
            if not check_password_hash(user.password_hash, password):
                return None
                
            return user
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
        finally:
            if 'session' in locals():
                session.close()
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Authenticate user and return JWT token"""
        try:
            data = request.json
            
            if not data or 'email' not in data or 'password' not in data:
                return jsonify({'message': 'Missing email or password'}), 400
            
            email = data.get('email')
            password = data.get('password')
            
            user = authenticate_user(email, password)
            
            if not user:
                return jsonify({'message': 'Invalid credentials'}), 401
            
            # Handle both dict and object user types
            if isinstance(user, dict):
                user_id = user['id']
                user_role = user['role']
                user_data = user
            else:
                user_id = user.id
                user_role = user.role
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            
            # Create access token
            access_token = create_access_token(
                identity=user_id,
                additional_claims={'role': user_role}
            )
            
            return jsonify({
                'token': access_token,
                'user': user_data
            })
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return jsonify({'message': 'Login failed', 'error': str(e)}), 500
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Register a new user"""
        try:
            data = request.json
            
            if not data or 'email' not in data or 'password' not in data:
                return jsonify({'message': 'Missing required fields'}), 400

            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            
            if not User:
                return jsonify({'message': 'Registration not available in demo mode'}), 503
            
            session = get_db_session()
            
            # Check if user exists
            existing_user = session.query(User).filter_by(email=email).first()
            if existing_user:
                return jsonify({'message': 'User already exists'}), 409
            
            # Create new user
            new_user = User(
                email=email,
                password_hash=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                role='user'
            )
            
            session.add(new_user)
            session.commit()
            
            # Generate token
            access_token = create_access_token(
                identity=new_user.id,
                additional_claims={'role': new_user.role}
            )
            
            user_data = {
                'id': new_user.id,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'role': new_user.role
            }
            
            return jsonify({
                'message': 'User registered successfully',
                'token': access_token,
                'user': user_data
            }), 201
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return jsonify({'message': 'Registration failed', 'error': str(e)}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    # ============ DASHBOARD ROUTES ============
    
    @app.route('/api/dashboard/metrics')
    def dashboard_metrics():
        """Dashboard metrics endpoint"""
        try:
            if not User or not Invoice or not Vendor:
                # Return mock data for demo mode
                return jsonify({
                    'total_spend': 1250000.0,
                    'totalSpend': 1250000.0,
                    'invoice_count': 150,
                    'invoiceCount': 150,
                    'vendor_count': 25,
                    'vendorCount': 25,
                    'average_risk_score': 0.35,
                    'averageRiskScore': 0.35,
                    'spend_change_percentage': 12.5,
                    'spendChange': 12.5,
                    'high_risk_invoices_count': 8,
                    'risk_factors_count': 15,
                    'avg_processing_time': 3.2,
                    'recent_invoices': [
                        {'id': 1, 'vendor': 'Morrison & Foerster LLP', 'amount': 45750.0, 'date': '2024-01-15', 'status': 'approved', 'riskScore': 0.25},
                        {'id': 2, 'vendor': 'Baker McKenzie', 'amount': 32100.0, 'date': '2024-01-14', 'status': 'pending', 'riskScore': 0.15},
                        {'id': 3, 'vendor': 'Latham & Watkins', 'amount': 67800.0, 'date': '2024-01-13', 'status': 'approved', 'riskScore': 0.45}
                    ],
                    'recentInvoices': [
                        {'id': 1, 'vendor': 'Morrison & Foerster LLP', 'amount': 45750.0, 'date': '2024-01-15', 'status': 'approved', 'riskScore': 0.25},
                        {'id': 2, 'vendor': 'Baker McKenzie', 'amount': 32100.0, 'date': '2024-01-14', 'status': 'pending', 'riskScore': 0.15},
                        {'id': 3, 'vendor': 'Latham & Watkins', 'amount': 67800.0, 'date': '2024-01-13', 'status': 'approved', 'riskScore': 0.45}
                    ],
                    'top_vendors': [
                        {'name': 'Morrison & Foerster LLP', 'totalSpend': 285000.0},
                        {'name': 'Baker McKenzie', 'totalSpend': 198000.0},
                        {'name': 'Latham & Watkins', 'totalSpend': 175000.0}
                    ],
                    'topVendors': [
                        {'name': 'Morrison & Foerster LLP', 'totalSpend': 285000.0},
                        {'name': 'Baker McKenzie', 'totalSpend': 198000.0},
                        {'name': 'Latham & Watkins', 'totalSpend': 175000.0}
                    ]
                })
            
            # Real database metrics
            session = get_db_session()
            
            total_spend = session.query(func.sum(Invoice.amount)).scalar() or 0
            invoice_count = session.query(func.count(Invoice.id)).scalar() or 0
            vendor_count = session.query(func.count(func.distinct(Invoice.vendor_id))).scalar() or 0
            avg_risk_score = session.query(func.avg(Invoice.risk_score)).scalar() or 0
            
            recent_invoices = session.query(Invoice)\
                .join(Vendor, Invoice.vendor_id == Vendor.id, isouter=True)\
                .order_by(desc(Invoice.created_at))\
                .limit(5)\
                .all()
            
            top_vendors = session.query(
                Vendor.name,
                func.sum(Invoice.amount).label('total_spend')
            ).join(Invoice)\
             .group_by(Vendor.name)\
             .order_by(desc('total_spend'))\
             .limit(5)\
             .all()
            
            # Process data
            recent_invoices_data = []
            for invoice in recent_invoices:
                vendor_name = invoice.vendor.name if invoice.vendor else 'Unknown'
                recent_invoices_data.append({
                    'id': invoice.id,
                    'vendor': vendor_name,
                    'amount': float(invoice.amount),
                    'date': invoice.date.isoformat() if invoice.date else None,
                    'status': invoice.status,
                    'riskScore': float(invoice.risk_score) if invoice.risk_score else 0
                })
            
            top_vendors_data = [
                {'name': vendor.name, 'totalSpend': float(vendor.total_spend)}
                for vendor in top_vendors
            ]
            
            return jsonify({
                'total_spend': float(total_spend),
                'totalSpend': float(total_spend),
                'invoice_count': int(invoice_count),
                'invoiceCount': int(invoice_count),
                'vendor_count': int(vendor_count),
                'vendorCount': int(vendor_count),
                'average_risk_score': float(avg_risk_score),
                'averageRiskScore': float(avg_risk_score),
                'spend_change_percentage': 12.5,
                'spendChange': 12.5,
                'high_risk_invoices_count': 8,
                'risk_factors_count': 15,
                'avg_processing_time': 3.2,
                'recent_invoices': recent_invoices_data,
                'recentInvoices': recent_invoices_data,
                'top_vendors': top_vendors_data,
                'topVendors': top_vendors_data
            })
            
        except Exception as e:
            logger.error(f"Dashboard metrics error: {str(e)}")
            return jsonify({'error': str(e)}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    # ============ ANALYTICS ROUTES ============
    
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
    
    @app.route('/api/analytics/vendor-performance', methods=['GET'])
    def vendor_performance_analytics():
        """Get vendor performance analytics"""
        try:
            performance = {
                'vendors': [
                    {'name': 'Morrison & Foerster LLP', 'performance': 0.92, 'trend': 'up', 'spend': 850000, 'efficiency': 0.88},
                    {'name': 'Baker McKenzie', 'performance': 0.85, 'trend': 'stable', 'spend': 720000, 'efficiency': 0.84},
                    {'name': 'Latham & Watkins', 'performance': 0.89, 'trend': 'up', 'spend': 680000, 'efficiency': 0.91},
                    {'name': 'White & Case', 'performance': 0.82, 'trend': 'stable', 'spend': 640000, 'efficiency': 0.79},
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
    
    # ============ VENDOR ROUTES ============
    
    @app.route('/api/vendors', methods=['GET'])
    def get_vendors():
        """Get all vendors"""
        try:
            if not Vendor:
                # Mock data for demo
                return jsonify([
                    {"id": 1, "name": "Morrison & Foerster LLP", "industry_category": "AmLaw 100", "status": "active"},
                    {"id": 2, "name": "Baker McKenzie", "industry_category": "Global", "status": "active"},
                    {"id": 3, "name": "Latham & Watkins", "industry_category": "AmLaw 100", "status": "active"},
                    {"id": 4, "name": "White & Case", "industry_category": "Global", "status": "active"},
                    {"id": 5, "name": "Skadden Arps", "industry_category": "AmLaw 50", "status": "active"}
                ])
            
            session = get_db_session()
            vendors = session.query(Vendor).all()
            
            vendors_data = []
            for vendor in vendors:
                vendors_data.append({
                    'id': vendor.id,
                    'name': vendor.name,
                    'industry_category': vendor.industry_category,
                    'status': getattr(vendor, 'status', 'active')
                })
            
            return jsonify(vendors_data)
            
        except Exception as e:
            logger.error(f"Vendors error: {str(e)}")
            return jsonify({'error': str(e)}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    # ============ INVOICE ROUTES ============
    
    @app.route('/api/invoices', methods=['GET'])
    def get_invoices():
        """Get all invoices"""
        try:
            if not Invoice:
                # Mock data for demo
                return jsonify([
                    {"id": 1, "vendor": "Morrison & Foerster LLP", "amount": 45750, "status": "approved", "date": "2024-01-15", "riskScore": 0.25},
                    {"id": 2, "vendor": "Baker McKenzie", "amount": 32100, "status": "pending", "date": "2024-01-14", "riskScore": 0.15},
                    {"id": 3, "vendor": "Latham & Watkins", "amount": 67800, "status": "approved", "date": "2024-01-13", "riskScore": 0.45},
                    {"id": 4, "vendor": "White & Case", "amount": 28900, "status": "review", "date": "2024-01-12", "riskScore": 0.35},
                    {"id": 5, "vendor": "Skadden Arps", "amount": 51200, "status": "approved", "date": "2024-01-11", "riskScore": 0.20}
                ])
            
            session = get_db_session()
            invoices = session.query(Invoice)\
                .join(Vendor, Invoice.vendor_id == Vendor.id, isouter=True)\
                .order_by(desc(Invoice.created_at))\
                .limit(100)\
                .all()
            
            invoices_data = []
            for invoice in invoices:
                vendor_name = invoice.vendor.name if invoice.vendor else 'Unknown'
                invoices_data.append({
                    'id': invoice.id,
                    'vendor': vendor_name,
                    'amount': float(invoice.amount),
                    'status': invoice.status,
                    'date': invoice.date.isoformat() if invoice.date else None,
                    'riskScore': float(invoice.risk_score) if invoice.risk_score else 0
                })
            
            return jsonify(invoices_data)
            
        except Exception as e:
            logger.error(f"Invoices error: {str(e)}")
            return jsonify({'error': str(e)}), 500
        finally:
            if 'session' in locals():
                session.close()
    
    # ============ REGISTER ADDITIONAL ROUTES ============
    
    # Try to register blueprints if available
    try:
        from routes import register_routes
        with app.app_context():
            register_routes(app)
            logger.info("✅ Additional routes registered successfully")
    except ImportError as e:
        logger.info(f"Additional routes not available: {e}")
    
    return app

# Create the unified application instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting LAIT Unified Legal Intelligence API v3.0")
    print("🔧 Initializing Unified Environment...")
    
    try:
        # Get configuration
        port = int(os.environ.get('API_PORT', 5003))
        host = os.environ.get('API_HOST', '0.0.0.0')
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        # Report system status
        endpoints_count = len([rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/api/')])
        
        print(f"✅ System Initialized:")
        print(f"   - Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"   - API: {endpoints_count} active endpoints")
        print(f"   - Features: Authentication, Dashboard, Analytics, ML Models")
        print(f"   - Socket.IO: Enabled")
        print(f"   - CORS: Configured for development")
        
        print(f"🌐 Starting server on http://{host}:{port}")
        print(f"📊 Dashboard: http://{host}:{port}")
        print(f"🔐 Demo Login: admin@lait.com / admin123")
        
        # Use Socket.IO to run the application
        socketio.run(app, host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested. Exiting gracefully...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
