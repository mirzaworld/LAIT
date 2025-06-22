#!/usr/bin/env python3
"""
Data Seeding Script for LAIT
Populates the database with realistic legal invoice data for testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import init_db, get_db_session, User, Invoice, Vendor, Matter
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with realistic legal data"""
    
    try:
        # Initialize database
        init_db()
        session = get_db_session()
        
        # Check if data already exists
        if session.query(Vendor).count() > 0:
            logger.info("Database already contains data. Skipping seeding.")
            return
        
        logger.info("Seeding database with realistic legal data...")
        
        # Create realistic law firms (vendors)
        law_firms = [
            {
                'name': 'Morrison & Foerster LLP',
                'industry_category': 'AmLaw 100',
                'practice_area': 'Corporate Law',
                'firm_size_category': 'Large',
                'employee_count': 1000,
                'country': 'United States',
                'state_province': 'California',
                'city': 'San Francisco',
                'risk_profile': 0.15,
                'diversity_score': 78.5
            },
            {
                'name': 'Baker McKenzie',
                'industry_category': 'Global Elite',
                'practice_area': 'International Law',
                'firm_size_category': 'Large',
                'employee_count': 4500,
                'country': 'United States',
                'state_province': 'Illinois',
                'city': 'Chicago',
                'risk_profile': 0.12,
                'diversity_score': 82.3
            },
            {
                'name': 'Latham & Watkins LLP',
                'industry_category': 'AmLaw 100',
                'practice_area': 'Litigation',
                'firm_size_category': 'Large',
                'employee_count': 2800,
                'country': 'United States',
                'state_province': 'California',
                'city': 'Los Angeles',
                'risk_profile': 0.18,
                'diversity_score': 65.8
            },
            {
                'name': 'White & Case LLP',
                'industry_category': 'Global Elite',
                'practice_area': 'M&A',
                'firm_size_category': 'Large',
                'employee_count': 2200,
                'country': 'United States',
                'state_province': 'New York',
                'city': 'New York',
                'risk_profile': 0.22,
                'diversity_score': 71.4
            },
            {
                'name': 'Skadden, Arps, Slate, Meagher & Flom LLP',
                'industry_category': 'AmLaw 50',
                'practice_area': 'Securities Law',
                'firm_size_category': 'Large',
                'employee_count': 1700,
                'country': 'United States',
                'state_province': 'New York',
                'city': 'New York',
                'risk_profile': 0.14,
                'diversity_score': 58.9
            },
            {
                'name': 'Regional Legal Associates',
                'industry_category': 'Regional',
                'practice_area': 'Employment Law',
                'firm_size_category': 'Medium',
                'employee_count': 150,
                'country': 'United States',
                'state_province': 'Texas',
                'city': 'Austin',
                'risk_profile': 0.35,
                'diversity_score': 45.2
            }
        ]
        
        vendors = []
        for firm_data in law_firms:
            vendor = Vendor(**firm_data)
            session.add(vendor)
            vendors.append(vendor)
        
        session.flush()  # Get IDs
        
        # Create legal matters
        matters = [
            {
                'name': 'TechCorp Acquisition',
                'category': 'M&A',
                'status': 'active',
                'budget': 250000.0,
                'start_date': datetime.now() - timedelta(days=120)
            },
            {
                'name': 'Patent Infringement Defense',
                'category': 'IP Litigation',
                'status': 'active',
                'budget': 180000.0,
                'start_date': datetime.now() - timedelta(days=90)
            },
            {
                'name': 'Employment Compliance Audit',
                'category': 'Employment Law',
                'status': 'completed',
                'budget': 75000.0,
                'start_date': datetime.now() - timedelta(days=60),
                'end_date': datetime.now() - timedelta(days=10)
            },
            {
                'name': 'SEC Investigation Response',
                'category': 'Securities Law',
                'status': 'active',
                'budget': 320000.0,
                'start_date': datetime.now() - timedelta(days=45)
            },
            {
                'name': 'Contract Dispute Resolution',
                'category': 'Commercial Litigation',
                'status': 'active',
                'budget': 95000.0,
                'start_date': datetime.now() - timedelta(days=30)
            }
        ]
        
        matter_objects = []
        for matter_data in matters:
            matter = Matter(**matter_data)
            session.add(matter)
            matter_objects.append(matter)
        
        session.flush()  # Get IDs
        
        # Create realistic invoices
        practice_areas = ['Corporate Law', 'Litigation', 'IP Law', 'Employment Law', 'Securities Law', 'M&A']
        attorneys = [
            'Sarah Johnson, Partner', 'Michael Chen, Senior Associate', 'Jennifer Davis, Partner',
            'Robert Wilson, Associate', 'Lisa Martinez, Senior Partner', 'David Brown, Of Counsel',
            'Amanda Taylor, Associate', 'James Anderson, Partner', 'Maria Garcia, Senior Associate'
        ]
        
        invoice_statuses = ['approved', 'pending', 'review', 'flagged']
        
        # Generate invoices over the last 6 months
        invoice_id = 1
        for i in range(150):  # Create 150 invoices
            vendor = random.choice(vendors)
            matter = random.choice(matter_objects)
            
            # Generate realistic invoice data
            base_rate = random.uniform(400, 1200)  # Hourly rates
            hours = random.uniform(5, 80)  # Hours worked
            amount = base_rate * hours
            
            # Add some variability for realism
            amount *= random.uniform(0.9, 1.1)
            
            # Create invoice date within last 6 months
            days_ago = random.randint(1, 180)
            invoice_date = datetime.now() - timedelta(days=days_ago)
            
            # Calculate risk score based on various factors
            risk_score = 0.0
            
            # Higher amounts are riskier
            if amount > 50000:
                risk_score += 0.3
            elif amount > 25000:
                risk_score += 0.15
            
            # Higher rates are riskier
            if base_rate > 900:
                risk_score += 0.2
            elif base_rate > 700:
                risk_score += 0.1
            
            # Vendor risk profile
            risk_score += vendor.risk_profile
            
            # Add some randomness
            risk_score += random.uniform(-0.1, 0.1)
            risk_score = max(0.0, min(1.0, risk_score))
            
            invoice = Invoice(
                invoice_number=f'INV-2024-{invoice_id:04d}',
                vendor_id=vendor.id,
                matter_id=matter.id,
                amount=round(amount, 2),
                date=invoice_date,
                status=random.choice(invoice_statuses),
                description=f'Legal services for {matter.name}',
                practice_area=random.choice(practice_areas),
                attorney_name=random.choice(attorneys),
                total_hours=round(hours, 2),
                rate=round(base_rate, 2),
                risk_score=round(risk_score, 3),
                processed=random.choice([True, False])
            )
            
            session.add(invoice)
            invoice_id += 1
        
        # Create an admin user
        admin_user = User(
            email='admin@lait.demo',
            first_name='Admin',
            last_name='User',
            password_hash='pbkdf2:sha256:260000$...',  # In real app, properly hash password
            role='admin'
        )
        session.add(admin_user)
        
        # Commit all data
        session.commit()
        
        logger.info(f"Successfully seeded database with:")
        logger.info(f"  - {len(vendors)} law firms")
        logger.info(f"  - {len(matter_objects)} legal matters")
        logger.info(f"  - 150 invoices")
        logger.info(f"  - 1 admin user")
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == '__main__':
    seed_database()
