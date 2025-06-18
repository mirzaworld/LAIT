from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

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
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    matter = relationship("Matter", back_populates="invoices")
    line_items = relationship("LineItem", back_populates="invoice")
    risk_factors = relationship("RiskFactor", back_populates="invoice")
    uploader = relationship("User")

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
    
    # Relationships
    invoices = relationship("Invoice", back_populates="matter")

class Vendor(Base):
    __tablename__ = 'vendors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    vendor_type = Column(String(50))
    risk_profile = Column(Float)
    historical_performance = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="vendor")

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
    is_flagged = Column(Boolean, default=False)  # Anomaly flag
    flag_reason = Column(String(255))            # Reason for flag
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
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
    
    # Relationships
    invoice = relationship("Invoice", back_populates="risk_factors")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String(1000))  # JSON or text for extra info
    user = relationship("User")
