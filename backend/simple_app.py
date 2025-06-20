#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Sample data
invoices = [
    {"id": "INV-001", "vendor": "Morrison & Foerster LLP", "amount": 45750, "status": "approved", "date": "2024-01-15", "riskScore": 25, "category": "Litigation", "hours": 65, "rate": 950},
    {"id": "INV-002", "vendor": "Baker McKenzie", "amount": 23400, "status": "pending", "date": "2024-01-14", "riskScore": 45, "category": "Corporate", "hours": 32, "rate": 850},
    {"id": "INV-003", "vendor": "Latham & Watkins", "amount": 67200, "status": "flagged", "date": "2024-01-13", "riskScore": 78, "category": "Corporate", "hours": 85, "rate": 1250},
    {"id": "INV-004", "vendor": "Skadden, Arps", "amount": 89100, "status": "approved", "date": "2024-01-12", "riskScore": 32, "category": "Corporate", "hours": 78, "rate": 1200},
    {"id": "INV-005", "vendor": "Gibson Dunn", "amount": 34500, "status": "processing", "date": "2024-01-11", "riskScore": 15, "category": "Employment", "hours": 48, "rate": 750}
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

@app.route('/api/upload-invoice', methods=['POST'])
def upload_invoice():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Create new invoice
        new_invoice = {
            "id": f"INV-{len(uploaded_invoices) + 6:03d}",
            "vendor": file.filename.split('.')[0].replace('_', ' ').title(),
            "amount": round(random.uniform(5000, 75000), 2),
            "status": "pending",
            "date": "2024-06-20",
            "riskScore": random.randint(10, 90),
            "category": "General",
            "hours": random.randint(20, 100),
            "rate": random.randint(500, 1200)
        }
        
        uploaded_invoices.append(new_invoice)
        
        return jsonify({
            "invoice_added": True,
            "invoice_id": new_invoice["id"],
            "analysis": {
                "risk_score": new_invoice["riskScore"],
                "risk_level": "high" if new_invoice["riskScore"] >= 70 else "medium" if new_invoice["riskScore"] >= 40 else "low",
                "recommendations": ["Review invoice details", "Verify billing accuracy"]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Advanced analytics endpoints
@app.route('/api/analytics/predictive')
def get_predictive_analytics():
    return jsonify({
        "predictions": {
            "next_month_spend": {"amount": 225000, "confidence": 0.85, "trend": "increasing"},
            "budget_alert": {"probability": 0.73, "message": "High probability of exceeding budget in Q4"}
        },
        "ai_insights": {
            "cost_optimization": "Consider consolidating vendors for better rates",
            "compliance_score": 92,
            "efficiency_rating": "A-"
        }
    })

@app.route('/api/analytics/vendor-performance')
def get_vendor_performance():
    vendor_data = []
    for vendor in set(inv["vendor"] for inv in invoices):
        vendor_invoices = [inv for inv in invoices if inv["vendor"] == vendor]
        avg_risk = sum(inv["riskScore"] for inv in vendor_invoices) / len(vendor_invoices)
        performance_score = max(0, 100 - avg_risk)
        
        vendor_data.append({
            "vendor": vendor,
            "performance_score": round(performance_score, 1),
            "total_spend": sum(inv["amount"] for inv in vendor_invoices),
            "invoice_count": len(vendor_invoices),
            "avg_risk_score": round(avg_risk, 1),
            "efficiency_rating": "A" if performance_score > 90 else "B" if performance_score > 80 else "C",
            "recommendation": "Preferred vendor" if performance_score > 85 else "Monitor closely"
        })
    
    return jsonify({"vendor_performance": vendor_data, "summary": {"total_vendors": len(vendor_data)}})

@app.route('/api/analytics/budget-forecast')
def get_budget_forecast():
    base_forecast = sum(inv["amount"] for inv in invoices) * 1.2
    return jsonify({
        "forecast": {
            "annual_projection": round(base_forecast, 2),
            "confidence_interval": {"optimistic": round(base_forecast * 0.9, 2), "pessimistic": round(base_forecast * 1.15, 2)}
        },
        "recommendations": [
            "Set Q4 budget cap at $250K to stay on track",
            "Negotiate volume discounts with top 3 vendors",
            "Consider alternative fee arrangements for large matters"
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting LAIT Legal Intelligence API on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
