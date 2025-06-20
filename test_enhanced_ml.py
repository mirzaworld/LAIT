#!/usr/bin/env python3
"""
Test the enhanced ML invoice analysis functionality
"""
import json
import requests
from datetime import datetime

# Sample invoice data for testing
test_invoice = {
    "id": "test-001",
    "amount": 15500.50,
    "currency": "USD",
    "date": "2024-12-15",
    "vendor": "BigLaw Firm",
    "line_items": [
        {
            "description": "Corporate merger due diligence review",
            "hours": 8.5,
            "rate": 1250.0,
            "amount": 10625.0,
            "attorney": "Senior Partner Smith"
        },
        {
            "description": "Document review and analysis", 
            "hours": 12.0,
            "rate": 350.0,
            "amount": 4200.0,
            "attorney": "Associate Johnson"
        },
        {
            "description": "Client meeting and strategy session",
            "hours": 2.0,
            "rate": 450.0,
            "amount": 900.0,
            "attorney": "Counsel Williams"
        }
    ]
}

def test_enhanced_analysis():
    """Test the enhanced invoice analysis"""
    print("🧪 Testing Enhanced ML Invoice Analysis")
    print("=" * 50)
    
    # Test the direct enhanced analyzer
    try:
        print("📊 Running enhanced analysis on test invoice...")
        print(f"Invoice amount: ${test_invoice['amount']:,.2f}")
        print(f"Line items: {len(test_invoice['line_items'])}")
        
        # Import and test the enhanced analyzer directly
        import sys
        sys.path.append('/app/backend')
        from models.enhanced_invoice_analyzer import analyze_invoice_enhanced
        
        result = analyze_invoice_enhanced(test_invoice)
        
        print("\n🎯 Analysis Results:")
        print(f"Analysis timestamp: {result.get('analysis_timestamp', 'N/A')}")
        
        # Display outlier analysis
        outlier_analysis = result.get('outlier_analysis', {})
        print(f"\n🔍 Outlier Detection:")
        print(f"  Has outliers: {outlier_analysis.get('has_outliers', False)}")
        print(f"  Overall score: {outlier_analysis.get('overall_score', 0):.3f}")
        print(f"  Outlier items: {len(outlier_analysis.get('outlier_items', []))}")
        
        for item in outlier_analysis.get('outlier_items', []):
            print(f"    - {item['description'][:50]}... (Score: {item['outlier_score']:.3f})")
        
        # Display rate analysis
        rate_analysis = result.get('rate_analysis', {})
        print(f"\n💰 Rate Analysis:")
        print(f"  Average rate: ${rate_analysis.get('average_rate', 0):.2f}/hour")
        print(f"  Market position: {rate_analysis.get('market_position', 'unknown')}")
        print(f"  Rate outliers: {len(rate_analysis.get('rate_outliers', []))}")
        
        for comparison in rate_analysis.get('benchmark_comparisons', []):
            print(f"    - Rate: ${comparison['actual_rate']:.0f} vs Market: ${comparison['benchmark_mean']:.0f} ({comparison['market_position']})")
        
        # Display insights
        insights = result.get('insights', [])
        print(f"\n💡 Key Insights:")
        for insight in insights:
            print(f"  {insight}")
        
        # Display recommendations
        recommendations = result.get('recommendations', [])
        print(f"\n📋 Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
        
        print("\n✅ Enhanced ML analysis completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_status():
    """Test model loading status"""
    print("\n🔧 Testing ML Model Status")
    print("-" * 30)
    
    try:
        import sys
        sys.path.append('/app/backend')
        from models.enhanced_invoice_analyzer import EnhancedInvoiceAnalyzer
        
        analyzer = EnhancedInvoiceAnalyzer()
        
        print(f"Models directory: {analyzer.models_dir}")
        print(f"Loaded models: {list(analyzer.models.keys())}")
        print(f"Available scalers: {list(analyzer.scalers.keys())}")
        print(f"Rate benchmarks: {len(analyzer.rate_benchmarks)} practice areas")
        
        if analyzer.rate_benchmarks:
            print("\nBenchmark coverage:")
            for area, roles in analyzer.rate_benchmarks.items():
                if isinstance(roles, dict):
                    print(f"  {area}: {list(roles.keys())}")
        
        print("✅ Model status check completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking model status: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 LAIT Enhanced ML Analysis Test Suite")
    print("=" * 60)
    
    # Test model status first
    status_ok = test_model_status()
    
    if status_ok:
        # Run enhanced analysis test
        analysis_ok = test_enhanced_analysis()
        
        if analysis_ok:
            print(f"\n🎉 All tests passed! Enhanced ML system is working correctly.")
        else:
            print(f"\n⚠️ Analysis test failed. Check the error details above.")
    else:
        print(f"\n⚠️ Model status check failed. Models may not be loaded correctly.")
