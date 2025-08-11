#!/usr/bin/env python3
"""
Backend API Integration Test
Tests all critical endpoints to verify the application is ready for production
"""
import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:5003"

def test_endpoint(endpoint: str, method: str = "GET", data: dict = None, expected_status: int = 200) -> Dict[str, Any]:
    """Test an endpoint and return result"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}
        
        return {
            "status": "success" if response.status_code == expected_status else "error",
            "status_code": response.status_code,
            "expected_status": expected_status,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    print("🚀 LAIT Backend API Integration Test")
    print("=" * 50)
    
    tests = [
        # Core health endpoints
        ("/api/health", "GET", None, 200),
        ("/api/readiness", "GET", None, 200),
        
        # Dashboard and metrics
        ("/api/dashboard/metrics", "GET", None, 200),
        
        # Notifications
        ("/api/notifications", "GET", None, 200),
        ("/api/notifications/unread-count", "GET", None, 200),
        
        # Auth endpoints
        ("/api/auth/dev-login", "POST", {"username": "test", "password": "test"}, 200),
        
        # Analytics (might be empty but should respond)
        ("/api/analytics/spending-trends", "GET", None, 200),
        ("/api/analytics/vendor-analysis", "GET", None, 200),
        
        # Legal intelligence
        ("/api/legal-intelligence/health", "GET", None, 200),
    ]
    
    results = []
    for endpoint, method, data, expected_status in tests:
        print(f"Testing {method} {endpoint}...")
        result = test_endpoint(endpoint, method, data, expected_status)
        results.append((endpoint, method, result))
        
        if result["status"] == "success":
            print(f"  ✅ PASS (status: {result['status_code']})")
        else:
            print(f"  ❌ FAIL (status: {result.get('status_code', 'N/A')}, expected: {expected_status})")
            if 'message' in result:
                print(f"     Error: {result['message']}")
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, _, result in results if result["status"] == "success")
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Backend is ready for production.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\nFailed tests:")
        for endpoint, method, result in results:
            if result["status"] != "success":
                print(f"  - {method} {endpoint}: {result.get('message', 'Status code mismatch')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
