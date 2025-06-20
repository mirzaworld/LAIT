# Import all routes for easy importing

from routes.auth import auth_bp
# from routes.invoice import invoice_bp
from routes.invoices import invoices_bp
from routes.analytics import analytics_bp
from routes.admin import admin_bp
from routes.notification import notification_bp
from routes.vendors import vendors_bp
from routes.legal_intelligence import legal_intel_bp

# List of all blueprints
blueprints = [
    (auth_bp, '/api/auth'),
    (invoices_bp, None),  # url_prefix already included in blueprint
    (analytics_bp, '/api/analytics'),
    (admin_bp, '/api/admin'),
    (notification_bp, '/api/notifications'),
    (vendors_bp, None),  # url_prefix already included in blueprint
    (legal_intel_bp, '/api/legal-intelligence')
]

# We're removing this block to avoid duplicate blueprint registration
# # Add invoices_bp if it exists and is different from invoice_bp
# if invoices_bp and invoices_bp.name != invoice_bp.name:
#     blueprints.append((invoices_bp, None))  # url_prefix is already included in blueprint definition
