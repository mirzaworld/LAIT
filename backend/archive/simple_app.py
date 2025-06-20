#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)

# Configure CORS properly for production use
CORS(app, 
     resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174"]}},
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
     supports_credentials=False)

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

@app.route('/api/vendors')
def get_vendors():
    """Get all vendors with their metrics"""
    all_invoices = invoices + uploaded_invoices
    vendor_data = {}
    
    # Aggregate vendor data
    for inv in all_invoices:
        vendor = inv["vendor"]
        if vendor not in vendor_data:
            vendor_data[vendor] = {
                "id": f"vendor-{len(vendor_data) + 1}",
                "name": vendor,
                "category": inv["category"],
                "spend": 0,
                "matter_count": 0,
                "avg_rate": 0,
                "performance_score": 0,
                "diversity_score": 85,  # Mock data
                "on_time_rate": 0.92,  # Mock data
                "invoice_count": 0,
                "total_hours": 0
            }
        
        vendor_data[vendor]["spend"] += inv["amount"]
        vendor_data[vendor]["invoice_count"] += 1
        vendor_data[vendor]["total_hours"] += inv.get("hours", 0)
        
        # Calculate average rate
        if vendor_data[vendor]["total_hours"] > 0:
            vendor_data[vendor]["avg_rate"] = vendor_data[vendor]["spend"] / vendor_data[vendor]["total_hours"]
        
        # Calculate performance score based on inverse of risk
        avg_risk = sum(invoice["riskScore"] for invoice in all_invoices if invoice["vendor"] == vendor) / vendor_data[vendor]["invoice_count"]
        vendor_data[vendor]["performance_score"] = max(0, 100 - avg_risk)
    
    # Convert to list and add matter count
    vendors_list = []
    for vendor_name, data in vendor_data.items():
        data["matter_count"] = data["invoice_count"]  # Simplified - one matter per invoice
        vendors_list.append(data)
    
    return jsonify(vendors_list)

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
@app.route('/api/analytics/spend-trends')
def get_spend_trends():
    """Get spending trends for charts and analytics"""
    period = request.args.get('period', 'monthly')
    category = request.args.get('category')
    
    all_invoices = invoices + uploaded_invoices
    
    if period == 'monthly':
        # Generate monthly trend data
        monthly_data = []
        for i in range(12):
            month = f"2024-{i+1:02d}"
            month_invoices = [inv for inv in all_invoices if inv.get('date', '').startswith(month)]
            amount = sum(inv['amount'] for inv in month_invoices)
            if amount == 0:  # Fill in some realistic mock data for months with no data
                amount = random.randint(15000, 25000)
            monthly_data.append({
                "month": month,
                "amount": amount,
                "invoice_count": len(month_invoices)
            })
        return jsonify({
            "period": "monthly",
            "data": monthly_data,
            "total": sum(item["amount"] for item in monthly_data),
            "trend": "increasing" if monthly_data[-1]["amount"] > monthly_data[0]["amount"] else "decreasing"
        })
    
    elif period == 'weekly':
        # Generate weekly trend data
        weekly_data = []
        for i in range(8):  # Last 8 weeks
            week_amount = random.randint(3000, 8000)
            weekly_data.append({
                "week": f"Week {i+1}",
                "amount": week_amount,
                "invoice_count": random.randint(1, 3)
            })
        return jsonify({
            "period": "weekly", 
            "data": weekly_data,
            "total": sum(item["amount"] for item in weekly_data),
            "trend": "stable"
        })
    
    else:
        return jsonify({"error": "Unsupported period"}), 400

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

