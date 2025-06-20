#!/usr/bin/env python3
"""
Enhanced ML Training Script for LAIT using Real-World Legal Data
This script integrates the collected real-world legal billing data to train production-ready models
"""

import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, mean_squared_error, silhouette_score
import joblib
import logging

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealWorldLegalDataProcessor:
    """Process real-world legal billing data for ML training"""
    
    def __init__(self, data_dir='data/real_world'):
        self.data_dir = data_dir
        self.rate_cards_df = None
        self.court_fees_df = None
        self.sample_invoices = []
        
    def load_real_world_data(self):
        """Load all real-world datasets"""
        logger.info("Loading real-world legal billing data...")
        
        # Load rate cards
        rate_cards_path = os.path.join(self.data_dir, 'rate_cards.csv')
        if os.path.exists(rate_cards_path):
            self.rate_cards_df = pd.read_csv(rate_cards_path)
            logger.info(f"Loaded {len(self.rate_cards_df)} rate card entries")
        
        # Load court fees
        court_fees_path = os.path.join(self.data_dir, 'court_fees_us_uk.csv')
        if os.path.exists(court_fees_path):
            self.court_fees_df = pd.read_csv(court_fees_path)
            logger.info(f"Loaded {len(self.court_fees_df)} court fee entries")
        
        # Load sample invoice
        sample_invoice_path = os.path.join(self.data_dir, 'sample_invoice.json')
        if os.path.exists(sample_invoice_path):
            with open(sample_invoice_path, 'r') as f:
                self.sample_invoices.append(json.load(f))
            logger.info("Loaded sample invoice data")
    
    def normalize_currencies(self, df, rate_col='rate_value', currency_col='rate_currency'):
        """Convert all rates to USD using approximate exchange rates"""
        exchange_rates = {
            'USD': 1.0,
            'GBP': 1.27,  # 1 GBP = 1.27 USD (approximate)
            'EUR': 1.09,  # 1 EUR = 1.09 USD (approximate)
            'CAD': 0.74,  # 1 CAD = 0.74 USD (approximate)
            'AUD': 0.67,  # 1 AUD = 0.67 USD (approximate)
            'PKR': 0.0036  # 1 PKR = 0.0036 USD (approximate)
        }
        
        df = df.copy()
        df['rate_usd'] = df.apply(
            lambda row: row[rate_col] * exchange_rates.get(row[currency_col], 1.0),
            axis=1
        )
        return df
    
    def generate_enhanced_synthetic_data(self, n_samples=1000):
        """Generate synthetic data enhanced with real-world patterns"""
        logger.info(f"Generating {n_samples} enhanced synthetic invoice line items...")
        
        # Use real rate data to inform synthetic generation
        if self.rate_cards_df is not None:
            real_rates = self.normalize_currencies(self.rate_cards_df)
            
            # Get rate distributions by role
            partner_rates = real_rates[real_rates['role'].str.contains('Partner', case=False, na=False)]['rate_usd']
            associate_rates = real_rates[real_rates['role'].str.contains('Associate', case=False, na=False)]['rate_usd']
            attorney_rates = real_rates[real_rates['role'].str.contains('Attorney', case=False, na=False)]['rate_usd']
            
            # Calculate realistic rate ranges
            partner_mean, partner_std = partner_rates.mean(), partner_rates.std()
            associate_mean, associate_std = associate_rates.mean(), associate_rates.std()
            attorney_mean, attorney_std = attorney_rates.mean(), attorney_rates.std()
            
            logger.info(f"Real-world rate analysis:")
            logger.info(f"  Partners: ${partner_mean:.0f} ± ${partner_std:.0f}")
            logger.info(f"  Associates: ${associate_mean:.0f} ± ${associate_std:.0f}")
            logger.info(f"  Attorneys: ${attorney_mean:.0f} ± ${attorney_std:.0f}")
        else:
            # Fallback to estimated ranges
            partner_mean, partner_std = 800, 400
            associate_mean, associate_std = 400, 200
            attorney_mean, attorney_std = 350, 150
        
        synthetic_data = []
        
        for i in range(n_samples):
            # Randomly assign role based on typical firm composition
            role_choice = np.random.choice(['Partner', 'Associate', 'Attorney'], 
                                         p=[0.2, 0.5, 0.3])
            
            if role_choice == 'Partner':
                rate = max(200, np.random.normal(partner_mean, partner_std))
            elif role_choice == 'Associate':
                rate = max(150, np.random.normal(associate_mean, associate_std))
            else:
                rate = max(100, np.random.normal(attorney_mean, attorney_std))
            
            # Generate realistic time entries
            hours = np.random.exponential(2.5)  # Most entries are small, some are large
            hours = min(hours, 24)  # Cap at 24 hours per day
            hours = round(hours * 4) / 4  # Round to quarter hours
            
            amount = hours * rate
            
            # Add practice area based on real data
            practice_areas = ['Corporate', 'Litigation', 'IP', 'Employment', 'Real Estate', 
                            'Family Law', 'Criminal', 'Estate Planning']
            practice_area = np.random.choice(practice_areas)
            
            # Add vendor/firm information
            firm_types = ['AmLaw 100', 'Regional', 'Boutique', 'Solo']
            firm_type = np.random.choice(firm_types, p=[0.3, 0.4, 0.2, 0.1])
            
            synthetic_data.append({
                'hours': hours,
                'rate': rate,
                'amount': amount,
                'role': role_choice,
                'practice_area': practice_area,
                'firm_type': firm_type,
                'date': datetime.now() - timedelta(days=np.random.randint(0, 365))
            })
        
        return pd.DataFrame(synthetic_data)

