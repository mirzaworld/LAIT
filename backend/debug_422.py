#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_app import create_app
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

def debug_422_error():
    app = create_app()
    
    with app.test_client() as test_client:
        print("=== Testing WITHOUT auth ===")
        response = test_client.get('/api/invoices')
        print(f"Status Code: {response.status_code}")
        print(f"Data: {response.get_data(as_text=True)}")
        print()

        # Now test with JWT like in the conftest
        print("=== Testing WITH JWT auth (like test fixture) ===")
        with app.app_context():
            try:
                token = create_access_token(identity=1)
                print(f"Generated token: {token[:50]}...")
                
                response = test_client.get('/api/invoices', 
                                         headers={'Authorization': f'Bearer {token}'})
                print(f"Status Code: {response.status_code}")
                print(f"Data: {response.get_data(as_text=True)}")
            except Exception as e:
                print(f"Error creating token: {e}")

if __name__ == '__main__':
    debug_422_error()
