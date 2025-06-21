from sqlalchemy import create_engine
import os
from database import Base, engine, init_db

def create_all_tables():
    """Create all database tables"""
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_all_tables()
