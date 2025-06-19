import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
from generate_synthetic_data import generate_synthetic_invoices

def train_vendor_cluster_model(invoices_df=None, line_items_df=None):
    """Train a clustering model to group vendors by performance metrics."""
    
    if invoices_df is None or line_items_df is None:
        invoices_df, line_items_df = generate_synthetic_invoices(200)
    
    # Merge invoice and line item data to get vendor info
    merged_data = pd.merge(line_items_df, invoices_df[['invoice_id', 'vendor_id', 'vendor_name']], on='invoice_id')
    
    # Aggregate metrics by vendor
    vendor_metrics = merged_data.groupby('vendor_id').agg({
        'rate': ['mean', 'std'],
        'hours': ['sum', 'mean'],
        'amount': ['sum', 'mean'],
        'is_flagged': 'mean'  # Proportion of flagged items
    }).reset_index()
    
    # Flatten column names
    vendor_metrics.columns = ['vendor_id', 'avg_rate', 'std_rate', 'total_hours', 
                            'avg_hours', 'total_amount', 'avg_amount', 'flag_rate']
    
    # Add invoice count
    invoice_counts = invoices_df['vendor_id'].value_counts().reset_index()
    invoice_counts.columns = ['vendor_id', 'invoice_count']
    vendor_metrics = pd.merge(vendor_metrics, invoice_counts, on='vendor_id')
    
    # Create synthetic success rate and diversity score (in real app, these would come from external data)
    np.random.seed(42)
    vendor_metrics['success_rate'] = np.random.uniform(0.6, 1.0, size=len(vendor_metrics))
    vendor_metrics['diversity_score'] = np.random.uniform(0.3, 0.9, size=len(vendor_metrics))
    
    # Select features for clustering
    features = ['avg_rate', 'flag_rate', 'success_rate', 'diversity_score']
    X = vendor_metrics[features]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train KMeans
    n_clusters = min(3, len(X))  # Use 3 clusters or less if we have fewer vendors
    model = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = model.fit_predict(X_scaled)
    
    # Add clusters to vendor metrics
    vendor_metrics['cluster'] = clusters
    
    # Print cluster characteristics
    print("\nCluster Characteristics:")
    for cluster in range(n_clusters):
        cluster_data = vendor_metrics[vendor_metrics['cluster'] == cluster]
        print(f"\nCluster {cluster}:")
        print(f"Number of vendors: {len(cluster_data)}")
        print(f"Average rate: ${cluster_data['avg_rate'].mean():.2f}")
        print(f"Average success rate: {cluster_data['success_rate'].mean():.2%}")
        print(f"Average diversity score: {cluster_data['diversity_score'].mean():.2f}")
    
    # Save model and scaler
    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(model, 'ml/models/vendor_cluster_model.joblib')
    joblib.dump(scaler, 'ml/models/vendor_cluster_scaler.joblib')
    
    return model, scaler, vendor_metrics

def predict_vendor_cluster(vendor_metrics, model=None, scaler=None):
    """Predict cluster for new vendor data."""
    if model is None or scaler is None:
        model = joblib.load('ml/models/vendor_cluster_model.joblib')
        scaler = joblib.load('ml/models/vendor_cluster_scaler.joblib')
    
    features = ['avg_rate', 'flag_rate', 'success_rate', 'diversity_score']
    X = pd.DataFrame([vendor_metrics])[features]
    X_scaled = scaler.transform(X)
    cluster = model.predict(X_scaled)[0]
    
    return cluster

if __name__ == "__main__":
    print("Training vendor clustering model...")
    model, scaler, vendor_metrics = train_vendor_cluster_model()
    print("Model saved to ml/models/vendor_cluster_model.joblib")
    
    # Save vendor metrics for reference
    vendor_metrics.to_csv('data/vendor_metrics.csv', index=False)
    print("Vendor metrics saved to data/vendor_metrics.csv")
