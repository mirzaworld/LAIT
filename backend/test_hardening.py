#!/usr/bin/env python3
"""
Test script for hardened LAIT backend
Tests rate limiting, file validation, error responses
"""

import requests
import json
import time
from io import BytesIO

BASE_URL = "http://localhost:5003"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_login_rate_limit():
    """Test login rate limiting (5 per minute)"""
    print("\n=== Testing Login Rate Limiting ===")
    
    login_data = {
        "email": "nonexistent@test.com",
        "password": "wrongpassword"
    }
    
    results = []
    for i in range(7):  # Try 7 times, should get 429 after 5th
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data,
                timeout=5
            )
            print(f"Login attempt {i+1}: {response.status_code}")
            if response.status_code == 429:
                print(f"Rate limit response: {response.text}")
            results.append(response.status_code)
            time.sleep(0.5)
        except Exception as e:
            print(f"Login attempt {i+1} failed: {e}")
            results.append(0)
    
    # Check if we got rate limited
    rate_limited = 429 in results
    print(f"Rate limiting working: {rate_limited}")
    return rate_limited

def test_file_validation():
    """Test file upload validation"""
    print("\n=== Testing File Upload Validation ===")
    
    # First register a user
    register_data = {
        "email": f"test{int(time.time())}@test.com",
        "password": "testpassword123",
        "firstName": "Test",
        "lastName": "User"
    }
    
    try:
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data, timeout=5)
        if reg_response.status_code != 201:
            print(f"Registration failed: {reg_response.text}")
            return False
        
        token = reg_response.json().get('token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test invalid file type
        files = {'file': ('test.exe', b'invalid content', 'application/octet-stream')}
        response = requests.post(f"{BASE_URL}/api/invoices/upload", files=files, headers=headers, timeout=5)
        print(f"Invalid file type test: {response.status_code}")
        if response.status_code in [400, 415]:
            print(f"Error response: {response.text}")
        
        # Test valid file type
        files = {'file': ('test.txt', b'Valid invoice content', 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/invoices/upload", files=files, headers=headers, timeout=5)
        print(f"Valid file type test: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"File validation test failed: {e}")
        return False

def test_consistent_errors():
    """Test consistent error responses"""
    print("\n=== Testing Consistent Error Responses ===")
    
    try:
        # Test missing body
        response = requests.post(f"{BASE_URL}/api/auth/login", timeout=5)
        print(f"Missing body: {response.status_code}")
        if response.status_code == 400:
            error_data = response.json()
            has_error = 'error' in error_data
            has_code = 'code' in error_data
            print(f"Has error field: {has_error}, Has code field: {has_code}")
            print(f"Response: {error_data}")
        
        return True
        
    except Exception as e:
        print(f"Error response test failed: {e}")
        return False

def main():
    print("=== LAIT Backend Hardening Tests ===")
    
    # Test if server is running
    if not test_health():
        print("❌ Backend server is not accessible")
        return
    
    print("✅ Backend server is running")
    
    # Run tests
    tests = [
        ("Rate Limiting", test_login_rate_limit),
        ("File Validation", test_file_validation), 
        ("Consistent Errors", test_consistent_errors)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n--- Running {test_name} Test ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n=== Test Results Summary ===")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")

if __name__ == "__main__":
    main()
