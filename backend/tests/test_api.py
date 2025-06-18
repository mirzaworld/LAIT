import unittest
import json
import sys
import os

# Add parent directory to path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class APITestCase(unittest.TestCase):
    """Test case for the Flask API endpoints"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.app.get('/api/health')
        data = json.loads(response.get_data())
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
    
    def test_get_invoices(self):
        """Test getting invoices"""
        response = self.app.get('/api/invoices')
        data = json.loads(response.get_data())
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('invoices', data)
        self.assertIsInstance(data['invoices'], list)
    
    def test_get_invoice_details(self):
        """Test getting invoice details"""
        response = self.app.get('/api/invoices/INV-2024-001')
        data = json.loads(response.get_data())
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], 'INV-2024-001')
        self.assertIn('line_items', data)
    
    def test_analyze_invoice(self):
        """Test invoice analysis"""
        response = self.app.post('/api/invoices/INV-2024-001/analyze')
        data = json.loads(response.get_data())
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('risk_score', data)
        self.assertIn('recommendations', data)
    
    def test_dashboard_metrics(self):
        """Test dashboard metrics"""
        response = self.app.get('/api/dashboard/metrics')
        data = json.loads(response.get_data())
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_spend', data)
        self.assertIn('active_matters', data)
        self.assertIn('vendor_count', data)

if __name__ == '__main__':
    unittest.main()
