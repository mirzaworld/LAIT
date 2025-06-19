# Import all routes for easy importing

from backend.routes.auth import auth_bp
from backend.routes.invoice import invoice_bp
# Import only one invoice blueprint
# from backend.routes.invoices import invoices_bp
from backend.routes.analytics import analytics_bp
from backend.routes.admin import admin_bp
from backend.routes.notification import notification_bp

# List of all blueprints
blueprints = [
    (auth_bp, '/api/auth'),
    (invoice_bp, '/api/invoices'),
    (analytics_bp, '/api/analytics'),
    (admin_bp, '/api/admin'),
    (notification_bp, '/api/notifications')
]

# We're removing this block to avoid duplicate blueprint registration
# # Add invoices_bp if it exists and is different from invoice_bp
# if invoices_bp and invoices_bp.name != invoice_bp.name:
#     blueprints.append((invoices_bp, None))  # url_prefix is already included in blueprint definition
