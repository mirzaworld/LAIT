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

# --- NEW: Testing support: allow rebinding engine to fresh SQLite path ---
def rebind_engine(db_url: str, drop: bool = False):  # pragma: no cover - used in tests
    """Rebind global engine/session to a new database URL (used by tests).
    If drop is True, drop existing tables first (safe for ephemeral test DBs).
    """
    global engine, SessionLocal, session_factory, DATABASE_URL
    try:
        if 'sqlite' not in db_url and drop:
            # Safety: don't drop non-sqlite (persistent) DBs automatically
            drop = False
        old_engine = engine
    except NameError:
        old_engine = None  # first initialization
    DATABASE_URL = db_url
    # Dispose old engine if present
    if old_engine is not None:
        try:
            old_engine.dispose()
        except Exception:
            pass
    engine = create_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    SessionLocal = scoped_session(session_factory)
    if drop:
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception:
            pass
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Get a new database session"""
    return SessionLocal()

__all__ = [
    'Base', 'User', 'Notification', 'Vendor', 'Matter', 'Invoice', 'LineItem', 'RiskFactor',
    'init_db', 'get_db_session', 'SessionLocal', 'engine', 'rebind_engine'
]
