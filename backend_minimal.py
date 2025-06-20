#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)

# Simple CORS configuration for debugging
CORS(app)

# Sample data
invoices = [
    {"id": "INV-001", "vendor": "Morrison & Foerster LLP", "amount": 45750, "status": "approved", "date": "2024-01-15", "riskScore": 25, "category": "Litigation", "hours": 65, "rate": 950},
    {"id": "INV-002", "vendor": "Baker McKenzie", "amount": 23400, "status": "pending", "date": "2024-01-14", "riskScore": 45, "category": "Corporate", "hours": 32, "rate": 850},
]

uploaded_invoices = []

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/invoices')
def get_invoices():
    return jsonify(invoices + uploaded_invoices)

@app.route('/api/dashboard/metrics')
def get_metrics():
    all_invoices = invoices + uploaded_invoices
    total_spend = sum(inv["amount"] for inv in all_invoices)
    return jsonify({
        "total_spend": int(total_spend),
        "invoice_count": len(all_invoices),
        "active_matters": 5,
        "risk_factors_count": 35,
        "high_risk_invoices_count": len([inv for inv in all_invoices if inv["riskScore"] >= 70]),
        "avg_processing_time": 3.2,
        "spend_change_percentage": 15.3,
        "uploaded_invoices_count": len(uploaded_invoices),
        "trend_data": {"monthly_spend": [{"period": f"2024-{i+1:02d}", "amount": random.randint(15000, 25000)} for i in range(12)]}
    })

@app.route('/api/vendors')
def get_vendors():
    return jsonify([
        {"id": "vendor-1", "name": "Morrison & Foerster LLP", "category": "Litigation", "spend": 45750},
        {"id": "vendor-2", "name": "Baker McKenzie", "category": "Corporate", "spend": 23400}
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

if __name__ == '__main__':
    print("🚀 Starting LAIT Legal Intelligence API on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
