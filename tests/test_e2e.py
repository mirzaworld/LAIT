#!/usr/bin/env python3
"""
LAIT Platform End-to-End Tests
==============================

Comprehensive E2E tests for the LAIT platform that validate:
- Backend health and API connectivity
- User registration and authentication  
- Invoice upload and processing
- Dashboard metrics validation (invoices_count>=1 and total_spend>0)
- Complete workflow integrity

Prerequisites:
- Backend must be running on localhost:5003
- Or set LAIT_API_BASE environment variable

Usage:
    pytest -q
    pytest tests/test_e2e.py -v
    python -m pytest tests/test_e2e.py

Author: LAIT Development Team
Version: 1.1.0
"""

import pytest
import requests
import time
import tempfile
import os
from typing import Optional


# Test configuration
API_BASE = os.getenv("LAIT_API_BASE", "http://localhost:5003")
TIMEOUT = 10

# Global test state
test_token: Optional[str] = None
test_email: str = ""


def test_01_api_health():
    """Test: Backend health endpoint is accessible"""
    print(f"🏥 Testing API health at {API_BASE}")
    
    response = requests.get(f"{API_BASE}/api/health", timeout=TIMEOUT)
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    
    data = response.json()
    # Accept various health response formats
    assert data.get("ok") is True or data.get("status") == "healthy" or "status" in data
    
    print("✅ API health check passed")


def test_02_user_registration():
    """Test: User registration creates account and returns JWT token"""
    global test_token, test_email
    
    # Generate unique email to avoid conflicts
    test_email = f"pytest_{int(time.time())}@lait.test"
    test_password = "TestPytest123!"
    
    payload = {
        "email": test_email,
        "password": test_password,
        "firstName": "Pytest",
        "lastName": "Tester",
        "company": "LAIT Test Suite"
    }
    
    print(f"👤 Registering user: {test_email}")
    
    response = requests.post(
        f"{API_BASE}/api/auth/register",
        json=payload,
        timeout=TIMEOUT
    )
    
    # Accept 201 (new user) or 409 (user exists) - in CI, user might already exist
    assert response.status_code in [201, 409], f"Registration failed: {response.status_code} - {response.text}"
    
    if response.status_code == 201:
        data = response.json()
        test_token = data.get("token") or data.get("access_token")
        assert test_token is not None, f"No token in registration response: {data}"
        print(f"✅ User registered successfully: {test_email}")
    else:
        # User already exists, try to login
        print(f"ℹ️  User exists, attempting login...")
        login_payload = {"email": test_email, "password": test_password}
        login_response = requests.post(f"{API_BASE}/api/auth/login", json=login_payload, timeout=TIMEOUT)
        
        if login_response.status_code == 200:
            data = login_response.json()
            test_token = data.get("token") or data.get("access_token")
            print(f"✅ User login successful: {test_email}")
        else:
            # If login fails, generate new unique email
            test_email = f"pytest_{int(time.time())}{os.getpid()}@lait.test"
            payload["email"] = test_email
            response = requests.post(f"{API_BASE}/api/auth/register", json=payload, timeout=TIMEOUT)
            assert response.status_code == 201, f"Second registration attempt failed: {response.text}"
            data = response.json()
            test_token = data.get("token") or data.get("access_token")
    
    assert test_token is not None, "Failed to obtain JWT token"
    print(f"✅ JWT token obtained: {test_token[:30]}...")


def test_03_protected_endpoint_auth():
    """Test: Protected endpoints require authentication"""
    # Test without auth - should return 401
    response = requests.get(f"{API_BASE}/api/invoices", timeout=TIMEOUT)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    
    # Test with auth - should return 200
    headers = {'Authorization': f'Bearer {test_token}'}
    response = requests.get(f"{API_BASE}/api/invoices", headers=headers, timeout=TIMEOUT)
    assert response.status_code == 200, f"Authenticated request failed: {response.status_code}"
    
    print("✅ Authentication validation passed")


