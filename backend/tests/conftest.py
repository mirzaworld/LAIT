"""Test configuration and fixtures."""
import pytest
from datetime import datetime, timedelta
import os
from flask import Flask
from flask.testing import FlaskClient
import jwt
from typing import Generator, Dict, Any
import tempfile
import sys

# --- NEW: Ignore legacy root-level test file causing import mismatch ---

def pytest_ignore_collect(path):
    # Prevent pytest from collecting the legacy /backend/test_api.py which conflicts
    return str(path).endswith('backend/test_api.py')

try:
    from enhanced_app import create_app
except ImportError:
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..')))
    from enhanced_app import create_app

from db.database import init_db, get_db_session
from models.db_models import User, Invoice, Vendor, Matter, LineItem
from services.s3_service import S3Service

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
        'WTF_CSRF_ENABLED': False
    })

    # Create the database and load test data
    with app.app_context():
        init_db()
        
    yield app

    # Clean up the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def session(app):
    """Create a database session for testing."""
    with app.app_context():
        session = get_db_session()
        yield session
        session.close()

@pytest.fixture
def admin_token(app: Flask) -> str:
    """Create a JWT token for an admin user."""
    token = jwt.encode(
        {
            'user_id': 1,
            'role': 'admin',
            'exp': datetime.utcnow() + timedelta(days=1)
        },
        app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    return f'Bearer {token}'

@pytest.fixture
def regular_token(app: Flask) -> str:
    """Create a JWT token for a regular user."""
    token = jwt.encode(
        {
            'user_id': 2,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(days=1)
        },
        app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    return f'Bearer {token}'

@pytest.fixture
def mock_s3(monkeypatch) -> None:
    """Mock S3 service for testing file uploads."""
    def mock_upload_file(*args, **kwargs) -> str:
        return f"test-key-{datetime.now().timestamp()}"

    def mock_generate_presigned_url(*args, **kwargs) -> str:
        return f"https://test-bucket.s3.amazonaws.com/{args[0]}"

    monkeypatch.setattr(S3Service, 'upload_file', mock_upload_file)
    monkeypatch.setattr(S3Service, 'generate_presigned_url', mock_generate_presigned_url)

@pytest.fixture
def sample_vendor(session) -> Vendor:
    """Create a sample vendor."""
    vendor = Vendor(
        name='Test Law Firm',
        average_rate=500.0,
        diversity_score=80,
        success_rate=0.85
    )
    session.add(vendor)
    session.commit()
    return vendor

@pytest.fixture
def sample_invoice(session, sample_vendor) -> Invoice:
    """Create a sample invoice."""
    invoice = Invoice(
        vendor_id=sample_vendor.id,
        client_name='Test Client',
        matter='Test Matter',
        invoice_number='INV-2025-001',
        date=datetime.now(),
        total_amount=10000.0,
        pdf_s3_key='test-invoice.pdf',
        uploaded_by=1
    )
    session.add(invoice)
    session.commit()
    return invoice
