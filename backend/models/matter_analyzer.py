import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta, date
import logging

class MatterAnalyzer:
    def __init__(self):
        self.model_path = 'models/matter_forecast_model.joblib'
        self.scaler_path = 'models/matter_scaler.joblib'
        self.model = None
        self.scaler = None
        
        # Load models if they exist
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models if available"""
        try:
            if all(os.path.exists(p) for p in [self.model_path, self.scaler_path]):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print("Matter analysis models loaded successfully")
            else:
                print("Matter analysis models not found, will be trained on first use")
                self.model = None
                self.scaler = None
        except Exception as e:
            print(f"Error loading matter analysis models: {str(e)}")
            self.model = None
            self.scaler = None
    
    def _extract_features(self, matter_data, invoices_data):
        """Extract features for matter expense forecasting"""
        features = []
        
        # Matter-level features
        category = matter_data.get('category', '')
        budget = float(matter_data.get('budget', 0))
        status = matter_data.get('status', '')
        
        # Encode category (one-hot encoding would be better in a real system)
        category_value = 0
        if 'litigation' in category.lower():
            category_value = 1
        elif 'm&a' in category.lower() or 'merger' in category.lower():
            category_value = 2
        elif 'compliance' in category.lower() or 'regulatory' in category.lower():
            category_value = 3
            
        # Status as numeric
        status_value = 0
        if status.lower() == 'active':
            status_value = 1
        elif status.lower() == 'completed':
            status_value = 2
            
        # Calculate days since start
        start_date = matter_data.get('start_date')
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
            
        days_since_start = (datetime.now().date() - start_date).days if start_date else 0
        
        # Invoice-level aggregated features
        if invoices_data:
            invoice_count = len(invoices_data)
            total_spend = sum(inv.get('amount', 0) for inv in invoices_data)
            avg_invoice_amount = total_spend / invoice_count if invoice_count > 0 else 0
            
            # Calculate spending velocity (spend per day)
            spend_velocity = total_spend / max(days_since_start, 1)
            
            # Calculate budget utilization
            budget_utilization = total_spend / budget if budget > 0 else 0
            
            # Timekeeper composition
            partner_hours = sum(inv.get('partner_hours', 0) for inv in invoices_data)
            associate_hours = sum(inv.get('associate_hours', 0) for inv in invoices_data)
            paralegal_hours = sum(inv.get('paralegal_hours', 0) for inv in invoices_data)
            total_hours = partner_hours + associate_hours + paralegal_hours
            
            partner_ratio = partner_hours / total_hours if total_hours > 0 else 0
            associate_ratio = associate_hours / total_hours if total_hours > 0 else 0
            
            features = [
                budget,
                category_value,
                status_value,
                days_since_start,
                total_spend,
                avg_invoice_amount,
                spend_velocity,
                budget_utilization,
                partner_ratio,
                associate_ratio
            ]
        else:
            # Default values if no invoices
            features = [
                budget,
                category_value,
                status_value,
                days_since_start,
                0,  # total_spend
                0,  # avg_invoice_amount
                0,  # spend_velocity
                0,  # budget_utilization
                0,  # partner_ratio
                0   # associate_ratio
            ]
            
        return np.array(features).reshape(1, -1)
    
    def _train_model(self, matters_data):
        """Train the expense forecasting model"""
        print("Training matter expense forecasting model...")
        
        # Extract features and targets
        features_list = []
        targets = []
        
        for matter in matters_data:
            # Only use matters with actual spending data
            if 'invoices' in matter and matter['invoices'] and 'budget' in matter and matter['budget'] > 0:
                features = self._extract_features(matter, matter['invoices'])
                features_list.append(features.flatten())
                
                # Target is the final cost as percentage of budget
                final_cost = sum(inv.get('amount', 0) for inv in matter['invoices'])
                budget = matter['budget']
                cost_pct = min(final_cost / budget, 2.0)  # Cap at 200% over budget
                targets.append(cost_pct)
        
        if not features_list:
            print("Not enough data to train the model")
            return False
            
        # Convert to numpy arrays
        X = np.array(features_list)
        y = np.array(targets)
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        print("Matter expense forecasting model training complete")
        return True
    
    def forecast_expenses(self, matter_id):
        """Forecast final expenses for a matter based on current data"""
        from db.database import get_db_session, Matter, Invoice
        
        session = get_db_session()
        try:
            # Get matter data
            matter = session.query(Matter).filter(Matter.id == matter_id).first()
            if not matter:
                return {'error': f'Matter {matter_id} not found'}
                
            # Get associated invoices
            invoices = session.query(Invoice).filter(Invoice.matter_id == matter_id).all()
            
            # Convert to dictionaries
            matter_data = {
                'id': matter.id,
                'name': matter.name,
                'category': matter.category,
                'status': matter.status,
                'start_date': matter.start_date,
                'end_date': matter.end_date,
                'budget': matter.budget
            }
            
            invoices_data = [
                {
                    'id': inv.id,
                    'amount': inv.amount,
                    'date': inv.date,
                    'hours': inv.hours
                } for inv in invoices
            ]
            
            # Process the data and make prediction
            return self._generate_forecast(matter_data, invoices_data)
            
        except Exception as e:
            print(f"Error in forecast_expenses: {str(e)}")
            return {'error': f'Error generating forecast: {str(e)}'}
        finally:
            session.close()
    
    def _generate_forecast(self, matter_data, invoices_data):
        """Generate expense forecast using the ML model"""
        # Convert any datetime.date instances to datetime.datetime before extraction
        if isinstance(matter_data.get('start_date'), date) and not isinstance(matter_data.get('start_date'), datetime):
            matter_data['start_date'] = datetime.combine(matter_data['start_date'], datetime.min.time())
        
        if isinstance(matter_data.get('end_date'), date) and not isinstance(matter_data.get('end_date'), datetime):
            matter_data['end_date'] = datetime.combine(matter_data['end_date'], datetime.min.time())
            
        current_spend = sum(inv.get('amount', 0) for inv in invoices_data)
        budget = float(matter_data.get('budget', 0))
        
        # Calculate basic metrics
        result = {
            'matter_id': matter_data.get('id'),
            'matter_name': matter_data.get('name'),
            'current_spend': current_spend,
            'budget': budget,
            'budget_utilization': current_spend / budget if budget > 0 else 0,
            'invoice_count': len(invoices_data)
        }
        
        # Make prediction if model is trained and matter has a budget
        if self.model and self.scaler and budget > 0:
            # Extract features
            features = self._extract_features(matter_data, invoices_data)
            features_scaled = self.scaler.transform(features)
            
            # Predict final cost as percentage of budget
            cost_pct_prediction = self.model.predict(features_scaled)[0]
            
            # Calculate projected final cost
            projected_final_cost = cost_pct_prediction * budget
            
            # Remaining budget calculation
            remaining_budget = budget - current_spend
            projected_remaining_cost = projected_final_cost - current_spend
            
            # Budget status
            if projected_final_cost > budget * 1.1:  # More than 10% over budget
                budget_status = 'at_risk'
            elif projected_final_cost > budget:
                budget_status = 'over_budget'
            elif projected_final_cost > budget * 0.9:  # Within 90% of budget
                budget_status = 'near_budget'
            else:
                budget_status = 'under_budget'
                
            # Add ML-based projections to result
            result.update({
                'projected_final_cost': projected_final_cost,
                'budget_variance_amount': projected_final_cost - budget,
                'budget_variance_pct': ((projected_final_cost / budget) - 1) * 100 if budget > 0 else 0,
                'remaining_budget': remaining_budget,
                'projected_remaining_cost': projected_remaining_cost,
                'budget_status': budget_status,
                'confidence_score': 0.85  # Placeholder, would calculate actual confidence in a real system
            })
        else:
            # Fallback to simple extrapolation if ML model not available
            result.update(self._simple_extrapolation(matter_data, invoices_data))
            
        return result
    
    def _simple_extrapolation(self, matter_data, invoices_data):
        """Simple extrapolation when ML model is not available"""
        current_spend = sum(inv.get('amount', 0) for inv in invoices_data)
        budget = float(matter_data.get('budget', 0))
        
        # Estimate based on budget utilization and time elapsed
        start_date = matter_data.get('start_date')
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            
        end_date = matter_data.get('end_date')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        elif end_date is None:
            # If no end date, estimate 6 months from start
            end_date = start_date + timedelta(days=180) if start_date else datetime.now() + timedelta(days=90)
            
        total_days = (end_date - start_date).days if start_date else 180
        elapsed_days = (datetime.now() - start_date).days if start_date else 90
        
        # Avoid division by zero
        time_pct = min(elapsed_days / max(total_days, 1), 1.0)
        
        # Simple linear projection
        if time_pct > 0:
            projected_final_cost = current_spend / time_pct
        else:
            projected_final_cost = current_spend
            
        # Budget status calculation
        if projected_final_cost > budget * 1.1:  # More than 10% over budget
            budget_status = 'at_risk'
        elif projected_final_cost > budget:
            budget_status = 'over_budget'
        elif projected_final_cost > budget * 0.9:  # Within 90% of budget
            budget_status = 'near_budget'
        else:
            budget_status = 'under_budget'
            
        return {
            'projected_final_cost': projected_final_cost,
            'budget_variance_amount': projected_final_cost - budget,
            'budget_variance_pct': ((projected_final_cost / budget) - 1) * 100 if budget > 0 else 0,
            'remaining_budget': budget - current_spend,
            'projected_remaining_cost': projected_final_cost - current_spend,
            'budget_status': budget_status,
            'confidence_score': 0.6,  # Lower confidence for simple extrapolation
            'is_ml_prediction': False
        }
    
    def analyze_matter_risk(self, matter_id):
        """Analyze risk factors for a specific matter"""
        from db.database import get_db_session, Matter, Invoice, LineItem, RiskFactor
        
        session = get_db_session()
        try:
            # Get matter data
            matter = session.query(Matter).filter(Matter.id == matter_id).first()
            if not matter:
                return {'error': f'Matter {matter_id} not found'}
                
            # Get invoices and risk factors
            invoices = session.query(Invoice).filter(Invoice.matter_id == matter_id).all()
            
            # Calculate total spend and budget utilization
            total_spend = sum(inv.amount for inv in invoices)
            budget_utilization = total_spend / matter.budget if matter.budget else 0
            
            # Risk factors identification
            risk_factors = []
            
            # 1. Budget overrun risk
            if budget_utilization > 0.9:
                risk_factors.append({
                    'type': 'budget_overrun',
                    'severity': 'high' if budget_utilization > 1.1 else 'medium',
                    'description': f"Budget utilization at {budget_utilization:.1%}"
                })
                
            # 2. Rate inconsistency risk
            rates = []
            for invoice in invoices:
                line_items = session.query(LineItem).filter(LineItem.invoice_id == invoice.id).all()
                for item in line_items:
                    if item.rate and item.rate > 0:
                        rates.append(item.rate)
            
            if rates:
                avg_rate = sum(rates) / len(rates)
                rate_variance = np.std(rates) / avg_rate if avg_rate > 0 else 0
                
                if rate_variance > 0.25:  # More than 25% variance in rates
                    risk_factors.append({
                        'type': 'rate_inconsistency',
                        'severity': 'medium',
                        'description': f"High rate variance ({rate_variance:.1%}) across invoices"
                    })
            
            # 3. Staffing risk (partner heavy)
            partner_hours = 0
            total_hours = 0
            
            for invoice in invoices:
                line_items = session.query(LineItem).filter(LineItem.invoice_id == invoice.id).all()
                for item in line_items:
                    if 'partner' in item.timekeeper_title.lower():
                        partner_hours += item.hours
                    total_hours += item.hours
            
            partner_ratio = partner_hours / total_hours if total_hours > 0 else 0
            
            if partner_ratio > 0.5:  # More than 50% partner hours
                risk_factors.append({
                    'type': 'partner_heavy',
                    'severity': 'medium',
                    'description': f"Partner-heavy staffing ({partner_ratio:.1%} of hours)"
                })
                
            # 4. Timeline risk
            if matter.end_date:
                days_left = (matter.end_date - datetime.now().date()).days
                completion_risk = False
                
                if days_left < 30 and budget_utilization < 0.7:
                    completion_risk = True
                
                if completion_risk:
                    risk_factors.append({
                        'type': 'timeline_risk',
                        'severity': 'high',
                        'description': f"Only {days_left} days left with {budget_utilization:.1%} budget utilization"
                    })
            
            # Generate risk score (0-100)
            risk_score = min(20 * len(risk_factors) + 40 * budget_utilization, 100)
            
            # Risk level
            if risk_score >= 70:
                risk_level = 'high'
            elif risk_score >= 40:
                risk_level = 'medium'
            else:
                risk_level = 'low'
                
            result = {
                'matter_id': matter_id,
                'matter_name': matter.name,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'budget_utilization': budget_utilization
            }
            
            return result
            
        except Exception as e:
            print(f"Error in analyze_matter_risk: {str(e)}")
            return {'error': f'Error analyzing matter risk: {str(e)}'}
        finally:
            session.close()
    
    def get_mock_matters(self):
        """Return mock matter data for testing purposes"""
        today = datetime.now().date()
        six_months_ago = today - timedelta(days=180)
        five_months_ago = today - timedelta(days=150)
        four_months_ago = today - timedelta(days=120)
        three_months_ago = today - timedelta(days=90)
        two_months_ago = today - timedelta(days=60)
        one_month_ago = today - timedelta(days=30)
        
        return [
            {
                'id': '1',
                'name': 'IP Litigation - TechCorp vs CompetitorX',
                'category': 'Litigation',
                'status': 'Active',
                'start_date': six_months_ago,
                'end_date': today + timedelta(days=90),
                'budget': 500000,
                'invoices': [
                    {'amount': 120000, 'date': five_months_ago, 'partner_hours': 80, 'associate_hours': 200, 'paralegal_hours': 50},
                    {'amount': 150000, 'date': three_months_ago, 'partner_hours': 100, 'associate_hours': 250, 'paralegal_hours': 60},
                    {'amount': 90000, 'date': one_month_ago, 'partner_hours': 60, 'associate_hours': 150, 'paralegal_hours': 40}
                ]
            },
            {
                'id': '2',
                'name': 'M&A Advisory - Acquisition of StartupY',
                'category': 'M&A',
                'status': 'Active',
                'start_date': three_months_ago,
                'end_date': today + timedelta(days=60),
                'budget': 300000,
                'invoices': [
                    {'amount': 100000, 'date': two_months_ago, 'partner_hours': 60, 'associate_hours': 100, 'paralegal_hours': 20},
                    {'amount': 120000, 'date': one_month_ago, 'partner_hours': 70, 'associate_hours': 120, 'paralegal_hours': 25}
                ]
            },
            {
                'id': '3',
                'name': 'Regulatory Compliance - FDA Approval',
                'category': 'Regulatory',
                'status': 'Completed',
                'start_date': six_months_ago,
                'end_date': one_month_ago,
                'budget': 250000,
                'invoices': [
                    {'amount': 80000, 'date': five_months_ago, 'partner_hours': 40, 'associate_hours': 120, 'paralegal_hours': 30},
                    {'amount': 100000, 'date': three_months_ago, 'partner_hours': 50, 'associate_hours': 150, 'paralegal_hours': 40},
                    {'amount': 90000, 'date': one_month_ago, 'partner_hours': 45, 'associate_hours': 130, 'paralegal_hours': 35}
                ]
            }
        ]
