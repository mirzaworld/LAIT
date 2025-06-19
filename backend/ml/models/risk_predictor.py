"""
Risk prediction model for invoices
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

class RiskPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_importance = {}
    
    def _extract_features(self, invoices: pd.DataFrame, line_items: pd.DataFrame = None) -> pd.DataFrame:
        """Extract features for risk prediction"""
        features = pd.DataFrame()
        
        # Basic invoice features
        features['total_amount'] = invoices['total_amount']
        features['is_pending'] = (invoices['status'] == 'pending').astype(int)
        
        # Add line item features if available
        if line_items is not None:
            line_items_agg = line_items.groupby('invoice_id').agg({
                'hours': ['sum', 'mean', 'std'],
                'rate': ['mean', 'std'],
                'amount': ['sum', 'mean', 'std']
            }).fillna(0)
            
            line_items_agg.columns = [f'{col[0]}_{col[1]}' for col in line_items_agg.columns]
            features = features.join(line_items_agg, on='invoice_id')
        
        return features.fillna(0)
    
    def train(self, invoices: pd.DataFrame, line_items: pd.DataFrame) -> None:
        """Train the risk prediction model"""
        X = self._extract_features(invoices, line_items)
        
        # Target is derived from various risk factors
        y = self._calculate_risk_target(invoices, line_items)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Store feature importance
        self.feature_importance = dict(zip(X.columns, self.model.feature_importances_))
    
    def predict(self, invoice: pd.DataFrame, line_items: pd.DataFrame = None) -> float:
        """Predict risk score for an invoice"""
        X = self._extract_features(invoice, line_items)
        X_scaled = self.scaler.transform(X)
        return float(self.model.predict(X_scaled)[0])
    
    def explain_risk(self, invoice: pd.DataFrame) -> list:
        """Explain risk factors for an invoice"""
        X = self._extract_features(invoice)
        risk_factors = []
        
        # Get feature contributions
        for feature, importance in self.feature_importance.items():
            if importance > 0.05:  # Only include significant factors
                value = X[feature].iloc[0]
                risk_factors.append({
                    'factor': feature,
                    'importance': float(importance),
                    'value': float(value)
                })
        
        return sorted(risk_factors, key=lambda x: x['importance'], reverse=True)
    
    def _calculate_risk_target(self, invoices: pd.DataFrame, line_items: pd.DataFrame) -> np.ndarray:
        """Calculate risk target based on various factors"""
        risk_scores = pd.Series(0.0, index=invoices.index)
        
        # High amount invoices
        amount_threshold = invoices['total_amount'].quantile(0.9)
        risk_scores += (invoices['total_amount'] > amount_threshold).astype(float) * 0.3
        
        # Unusual hours
        if 'hours' in line_items.columns:
            line_items_agg = line_items.groupby('invoice_id')['hours'].agg(['mean', 'std'])
            hours_threshold = line_items_agg['mean'].quantile(0.9)
            risk_scores += (line_items_agg['mean'] > hours_threshold).astype(float) * 0.3
        
        # Pending status
        risk_scores += (invoices['status'] == 'pending').astype(float) * 0.2
        
        # Normalize to 0-1 range
        return risk_scores / risk_scores.max()
    
    def save_model(self, path: str) -> None:
        """Save model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance
        }, path)
    
    def load_model(self, path: str) -> None:
        """Load model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_importance = data['feature_importance']
