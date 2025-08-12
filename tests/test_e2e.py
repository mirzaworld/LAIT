#!/usr/bin/env python3
"""
LAIT Platform End-to-End Tests
==============================

This module contains comprehensive E2E tests for the LAIT platform,
testing the complete workflow from user registration to invoice analysis.

Tests:
- Calls the running backend on http://localhost:5003
- Registers a user, uploads a small text invoice, asserts invoices_count>=1
- Uses 'requests' and pytest

Author: LAIT Development Team
Version: 1.0.0
"""

import pytest
import requests
import time
import tempfile
import os


def test_api_health():
    """Test API health endpoint."""
    response = requests.get("http://localhost:5003/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True
    print("✅ API health check passed")


def test_user_registration_upload_and_list():
    """
    Main E2E test:
    - Registers a user
    - Uploads a small text invoice  
    - Lists invoices
    - Asserts invoices_count >= 1
    """
    
    # Generate unique email
    test_email = f"pytest+{int(time.time())}@lait.com"
    test_password = "TestPytest123!"
    
    # Step 1: Register user
    payload = {
        "email": test_email,
        "password": test_password,
        "firstName": "Pytest",
        "lastName": "Tester",
        "company": "LAIT Test Suite"
    }
    
    response = requests.post(
        "http://localhost:5003/api/auth/register",
        json=payload
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Extract token
    token = data.get("token") or data.get("access_token")
    assert token is not None, f"No token in response: {data}"
    
    print(f"✅ User registered: {test_email}")
    print(f"✅ Token captured: {token[:20]}...")
    
    # Step 2: Upload small text invoice
    invoice_content = """INVOICE #PYTEST-001
From: Test Legal Services Inc
To: LAIT Test Company
Date: August 11, 2025
Amount: $2,500.00
Description: Pytest test invoice
Total: $2,500.00
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(invoice_content)
        temp_file_path = temp_file.name
    
    try:
        # Upload the invoice
        with open(temp_file_path, 'rb') as file:
            files = {'file': ('pytest_invoice.txt', file, 'text/plain')}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                "http://localhost:5003/api/invoices/upload",
                files=files,
                headers=headers
            )
        
        assert response.status_code in [200, 201], f"Upload failed: {response.text}"
        
        upload_data = response.json()
        assert "invoice_id" in upload_data or "id" in upload_data
        
        print("✅ Invoice upload successful")
        
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    # Step 3: List invoices and assert count >= 1
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        "http://localhost:5003/api/invoices",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    invoices = data.get("invoices", [])
    invoices_count = len(invoices)
    
    # MAIN ASSERTION: invoices_count >= 1
    assert invoices_count >= 1, f"Expected invoices_count >= 1, got {invoices_count}"
    
    print(f"✅ ASSERTION PASSED: invoices_count >= 1 (got {invoices_count})")
    print("✅ All E2E tests passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
