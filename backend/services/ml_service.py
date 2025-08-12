#!/usr/bin/env python3
"""
LAIT ML Service
===============

Machine Learning service for legal invoice analysis.
Loads pre-trained models for anomaly detection and overspend classification,
with fallback to deterministic scoring when models are unavailable.

Models:
- models/iso_forest.pkl: Isolation Forest for anomaly detection
- models/overspend.pkl: Binary classifier for overspend detection

Author: LAIT Development Team
Version: 1.0.0
"""

import os
import logging
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class MLService:
    """ML Service for invoice line scoring and anomaly detection"""
    
    def __init__(self):
        self.models_dir = Path(__file__).parent.parent.parent / 'models'
        self.iso_forest_model = None
        self.overspend_model = None
        self.models_loaded = False
        self.fallback_mode = True
        
        # Load models on initialization
        self._load_models()
    
    def _load_models(self):
        """Load ML models from disk if available"""
        try:
            # Load Isolation Forest model for anomaly detection
            iso_forest_path = self.models_dir / 'iso_forest.pkl'
            if iso_forest_path.exists():
                self.iso_forest_model = joblib.load(iso_forest_path)
                logger.info(f"✅ Loaded Isolation Forest model from {iso_forest_path}")
            else:
                logger.warning(f"⚠️  Isolation Forest model not found at {iso_forest_path}")
            
            # Load overspend classifier model
            overspend_path = self.models_dir / 'overspend.pkl'
            if overspend_path.exists():
                self.overspend_model = joblib.load(overspend_path)
                logger.info(f"✅ Loaded overspend classifier from {overspend_path}")
            else:
                logger.warning(f"⚠️  Overspend model not found at {overspend_path}")
            
            # Check if both models are loaded
            if self.iso_forest_model is not None and self.overspend_model is not None:
                self.models_loaded = True
                self.fallback_mode = False
                logger.info("🤖 ML models loaded successfully - using ML scoring")
            else:
                logger.info("📊 Using deterministic fallback scoring")
                
        except Exception as e:
            logger.error(f"❌ Error loading ML models: {e}")
            logger.info("📊 Falling back to deterministic scoring")
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models from invoice line DataFrame"""
        try:
            # Create a copy to avoid modifying original
            features_df = df.copy()
            
            # Basic numeric features
            features_df['amount'] = pd.to_numeric(features_df.get('amount', 0), errors='coerce').fillna(0)
            features_df['billable_hours'] = pd.to_numeric(features_df.get('billable_hours', 0), errors='coerce').fillna(0)
            features_df['rate'] = pd.to_numeric(features_df.get('rate', 0), errors='coerce').fillna(0)
            
            # Derived features
            features_df['amount_log'] = np.log1p(features_df['amount'])
            features_df['rate_log'] = np.log1p(features_df['rate'])
            features_df['hours_log'] = np.log1p(features_df['billable_hours'])
            
            # Description length feature
            features_df['description_length'] = features_df.get('description', '').astype(str).str.len()
            
            # Rate bands (categorical to numeric)
            features_df['rate_band'] = pd.cut(
                features_df['rate'], 
                bins=[0, 150, 250, 350, 500, float('inf')], 
                labels=[1, 2, 3, 4, 5]
            ).astype(float).fillna(1)
            
            # Amount bands
            features_df['amount_band'] = pd.cut(
                features_df['amount'], 
                bins=[0, 1000, 5000, 10000, float('inf')], 
                labels=[1, 2, 3, 4]
            ).astype(float).fillna(1)
            
            # Hours efficiency (amount per hour)
            features_df['efficiency'] = np.where(
                features_df['billable_hours'] > 0,
                features_df['amount'] / features_df['billable_hours'],
                features_df['amount']
            )
            features_df['efficiency_log'] = np.log1p(features_df['efficiency'])
            
            # Select features for ML models (adjust based on your model training)
            ml_features = [
                'amount', 'billable_hours', 'rate',
                'amount_log', 'rate_log', 'hours_log',
                'description_length', 'rate_band', 'amount_band',
                'efficiency', 'efficiency_log'
            ]
            
            # Return only the ML features
            return features_df[ml_features].fillna(0)
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            # Return minimal features on error
            return pd.DataFrame({
                'amount': df.get('amount', [0] * len(df)),
                'rate': df.get('rate', [0] * len(df))
            })
    
    def _ml_score_lines(self, df: pd.DataFrame) -> List[Tuple[float, bool, str]]:
        """Score lines using ML models"""
        try:
            # Prepare features
            features = self._prepare_features(df)
            
            # Get anomaly scores from Isolation Forest
            anomaly_scores = self.iso_forest_model.decision_function(features)
            
            # Get overspend predictions 
            overspend_probs = self.overspend_model.predict_proba(features)[:, 1]  # Probability of positive class
            
            results = []
            for i in range(len(df)):
                # Combine anomaly and overspend scores
                anomaly_score = float(anomaly_scores[i])
                overspend_prob = float(overspend_probs[i])
                
                # Normalize anomaly score to 0-1 range (Isolation Forest gives negative values for anomalies)
                normalized_anomaly = max(0, min(1, (anomaly_score + 0.5) * -1))  # Invert and normalize
                
                # Combined risk score
                combined_score = (normalized_anomaly * 0.6) + (overspend_prob * 0.4)
                
                # Flag if high risk
                is_flagged = combined_score > 0.7  # Threshold can be tuned
                
                # Generate reason
                if is_flagged:
                    if overspend_prob > 0.8:
                        flag_reason = "ML: High overspend probability"
                    elif normalized_anomaly > 0.8:
                        flag_reason = "ML: Anomalous billing pattern"
                    else:
                        flag_reason = "ML: Combined risk factors"
                else:
                    flag_reason = "ML: Normal billing pattern"
                
                results.append((combined_score, is_flagged, flag_reason))
            
            logger.info(f"🤖 ML scoring completed for {len(results)} lines")
            return results
            
        except Exception as e:
            logger.error(f"Error in ML scoring: {e}")
            # Fall back to deterministic on ML error
            return self._deterministic_score_lines(df)
    
    def _deterministic_score_lines(self, df: pd.DataFrame) -> List[Tuple[float, bool, str]]:
        """Fallback deterministic scoring (original logic)"""
        results = []
        
        for _, row in df.iterrows():
            try:
                description = str(row.get('description', '')).upper()
                amount = float(row.get('amount', 0))
                rate = float(row.get('rate', 0))
                hours = float(row.get('billable_hours', 0))
                
                # Initialize risk factors
                risk_score = 0.0
                risk_factors = []
                
                # High rate detection
                if rate > 800:
                    risk_score += 0.4
                    risk_factors.append("extremely high rate")
                elif rate > 500:
                    risk_score += 0.2
                    risk_factors.append("high rate")
                
                # High amount detection
                if amount > 10000:
                    risk_score += 0.3
                    risk_factors.append("high amount")
                elif amount > 5000:
                    risk_score += 0.15
                    risk_factors.append("elevated amount")
                
                # Suspicious keywords
                suspicious_keywords = [
                    'UNUSUAL', 'SUSPICIOUS', 'EMERGENCY', 'WEEKEND', 'HOLIDAY',
                    'PREMIUM', 'RUSH', 'OVERTIME', 'FLAGGED', 'MISCELLANEOUS',
                    'CONSULTATION FEE', 'TRAVEL EXPENSE', 'ENTERTAINMENT'
                ]
                
                for keyword in suspicious_keywords:
                    if keyword in description:
                        risk_score += 0.25
                        risk_factors.append(f"suspicious term: {keyword.lower()}")
                        break
                
                # Zero hours with high amount (suspicious)
                if hours == 0 and amount > 1000:
                    risk_score += 0.3
                    risk_factors.append("high amount with no billable hours")
                
                # Unusual efficiency (very high or very low amount per hour)
                if hours > 0:
                    efficiency = amount / hours
                    if efficiency > 1000:  # More than $1000/hour
                        risk_score += 0.2
                        risk_factors.append("extremely high hourly rate")
                    elif efficiency < 50:  # Less than $50/hour
                        risk_score += 0.1
                        risk_factors.append("unusually low hourly rate")
                
                # Normalize risk score
                risk_score = min(1.0, risk_score)
                
                # Determine if flagged (threshold: 0.5)
                is_flagged = risk_score >= 0.5
                
                # Generate flag reason
                if is_flagged and risk_factors:
                    flag_reason = f"Deterministic: {'; '.join(risk_factors[:2])}"  # Limit to 2 main reasons
                elif is_flagged:
                    flag_reason = "Deterministic: Multiple risk factors"
                else:
                    flag_reason = "Deterministic: Normal billing pattern"
                
                results.append((risk_score, is_flagged, flag_reason))
                
            except Exception as e:
                logger.warning(f"Error scoring line: {e}")
                # Default to safe values on error
                results.append((0.1, False, "Error in scoring - marked as safe"))
        
        logger.info(f"📊 Deterministic scoring completed for {len(results)} lines")
        return results
    
    def score_lines(self, df: pd.DataFrame) -> Tuple[List[Tuple[float, bool, str]], Dict[str, Any]]:
        """
        Main scoring function - uses ML models if available, falls back to deterministic
        
        Args:
            df: DataFrame with invoice line data
        
        Returns:
            Tuple of (scoring_results, metadata)
            scoring_results: List of (risk_score, is_flagged, flag_reason) tuples
            metadata: Dictionary with scoring method info
        """
        if df is None or len(df) == 0:
            return [], {"method": "no_data", "note": "No lines to score"}
        
        # Metadata about scoring method
        metadata = {
            "method": "ml" if self.models_loaded else "deterministic",
            "models_loaded": self.models_loaded,
            "lines_scored": len(df)
        }
        
        try:
            if self.models_loaded and not self.fallback_mode:
                results = self._ml_score_lines(df)
                metadata["note"] = "ML models used successfully"
            else:
                results = self._deterministic_score_lines(df)
                metadata["note"] = "model_fallback"
                metadata["reason"] = "ML models not available - using deterministic scoring"
            
            return results, metadata
            
        except Exception as e:
            logger.error(f"Critical error in score_lines: {e}")
            # Emergency fallback
            emergency_results = [(0.1, False, f"Emergency fallback - error: {str(e)[:50]}...")] * len(df)
            metadata["note"] = "emergency_fallback"
            metadata["error"] = str(e)
            return emergency_results, metadata
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current status of loaded models"""
        return {
            "models_loaded": self.models_loaded,
            "fallback_mode": self.fallback_mode,
            "iso_forest_available": self.iso_forest_model is not None,
            "overspend_available": self.overspend_model is not None,
            "models_dir": str(self.models_dir),
            "models_dir_exists": self.models_dir.exists()
        }


# Global ML service instance
_ml_service = None

def get_ml_service() -> MLService:
    """Get the global ML service instance (singleton pattern)"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service

# Convenience function for direct use
def score_lines(df: pd.DataFrame) -> Tuple[List[Tuple[float, bool, str]], Dict[str, Any]]:
    """
    Score invoice lines using ML service
    
    Args:
        df: DataFrame with invoice line data
        
    Returns:
        Tuple of (scoring_results, metadata)
    """
    service = get_ml_service()
    return service.score_lines(df)

# Additional convenience functions
def get_model_status() -> Dict[str, Any]:
    """Get ML model loading status"""
    service = get_ml_service()
    return service.get_model_status()

def reload_models() -> bool:
    """Reload ML models from disk"""
    global _ml_service
    try:
        _ml_service = MLService()
        return _ml_service.models_loaded
    except Exception as e:
        logger.error(f"Failed to reload models: {e}")
        return False
