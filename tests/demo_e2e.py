#!/usr/bin/env python3
"""
LAIT E2E Test Demo

Quick demo of the E2E test functionality with fallback for database issues.
This shows the test structure and what would happen with a properly configured backend.
"""

import requests
import json

API_BASE_URL = "http://localhost:5003/api"

def test_api_connectivity():
    """Test basic API connectivity"""
    print("🔍 Testing API connectivity...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"📡 GET /health -> {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data.get('status', 'unknown')}")
            return True
        elif response.status_code == 500:
            data = response.json()
            error = data.get('error', 'Unknown error')
            print(f"⚠️  API responded but has database issues:")
            print(f"   Error: {error}")
            return False
        else:
            print(f"❌ API returned unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API - server not running")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def demo_test_structure():
    """Show what the E2E tests would do"""
    print("\n📋 E2E Test Structure Demo:")
    print("=" * 40)
    
    test_cases = [
        "1. 🔍 Health Check - Verify API is running",
        "2. 👤 User Registration - Create test account",
        "3. 🔐 User Login - Authenticate user",
        "4. 📄 Invoice Upload - Upload sample invoice",
        "5. 📋 Invoice List - Retrieve user invoices", 
        "6. 📊 Analytics Summary - Get dashboard metrics",
        "7. ✅ Data Consistency - Verify data integrity"
    ]
    
    for test_case in test_cases:
        print(f"   {test_case}")
    
    print("\n📊 Test Coverage:")
    print("   ✅ Authentication (register/login)")
    print("   ✅ File Upload (PDF/TXT processing)")
    print("   ✅ Data Retrieval (invoices/analytics)")
    print("   ✅ AI Analysis (risk scoring)")
    print("   ✅ Data Integrity (consistency checks)")

def show_sample_test_data():
    """Show sample test data that would be used"""
    print("\n📝 Sample Test Data:")
    print("=" * 40)
    
    # Sample user data
    user_data = {
        "email": "test@lait.example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "company": "LAIT Test Company"
    }
    
    print("👤 Test User:")
    for key, value in user_data.items():
        if key != 'password':
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {'*' * len(value)}")
    
    print("\n📄 Sample Invoice:")
    print("   Vendor: Legal Services LLC")
    print("   Amount: $5,967.50")
    print("   Hours: 15.5")
    print("   Rate: $350/hour")
    print("   Format: Text file (.txt)")

def show_expected_results():
    """Show what successful test results would look like"""
    print("\n🎯 Expected Test Results:")
    print("=" * 40)
    
    # Sample successful responses
    print("📡 Registration Response:")
    reg_response = {
        "message": "User registered successfully",
        "token": "eyJ0eXAiOiJKV1Q...",
        "user": {
            "id": "user_123",
            "email": "test@lait.example.com",
            "first_name": "Test",
            "last_name": "User"
        }
    }
    print(f"   {json.dumps(reg_response, indent=2)}")
    
    print("\n📄 Upload Response:")
    upload_response = {
        "message": "Invoice uploaded successfully",
        "invoice": {
            "id": "INV-001",
            "vendor": "Legal Services LLC",
            "amount": 5967.50,
            "filename": "test_invoice.txt"
        },
        "analysis": {
            "risk_score": 25,
            "risk_level": "low",
            "category": "Legal Services",
            "recommendations": ["Review billing rates", "Verify hours worked"]
        }
    }
    print(f"   {json.dumps(upload_response, indent=2)}")

def main():
    """Main demo function"""
    print("🧪 LAIT E2E Test Suite Demo")
    print("=" * 50)
    
    # Test API connectivity
    api_working = test_api_connectivity()
    
    # Show test structure regardless of API status
    demo_test_structure()
    show_sample_test_data()
    show_expected_results()
    
    print("\n" + "=" * 50)
    
    if api_working:
        print("✅ API is healthy - E2E tests ready to run!")
        print("💡 Run: ./backend/venv_real/bin/python3 tests/test_e2e.py")
    else:
        print("⚠️  API has database connection issues")
        print("💡 To run E2E tests:")
        print("   1. Set up PostgreSQL database")
        print("   2. Or configure SQLite for testing")
        print("   3. Then run: ./backend/venv_real/bin/python3 tests/test_e2e.py")
    
    print("\n📁 Test Files Created:")
    print("   📄 tests/test_e2e.py - Standalone E2E tests")
    print("   📄 tests/test_e2e_pytest.py - Pytest framework tests")  
    print("   📄 tests/run_tests.sh - Automated test runner")
    print("   📄 tests/requirements.txt - Test dependencies")
    print("   📄 tests/README.md - Comprehensive documentation")

if __name__ == "__main__":
    main()
