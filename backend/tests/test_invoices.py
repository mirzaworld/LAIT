import io
import os
import tempfile

import pytest

from db.database import rebind_engine, get_db_session
from models.db_models import Vendor, User, Invoice, LineItem


def setup_module(module):
    # Rebind to an in-memory SQLite DB for fast, isolated tests
    rebind_engine('sqlite:///:memory:', drop=True)


def create_app_client():
    # Import here so rebind_engine runs first
    from enhanced_app import create_app
    app = create_app()
    app.config['TESTING'] = True
    # Ensure development auth bypass is enabled for tests
    app.config['AUTO_AUTH_BYPASS'] = True
    return app.test_client(), app


def seed_sample_data():
    session = get_db_session()
    try:
        # Create a vendor and a user and a sample invoice
        vendor = Vendor(name='ACME Legal')
        session.add(vendor)
        session.flush()

        user = User(email='test@example.com', password_hash='x')
        session.add(user)
        session.flush()

        inv = Invoice(
            invoice_number='INV-100',
            vendor_id=vendor.id,
            amount=1500.0,
            total_amount=1500.0,
            status='processed',
            uploaded_by=user.id,
        )
        session.add(inv)
        session.flush()

        li = LineItem(invoice_id=inv.id, description='Legal work', hours=3.0, rate=500.0, amount=1500.0)
        session.add(li)
        session.commit()
        return inv.id
    finally:
        session.close()


def test_list_invoices_returns_seeded_invoice():
    client, app = create_app_client()
    inv_id = seed_sample_data()

    resp = client.get('/api/invoices')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'invoices' in data
    assert any(str(inv.get('id')) == str(inv_id) or inv.get('invoice_number') == 'INV-100' for inv in data['invoices'])


def test_get_invoice_detail():
    client, app = create_app_client()
    inv_id = seed_sample_data()

    resp = client.get(f'/api/invoices/{inv_id}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['id'] == inv_id or int(data.get('id')) == int(inv_id)
    assert 'vendor_name' in data


def test_upload_invoice_file_fallback_parsing():
    client, app = create_app_client()

    # Create a simple text file to upload; parser may fallback to raw text
    file_content = b"Test line,1,100,100\n"
    data = {
        'vendor': 'Upload Vendor',
        'amount': '200.0',
        'date': '2025-11-11'
    }
    resp = client.post('/api/invoices/upload', data={**data, 'file': (io.BytesIO(file_content), 'test.txt')}, content_type='multipart/form-data')
    assert resp.status_code == 200 or resp.status_code == 201
    json_data = resp.get_json()
    # Response should include invoice_id and analysis keys per contract
    assert 'invoice_id' in json_data or ('invoice' in json_data and 'id' in json_data['invoice'])
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
