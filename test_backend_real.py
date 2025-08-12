#!/usr/bin/env python3
"""
Test script for LAIT Real Backend API endpoints
"""

import json
import requests
import time

BASE_URL = "http://localhost:5003"

def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_register():
    """Test user registration"""
    print("\nTesting /api/auth/register...")
    user_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "company": "Test Company"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 201:
            return result.get('token')
        elif response.status_code == 409:  # User already exists
            print("User already exists, trying login...")
            return test_login()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\nTesting /api/auth/login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            return result.get('token')
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_upload_json(token):
    """Test invoice upload with JSON data"""
    print("\nTesting /api/invoices/upload (JSON)...")
    
    invoice_data = {
        "vendor": "Test Law Firm",
        "invoice_number": "INV-2025-001",
        "date": "2025-08-11",
        "lines": [
            {
                "description": "Legal Research",
                "hours": 5.0,
                "rate": 450.0
            },
            {
                "description": "Document Review", 
                "hours": 12.0,  # This should be flagged (>10 hours)
                "rate": 950.0   # This should be flagged (>900 rate)
            },
            {
                "description": "Court Filing",
                "hours": 2.0,
                "rate": 300.0
            }
        ]
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/invoices/upload", json=invoice_data, headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_upload_text_file(token):
    """Test invoice upload with text file"""
    print("\nTesting /api/invoices/upload (Text File)...")
    
    # Create a simple CSV-like text file
    text_content = """Legal Analysis,8.0,500.0,4000.0
Contract Review,15.0,600.0,9000.0
Client Meeting,3.0,400.0,1200.0"""
    
    files = {'file': ('test_invoice.csv', text_content, 'text/plain')}
    data = {'vendor': 'CSV Test Firm', 'invoice_number': 'CSV-001'}
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/invoices/upload", files=files, data=data, headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_invoices(token):
    """Test getting invoices list"""
    print("\nTesting /api/invoices...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/invoices", headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_dashboard_metrics(token):
    """Test dashboard metrics"""
    print("\nTesting /api/dashboard/metrics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/metrics", headers=headers)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("LAIT Real Backend API Test Suite")
    print("=" * 40)
    
    # Test health endpoint
    if not test_health():
        print("Health check failed - server might not be running")
        return
    
    # Test authentication
    token = test_register()
    if not token:
        print("Authentication failed")
        return
    
    print(f"\nAuthentication successful! Token: {token[:20]}...")
    
    # Test invoice uploads
    print("\n" + "=" * 40)
    print("Testing Invoice Upload Endpoints")
    print("=" * 40)
    
    test_upload_json(token)
    test_upload_text_file(token)
    
    # Test data retrieval
    print("\n" + "=" * 40)
    print("Testing Data Retrieval Endpoints")
    print("=" * 40)
    
    test_get_invoices(token)
    test_dashboard_metrics(token)
    
    print("\n" + "=" * 40)
    print("All tests completed!")

if __name__ == "__main__":
    main()
