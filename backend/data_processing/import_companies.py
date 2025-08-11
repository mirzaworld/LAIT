"""
Database Import Script for Legal Company Data
Imports the processed legal companies into the LAIT vendor management system
"""

import pandas as pd
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add backend to path for imports
sys.path.append('/app/backend')
sys.path.append('/app')

from models.db_models import Base, Vendor
from db.database import get_db_session

def categorize_practice_area(industry: str, name: str = '') -> str:
    """Categorize companies into primary practice areas"""
    if pd.isna(industry):
        industry = ''
    if pd.isna(name):
        name = ''
        
    industry_lower = str(industry).lower()
    name_lower = str(name).lower()
    
    combined = f"{industry_lower} {name_lower}"
    
    if any(keyword in combined for keyword in ['corporate', 'business', 'commercial']):
        return 'Corporate Law'
    elif any(keyword in combined for keyword in ['intellectual property', 'ip', 'patent', 'trademark']):
        return 'Intellectual Property'
    elif any(keyword in combined for keyword in ['employment', 'labor']):
        return 'Employment Law'
    elif any(keyword in combined for keyword in ['real estate', 'property']):
        return 'Real Estate Law'
    elif any(keyword in combined for keyword in ['litigation', 'trial', 'dispute']):
        return 'Litigation'
    elif any(keyword in combined for keyword in ['tax']):
        return 'Tax Law'
    elif any(keyword in combined for keyword in ['criminal']):
        return 'Criminal Law'
    elif any(keyword in combined for keyword in ['family', 'divorce']):
        return 'Family Law'
    elif any(keyword in combined for keyword in ['immigration']):
        return 'Immigration Law'
    elif any(keyword in combined for keyword in ['personal injury', 'accident']):
        return 'Personal Injury'
    else:
        return 'General Practice'

def estimate_company_tier(size: str, founded: str = None) -> str:
    """Estimate company tier based on available information"""
    if pd.isna(size):
        size = ''
    
    size = str(size).lower()
    
    # Large firms
    if any(indicator in size for indicator in ['500+', '1000+', '5000+', '10000+']):
        return 'Large Law Firm'
    elif any(indicator in size for indicator in ['201-500', '501-1000']):
        return 'Mid-Size Law Firm'
    # Small/medium firms
    elif any(indicator in size for indicator in ['51-200', '11-50']):
        return 'Small to Medium Law Firm'
    # Solo practitioners and very small firms
    elif '1-10' in size:
        return 'Small Law Firm'
    else:
        # Use founding year as additional indicator
        try:
            founded_year = int(founded) if founded and not pd.isna(founded) else None
            if founded_year and founded_year < 1980:
                return 'Established Law Firm'
        except:
            pass
        return 'Law Firm'

def clean_website(website: str) -> str:
    """Clean and validate website URLs"""
    if pd.isna(website) or website == '':
        return None
        
    website = str(website).strip().lower()
    
    # Add protocol if missing
    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website
        
    return website

def import_legal_companies():
    """Import legal companies from CSV into database"""
    print("Starting import of legal companies...")
    
    # Read the sample data
    csv_path = '/app/backend/data_processing/legal_companies_sample.csv'
    df = pd.read_csv(csv_path)
    
    print(f"Loaded {len(df)} companies from CSV")
    
    # Get database session
    session = get_db_session()
    
    try:
        imported_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                # Check if vendor already exists (by external_id or name)
                existing = session.query(Vendor).filter(
                    (Vendor.external_id == row['id']) | 
                    (Vendor.name == row['name'])
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Clean and process data
                website = clean_website(row.get('website'))
                practice_area = categorize_practice_area(row.get('industry'), row.get('name'))
                company_tier = estimate_company_tier(row.get('size'), row.get('founded'))
                
                # Create vendor record
                vendor = Vendor(
                    external_id=row['id'],
                    name=str(row['name']).title() if not pd.isna(row['name']) else 'Unknown',
                    vendor_type='Legal Service Provider',
                    industry_category=row.get('industry'),
                    practice_area=practice_area,
                    firm_size_category=company_tier,
                    employee_count=row.get('size'),
                    founded_year=int(row['founded']) if row.get('founded') and not pd.isna(row['founded']) else None,
                    country=str(row['country']).title() if not pd.isna(row['country']) else None,
                    state_province=str(row['region']).title() if not pd.isna(row['region']) else None,
                    city=str(row['locality']).title() if not pd.isna(row['locality']) else None,
                    website=website,
                    linkedin_url=row.get('linkedin_url') if not pd.isna(row.get('linkedin_url')) else None,
                    status='Prospect',
                    data_source='Company Dataset',
                    created_at=datetime.now(timezone.utc)
                )
                
                session.add(vendor)
                imported_count += 1
                
                # Commit every 100 records
                if imported_count % 100 == 0:
                    session.commit()
                    print(f"Imported {imported_count} companies...")
                    
            except Exception as e:
                print(f"Error importing row {index}: {str(e)}")
                continue
        
        # Final commit
        session.commit()
        
        print(f"\nImport completed!")
        print(f"Imported: {imported_count} companies")
        print(f"Skipped (duplicates): {skipped_count} companies")
        
        # Show some statistics
        print("\n=== Import Statistics ===")
        
        # Practice area distribution
        practice_areas = session.query(Vendor.practice_area, 
                                     session.query(Vendor).filter(Vendor.practice_area == Vendor.practice_area).count().label('count'))\
                               .filter(Vendor.data_source == 'Company Dataset')\
                               .group_by(Vendor.practice_area)\
                               .all()
        
        print("\nPractice Areas:")
        for area in practice_areas[:10]:
            count = session.query(Vendor).filter(Vendor.practice_area == area[0]).count()
            print(f"  {area[0]}: {count}")
        
        # Country distribution
        print("\nTop Countries:")
        countries = session.query(Vendor.country)\
                          .filter(Vendor.data_source == 'Company Dataset')\
                          .filter(Vendor.country.isnot(None))\
                          .all()
        
        country_counts = {}
        for country in countries:
            country_counts[country[0]] = country_counts.get(country[0], 0) + 1
        
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {country}: {count}")
        
    except Exception as e:
        session.rollback()
        print(f"Error during import: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import_legal_companies()
