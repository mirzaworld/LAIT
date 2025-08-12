#!/usr/bin/env python3
"""
LAIT Route Probe Script
=======================

Tests all critical API endpoints and validates response codes.
Provides detailed status reporting for system health validation.
"""

import requests
import json
import sys
from typing import List, Tuple

# API base URL
API_BASE = "http://localhost:5003"

# Routes to test with expected behavior
ROUTES_TO_TEST = [
    ("/api/health", "GET", [200]),
    ("/api/auth/register", "POST", [400, 422]),  # Bad request without proper data
    ("/api/auth/login", "POST", [400, 422]),     # Bad request without proper data
    ("/api/invoices", "GET", [401]),             # Unauthorized without JWT
    ("/api/invoices/upload", "POST", [401]),     # Unauthorized without JWT
    ("/api/dashboard/metrics", "GET", [401]),    # Unauthorized without JWT
    ("/api/ml/status", "GET", [200]),            # Should work without auth
]

def probe_route(route: str, method: str, expected_codes: List[int]) -> Tuple[str, int, str, bool]:
    """
    Probe a single route and return its status.
    Returns: (route, status_code, status_description, is_expected)
    """
    url = f"{API_BASE}{route}"
    
    try:
        # Use appropriate HTTP method
        if method.upper() == "POST":
            response = requests.post(url, json={}, timeout=5)
        else:
            response = requests.get(url, timeout=5)
            
        status_code = response.status_code
        is_expected = status_code in expected_codes
        
        if status_code == 200:
            status_desc = "✅ OK"
        elif status_code == 201:
            status_desc = "✅ CREATED"
        elif status_code == 401:
            status_desc = "🔒 UNAUTHORIZED (Expected for protected routes)" if is_expected else "🔒 UNAUTHORIZED"
        elif status_code == 400:
            status_desc = "⚠️  BAD REQUEST (Expected for routes requiring data)" if is_expected else "⚠️  BAD REQUEST"
        elif status_code == 422:
            status_desc = "⚠️  VALIDATION ERROR (Expected for routes requiring data)" if is_expected else "⚠️  VALIDATION ERROR"
        elif status_code == 404:
            status_desc = "❌ NOT FOUND"
        elif status_code == 405:
            status_desc = "⚠️  METHOD NOT ALLOWED"
        elif status_code >= 500:
            status_desc = "💥 SERVER ERROR"
        else:
            status_desc = f"ℹ️  {response.reason}"
            
    except requests.exceptions.ConnectionError:
        status_code = 0
        status_desc = "🔴 CONNECTION REFUSED - Backend not running?"
        is_expected = False
    except requests.exceptions.Timeout:
        status_code = 0
        status_desc = "⏱️  TIMEOUT"
        is_expected = False
    except Exception as e:
        status_code = 0
        status_desc = f"💥 ERROR: {str(e)}"
        is_expected = False
    
    return (route, status_code, status_desc, is_expected)

def main():
    """Main probe function"""
    print("🚀 LAIT API Route Probe")
    print("=" * 50)
    print(f"Testing against: {API_BASE}")
    print()
    
    results = []
    all_good = True
    
    for route, method, expected_codes in ROUTES_TO_TEST:
        route_path, status_code, status_desc, is_expected = probe_route(route, method, expected_codes)
        results.append((route_path, status_code, status_desc, is_expected))
        
        # Color coding based on expectation
        status_indicator = "✅" if is_expected else "❌"
        
        # Print result
        print(f"{route_path:<25} → {method:<4} {status_code:<3} {status_desc} {status_indicator}")
        
        # Check for critical failures
        if not is_expected or status_code == 0:
            all_good = False
    
    print()
    print("=" * 50)
    
    # Test a legacy route that should return 404
    print("🧪 Testing legacy route (should be 404):")
    legacy_route, legacy_status, legacy_desc, _ = probe_route("/api/upload-invoice", "POST", [404])
    legacy_ok = legacy_status == 404
    legacy_indicator = "✅" if legacy_ok else "❌"
    print(f"{'/api/upload-invoice':<25} → POST {legacy_status:<3} {legacy_desc} {legacy_indicator}")
    
    if not legacy_ok:
        all_good = False
    
    print()
    print("=" * 50)
    
    # Summary
    if all_good:
        print("✅ All critical routes behave as expected!")
        print("✅ Authentication routes properly reject empty requests")
        print("✅ Protected routes require JWT tokens")
        print("✅ Health and ML status endpoints are accessible")
        return 0
    else:
        print("❌ Some routes failed expectations - check backend status")
        return 1

if __name__ == "__main__":
    sys.exit(main())
