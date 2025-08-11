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
from flask_jwt_extended import create_access_token  # type: ignore
import flask_jwt_extended.view_decorators as _jwt_views
from flask_jwt_extended import get_jwt_identity as _real_get_jwt_identity, create_access_token as _create_access_token

# Ensure env flags for dev/test bypass
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('ENVIRONMENT', 'dev')

# --- NEW: Ignore legacy root-level test file causing import mismatch ---

def pytest_ignore_collect(path):
    # Prevent pytest from collecting the legacy /backend/test_api.py which conflicts
    if str(path).endswith('backend/test_api.py'):
        return True
    # Also ignore duplicated outdated unittest style test in tests/test_api.py
    if str(path).endswith('backend/tests/test_api.py'):
        return True
    # Ignore test_server.py which is a Flask server, not a test file
    if str(path).endswith('backend/test_server.py'):
        return True
    return False

try:
    from enhanced_app import create_app
except ImportError:
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..')))
    from enhanced_app import create_app

from db.database import init_db, get_db_session, rebind_engine
from models.db_models import User, Invoice, Vendor, Matter, LineItem
from services.s3_service import S3Service

# --- UPDATED: Auto auth headers will be populated with a REAL JWT token in client fixture ---
AUTO_AUTH_HEADER = {'Authorization': 'Bearer mock-jwt-token-for-development'}  # will be overridden

@pytest.fixture
def app():
    """Create and configure a new app instance for each test with isolated DB."""
    # Create a temporary SQLite DB path
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    db_url = f'sqlite:///{db_path}'

    # Rebind engine to new temp DB and create schema
    rebind_engine(db_url, drop=True)

    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE_URL': db_url,
        'WTF_CSRF_ENABLED': False
    })

    # Create the database and load test data
    with app.app_context():
        init_db()
        session = get_db_session()
        # Insert a default user for auth dependent tests
        if not session.query(User).filter_by(email='default@example.com').first():
            from werkzeug.security import generate_password_hash
            user = User(email='default@example.com', password_hash=generate_password_hash('Password123'), first_name='Default', last_name='User')
            session.add(user)
            session.commit()
        session.close()

    yield app

    # Clean up
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass

@pytest.fixture
def client(app):
    """Create a test client with automatic auth header injection (real JWT)."""
    # Generate a real JWT token tied to default user (id=1) so @jwt_required passes
    # NOTE: JWT subject must be a string, not integer
    with app.app_context():
        token = create_access_token(identity="1")
    real_header = {'Authorization': f'Bearer {token}'}

    class AutoAuthClient(FlaskClient):
        def open(self, *args, **kwargs):  # type: ignore
            headers = kwargs.pop('headers', {}) or {}
            if 'Authorization' not in headers:
                headers.update(real_header)
            kwargs['headers'] = headers
            return super().open(*args, **kwargs)

    app.test_client_class = AutoAuthClient  # type: ignore
    return app.test_client()

@pytest.fixture
def no_auth_client(app):
    """Create a test client without automatic auth header injection."""
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
    with app.app_context():
        from flask_jwt_extended import create_access_token
        # Use create_access_token for consistency with Flask-JWT-Extended
        # Identity must be string, not int
        token = create_access_token(
            identity='1',
            additional_claims={'role': 'admin'}
        )
    return f'Bearer {token}'

@pytest.fixture
def regular_token(app: Flask) -> str:
    """Create a JWT token for a regular user."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        # Use create_access_token for consistency with Flask-JWT-Extended
        # Identity must be string, not int
        token = create_access_token(
            identity='2', 
            additional_claims={'role': 'user'}
        )
    return f'Bearer {token}'

@pytest.fixture
def auto_auth_headers(app):  # keep for backward compatibility
    """Headers using real JWT token for authenticated requests."""
    with app.app_context():
        token = create_access_token(identity="1")  # Fix: use string identity
    return {'Authorization': f'Bearer {token}'}

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

# Removed automatic JWT bypass fixture - using development_jwt_required decorator instead
