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
    description = Column(String(2000))  # Case description for complexity analysis
    court = Column(String(200))  # Court where case is filed
    judge_name = Column(String(200))  # Assigned judge
    opposing_counsel = Column(String(500))  # Opposing attorney/firm
    case_type = Column(String(100))  # Type of legal matter
    priority = Column(String(20))  # High, Medium, Low
    
    # Dates
    start_date = Column(Date)
    end_date = Column(Date)
    expected_duration_months = Column(Integer)  # Expected duration
    
    # Financial
    budget = Column(Float)
    estimated_cost = Column(Float)  # AI-estimated cost based on complexity
    risk_multiplier = Column(Float, default=1.0)  # Complexity-based risk multiplier
    
    # Legal Intelligence Fields
    complexity_score = Column(Integer)  # 1-10 complexity rating from CourtListener
    success_probability = Column(Float)  # Estimated success probability
    
    # Metadata
    additional_info = Column(JSON)  # Store CourtListener analysis results
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="matter")

class Vendor(Base):
    __tablename__ = 'vendors'
    
    id = Column(Integer, primary_key=True)
    external_id = Column(String(100), unique=True)  # From company dataset
    name = Column(String(200), nullable=False)
    vendor_type = Column(String(50))
    
    # Company Information
    industry_category = Column(String(100))
    practice_area = Column(String(100))  # Primary legal practice area
    firm_size_category = Column(String(50))  # Large, Medium, Small, etc.
    employee_count = Column(String(20))  # Employee range (1-10, 11-50, etc.)
    founded_year = Column(Integer)
    
    # Location Information
    country = Column(String(100))
    state_province = Column(String(100))
    city = Column(String(100))
    address = Column(String(500))  # Full address if available
    
    # Contact Information
    website = Column(String(255))
    linkedin_url = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    
    # LAIT-specific fields
    status = Column(String(20), default='Prospect')  # Prospect, Active, Inactive
    risk_profile = Column(Float)
    performance_score = Column(Float)  # Overall performance rating
    diversity_score = Column(Float)    # Diversity metrics
    
    # Analytics fields
    total_spend = Column(Float, default=0.0)
    invoice_count = Column(Integer, default=0)
    avg_rate = Column(Float)
    on_time_rate = Column(Float)  # Percentage of on-time deliveries
    success_rate = Column(Float)  # Success rate for matters
    
    # Metadata
    data_source = Column(String(50))  # Company Dataset, Manual Entry, etc.
    historical_performance = Column(JSON)
    additional_info = Column(JSON)  # Store CourtListener verification and analysis
    notes = Column(String(1000))
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

class VendorMarketInsight(Base):
    """Market insights derived from company dataset analysis"""
    __tablename__ = 'vendor_market_insights'
    
    id = Column(Integer, primary_key=True)
    practice_area = Column(String(100), nullable=False)
    region = Column(String(100))
    country = Column(String(100))
    
    # Market statistics
    total_firms = Column(Integer)
    avg_firm_size = Column(String(20))
    market_concentration = Column(Float)  # HHI or similar measure
    
    # Competitive landscape
    top_5_firms = Column(JSON)  # Names and sizes of top firms
    emerging_firms_count = Column(Integer)  # Firms founded in last 5 years
    
    # Growth trends
    new_entrants_last_year = Column(Integer)
    market_growth_rate = Column(Float)
    
    # Geographic distribution
    major_cities = Column(JSON)  # Cities with highest firm concentration
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VendorBenchmark(Base):
    """Benchmarking data for vendor performance comparison"""
    __tablename__ = 'vendor_benchmarks'
    
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    benchmark_type = Column(String(50))  # Rate, Performance, Quality, etc.
    
    # Benchmark metrics
    vendor_value = Column(Float)
    market_average = Column(Float)
    market_median = Column(Float)
    percentile_rank = Column(Float)  # Where vendor ranks (0-100)
    
    # Peer comparison
    peer_group = Column(String(100))  # Similar firms for comparison
    peer_average = Column(Float)
    
    # Time period
    period_start = Column(Date)
    period_end = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor = relationship("Vendor")
