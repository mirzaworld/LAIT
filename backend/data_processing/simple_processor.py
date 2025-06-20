"""
Simple Company Data Processor - Process a sample of the dataset first
"""

import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_sample_legal_companies():
    """Process a sample of legal companies from the dataset"""
    logger.info("Processing sample of legal companies")
    
    # Read just the first 100,000 rows to test
    try:
        df = pd.read_csv(
            '/Users/mirza/Documents/GitHub/LAIT/free_company_dataset.csv',
            nrows=100000,
            on_bad_lines='skip',
            dtype=str
        )
        
        logger.info(f"Loaded {len(df)} records")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Filter for legal companies
        legal_keywords = [
            'law practice', 'legal services', 'attorney', 'lawyer',
            'litigation', 'counsel', 'legal consulting'
        ]
        
        # Create mask for legal companies
        mask = pd.Series([False] * len(df), index=df.index)
        
        # Check industry column
        if 'industry' in df.columns:
            industry_mask = df['industry'].fillna('').str.contains(
                '|'.join(legal_keywords), 
                case=False, 
                na=False
            )
            mask |= industry_mask
        
        # Check company name for legal indicators
        if 'name' in df.columns:
            name_keywords = ['law', 'legal', 'attorney', 'counsel', 'esq']
            name_mask = df['name'].fillna('').str.contains(
                '|'.join(name_keywords), 
                case=False, 
                na=False
            )
            mask |= name_mask
        
        legal_companies = df[mask].copy()
        logger.info(f"Found {len(legal_companies)} legal companies")
        
        if len(legal_companies) > 0:
            # Show sample
            print("\n=== Sample Legal Companies ===")
            print(legal_companies[['name', 'industry', 'country', 'size']].head(10))
            
            # Show industry distribution
            print("\n=== Industry Distribution ===")
            print(legal_companies['industry'].value_counts().head(10))
            
            # Show country distribution
            print("\n=== Country Distribution ===")
            print(legal_companies['country'].value_counts().head(10))
            
            # Export sample
            output_path = '/Users/mirza/Documents/GitHub/LAIT/backend/data_processing/legal_companies_sample.csv'
            legal_companies.to_csv(output_path, index=False)
            logger.info(f"Exported sample to {output_path}")
        
        return legal_companies
        
    except Exception as e:
        logger.error(f"Error processing sample: {str(e)}")
        raise

if __name__ == "__main__":
    process_sample_legal_companies()
