import pytest
import json
from flask import Flask
from enhanced_app import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()

class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Test that the health endpoint returns 200."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

class TestLegalIntelligenceEndpoints:
    """Test legal intelligence API endpoints."""
    
    def test_legal_intelligence_test(self, client):
        """Test the legal intelligence test endpoint."""
        response = client.get('/api/legal-intelligence/test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'services' in data
        assert data['services']['courtlistener'] == 'available'
    
    def test_verify_attorney(self, client):
        """Test attorney verification endpoint."""
        data = {
            'attorney_name': 'John Smith',
            'law_firm': 'Test Law Firm',
            'bar_number': '12345',
            'state': 'CA'
        }
        response = client.post('/api/legal-intelligence/verify-attorney', 
                             json=data)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'verified' in data
        # Response has attorney_info instead of attorney_name
        if data.get('verified'):
            assert 'attorney_info' in data
    
    def test_search_cases(self, client):
        """Test case search endpoint."""
        data = {
            'query': 'contract dispute',
            'court': 'federal',
            'limit': 10
        }
        response = client.post('/api/legal-intelligence/search-cases', 
                             json=data)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'cases' in data

class TestAnalyticsEndpoints:
    """Test analytics API endpoints."""
    
    def test_dashboard_metrics(self, client):
        """Test dashboard metrics endpoint."""
        response = client.get('/api/analytics/dashboard/metrics')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'totalSpend' in data
        assert 'invoiceCount' in data
        assert 'vendorCount' in data
    
    def test_analytics_summary(self, client):
        """Test analytics summary endpoint."""
        response = client.get('/api/analytics/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_spend' in data
        assert 'invoice_count' in data
    
    def test_vendor_analytics(self, client):
        """Test vendor analytics endpoint."""
        response = client.get('/api/analytics/vendors')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'vendors' in data

class TestMLEndpoints:
    """Test ML model endpoints."""
    
    def test_ml_status(self, client):
        """Test ML model status endpoint."""
        response = client.get('/api/ml/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'models' in data
        assert 'enhanced_invoice_analyzer' in data['models']
        assert 'invoice_analyzer' in data['models']
        assert 'matter_analyzer' in data['models']
        assert 'risk_predictor' in data['models']
        assert 'vendor_analyzer' in data['models']

class TestVendorEndpoints:
    """Test vendor management endpoints."""
    
    def test_list_vendors(self, client):
        """Test vendor listing endpoint."""
        response = client.get('/api/vendors')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'vendors' in data
    
    def test_vendor_search(self, client):
        """Test vendor search endpoint."""
        response = client.get('/api/vendors/search?name=test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'vendors' in data
    
    def test_vendor_analytics_summary(self, client):
        """Test vendor analytics summary endpoint."""
        response = client.get('/api/vendors/analytics/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Response has portfolio_summary.total_vendors structure
        assert 'portfolio_summary' in data
        assert 'total_vendors' in data['portfolio_summary']

class TestInvoiceEndpoints:
    """Test invoice management endpoints."""
    
    def test_list_invoices(self, client):
        """Test invoice listing endpoint."""
        response = client.get('/api/invoices')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list) or 'invoices' in data

class TestAdminEndpoints:
    """Test admin endpoints."""
    
    def test_admin_settings(self, client):
        """Test admin settings endpoint (requires auth)."""
        response = client.get('/api/admin/settings')
        # Should return 401 without authentication
        assert response.status_code in [401, 403]

class TestErrorHandling:
    """Test error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_json(self, client):
        """Test invalid JSON handling."""
        response = client.post('/api/legal-intelligence/verify-attorney',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400

class TestPerformance:
    """Test API performance."""
    
    def test_health_response_time(self, client):
        """Test health endpoint response time."""
        import time
        start_time = time.time()
        response = client.get('/api/health')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    def test_ml_status_response_time(self, client):
        """Test ML status endpoint response time."""
        import time
        start_time = time.time()
        response = client.get('/api/ml/status')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds 