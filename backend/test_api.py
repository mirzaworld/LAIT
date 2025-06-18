from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from models.matter_analyzer import MatterAnalyzer
from models.vendor_analyzer import VendorAnalyzer
from models.invoice_analyzer import InvoiceAnalyzer
from db.database_sqlite import init_db, get_db_session, Invoice, LineItem, Vendor, Matter, RiskFactor, User

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize database
init_db()

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

# Matter analytics endpoints
@app.route('/api/analytics/matter/<matter_id>/forecast', methods=['GET'])
def get_matter_expense_forecast(matter_id):
    """Get expense forecast for a specific matter."""
    try:
        analyzer = MatterAnalyzer()
        session = get_db_session()
        
        try:
            # Get matter from database
            cursor = session.conn.cursor()
            cursor.execute("SELECT * FROM matters WHERE id = ?", (matter_id,))
            matter = cursor.fetchone()
            if not matter:
                return jsonify({'error': f'Matter {matter_id} not found'}), 404
            
            # Get invoices for this matter
            cursor.execute("SELECT * FROM invoices WHERE matter_id = ?", (matter_id,))
            invoices = cursor.fetchall()
            
            # Convert to dictionary format
            matter_data = {
                'id': matter['id'],
                'name': matter['name'],
                'category': matter['category'],
                'status': matter['status'],
                'start_date': matter['start_date'],
                'end_date': matter['end_date'],
                'budget': matter['budget']
            }
            
            invoices_data = []
            for inv in invoices:
                # Get line items for hours distribution
                cursor.execute("""
                    SELECT SUM(hours) as hours, timekeeper_title 
                    FROM line_items 
                    WHERE invoice_id = ? 
                    GROUP BY timekeeper_title
                """, (inv['id'],))
                hours_data = cursor.fetchall()
                
                partner_hours = 0
                associate_hours = 0
                paralegal_hours = 0
                
                for h in hours_data:
                    title = h['timekeeper_title'].lower() if h['timekeeper_title'] else ''
                    hours = h['hours'] or 0
                    if 'partner' in title:
                        partner_hours = hours
                    elif 'associate' in title:
                        associate_hours = hours
                    elif 'paralegal' in title:
                        paralegal_hours = hours
                
                invoices_data.append({
                    'id': inv['id'],
                    'amount': inv['amount'],
                    'date': inv['date'],
                    'hours': inv['hours'],
                    'partner_hours': partner_hours,
                    'associate_hours': associate_hours,
                    'paralegal_hours': paralegal_hours
                })
            
            # Generate forecast using the matter data and its invoices
            forecast = analyzer._generate_forecast(matter_data, invoices_data)
            return jsonify(forecast)
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': f'Error generating matter expense forecast: {str(e)}'}), 500

@app.route('/api/analytics/matter/<matter_id>/risk_profile', methods=['GET'])
def get_matter_risk_profile(matter_id):
    """Get risk analysis for a specific matter."""
    try:
        session = get_db_session()
        try:
            # Get matter from database
            cursor = session.conn.cursor()
            cursor.execute("SELECT * FROM matters WHERE id = ?", (matter_id,))
            matter = cursor.fetchone()
            if not matter:
                return jsonify({'error': f'Matter {matter_id} not found'}), 404
            
            # Get invoices for this matter
            cursor.execute("SELECT * FROM invoices WHERE matter_id = ?", (matter_id,))
            invoices = cursor.fetchall()
            
            # Calculate total spend and budget utilization
            total_spend = sum(inv['amount'] for inv in invoices)
            budget_utilization = total_spend / matter['budget'] if matter['budget'] else 0
            
            # Generate risk factors
            risk_factors = []
            
            if budget_utilization > 0.7:
                risk_factors.append({
                    'type': 'budget_overrun',
                    'severity': 'medium' if budget_utilization < 0.9 else 'high',
                    'description': f'Budget utilization at {budget_utilization:.1%}'
                })
            
            # Calculate hours distribution
            cursor.execute("""
                SELECT SUM(li.hours) as hours, li.timekeeper_title 
                FROM line_items li
                JOIN invoices inv ON li.invoice_id = inv.id
                WHERE inv.matter_id = ?
                GROUP BY li.timekeeper_title
            """, (matter_id,))
            hours_data = cursor.fetchall()
            
            partner_hours = 0
            total_hours = 0
            
            for h in hours_data:
                title = h['timekeeper_title'].lower() if h['timekeeper_title'] else ''
                hours = h['hours'] or 0
                total_hours += hours
                if 'partner' in title:
                    partner_hours += hours
            
            partner_ratio = partner_hours / total_hours if total_hours > 0 else 0
            
            if partner_ratio > 0.4:
                risk_factors.append({
                    'type': 'partner_heavy',
                    'severity': 'medium' if partner_ratio < 0.6 else 'high',
                    'description': f'Partner-heavy staffing ({partner_ratio:.1%} of hours)'
                })
            
            # Calculate risk score
            risk_score = min(25 * len(risk_factors) + 40 * budget_utilization, 100)
            
            # Determine risk level
            risk_level = 'low'
            if risk_score >= 70:
                risk_level = 'high'
            elif risk_score >= 40:
                risk_level = 'medium'
            
            profile = {
                'matter_id': matter_id,
                'matter_name': matter['name'],
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'budget_utilization': budget_utilization
            }
            
            return jsonify(profile)
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': f'Error generating matter risk profile: {str(e)}'}), 500

