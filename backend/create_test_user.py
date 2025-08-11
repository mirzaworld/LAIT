#!/usr/bin/env python3
"""
Create a test user with the correct password hash
"""

import sys
import os
sys.path.append('/Users/mirza/Documents/GitHub/LAIT/backend')

from werkzeug.security import generate_password_hash
from db.database import get_db_session, User

def create_test_user():
    """Create a test user with correct password hash"""
    session = get_db_session()
    
    try:
        # Check if user exists
        existing_user = session.query(User).filter(User.email == 'test@example.com').first()
        
        if existing_user:
            # Update the password hash
            existing_user.password_hash = generate_password_hash('testpass123')
            print("Updated existing user password")
        else:
            # Create new user
            new_user = User(
                email='test@example.com',
                password_hash=generate_password_hash('testpass123'),
                first_name='Test',
                last_name='User',
                role='user',
                company='Test Corp'
            )
            session.add(new_user)
            print("Created new test user")
        
        session.commit()
        print("✅ Test user ready with password: testpass123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    create_test_user()
