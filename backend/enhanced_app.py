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
from backend.db.database import User, Invoice, Vendor, SessionLocal, init_db
from backend.models.db_models import AuditLog

# Import ML models and analyzers
try:
    from backend.models.invoice_analyzer import InvoiceAnalyzer
    from backend.models.vendor_analyzer import VendorAnalyzer
    from backend.models.risk_predictor import RiskPredictor
    from backend.models.matter_analyzer import MatterAnalyzer
    from backend.models.enhanced_invoice_analyzer import EnhancedInvoiceAnalyzer
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
    from backend.services.real_time_data_collector import RealTimeLegalDataCollector
    
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
            from backend.db.database import get_db_session
            from backend.models.db_models import Invoice, Vendor
            
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

    # Legal Intelligence API Routes
    @app.route('/api/legal-intelligence/search', methods=['POST'])
    @jwt_required()
    def search_legal_cases():
        """Enhanced legal case search with real-time data integration"""
        try:
            data = request.get_json()
            query = data.get('query', '')
            jurisdiction = data.get('jurisdiction', 'all')
            date_range = data.get('dateRange', {})
            
            if not query:
                return jsonify({'error': 'Query is required'}), 400
            
            # Use real-time data collector for comprehensive search
            collector = app.data_collector
            
            # Search multiple sources simultaneously
            search_results = {
                'cases': [],
                'metadata': {
                    'total_results': 0,
                    'search_time': 0,
                    'sources_searched': []
                }
            }
            
            start_time = time.time()
            
            # 1. Search CourtListener API
            try:
                courtlistener_results = collector.fetch_courtlistener_data(query, limit=20)
                if courtlistener_results and 'results' in courtlistener_results:
                    for case in courtlistener_results['results']:
                        search_results['cases'].append({
                            'id': case.get('id'),
                            'title': case.get('caseName', case.get('name', 'Unknown Case')),
                            'court': case.get('court', {}).get('name', 'Unknown Court'),
                            'date': case.get('dateFiled'),
                            'citation': case.get('citation', []),
                            'summary': case.get('summary', '')[:200] + '...' if case.get('summary') else '',
                            'url': case.get('absolute_url'),
                            'source': 'CourtListener',
                            'jurisdiction': case.get('court', {}).get('jurisdiction', 'Federal')
                        })
                search_results['metadata']['sources_searched'].append('CourtListener')
            except Exception as e:
                logger.error(f"CourtListener search error: {e}")
            
            # 2. Search Justia
            try:
                justia_results = collector.search_justia_cases(query)
                if justia_results:
                    for case in justia_results[:10]:  # Limit results
                        search_results['cases'].append({
                            'id': f"justia_{case.get('id', len(search_results['cases']))}",
                            'title': case.get('title', 'Unknown Case'),
                            'court': case.get('court', 'Unknown Court'),
                            'date': case.get('date'),
                            'citation': case.get('citation', []),
                            'summary': case.get('summary', '')[:200] + '...' if case.get('summary') else '',
                            'url': case.get('url'),
                            'source': 'Justia',
                            'jurisdiction': case.get('jurisdiction', 'State')
                        })
                search_results['metadata']['sources_searched'].append('Justia')
            except Exception as e:
                logger.error(f"Justia search error: {e}")
            
            # 3. Search Google Scholar
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
                            'summary': case.get('snippet', '')[:200] + '...' if case.get('snippet') else '',
                            'url': case.get('link'),
                            'source': 'Google Scholar',
                            'jurisdiction': case.get('jurisdiction', 'Unknown')
                        })
                search_results['metadata']['sources_searched'].append('Google Scholar')
            except Exception as e:
                logger.error(f"Google Scholar search error: {e}")
            
            # Apply filters
            if jurisdiction != 'all':
                search_results['cases'] = [
                    case for case in search_results['cases'] 
                    if case.get('jurisdiction', '').lower() == jurisdiction.lower()
                ]
            
            # Sort by relevance and date
            search_results['cases'] = sorted(
                search_results['cases'], 
                key=lambda x: (x.get('date') or '0000-01-01'), 
                reverse=True
            )
            
            search_results['metadata']['total_results'] = len(search_results['cases'])
            search_results['metadata']['search_time'] = round(time.time() - start_time, 2)
            
            return jsonify(search_results)
            
        except Exception as e:
            logger.error(f"Legal case search error: {str(e)}")
            return jsonify({'error': f'Search failed: {str(e)}'}), 500

    @app.route('/api/legal-intelligence/case/<case_id>')
    @jwt_required()
    def get_case_details(case_id):
        """Get detailed information about a specific legal case"""
        try:
            collector = app.data_collector
            
            # Parse case source from ID
            source = 'unknown'
            if case_id.startswith('justia_'):
                source = 'justia'
                actual_id = case_id.replace('justia_', '')
            elif case_id.startswith('scholar_'):
                source = 'scholar'
                actual_id = case_id.replace('scholar_', '')
            else:
                source = 'courtlistener'
                actual_id = case_id
            
            case_details = {
                'id': case_id,
                'source': source,
                'loading': False,
                'error': None
            }
            
            # Fetch detailed case information based on source
            if source == 'courtlistener':
                try:
                    # Use CourtListener API to get case details
                    details = collector.get_case_details_courtlistener(actual_id)
                    if details:
                        case_details.update({
                            'title': details.get('caseName', 'Unknown Case'),
                            'court': details.get('court', {}).get('name', 'Unknown Court'),
                            'date_filed': details.get('dateFiled'),
                            'date_argued': details.get('dateArgued'),
                            'judges': details.get('judges', []),
                            'parties': details.get('parties', []),
                            'docket_number': details.get('docketNumber'),
                            'citations': details.get('citations', []),
                            'summary': details.get('summary', ''),
                            'opinion_text': details.get('text', ''),
                            'procedural_history': details.get('procedural_history', []),
                            'key_holdings': details.get('holdings', []),
                            'legal_issues': details.get('legal_issues', []),
                            'outcome': details.get('outcome', ''),
                            'significance': details.get('significance', ''),
                            'related_cases': details.get('related_cases', []),
                            'url': details.get('absolute_url')
                        })
                except Exception as e:
                    logger.error(f"CourtListener case details error: {e}")
                    case_details['error'] = str(e)
                    
            elif source == 'justia':
                try:
                    details = collector.get_case_details_justia(actual_id)
                    if details:
                        case_details.update(details)
                except Exception as e:
                    logger.error(f"Justia case details error: {e}")
                    case_details['error'] = str(e)
                    
            else:  # Google Scholar or unknown
                case_details.update({
                    'title': 'Case details not available',
                    'summary': 'Full case details are not available for this source.',
                    'error': 'Detailed view not supported for this source'
                })
            
            return jsonify(case_details)
            
        except Exception as e:
            logger.error(f"Case details error: {str(e)}")
            return jsonify({'error': f'Failed to fetch case details: {str(e)}'}), 500

    @app.route('/api/legal-intelligence/citations')
    @jwt_required()
    def search_citations():
        """Search for legal citations and precedents"""
        try:
            query = request.args.get('query', '')
            citation_type = request.args.get('type', 'all')  # case, statute, regulation
            
            if not query:
                return jsonify({'error': 'Query is required'}), 400
            
            collector = app.data_collector
            citations = []
            
            # Search for citations across multiple sources
            try:
                # Use CourtListener for legal citations
                courtlistener_citations = collector.search_citations_courtlistener(query)
                citations.extend(courtlistener_citations or [])
                
                # Add Justia citations
                justia_citations = collector.search_justia_citations(query)
                citations.extend(justia_citations or [])
                
            except Exception as e:
                logger.error(f"Citation search error: {e}")
            
            # Filter by type if specified
            if citation_type != 'all':
                citations = [c for c in citations if c.get('type') == citation_type]
            
            return jsonify({
                'citations': citations[:50],  # Limit results
                'total': len(citations),
                'query': query,
                'type_filter': citation_type
            })
            
        except Exception as e:
            logger.error(f"Citation search error: {str(e)}")
            return jsonify({'error': f'Citation search failed: {str(e)}'}), 500

    @app.route('/api/legal-intelligence/analytics')
    @jwt_required()
    def legal_analytics():
        """Get legal intelligence analytics and insights"""
        try:
            collector = app.data_collector
            
            # Collect analytics from multiple sources
            analytics = {
                'case_trends': collector.get_case_trends(),
                'jurisdiction_stats': collector.get_jurisdiction_statistics(),
                'practice_area_insights': collector.get_practice_area_insights(),
                'citation_patterns': collector.get_citation_patterns(),
                'court_performance': collector.get_court_performance_metrics(),
                'recent_developments': collector.get_recent_legal_developments(),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return jsonify(analytics)
            
        except Exception as e:
            logger.error(f"Legal analytics error: {str(e)}")
            return jsonify({'error': f'Analytics generation failed: {str(e)}'}), 500

    @app.route('/api/legal-intelligence/jurisdictions')
    @jwt_required()
    def get_jurisdictions():
        """Get available jurisdictions for filtering"""
        jurisdictions = [
            {'id': 'federal', 'name': 'Federal Courts', 'type': 'federal'},
            {'id': 'supreme', 'name': 'U.S. Supreme Court', 'type': 'federal'},
            {'id': 'circuit', 'name': 'Circuit Courts', 'type': 'federal'},
            {'id': 'district', 'name': 'District Courts', 'type': 'federal'},
            {'id': 'state', 'name': 'State Courts', 'type': 'state'},
            {'id': 'california', 'name': 'California', 'type': 'state'},
            {'id': 'new_york', 'name': 'New York', 'type': 'state'},
            {'id': 'texas', 'name': 'Texas', 'type': 'state'},
            {'id': 'florida', 'name': 'Florida', 'type': 'state'},
            {'id': 'illinois', 'name': 'Illinois', 'type': 'state'}
        ]
        
        return jsonify({'jurisdictions': jurisdictions})

    @app.route('/api/legal-intelligence/refresh', methods=['POST'])
    @jwt_required()
    def refresh_legal_data():
        """Refresh legal intelligence data from all sources"""
        try:
            collector = app.data_collector
            
            # Trigger data refresh
            refresh_status = {
                'started_at': datetime.utcnow().isoformat(),
                'sources_updated': [],
                'errors': []
            }
            
            # Refresh each data source
            sources = [
                'courtlistener',
                'justia', 
                'google_scholar',
                'legal_news',
                'bar_associations'
            ]
            
            for source in sources:
                try:
                    if source == 'courtlistener':
                        collector.refresh_courtlistener_data()
                    elif source == 'justia':
                        collector.refresh_justia_data()
                    elif source == 'google_scholar':
                        collector.refresh_google_scholar_data()
                    elif source == 'legal_news':
                        collector.refresh_legal_news()
                    elif source == 'bar_associations':
                        collector.refresh_bar_association_data()
                        
                    refresh_status['sources_updated'].append(source)
                    
                except Exception as e:
                    error_msg = f"{source}: {str(e)}"
                    refresh_status['errors'].append(error_msg)
                    logger.error(f"Refresh error for {source}: {e}")
            
            refresh_status['completed_at'] = datetime.utcnow().isoformat()
            refresh_status['success'] = len(refresh_status['errors']) == 0
            
            return jsonify(refresh_status)
            
        except Exception as e:
            logger.error(f"Data refresh error: {str(e)}")
            return jsonify({'error': f'Data refresh failed: {str(e)}'}), 500

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
