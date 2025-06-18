from utils.sample_data_generator import generate_sample_data
from db.database import init_db, get_db_session
from db.database import Invoice, Vendor, Matter, LineItem, RiskFactor
import json
import os
from datetime import datetime

def load_sample_data():
    """Generate and load sample data into the database"""
    print("Generating sample data...")
    generate_sample_data(count=100)
    
    print("Initializing database...")
    init_db()
    
    session = get_db_session()
    try:
        print("Loading data into database...")
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Load vendors
        with open(os.path.join(data_dir, 'sample_vendors.json'), 'r') as f:
            vendors_data = json.load(f)
            
        for vendor_data in vendors_data:
            vendor = Vendor(
                name=vendor_data['name'],
                category=vendor_data['type'],
                hourly_rate_avg=vendor_data['hourly_rate_base'],
                performance_score=vendor_data['performance_score'],
                risk_profile=vendor_data['risk_profile'],
                historical_performance=vendor_data['rate_range']
            )
            session.add(vendor)
        
        session.commit()
        print(f"Loaded {len(vendors_data)} vendors")
        
        # Load matters
        with open(os.path.join(data_dir, 'sample_matters.json'), 'r') as f:
            matters_data = json.load(f)
            
        for matter_data in matters_data:
            matter = Matter(
                name=matter_data['name'],
                category=matter_data['type'],
                status='active',
                start_date=datetime.strptime(matter_data['start_date'], '%Y-%m-%d'),
                end_date=datetime.strptime(matter_data['end_date'], '%Y-%m-%d'),
                budget=matter_data['budget']
            )
            session.add(matter)
        
        session.commit()
        print(f"Loaded {len(matters_data)} matters")
        
        # Load invoices
        with open(os.path.join(data_dir, 'sample_invoices.json'), 'r') as f:
            invoices_data = json.load(f)
            
        for invoice_data in invoices_data:
            # Create invoice
            invoice = Invoice(
                invoice_number=invoice_data['invoice_number'],
                vendor_id=invoice_data['vendor_id'],
                matter_id=invoice_data['matter_id'],
                amount=invoice_data['amount'],
                date=datetime.strptime(invoice_data['date'], '%Y-%m-%d'),
                status=invoice_data['status'],
                hours=invoice_data['hours'],
                risk_score=invoice_data['risk_score']
            )
            session.add(invoice)
            session.flush()  # Get invoice ID
            
            # Add line items
            for item in invoice_data['line_items']:
                line_item = LineItem(
                    invoice_id=invoice.id,
                    description=item['description'],
                    hours=item['hours'],
                    rate=item['rate'],
                    amount=item['amount'],
                    timekeeper=item['timekeeper'],
                    timekeeper_title=item['timekeeper_title'],
                    date=datetime.strptime(item['date'], '%Y-%m-%d')
                )
                session.add(line_item)
            
            # Add risk factors
            for anomaly in invoice_data.get('anomalies', []):
                risk_factor = RiskFactor(
                    invoice_id=invoice.id,
                    factor_type=anomaly['type'],
                    description=anomaly['description'],
                    severity=anomaly['severity'],
                    impact_score=invoice.risk_score
                )
                session.add(risk_factor)
        
        session.commit()
        print(f"Loaded {len(invoices_data)} invoices with line items and risk factors")
        
    except Exception as e:
        session.rollback()
        print(f"Error loading data: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    load_sample_data()
