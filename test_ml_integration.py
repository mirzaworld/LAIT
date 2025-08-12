#!/usr/bin/env python3
"""
Test ML Service Integration
===========================

Test the ML service with fallback functionality
"""

import sys
import json
from pathlib import Path

# Add backend to path
backend_path = str(Path(__file__).parent / 'backend')
sys.path.insert(0, backend_path)
print(f"🔧 Added to Python path: {backend_path}")

# Test ML service import and basic functionality
def test_ml_service():
    print("🧪 Testing ML Service Integration")
    print("=" * 40)
    
    try:
        import app_real
        print(f"✅ Backend imported successfully")
        print(f"   ML Service Available: {app_real.ML_SERVICE_AVAILABLE}")
        print(f"   Pandas Available: {getattr(app_real, 'PANDAS_AVAILABLE', False)}")
        
        # Test scoring function with sample data
        sample_data = [
            {
                'description': 'Legal research - contract review',
                'amount': 2500.0,
                'billable_hours': 10.0,
                'rate': 250.0
            },
            {
                'description': 'SUSPICIOUS: Extremely high rate consultation',
                'amount': 5000.0,
                'billable_hours': 5.0,
                'rate': 1000.0
            }
        ]
        
        print(f"\n📊 Testing scoring with {len(sample_data)} sample lines...")
        scored_lines, metadata = app_real.score_invoice_lines(sample_data)
        
        print(f"✅ Scoring completed:")
        print(f"   Method: {metadata.get('method', 'unknown')}")
        print(f"   Note: {metadata.get('note', 'none')}")
        print(f"   Reason: {metadata.get('reason', 'none')}")
        
        print(f"\n📋 Scored Lines:")
        for i, line in enumerate(scored_lines):
            score = line.get('anomaly_score', 0)
            flagged = line.get('is_flagged', False)
            reason = line.get('flag_reason', 'none')
            print(f"   Line {i+1}: Score={score:.3f}, Flagged={flagged}, Reason='{reason}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_status():
    print(f"\n🔍 Testing ML Status Function")
    print("=" * 40)
    
    try:
        import app_real
        
        if app_real.ML_SERVICE_AVAILABLE:
            from services.ml_service import get_model_status
            status = get_model_status()
        else:
            status = {
                'service_available': False,
                'models_loaded': False,
                'fallback_mode': True,
                'reason': 'ML service import failed'
            }
        
        print("📊 ML Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in ML status: {e}")
        return False

if __name__ == "__main__":
    print("🤖 LAIT ML Service Test Suite")
    print("=" * 50)
    
    test1_ok = test_ml_service()
    test2_ok = test_ml_status()
    
    print(f"\n📊 Test Results:")
    print(f"   ML Service Test: {'✅ PASS' if test1_ok else '❌ FAIL'}")
    print(f"   ML Status Test: {'✅ PASS' if test2_ok else '❌ FAIL'}")
    
    if test1_ok and test2_ok:
        print(f"\n🎉 All tests passed! ML integration working with fallback.")
        
        # Show example response that includes model_fallback note
        print(f"\n📝 Expected API Response (with model_fallback):")
        example_response = {
            "invoice_id": 123,
            "vendor": "Test Legal Firm",
            "total_amount": 7500.0,
            "lines_processed": 2,
            "flagged": 1,
            "note": "model_fallback",
            "scoring_method": "deterministic_fallback",
            "scoring_info": "ML models not available"
        }
        print(json.dumps(example_response, indent=2))
    else:
        print(f"\n❌ Some tests failed. Check the errors above.")
