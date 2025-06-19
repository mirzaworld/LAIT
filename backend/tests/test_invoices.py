"""Test invoice-related endpoints."""
import pytest
from datetime import datetime
import json
from io import BytesIO

def test_upload_invoice_success(client, admin_token, mock_s3):
    """Test successful invoice upload."""
    data = {
        'file': (BytesIO(b'test pdf content'), 'test.pdf'),
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
    assert 'id' in response.json
    assert 'pdf_s3_key' in response.json

def test_upload_invalid_file_type(client, admin_token):
    """Test upload with invalid file type."""
    data = {
        'file': (BytesIO(b'not a pdf'), 'test.txt'),
        'client_name': 'Test Client',
        'matter': 'Test Matter'
    }
    response = client.post(
        '/api/invoices',
        data=data,
        headers={'Authorization': admin_token},
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'PDF' in response.json['error']

def test_get_invoice_list(client, admin_token, sample_invoice):
    """Test getting list of invoices."""
    response = client.get(
        '/api/invoices',
        headers={'Authorization': admin_token}
    )
    assert response.status_code == 200
    assert len(response.json['items']) > 0
    assert response.json['items'][0]['id'] == sample_invoice.id

def test_get_invoice_detail(client, admin_token, sample_invoice):
    """Test getting invoice details."""
    response = client.get(
        f'/api/invoices/{sample_invoice.id}',
        headers={'Authorization': admin_token}
    )
    assert response.status_code == 200
    assert response.json['id'] == sample_invoice.id
    assert response.json['client_name'] == sample_invoice.client_name

def test_unauthorized_access(client, regular_token, sample_invoice):
    """Test unauthorized access to admin-only endpoints."""
    response = client.get(
        '/api/admin/auditlogs',
        headers={'Authorization': regular_token}
    )
    assert response.status_code == 403
