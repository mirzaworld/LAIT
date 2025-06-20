#!/usr/bin/env python3
"""
Quick script to add sample data for testing frontend-backend integration
"""

import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api"

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "email": "admin@lait.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def add_sample_data():
    """Add sample data to the database"""
    token = get_auth_token()
    if not token:
        print("Could not authenticate")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Add sample vendors
    vendors = [
        {"name": "Morrison & Foerster LLP", "category": "AmLaw 100"},
        {"name": "Baker McKenzie", "category": "Global"},
        {"name": "Latham & Watkins", "category": "AmLaw 100"},
        {"name": "Skadden Arps", "category": "AmLaw 100"},
        {"name": "White & Case", "category": "Global"}
    ]
    
    vendor_ids = []
    for vendor in vendors:
        try:
            response = requests.post(f"{BASE_URL}/vendors", json=vendor, headers=headers)
            if response.status_code in [200, 201]:
                vendor_ids.append(response.json().get("id"))
                print(f"Added vendor: {vendor['name']}")
            else:
                print(f"Failed to add vendor {vendor['name']}: {response.text}")
        except Exception as e:
            print(f"Error adding vendor {vendor['name']}: {e}")
    
    # Add sample matters
    matters = [
        {"name": "IP Litigation - TechCorp vs CompetitorX", "practice_area": "Litigation"},
        {"name": "M&A Advisory - Acquisition of StartupY", "practice_area": "Corporate"},
        {"name": "Regulatory Compliance - FDA Approval", "practice_area": "Regulatory"},
        {"name": "Employment Dispute Resolution", "practice_area": "Employment"},
        {"name": "Contract Negotiation - Software License", "practice_area": "IP"}
    ]
    
    matter_ids = []
    for matter in matters:
        try:
            response = requests.post(f"{BASE_URL}/matters", json=matter, headers=headers)
            if response.status_code in [200, 201]:
                matter_ids.append(response.json().get("id"))
                print(f"Added matter: {matter['name']}")
            else:
                print(f"Failed to add matter {matter['name']}: {response.text}")
        except Exception as e:
            print(f"Error adding matter {matter['name']}: {e}")
    
    # Add sample invoices
    if vendor_ids and matter_ids:
        for i in range(20):
            days_ago = random.randint(1, 365)
            invoice_date = datetime.now() - timedelta(days=days_ago)
            
            invoice = {
                "vendor_id": random.choice(vendor_ids),
                "matter_id": random.choice(matter_ids),
                "amount": random.randint(5000, 100000),
                "date": invoice_date.strftime("%Y-%m-%d"),
                "status": random.choice(["pending", "approved", "flagged", "processing"]),
                "risk_score": random.randint(1, 10)
            }
            
            try:
                response = requests.post(f"{BASE_URL}/invoices", json=invoice, headers=headers)
                if response.status_code in [200, 201]:
                    print(f"Added invoice {i+1}")
                else:
                    print(f"Failed to add invoice {i+1}: {response.text}")
            except Exception as e:
                print(f"Error adding invoice {i+1}: {e}")
    
    print("Sample data creation completed!")

if __name__ == "__main__":
    add_sample_data()
