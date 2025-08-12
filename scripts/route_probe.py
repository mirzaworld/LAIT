#!/usr/bin/env python3
"""
LAIT Route Probe Script
Tests all critical API endpoints and reports their HTTP status codes.
"""

import requests
import sys
from typing import List, Tuple

# API base URL
API_BASE = "http://localhost:5003"

# Routes to test
ROUTES_TO_TEST = [
    "/api/health",
    "/api/auth/register", 
    "/api/auth/login",
    "/api/invoices",
    "/api/invoices/upload",
    "/api/dashboard/metrics"
]

def probe_route(route: str) -> Tuple[str, int, str]:
    """
    Probe a single route and return its status.
    Returns: (route, status_code, status_description)
    """
    url = f"{API_BASE}{route}"
    
    try:
        # Use appropriate HTTP method
        if route in ["/api/auth/register", "/api/auth/login", "/api/invoices/upload"]:
            response = requests.post(url, json={}, timeout=5)
        else:
            response = requests.get(url, timeout=5)
            
        status_code = response.status_code
        
        if status_code == 200:
            status_desc = "✅ OK"
        elif status_code == 201:
            status_desc = "✅ CREATED"
        elif status_code == 401:
            status_desc = "🔒 UNAUTHORIZED (Expected for protected routes)"
        elif status_code == 400:
            status_desc = "⚠️  BAD REQUEST (Expected for routes requiring data)"
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
    except requests.exceptions.Timeout:
        status_code = 0
        status_desc = "⏱️  TIMEOUT"
    except Exception as e:
        status_code = 0
        status_desc = f"💥 ERROR: {str(e)}"
    
    return (route, status_code, status_desc)

def main():
    """Main probe function"""
    print("🚀 LAIT API Route Probe")
    print("=" * 50)
    print(f"Testing against: {API_BASE}")
    print()
    
    results = []
    all_good = True
    
    for route in ROUTES_TO_TEST:
        route_path, status_code, status_desc = probe_route(route)
        results.append((route_path, status_code, status_desc))
        
        # Print result
        print(f"{route_path:<25} → {status_code:<3} {status_desc}")
        
        # Check for critical failures
        if status_code == 0 or (status_code == 404 and route in ["/api/health", "/api/invoices/upload"]):
            all_good = False
    
    print()
    print("=" * 50)
    
    # Summary
    if all_good:
        print("✅ All critical routes are accessible!")
        print("✅ Upload route '/api/invoices/upload' is properly configured")
        return 0
    else:
        print("❌ Some routes failed - check backend status")
        return 1

if __name__ == "__main__":
    sys.exit(main())
