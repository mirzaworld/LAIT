from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create global instances to be initialized later
socketio = SocketIO()

def create_app():
    """
    Application factory function to create and configure the Flask app
    """
    # Initialize Flask app
    flask_app = Flask(__name__)
    
    # Import config
    try:
        from backend.config import Config
        flask_app.config.from_object(Config)
    except ImportError as e:
        logger.info(f"First import attempt failed: {e}")
        try:
            import config
            flask_app.config.from_object(config.Config)
        except ImportError as e:
            logger.warning(f"Config module not found: {e}, using default configurations")
    
    # Configure the app
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/legalspend')
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
    flask_app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-prod')
    
    # Initialize extensions
    try:
        from backend.models import db
        db.init_app(flask_app)
        migrate = Migrate(flask_app, db)
    except ImportError:
        try:
            from models import db
            db.init_app(flask_app)
            migrate = Migrate(flask_app, db)
        except ImportError:
            logger.warning("Database models not found, skipping database initialization")
    
    # Initialize JWT Manager
    jwt = JWTManager(flask_app)
    
    # Security configurations
    if flask_app.config.get('ENV') == 'production':
        # Enable HTTPS
        Talisman(flask_app, 
                force_https=True,
                strict_transport_security=True,
                session_cookie_secure=True)

        # Configure CORS for production
        CORS(flask_app, 
            resources={r"/api/*": {"origins": [flask_app.config.get('FRONTEND_URL')]}},
            supports_credentials=True)
    else:
        # Development CORS settings
        CORS(flask_app)

    # Configure rate limiting
    try:
        limiter = Limiter(
            app=flask_app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=flask_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        )
    except Exception as e:
        logger.warning(f"Rate limiter initialization failed: {e}")

    # Initialize SocketIO
    socketio.init_app(flask_app, cors_allowed_origins="*")

    # Register root route
    @flask_app.route('/')
    def root():
        return jsonify({
            "message": "LAIT API is running",
            "status": "ok",
            "version": "1.0.0"
        })

    # Import and register blueprints
    try:
        # Try importing from the routes package
        from routes import blueprints
        
        for blueprint, url_prefix in blueprints:
            flask_app.register_blueprint(blueprint, url_prefix=url_prefix)
            logger.info(f"Registered blueprint {blueprint.name} at {url_prefix}")
    except ImportError as e:
        try:
            # Fallback to direct imports from backend.routes
            from backend.routes import blueprints
            
            for blueprint, url_prefix in blueprints:
                flask_app.register_blueprint(blueprint, url_prefix=url_prefix)
                logger.info(f"Registered blueprint {blueprint.name} at {url_prefix}")
        except ImportError as e:
            logger.warning(f"Routes not found, skipping blueprint registration: {e}")
    
    # Define health check endpoint
    @flask_app.route('/api/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint"""
        return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

    # Define error handlers
    @flask_app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @flask_app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    @flask_app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    @flask_app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401

    @flask_app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403

    # Make sure all error responses are in JSON
    @flask_app.errorhandler(Exception)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # Start with the correct headers and status code
        response = {"error": str(e)}
        # Replace the body with JSON
        return jsonify(response), 500

    # Define socketio event handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info('Client connected')
        
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info('Client disconnected')

    return flask_app

# This allows running the file directly for development
if __name__ == '__main__':
    app = create_app()
    host = os.environ.get('API_HOST', '0.0.0.0')
    port = int(os.environ.get('API_PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    socketio.run(app, host=host, port=port, debug=debug)
