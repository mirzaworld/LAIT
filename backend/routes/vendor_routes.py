"""Vendor-related routes"""
from flask import jsonify, request, current_app as app

def register_vendor_routes(app):
    """Register vendor-related routes"""
    
    @app.route('/api/vendors')
    def get_vendors():
        """Get all vendors with comprehensive metrics"""
        try:
            # Get unique vendors from invoices
            db = app.extensions['sqlalchemy'].db
            vendor_data = {}
            invoices = db.session.query(app.models.Invoice).all()
            
            for invoice in invoices:
                if invoice.vendor not in vendor_data:
                    vendor_data[invoice.vendor] = {
                        'name': invoice.vendor,
                        'total_spend': 0,
                        'invoice_count': 0,
                        'average_risk_score': 0,
                        'risk_scores': []
                    }
                    
                vendor = vendor_data[invoice.vendor]
                vendor['total_spend'] += invoice.amount
                vendor['invoice_count'] += 1
                vendor['risk_scores'].append(invoice.risk_score)
                
            # Calculate metrics
            vendors = []
            for vendor in vendor_data.values():
                vendor['average_risk_score'] = sum(vendor['risk_scores']) / len(vendor['risk_scores'])
                del vendor['risk_scores']  # Remove raw scores
                vendors.append(vendor)
                
            return jsonify(vendors)
            
        except Exception as e:
            app.logger.error(f"Error fetching vendors: {e}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/vendors/<vendor_name>')
    def get_vendor_details(vendor_name):
        """Get detailed vendor information and analytics"""
        try:
            # Get vendor analytics
            db = app.extensions['sqlalchemy'].db
            invoices = db.session.query(app.models.Invoice).filter_by(vendor=vendor_name).all()
            
            if not invoices:
                return jsonify({"error": "Vendor not found"}), 404
                
            # Calculate vendor metrics
            total_spend = sum(inv.amount for inv in invoices)
            risk_scores = [inv.risk_score for inv in invoices]
            average_risk = sum(risk_scores) / len(risk_scores)
            
            # Use vendor analyzer if available
            vendor_analysis = None
            if app.vendor_analyzer:
                vendor_analysis = app.vendor_analyzer.analyze_vendor(vendor_name, invoices)
                
            vendor_details = {
                'name': vendor_name,
                'metrics': {
                    'total_spend': total_spend,
                    'invoice_count': len(invoices),
                    'average_risk_score': average_risk
                },
                'analysis': vendor_analysis or {},
                'recent_invoices': [inv.to_dict() for inv in invoices[-5:]]  # Last 5 invoices
            }
            
            return jsonify(vendor_details)
            
        except Exception as e:
            app.logger.error(f"Error fetching vendor details for {vendor_name}: {e}")
            return jsonify({"error": str(e)}), 500
