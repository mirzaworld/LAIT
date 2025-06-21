"""Invoice-related routes"""
from flask import jsonify, request, current_app as app
from datetime import datetime

def register_invoice_routes(app):
    """Register invoice-related routes"""
    
    @app.route('/api/invoices')
    def get_invoices():
        """Get all invoices with enhanced data"""
        try:
            db = app.extensions['sqlalchemy'].db
            invoices = db.session.query(app.models.Invoice).all()
            return jsonify([invoice.to_dict() for invoice in invoices])
        except Exception as e:
            app.logger.error(f"Error fetching invoices: {e}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/invoices/<invoice_id>')
    def get_invoice(invoice_id):
        """Get detailed invoice information"""
        try:
            db = app.extensions['sqlalchemy'].db
            invoice = db.session.query(app.models.Invoice).filter_by(id=invoice_id).first()
            if not invoice:
                return jsonify({"error": "Invoice not found"}), 404
            return jsonify(invoice.to_dict())
        except Exception as e:
            app.logger.error(f"Error fetching invoice {invoice_id}: {e}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/invoices', methods=['POST'])
    def create_invoice():
        """Create a new invoice and analyze it"""
        try:
            data = request.get_json()
            
            # Basic validation
            required_fields = ['vendor', 'amount', 'date']
            if not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields"}), 400
                
            db = app.extensions['sqlalchemy'].db
            
            # Create invoice
            invoice = app.models.Invoice(
                vendor=data['vendor'],
                amount=data['amount'],
                date=datetime.strptime(data['date'], '%Y-%m-%d'),
                status='pending',
                category=data.get('category', 'Other'),
                hours=data.get('hours', 0),
                rate=data.get('rate', 0)
            )
            
            # Analyze invoice if models are available
            if app.invoice_analyzer:
                analysis = app.invoice_analyzer.analyze_invoice(data)
                invoice.risk_score = analysis.get('risk_score', 50)
                
            db.session.add(invoice)
            db.session.commit()
            
            return jsonify(invoice.to_dict()), 201
            
        except Exception as e:
            app.logger.error(f"Error creating invoice: {e}")
            return jsonify({"error": str(e)}), 500
