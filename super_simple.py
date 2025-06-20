#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/invoices') 
def get_invoices():
    return jsonify([
        {"id": "INV-001", "vendor": "Test Vendor", "amount": 1000, "status": "approved"}
    ])

@app.route('/api/dashboard/metrics')
def get_metrics():
    return jsonify({
        "total_spend": 1000,
        "invoice_count": 1,
        "active_matters": 1,
        "risk_factors_count": 0
    })

@app.route('/api/vendors') 
def get_vendors():
    return jsonify([
        {"id": "vendor-1", "name": "Test Vendor", "category": "Litigation", "spend": 1000}
    ])

@app.route('/api/analytics/spend-trends')
def get_spend_trends():
    return jsonify({
        "trends": [
            {"period": "2024-01", "amount": 20000},
            {"period": "2024-02", "amount": 25000},
            {"period": "2024-03", "amount": 30000}
        ]
    })

@app.route('/api/upload-invoice', methods=['POST'])
def upload_invoice():
    return jsonify({"message": "Upload functionality will be implemented", "status": "success"})

if __name__ == '__main__':
    print("🚀 Starting Working API on port 5002")
    app.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False)
