# Import all routes for easy importing

from backend.routes.auth import auth_bp
from backend.routes.invoice import invoice_bp
from backend.routes.invoices import invoices_bp
from backend.routes.analytics import analytics_bp
from backend.routes.admin import admin_bp
from backend.routes.notification import notification_bp

# List of all blueprints
blueprints = [
    (auth_bp, '/api/auth'),
    (invoice_bp, '/api/invoices'),
    (invoices_bp, None),  # url_prefix is already included in blueprint definition
    (analytics_bp, '/api/analytics'),
    (admin_bp, '/api/admin'),
    (notification_bp, '/api/notifications')
]

# Add invoices_bp if it exists
if invoices_bp:
    blueprints.append((invoices_bp, '/api/invoices'))
