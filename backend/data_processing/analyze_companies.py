#!/usr/bin/env python3
"""
Simple CSV Data Processor for Legal Companies
Processes the legal company data and shows import statistics
"""

import pandas as pd
import os

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

def analyze_legal_companies():
    """Analyze the legal company data"""
    
    # Load the CSV file
    csv_file = 'legal_companies_sample.csv'
    if not os.path.exists(csv_file):
        print(f"❌ CSV file {csv_file} not found")
        return
    
    print(f"📊 Loading legal company data from {csv_file}")
    df = pd.read_csv(csv_file)
    
    print(f"✅ Loaded {len(df)} companies")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Basic statistics
    print("\n🌍 Geographic Distribution:")
    country_counts = df['country'].value_counts()
    for country, count in country_counts.head(10).items():
        print(f"  {country}: {count} companies")
    
    print(f"\n🏢 Company Size Distribution:")
    size_counts = df['size'].value_counts()
    for size, count in size_counts.items():
        if pd.notna(size):
            print(f"  {size}: {count} companies")
    
    # Categorize practice areas
    print("\n⚖️  Categorizing Practice Areas...")
    df['practice_area'] = df.apply(lambda row: categorize_practice_area(row['industry'], row['name']), axis=1)
    
    practice_area_counts = df['practice_area'].value_counts()
    print("\n📚 Practice Area Distribution:")
    for area, count in practice_area_counts.items():
        print(f"  {area}: {count} companies")
    
    # Companies with websites
    websites = df['website'].notna().sum()
    print(f"\n🌐 Companies with websites: {websites}/{len(df)} ({websites/len(df)*100:.1f}%)")
    
    # Companies with LinkedIn
    linkedin = df['linkedin_url'].notna().sum()
    print(f"📱 Companies with LinkedIn: {linkedin}/{len(df)} ({linkedin/len(df)*100:.1f}%)")
    
    # US-based law firms
    us_law_firms = df[(df['country'] == 'united states') & (df['industry'].str.contains('law', na=False, case=False))]
    print(f"\n🇺🇸 US-based law firms: {len(us_law_firms)}")
    
    # Show sample of processed data
    print("\n📋 Sample processed companies:")
    sample_columns = ['name', 'country', 'region', 'practice_area', 'size']
    print(df[sample_columns].head().to_string(index=False))
    
    print("\n✅ Legal company data analysis complete!")
    print(f"🎯 Ready for import: {len(df)} companies categorized and processed")

if __name__ == "__main__":
    analyze_legal_companies()
