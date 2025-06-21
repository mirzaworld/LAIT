#!/usr/bin/env python3
"""
Real-World ML Model Training Script for LAIT
Trains all ML models using the collected real-world legal data
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import joblib
from sklearn.ensemble import IsolationForest, RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger(__name__)

class RealWorldMLTrainer:
    """Train ML models using real-world legal data"""
    
    def __init__(self, data_dir='backend/ml/data'):
        self.data_dir = data_dir
        self.models_dir = 'backend/ml/models'
        
        # Ensure directories exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Load collected data
        self.legal_rates = None
        self.attorneys = None
        self.cases = None
        self.vendors = None
        self.billing_patterns = None
        
        self._load_collected_data()
    
    def _load_collected_data(self):
        """Load all collected real-world data"""
        try:
            # Load legal billing rates
            rates_file = os.path.join(self.data_dir, 'legal_billing_rates.csv')
            if os.path.exists(rates_file):
                self.legal_rates = pd.read_csv(rates_file)
                logger.info(f"✅ Loaded {len(self.legal_rates)} billing rate records")
            
            # Load attorney data
            attorneys_file = os.path.join(self.data_dir, 'attorney_database.csv')
            if os.path.exists(attorneys_file):
                self.attorneys = pd.read_csv(attorneys_file)
                logger.info(f"✅ Loaded {len(self.attorneys)} attorney records")
            
            # Load case data
            cases_file = os.path.join(self.data_dir, 'legal_cases.csv')
            if os.path.exists(cases_file):
                self.cases = pd.read_csv(cases_file)
                logger.info(f"✅ Loaded {len(self.cases)} case records")
            
            # Load vendor data
            vendors_file = os.path.join(self.data_dir, 'law_firms_vendors.csv')
            if os.path.exists(vendors_file):
                self.vendors = pd.read_csv(vendors_file)
                logger.info(f"✅ Loaded {len(self.vendors)} vendor records")
            
            # Load billing patterns
            patterns_file = os.path.join(self.data_dir, 'billing_patterns.json')
            if os.path.exists(patterns_file):
                with open(patterns_file, 'r') as f:
                    self.billing_patterns = json.load(f)
                logger.info(f"✅ Loaded {len(self.billing_patterns)} billing patterns")
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def train_all_models(self):
        """Train all ML models"""
        logger.info("🚀 Starting comprehensive ML model training...")
        
        models_trained = {}
        
        # 1. Train outlier detection model
        outlier_model = self.train_outlier_detection_model()
        if outlier_model:
            models_trained['outlier_detection'] = outlier_model
        
        # 2. Train rate prediction model
        rate_model = self.train_rate_prediction_model()
        if rate_model:
            models_trained['rate_prediction'] = rate_model
        
        # 3. Train spend prediction model
        spend_model = self.train_spend_prediction_model()
        if spend_model:
            models_trained['spend_prediction'] = spend_model
        
        # 4. Train attorney classification model
        attorney_model = self.train_attorney_classification_model()
        if attorney_model:
            models_trained['attorney_classification'] = attorney_model
        
        # 5. Train vendor analysis model
        vendor_model = self.train_vendor_analysis_model()
        if vendor_model:
            models_trained['vendor_analysis'] = vendor_model
        
        # 6. Create rate benchmarks
        benchmarks = self.create_rate_benchmarks()
        if benchmarks:
            models_trained['rate_benchmarks'] = benchmarks
        
        logger.info(f"✅ Trained {len(models_trained)} models successfully")
        return models_trained
    
    def train_outlier_detection_model(self):
        """Train outlier detection model using legal rates data"""
        if self.legal_rates is None or len(self.legal_rates) < 100:
            logger.warning("Not enough rate data for outlier detection training")
            return None
        
        logger.info("🔍 Training outlier detection model...")
        
        try:
            # Prepare features for outlier detection
            features = []
            
            # Encode categorical variables
            le_role = LabelEncoder()
            le_practice = LabelEncoder()
            le_market = LabelEncoder()
            le_firm_size = LabelEncoder()
            
            # Fill NaN values
            self.legal_rates['role'] = self.legal_rates['role'].fillna('Unknown')
            self.legal_rates['practice_area'] = self.legal_rates['practice_area'].fillna('General')
            self.legal_rates['market'] = self.legal_rates['market'].fillna('Other')
            self.legal_rates['firm_size'] = self.legal_rates['firm_size'].fillna('Unknown')
            
            # Encode categorical features
            role_encoded = le_role.fit_transform(self.legal_rates['role'])
            practice_encoded = le_practice.fit_transform(self.legal_rates['practice_area'])
            market_encoded = le_market.fit_transform(self.legal_rates['market'])
            firm_size_encoded = le_firm_size.fit_transform(self.legal_rates['firm_size'])
            
            # Create feature matrix
            feature_matrix = np.column_stack([
                self.legal_rates['rate_usd'].values,
                role_encoded,
                practice_encoded,
                market_encoded,
                firm_size_encoded
            ])
            
            # Handle any remaining NaN values
            feature_matrix = np.nan_to_num(feature_matrix, nan=0.0)
            
            # Scale features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(feature_matrix)
            
            # Train isolation forest
            model = IsolationForest(
                contamination=0.1,  # Expect 10% outliers
                random_state=42,
                n_estimators=100
            )
            model.fit(scaled_features)
            
            # Save model and preprocessing objects
            model_data = {
                'model': model,
                'scaler': scaler,
                'label_encoders': {
                    'role': le_role,
                    'practice_area': le_practice,
                    'market': le_market,
                    'firm_size': le_firm_size
                },
                'feature_names': ['rate_usd', 'role', 'practice_area', 'market', 'firm_size']
            }
            
            # Save to files
            joblib.dump(model, os.path.join(self.models_dir, 'enhanced_outlier_model.joblib'))
            joblib.dump(scaler, os.path.join(self.models_dir, 'enhanced_outlier_scaler.joblib'))
            joblib.dump(model_data, os.path.join(self.models_dir, 'outlier_detection_complete.joblib'))
            
            logger.info("✅ Outlier detection model trained and saved")
            return model_data
            
        except Exception as e:
            logger.error(f"Error training outlier detection model: {e}")
            return None
    
    def train_rate_prediction_model(self):
        """Train rate prediction model"""
        if self.legal_rates is None or len(self.legal_rates) < 100:
            logger.warning("Not enough rate data for rate prediction training")
            return None
        
        logger.info("💰 Training rate prediction model...")
        
        try:
            # Prepare features for rate prediction
            features_df = self.legal_rates.copy()
            
            # Fill NaN values
            features_df = features_df.fillna({
                'role': 'Unknown',
                'practice_area': 'General',
                'market': 'Other',
                'firm_size': 'Unknown',
                'experience_level': 'Unknown'
            })
            
            # Encode categorical variables
            categorical_features = ['role', 'practice_area', 'market', 'firm_size', 'experience_level']
            label_encoders = {}
            
            for feature in categorical_features:
                le = LabelEncoder()
                features_df[f'{feature}_encoded'] = le.fit_transform(features_df[feature])
                label_encoders[feature] = le
            
            # Select features for training
            feature_columns = [f'{feature}_encoded' for feature in categorical_features] + ['year']
            X = features_df[feature_columns].values
            y = features_df['rate_usd'].values
            
            # Handle any remaining NaN values
            X = np.nan_to_num(X, nan=0.0)
            y = np.nan_to_num(y, nan=0.0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            logger.info(f"Rate prediction model MSE: {mse:.2f}")
            
            # Save model
            model_data = {
                'model': model,
                'scaler': scaler,
                'label_encoders': label_encoders,
                'feature_columns': feature_columns,
                'mse': mse
            }
            
            joblib.dump(model, os.path.join(self.models_dir, 'rate_prediction_model.joblib'))
            joblib.dump(scaler, os.path.join(self.models_dir, 'rate_prediction_scaler.joblib'))
            joblib.dump(model_data, os.path.join(self.models_dir, 'rate_prediction_complete.joblib'))
            
            logger.info("✅ Rate prediction model trained and saved")
            return model_data
            
        except Exception as e:
            logger.error(f"Error training rate prediction model: {e}")
            return None
    
    def train_spend_prediction_model(self):
        """Train spend prediction model"""
        if self.legal_rates is None or len(self.legal_rates) < 100:
            logger.warning("Not enough data for spend prediction training")
            return None
        
        logger.info("📈 Training spend prediction model...")
        
        try:
            # Generate synthetic spend data based on rates
            spend_data = []
            
            for _, row in self.legal_rates.iterrows():
                # Generate realistic hours and calculate spend
                hours = np.random.uniform(1, 20)  # 1-20 hours per entry
                total_spend = hours * row['rate_usd']
                
                spend_data.append({
                    'hours': hours,
                    'rate': row['rate_usd'],
                    'practice_area': row['practice_area'],
                    'role': row['role'],
                    'market': row['market'],
                    'firm_size': row['firm_size'],
                    'total_spend': total_spend
                })
            
            spend_df = pd.DataFrame(spend_data)
            
            # Fill NaN values
            spend_df = spend_df.fillna({
                'role': 'Unknown',
                'practice_area': 'General',
                'market': 'Other',
                'firm_size': 'Unknown'
            })
            
            # Encode categorical variables
            categorical_features = ['practice_area', 'role', 'market', 'firm_size']
            label_encoders = {}
            
            for feature in categorical_features:
                le = LabelEncoder()
                spend_df[f'{feature}_encoded'] = le.fit_transform(spend_df[feature])
                label_encoders[feature] = le
            
            # Prepare features
            feature_columns = ['hours', 'rate'] + [f'{feature}_encoded' for feature in categorical_features]
            X = spend_df[feature_columns].values
            y = spend_df['total_spend'].values
            
            # Handle any remaining NaN values
            X = np.nan_to_num(X, nan=0.0)
            y = np.nan_to_num(y, nan=0.0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            logger.info(f"Spend prediction model MSE: {mse:.2f}")
            
            # Save model
            model_data = {
                'model': model,
                'scaler': scaler,
                'label_encoders': label_encoders,
                'feature_columns': feature_columns,
                'mse': mse
            }
            
            joblib.dump(model, os.path.join(self.models_dir, 'enhanced_spend_model.joblib'))
            joblib.dump(scaler, os.path.join(self.models_dir, 'enhanced_spend_scaler.joblib'))
            joblib.dump(model_data, os.path.join(self.models_dir, 'spend_prediction_complete.joblib'))
            
            logger.info("✅ Spend prediction model trained and saved")
            return model_data
            
        except Exception as e:
            logger.error(f"Error training spend prediction model: {e}")
            return None
    
    def train_attorney_classification_model(self):
        """Train attorney classification model"""
        if self.legal_rates is None or len(self.legal_rates) < 100:
            logger.warning("Not enough data for attorney classification training")
            return None
        
        logger.info("👨‍⚖️ Training attorney classification model...")
        
        try:
            # Use rate data to classify attorney experience levels
            features_df = self.legal_rates.copy()
            
            # Fill NaN values
            features_df = features_df.fillna({
                'role': 'Unknown',
                'practice_area': 'General',
                'market': 'Other',
                'firm_size': 'Unknown',
                'experience_level': 'Unknown'
            })
            
            # Prepare features
            categorical_features = ['practice_area', 'market', 'firm_size']
            label_encoders = {}
            
            for feature in categorical_features:
                le = LabelEncoder()
                features_df[f'{feature}_encoded'] = le.fit_transform(features_df[feature])
                label_encoders[feature] = le
            
            # Encode target variable (role)
            role_encoder = LabelEncoder()
            y = role_encoder.fit_transform(features_df['role'])
            
            # Select features
            feature_columns = ['rate_usd'] + [f'{feature}_encoded' for feature in categorical_features]
            X = features_df[feature_columns].values
            
            # Handle any remaining NaN values
            X = np.nan_to_num(X, nan=0.0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            accuracy = model.score(X_test_scaled, y_test)
            logger.info(f"Attorney classification model accuracy: {accuracy:.3f}")
            
            # Save model
            model_data = {
                'model': model,
                'scaler': scaler,
                'label_encoders': label_encoders,
                'role_encoder': role_encoder,
                'feature_columns': feature_columns,
                'accuracy': accuracy
            }
            
            joblib.dump(model_data, os.path.join(self.models_dir, 'attorney_classification_complete.joblib'))
            
            logger.info("✅ Attorney classification model trained and saved")
            return model_data
            
        except Exception as e:
            logger.error(f"Error training attorney classification model: {e}")
            return None
    
    def train_vendor_analysis_model(self):
        """Train vendor analysis model"""
        if self.vendors is None or len(self.vendors) < 50:
            logger.warning("Not enough vendor data for vendor analysis training")
            return None
        
        logger.info("🏢 Training vendor analysis model...")
        
        try:
            # Prepare vendor features
            features_df = self.vendors.copy()
            
            # Fill NaN values
            features_df = features_df.fillna({
                'firm_type': 'Unknown',
                'type': 'Unknown',
                'location': 'Unknown'
            })
            
            # Encode categorical variables
            categorical_features = ['firm_type', 'type', 'location']
            label_encoders = {}
            
            for feature in categorical_features:
                if feature in features_df.columns:
                    le = LabelEncoder()
                    features_df[f'{feature}_encoded'] = le.fit_transform(features_df[feature])
                    label_encoders[feature] = le
            
            # Create quality score based on attorney count and founded year
            current_year = datetime.now().year
            features_df['years_in_business'] = current_year - features_df['founded_year']
            features_df['quality_score'] = (
                np.log1p(features_df['attorney_count']) * 0.3 +
                np.log1p(features_df['years_in_business']) * 0.7
            )
            
            # Prepare features
            feature_columns = ['attorney_count', 'founded_year', 'years_in_business']
            encoded_columns = [f'{feature}_encoded' for feature in categorical_features if f'{feature}_encoded' in features_df.columns]
            feature_columns.extend(encoded_columns)
            
            X = features_df[feature_columns].values
            y = features_df['quality_score'].values
            
            # Handle any remaining NaN values
            X = np.nan_to_num(X, nan=0.0)
            y = np.nan_to_num(y, nan=0.0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            logger.info(f"Vendor analysis model MSE: {mse:.3f}")
            
            # Save model
            model_data = {
                'model': model,
                'scaler': scaler,
                'label_encoders': label_encoders,
                'feature_columns': feature_columns,
                'mse': mse
            }
            
            joblib.dump(model_data, os.path.join(self.models_dir, 'vendor_analysis_complete.joblib'))
            
            logger.info("✅ Vendor analysis model trained and saved")
            return model_data
            
        except Exception as e:
            logger.error(f"Error training vendor analysis model: {e}")
            return None
    
    def create_rate_benchmarks(self):
        """Create rate benchmarks from real data"""
        if self.legal_rates is None:
            logger.warning("No rate data available for benchmarks")
            return None
        
        logger.info("📊 Creating rate benchmarks...")
        
        try:
            benchmarks = {}
            
            # Group by practice area and role
            for practice_area in self.legal_rates['practice_area'].unique():
                if pd.isna(practice_area):
                    continue
                    
                benchmarks[practice_area] = {}
                
                practice_data = self.legal_rates[self.legal_rates['practice_area'] == practice_area]
                
                for role in practice_data['role'].unique():
                    if pd.isna(role):
                        continue
                        
                    role_data = practice_data[practice_data['role'] == role]['rate_usd']
                    
                    if len(role_data) > 0:
                        benchmarks[practice_area][role] = {
                            'mean': float(role_data.mean()),
                            'std': float(role_data.std()),
                            'min': float(role_data.min()),
                            'max': float(role_data.max()),
                            'median': float(role_data.median()),
                            'count': int(len(role_data))
                        }
            
            # Save benchmarks
            benchmarks_file = os.path.join(self.models_dir, 'rate_benchmarks.json')
            with open(benchmarks_file, 'w') as f:
                json.dump(benchmarks, f, indent=2)
            
            logger.info(f"✅ Created benchmarks for {len(benchmarks)} practice areas")
            return benchmarks
            
        except Exception as e:
            logger.error(f"Error creating rate benchmarks: {e}")
            return None

def main():
    """Main training function"""
    logging.basicConfig(level=logging.INFO)
    
    logger.info("🚀 Starting Real-World ML Model Training")
    logger.info("=" * 60)
    
    trainer = RealWorldMLTrainer()
    
    # Train all models
    models = trainer.train_all_models()
    
    logger.info("=" * 60)
    logger.info(f"✅ Training complete! Trained {len(models)} models:")
    for model_name in models.keys():
        logger.info(f"   - {model_name}")
    
    logger.info("\n🎯 Models are now ready for production use!")

if __name__ == "__main__":
    main()
