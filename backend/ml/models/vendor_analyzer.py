"""
Vendor analysis and clustering model
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

class VendorAnalyzer:
    def __init__(self):
        self.clustering_model = KMeans(n_clusters=4, random_state=42)
        self.scaler = StandardScaler()
        self.vendor_features = {}
    
    def train(self, invoices: pd.DataFrame, line_items: pd.DataFrame) -> None:
        """Train the vendor analysis model"""
        # Calculate vendor metrics
        metrics = self.calculate_vendor_metrics(invoices, line_items)
        
        # Convert metrics to feature matrix
        features = []
        for vendor_id, vendor_metrics in metrics.items():
            feature_vector = [
                vendor_metrics['total_spend'],
                vendor_metrics['avg_rate'],
                vendor_metrics['efficiency_score'],
                vendor_metrics['quality_score']
            ]
            features.append(feature_vector)
        
        X = np.array(features)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train clustering model
        self.clustering_model.fit(X_scaled)
        
        # Store vendor features
        self.vendor_features = dict(zip(metrics.keys(), features))
    
    def cluster_vendors(self, invoices: pd.DataFrame) -> dict:
        """Assign vendors to clusters"""
        vendor_metrics = self.calculate_vendor_metrics(invoices)
        features = []
        vendor_ids = []
        
        for vendor_id, metrics in vendor_metrics.items():
            feature_vector = [
                metrics['total_spend'],
                metrics['avg_rate'],
                metrics['efficiency_score'],
                metrics['quality_score']
            ]
            features.append(feature_vector)
            vendor_ids.append(vendor_id)
        
        X = np.array(features)
        X_scaled = self.scaler.transform(X)
        clusters = self.clustering_model.predict(X_scaled)
        
        return dict(zip(vendor_ids, clusters))
    
    def calculate_vendor_metrics(self, invoices: pd.DataFrame, line_items: pd.DataFrame = None) -> dict:
        """Calculate performance metrics for each vendor"""
        metrics = {}
        
        # Group by vendor
        vendor_groups = invoices.groupby('vendor_id')
        
        for vendor_id, group in vendor_groups:
            vendor_metrics = {
                'total_spend': group['total_amount'].sum(),
                'invoice_count': len(group),
                'avg_invoice_amount': group['total_amount'].mean()
            }
            
            if line_items is not None:
                vendor_line_items = line_items[line_items['invoice_id'].isin(group.index)]
                vendor_metrics.update({
                    'avg_rate': vendor_line_items['rate'].mean(),
                    'efficiency_score': self._calculate_efficiency_score(vendor_line_items),
                    'quality_score': self._calculate_quality_score(group, vendor_line_items)
                })
            
            metrics[vendor_id] = vendor_metrics
        
        return metrics
    
    def _calculate_efficiency_score(self, line_items: pd.DataFrame) -> float:
        """Calculate vendor efficiency score"""
        if len(line_items) == 0:
            return 0.0
            
        # Based on hours distribution and rates
        hours_per_task = line_items.groupby('description')['hours'].mean()
        rate_consistency = 1 - line_items['rate'].std() / line_items['rate'].mean()
        
        return float(0.7 * (1 - hours_per_task.std() / hours_per_task.mean()) + 
                    0.3 * rate_consistency)
    
    def _calculate_quality_score(self, invoices: pd.DataFrame, line_items: pd.DataFrame) -> float:
        """Calculate vendor quality score"""
        if len(invoices) == 0:
            return 0.0
            
        # Based on various factors
        on_time_ratio = (invoices['status'] == 'paid').mean()
        detail_score = len(line_items) / len(invoices)  # Average line items per invoice
        
        return float(0.6 * on_time_ratio + 0.4 * min(detail_score / 10, 1))
    
    def get_vendor_recommendations(self, vendor_id: int) -> list:
        """Get recommendations for a vendor"""
        if vendor_id not in self.vendor_features:
            return []
            
        vendor_cluster = self.clustering_model.predict([self.vendor_features[vendor_id]])[0]
        recommendations = []
        
        # Find similar vendors
        for other_id, features in self.vendor_features.items():
            if other_id != vendor_id:
                other_cluster = self.clustering_model.predict([features])[0]
                if other_cluster == vendor_cluster:
                    recommendations.append({
                        'vendor_id': other_id,
                        'similarity_score': self._calculate_similarity(
                            self.vendor_features[vendor_id],
                            features
                        )
                    })
        
        return sorted(recommendations, key=lambda x: x['similarity_score'], reverse=True)
    
    def _calculate_similarity(self, features1: list, features2: list) -> float:
        """Calculate similarity between two vendors"""
        return float(1 / (1 + np.linalg.norm(np.array(features1) - np.array(features2))))
    
    def save_model(self, path: str) -> None:
        """Save model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'clustering_model': self.clustering_model,
            'scaler': self.scaler,
            'vendor_features': self.vendor_features
        }, path)
    
    def load_model(self, path: str) -> None:
        """Load model from disk"""
        data = joblib.load(path)
        self.clustering_model = data['clustering_model']
        self.scaler = data['scaler']
        self.vendor_features = data['vendor_features']