# Report generation endpoints
@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate a comprehensive legal spend report"""
    all_invoices = invoices + uploaded_invoices
    
    # Calculate comprehensive metrics
    total_spend = sum(inv["amount"] for inv in all_invoices)
    total_invoices = len(all_invoices)
    avg_invoice_amount = total_spend / total_invoices if total_invoices > 0 else 0
    high_risk_count = len([inv for inv in all_invoices if inv["riskScore"] >= 70])
    
    # Vendor analysis
    vendor_analysis = {}
    for inv in all_invoices:
        vendor = inv["vendor"]
        if vendor not in vendor_analysis:
            vendor_analysis[vendor] = {"total_spend": 0, "invoice_count": 0, "avg_risk": 0, "invoices": []}
        vendor_analysis[vendor]["total_spend"] += inv["amount"]
        vendor_analysis[vendor]["invoice_count"] += 1
        vendor_analysis[vendor]["invoices"].append(inv)
    
    # Calculate averages
    for vendor, data in vendor_analysis.items():
        data["avg_risk"] = sum(inv["riskScore"] for inv in data["invoices"]) / len(data["invoices"])
        data["avg_amount"] = data["total_spend"] / data["invoice_count"]
    
    # Category analysis
    category_analysis = {}
    for inv in all_invoices:
        category = inv["category"]
        if category not in category_analysis:
            category_analysis[category] = {"total_spend": 0, "invoice_count": 0}
        category_analysis[category]["total_spend"] += inv["amount"]
        category_analysis[category]["invoice_count"] += 1
    
    report_data = {
        "report_id": f"LAIT-RPT-{len(all_invoices)}-{random.randint(1000, 9999)}",
        "generated_date": "2024-01-20",
        "period": "All Time",
        "executive_summary": {
            "total_spend": total_spend,
            "total_invoices": total_invoices,
            "avg_invoice_amount": round(avg_invoice_amount, 2),
            "high_risk_invoices": high_risk_count,
            "risk_percentage": round((high_risk_count / total_invoices * 100) if total_invoices > 0 else 0, 1),
            "top_vendor": max(vendor_analysis.keys(), key=lambda v: vendor_analysis[v]["total_spend"]) if vendor_analysis else "N/A",
            "cost_savings_opportunities": round(total_spend * 0.15, 2)  # Estimated 15% savings opportunity
        },
        "vendor_analysis": [
            {
                "vendor": vendor,
                "total_spend": data["total_spend"],
                "invoice_count": data["invoice_count"],
                "avg_invoice_amount": round(data["avg_amount"], 2),
                "avg_risk_score": round(data["avg_risk"], 1),
                "performance_grade": "A" if data["avg_risk"] < 30 else "B" if data["avg_risk"] < 60 else "C",
                "recommendations": get_vendor_recommendations(data["avg_risk"], data["total_spend"])
            }
            for vendor, data in vendor_analysis.items()
        ],
        "category_analysis": [
            {
                "category": category,
                "total_spend": data["total_spend"],
                "invoice_count": data["invoice_count"],
                "percentage_of_total": round((data["total_spend"] / total_spend * 100) if total_spend > 0 else 0, 1)
            }
            for category, data in category_analysis.items()
        ],
        "risk_analysis": {
            "total_risk_factors": sum(inv["riskScore"] for inv in all_invoices),
            "avg_risk_score": round(sum(inv["riskScore"] for inv in all_invoices) / len(all_invoices), 1) if all_invoices else 0,
            "high_risk_invoices": [
                {
                    "id": inv["id"],
                    "vendor": inv["vendor"],
                    "amount": inv["amount"],
                    "risk_score": inv["riskScore"],
                    "reason": get_risk_reason(inv["riskScore"])
                }
                for inv in all_invoices if inv["riskScore"] >= 70
            ]
        },
        "recommendations": [
            "Implement volume discounts with top 3 vendors",
            "Review high-risk invoices for potential overbilling",
            "Consider alternative fee arrangements for recurring work",
            "Establish spending caps for Q4 to stay within budget",
            "Negotiate better rates with underperforming vendors"
        ]
    }
    
    return jsonify(report_data)

def get_vendor_recommendations(avg_risk, total_spend):
    recommendations = []
    if avg_risk > 70:
        recommendations.append("High risk vendor - require additional oversight")
    if avg_risk > 50:
        recommendations.append("Review billing practices and rate structures")
    if total_spend > 50000:
        recommendations.append("Negotiate volume discounts")
    if len(recommendations) == 0:
        recommendations.append("Preferred vendor - maintain current relationship")
    return recommendations

def get_risk_reason(risk_score):
    if risk_score >= 90:
        return "Extremely high rates and billing anomalies detected"
    elif risk_score >= 70:
        return "High rates or unusual billing patterns"
    elif risk_score >= 50:
        return "Moderate billing irregularities"
    else:
        return "Low risk profile"

@app.route('/api/reports/<report_id>')
def get_report(report_id):
    """Get a specific report by ID (mock implementation)"""
    # In a real implementation, this would fetch from a database
    return jsonify({
        "error": "Report retrieval not implemented in this demo",
        "message": "Use POST /api/reports/generate to create a new report"
    })

if __name__ == '__main__':
    print("🚀 Starting LAIT Legal Intelligence API on port 5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
