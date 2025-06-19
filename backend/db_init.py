from sqlalchemy import create_engine
import os
import psycopg2
from backend.db.database import Base

# Get database connection details from environment variables
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'legalspend')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'securepassword')

# Create database URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_tables():
    """Create all tables in the database."""
    engine = create_engine(DB_URL)
    print(f"Creating tables in {DB_URL}...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == '__main__':
    create_tables()
