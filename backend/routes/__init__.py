"""Route registration and blueprints"""
from flask import jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Import all routes for easy importing
from .auth import auth_bp
from .enhanced_auth import enhanced_auth_bp
# from .invoice import invoice_bp
from .invoices import invoices_bp
from .analytics import analytics_bp
from .admin import admin_bp
from .notification import notification_bp
from .vendors import vendors_bp
from .legal_intelligence import legal_intel_bp
from .enhanced_upload import upload_bp

# List of all blueprints
blueprints = [
    (auth_bp, '/api/auth'),  # Legacy auth routes
    (enhanced_auth_bp, '/api/auth'),  # Enhanced auth with complete user management
    (invoices_bp, None),  # url_prefix already included in blueprint
    (analytics_bp, '/api/analytics'),
    (admin_bp, '/api/admin'),
    (notification_bp, None),  # blueprint already has /api/notifications prefix
    (vendors_bp, None),  # url_prefix already included in blueprint
    (legal_intel_bp, '/api/legal-intelligence'),
    (upload_bp, None)  # url_prefix already included in blueprint
]

def register_routes(app):
    """Register all routes for the application"""

    # Register all blueprints
    for blueprint, url_prefix in blueprints:
        try:
            if url_prefix:
                app.register_blueprint(blueprint, url_prefix=url_prefix)
            else:
                app.register_blueprint(blueprint)
            app.logger.info(f"Registered blueprint: {blueprint.name}")
        except Exception as e:
            app.logger.error(f"Failed to register blueprint {blueprint.name}: {e}")

    # Register additional route modules (if they exist) - commented out to avoid conflicts
    # try:
    #     from .invoice_routes import register_invoice_routes
    #     register_invoice_routes(app)
    # except ImportError:
    #     pass

    # try:
    #     from .vendor_routes import register_vendor_routes
    #     register_vendor_routes(app)
    # except ImportError:
    #     pass

    # try:
    #     from .ml_routes import register_ml_routes
    #     register_ml_routes(app)
    # except ImportError:
    #     pass

    # try:
    #     from .document_routes import register_document_routes
    #     register_document_routes(app)
    # except ImportError:
    #     pass

    try:
        from .workflow_routes import register_workflow_routes
        register_workflow_routes(app)
        logger.info('✅ Workflow routes registered')
    except ImportError as e:
        logger.warning(f'❌ Failed to import workflow routes: {e}')
    except Exception as e:
        logger.warning(f'❌ Failed to register workflow routes: {e}')

    return app  # Return the app for chaining
