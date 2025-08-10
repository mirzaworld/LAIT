"""
Outlier detection model for invoice line items
"""
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np
import joblib
import os

class OutlierDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,
            random_state=42,
            n_estimators=100
        )
        self.features = ['hours', 'rate', 'amount']
    
    def preprocess_data(self, data: pd.DataFrame) -> np.ndarray:
        """Preprocess data for outlier detection"""
        if not all(f in data.columns for f in self.features):
            raise ValueError(f"Data must contain all features: {self.features}")
        
        return data[self.features].values
    
    def train(self, data: pd.DataFrame) -> None:
        """Train the outlier detection model"""
        if len(data) == 0:
            raise ValueError("Cannot train on empty dataset")
            
        X = self.preprocess_data(data)
        self.model.fit(X)
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict outliers returning boolean flags (True = outlier)."""
        X = self.preprocess_data(data)
        return (self.model.predict(X) == -1)
    
    def get_anomaly_scores(self, data: pd.DataFrame) -> np.ndarray:
        """Get anomaly scores for each data point"""
        X = self.preprocess_data(data)
        return -self.model.score_samples(X)
    
    def save_model(self, path: str) -> None:
        """Save model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
    
    def load_model(self, path: str) -> None:
        """Load model from disk"""
        self.model = joblib.load(path)
