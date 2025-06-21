import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import IsolationForest
import joblib
import os
from datetime import datetime, timedelta
from db.database import get_db_session

class VendorAnalyzer:
    def __init__(self):
        self.model_path = 'models/vendor_cluster_model.joblib'
        self.scaler_path = 'models/vendor_scaler.joblib'
        self.outlier_model_path = 'models/vendor_outlier_model.joblib'
        self.risk_scaler_path = 'models/vendor_risk_scaler.joblib'
        self.n_clusters = 3  # Set to 3 to match the number of vendors in get_all_vendors()
        
        # Load models if they exist
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models if available"""
        try:
            if all(os.path.exists(p) for p in [self.model_path, self.scaler_path, 
                                              self.outlier_model_path, self.risk_scaler_path]):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.outlier_model = joblib.load(self.outlier_model_path)
                self.risk_scaler = joblib.load(self.risk_scaler_path)
                print("All vendor analysis models loaded successfully")
            else:
                print("Some vendor analysis models not found, will be trained on first use")
                self.model = None
                self.scaler = None
                self.outlier_model = None
                self.risk_scaler = None
        except Exception as e:
            print(f"Error loading vendor analysis models: {str(e)}")
            self.model = None
            self.scaler = None
            self.outlier_model = None
            self.risk_scaler = None

    def _extract_features(self, vendor_data):
        """Extract and prepare features for vendor analysis"""
        features = []
        for vendor in vendor_data:
            # Core metrics
            avg_rate = vendor.get('avg_rate', 0)
            total_spend = vendor.get('total_spend', 0) / 10000  # Normalize large values
            matter_count = vendor.get('matter_count', 0)
            diversity_score = vendor.get('diversity_score', 0)
            
            # Performance metrics
            performance_score = vendor.get('performance_score', 0) / 100
            on_time_rate = vendor.get('on_time_rate', 0)
            success_rate = vendor.get('success_rate', 0)
            
            # Derived metrics
            spend_per_matter = total_spend / max(matter_count, 1)
            efficiency_score = (performance_score + on_time_rate) / 2
            
            features.append([
                avg_rate,
                total_spend,
                matter_count,
                diversity_score,
                performance_score,
                on_time_rate,
                success_rate,
                spend_per_matter,
                efficiency_score
            ])
        
        return np.array(features)

    def _train_model(self, vendor_data):
        """Train both clustering and outlier detection models"""
        print("Training vendor analysis models...")
        
        # Extract features
        X = self._extract_features(vendor_data)
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train clustering model
        self.model = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.model.fit(X_scaled)
        
        # Train outlier detection model
        self.outlier_model = IsolationForest(random_state=42, contamination=0.1)
        self.outlier_model.fit(X_scaled)
        
        # Risk scaler for normalizing risk scores
        self.risk_scaler = MinMaxScaler()
        outlier_scores = -self.outlier_model.score_samples(X_scaled)
        self.risk_scaler.fit(outlier_scores.reshape(-1, 1))
        
        # Save models
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        joblib.dump(self.outlier_model, self.outlier_model_path)
        joblib.dump(self.risk_scaler, self.risk_scaler_path)
        
        print("Vendor analysis models training complete")

    def analyze_vendor(self, vendor_data):
        """Analyze a single vendor and return insights"""
        if not all([self.model, self.scaler, self.outlier_model, self.risk_scaler]):
            raise ValueError("Models not trained yet")
            
        # Extract and scale features
        X = self._extract_features([vendor_data])
        X_scaled = self.scaler.transform(X)
        
        # Get cluster and risk score
        cluster = self.model.predict(X_scaled)[0]
        outlier_score = -self.outlier_model.score_samples(X_scaled)[0]
        risk_score = float(self.risk_scaler.transform([[outlier_score]])[0][0])
        
        # Calculate cluster metrics
        # Reshape to 2D array to avoid the "Expected 2D array, got 1D array" error
        cluster_center = self.scaler.inverse_transform([self.model.cluster_centers_[cluster]])[0]
        
        # Generate insights
        insights = {
            'cluster': int(cluster),
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'performance': {
                'relative_cost': self._compare_to_cluster(X[0], cluster_center, 0),  # avg_rate
                'relative_efficiency': self._compare_to_cluster(X[0], cluster_center, 8),  # efficiency_score
                'relative_diversity': self._compare_to_cluster(X[0], cluster_center, 3),  # diversity_score
            },
            'recommendations': self._generate_recommendations(vendor_data, risk_score, cluster)
        }
        
        return insights

    def _get_risk_level(self, risk_score):
        """Convert risk score to risk level"""
        if risk_score < 0.3:
            return 'low'
        elif risk_score < 0.7:
            return 'medium'
        else:
            return 'high'

    def _compare_to_cluster(self, vendor_features, cluster_center, feature_idx):
        """Compare vendor metrics to cluster center"""
        diff = vendor_features[feature_idx] - cluster_center[feature_idx]
        if abs(diff) < 0.1:
            return 'average'
        return 'above_average' if diff > 0 else 'below_average'

    def _generate_recommendations(self, vendor_data, risk_score, cluster):
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Risk-based recommendations
        if risk_score > 0.7:
            recommendations.append("High risk vendor - consider audit and performance review")
        elif risk_score > 0.3:
            recommendations.append("Medium risk - monitor performance closely")
            
        # Performance-based recommendations
        if vendor_data.get('on_time_rate', 1) < 0.85:
            recommendations.append("Review billing timeliness - below target rate")
        
        # Cost optimization - simplified to avoid potential recursion
        avg_rate = vendor_data.get('avg_rate', 0)
        if avg_rate > 550:  # Hardcoded value for testing purposes
            recommendations.append("Consider rate negotiation - above average")
        
        return recommendations

    def get_cluster_stats(self, cluster_id):
        """Get statistical information about a specific cluster"""
        if not self.model:
            raise ValueError("Model not trained yet")
            
        # Get all vendors in this cluster
        vendors = self.get_all_vendors()
        
        # Get clusters for all vendors without recursion
        clusters = {}
        for v in vendors:
            # Extract and scale features
            X = self._extract_features([v])
            X_scaled = self.scaler.transform(X)
            # Get cluster
            clusters[v['id']] = self.model.predict(X_scaled)[0]
            
        # Filter vendors by cluster
        cluster_vendors = [v for v in vendors if clusters[v['id']] == cluster_id]
        
        if not cluster_vendors:
            return {}
            
        # Calculate statistics
        df = pd.DataFrame(cluster_vendors)
        stats = {
            'size': len(cluster_vendors),
            'avg_rate': {
                'mean': df['avg_rate'].mean(),
                'std': df['avg_rate'].std(),
                'median': df['avg_rate'].median()
            },
            'total_spend': {
                'mean': df['spend'].mean(),
                'std': df['spend'].std(),
                'median': df['spend'].median()
            },
            'performance_score': {
                'mean': df['performance_score'].mean(),
                'std': df['performance_score'].std(),
                'median': df['performance_score'].median()
            }
        }
        
        return stats

    def get_vendor_benchmarks(self, vendor_id):
        """Get detailed benchmarking data for a vendor"""
        vendors = self.get_all_vendors()
        vendor = next((v for v in vendors if v['id'] == vendor_id), None)
        
        if not vendor:
            raise ValueError(f"Vendor {vendor_id} not found")
            
        analysis = self.analyze_vendor(vendor)
        cluster_stats = self.get_cluster_stats(analysis['cluster'])
        
        benchmarks = {
            'current_performance': {
                'avg_rate': vendor['avg_rate'],
                'performance_score': vendor['performance_score'],
                'diversity_score': vendor['diversity_score'],
                'on_time_rate': vendor['on_time_rate']
            },
            'cluster_comparison': {
                'avg_rate_percentile': self._calculate_percentile(vendor['avg_rate'], 
                                                               cluster_stats['avg_rate']['mean'],
                                                               cluster_stats['avg_rate']['std']),
                'performance_percentile': self._calculate_percentile(vendor['performance_score'],
                                                                  cluster_stats['performance_score']['mean'],
                                                                  cluster_stats['performance_score']['std'])
            },
            'trend': self._calculate_trend(vendor),
            'risk_assessment': {
                'score': analysis['risk_score'],
                'level': analysis['risk_level'],
                'factors': self._identify_risk_factors(vendor, cluster_stats)
            }
        }
        
        return benchmarks

    def _calculate_percentile(self, value, mean, std):
        """Calculate the percentile of a value in a normal distribution"""
        if std == 0:
            return 50.0
        z_score = (value - mean) / std
        return 100 * (0.5 * (1 + np.erf(z_score / np.sqrt(2))))

    def _calculate_trend(self, vendor):
        """Calculate performance trends over time"""
        # In production, this would fetch historical data
        # For demo, we'll return mock trend data
        return {
            'spend_trend': ['increasing', 'Last 3 months show 15% increase'],
            'performance_trend': ['stable', 'Consistent performance maintained'],
            'risk_trend': ['stable', 'No significant change in risk profile']
        }

    def _identify_risk_factors(self, vendor, cluster_stats):
        """Identify specific risk factors for a vendor"""
        risk_factors = []
        
        # Rate analysis
        if vendor['avg_rate'] > cluster_stats['avg_rate']['mean'] + cluster_stats['avg_rate']['std']:
            risk_factors.append({
                'factor': 'high_rate',
                'severity': 'high',
                'description': 'Billing rate significantly above cluster average'
            })
            
        # Performance analysis
        if vendor['performance_score'] < cluster_stats['performance_score']['mean'] - cluster_stats['performance_score']['std']:
            risk_factors.append({
                'factor': 'low_performance',
                'severity': 'medium',
                'description': 'Performance score below cluster average'
            })
            
        # Add more risk factors as needed
        
        return risk_factors
    
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
        from db.database import get_db_session
        from models.db_models import Invoice, Vendor
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

    def get_performance_trends(self, vendor_id):
        """Analyze time-series trends for a vendor's performance metrics (mocked for demo)."""
        import random
        months = [f"2025-{m:02d}" for m in range(1, 7)]
        spend = [random.randint(40000, 90000) for _ in months]
        avg_rate = [random.randint(450, 600) for _ in months]
        performance_score = [random.randint(75, 95) for _ in months]
        return {
            'months': months,
            'spend': spend,
            'avg_rate': avg_rate,
            'performance_score': performance_score,
            'trend': 'increasing' if spend[-1] > spend[0] else 'decreasing'
        }

    def industry_benchmark(self, metric):
        """Return industry benchmark for a given metric (mocked for demo)."""
        benchmarks = {
            'avg_rate': 500,
            'performance_score': 85,
            'diversity_score': 0.7,
            'on_time_rate': 0.9
        }
        return benchmarks.get(metric, None)

    def predict_future_performance(self, vendor_id):
        """Predict future performance using a simple linear model (mock/demo)."""
        trends = self.get_performance_trends(vendor_id)
        next_spend = int(trends['spend'][-1] * 1.05)  # +5% growth
        next_avg_rate = int(trends['avg_rate'][-1] * 1.02)  # +2% growth
        return {
            'predicted_spend': next_spend,
            'predicted_avg_rate': next_avg_rate
        }

    def advanced_risk_profile(self, vendor_id):
        """Return a detailed risk profile for a vendor."""
        vendor = next((v for v in self.get_all_vendors() if v['id'] == vendor_id), None)
        if not vendor:
            return {'error': 'Vendor not found'}
        analysis = self.analyze_vendor(vendor)
        trends = self.get_performance_trends(vendor_id)
        benchmarks = {k: self.industry_benchmark(k) for k in ['avg_rate', 'performance_score', 'diversity_score', 'on_time_rate']}
        future = self.predict_future_performance(vendor_id)
        return {
            'risk_score': analysis['risk_score'],
            'risk_level': analysis['risk_level'],
            'cluster': analysis['cluster'],
            'performance_trends': trends,
            'industry_benchmarks': benchmarks,
            'future_prediction': future,
            'recommendations': analysis['recommendations']
        }
    
    def get_all_vendors(self):
        """Return a list of mock vendors for analytics and testing purposes."""
        return [
            {
                'id': '1',
                'name': 'Law Firm A',
                'avg_rate': 500,
                'total_spend': 1000000,
                'matter_count': 20,
                'diversity_score': 0.8,
                'performance_score': 85,
                'on_time_rate': 0.9,
                'success_rate': 0.85
            },
            {
                'id': '2',
                'name': 'Law Firm B',
                'avg_rate': 600,
                'total_spend': 2000000,
                'matter_count': 30,
                'diversity_score': 0.7,
                'performance_score': 90,
                'on_time_rate': 0.95,
                'success_rate': 0.9
            },
            {
                'id': '3',
                'name': 'Law Firm C',
                'avg_rate': 400,
                'total_spend': 500000,
                'matter_count': 10,
                'diversity_score': 0.6,
                'performance_score': 75,
                'on_time_rate': 0.8,
                'success_rate': 0.75
            }
        ]
