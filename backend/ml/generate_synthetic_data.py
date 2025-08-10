import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

def generate_synthetic_invoices(n_invoices=100):
    """Generate synthetic invoice data for training and testing."""
    if n_invoices is None or n_invoices <= 0:
        raise ValueError("n_invoices must be a positive integer")
    
    # Define possible values
    vendors = [
        {"name": "Smith & Associates", "base_rate": 500, "category": "Law Firm"},
        {"name": "Johnson Legal", "base_rate": 450, "category": "Law Firm"},
        {"name": "Legal Solutions Inc", "base_rate": 400, "category": "Legal Services"},
        {"name": "Premier Law Group", "base_rate": 550, "category": "Law Firm"},
        {"name": "Tech Legal Partners", "base_rate": 600, "category": "Law Firm"}
    ]
    
    matter_types = ["Contract Review", "Litigation", "Patent Filing", "M&A", "Regulatory Compliance"]
    task_types = ["Research", "Document Review", "Court Appearance", "Client Meeting", "Drafting"]
    timekeeper_levels = ["Partner", "Senior Associate", "Associate", "Paralegal"]
    
    # Lists to store generated data
    invoices = []
    line_items = []
    
    # Generate invoices
    for i in range(n_invoices):
        # Select vendor
        vendor = random.choice(vendors)
        
        # Generate dates
        date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        # Generate invoice
        invoice = {
            'invoice_id': i + 1,
            'vendor_id': vendors.index(vendor) + 1,
            'vendor_name': vendor['name'],
            'matter_type': random.choice(matter_types),
            'invoice_number': f'INV-{date.year}-{i+1:04d}',
            'date': date.strftime('%Y-%m-%d'),
            'total_amount': 0,  # Will calculate from line items
            'status': 'paid' if random.random() > 0.2 else 'pending'
        }
        
        # Generate line items for this invoice
        n_lines = random.randint(3, 10)
        invoice_total = 0
        
        for j in range(n_lines):
            # Determine rate based on timekeeper level
            timekeeper = random.choice(timekeeper_levels)
            base_rate = vendor['base_rate']
            if timekeeper == "Partner":
                rate = base_rate
            elif timekeeper == "Senior Associate":
                rate = base_rate * 0.8
            elif timekeeper == "Associate":
                rate = base_rate * 0.6
            else:  # Paralegal
                rate = base_rate * 0.4
                
            # Generate random hours (occasionally generate anomalous values)
            is_anomaly = random.random() < 0.05  # 5% chance of anomaly
            if is_anomaly:
                hours = random.uniform(20, 50)  # Unusually high hours
            else:
                hours = random.uniform(0.5, 8)
                
            # Calculate line total
            line_total = hours * rate
            
            line_item = {
                'line_item_id': len(line_items) + 1,
                'invoice_id': invoice['invoice_id'],
                'description': f"{random.choice(task_types)} - {invoice['matter_type']}",
                'timekeeper_name': f"{random.choice(['John', 'Jane', 'Bob', 'Alice'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}",
                'timekeeper_title': timekeeper,
                'hours': hours,
                'rate': rate,
                'amount': line_total,
                'is_flagged': is_anomaly
            }
            
            line_items.append(line_item)
            invoice_total += line_total
        
        invoice['total_amount'] = invoice_total
        invoices.append(invoice)
    
    # Convert to DataFrames
    df_invoices = pd.DataFrame(invoices)
    df_line_items = pd.DataFrame(line_items)
    
    # Save to CSV files
    os.makedirs('data', exist_ok=True)
    df_invoices.to_csv('data/synthetic_invoices.csv', index=False)
    df_line_items.to_csv('data/synthetic_line_items.csv', index=False)
    
    return df_invoices, df_line_items

if __name__ == "__main__":
    print("Generating synthetic invoice data...")
    invoices_df, line_items_df = generate_synthetic_invoices(200)
    print(f"Generated {len(invoices_df)} invoices with {len(line_items_df)} line items")
    print("Data saved to data/synthetic_invoices.csv and data/synthetic_line_items.csv")
