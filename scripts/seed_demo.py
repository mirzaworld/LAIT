#!/usr/bin/env python3
"""
LAIT Demo Data Seeder
====================

Creates demo user and loads sample invoice data into the database
using the same code paths as the actual upload functionality.

Usage:
    python scripts/seed_demo.py
    
Requirements:
    - Backend must be running on localhost:5003
    - Or set BACKEND_URL environment variable
"""

import sys
import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Add backend directory to path to import functions
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5003')
SAMPLE_DATA_PATH = Path(__file__).parent.parent / 'data' / 'staging' / 'sample_invoice.json'

# Demo user credentials
DEMO_USER = {
    "email": "demo@lait.com",
    "password": "demo123!",
    "firstName": "Demo",
    "lastName": "User", 
    "company": "LAIT Demo Corp"
}

class ColorOutput:
    """Simple colored console output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{ColorOutput.GREEN}✅ {msg}{ColorOutput.END}")

def print_error(msg):
    print(f"{ColorOutput.RED}❌ {msg}{ColorOutput.END}")

def print_info(msg):
    print(f"{ColorOutput.BLUE}ℹ️  {msg}{ColorOutput.END}")

def print_warning(msg):
    print(f"{ColorOutput.YELLOW}⚠️  {msg}{ColorOutput.END}")

def print_header(msg):
    print(f"\n{ColorOutput.BOLD}{ColorOutput.CYAN}=== {msg} ==={ColorOutput.END}")

def check_backend_health():
    """Check if backend is running and accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            return True
        else:
            print_error(f"Backend health check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to backend at {BACKEND_URL}: {e}")
        print_info("Make sure the backend is running:")
        print_info("cd backend && python app_real.py")
        return False

