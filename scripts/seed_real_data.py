"""
Real data seeding script for LAIT system
Creates realistic legal industry data for development and testing
"""

from backend.db.database import get_db_session, engine
from backend.models.db_models import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import uuid
from decimal import Decimal

# Sample data for realistic legal industry content
LAW_FIRMS = [
    {"name": "Morrison & Foerster LLP", "category": "AmLaw 100", "size": "large"},
    {"name": "Baker McKenzie", "category": "Global", "size": "large"},
    {"name": "Latham & Watkins", "category": "AmLaw 100", "size": "large"},
    {"name": "Skadden Arps", "category": "AmLaw 50", "size": "large"},
    {"name": "White & Case", "category": "Global", "size": "large"},
    {"name": "DLA Piper", "category": "AmLaw 100", "size": "large"},
    {"name": "Kirkland & Ellis", "category": "AmLaw 10", "size": "large"},
    {"name": "Sullivan & Cromwell", "category": "White Shoe", "size": "large"},
    {"name": "Davis Polk & Wardwell", "category": "White Shoe", "size": "large"},
    {"name": "Simpson Thacher & Bartlett", "category": "AmLaw 50", "size": "large"},
    {"name": "Regional Law Group", "category": "Regional", "size": "medium"},
    {"name": "Boutique Litigation Partners", "category": "Boutique", "size": "small"},
    {"name": "Intellectual Property Specialists", "category": "IP Boutique", "size": "small"},
    {"name": "Employment Law Associates", "category": "Labor Boutique", "size": "small"},
    {"name": "Corporate Counsel LLP", "category": "Regional", "size": "medium"}
]

PRACTICE_AREAS = [
    "Corporate/M&A", "Litigation", "Intellectual Property", "Employment Law",
    "Real Estate", "Tax", "Regulatory", "Bankruptcy", "Securities", "Antitrust",
    "Environmental", "Healthcare", "Energy", "Finance", "Insurance"
]

MATTER_TYPES = [
    "M&A Transaction", "IPO", "Contract Negotiation", "Litigation Defense",
    "Patent Filing", "Trademark Registration", "Employment Dispute",
    "Regulatory Compliance", "Real Estate Transaction", "Tax Planning",
    "Bankruptcy Proceeding", "Securities Investigation", "Antitrust Review",
    "Environmental Permitting", "Healthcare Compliance"
]

CLIENT_COMPANIES = [
    "TechCorp Industries", "Global Manufacturing Inc", "Financial Services Group",
    "Healthcare Systems LLC", "Energy Solutions Corp", "Retail Enterprises",
    "Pharmaceutical Research Inc", "Automotive Technologies", "Media Holdings Ltd",
    "Biotechnology Innovations", "Telecommunications Corp", "Real Estate Partners",
    "Insurance Solutions Inc", "Food & Beverage Corp", "Transportation Systems"
]

INVOICE_DESCRIPTIONS = [
    "Legal services for Q{quarter} {year}",
    "Corporate governance and compliance review",
    "Due diligence and transaction documentation",
    "Discovery and motion practice",
    "Contract review and negotiation",
    "Regulatory filing and compliance",
    "Patent prosecution and IP strategy",
    "Employment matter resolution",
    "Litigation management and settlement negotiations",
    "Securities compliance and reporting",
    "Environmental permitting and compliance",
    "Tax planning and structuring",
    "Merger and acquisition support",
    "Intellectual property portfolio management",
    "Regulatory investigation response"
]

def create_session():
    """Create database session"""
    Session = sessionmaker(bind=engine)
    return Session()

def seed_vendors(session, count=15):
    """Seed realistic vendor data"""
    vendors = []
    
    for i, firm_data in enumerate(LAW_FIRMS[:count]):
        vendor = Vendor(
            id=f"V{str(i+1).zfill(3)}",
            name=firm_data["name"],
            category=firm_data["category"],
            spend=random.randint(100000, 2000000),
            matter_count=random.randint(5, 50),
            avg_rate=random.randint(400, 1200),
            performance_score=random.randint(75, 98),
            diversity_score=random.randint(60, 95),
            on_time_rate=random.randint(85, 99)
        )
        vendors.append(vendor)
        session.add(vendor)
    
    session.commit()
    return vendors

