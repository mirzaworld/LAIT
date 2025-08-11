"""
LAIT End-to-End Tests - Pytest Version

Test the complete user workflow using pytest framework.
Includes proper test isolation, fixtures, and detailed assertions.
"""

import pytest
import requests
import time
from typing import Dict, Any
from io import BytesIO

# Test Configuration
API_BASE_URL = "http://localhost:5003/api"
REQUEST_TIMEOUT = 30

class TestClient:
    """Test client wrapper for LAIT API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', REQUEST_TIMEOUT)
        
        response = self.session.request(method, url, **kwargs)
        print(f"📡 {method} {endpoint} -> {response.status_code}")
        return response

@pytest.fixture(scope="session")
def api_client():
    """Create API client for tests"""
    client = TestClient()
    
    # Verify API is accessible
    try:
        response = client.make_request('GET', '/health')
        assert response.status_code == 200, "API should be accessible"
    except Exception as e:
        pytest.fail(f"Cannot connect to API at {API_BASE_URL}: {e}")
    
    return client

@pytest.fixture(scope="session") 
def sample_invoice():
    """Create sample invoice content"""
    content = """
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
    return content.strip().encode('utf-8')

@pytest.fixture(scope="function")
def test_user_data():
    """Generate unique test user data for each test"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    return {
        "email": f"test-{unique_id}@lait.example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": f"User-{unique_id}",
        "company": "LAIT Test Company"
    }

@pytest.mark.e2e
class TestEndToEndWorkflow:
    """Complete end-to-end workflow tests"""
    
    def test_health_check(self, api_client):
        """Test API health check endpoint"""
        response = api_client.make_request('GET', '/health')
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'message' in data
    
    def test_user_registration(self, api_client, test_user_data):
        """Test user registration"""
        response = api_client.make_request('POST', '/auth/register', json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert 'token' in data
        assert 'user' in data
        assert 'message' in data
        
        # Verify user data
        user = data['user']
        assert user['email'] == test_user_data['email']
        assert user['first_name'] == test_user_data['first_name']
        assert user['last_name'] == test_user_data['last_name']
        
        # Set token for subsequent requests
        api_client.token = data['token']
        api_client.session.headers.update({'Authorization': f'Bearer {data["token"]}'})
        
        return data
    
    def test_user_login(self, api_client, test_user_data):
        """Test user login after registration"""
        # First register the user
        self.test_user_registration(api_client, test_user_data)
        
        # Clear auth token
        api_client.token = None
        if 'Authorization' in api_client.session.headers:
            del api_client.session.headers['Authorization']
        
        # Now test login
        login_data = {
            "email": test_user_data['email'],
            "password": test_user_data['password']
        }
        
        response = api_client.make_request('POST', '/auth/login', json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'token' in data
        assert 'user' in data
        assert 'message' in data
        
        # Verify user data
        user = data['user']
        assert user['email'] == test_user_data['email']
        
        # Set token for subsequent requests
        api_client.token = data['token']
        api_client.session.headers.update({'Authorization': f'Bearer {data["token"]}'})
        
        return data
    
    @pytest.mark.upload
    def test_invoice_upload(self, api_client, test_user_data, sample_invoice):
        """Test invoice upload functionality"""
        # Setup authenticated user
        self.test_user_registration(api_client, test_user_data)
        
        # Prepare file upload
        files = {
            'file': ('test_invoice.txt', BytesIO(sample_invoice), 'text/plain')
        }
        
        headers = {}
        if api_client.token:
            headers['Authorization'] = f'Bearer {api_client.token}'
        
        response = api_client.make_request('POST', '/invoices/upload', files=files, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'message' in data
        assert 'invoice' in data  
        assert 'analysis' in data
        
        # Verify invoice data
        invoice = data['invoice']
        assert 'id' in invoice
        assert 'vendor' in invoice
        assert 'amount' in invoice
        assert 'status' in invoice
        assert 'filename' in invoice
        
        # Verify analysis data
        analysis = data['analysis']
        assert 'risk_score' in analysis
        assert 'risk_level' in analysis
        assert 'category' in analysis
        assert 'recommendations' in analysis
        assert isinstance(analysis['recommendations'], list)
        
        return data
    
    def test_invoices_list(self, api_client, test_user_data, sample_invoice):
        """Test retrieving user's invoices"""
        # Setup user and upload invoice
        upload_result = self.test_invoice_upload(api_client, test_user_data, sample_invoice)
        uploaded_invoice_id = upload_result['invoice']['id']
        
        # Get invoices list
        response = api_client.make_request('GET', '/invoices')
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'invoices' in data
        invoices = data['invoices']
        assert isinstance(invoices, list)
        assert len(invoices) >= 1
        
        # Find our uploaded invoice
        uploaded_invoice = None
        for invoice in invoices:
            if invoice['id'] == uploaded_invoice_id:
                uploaded_invoice = invoice
                break
        
        assert uploaded_invoice is not None, f"Should find uploaded invoice {uploaded_invoice_id}"
        
        # Verify invoice data structure
        assert 'id' in uploaded_invoice
        assert 'vendor' in uploaded_invoice
        assert 'amount' in uploaded_invoice
        assert 'date' in uploaded_invoice
        assert 'status' in uploaded_invoice
        
        return data
    
    @pytest.mark.analytics
    def test_analytics_summary(self, api_client, test_user_data, sample_invoice):
        """Test analytics summary endpoint"""
        # Setup user and upload invoice
        self.test_invoice_upload(api_client, test_user_data, sample_invoice)
        
        # Get analytics summary
        response = api_client.make_request('GET', '/analytics/summary')
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        required_fields = [
            'total_invoices', 'total_amount', 'total_vendors',
            'monthly_spending', 'top_vendors', 'recent_invoices',
            'spending_by_month'
        ]
        
        for field in required_fields:
            assert field in data, f"Analytics should have {field}"
        
        # Verify data types and values
        assert isinstance(data['total_invoices'], int)
        assert isinstance(data['total_amount'], (int, float))
        assert isinstance(data['total_vendors'], int)
        assert isinstance(data['monthly_spending'], (int, float))
        assert isinstance(data['top_vendors'], list)
        assert isinstance(data['recent_invoices'], list)
        assert isinstance(data['spending_by_month'], list)
        
        # Verify we have data (after upload)
        assert data['total_invoices'] >= 1
        assert data['total_amount'] > 0
        assert len(data['recent_invoices']) >= 1
        
        return data
    
    @pytest.mark.integration
    def test_complete_workflow(self, api_client, test_user_data, sample_invoice):
        """Test complete user workflow integration"""
        # 1. Register user
        register_result = self.test_user_registration(api_client, test_user_data)
        user_email = register_result['user']['email']
        
        # 2. Upload invoice
        upload_result = self.test_invoice_upload(api_client, test_user_data, sample_invoice)
        invoice_id = upload_result['invoice']['id']
        invoice_amount = upload_result['invoice']['amount']
        
        # 3. Get invoices list
        invoices_result = self.test_invoices_list(api_client, test_user_data, sample_invoice)
        invoices_count = len(invoices_result['invoices'])
        
        # 4. Get analytics
        analytics_result = self.test_analytics_summary(api_client, test_user_data, sample_invoice)
        
        # 5. Verify data consistency
        assert analytics_result['total_invoices'] == invoices_count
        assert analytics_result['total_invoices'] >= 1
        assert analytics_result['total_amount'] >= invoice_amount
        
        # Verify our invoice appears in recent invoices
        recent_invoice_ids = [inv['id'] for inv in analytics_result['recent_invoices']]
        assert invoice_id in recent_invoice_ids
        
        print(f"✅ Complete workflow test passed:")
        print(f"   User: {user_email}")
        print(f"   Invoice: {invoice_id}")
        print(f"   Amount: ${invoice_amount}")
        print(f"   Total Invoices: {analytics_result['total_invoices']}")
        print(f"   Total Amount: ${analytics_result['total_amount']}")

@pytest.mark.auth
class TestAuthentication:
    """Authentication specific tests"""
    
    def test_registration_validation(self, api_client):
        """Test registration input validation"""
        # Test missing required fields
        response = api_client.make_request('POST', '/auth/register', json={})
        assert response.status_code in [400, 422]  # Bad request or validation error
        
        # Test invalid email format
        invalid_data = {
            "email": "invalid-email",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        response = api_client.make_request('POST', '/auth/register', json=invalid_data)
        assert response.status_code in [400, 422]
    
    def test_login_validation(self, api_client):
        """Test login input validation"""
        # Test with invalid credentials
        invalid_login = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = api_client.make_request('POST', '/auth/login', json=invalid_login)
        assert response.status_code in [401, 404]  # Unauthorized or not found
    
    def test_protected_endpoint_without_auth(self, api_client):
        """Test accessing protected endpoint without authentication"""
        response = api_client.make_request('GET', '/invoices')
        assert response.status_code == 401  # Unauthorized

if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "--tb=short"])
