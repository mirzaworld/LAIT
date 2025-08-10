#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tempfile
from enhanced_app import create_app
from db.database import init_db, get_db_session, rebind_engine
from models.db_models import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, verify_jwt_in_request, decode_token
import jwt as pyjwt

def debug_jwt_422():
    # Reproduce test setup
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    db_url = f'sqlite:///{db_path}'
    rebind_engine(db_url, drop=True)

    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE_URL': db_url,
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        init_db()
        session = get_db_session()
        if not session.query(User).filter_by(email='default@example.com').first():
            user = User(email='default@example.com', password_hash=generate_password_hash('Password123'), first_name='Default', last_name='User')
            session.add(user)
            session.commit()
        session.close()
        
        # Create token and examine it
        token = create_access_token(identity=1)
        print(f"Created token: {token}")
        
        # Decode token to see claims
        decoded = decode_token(token)
        print(f"Token claims: {decoded}")
        
        # Test JWT verification manually
        try:
            # Mock a request with the token
            with app.test_request_context('/', headers={'Authorization': f'Bearer {token}'}):
                print("Testing JWT verification...")
                verify_jwt_in_request()
                print("JWT verification passed")
        except Exception as e:
            print(f"JWT verification failed: {e}")
            print(f"Exception type: {type(e)}")
            
        # Test the actual endpoint
        with app.test_client() as client:
            response = client.get('/api/invoices', headers={'Authorization': f'Bearer {token}'})
            print(f"Endpoint response: {response.status_code}")
            if response.status_code != 200:
                print(f"Response data: {response.get_data(as_text=True)}")

    os.close(db_fd)
    os.unlink(db_path)

if __name__ == '__main__':
    debug_jwt_422()
