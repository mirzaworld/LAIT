import sqlite3
import os
from datetime import datetime, timedelta
import json

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'lait.db')

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        status TEXT DEFAULT 'active',
        budget REAL,
        start_date DATE,
        end_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        matter_id INTEGER NOT NULL,
        invoice_number TEXT,
        date DATE NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        description TEXT,
        risk_score REAL DEFAULT 0,
        hours REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vendor_id) REFERENCES vendors (id),
        FOREIGN KEY (matter_id) REFERENCES matters (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS line_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        hours REAL,
        rate REAL,
        timekeeper_name TEXT,
        timekeeper_title TEXT,
        date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS risk_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        factor_type TEXT NOT NULL,
        description TEXT,
        severity TEXT,
        impact_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
    )
    ''')
    
    # Insert some sample data if tables are empty
    if cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, role) VALUES
        ('admin', 'admin@lait.com', 'pbkdf2:sha256:150000$abc123', 'admin'),
        ('user', 'user@lait.com', 'pbkdf2:sha256:150000$xyz456', 'user')
        ''')
    
    if cursor.execute('SELECT COUNT(*) FROM vendors').fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO vendors (name, email, category) VALUES
        ('Smith & Associates', 'info@smith.com', 'Law Firm'),
        ('Johnson Legal', 'contact@johnsonlegal.com', 'Law Firm'),
        ('Legal Solutions Inc', 'info@legalsolutions.com', 'Legal Services')
        ''')
    
    if cursor.execute('SELECT COUNT(*) FROM matters').fetchone()[0] == 0:
        today = datetime.now().date()
        six_months_ago = (datetime.now() - timedelta(days=180)).date()
        one_year_later = (datetime.now() + timedelta(days=365)).date()
        
        cursor.execute('''
        INSERT INTO matters (name, description, category, status, budget, start_date, end_date) VALUES
        ('IP Litigation - TechCorp vs CompetitorX', 'Patent infringement case', 'Litigation', 'active', 500000, ?, ?),
        ('M&A Advisory - Acquisition of StartupY', 'Due diligence for acquisition', 'M&A', 'active', 300000, ?, ?),
        ('Regulatory Compliance - FDA Approval', 'FDA compliance review', 'Regulatory', 'completed', 250000, ?, ?)
        ''', (six_months_ago.isoformat(), one_year_later.isoformat(), 
              (today - timedelta(days=90)).isoformat(), (today + timedelta(days=90)).isoformat(),
              six_months_ago.isoformat(), (today - timedelta(days=30)).isoformat()))
    
    if cursor.execute('SELECT COUNT(*) FROM invoices').fetchone()[0] == 0:
        today = datetime.now().date()
        
        cursor.execute('''
        INSERT INTO invoices (vendor_id, matter_id, invoice_number, date, amount, status, risk_score, hours) VALUES
        (1, 1, 'INV-001', ?, 120000, 'paid', 3.5, 240),
        (1, 1, 'INV-002', ?, 150000, 'paid', 5.2, 310),
        (1, 1, 'INV-003', ?, 90000, 'pending', 4.8, 185),
        (2, 2, 'INV-004', ?, 100000, 'paid', 2.1, 180),
        (2, 2, 'INV-005', ?, 120000, 'pending', 6.7, 215),
        (3, 3, 'INV-006', ?, 80000, 'paid', 1.8, 160),
        (3, 3, 'INV-007', ?, 100000, 'paid', 4.1, 200),
        (3, 3, 'INV-008', ?, 90000, 'paid', 3.2, 175)
        ''', ((today - timedelta(days=150)).isoformat(), 
              (today - timedelta(days=90)).isoformat(),
              (today - timedelta(days=30)).isoformat(),
              (today - timedelta(days=60)).isoformat(),
              (today - timedelta(days=30)).isoformat(),
              (today - timedelta(days=150)).isoformat(),
              (today - timedelta(days=90)).isoformat(),
              (today - timedelta(days=30)).isoformat()))
    
    if cursor.execute('SELECT COUNT(*) FROM line_items').fetchone()[0] == 0:
        today = datetime.now().date()
        
        # Add some sample line items
        for invoice_id in range(1, 9):
            if invoice_id <= 3:  # For matter 1
                cursor.execute('''
                INSERT INTO line_items (invoice_id, description, amount, hours, rate, timekeeper_name, timekeeper_title, date) VALUES
                (?, 'Legal research', ?, ?, 450, 'John Smith', 'Partner', ?),
                (?, 'Document review', ?, ?, 350, 'Alice Johnson', 'Associate', ?),
                (?, 'Client meetings', ?, ?, 450, 'John Smith', 'Partner', ?),
                (?, 'Court preparation', ?, ?, 250, 'Mike Davis', 'Paralegal', ?)
                ''', (invoice_id, 25000, 55, today - timedelta(days=30*invoice_id),
                      invoice_id, 35000, 100, today - timedelta(days=30*invoice_id),
                      invoice_id, 20000, 45, today - timedelta(days=30*invoice_id),
                      invoice_id, 10000, 40, today - timedelta(days=30*invoice_id)))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def get_db_session():
    """Dummy session for compatibility with SQLAlchemy code"""
    return SQLiteSession()

class SQLiteSession:
    """A class that mimics some basic SQLAlchemy session functionality"""
    
    def __init__(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()
    
    def close(self):
        self.conn.close()
    
    def execute(self, query, params=None):
        if params:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)
    
    def query(self, model):
        return SQLiteQuery(self.conn, model)
    
    def commit(self):
        self.conn.commit()

class SQLiteQuery:
    """A class that mimics some basic SQLAlchemy query functionality"""
    
    def __init__(self, conn, model):
        self.conn = conn
        self.cursor = conn.cursor()
        self.model = model
        self.model_name = model.__name__.lower() + 's'
        self.filters = []
        self.order_bys = []
        self.limit_val = None
        self.joins = []
    
    def filter(self, condition):
        # This is a simplified version that won't handle complex conditions
        self.filters.append(condition)
        return self
    
    def order_by(self, order):
        self.order_bys.append(order)
        return self
    
    def limit(self, limit_val):
        self.limit_val = limit_val
        return self
    
    def join(self, model, condition=None):
        self.joins.append((model, condition))
        return self
    
    def first(self):
        # Build a very simple query - this won't handle all SQLAlchemy cases
        query = f"SELECT * FROM {self.model_name}"
        
        if self.filters:
            query += " WHERE " + " AND ".join(["1=1" for _ in self.filters])  # Simplified
        
        query += " LIMIT 1"
        
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result:
            return self._row_to_model(result)
        return None
    
    def all(self):
        # Build a very simple query - this won't handle all SQLAlchemy cases
        query = f"SELECT * FROM {self.model_name}"
        
        if self.filters:
            query += " WHERE " + " AND ".join(["1=1" for _ in self.filters])  # Simplified
        
        if self.limit_val:
            query += f" LIMIT {self.limit_val}"
            
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [self._row_to_model(row) for row in results]
    
    def _row_to_model(self, row):
        return self.model(**dict(row))

# Define model classes with proper attributes
class Invoice:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.vendor_id = kwargs.get('vendor_id')
        self.matter_id = kwargs.get('matter_id')
        self.invoice_number = kwargs.get('invoice_number')
        self.date = kwargs.get('date')
        self.amount = kwargs.get('amount')
        self.status = kwargs.get('status', 'pending')
        self.description = kwargs.get('description')
        self.risk_score = kwargs.get('risk_score', 0)
        self.hours = kwargs.get('hours', 0)
        self.created_at = kwargs.get('created_at')

class LineItem:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.invoice_id = kwargs.get('invoice_id')
        self.description = kwargs.get('description')
        self.amount = kwargs.get('amount')
        self.hours = kwargs.get('hours')
        self.rate = kwargs.get('rate')
        self.timekeeper_name = kwargs.get('timekeeper_name')
        self.timekeeper_title = kwargs.get('timekeeper_title')
        self.date = kwargs.get('date')
        self.created_at = kwargs.get('created_at')

class Vendor:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.phone = kwargs.get('phone')
        self.address = kwargs.get('address')
        self.category = kwargs.get('category')
        self.created_at = kwargs.get('created_at')

class Matter:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.category = kwargs.get('category')
        self.status = kwargs.get('status', 'active')
        self.budget = kwargs.get('budget')
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.created_at = kwargs.get('created_at')

class RiskFactor:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.invoice_id = kwargs.get('invoice_id')
        self.factor_type = kwargs.get('factor_type')
        self.description = kwargs.get('description')
        self.severity = kwargs.get('severity')
        self.impact_score = kwargs.get('impact_score')
        self.created_at = kwargs.get('created_at')

class User:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.password_hash = kwargs.get('password_hash')
        self.role = kwargs.get('role', 'user')
        self.created_at = kwargs.get('created_at')

# Initialize database if this file is run directly
if __name__ == "__main__":
    init_db()
