import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

class RiskPredictor:
    def __init__(self):
        self.model_path = 'models/risk_prediction_model.joblib'
        self.scaler_path = 'models/risk_scaler.joblib'
        
        # Load model if exists, otherwise will be trained on first use
        self._load_model()
        
    def _load_model(self):
        """Load pre-trained model if available"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print("Risk prediction model loaded successfully")
            else:
                print("Risk prediction model not found, will be trained on first use")
                self.model = None
                self.scaler = None
        except Exception as e:
            print(f"Error loading risk prediction model: {str(e)}")
            self.model = None
            self.scaler = None
    
    def _train_model(self, invoice_data):
        """Train the risk prediction model"""
        print("Training risk prediction model...")
        
        # Extract features
        features = []
        targets = []
        
        for invoice in invoice_data:
            # Example features - in production these would be more comprehensive
            features.append([
                invoice['amount'],
                invoice['timekeeper_count'] if 'timekeeper_count' in invoice else 0,
                invoice['line_item_count'] if 'line_item_count' in invoice else 0,
                invoice['avg_rate'] if 'avg_rate' in invoice else 0,
                invoice['days_to_submit'] if 'days_to_submit' in invoice else 30,
                # Categorical features would be one-hot encoded
                1 if invoice.get('has_expenses', False) else 0,
                1 if invoice.get('is_litigation', False) else 0
            ])
            
            # Target is the historical risk score or known issues
            targets.append(invoice.get('historical_risk_score', 0))
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(targets)
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100)
        self.model.fit(X_scaled, y)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        print("Risk prediction model training complete")
    
    def predict_risk(self, invoice_data):
        """Predict risk score for a new invoice"""
        # If model doesn't exist yet, train it with sample data
        if self.model is None:
            sample_data = self._get_sample_training_data()
            self._train_model(sample_data)
        
        # Extract features from input invoice
        features = np.array([[
            invoice_data['amount'],
            invoice_data.get('timekeeper_count', 0),
            invoice_data.get('line_item_count', len(invoice_data.get('line_items', []))),
            invoice_data.get('avg_rate', self._calculate_avg_rate(invoice_data)),
            invoice_data.get('days_to_submit', 30),
            1 if invoice_data.get('has_expenses', False) else 0,
            1 if invoice_data.get('is_litigation', False) else 0
        ]])
        
        # Scale features
        X_scaled = self.scaler.transform(features)
        
        # Predict risk score
        risk_score = self.model.predict(X_scaled)[0]
        
        # Add additional risk factors
        additional_risk = self._evaluate_additional_risk_factors(invoice_data)
        final_risk_score = min(risk_score + additional_risk, 100)
        
        return {
            'risk_score': final_risk_score,
            'risk_level': self._get_risk_level(final_risk_score),
            'risk_factors': self._identify_risk_factors(invoice_data, final_risk_score)
        }
    
    def retrain_model(self):
        """Retrain the risk model with all available data"""
        from db.database import get_db_session, Invoice, LineItem, RiskFactor
        import pandas as pd
        
        session = get_db_session()
        try:
            # Get all invoices with risk factors
            invoices = session.query(Invoice).all()
            
            if len(invoices) < 10:
                print("Not enough data for risk model retraining")
                return False
            
            # Prepare training data
            features = []
            targets = []
            
            for invoice in invoices:
                # Skip invoices without risk score
                if invoice.risk_score is None:
                    continue
                
                # Get line items
                line_items = session.query(LineItem).filter(LineItem.invoice_id == invoice.id).all()
                
                # Get risk factors
                risk_factors = session.query(RiskFactor).filter(RiskFactor.invoice_id == invoice.id).all()
                
                # Extract features
                invoice_features = [
                    invoice.amount,
                    len(line_items),  # line item count
                    invoice.hours or 0,
                    invoice.rate or 0,
                    len(set(item.timekeeper for item in line_items if item.timekeeper)),  # unique timekeepers
                    len(risk_factors),  # risk factor count
                    1 if 'litigation' in (invoice.description or '').lower() else 0,  # litigation flag
                    1 if any(rf.factor_type == 'high_amount' for rf in risk_factors) else 0,  # high amount flag
                    1 if any(rf.factor_type == 'excessive_hours' for rf in risk_factors) else 0  # excessive hours flag
                ]
                
                features.append(invoice_features)
                targets.append(invoice.risk_score)
            
            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(targets)
            
            if len(X) < 10:
                print("Not enough complete data for risk model training")
                return False
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model with cross-validation to avoid overfitting
            from sklearn.model_selection import cross_val_score
            from sklearn.ensemble import GradientBoostingRegressor
            
            # Try different models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(random_state=42)
            }
            
            best_score = -float('inf')
            best_model = None
            
            for name, model in models.items():
                scores = cross_val_score(model, X_scaled, y, cv=5, scoring='neg_mean_absolute_error')
                avg_score = np.mean(scores)
                
                if avg_score > best_score:
                    best_score = avg_score
                    best_model = model
                    
                print(f"{name} model cross-validation score: {avg_score}")
            
            # Train final model on all data
            self.model = best_model
            self.model.fit(X_scaled, y)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            print("Risk prediction model successfully retrained and saved")
            return True
            
        except Exception as e:
            print(f"Error retraining risk prediction model: {e}")
            return False
            
        finally:
            session.close()
    
    def _calculate_avg_rate(self, invoice_data):
        """Calculate average rate from line items"""
        line_items = invoice_data.get('line_items', [])
        if not line_items:
            return 0
            
        rates = [item.get('rate', 0) for item in line_items if 'rate' in item]
        return sum(rates) / len(rates) if rates else 0
    
    def _evaluate_additional_risk_factors(self, invoice_data):
        """Evaluate additional risk factors not captured by the model"""
        additional_risk = 0
        risk_factors = []
        
        # Check for block billing
        if self._has_block_billing(invoice_data):
            additional_risk += 10
            risk_factors.append({
                'type': 'block_billing',
                'description': 'Line item(s) contain block billing',
                'severity': 'medium',
                'impact': 10
            })
        
        # Check for vague descriptions
        vague_items = self._find_vague_descriptions(invoice_data)
        if vague_items:
            additional_risk += 5
            risk_factors.append({
                'type': 'vague_descriptions',
                'description': f'Found {len(vague_items)} line item(s) with vague descriptions',
                'severity': 'low',
                'impact': 5
            })
            
        # Check for excessive time on administrative tasks
        admin_time = self._check_administrative_time(invoice_data)
        if admin_time > 5:  # More than 5 hours on admin tasks
            additional_risk += 15
            risk_factors.append({
                'type': 'excessive_admin',
                'description': f'Excessive time ({admin_time}h) on administrative tasks',
                'severity': 'high',
                'impact': 15
            })
            
        # Check for rate inconsistencies
        if self._has_rate_inconsistencies(invoice_data):
            additional_risk += 20
            risk_factors.append({
                'type': 'rate_inconsistency',
                'description': 'Rate inconsistencies found across similar timekeeper levels',
                'severity': 'high',
                'impact': 20
            })
            
        return additional_risk, risk_factors
    
    def _get_risk_level(self, score):
        """Convert risk score to risk level"""
        if score < 30:
            return 'low'
        elif score < 70:
            return 'medium'
        else:
            return 'high'
    
    def _identify_risk_factors(self, invoice_data, risk_score):
        """Identify specific risk factors that contributed to the score"""
        risk_factors = []
        
        # Sample logic to identify risk factors
        if invoice_data['amount'] > 50000:
            risk_factors.append({
                'type': 'high_amount',
                'description': 'Invoice amount exceeds typical threshold'
            })
        
        if invoice_data.get('avg_rate', 0) > 500:
            risk_factors.append({
                'type': 'high_rate',
                'description': 'Average hourly rate is above benchmark for similar matters'
            })
        
        line_items = invoice_data.get('line_items', [])
        for item in line_items:
            if item.get('hours', 0) > 10:
                risk_factors.append({
                    'type': 'high_hours',
                    'description': f"Time entry of {item.get('hours')} hours may indicate block billing"
                })
            
        return risk_factors
    
    def _get_sample_training_data(self):
        """Get sample data for initial model training"""
        # In production, this would come from historical invoices
        # For demo purposes, we're using synthetic data
        return [
            {
                'amount': 12500,
                'timekeeper_count': 2,
                'line_item_count': 8,
                'avg_rate': 350,
                'days_to_submit': 15,
                'has_expenses': False,
                'is_litigation': True,
                'historical_risk_score': 25
            },
            {
                'amount': 45000,
                'timekeeper_count': 5,
                'line_item_count': 20,
                'avg_rate': 450,
                'days_to_submit': 30,
                'has_expenses': True,
                'is_litigation': True,
                'historical_risk_score': 40
            },
            {
                'amount': 78000,
                'timekeeper_count': 8,
                'line_item_count': 45,
                'avg_rate': 525,
                'days_to_submit': 45,
                'has_expenses': True,
                'is_litigation': True,
                'historical_risk_score': 75
            },
            # More sample data would be included in a real system
        ]
    
    def _has_block_billing(self, invoice_data):
        """Check for block billing (multiple activities in single entry)"""
        line_items = invoice_data.get('line_items', [])
        
        for item in line_items:
            desc = item.get('description', '')
            if desc:
                # Check for multiple verbs or "and" with significant hours
                has_multiple_actions = len(re.findall(r'\b(?:and|;)\b', desc)) > 1
                has_significant_hours = item.get('hours', 0) > 4
                
                if has_multiple_actions and has_significant_hours:
                    return True
                    
        return False
    
    def _find_vague_descriptions(self, invoice_data):
        """Find line items with vague descriptions"""
        vague_items = []
        vague_terms = ['review', 'analyze', 'work on', 'attention to', 'research', 'various', 'miscellaneous']
        
        line_items = invoice_data.get('line_items', [])
        
        for item in line_items:
            desc = item.get('description', '').lower()
            
            # Check if description is just one of the vague terms
            if any(term == desc for term in vague_terms):
                vague_items.append(item)
            
            # Check if description is very short
            elif len(desc.split()) < 3:
                vague_items.append(item)
                
        return vague_items
    
    def _check_administrative_time(self, invoice_data):
        """Calculate time spent on administrative tasks"""
        admin_time = 0
        admin_keywords = ['file', 'organize', 'formatting', 'scheduling', 'calendar', 'email', 'correspondence']
        
        line_items = invoice_data.get('line_items', [])
        
        for item in line_items:
            desc = item.get('description', '').lower()
            
            # Check if description contains admin keywords
            if any(keyword in desc for keyword in admin_keywords):
                admin_time += float(item.get('hours', 0))
                
        return admin_time
    
    def _has_rate_inconsistencies(self, invoice_data):
        """Check for rate inconsistencies across similar timekeeper levels"""
        timekeeper_rates = {}
        line_items = invoice_data.get('line_items', [])
        
        # Group rates by timekeeper title
        for item in line_items:
            title = item.get('timekeeper_title', '').lower()
            rate = item.get('rate', 0)
            
            if title and rate > 0:
                if title not in timekeeper_rates:
                    timekeeper_rates[title] = []
                timekeeper_rates[title].append(rate)
        
        # Check for significant variance within same title
        for title, rates in timekeeper_rates.items():
            if len(rates) > 1:
                min_rate = min(rates)
                max_rate = max(rates)
                
                # If variance is more than 25%
                if max_rate > min_rate * 1.25:
                    return True
                    
        return False
