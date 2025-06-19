"""Test configuration and fixtures."""
import pytest
from datetime import datetime, timedelta
import os
from flask import Flask
from flask.testing import FlaskClient
import jwt
from typing import Generator, Dict, Any

from app import create_app
from models import db, User, Invoice, Vendor
from services.s3_service import S3Service

@pytest.fixture
def app() -> Flask:
    """Create and configure a Flask application for testing."""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:postgres@localhost:5432/test_db',
        'JWT_SECRET_KEY': 'test-secret',
        'S3_BUCKET': 'test-bucket'
    })
    return app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def db_session(app: Flask) -> Generator:
    """Create database tables and provide a session."""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()

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
def sample_vendor(db_session) -> Vendor:
    """Create a sample vendor."""
    vendor = Vendor(
        name='Test Law Firm',
        average_rate=500.0,
        diversity_score=80,
        success_rate=0.85
    )
    db_session.add(vendor)
    db_session.commit()
    return vendor

@pytest.fixture
def sample_invoice(db_session, sample_vendor) -> Invoice:
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
    db_session.add(invoice)
    db_session.commit()
    return invoice
