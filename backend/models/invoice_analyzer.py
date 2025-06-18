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
    
    def _analyze_line_items(self, line_items):
        """Detailed analysis of invoice line items"""
        results = []
        
        if not line_items:
            return []
            
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(line_items)
        
        # Extract numeric features for anomaly detection
        numeric_features = self._extract_numeric_features(df)
        
        # Text analysis for descriptions
        text_features = self._analyze_descriptions([item['description'] for item in line_items])
        
        # Detect rate and hours anomalies
        rate_anomalies = self._detect_rate_anomalies(df)
        hours_anomalies = self._detect_hours_anomalies(df)
        
        # Combine all anomalies
        for idx, item in enumerate(line_items):
            anomalies = []
            risk_score = 0.0
            
            # Check rate anomalies
            if rate_anomalies[idx]:
                anomalies.append({
                    'type': 'high_rate',
                    'severity': 'high',
                    'message': f"Hourly rate (${item['rate']}) significantly above normal range"
                })
                risk_score += 0.4
                
            # Check hours anomalies
            if hours_anomalies[idx]:
                anomalies.append({
                    'type': 'unusual_hours',
                    'severity': 'medium',
                    'message': f"Unusual number of hours ({item['hours']}) for this type of task"
                })
                risk_score += 0.3
                
            # Check text anomalies
            if text_features[idx].get('is_suspicious', False):
                anomalies.append({
                    'type': 'suspicious_description',
                    'severity': 'medium',
                    'message': text_features[idx].get('reason', 'Unusual task description')
                })
                risk_score += 0.3
                
            results.append({
                'line_item_id': item.get('id'),
                'risk_score': min(risk_score, 1.0),
                'anomalies': anomalies,
                'recommendations': self._get_line_item_recommendations(anomalies)
            })
            
        return results

    def _extract_numeric_features(self, df):
        """Extract numeric features from line items"""
        features = []
        
        if df.empty:
            return np.array([])
            
        # Basic features
        features.append(df['hours'].values)
        features.append(df['rate'].values)
        features.append(df['hours'] * df['rate'].values)  # total amount
        
        # Derived features
        if 'task_code' in df.columns:
            # Calculate average rate and hours by task code
            task_avg_rate = df.groupby('task_code')['rate'].transform('mean')
            task_avg_hours = df.groupby('task_code')['hours'].transform('mean')
            
            features.append(df['rate'] / task_avg_rate)  # rate ratio
            features.append(df['hours'] / task_avg_hours)  # hours ratio
            
        return np.column_stack(features)

    def _analyze_descriptions(self, descriptions):
        """Analyze line item descriptions for suspicious patterns"""
        results = []
        
        # Common vague terms that might indicate insufficient detail
        vague_terms = {'review', 'analyze', 'work on', 'attention to', 'various', 'miscellaneous'}
        
        # Patterns that might indicate block billing
        block_billing_patterns = [
            r'multiple tasks',
            r'various matters',
            r'and other',
            r'including.*and.*and'
        ]
        
        for desc in descriptions:
            analysis = {
                'is_suspicious': False,
                'reason': None,
                'suggestions': []
            }
            
            # Convert to lowercase for analysis
            desc_lower = desc.lower()
            
            # Check for vague descriptions
            vague_count = sum(1 for term in vague_terms if term in desc_lower)
            if vague_count >= 2:
                analysis['is_suspicious'] = True
                analysis['reason'] = 'Vague description'
                analysis['suggestions'].append('Provide more specific details about the work performed')
            
            # Check for block billing
            for pattern in block_billing_patterns:
                if re.search(pattern, desc_lower):
                    analysis['is_suspicious'] = True
                    analysis['reason'] = 'Potential block billing'
                    analysis['suggestions'].append('Split multiple tasks into separate line items')
                    break
            
            # Check description length
            if len(desc.split()) < 3:
                analysis['is_suspicious'] = True
                analysis['reason'] = 'Description too brief'
                analysis['suggestions'].append('Provide more detailed description')
            
            results.append(analysis)
            
        return results

    def _detect_rate_anomalies(self, df):
        """Detect anomalies in hourly rates"""
        if df.empty:
            return []
            
        rates = df['rate'].values.reshape(-1, 1)
        
        # Use robust statistics to detect outliers
        Q1 = np.percentile(rates, 25)
        Q3 = np.percentile(rates, 75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR
        
        return rates.flatten() > upper_bound

    def _detect_hours_anomalies(self, df):
        """Detect anomalies in hours billed"""
        if df.empty:
            return []
            
        hours = df['hours'].values.reshape(-1, 1)
        
        # Detect outliers using Isolation Forest for more robust detection
        if len(hours) >= 10:  # Only use ML for sufficient data
            clf = IsolationForest(contamination=0.1, random_state=42)
            return clf.fit_predict(hours) == -1
        else:
            # Use simple statistical method for small datasets
            Q1 = np.percentile(hours, 25)
            Q3 = np.percentile(hours, 75)
            IQR = Q3 - Q1
            upper_bound = Q3 + 2 * IQR  # More lenient threshold
            
            return hours.flatten() > upper_bound

    def _get_line_item_recommendations(self, anomalies):
        """Generate recommendations based on line item anomalies"""
        recommendations = []
        
        for anomaly in anomalies:
            if anomaly['type'] == 'high_rate':
                recommendations.append({
                    'action': 'review_rate',
                    'message': 'Consider negotiating lower rates or using alternative resources'
                })
            elif anomaly['type'] == 'unusual_hours':
                recommendations.append({
                    'action': 'review_hours',
                    'message': 'Verify time entries and task complexity'
                })
            elif anomaly['type'] == 'suspicious_description':
                recommendations.append({
                    'action': 'improve_description',
                    'message': 'Request more detailed task descriptions'
                })
                
        return recommendations

    def _compare_with_historical(self, processed_data, session):
        """Compare invoice with historical data"""
        vendor_id = processed_data.get('vendor_id')
        matter_id = processed_data.get('matter_id')
        
        if not vendor_id or not matter_id:
            return {}
            
        # Query historical data
        historical = session.query(Invoice).filter(
            Invoice.vendor_id == vendor_id,
            Invoice.matter_id == matter_id,
            Invoice.processed == True  # Only consider processed invoices
        ).all()
        
        if not historical:
            return {
                'comparison_available': False,
                'reason': 'No historical data available for this vendor/matter combination'
            }
            
        # Calculate historical metrics
        historical_rates = []
        historical_hours = []
        historical_totals = []
        
        for inv in historical:
            for line in inv.line_items:
                if line.rate:
                    historical_rates.append(line.rate)
                if line.hours:
                    historical_hours.append(line.hours)
            historical_totals.append(inv.amount)
            
        if not historical_rates or not historical_hours:
            return {
                'comparison_available': False,
                'reason': 'Insufficient historical data for comparison'
            }
            
        # Calculate statistics
        comparison = {
            'comparison_available': True,
            'rates': {
                'avg': np.mean(historical_rates),
                'std': np.std(historical_rates),
                'current_vs_avg': (processed_data['avg_rate'] / np.mean(historical_rates) - 1) * 100
            },
            'hours': {
                'avg': np.mean(historical_hours),
                'std': np.std(historical_hours),
                'current_vs_avg': (processed_data['total_hours'] / np.mean(historical_hours) - 1) * 100
            },
            'total': {
                'avg': np.mean(historical_totals),
                'std': np.std(historical_totals),
                'current_vs_avg': (processed_data['total_amount'] / np.mean(historical_totals) - 1) * 100
            }
        }
        
        # Add trend analysis if sufficient data
        if len(historical) >= 3:
            comparison['trend'] = self._analyze_trends(historical)
            
        return comparison

    def _analyze_trends(self, historical_invoices):
        """Analyze trends in historical invoice data"""
        dates = [inv.date for inv in historical_invoices]
        amounts = [inv.amount for inv in historical_invoices]
        
        # Sort by date
        sorted_data = sorted(zip(dates, amounts))
        dates, amounts = zip(*sorted_data)
        
        # Calculate basic trend
        if len(dates) >= 2:
            first_amount = amounts[0]
            last_amount = amounts[-1]
            time_diff = (dates[-1] - dates[0]).days / 30  # Convert to months
            
            if time_diff > 0:
                monthly_change = ((last_amount / first_amount) ** (1/time_diff) - 1) * 100
                
                return {
                    'duration_months': round(time_diff, 1),
                    'monthly_change_pct': round(monthly_change, 2),
                    'direction': 'increasing' if monthly_change > 0 else 'decreasing',
                    'significant': abs(monthly_change) > 5  # Flag if change is more than 5% per month
                }
        
        return None