def create_or_login_demo_user():
    """Create demo user or login if already exists"""
    print_header("Demo User Setup")
    
    # Try to register demo user
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json=DEMO_USER,
            timeout=10
        )
        
        if response.status_code == 201:
            print_success("Demo user created successfully")
            token = response.json().get('token')
            return token
        elif response.status_code == 409:
            print_info("Demo user already exists, logging in...")
            # User exists, try to login
            login_data = {
                "email": DEMO_USER["email"],
                "password": DEMO_USER["password"]
            }
            response = requests.post(
                f"{BACKEND_URL}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print_success("Demo user logged in successfully")
                token = response.json().get('token')
                return token
            else:
                print_error(f"Login failed: {response.text}")
                return None
        else:
            print_error(f"Registration failed: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to create/login demo user: {e}")
        return None

def load_sample_data():
    """Load sample invoice data from JSON file"""
    try:
        with open(SAMPLE_DATA_PATH, 'r') as f:
            data = json.load(f)
        print_success(f"Loaded sample data: {len(data)} invoices")
        return data
    except FileNotFoundError:
        print_error(f"Sample data file not found: {SAMPLE_DATA_PATH}")
        return None
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in sample data file: {e}")
        return None

def create_invoice_via_api(token, invoice_data):
    """Create an invoice using the upload API endpoint with file simulation"""
    
    # Create a temporary text file with line items
    invoice_content = f"Invoice: {invoice_data['matter_id']}\n"
    invoice_content += f"Client: {invoice_data['client_name']}\n"
    invoice_content += f"Vendor: {invoice_data['vendor']}\n"
    invoice_content += f"Date: {invoice_data['invoice_date']}\n"
    invoice_content += f"Description: {invoice_data['description']}\n"
    invoice_content += f"Total: ${invoice_data['total_amount']:,.2f}\n\n"
    
    # Add line items
    for line_item in invoice_data['line_items']:
        invoice_content += f"{line_item}\n"
    
    # Create form data as if uploading a file
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Simulate file upload using multipart form data
    files = {
        'file': (f"{invoice_data['matter_id']}.txt", invoice_content, 'text/plain')
    }
    
    form_data = {
        'client_name': invoice_data['client_name'],
        'matter_id': invoice_data['matter_id']
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/invoices/upload",
            files=files,
            data=form_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            invoice_id = result.get('invoice_id') or result.get('id')
            lines_processed = result.get('lines_processed', 0)
            return True, invoice_id, lines_processed
        else:
            print_error(f"Failed to create invoice {invoice_data['matter_id']}: {response.text}")
            return False, None, 0
            
    except requests.exceptions.RequestException as e:
        print_error(f"API request failed for invoice {invoice_data['matter_id']}: {e}")
        return False, None, 0

def seed_invoices(token, invoices_data):
    """Seed all sample invoices"""
    print_header("Seeding Invoice Data")
    
    success_count = 0
    total_count = len(invoices_data)
    total_lines = 0
    
    for i, invoice in enumerate(invoices_data, 1):
        client = invoice["client_name"]
        matter_id = invoice["matter_id"]
        vendor = invoice["vendor"]
        line_count = len(invoice["line_items"])
        
        print_info(f"({i}/{total_count}) Creating invoice {matter_id}")
        print_info(f"  Client: {client}")
        print_info(f"  Vendor: {vendor}")
        print_info(f"  Lines: {line_count}")
        
        success, invoice_id, lines_processed = create_invoice_via_api(token, invoice)
        if success:
            print_success(f"✅ Created invoice {matter_id} (ID: {invoice_id}, Lines: {lines_processed})")
            success_count += 1
            total_lines += lines_processed
        else:
            print_error(f"❌ Failed to create invoice {matter_id}")
        
        print()  # Add spacing between invoices
    
    print_header("Seeding Summary")
    print_success(f"Successfully created {success_count}/{total_count} invoices")
    print_success(f"Total lines processed: {total_lines}")
    
    if success_count < total_count:
        print_warning(f"{total_count - success_count} invoices failed to create")
    
    return success_count

def get_dashboard_metrics(token):
    """Fetch and display dashboard metrics"""
    print_header("Dashboard Metrics")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/dashboard/metrics",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            metrics = response.json()
            
            print_success("Dashboard metrics loaded:")
            print(f"  📊 Invoices Count: {metrics.get('invoices_count', 0)}")
            print(f"  💰 Total Spend: ${metrics.get('total_spend', 0):,.2f}")
            print(f"  📝 Total Lines: {metrics.get('total_lines', 0)}")
            print(f"  🚩 Flagged Lines: {metrics.get('flagged_lines', 0)}")
            print(f"  ⚖️  Average Score: {metrics.get('avg_risk_score', 0):.2f}")
            
            flagged_pct = 0
            if metrics.get('total_lines', 0) > 0:
                flagged_pct = (metrics.get('flagged_lines', 0) / metrics.get('total_lines', 0)) * 100
            print(f"  🎯 Flagged Rate: {flagged_pct:.1f}%")
            
            return metrics
        else:
            print_error(f"Failed to fetch metrics: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to fetch dashboard metrics: {e}")
        return None

def main():
    """Main seeder function"""
    print(f"{ColorOutput.BOLD}{ColorOutput.PURPLE}")
    print("🌱 LAIT Demo Data Seeder")
    print("========================")
    print(f"{ColorOutput.END}")
    
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Sample data: {SAMPLE_DATA_PATH}")
    
    # 1. Check backend health
    if not check_backend_health():
        sys.exit(1)
    print_success("Backend is running and accessible")
    
    # 2. Create/login demo user
    token = create_or_login_demo_user()
    if not token:
        print_error("Failed to setup demo user")
        sys.exit(1)
    
    # 3. Load sample data
    invoices_data = load_sample_data()
    if not invoices_data:
        sys.exit(1)
    
    # 4. Seed invoices
    success_count = seed_invoices(token, invoices_data)
    
    # 5. Show dashboard metrics
    if success_count > 0:
        get_dashboard_metrics(token)
    
    # Final summary with usage instructions
    print_header("Seeding Complete")
    if success_count == len(invoices_data):
        print_success("🎉 All sample data seeded successfully!")
        print_info(f"Demo user: {DEMO_USER['email']} / {DEMO_USER['password']}")
        print_info("You can now:")
        print_info("  1. Login to the frontend with demo credentials")
        print_info(f"  2. View dashboard: http://localhost:5173")
        print_info(f"  3. API endpoints:")
        print_info(f"     • Metrics: {BACKEND_URL}/api/dashboard/metrics")
        print_info(f"     • Invoices: {BACKEND_URL}/api/invoices")
        
        # Print the count for Makefile output
        print_header("COUNT INSERTED")
        print_success(f"{success_count} invoices inserted successfully")
        
        # Show sample curl command with token
        print_header("Sample API Commands")
        print_info("To test the API with curl:")
        print_info(f'export JWT_TOKEN="{token[:50]}..."')
        print_info(f'curl -H "Authorization: Bearer $JWT_TOKEN" {BACKEND_URL}/api/dashboard/metrics')
        
    else:
        print_warning("Some invoices failed to seed. Check the errors above.")
        print_info(f"Successfully inserted: {success_count} invoices")

if __name__ == "__main__":
    main()
