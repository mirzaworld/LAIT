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
        print_success(f"Loaded sample data: {len(data['invoices'])} invoices")
        return data['invoices']
    except FileNotFoundError:
        print_error(f"Sample data file not found: {SAMPLE_DATA_PATH}")
        return None
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in sample data file: {e}")
        return None

def create_invoice_via_api(token, invoice_data):
    """Create an invoice using the upload API endpoint"""
    
    # Prepare invoice data for API
    api_data = {
        "vendor": invoice_data["vendor_name"],
        "invoice_number": invoice_data["invoice_number"], 
        "date": invoice_data["invoice_date"],
        "filename": invoice_data["filename"],
        "lines": []
    }
    
    # Convert lines to API format
    for line in invoice_data["lines"]:
        api_line = {
            "description": line["description"],
            "amount": line["amount"],
            "line_number": line["line_number"],
            "attorney": line.get("attorney", "Unknown"),
            "billable_hours": line.get("billable_hours", 0),
            "rate": line.get("rate", 0)
        }
        api_data["lines"].append(api_line)
    
    # Call the upload API with JSON data
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/invoices/upload",
            json=api_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            invoice_id = result.get('invoice_id') or result.get('id')
            return True, invoice_id
        else:
            print_error(f"Failed to create invoice {invoice_data['invoice_number']}: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print_error(f"API request failed for invoice {invoice_data['invoice_number']}: {e}")
        return False, None

def seed_invoices(token, invoices_data):
    """Seed all sample invoices"""
    print_header("Seeding Invoice Data")
    
    success_count = 0
    total_count = len(invoices_data)
    
    for i, invoice in enumerate(invoices_data, 1):
        vendor = invoice["vendor_name"]
        invoice_num = invoice["invoice_number"]
        line_count = len(invoice["lines"])
        
        print_info(f"({i}/{total_count}) Creating invoice {invoice_num} from {vendor} ({line_count} lines)...")
        
        success, invoice_id = create_invoice_via_api(token, invoice)
        if success:
            print_success(f"Created invoice {invoice_num} (ID: {invoice_id})")
            success_count += 1
        else:
            print_error(f"Failed to create invoice {invoice_num}")
    
    print_header("Seeding Summary")
    print_success(f"Successfully created {success_count}/{total_count} invoices")
    
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
            print(f"  📊 Total Invoices: {metrics.get('total_invoices', 0)}")
            print(f"  💰 Total Amount: ${metrics.get('total_amount', 0):,.2f}")
            print(f"  📝 Total Lines: {metrics.get('total_lines', 0)}")
            print(f"  🚩 Flagged Lines: {metrics.get('flagged_lines', 0)}")
            print(f"  ⚖️  Vendors: {metrics.get('vendor_count', 0)}")
            
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
    
    # Final summary
    print_header("Seeding Complete")
    if success_count == len(invoices_data):
        print_success("🎉 All sample data seeded successfully!")
        print_info(f"Demo user: {DEMO_USER['email']} / {DEMO_USER['password']}")
        print_info("You can now:")
        print_info("  1. Login to the frontend with demo credentials")
        print_info(f"  2. View dashboard metrics: {BACKEND_URL}/api/dashboard/metrics")
        print_info(f"  3. List invoices: {BACKEND_URL}/api/invoices")
    else:
        print_warning("Some invoices failed to seed. Check the errors above.")

if __name__ == "__main__":
    main()