def seed_matters(session, vendors, count=50):
    """Seed realistic matter data"""
    matters = []
    
    for i in range(count):
        start_date = datetime.now() - timedelta(days=random.randint(30, 730))
        
        matter = Matter(
            id=f"MAT-{str(i+1).zfill(4)}",
            name=f"{random.choice(MATTER_TYPES)} - {random.choice(CLIENT_COMPANIES)}",
            description=f"{random.choice(PRACTICE_AREAS)} matter for {random.choice(CLIENT_COMPANIES)}",
            practice_area=random.choice(PRACTICE_AREAS),
            matter_type=random.choice(MATTER_TYPES),
            status=random.choice(['open', 'closed', 'on_hold']),
            budget=Decimal(str(random.randint(50000, 1000000))),
            start_date=start_date,
            responsible_attorney=f"Attorney {i+1}"
        )
        matters.append(matter)
        session.add(matter)
    
    session.commit()
    return matters

def seed_invoices(session, vendors, matters, count=200):
    """Seed realistic invoice data"""
    invoices = []
    statuses = ['approved', 'pending', 'flagged', 'processing']
    status_weights = [0.6, 0.2, 0.1, 0.1]  # 60% approved, 20% pending, etc.
    
    for i in range(count):
        vendor = random.choice(vendors)
        matter = random.choice(matters)
        
        # Create realistic invoice amounts based on vendor rates and hours
        hours = round(random.uniform(10, 150), 1)
        rate = vendor.avg_rate + random.randint(-100, 200)  # Some variation from base rate
        amount = Decimal(str(round(hours * rate, 2)))
        
        # Create invoice date within the last year
        invoice_date = datetime.now() - timedelta(days=random.randint(1, 365))
        
        # Risk scoring based on various factors
        risk_score = calculate_risk_score(amount, rate, vendor, matter)
        
        status = random.choices(statuses, weights=status_weights)[0]
        
        invoice = Invoice(
            id=f"INV-{datetime.now().year}-{str(i+1).zfill(3)}",
            vendor=vendor.name,
            vendor_id=vendor.id,
            matter_id=matter.id,
            amount=amount,
            status=status,
            date=invoice_date,
            due_date=invoice_date + timedelta(days=30),
            description=random.choice(INVOICE_DESCRIPTIONS).format(
                quarter=random.randint(1, 4),
                year=random.choice([2024, 2025])
            ),
            hours=Decimal(str(hours)),
            rate=Decimal(str(rate)),
            risk_score=risk_score,
            category=matter.practice_area,
            total=amount
        )
        invoices.append(invoice)
        session.add(invoice)
    
    session.commit()
    return invoices

def calculate_risk_score(amount, rate, vendor, matter):
    """Calculate realistic risk scores based on multiple factors"""
    risk_score = 0
    
    # Amount-based risk
    if amount > 100000:
        risk_score += 30
    elif amount > 50000:
        risk_score += 15
    elif amount > 25000:
        risk_score += 5
    
    # Rate-based risk
    if rate > vendor.avg_rate * 1.5:
        risk_score += 25
    elif rate > vendor.avg_rate * 1.2:
        risk_score += 10
    
    # Vendor performance risk
    if vendor.performance_score < 80:
        risk_score += 20
    elif vendor.performance_score < 90:
        risk_score += 10
    
    # Random variation for realistic distribution
    risk_score += random.randint(-5, 15)
    
    return max(0, min(100, risk_score))

