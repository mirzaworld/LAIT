from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Unify model definitions: import single source of truth
from models.db_models import Base, User, Notification, Vendor, Matter, Invoice, LineItem, RiskFactor  # noqa: F401

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./legal_ai.db')
engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

def init_db():
    """Initialize the database, creating all tables using unified models"""
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Get a new database session"""
    return SessionLocal()

__all__ = [
    'Base', 'User', 'Notification', 'Vendor', 'Matter', 'Invoice', 'LineItem', 'RiskFactor',
    'init_db', 'get_db_session', 'SessionLocal', 'engine'
]
