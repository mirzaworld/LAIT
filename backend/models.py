"""
SQLAlchemy models for User, Invoice, InvoiceLine, Vendor, AuditLog
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    email = db.Column(db.String(120), unique=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    average_rate = db.Column(db.Float)
    diversity_score = db.Column(db.Float)
    success_rate = db.Column(db.Float)
    total_invoices = db.Column(db.Integer)
    total_spend = db.Column(db.Float)
    cluster = db.Column(db.Integer)
    invoices = db.relationship('Invoice', backref='vendor', lazy=True)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    vendor_name = db.Column(db.String(120))
    client_name = db.Column(db.String(120))
    matter = db.Column(db.String(120))
    invoice_number = db.Column(db.String(64))
    date = db.Column(db.Date)
    total_amount = db.Column(db.Float)
    pdf_s3_key = db.Column(db.String(256))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    overspend_risk = db.Column(db.Float)
    lines = db.relationship('InvoiceLine', backref='invoice', lazy=True)

class InvoiceLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(256))
    hours = db.Column(db.Float)
    rate = db.Column(db.Float)
    line_total = db.Column(db.Float)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.String(256))

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