def seed_line_items(session, invoices, count_per_invoice_range=(3, 15)):
    """Seed realistic line items for invoices"""
    line_items = []
    
    activities = [
        "Legal Research", "Document Review", "Client Communication", "Court Appearance",
        "Deposition Preparation", "Contract Drafting", "Due Diligence", "Settlement Negotiation",
        "Expert Witness Consultation", "Regulatory Filing", "Patent Research", "Trademark Search",
        "Employment Counseling", "Compliance Review", "Strategic Planning"
    ]
    
    attorney_titles = ["Partner", "Senior Associate", "Associate", "Junior Associate", "Paralegal"]
    attorney_rates = {"Partner": (800, 1500), "Senior Associate": (500, 800), 
                     "Associate": (300, 600), "Junior Associate": (200, 400), 
                     "Paralegal": (150, 300)}
    
    for invoice in invoices:
        num_items = random.randint(*count_per_invoice_range)
        total_hours = float(invoice.hours)
        
        for i in range(num_items):
            title = random.choice(attorney_titles)
            rate_range = attorney_rates[title]
            line_rate = random.randint(*rate_range)
            line_hours = round(random.uniform(0.5, min(8, total_hours / num_items * 2)), 1)
            
            line_item = LineItem(
                id=f"{invoice.id}-{i+1}",
                invoice_id=invoice.id,
                description=f"{random.choice(activities)} by {title}",
                attorney_name=f"{random.choice(['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia'])}",
                attorney_rate=Decimal(str(line_rate)),
                hours=Decimal(str(line_hours)),
                amount=Decimal(str(round(line_hours * line_rate, 2))),
                date=invoice.date + timedelta(days=random.randint(0, 7)),
                task_code=f"T{random.randint(1000, 9999)}",
                activity_code=f"A{random.randint(100, 999)}"
            )
            line_items.append(line_item)
            session.add(line_item)
    
    session.commit()
    return line_items

def seed_risk_factors(session, invoices, count=50):
    """Seed realistic risk factors"""
    risk_types = [
        "Rate Increase", "Unusual Hours", "Budget Overrun", "Duplicate Billing",
        "Compliance Issue", "Missing Documentation", "Unauthorized Work",
        "Vendor Performance Decline", "Pattern Anomaly", "Expense Irregularity"
    ]
    
    severities = ["low", "medium", "high"]
    
    risk_factors = []
    
    for i in range(count):
        invoice = random.choice(invoices)
        
        risk_factor = RiskFactor(
            id=f"RF-{str(i+1).zfill(3)}",
            invoice_id=invoice.id,
            risk_type=random.choice(risk_types),
            severity=random.choice(severities),
            description=f"Potential {random.choice(risk_types).lower()} detected in invoice {invoice.id}",
            impact_score=random.randint(1, 10),
            likelihood=random.uniform(0.1, 0.9),
            created_at=datetime.now()
        )
        risk_factors.append(risk_factor)
        session.add(risk_factor)
    
    session.commit()
    return risk_factors

def main():
    """Main seeding function"""
    print("🌱 Starting LAIT data seeding...")
    
    # Create database session
    session = create_session()
    
    try:
        # Clear existing data (be careful in production!)
        print("🗑️  Clearing existing data...")
        session.query(RiskFactor).delete()
        session.query(LineItem).delete()
        session.query(Invoice).delete()
        session.query(Matter).delete()
        session.query(Vendor).delete()
        session.commit()
        
        # Seed vendors
        print("🏢 Seeding vendors...")
        vendors = seed_vendors(session, count=15)
        print(f"✅ Created {len(vendors)} vendors")
        
        # Seed matters
        print("📋 Seeding matters...")
        matters = seed_matters(session, vendors, count=50)
        print(f"✅ Created {len(matters)} matters")
        
        # Seed invoices
        print("📄 Seeding invoices...")
        invoices = seed_invoices(session, vendors, matters, count=200)
        print(f"✅ Created {len(invoices)} invoices")
        
        # Seed line items
        print("📝 Seeding line items...")
        line_items = seed_line_items(session, invoices)
        print(f"✅ Created {len(line_items)} line items")
        
        # Seed risk factors
        print("⚠️  Seeding risk factors...")
        risk_factors = seed_risk_factors(session, invoices, count=50)
        print(f"✅ Created {len(risk_factors)} risk factors")
        
        print("🎉 Data seeding completed successfully!")
        
        # Print summary statistics
        print("\n📊 Data Summary:")
        print(f"   Vendors: {len(vendors)}")
        print(f"   Matters: {len(matters)}")
        print(f"   Invoices: {len(invoices)}")
        print(f"   Line Items: {len(line_items)}")
        print(f"   Risk Factors: {len(risk_factors)}")
        
        # Calculate totals
        total_spend = sum(float(invoice.amount) for invoice in invoices)
        avg_invoice = total_spend / len(invoices) if invoices else 0
        
        print(f"\n💰 Financial Summary:")
        print(f"   Total Spend: ${total_spend:,.2f}")
        print(f"   Average Invoice: ${avg_invoice:,.2f}")
        print(f"   Largest Invoice: ${max(float(invoice.amount) for invoice in invoices):,.2f}")
        
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
