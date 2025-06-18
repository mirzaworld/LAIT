import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

class VendorAnalyzer:
    def __init__(self):
        self.model_path = 'models/vendor_cluster_model.joblib'
        self.scaler_path = 'models/vendor_scaler.joblib'
        
        # Load model if exists
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if available"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print("Vendor analysis model loaded successfully")
            else:
                print("Vendor analysis model not found, will be trained on first use")
                self.model = None
                self.scaler = None
        except Exception as e:
            print(f"Error loading vendor analysis model: {str(e)}")
            self.model = None
            self.scaler = None
    
    def _train_model(self, vendor_data):
        """Train the vendor clustering model"""
        print("Training vendor clustering model...")
        
        # Extract features
        features = []
        for vendor in vendor_data:
            # Features: avg rate, total spend, matter count, diversity score
            features.append([
                vendor.get('avg_rate', 0),
                vendor.get('total_spend', 0) / 10000,  # Normalize large values
                vendor.get('matter_count', 0),
                vendor.get('diversity_score', 0) * 100  # Scale up small values
            ])
        
        # Convert to numpy array
        X = np.array(features)
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model (cluster vendors)
        self.model = KMeans(n_clusters=4, random_state=42)
        self.model.fit(X_scaled)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        print("Vendor clustering model training complete")
    
    def get_all_vendors(self):
        """Get all vendors with performance metrics"""
        # In production, this would fetch from database
        # For demo purposes, we're using mock data
        vendors = [
            {
                'id': '1',
                'name': 'Morrison & Foerster LLP',
                'category': 'IP Litigation',
                'spend': 847392,
                'matter_count': 23,
                'avg_rate': 525,
                'performance_score': 87,
                'diversity_score': 0.72,
                'on_time_rate': 0.95
            },
            {
                'id': '2',
                'name': 'Baker McKenzie',
                'category': 'Corporate',
                'spend': 623450,
                'matter_count': 18,
                'avg_rate': 475,
                'performance_score': 82,
                'diversity_score': 0.68,
                'on_time_rate': 0.88
            },
            {
                'id': '3',
                'name': 'Latham & Watkins',
                'category': 'M&A',
                'spend': 567800,
                'matter_count': 31,
                'avg_rate': 550,
                'performance_score': 91,
                'diversity_score': 0.75,
                'on_time_rate': 0.93
            },
            {
                'id': '4',
                'name': 'Skadden Arps',
                'category': 'Securities',
                'spend': 445600,
                'matter_count': 14,
                'avg_rate': 650,
                'performance_score': 89,
                'diversity_score': 0.65,
                'on_time_rate': 0.90
            },
            {
                'id': '5',
                'name': 'White & Case',
                'category': 'International',
                'spend': 398200,
                'matter_count': 19,
                'avg_rate': 510,
                'performance_score': 84,
                'diversity_score': 0.70,
                'on_time_rate': 0.85
            }
        ]
        
        return vendors
    
    def get_vendor_performance(self, vendor_id):
        """Get detailed performance metrics for a specific vendor"""
        # In production, this would fetch from database
        # For demo, we'll return mock data for a specific vendor
        
        # Get basic vendor info first
        vendors = self.get_all_vendors()
        vendor = next((v for v in vendors if v['id'] == vendor_id), None)
        
        if not vendor:
            return {'error': 'Vendor not found'}
        
        # Add detailed metrics
        performance = {
            'vendor': vendor,
            'metrics': {
                'billing_efficiency': 0.85,
                'budget_adherence': 0.92,
                'timekeeper_distribution': {
                    'partner': 0.25,
                    'senior_associate': 0.35,
                    'junior_associate': 0.30,
                    'paralegal': 0.10
                },
                'average_invoice_processing': 3.2,  # days
                'historical_rates': [
                    {'year': 2022, 'avg_rate': 490},
                    {'year': 2023, 'avg_rate': 510},
                    {'year': 2024, 'avg_rate': vendor['avg_rate']}
                ]
            },
            'comparison': {
                'rate_percentile': 75,  # percentile among peer firms
                'efficiency_percentile': 82,
                'diversity_percentile': 68
            },
            'recommendations': self._generate_vendor_recommendations(vendor)
        }
        
        return performance
    
    def analyze_vendor(self, vendor_data):
        """Analyze a vendor's performance and identify optimization opportunities"""
        # If model doesn't exist yet, train it
        if self.model is None:
            sample_data = self._get_sample_training_data()
            self._train_model(sample_data)
        
        # Extract features
        features = np.array([[
            vendor_data.get('avg_rate', 0),
            vendor_data.get('total_spend', 0) / 10000,
            vendor_data.get('matter_count', 0),
            vendor_data.get('diversity_score', 0) * 100
        ]])
        
        # Scale features
        X_scaled = self.scaler.transform(features)
        
        # Predict cluster
        cluster = self.model.predict(X_scaled)[0]
        
        # Map cluster to a named category
        vendor_tier = self._get_vendor_tier(cluster)
        
        analysis = {
            'vendor_id': vendor_data.get('id'),
            'tier': vendor_tier,
            'benchmarking': self._get_benchmarking_data(vendor_data),
            'optimization_opportunities': self._identify_optimization_opportunities(vendor_data)
        }
        
        return analysis
    
    def _get_vendor_tier(self, cluster):
        """Map cluster number to named tier"""
        tiers = {
            0: 'Premium',
            1: 'Standard',
            2: 'Economy',
            3: 'Specialized'
        }
        return tiers.get(cluster, 'Unknown')
    
    def _get_benchmarking_data(self, vendor):
        """Get benchmarking data comparing vendor to peers"""
        # In production, this would calculate real comparisons
        # For demo, we'll use mock data
        
        category = vendor.get('category', 'General')
        rate_diff = 0
        efficiency_diff = 0
        
        # Different benchmarks based on practice area
        if category == 'IP Litigation':
            benchmark_rate = 550
            benchmark_efficiency = 0.82
            rate_diff = vendor.get('avg_rate', 0) - benchmark_rate
            efficiency_diff = vendor.get('performance_score', 0) / 100 - benchmark_efficiency
        elif category == 'Corporate':
            benchmark_rate = 500
            benchmark_efficiency = 0.80
            rate_diff = vendor.get('avg_rate', 0) - benchmark_rate
            efficiency_diff = vendor.get('performance_score', 0) / 100 - benchmark_efficiency
        else:
            benchmark_rate = 525
            benchmark_efficiency = 0.81
            rate_diff = vendor.get('avg_rate', 0) - benchmark_rate
            efficiency_diff = vendor.get('performance_score', 0) / 100 - benchmark_efficiency
        
        return {
            'rate_comparison': {
                'vendor_rate': vendor.get('avg_rate', 0),
                'benchmark_rate': benchmark_rate,
                'difference': rate_diff,
                'difference_percent': round(rate_diff / benchmark_rate * 100, 1) if benchmark_rate else 0
            },
            'efficiency_comparison': {
                'vendor_efficiency': vendor.get('performance_score', 0) / 100,
                'benchmark_efficiency': benchmark_efficiency,
                'difference': efficiency_diff,
                'difference_percent': round(efficiency_diff / benchmark_efficiency * 100, 1) if benchmark_efficiency else 0
            }
        }
    
    def _identify_optimization_opportunities(self, vendor):
        """Identify opportunities to optimize spend with this vendor"""
        opportunities = []
        
        # Check rates
        if vendor.get('avg_rate', 0) > 500:
            opportunities.append({
                'type': 'rate_negotiation',
                'description': 'Consider rate negotiation based on volume of work',
                'potential_savings': '5-10%'
            })
        
        # Check timekeeper distribution
        if vendor.get('partner_percentage', 0) > 0.30:
            opportunities.append({
                'type': 'staffing_mix',
                'description': 'Partner heavy staffing - request more associate work',
                'potential_savings': '8-15%'
            })
        
        # Check matter concentration
        if vendor.get('matter_count', 0) < 5 and vendor.get('spend', 0) > 300000:
            opportunities.append({
                'type': 'volume_discount',
                'description': 'High spend on few matters - negotiate volume discount',
                'potential_savings': '7-12%'
            })
        
        return opportunities
    
    def _generate_vendor_recommendations(self, vendor):
        """Generate recommendations for vendor management"""
        recommendations = []
        
        # Rate recommendations
        if vendor.get('avg_rate', 0) > 600:
            recommendations.append({
                'category': 'cost',
                'text': 'Negotiate blended rates for routine matters'
            })
        
        # Performance recommendations
        if vendor.get('performance_score', 0) < 85:
            recommendations.append({
                'category': 'performance',
                'text': 'Schedule quarterly review of key performance metrics'
            })
        
        # Diversity recommendations
        if vendor.get('diversity_score', 0) < 0.7:
            recommendations.append({
                'category': 'diversity',
                'text': 'Request diversity staffing plan for new matters'
            })
        
        # Efficiency recommendations
        if vendor.get('on_time_rate', 0) < 0.9:
            recommendations.append({
                'category': 'efficiency',
                'text': 'Implement early billing notification system'
            })
        
        return recommendations
    
    def _get_sample_training_data(self):
        """Get sample data for initial model training"""
        # In production, this would come from historical vendor data
        # For demo, we're using synthetic data
        return [
            {
                'avg_rate': 550,
                'total_spend': 850000,
                'matter_count': 25,
                'diversity_score': 0.72
            },
            {
                'avg_rate': 475,
                'total_spend': 620000,
                'matter_count': 15,
                'diversity_score': 0.68
            },
            {
                'avg_rate': 525,
                'total_spend': 570000,
                'matter_count': 30,
                'diversity_score': 0.75
            },
            {
                'avg_rate': 650,
                'total_spend': 450000,
                'matter_count': 12,
                'diversity_score': 0.65
            },
            {
                'avg_rate': 500,
                'total_spend': 400000,
                'matter_count': 20,
                'diversity_score': 0.70
            },
            # More sample data would be included in a real system
        ]
    
    def retrain_model(self):
        """Retrain the vendor clustering model with all available data"""
        from db.database import get_db_session, Invoice, Vendor
        import pandas as pd
        from sqlalchemy import func
        
        session = get_db_session()
        try:
            # Get all vendors with their metrics
            vendors = session.query(Vendor).all()
            
            if len(vendors) < 5:  # Need at least a few vendors for clustering
                print("Not enough vendor data for clustering model training")
                return False
                
            # Gather features for each vendor
            features = []
            vendor_ids = []
            
            for vendor in vendors:
                # Get vendor's invoices
                invoices = session.query(Invoice).filter(Invoice.vendor_id == vendor.id).all()
                
                if not invoices:
                    continue
                    
                # Calculate metrics
                total_spend = sum(invoice.amount for invoice in invoices)
                matter_count = session.query(func.count(func.distinct(Invoice.matter_id)))\
                    .filter(Invoice.vendor_id == vendor.id).scalar() or 0
                
                avg_rate = 0
                if any(invoice.rate for invoice in invoices if invoice.rate):
                    rates = [invoice.rate for invoice in invoices if invoice.rate]
                    avg_rate = sum(rates) / len(rates)
                
                # Use risk_profile as diversity score if available or default value
                diversity_score = vendor.risk_profile if vendor.risk_profile is not None else 0.5
                
                # Extract features
                vendor_features = [
                    avg_rate,
                    total_spend / 10000,  # Normalize large values
                    matter_count,
                    diversity_score * 100  # Scale up small values
                ]
                
                features.append(vendor_features)
                vendor_ids.append(vendor.id)
            
            if len(features) < 5:
                print("Not enough complete vendor data for clustering")
                return False
                
            # Convert to numpy array
            X = np.array(features)
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Determine optimal number of clusters (between 2 and 6)
            from sklearn.metrics import silhouette_score
            
            best_score = -1
            optimal_clusters = 3  # Default
            
            for n_clusters in range(2, min(7, len(features))):
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(X_scaled)
                
                if len(set(cluster_labels)) > 1:  # Ensure we have at least 2 clusters
                    silhouette_avg = silhouette_score(X_scaled, cluster_labels)
                    print(f"Silhouette score for {n_clusters} clusters: {silhouette_avg}")
                    
                    if silhouette_avg > best_score:
                        best_score = silhouette_avg
                        optimal_clusters = n_clusters
            
            print(f"Selected optimal number of clusters: {optimal_clusters}")
            
            # Train model with optimal clusters
            self.model = KMeans(n_clusters=optimal_clusters, random_state=42)
            self.model.fit(X_scaled)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            print("Vendor clustering model successfully retrained")
            
            # Update vendor historical performance with cluster information
            cluster_labels = self.model.predict(X_scaled)
            
            # Calculate cluster characteristics for reporting
            cluster_profiles = {}
            for i in range(optimal_clusters):
                cluster_indices = [idx for idx, label in enumerate(cluster_labels) if label == i]
                if cluster_indices:
                    cluster_data = X[cluster_indices]
                    cluster_profiles[i] = {
                        'avg_rate': np.mean(cluster_data[:, 0]),
                        'avg_spend': np.mean(cluster_data[:, 1]) * 10000,  # De-normalize
                        'avg_matters': np.mean(cluster_data[:, 2]),
                        'avg_diversity': np.mean(cluster_data[:, 3]) / 100,  # De-normalize
                        'vendor_count': len(cluster_indices)
                    }
            
            # Update vendors with cluster information
            for idx, vendor_id in enumerate(vendor_ids):
                vendor = session.query(Vendor).filter(Vendor.id == vendor_id).first()
                if vendor:
                    cluster_label = int(cluster_labels[idx])
                    
                    # Create or update vendor historical performance
                    historical_performance = vendor.historical_performance or {}
                    historical_performance['cluster'] = cluster_label
                    historical_performance['cluster_profile'] = cluster_profiles.get(cluster_label, {})
                    
                    vendor.historical_performance = historical_performance
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error retraining vendor clustering model: {e}")
            return False
            
        finally:
            session.close()
