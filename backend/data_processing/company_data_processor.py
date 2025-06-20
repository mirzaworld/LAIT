"""
Company Data Processor for LAIT Legal Spend Optimizer

This script processes the free_company_dataset.csv to extract legal service providers
and integrate them into the LAIT system for enhanced vendor management and analytics.
"""

import pandas as pd
import numpy as np
import re
from typing import List, Dict, Optional
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyDataProcessor:
    """Process company dataset for legal service providers"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.legal_keywords = [
            'law practice', 'legal services', 'law firm', 'attorney', 'lawyer',
            'litigation', 'counsel', 'legal consulting', 'paralegal', 'legal advice',
            'intellectual property law', 'corporate law', 'employment law',
            'real estate law', 'tax law', 'criminal law', 'family law'
        ]
        
    def load_and_filter_legal_companies(self) -> pd.DataFrame:
        """Load CSV and filter for legal service companies"""
        logger.info(f"Loading company data from {self.csv_path}")
        
        # Read in chunks due to large file size
        chunk_size = 50000
        legal_companies = []
        
        try:
            for chunk_num, chunk in enumerate(pd.read_csv(
                self.csv_path, 
                chunksize=chunk_size,
                low_memory=False,
                on_bad_lines='skip',  # Skip problematic lines
                dtype=str  # Read all as string to avoid type issues
            )):
                logger.info(f"Processing chunk {chunk_num + 1}")
                
                # Filter for legal companies
                legal_chunk = self._filter_legal_companies(chunk)
                if not legal_chunk.empty:
                    legal_companies.append(legal_chunk)
                    
                # Log progress every 100 chunks
                if (chunk_num + 1) % 100 == 0:
                    logger.info(f"Processed {(chunk_num + 1) * chunk_size} records")
            
            if legal_companies:
                result_df = pd.concat(legal_companies, ignore_index=True)
                logger.info(f"Found {len(result_df)} legal service companies")
                return result_df
            else:
                logger.warning("No legal companies found")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise
    
    def _filter_legal_companies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter dataframe for legal service companies"""
        # Reset index to avoid alignment issues
        df = df.reset_index(drop=True)
        
        # Create mask for legal companies
        mask = pd.Series([False] * len(df), index=df.index)
        
        # Check industry column
        if 'industry' in df.columns:
            industry_mask = df['industry'].fillna('').str.contains(
                '|'.join(self.legal_keywords), 
                case=False, 
                na=False
            )
            mask |= industry_mask
        
        # Check company name for additional legal indicators
        if 'name' in df.columns:
            name_keywords = ['law', 'legal', 'attorney', 'counsel', 'esq']
            name_mask = df['name'].fillna('').str.contains(
                '|'.join(name_keywords), 
                case=False, 
                na=False
            )
            mask |= name_mask
            
        return df[mask].copy()
    
    def clean_and_standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the legal companies data"""
        logger.info("Cleaning and standardizing data")
        
        # Create a copy to avoid warnings
        df = df.copy()
        
        # Standardize company names
        df['name'] = df['name'].str.title().str.strip()
        
        # Clean and standardize locations
        df['country'] = df['country'].str.title().str.strip()
        df['region'] = df['region'].str.title().str.strip()
        df['locality'] = df['locality'].str.title().str.strip()
        
        # Standardize company sizes
        df['size'] = df['size'].fillna('Unknown')
        
        # Clean websites (remove invalid URLs)
        df['website'] = df['website'].apply(self._clean_website)
        
        # Convert founded year to integer
        df['founded'] = pd.to_numeric(df['founded'], errors='coerce')
        
        # Create standardized industry categories
        df['primary_practice_area'] = df['industry'].apply(self._categorize_practice_area)
        
        # Add estimated company tier based on size and other factors
        df['company_tier'] = df.apply(self._estimate_company_tier, axis=1)
        
        # Remove duplicates based on name and location
        df = df.drop_duplicates(subset=['name', 'locality', 'region'], keep='first')
        
        logger.info(f"Cleaned data: {len(df)} unique legal companies")
        return df
    
    def _clean_website(self, website: str) -> Optional[str]:
        """Clean and validate website URLs"""
        if pd.isna(website) or website == '':
            return None
            
        website = str(website).strip().lower()
        
        # Add protocol if missing
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
            
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
        if url_pattern.match(website):
            return website
        return None
    
    def _categorize_practice_area(self, industry: str) -> str:
        """Categorize companies into primary practice areas"""
        if pd.isna(industry):
            return 'General Practice'
            
        industry_lower = str(industry).lower()
        
        if 'corporate' in industry_lower or 'business' in industry_lower:
            return 'Corporate Law'
        elif 'intellectual property' in industry_lower or 'ip' in industry_lower:
            return 'Intellectual Property'
        elif 'employment' in industry_lower or 'labor' in industry_lower:
            return 'Employment Law'
        elif 'real estate' in industry_lower or 'property' in industry_lower:
            return 'Real Estate Law'
        elif 'litigation' in industry_lower or 'trial' in industry_lower:
            return 'Litigation'
        elif 'tax' in industry_lower:
            return 'Tax Law'
        elif 'criminal' in industry_lower:
            return 'Criminal Law'
        elif 'family' in industry_lower:
            return 'Family Law'
        elif 'immigration' in industry_lower:
            return 'Immigration Law'
        else:
            return 'General Practice'
    
    def _estimate_company_tier(self, row) -> str:
        """Estimate company tier based on available information"""
        size = str(row.get('size', '')).lower()
        founded = row.get('founded')
        
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
            if founded and founded < 1980:
                return 'Established Law Firm'
            else:
                return 'Law Firm'
    
    def generate_sample_data(self, df: pd.DataFrame, sample_size: int = 1000) -> pd.DataFrame:
        """Generate a sample of the data for testing"""
        if len(df) <= sample_size:
            return df
            
        # Stratified sampling to get diverse representation
        sample_dfs = []
        
        # Sample by company tier
        for tier in df['company_tier'].unique():
            tier_df = df[df['company_tier'] == tier]
            tier_sample_size = min(len(tier_df), max(1, sample_size // len(df['company_tier'].unique())))
            sample_dfs.append(tier_df.sample(n=tier_sample_size, random_state=42))
        
        result = pd.concat(sample_dfs, ignore_index=True)
        logger.info(f"Generated sample of {len(result)} companies")
        return result
    
    def export_for_database(self, df: pd.DataFrame, output_path: str):
        """Export processed data in format suitable for database import"""
        # Select and rename columns for database schema
        db_columns = {
            'id': 'external_id',
            'name': 'name',
            'industry': 'industry_category',
            'primary_practice_area': 'practice_area',
            'company_tier': 'firm_size_category',
            'size': 'employee_count',
            'founded': 'founded_year',
            'country': 'country',
            'region': 'state_province',
            'locality': 'city',
            'website': 'website',
            'linkedin_url': 'linkedin_url'
        }
        
        export_df = df[list(db_columns.keys())].rename(columns=db_columns)
        
        # Add additional fields for LAIT system
        export_df['vendor_type'] = 'Legal Service Provider'
        export_df['status'] = 'Prospect'
        export_df['created_at'] = pd.Timestamp.now()
        export_df['data_source'] = 'Company Dataset'
        
        # Export to CSV
        export_df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(export_df)} records to {output_path}")
        
        return export_df

def main():
    """Main processing function"""
    # Initialize processor
    processor = CompanyDataProcessor('/Users/mirza/Documents/GitHub/LAIT/free_company_dataset.csv')
    
    # Process the data
    legal_companies = processor.load_and_filter_legal_companies()
    
    if not legal_companies.empty:
        # Clean and standardize
        cleaned_data = processor.clean_and_standardize(legal_companies)
        
        # Generate sample for testing
        sample_data = processor.generate_sample_data(cleaned_data, 5000)
        
        # Export sample for database import
        output_dir = Path('/Users/mirza/Documents/GitHub/LAIT/backend/data_processing/output')
        output_dir.mkdir(exist_ok=True)
        
        sample_output = output_dir / 'legal_companies_sample.csv'
        full_output = output_dir / 'legal_companies_full.csv'
        
        processor.export_for_database(sample_data, sample_output)
        processor.export_for_database(cleaned_data, full_output)
        
        # Print summary statistics
        print("\n=== Processing Summary ===")
        print(f"Total legal companies found: {len(cleaned_data)}")
        print(f"Sample size for testing: {len(sample_data)}")
        print(f"\nPractice area distribution:")
        print(cleaned_data['primary_practice_area'].value_counts())
        print(f"\nCompany tier distribution:")
        print(cleaned_data['company_tier'].value_counts())
        print(f"\nCountry distribution (top 10):")
        print(cleaned_data['country'].value_counts().head(10))
    else:
        logger.error("No legal companies found in dataset")

if __name__ == "__main__":
    main()
