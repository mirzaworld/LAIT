import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import joblib
import os
import re
import nltk
import spacy
from datetime import datetime
from db.database import get_db_session
from db.database import Invoice, LineItem, RiskFactor, Vendor

class InvoiceAnalyzer:
    def __init__(self):
        self.model_path = 'models/invoice_anomaly_model.joblib'
        self.vectorizer_path = 'models/invoice_vectorizer.joblib'
        self.scaler_path = 'models/invoice_scaler.joblib'
        
        # Initialize NLP resources
        try:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            self.nlp = spacy.load('en_core_web_sm')
            self.stop_words = set(nltk.corpus.stopwords.words('english'))
        except:
            print("NLP resources couldn't be downloaded. Using basic processing.")
            self.stop_words = {'the', 'and', 'to', 'of', 'in', 'for', 'with'}
        
        self._load_models()
        
    def _load_models(self):
        """Load or initialize all ML models"""
        try:
            # Load anomaly detection model
            if os.path.exists(self.model_path):
                self.isolation_forest = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                self.scaler = joblib.load(self.scaler_path)
            else:
                # Initialize new models
                self.isolation_forest = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words=self.stop_words
                )
                self.scaler = StandardScaler()
                
                # Train models with historical data if available
                self._train_initial_models()
                
        except Exception as e:
            print(f"Error loading models: {str(e)}")
            self._initialize_new_models()
    
    def analyze_invoice(self, invoice_data):
        """Comprehensive invoice analysis"""
        session = get_db_session()
        try:
            # Extract and process invoice data
            processed_data = self._preprocess_invoice(invoice_data)
            
            # Calculate risk score and detect anomalies
            risk_analysis = self._analyze_risk(processed_data)
            
            # Analyze line items
            line_items_analysis = self._analyze_line_items(processed_data['line_items'])
            
            # Compare with historical data
            historical_analysis = self._compare_with_historical(processed_data, session)
            
            # Generate final analysis and recommendations
            analysis_result = {
                'risk_score': risk_analysis['risk_score'],
                'anomalies': risk_analysis['anomalies'],
                'line_items_analysis': line_items_analysis,
                'historical_comparison': historical_analysis,
                'recommendations': self._generate_recommendations(
                    risk_analysis,
                    line_items_analysis,
                    historical_analysis
                )
            }
            
            # Save analysis results
            invoice = self._save_analysis_results(invoice_data, analysis_result, session)
            
            return analysis_result
            
        finally:
            session.close()
    
    def _preprocess_invoice(self, invoice_data):
        """Preprocess and structure invoice data"""
        processed = {
            'total_amount': float(invoice_data.get('amount', 0)),
            'line_items': self._process_line_items(invoice_data.get('line_items', [])),
            'metadata': self._extract_metadata(invoice_data),
            'text_features': self._extract_text_features(invoice_data)
        }
        return processed
    
    def _analyze_risk(self, processed_data):
        """Analyze invoice risk using ML models"""
        risk_factors = []
        risk_score = 0
        
        # Extract feature vector
        features = self._extract_features(processed_data)
        
        # Detect anomalies
        if self.isolation_forest and self.scaler:
            scaled_features = self.scaler.transform([features])
            anomaly_score = self.isolation_forest.score_samples(scaled_features)[0]
            risk_score = self._calculate_risk_score(anomaly_score, processed_data)
            
            # Identify specific risk factors
            risk_factors = self._identify_risk_factors(features, anomaly_score)
        
        return {
            'risk_score': risk_score,
            'anomalies': risk_factors
        }
    
    def _calculate_risk_score(self, anomaly_score, processed_data):
        """Calculate final risk score using multiple factors"""
        base_score = 50 - (anomaly_score * 20)  # Convert to 0-100 scale
        
        # Adjust based on amount thresholds
        amount = processed_data['total_amount']
        if amount > 50000:
            base_score += 10
        elif amount > 100000:
            base_score += 20
            
        # Adjust based on line item analysis
        if self._has_suspicious_line_items(processed_data['line_items']):
            base_score += 15
            
        # Cap the score between 0 and 100
        return min(max(base_score, 0), 100)
    
    def _identify_risk_factors(self, features, anomaly_score):
        """Identify specific risk factors from features"""
        risk_factors = []
        
        # Check for high amounts
        if features[0] > self.amount_threshold:
            risk_factors.append({
                'type': 'high_amount',
                'severity': 'high',
                'description': f"Invoice amount (${features[0]}) exceeds normal range"
            })
            
        # Check for unusual hours
        if features[1] > self.hours_threshold:
            risk_factors.append({
                'type': 'excessive_hours',
                'severity': 'medium',
                'description': f"Total hours ({features[1]}) are higher than typical"
            })
            
        # Check for rate anomalies
        if features[2] > self.rate_threshold:
            risk_factors.append({
                'type': 'high_rate',
                'severity': 'high',
                'description': f"Hourly rate (${features[2]}) is above normal range"
            })
            
        return risk_factors
    
    def _generate_recommendations(self, risk_analysis, line_items_analysis, historical_analysis):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Process risk-based recommendations
        if risk_analysis['risk_score'] > 70:
            recommendations.append({
                'type': 'review',
                'priority': 'high',
                'description': 'Manual review recommended due to high risk score',
                'rationale': f"Risk score of {risk_analysis['risk_score']} exceeds threshold"
            })
            
        # Add line item specific recommendations
        for item in line_items_analysis.get('flagged_items', []):
            recommendations.append({
                'type': 'line_item',
                'priority': 'medium',
                'description': f"Review suspicious line item: {item['description']}",
                'potential_savings': item.get('potential_savings', 0)
            })
            
        # Add historical comparison recommendations
        if historical_analysis.get('rate_increase', 0) > 10:
            recommendations.append({
                'type': 'rate_negotiation',
                'priority': 'high',
                'description': 'Consider rate negotiation',
                'rationale': f"{historical_analysis['rate_increase']}% increase in rates"
            })
            
        return recommendations
    
    def _save_analysis_results(self, invoice_data, analysis_result, session):
        """Save analysis results to database"""
        try:
            # Create/update invoice record
            invoice = Invoice(
                invoice_number=invoice_data['invoice_number'],
                vendor_id=invoice_data['vendor_id'],
                amount=invoice_data['amount'],
                date=datetime.strptime(invoice_data['date'], '%Y-%m-%d'),
                status='pending_review',
                description=invoice_data.get('description', ''),
                risk_score=analysis_result['risk_score'],
                analysis_result=analysis_result
            )
            session.add(invoice)
            
            # Add risk factors
            for anomaly in analysis_result['anomalies']:
                risk_factor = RiskFactor(
                    invoice=invoice,
                    factor_type=anomaly['type'],
                    description=anomaly['description'],
                    severity=anomaly['severity'],
                    impact_score=analysis_result['risk_score']
                )
                session.add(risk_factor)
            
            # Add line items
            for item in invoice_data.get('line_items', []):
                line_item = LineItem(
                    invoice=invoice,
                    description=item['description'],
                    hours=item.get('hours', 0),
                    rate=item.get('rate', 0),
                    amount=item.get('amount', 0),
                    timekeeper=item.get('timekeeper', ''),
                    timekeeper_title=item.get('timekeeper_title', ''),
                    date=datetime.strptime(item.get('date', invoice_data['date']), '%Y-%m-%d')
                )
                session.add(line_item)
            
            session.commit()
            return invoice
            
        except Exception as e:
            session.rollback()
            raise e
    
    def _initialize_new_models(self):
        """Initialize new ML models when they don't exist or fail to load"""
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )
        
        self.scaler = StandardScaler()
        
        # Set default thresholds based on domain knowledge
        self.amount_threshold = 50000
        self.hours_threshold = 200
        self.rate_threshold = 800
        
        # Try to train with any available data
        self._train_initial_models()
    
    def retrain_model(self):
        """Retrain models with all available data"""
        from db.database import get_db_session, Invoice, LineItem
        from utils.ml_preprocessing import extract_invoice_features, preprocess_text, scale_features
        import pandas as pd
        
        session = get_db_session()
        try:
            # Get all invoice data
            invoices = session.query(Invoice).all()
            
            if len(invoices) < 10:
                print("Not enough data for model retraining")
                return False
                
            # Extract features from invoices
            feature_list = []
            text_data = []
            
            for invoice in invoices:
                # Convert invoice to dict
                invoice_dict = {
                    'id': invoice.id,
                    'amount': invoice.amount,
                    'hours': invoice.hours or 0,
                    'rate': invoice.rate or 0,
                    'description': invoice.description,
                    'status': invoice.status,
                    'line_items': []
                }
                
                # Get line items for this invoice
                line_items = session.query(LineItem).filter(LineItem.invoice_id == invoice.id).all()
                
                for item in line_items:
                    line_item_dict = {
                        'description': item.description,
                        'hours': item.hours,
                        'rate': item.rate,
                        'amount': item.amount,
                        'timekeeper': item.timekeeper,
                        'timekeeper_title': item.timekeeper_title
                    }
                    invoice_dict['line_items'].append(line_item_dict)
                
                # Extract numerical features
                features, _ = extract_invoice_features(invoice_dict)
                feature_list.append(features)
                
                # Process text data
                text_corpus = invoice.description + ' ' + ' '.join([item.description for item in line_items if item.description])
                text_data.append(preprocess_text(text_corpus))
            
            # Convert to DataFrame and normalize
            feature_df = pd.DataFrame(feature_list)
            self.scaler = StandardScaler().fit(feature_df)
            scaled_features = self.scaler.transform(feature_df)
            
            # Fit text vectorizer
            self.vectorizer.fit(text_data)
            
            # Train isolation forest model for anomaly detection
            self.isolation_forest = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
            self.isolation_forest.fit(scaled_features)
            
            # Calculate new thresholds based on data distribution
            self.amount_threshold = np.percentile([invoice.amount for invoice in invoices], 90)
            self.hours_threshold = np.percentile([invoice.hours for invoice in invoices if invoice.hours], 90)
            self.rate_threshold = np.percentile([invoice.rate for invoice in invoices if invoice.rate], 90)
            
            # Save models
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.isolation_forest, self.model_path)
            joblib.dump(self.vectorizer, self.vectorizer_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            print("Models successfully retrained and saved")
            return True
            
        except Exception as e:
            print(f"Error retraining models: {e}")
            return False
            
        finally:
            session.close()

    def _train_initial_models(self):
        """Train the initial models with historical data if available"""
        from db.database import get_db_session, Invoice, LineItem
        from utils.ml_preprocessing import extract_invoice_features, preprocess_text
        import pandas as pd
        
        session = get_db_session()
        try:
            # Get historical invoice data
            invoices = session.query(Invoice).all()
            
            if len(invoices) < 10:
                print("Not enough historical data for initial model training")
                return
                
            # Extract features from historical invoices
            feature_list = []
            text_data = []
            
            for invoice in invoices:
                # Convert invoice to dict
                invoice_dict = {
                    'id': invoice.id,
                    'amount': invoice.amount,
                    'hours': invoice.hours or 0,
                    'rate': invoice.rate or 0,
                    'description': invoice.description,
                    'status': invoice.status,
                    'line_items': []
                }
                
                # Get line items for this invoice
                line_items = session.query(LineItem).filter(LineItem.invoice_id == invoice.id).all()
                
                for item in line_items:
                    line_item_dict = {
                        'description': item.description,
                        'hours': item.hours,
                        'rate': item.rate,
                        'amount': item.amount,
                        'timekeeper': item.timekeeper,
                        'timekeeper_title': item.timekeeper_title
                    }
                    invoice_dict['line_items'].append(line_item_dict)
                
                # Extract numerical features
                features, _ = extract_invoice_features(invoice_dict)
                feature_list.append(features)
                
                # Process text data
                text_corpus = invoice.description + ' ' + ' '.join([item.description for item in line_items if item.description])
                text_data.append(preprocess_text(text_corpus))
            
            # Convert to DataFrame and normalize
            feature_df = pd.DataFrame(feature_list)
            self.scaler.fit(feature_df)
            scaled_features = self.scaler.transform(feature_df)
            
            # Fit text vectorizer
            self.vectorizer.fit(text_data)
            
            # Train isolation forest model for anomaly detection
            self.isolation_forest.fit(scaled_features)
            
            # Save models
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.isolation_forest, self.model_path)
            joblib.dump(self.vectorizer, self.vectorizer_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            print("Initial models trained and saved successfully")
            
        except Exception as e:
            print(f"Error training initial models: {e}")
            
        finally:
            session.close()
