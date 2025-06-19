from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
import os
from datetime import datetime
import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    password_hash = Column(String(256), nullable=False)
    role = Column(String(50), default='user')  # 'user', 'admin', 'manager'
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notifications = relationship("Notification", back_populates="user")

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String(50))
    content = Column(JSON)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class Vendor(Base):
    __tablename__ = 'vendors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    hourly_rate_avg = Column(Float)
    diversity_score = Column(Float)
    performance_score = Column(Float)
    risk_profile = Column(Float)
    historical_performance = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    invoices = relationship('Invoice', back_populates='vendor')
    
class Matter(Base):
    __tablename__ = 'matters'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    status = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    invoices = relationship('Invoice', back_populates='matter')

class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    matter_id = Column(Integer, ForeignKey('matters.id'))
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20))
    description = Column(String(1000))
    hours = Column(Float)
    rate = Column(Float)
    risk_score = Column(Float)
    analysis_result = Column(JSON)
    pdf_s3_key = Column(String(255))  # S3 key for the uploaded PDF
    overspend_risk = Column(Float)    # Probability or boolean for overspend risk
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vendor = relationship("Vendor", back_populates="invoices")
    matter = relationship("Matter", back_populates="invoices")
    line_items = relationship("LineItem", back_populates="invoice")
    risk_factors = relationship("RiskFactor", back_populates="invoice")
    uploader = relationship("User")

class LineItem(Base):
    __tablename__ = 'line_items'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    description = Column(String(500))
    hours = Column(Float)
    rate = Column(Float)
    amount = Column(Float)
    timekeeper = Column(String(100))
    timekeeper_title = Column(String(100))
    date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice = relationship("Invoice", back_populates="line_items")

class RiskFactor(Base):
    __tablename__ = 'risk_factors'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    factor_type = Column(String(50))
    description = Column(String(500))
    severity = Column(String(20))
    impact_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice = relationship("Invoice", back_populates="risk_factors")

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./legal_ai.db')
engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

def init_db():
    """Initialize the database, creating all tables"""
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Get a new database session"""
    session = SessionLocal()
    return session