def test_04_invoice_upload():
    """Test: Upload small text invoice and validate processing"""
    global test_token
    assert test_token is not None, "JWT token required for upload test"
    
    # Create realistic test invoice content
    invoice_content = """Legal Services Invoice - E2E Test
Client: LAIT Test Corp
Matter: PYTEST-2024-001
Date: August 12, 2025

Billing Details:
Senior Partner consultation: Rate: 500/hr, Hours: 2.5, Total: 1250.00
Associate research: Rate: 300/hr, Hours: 4.0, Total: 1200.00  
Paralegal document review: Rate: 180/hr, Hours: 3.5, Total: 630.00
Court filing fees: Rate: 0/hr, Hours: 0, Total: 125.00

Total Amount: $3,205.00
"""
    
    print("📄 Uploading test invoice...")
    
    # Create temporary file for upload
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(invoice_content)
        temp_file_path = temp_file.name
    
    try:
        # Upload invoice using multipart form data
        with open(temp_file_path, 'rb') as file:
            files = {'file': ('pytest_invoice.txt', file, 'text/plain')}
            form_data = {
                'client_name': 'LAIT Test Corp',
                'matter_id': 'PYTEST-2024-001'
            }
            headers = {'Authorization': f'Bearer {test_token}'}
            
            response = requests.post(
                f"{API_BASE}/api/invoices/upload",
                files=files,
                data=form_data,
                headers=headers,
                timeout=TIMEOUT
            )
        
        assert response.status_code in [200, 201], f"Upload failed: {response.status_code} - {response.text}"
        
        upload_data = response.json()
        
        # Validate response contains expected fields
        assert "lines_processed" in upload_data, f"Missing 'lines_processed' in response: {upload_data}"
        
        lines_processed = upload_data["lines_processed"]
        assert lines_processed >= 1, f"Expected lines_processed >= 1, got {lines_processed}"
        
        # Check for invoice ID
        invoice_id = upload_data.get("invoice_id") or upload_data.get("id")
        assert invoice_id is not None, f"No invoice ID in response: {upload_data}"
        
        print(f"✅ Invoice uploaded successfully:")
        print(f"   📊 Lines processed: {lines_processed}")
        print(f"   🆔 Invoice ID: {invoice_id}")
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def test_05_invoice_list_non_empty():
    """Test: Invoice list returns non-empty results after upload"""
    assert test_token is not None, "JWT token required for invoice list test"
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = requests.get(f"{API_BASE}/api/invoices", headers=headers, timeout=TIMEOUT)
    
    assert response.status_code == 200, f"Invoice list failed: {response.status_code} - {response.text}"
    
    data = response.json()
    assert "invoices" in data, f"Missing 'invoices' field in response: {data}"
    
    invoices = data["invoices"]
    invoices_count = len(invoices)
    
    # MAIN ASSERTION: invoices_count >= 1
    assert invoices_count >= 1, f"Expected invoices_count >= 1, got {invoices_count}"
    
    print(f"✅ ASSERTION PASSED: invoices_count >= 1 (found {invoices_count} invoices)")


def test_06_dashboard_metrics_validation():
    """Test: Dashboard metrics show invoices_count>=1 and total_spend>0"""
    assert test_token is not None, "JWT token required for dashboard metrics test"
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = requests.get(f"{API_BASE}/api/dashboard/metrics", headers=headers, timeout=TIMEOUT)
    
    assert response.status_code == 200, f"Dashboard metrics failed: {response.status_code} - {response.text}"
    
    metrics_data = response.json()
    print(f"📊 Dashboard metrics response: {metrics_data}")
    
    # Validate invoices_count >= 1 (try multiple field names)
    invoices_count = metrics_data.get('invoices_count', metrics_data.get('total_invoices', 0))
    assert invoices_count >= 1, f"Expected invoices_count >= 1, got {invoices_count}"
    
    # Validate total_spend > 0 (try multiple field names)  
    total_spend = metrics_data.get('total_spend', metrics_data.get('total_amount', 0))
    assert float(total_spend) > 0, f"Expected total_spend > 0, got {total_spend}"
    
    print(f"✅ ASSERTION PASSED: invoices_count >= 1 (got {invoices_count})")
    print(f"✅ ASSERTION PASSED: total_spend > 0 (got ${total_spend:,.2f})")
    
    # Print additional metrics for debugging
    for key, value in metrics_data.items():
        if key not in ['invoices_count', 'total_invoices', 'total_spend', 'total_amount']:
            print(f"   📈 {key}: {value}")


def test_07_complete_e2e_workflow():
    """Test: Final validation of complete end-to-end workflow"""
    print("🎯 Running complete E2E workflow validation...")
    
    assert test_token is not None, "JWT token should be available from previous tests"
    assert test_email != "", "Test email should be set from registration"
    
    # Validate we can still access all endpoints
    headers = {'Authorization': f'Bearer {test_token}'}
    
    # Health check
    health_response = requests.get(f"{API_BASE}/api/health", timeout=TIMEOUT)
    assert health_response.status_code == 200
    
    # User info (if endpoint exists)
    try:
        me_response = requests.get(f"{API_BASE}/api/auth/me", headers=headers, timeout=TIMEOUT)
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"✅ User profile accessible: {user_info.get('email', 'N/A')}")
    except:
        pass  # Optional endpoint
    
    # Invoice list
    invoices_response = requests.get(f"{API_BASE}/api/invoices", headers=headers, timeout=TIMEOUT)
    assert invoices_response.status_code == 200
    
    # Dashboard metrics
    metrics_response = requests.get(f"{API_BASE}/api/dashboard/metrics", headers=headers, timeout=TIMEOUT)
    assert metrics_response.status_code == 200
    
    print("✅ Complete E2E workflow validation passed")
    print(f"🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print(f"   Test user: {test_email}")
    print(f"   API endpoint: {API_BASE}")


# Keep the legacy test for backward compatibility
def test_user_registration_upload_and_list():
    """
    Legacy test maintained for compatibility
    Main E2E test combining registration, upload, and list validation
    """
    # This test is now covered by the individual test methods above
    # but kept for any existing CI that might reference it specifically
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
