from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
from models.invoice_analyzer import InvoiceAnalyzer
from models.risk_predictor import RiskPredictor
from models.vendor_analyzer import VendorAnalyzer
from db.database import init_db, get_db_session
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
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development_key')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
notification_service = NotificationService(socketio)

# Initialize database
init_db()

# Initialize ML models
invoice_analyzer = InvoiceAnalyzer()
risk_predictor = RiskPredictor()
vendor_analyzer = VendorAnalyzer()

# Register blueprints
app.register_blueprint(invoice_bp, url_prefix='/api/invoices')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
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
