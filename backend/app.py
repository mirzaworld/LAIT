from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import os
from dotenv import load_dotenv

# Import database models and migrations
from models import db, User, Invoice, Vendor

# Import ML models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.models.outlier_detector import OutlierDetector
from ml.models.risk_predictor import RiskPredictor
from ml.models.vendor_analyzer import VendorAnalyzer
from models.invoice_analyzer import InvoiceAnalyzer

# Import services and routes
from services.notification_service import NotificationService
from routes.invoice import invoice_bp
from routes.auth import auth_bp
from routes.analytics import analytics_bp
from routes.admin import admin_bp
from routes.notification import notification_bp
import config

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config.Config)

# Security configurations
if app.config['ENV'] == 'production':
    # Enable HTTPS
    Talisman(app, 
             force_https=True,
             strict_transport_security=True,
             session_cookie_secure=True)

    # Configure CORS for production
    CORS(app, 
         resources={r"/api/*": {"origins": [app.config['FRONTEND_URL']]}},
         supports_credentials=True)
else:
    # Development CORS settings
    CORS(app)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config['REDIS_URL']
)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/legalspend')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-prod')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
notification_service = NotificationService(socketio)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(invoice_bp, url_prefix='/api/invoices')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(notification_bp, url_prefix='/api/notifications')

# Initialize ML models
outlier_detector = OutlierDetector()
risk_predictor = RiskPredictor()
vendor_analyzer = VendorAnalyzer()
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(notification_bp, url_prefix='/api/notifications')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

# Make sure all error responses are in JSON
@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # Start with the correct headers and status code
    response = {"error": str(e)}
    # Replace the body with JSON
    return jsonify(response), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    
@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    host = os.environ.get('API_HOST', '0.0.0.0')
    port = int(os.environ.get('API_PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    socketio.run(app, host=host, port=port, debug=debug)