class EnhancedOutlierDetector:
    """Enhanced outlier detection using real-world legal billing patterns"""
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.rate_benchmarks = {}
        
    def fit(self, data, rate_cards_df=None):
        """Train outlier detection model with real-world benchmarks"""
        logger.info("Training enhanced outlier detection model...")
        
        # Create rate benchmarks from real data
        if rate_cards_df is not None:
            self._create_rate_benchmarks(rate_cards_df)
        
        # Prepare features
        features = self._extract_features(data)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(features_scaled)
        
        logger.info("Outlier detection model training completed")
        
    def _create_rate_benchmarks(self, rate_cards_df):
        """Create rate benchmarks from real-world data"""
        normalized_rates = pd.DataFrame()
        normalized_rates['practice_area'] = rate_cards_df['practice_area']
        normalized_rates['role'] = rate_cards_df['role']
        
        # Handle currency conversion with fallback
        currency_map = {
            'USD': 1.0, 'GBP': 1.27, 'EUR': 1.09, 'CAD': 0.74, 'AUD': 0.67, 'PKR': 0.0036
        }
        
        normalized_rates['rate_usd'] = rate_cards_df.apply(
            lambda row: row['rate_value'] * currency_map.get(row.get('rate_currency', 'USD'), 1.0),
            axis=1
        )
        
        # Calculate benchmarks by practice area and role
        for practice_area in normalized_rates['practice_area'].unique():
            if practice_area not in self.rate_benchmarks:
                self.rate_benchmarks[practice_area] = {}
            
            area_data = normalized_rates[normalized_rates['practice_area'] == practice_area]
            for role in area_data['role'].unique():
                role_rates = area_data[area_data['role'] == role]['rate_usd']
                if len(role_rates) > 0:
                    self.rate_benchmarks[practice_area][role] = {
                        'mean': role_rates.mean(),
                        'std': role_rates.std(),
                        'min': role_rates.min(),
                        'max': role_rates.max()
                    }
    
    def _extract_features(self, data):
        """Extract features for outlier detection"""
        features = []
        
        for _, row in data.iterrows():
            feature_vector = [
                row['hours'],
                row['rate'],
                row['amount'],
                row['rate'] / data['rate'].mean(),  # Rate relative to average
                row['hours'] * row['rate'],  # Total cost
            ]
            
            # Add benchmark comparison if available
            practice_area = row.get('practice_area', 'Unknown')
            role = row.get('role', 'Unknown')
            
            if (practice_area in self.rate_benchmarks and 
                role in self.rate_benchmarks[practice_area]):
                benchmark = self.rate_benchmarks[practice_area][role]
                rate_z_score = (row['rate'] - benchmark['mean']) / max(benchmark['std'], 1)
                feature_vector.append(rate_z_score)
            else:
                feature_vector.append(0)
            
            features.append(feature_vector)
        
        # Convert to numpy array and handle NaN values
        features_array = np.array(features)
        
        # Replace any NaN values with 0
        features_array = np.nan_to_num(features_array, nan=0.0, posinf=0.0, neginf=0.0)
        
        return features_array
    
    def predict(self, data):
        """Predict outliers in new data"""
        features = self._extract_features(data)
        features_scaled = self.scaler.transform(features)
        outlier_scores = self.model.decision_function(features_scaled)
        outlier_predictions = self.model.predict(features_scaled)
        
        return outlier_predictions, outlier_scores

