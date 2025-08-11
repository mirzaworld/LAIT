#!/usr/bin/env python3
"""
Database Setup for LAIT Real Backend
Creates PostgreSQL database and tables
"""

import os
import sys
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database

# Add backend to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_postgresql():
    """Setup PostgreSQL database"""
    
    # Database configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'lait_production')
    DB_USER = os.environ.get('DB_USER', 'lait_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'lait_secure_password_2024')
    
    # Admin connection (to create database and user)
    admin_url = f'postgresql://postgres:@{DB_HOST}:{DB_PORT}/postgres'
    
    # Target database URL
    database_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    try:
        print("🔧 Setting up PostgreSQL database...")
        
        # Connect as admin to create database and user
        admin_engine = create_engine(admin_url)
        
        with admin_engine.connect() as conn:
            # Use autocommit for database creation
            conn = conn.execution_options(autocommit=True)
            
            # Create user if doesn't exist
            try:
                conn.execute(text(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';"))
                print(f"✅ Created user: {DB_USER}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"ℹ️  User {DB_USER} already exists")
                else:
                    print(f"⚠️  User creation warning: {e}")
            
            # Create database if doesn't exist
            if not database_exists(database_url):
                create_database(database_url)
                print(f"✅ Created database: {DB_NAME}")
            else:
                print(f"ℹ️  Database {DB_NAME} already exists")
            
            # Grant privileges
            conn.execute(text(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};"))
            print(f"✅ Granted privileges to {DB_USER}")
        
        admin_engine.dispose()
        
        # Test connection to new database
        target_engine = create_engine(database_url)
        with target_engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
            print("✅ Database connection successful")
        
        target_engine.dispose()
        
        # Initialize Flask app and create tables
        from app_real import app, db
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
        
        print(f"""
🎉 PostgreSQL setup complete!

Database Details:
- Host: {DB_HOST}:{DB_PORT}
- Database: {DB_NAME}  
- User: {DB_USER}
- Connection URL: {database_url}

Environment Variables (add to your .env):
DATABASE_URL={database_url}
DB_HOST={DB_HOST}
DB_PORT={DB_PORT}
DB_NAME={DB_NAME}
DB_USER={DB_USER}
DB_PASSWORD={DB_PASSWORD}
""")
        
        return database_url
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        print("\n🔧 Manual setup instructions:")
        print("1. Install PostgreSQL: brew install postgresql")
        print("2. Start PostgreSQL: brew services start postgresql")
        print(f"3. Create database: createdb {DB_NAME}")
        print(f"4. Create user: psql -c \"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';\"")
        print(f"5. Grant privileges: psql -c \"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};\"")
        return None

def setup_sqlite_fallback():
    """Setup SQLite as fallback database"""
    print("🔄 Setting up SQLite fallback database...")
    
    # Update database URL to use SQLite
    sqlite_url = 'sqlite:///lait_real.db'
    
    try:
        from app_real import app, db
        
        # Temporarily override database URL
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_url
        
        with app.app_context():
            db.create_all()
            print("✅ SQLite database created successfully")
        
        print(f"""
✅ SQLite setup complete!

Database Details:
- Type: SQLite
- File: lait_real.db
- Connection URL: {sqlite_url}

To use SQLite, set this environment variable:
DATABASE_URL={sqlite_url}
""")
        
        return sqlite_url
        
    except Exception as e:
        print(f"❌ SQLite setup failed: {str(e)}")
        return None

def main():
    """Main setup function"""
    print("🚀 LAIT Database Setup")
    print("=" * 40)
    
    # Check if PostgreSQL is available
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL found")
            database_url = setup_postgresql()
        else:
            raise Exception("PostgreSQL not found")
    except Exception as e:
        print(f"⚠️  PostgreSQL not available: {e}")
        print("🔄 Falling back to SQLite...")
        database_url = setup_sqlite_fallback()
    
    if database_url:
        print("\n🎯 Next steps:")
        print("1. Install backend dependencies: pip install -r requirements_real.txt")
        print("2. Set environment variables")
        print("3. Start backend: python app_real.py")
        print("\n🚀 Backend will be available at: http://localhost:5003")
    else:
        print("\n❌ Database setup failed. Please set up database manually.")
        sys.exit(1)

if __name__ == '__main__':
    main()
