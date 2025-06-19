#!/usr/bin/env python3
"""
Demo script to show all LAIT AI/ML capabilities
"""
import sys
sys.path.append('/app/backend')

from models.invoice_analyzer import InvoiceAnalyzer
from models.risk_predictor import RiskPredictor
from models.vendor_analyzer import VendorAnalyzer
from models.matter_analyzer import MatterAnalyzer
import json

def demo_invoice_analysis():
    """Demo invoice anomaly detection"""
    print("🔍 INVOICE ANOMALY DETECTION DEMO")
    print("=" * 50)
    
    analyzer = InvoiceAnalyzer()
    
    # Sample invoice data
    sample_invoice = {
        'id': 1,
        'amount': 50000,
        'description': 'Legal services for contract review',
        'vendor_name': 'Smith & Associates',
        'line_items': [
            {
                'description': 'Contract review and analysis',
                'hours': 40,
                'rate': 500,
                'amount': 20000,
                'timekeeper': 'John Smith',
                'timekeeper_title': 'Partner'
            },
            {
                'description': 'Research and documentation',
                'hours': 50,  # Unusual high hours - potential anomaly
                'rate': 600,  # High rate
                'amount': 30000,
                'timekeeper': 'Jane Doe',
                'timekeeper_title': 'Partner'
            }
        ]
    }
    
    # Analyze invoice
    result = analyzer.analyze_invoice(sample_invoice)
    
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"Status: {result['status']}")
    print(f"Anomalies Found: {len(result['anomalies'])}")
    
    for i, anomaly in enumerate(result['anomalies'], 1):
        print(f"  {i}. {anomaly['type']}: {anomaly['description']}")
    
    print(f"Recommendations: {len(result['recommendations'])}")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec['action']} (Priority: {rec['priority']})")
    
    print()

def demo_risk_prediction():
    """Demo risk score prediction"""
    print("⚠️ RISK PREDICTION DEMO")
    print("=" * 50)
    
    predictor = RiskPredictor()
    
    # Sample invoice for risk prediction
    invoice_data = {
        'amount': 75000,
        'hours': 150,
        'rate': 500,
        'timekeeper_count': 3,
        'line_item_count': 8,
        'description': 'Complex litigation matter with multiple depositions',
        'is_litigation': True,
        'has_expenses': True,
        'days_to_submit': 45
    }
    
    risk_score = predictor.predict_risk(invoice_data)
    print(f"Predicted Risk Score: {risk_score:.1f}/100")
    
    if risk_score > 80:
        print("🔴 HIGH RISK - Requires immediate review")
    elif risk_score > 60:
        print("🟡 MEDIUM RISK - Flag for review")
    else:
        print("🟢 LOW RISK - Normal processing")
    
    print()

def demo_vendor_analysis():
    """Demo vendor performance analysis"""
    print("👥 VENDOR ANALYSIS DEMO")
    print("=" * 50)
    
    analyzer = VendorAnalyzer()
    
    # Sample vendor data
    vendor_data = {
        'vendor_id': 1,
        'vendor_name': 'Premium Law Firm',
        'avg_rate': 550,
        'total_spend': 500000,
        'matter_count': 15,
        'avg_hours_per_matter': 120,
        'on_time_delivery': 0.95,
        'quality_score': 0.88
    }
    
    analysis = analyzer.analyze_vendor(vendor_data)
    
    print(f"Vendor: {vendor_data['vendor_name']}")
    print(f"Performance Cluster: {analysis['cluster']}")
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"Overall Score: {analysis['performance_score']:.1f}/10")
    
    print("\nRecommendations:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print()

def demo_matter_forecasting():
    """Demo matter expense forecasting"""
    print("📊 MATTER EXPENSE FORECASTING DEMO")
    print("=" * 50)
    
    analyzer = MatterAnalyzer()
    
    # Sample matter for forecasting
    matter_id = 1
    forecast = analyzer.forecast_expenses(matter_id)
    
    print(f"Matter ID: {matter_id}")
    print(f"Forecasted Total Cost: ${forecast['forecasted_total']:,.2f}")
    print(f"Current Spend: ${forecast['current_spend']:,.2f}")
    print(f"Remaining Budget: ${forecast['remaining_budget']:,.2f}")
    print(f"Confidence Level: {forecast['confidence']:.1%}")
    
    if forecast['forecasted_total'] > forecast.get('budget', float('inf')):
        print("⚠️ WARNING: Forecasted cost exceeds budget!")
    
    print()

def main():
    """Run all ML demos"""
    print("🤖 LAIT AI/ML CAPABILITIES DEMONSTRATION")
    print("🏛️ Legal AI Invoice Tracking System")
    print("=" * 60)
    print()
    
    try:
        # Run all demos
        demo_invoice_analysis()
        demo_risk_prediction() 
        demo_vendor_analysis()
        demo_matter_forecasting()
        
        print("✅ All ML models demonstrated successfully!")
        print()
        print("🔧 Available ML Models:")
        print("  • Invoice Anomaly Detection (Isolation Forest)")
        print("  • Risk Score Prediction (Random Forest)")
        print("  • Vendor Performance Clustering (K-Means)")
        print("  • Matter Expense Forecasting (Gradient Boosting)")
        print("  • NLP Text Analysis (spaCy)")
        print("  • Outlier Detection (Isolation Forest)")
        
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