class EnhancedSpendPredictor:
    """Enhanced spend prediction using real-world patterns"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def fit(self, data):
        """Train spend prediction model"""
        logger.info("Training enhanced spend prediction model...")
        
        # Create features for spend prediction
        features, targets = self._prepare_spend_data(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, targets, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"Spend prediction model - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        
    def _prepare_spend_data(self, data):
        """Prepare data for spend prediction"""
        # Group by matter/date to create spend patterns
        features = []
        targets = []
        
        # Create rolling windows of spending
        data_sorted = data.sort_values('date')
        
        for i in range(len(data_sorted) - 5):
            window_data = data_sorted.iloc[i:i+5]
            next_spend = data_sorted.iloc[i+5]['amount']
            
            # Calculate features with fallback for NaN
            amount_std = window_data['amount'].std()
            if pd.isna(amount_std):
                amount_std = 0
            
            feature_vector = [
                window_data['amount'].sum(),
                window_data['amount'].mean(),
                amount_std,
                window_data['hours'].sum(),
                window_data['rate'].mean(),
                len(window_data['practice_area'].unique()),
                len(window_data['role'].unique())
            ]
            
            features.append(feature_vector)
            targets.append(next_spend)
        
        # Convert to numpy arrays and handle NaN values
        features_array = np.array(features)
        targets_array = np.array(targets)
        
        # Replace any NaN values
        features_array = np.nan_to_num(features_array, nan=0.0, posinf=0.0, neginf=0.0)
        targets_array = np.nan_to_num(targets_array, nan=0.0, posinf=0.0, neginf=0.0)
        
        return features_array, targets_array

def main():
    """Main training function"""
    logger.info("🤖 Starting Enhanced LAIT ML Training with Real-World Data")
    logger.info("="*60)
    
    # Initialize data processor
    processor = RealWorldLegalDataProcessor()
    
    # Load real-world data
    processor.load_real_world_data()
    
    # Generate enhanced synthetic data
    synthetic_data = processor.generate_enhanced_synthetic_data(2000)
    
    # Train enhanced outlier detection
    outlier_detector = EnhancedOutlierDetector()
    outlier_detector.fit(synthetic_data, processor.rate_cards_df)
    
    # Test outlier detection
    outlier_predictions, outlier_scores = outlier_detector.predict(synthetic_data)
    n_outliers = (outlier_predictions == -1).sum()
    logger.info(f"Detected {n_outliers} outliers in {len(synthetic_data)} records ({100*n_outliers/len(synthetic_data):.1f}%)")
    
    # Train spend prediction
    spend_predictor = EnhancedSpendPredictor()
    spend_predictor.fit(synthetic_data)
    
    # Save models
    models_dir = 'backend/ml/models'
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(outlier_detector.model, f'{models_dir}/enhanced_outlier_model.joblib')
    joblib.dump(outlier_detector.scaler, f'{models_dir}/enhanced_outlier_scaler.joblib')
    joblib.dump(spend_predictor.model, f'{models_dir}/enhanced_spend_model.joblib')
    joblib.dump(spend_predictor.scaler, f'{models_dir}/enhanced_spend_scaler.joblib')
    
    # Save rate benchmarks
    with open(f'{models_dir}/rate_benchmarks.json', 'w') as f:
        json.dump(outlier_detector.rate_benchmarks, f, indent=2, default=str)
    
    logger.info("🎉 Enhanced ML training completed successfully!")
    logger.info(f"Models saved to {models_dir}/")
    
    # Display real-world insights
    if processor.rate_cards_df is not None:
        logger.info("\n📊 Real-World Rate Analysis:")
        rate_df = processor.normalize_currencies(processor.rate_cards_df)
        
        # Top rates by role
        for role in ['Partner', 'Associate', 'Attorney']:
            role_data = rate_df[rate_df['role'].str.contains(role, case=False, na=False)]
            if len(role_data) > 0:
                avg_rate = role_data['rate_usd'].mean()
                max_rate = role_data['rate_usd'].max()
                min_rate = role_data['rate_usd'].min()
                logger.info(f"  {role}: ${min_rate:.0f} - ${max_rate:.0f} (avg: ${avg_rate:.0f})")
        
        # Top firms
        logger.info("\n🏢 Rate Analysis by Source:")
        source_analysis = rate_df.groupby('source_type')['rate_usd'].agg(['mean', 'count'])
        for source_type, stats in source_analysis.iterrows():
            logger.info(f"  {source_type}: ${stats['mean']:.0f} avg ({stats['count']} entries)")

if __name__ == "__main__":
    main()