@app.route('/api/analytics/vendor/<vendor_id>/risk_profile', methods=['GET'])
def get_vendor_risk_profile(vendor_id):
    """Get advanced risk profile for a vendor."""
    try:
        session = get_db_session()
        try:
            # Get vendor from database
            cursor = session.conn.cursor()
            cursor.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,))
            vendor = cursor.fetchone()
            if not vendor:
                return jsonify({'error': f'Vendor {vendor_id} not found'}), 404
            
            # Get invoices for this vendor
            cursor.execute("SELECT * FROM invoices WHERE vendor_id = ?", (vendor_id,))
            invoices = cursor.fetchall()
            
            if not invoices:
                return jsonify({'error': f'No invoices found for vendor {vendor_id}'}), 404
                
            # Calculate vendor metrics
            total_invoices = len(invoices)
            total_amount = sum(inv['amount'] for inv in invoices)
            avg_risk_score = sum(inv['risk_score'] for inv in invoices) / total_invoices if total_invoices > 0 else 0
            
            # Get average rates
            cursor.execute("""
                SELECT AVG(li.rate) as avg_rate
                FROM line_items li
                JOIN invoices inv ON li.invoice_id = inv.id
                WHERE inv.vendor_id = ?
            """, (vendor_id,))
            vendor_avg_rate = cursor.fetchone()['avg_rate'] or 0
            
            # Get industry average rates
            cursor.execute("""
                SELECT AVG(li.rate) as avg_rate
                FROM line_items li
                JOIN invoices inv ON li.invoice_id = inv.id
            """)
            industry_avg_rate = cursor.fetchone()['avg_rate'] or 0
            
            # Calculate peer comparison rate (similar vendors)
            cursor.execute("""
                SELECT AVG(li.rate) as avg_rate
                FROM line_items li
                JOIN invoices inv ON li.invoice_id = inv.id
                JOIN vendors v ON inv.vendor_id = v.id
                WHERE v.category = (SELECT category FROM vendors WHERE id = ?)
            """, (vendor_id,))
            peer_avg_rate = cursor.fetchone()['avg_rate'] or industry_avg_rate
            
            # Calculate billing efficiency
            billing_efficiency = max(0, min(100, 100 - (avg_risk_score * 10)))
            
            # Determine matter complexity
            complexity_level = "medium"
            if total_amount / total_invoices > 100000:
                complexity_level = "high"
            elif total_amount / total_invoices < 50000:
                complexity_level = "low"
                
            # Calculate staffing efficiency
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN lower(li.timekeeper_title) LIKE '%partner%' THEN li.hours ELSE 0 END) as partner_hours,
                    SUM(CASE WHEN lower(li.timekeeper_title) LIKE '%associate%' THEN li.hours ELSE 0 END) as associate_hours,
                    SUM(li.hours) as total_hours
                FROM line_items li
                JOIN invoices inv ON li.invoice_id = inv.id
                WHERE inv.vendor_id = ?
            """, (vendor_id,))
            hours_data = cursor.fetchone()
            
            partner_hours = hours_data['partner_hours'] or 0
            total_hours = hours_data['total_hours'] or 0
            
            # Partner ratio - lower is better for efficiency
            partner_ratio = partner_hours / total_hours if total_hours > 0 else 0
            staffing_efficiency = max(0, min(100, 100 - (partner_ratio * 100)))
            
            # Calculate risk score
            rate_factor = (vendor_avg_rate / industry_avg_rate) if industry_avg_rate > 0 else 1
            risk_score = min(100, max(0, 
                              (avg_risk_score * 20) + 
                              (rate_factor * 20) + 
                              (partner_ratio * 50)))
            
            # Determine risk level
            risk_level = "medium"
            if risk_score >= 70:
                risk_level = "high"
            elif risk_score <= 30:
                risk_level = "low"
                
            profile = {
                'vendor_id': vendor_id,
                'vendor_name': vendor['name'],
                'risk_score': risk_score,
                'risk_level': risk_level,
                'performance_metrics': {
                    'billing_efficiency': billing_efficiency,
                    'matter_complexity': complexity_level,
                    'staffing_efficiency': staffing_efficiency
                },
                'benchmarks': {
                    'industry_avg_rate': round(industry_avg_rate, 2),
                    'peer_avg_rate': round(peer_avg_rate, 2),
                    'vendor_avg_rate': round(vendor_avg_rate, 2)
                }
            }
            return jsonify(profile)
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': f'Error generating vendor risk profile: {str(e)}'}), 500



@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user from token"""
    auth_header = request.headers.get('Authorization', '')
    
    # In a real app, we'd validate the JWT token
    # For testing, we'll just check if it contains a user id
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        if token.startswith('test_jwt_token_'):
            user_id = token.split('_')[-1]
            
            session = get_db_session()
            try:
                cursor = session.conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                
                if user:
                    return jsonify({
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'role': user['role']
                    })
            finally:
                session.close()
    
    return jsonify({'error': 'Unauthorized'}), 401

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login route for authentication"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        session = get_db_session()
        try:
            cursor = session.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
                
            # In a real app, we'd check the password hash
            # For testing, we'll just allow any password
            
            token = 'test_jwt_token_' + str(user['id'])
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            })
        finally:
            session.close()
    except Exception as e:
        return jsonify({'error': f'Login error: {str(e)}'}), 500

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8080
    
    print(f"Starting test server on {host}:{port}")
    app.run(host=host, port=port, debug=True)
