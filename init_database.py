#!/usr/bin/env python3
"""
Script to initialize the database and create all tables.
This is helpful when starting a fresh installation or when tables are missing.
"""

from sqlalchemy import create_engine
from backend.db.database import Base, init_db

def main():
    """Initialize database and create all tables"""
    print("Running database initialization...")
    init_db()
    print("Database initialization completed successfully!")

if __name__ == "__main__":
    main()
