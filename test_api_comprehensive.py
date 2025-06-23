#!/usr/bin/env python3
"""
Comprehensive API Test Suite
Tests all major endpoints of the LAIT system
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5003"

def test_endpoint(name, url, expected_keys=None):
    """Test a single endpoint"""
    try:
        print(f"Testing {name}...")
        response = requests.get(f"{BASE_URL}{url}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ {name} - Status: {response.status_code}")
            
            if expected_keys:
                for key in expected_keys:
                    if key in data:
                        print(f"    ✓ {key}: {type(data[key]).__name__}")
                    else:
                        print(f"    ❌ Missing key: {key}")
                        
            return True
        else:
            print(f"  ❌ {name} - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ {name} - Error: {str(e)}")
        return False

def main():
    """Run comprehensive API tests"""
    print("🚀 LAIT System - Comprehensive API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", "/api/health", ["status", "database", "ml_models", "live_data"]),
        ("Dashboard Metrics", "/api/dashboard/metrics", ["totalSpend", "invoiceCount", "vendorCount", "recentInvoices"]),
        ("Analytics - Spend Trends", "/api/analytics/spend-trends", ["labels", "datasets", "summary"]),
        ("Vendors List", "/api/vendors", None),
        ("Invoices List", "/api/invoices", None),
        ("Live Data Status", "/api/live-data/status", ["service_status", "active_sources"]),
        ("Live Data Insights", "/api/live-data/insights", ["insights", "total_count"]),
        ("Live Data Sources", "/api/live-data/sources", ["sources", "total_sources"]),
        ("Diagnostics", "/api/diagnostics", ["overall_status", "checks"]),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, endpoint, keys in tests:
        if test_endpoint(test_name, endpoint, keys):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! System is ready for production.")
        return 0
    else:
        print("❌ Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
