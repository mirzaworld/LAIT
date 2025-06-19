"""
SQLAlchemy models for User, Invoice, InvoiceLine, Vendor, AuditLog
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(TimestampMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    invoices = db.relationship('Invoice', backref='uploaded_by_user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

class Vendor(TimestampMixin, db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    average_rate = db.Column(db.Float)
    diversity_score = db.Column(db.Float)
    success_rate = db.Column(db.Float)
    total_invoices = db.Column(db.Integer)
    total_spend = db.Column(db.Float)
    cluster = db.Column(db.Integer)
    invoices = db.relationship('Invoice', backref='vendor', lazy='dynamic')
    
    __table_args__ = (
        db.Index('idx_vendor_cluster', 'cluster'),
        db.Index('idx_vendor_total_spend', 'total_spend')
    )

class Invoice(TimestampMixin, db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(64))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    matter_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending', index=True)
    description = db.Column(db.Text)
    hours = db.Column(db.Float)
    rate = db.Column(db.Float)
    risk_score = db.Column(db.Float)
    analysis_result = db.Column(db.JSON)
    pdf_s3_key = db.Column(db.String(256))
    overspend_risk = db.Column(db.Float)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    lines = db.relationship('InvoiceLine', backref='invoice', lazy=True)

    __table_args__ = (
        db.Index('idx_invoice_date', 'date'),
        db.Index('idx_invoice_vendor', 'vendor_id'),
        db.Index('idx_invoice_status', 'status')
    )

class InvoiceLine(TimestampMixin, db.Model):
    __tablename__ = 'invoice_lines'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    description = db.Column(db.Text)
    hours = db.Column(db.Float)
    rate = db.Column(db.Float)
    line_total = db.Column(db.Float)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(256))

class AuditLog(TimestampMixin, db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    
    __table_args__ = (
        db.Index('idx_audit_user', 'user_id'),
        db.Index('idx_audit_action', 'action'),
        db.Index('idx_audit_resource', 'resource_type', 'resource_id')
    )
