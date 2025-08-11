"""Test invoice endpoints."""
import pytest
from datetime import datetime
import json
from io import BytesIO

def test_upload_invoice_success(client, admin_token):
    """Test successful invoice upload."""
    # Mock PDF content that won't fail parsing
    from unittest.mock import patch
    
    with patch('services.pdf_parser_service.PDFParserService.parse_pdf') as mock_parse:
        mock_parse.return_value = {
            'vendor_name': 'Test Vendor',
            'invoice_number': 'INV-001',
            'amount': 1000.0,
            'date': '2023-01-15'
        }
        
        data = {
            'file': (BytesIO(b'fake pdf content'), 'test.pdf'),
            'client_name': 'Test Client',
            'matter': 'Test Matter'
        }
        response = client.post(
            '/api/invoices',
            data=data,
            headers={'Authorization': admin_token},
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        # Response has invoice_id instead of id
        assert 'invoice_id' in response.json

def test_upload_invalid_file_type(client, admin_token):
    """Test upload with invalid file type."""
    data = {
        'file': (BytesIO(b'not a pdf'), 'test.txt'),
        'client_name': 'Test Client',
        'matter': 'Test Matter'
    }
    response = client.post(
        '/api/invoices/upload',
        data=data,
        headers={'Authorization': admin_token},
        content_type='multipart/form-data'
    )
    assert response.status_code == 400

def test_get_invoice_list(client, admin_token, sample_invoice):
    """Test getting list of invoices."""
    response = client.get(
        '/api/invoices',
        headers={'Authorization': admin_token}
    )
    assert response.status_code == 200
    assert 'items' in response.json
    if len(response.json['items']) > 0:
        # ID is returned as string, convert for comparison
        assert int(response.json['items'][0]['id']) == sample_invoice.id

def test_get_invoice_detail(client, admin_token, sample_invoice):
    """Test getting specific invoice details."""
    response = client.get(
        f'/api/invoices/{sample_invoice.id}',
        headers={'Authorization': admin_token}
    )
    assert response.status_code == 200
    assert response.json['id'] == sample_invoice.id

def test_unauthorized_access(client, regular_token, sample_invoice):
    """Test unauthorized access to admin-only endpoints."""
    response = client.get(
        '/api/admin/audit-logs',
        headers={'Authorization': regular_token}
    )
    assert response.status_code == 403
