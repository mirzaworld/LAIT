from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from models.matter_analyzer import MatterAnalyzer
from models.vendor_analyzer import VendorAnalyzer
from models.invoice_analyzer import InvoiceAnalyzer

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
        # For test purposes, use get_mock_matters to simulate a database
        mock_matters = analyzer.get_mock_matters()
        matter_data = None
        for matter in mock_matters:
            if matter['id'] == matter_id:
                matter_data = matter
                break
            
        if not matter_data:
            return jsonify({'error': f'Matter {matter_id} not found'}), 404
            
        # Generate forecast using the matter data and its invoices
        forecast = analyzer._generate_forecast(matter_data, matter_data.get('invoices', []))
        return jsonify(forecast)
    except Exception as e:
        return jsonify({'error': f'Error generating matter expense forecast: {str(e)}'}), 500

@app.route('/api/analytics/matter/<matter_id>/risk_profile', methods=['GET'])
def get_matter_risk_profile(matter_id):
    """Get risk analysis for a specific matter."""
    try:
        analyzer = MatterAnalyzer()
        # For test purposes, use get_mock_matters to simulate a database
        mock_matters = analyzer.get_mock_matters()
        matter_data = None
        for matter in mock_matters:
            if matter['id'] == matter_id:
                matter_data = matter
                break
            
        if not matter_data:
            return jsonify({'error': f'Matter {matter_id} not found'}), 404
            
        # Generate a simplified risk profile based on the matter data
        risk_score = 65 if matter_data.get('budget', 0) > 0 else 0
        risk_level = 'medium'
        
        profile = {
            'matter_id': matter_id,
            'matter_name': matter_data.get('name', ''),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': [
                {
                    'type': 'budget_overrun',
                    'severity': 'medium',
                    'description': 'Budget utilization at 72.0%'
                }
            ],
            'budget_utilization': 0.72
        }
        
        return jsonify(profile)
    except Exception as e:
        return jsonify({'error': f'Error generating matter risk profile: {str(e)}'}), 500

@app.route('/api/analytics/vendor/<vendor_id>/risk_profile', methods=['GET'])
def get_vendor_risk_profile(vendor_id):
    """Get advanced risk profile for a vendor."""
    try:
        analyzer = VendorAnalyzer()
        # Create a simple mock response for testing
        profile = {
            'vendor_id': vendor_id,
            'risk_score': 75,
            'risk_level': 'high',
            'performance_metrics': {
                'billing_efficiency': 82,
                'matter_complexity': 'high',
                'staffing_efficiency': 68
            },
            'benchmarks': {
                'industry_avg_rate': 350,
                'peer_avg_rate': 380,
                'vendor_avg_rate': 425
            }
        }
        return jsonify(profile)
    except Exception as e:
        return jsonify({'error': f'Error generating vendor risk profile: {str(e)}'}), 500

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8080
    
    print(f"Starting test server on {host}:{port}")
    app.run(host=host, port=port, debug=True)
