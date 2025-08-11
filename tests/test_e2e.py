#!/usr/bin/env python3
"""
LAIT End-to-End Tests

Tests the complete user workflow:
1. User registration
2. User login
3. Invoice upload
4. Invoice listing
5. Analytics metrics

Prerequisites:
- Backend server running on localhost:5003
- Clean database state for each test run
"""

import os
import sys
import json
import time
import tempfile
import requests
from typing import Dict, Any, Optional
from io import BytesIO

# Test Configuration
API_BASE_URL = "http://localhost:5003/api"
TEST_USER_EMAIL = "test@lait.example.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_FIRST_NAME = "Test"
TEST_USER_LAST_NAME = "User"
TEST_USER_COMPANY = "LAIT Test Company"

# Request timeout in seconds
REQUEST_TIMEOUT = 30

class LAITTestClient:
    """Test client for LAIT API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.user_data: Optional[Dict[str, Any]] = None
    
    def set_auth_token(self, token: str) -> None:
        """Set JWT authentication token"""
        self.token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def clear_auth(self) -> None:
        """Clear authentication"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Set default timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = REQUEST_TIMEOUT
        
        try:
            response = self.session.request(method, url, **kwargs)
            print(f"📡 {method} {endpoint} -> {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {method} {endpoint} - {e}")
            raise
    
    def register_user(self, email: str, password: str, first_name: str, 
                     last_name: str, company: str = "") -> Dict[str, Any]:
        """Register a new user"""
        data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "company": company
        }
        
        response = self.make_request('POST', '/auth/register', json=data)
        
        if response.status_code == 201:
            result = response.json()
            self.set_auth_token(result['token'])
            self.user_data = result.get('user')
            return result
        else:
            raise Exception(f"Registration failed: {response.status_code} - {response.text}")
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        data = {
            "email": email,
            "password": password
        }
        
        response = self.make_request('POST', '/auth/login', json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.set_auth_token(result['token'])
            self.user_data = result.get('user')
            return result
        else:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
    
    def upload_invoice(self, file_content: bytes, filename: str, 
                      content_type: str = 'application/pdf') -> Dict[str, Any]:
        """Upload an invoice file"""
        files = {
            'file': (filename, BytesIO(file_content), content_type)
        }
        
        # Remove content-type header for file upload
        headers = {}
        if 'Authorization' in self.session.headers:
            headers['Authorization'] = self.session.headers['Authorization']
        
        response = self.make_request('POST', '/invoices/upload', files=files, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    
    def get_invoices(self) -> Dict[str, Any]:
        """Get user's invoices"""
        response = self.make_request('GET', '/invoices')
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Get invoices failed: {response.status_code} - {response.text}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        response = self.make_request('GET', '/analytics/summary')
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Get analytics failed: {response.status_code} - {response.text}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.make_request('GET', '/health')
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Health check failed: {response.status_code} - {response.text}")

def create_sample_invoice_content() -> bytes:
    """Create sample invoice content for testing"""
    invoice_text = """
    INVOICE
    
    From: Legal Services LLC
    123 Law Street
    Legal City, LC 12345
    
    To: Test Company
    456 Business Ave
    Business City, BC 67890
    
    Invoice Number: INV-2025-001
    Date: August 11, 2025
    
    Description of Services:
    - Legal consultation regarding contract review
    - Document preparation and analysis
    - Client meeting and correspondence
    
    Hours: 15.5
    Rate: $350/hour
    
    Subtotal: $5,425.00
    Tax: $542.50
    Total Amount: $5,967.50
    
    Payment Terms: Net 30 days
    
    Thank you for your business!
    """
    return invoice_text.encode('utf-8')

def run_e2e_tests():
    """Run complete end-to-end test suite"""
    print("🧪 Starting LAIT End-to-End Tests")
    print("=" * 50)
    
    client = LAITTestClient()
    
    try:
        # Test 1: Health Check
        print("\n1. 🔍 Testing API Health Check...")
        health = client.health_check()
        assert health['status'] == 'healthy', f"Expected healthy status, got {health['status']}"
        print("✅ Health check passed")
        
        # Test 2: User Registration
        print("\n2. 👤 Testing User Registration...")
        register_result = client.register_user(
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME,
            company=TEST_USER_COMPANY
        )
        
        assert 'token' in register_result, "Registration should return token"
        assert 'user' in register_result, "Registration should return user data"
        assert client.token is not None, "Client should have auth token set"
        print(f"✅ User registered successfully: {register_result['user']['email']}")
        
        # Test 3: User Login (clear token first to test login)
        print("\n3. 🔐 Testing User Login...")
        client.clear_auth()
        login_result = client.login_user(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        
        assert 'token' in login_result, "Login should return token"
        assert 'user' in login_result, "Login should return user data"
        assert client.token is not None, "Client should have auth token set"
        print(f"✅ User logged in successfully: {login_result['user']['email']}")
        
        # Test 4: Invoice Upload
        print("\n4. 📄 Testing Invoice Upload...")
        sample_invoice = create_sample_invoice_content()
        upload_result = client.upload_invoice(
            file_content=sample_invoice,
            filename="test_invoice.txt",
            content_type="text/plain"
        )
        
        assert 'message' in upload_result, "Upload should return message"
        assert 'invoice' in upload_result, "Upload should return invoice data"
        assert 'analysis' in upload_result, "Upload should return analysis data"
        
        invoice_data = upload_result['invoice']
        analysis_data = upload_result['analysis']
        
        assert 'id' in invoice_data, "Invoice should have ID"
        assert 'vendor' in invoice_data, "Invoice should have vendor"
        assert 'amount' in invoice_data, "Invoice should have amount"
        
        assert 'risk_score' in analysis_data, "Analysis should have risk score"
        assert 'category' in analysis_data, "Analysis should have category"
        assert 'recommendations' in analysis_data, "Analysis should have recommendations"
        
        uploaded_invoice_id = invoice_data['id']
        print(f"✅ Invoice uploaded successfully: {uploaded_invoice_id}")
        print(f"   Vendor: {invoice_data['vendor']}")
        print(f"   Amount: ${invoice_data['amount']}")
        print(f"   Risk Score: {analysis_data['risk_score']}")
        
        # Test 5: Invoice List
        print("\n5. 📋 Testing Invoice List...")
        invoices_result = client.get_invoices()
        
        assert 'invoices' in invoices_result, "Should return invoices list"
        invoices_list = invoices_result['invoices']
        assert len(invoices_list) >= 1, "Should have at least 1 invoice"
        
        # Find our uploaded invoice
        uploaded_invoice = None
        for invoice in invoices_list:
            if invoice['id'] == uploaded_invoice_id:
                uploaded_invoice = invoice
                break
        
        assert uploaded_invoice is not None, f"Should find uploaded invoice {uploaded_invoice_id}"
        print(f"✅ Invoice list retrieved: {len(invoices_list)} invoice(s)")
        print(f"   Found uploaded invoice: {uploaded_invoice['id']}")
        
        # Test 6: Analytics Summary
        print("\n6. 📊 Testing Analytics Summary...")
        analytics_result = client.get_analytics_summary()
        
        required_fields = [
            'total_invoices', 'total_amount', 'total_vendors', 
            'monthly_spending', 'top_vendors', 'recent_invoices', 
            'spending_by_month'
        ]
        
        for field in required_fields:
            assert field in analytics_result, f"Analytics should have {field}"
        
        assert analytics_result['total_invoices'] >= 1, "Should have at least 1 invoice"
        assert analytics_result['total_amount'] > 0, "Should have positive total amount"
        assert len(analytics_result['recent_invoices']) >= 1, "Should have recent invoices"
        
        print(f"✅ Analytics retrieved successfully:")
        print(f"   Total Invoices: {analytics_result['total_invoices']}")
        print(f"   Total Amount: ${analytics_result['total_amount']:,}")
        print(f"   Total Vendors: {analytics_result['total_vendors']}")
        print(f"   Monthly Spending: ${analytics_result['monthly_spending']:,}")
        
        # Test 7: Data Consistency Check
        print("\n7. 🔍 Testing Data Consistency...")
        
        # Check that invoice counts match between invoices list and analytics
        assert len(invoices_list) == analytics_result['total_invoices'], \
            f"Invoice count mismatch: list={len(invoices_list)}, analytics={analytics_result['total_invoices']}"
        
        # Check that our invoice appears in recent invoices
        recent_invoice_ids = [inv['id'] for inv in analytics_result['recent_invoices']]
        assert uploaded_invoice_id in recent_invoice_ids, \
            f"Uploaded invoice {uploaded_invoice_id} should appear in recent invoices"
        
        print("✅ Data consistency verified")
        
        # Success Summary
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        print(f"✅ Health Check: API is healthy")
        print(f"✅ User Registration: {TEST_USER_EMAIL}")
        print(f"✅ User Login: Authentication working")
        print(f"✅ Invoice Upload: {uploaded_invoice_id}")
        print(f"✅ Invoice List: {len(invoices_list)} invoice(s)")
        print(f"✅ Analytics: ${analytics_result['total_amount']:,} total spend")
        print(f"✅ Data Consistency: All data matches")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("=" * 50)
        return False
    
    except KeyboardInterrupt:
        print(f"\n⏹️ Tests interrupted by user")
        print("=" * 50)
        return False

def main():
    """Main test runner"""
    print("LAIT End-to-End Test Suite")
    print(f"Target API: {API_BASE_URL}")
    print(f"Test User: {TEST_USER_EMAIL}")
    
    # Check if API is accessible
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API not accessible: {response.status_code}")
            print("💡 Make sure the backend server is running on localhost:5003")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot reach API: {e}")
        print("💡 Make sure the backend server is running on localhost:5003")
        sys.exit(1)
    
    # Run the tests
    success = run_e2e_tests()
    
    if success:
        print("\n🎯 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test suite failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
