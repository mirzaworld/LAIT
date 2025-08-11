#!/usr/bin/env python3
"""
Minimal LAIT Backend for Development and Testing
Provides essential authentication and API endpoints for the frontend.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'lait-development-secret-key-2024'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'])
jwt = JWTManager(app)

# Initialize simple SQLite database
def init_db():
    conn = sqlite3.connect('lait_minimal.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            company TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            vendor_name TEXT,
            amount REAL,
            date_received TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create a default admin user
    cursor.execute('SELECT id FROM users WHERE email = ?', ('admin@lait.com',))
    if not cursor.fetchone():
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (email, password_hash, first_name, last_name, company, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin@lait.com', password_hash, 'Admin', 'User', 'LAIT Demo', 'admin'))
        
        cursor.execute('''
            INSERT INTO users (email, password_hash, first_name, last_name, company, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('demo@lait.com', generate_password_hash('demo123'), 'Demo', 'User', 'LAIT Demo', 'user'))
    
    conn.commit()
    conn.close()

# Database helper functions
def get_db():
    return sqlite3.connect('lait_minimal.db')

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, password_hash, first_name, last_name, company, role FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(email, password_hash, first_name, last_name, company=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (email, password_hash, first_name, last_name, company)
        VALUES (?, ?, ?, ?, ?)
    ''', (email, password_hash, first_name, last_name, company))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

# Routes

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'LAIT Backend',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/health', methods=['GET'])
def auth_health():
    return jsonify({
        'status': 'healthy',
        'auth': 'active',
        'database': 'connected'
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        company = data.get('company', '')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Check if user already exists
        if get_user_by_email(email):
            return jsonify({'error': 'User already exists'}), 400

        # Create user
        password_hash = generate_password_hash(password)
        user_id = create_user(email, password_hash, first_name, last_name, company)

        # Generate token
        token = create_access_token(identity=str(user_id))

        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'company': company,
                'role': 'user'
            }
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        user_id, user_email, password_hash, first_name, last_name, company, role = user

        if not check_password_hash(password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate token
        token = create_access_token(identity=str(user_id))

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user_id,
                'email': user_email,
                'first_name': first_name,
                'last_name': last_name,
                'company': company,
                'role': role
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, first_name, last_name, company, role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': user[0],
            'email': user[1],
            'first_name': user[2],
            'last_name': user[3],
            'company': user[4],
            'role': user[5]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/metrics', methods=['GET'])
@jwt_required()
def dashboard_metrics():
    """Return dashboard metrics for the frontend"""
    return jsonify({
        'total_spend': 125000.00,
        'invoice_count': 45,
        'vendor_count': 12,
        'this_month_spend': 18500.00,
        'spend_trend': [
            {'month': 'Jan', 'amount': 12000},
            {'month': 'Feb', 'amount': 15000},
            {'month': 'Mar', 'amount': 18500},
        ],
        'top_vendors': [
            {'name': 'Baker & McKenzie', 'amount': 45000, 'invoices': 8},
            {'name': 'Deloitte Legal', 'amount': 32000, 'invoices': 5},
            {'name': 'Court Reporters Inc', 'amount': 18000, 'invoices': 12},
        ],
        'recent_invoices': [
            {'id': 1, 'vendor': 'Baker & McKenzie', 'amount': 8500, 'date': '2024-03-15', 'status': 'approved'},
            {'id': 2, 'vendor': 'Deloitte Legal', 'amount': 4200, 'date': '2024-03-14', 'status': 'pending'},
            {'id': 3, 'vendor': 'Court Reporters Inc', 'amount': 750, 'date': '2024-03-13', 'status': 'approved'},
        ]
    })

@app.route('/api/invoices/upload', methods=['POST'])
@jwt_required()
def upload_invoice():
    """Handle invoice upload"""
    try:
        user_id = int(get_jwt_identity())
        
        # Check for file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # For demo purposes, just save metadata
        vendor_name = request.form.get('vendor_name', 'Unknown Vendor')
        amount = float(request.form.get('amount', '0'))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO invoices (user_id, filename, vendor_name, amount)
            VALUES (?, ?, ?, ?)
        ''', (user_id, file.filename, vendor_name, amount))
        invoice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Invoice uploaded successfully',
            'invoice_id': invoice_id,
            'filename': file.filename,
            'vendor_name': vendor_name,
            'amount': amount
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get user's invoices"""
    try:
        user_id = int(get_jwt_identity())
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, filename, vendor_name, amount, date_received, status
            FROM invoices WHERE user_id = ?
            ORDER BY date_received DESC
        ''', (user_id,))
        invoices = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': inv[0],
            'filename': inv[1],
            'vendor_name': inv[2],
            'amount': inv[3],
            'date_received': inv[4],
            'status': inv[5]
        } for inv in invoices])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/vendors', methods=['GET'])
@jwt_required()
def vendor_analytics():
    """Get vendor analytics data"""
    return jsonify({
        'vendors': [
            {
                'id': 1,
                'name': 'Baker & McKenzie',
                'total_spend': 45000,
                'invoice_count': 8,
                'average_amount': 5625,
                'category': 'Law Firm'
            },
            {
                'id': 2,
                'name': 'Deloitte Legal',
                'total_spend': 32000,
                'invoice_count': 5,
                'average_amount': 6400,
                'category': 'Consulting'
            }
        ]
    })

if __name__ == '__main__':
    init_db()
    print("🚀 Starting LAIT Backend...")
    print("📊 Dashboard: http://localhost:8000/api/health")
    print("🔐 Auth endpoints available")
    print("📄 Invoice upload ready")
    app.run(host='0.0.0.0', port=8000, debug=True)
