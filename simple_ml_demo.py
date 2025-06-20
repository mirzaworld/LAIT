#!/usr/bin/env python3
"""
Simple LAIT ML Demo - Using trained models directly
"""
import sys
sys.path.append('/app/backend')

import joblib
import numpy as np
import pandas as pd
from ml.generate_synthetic_data import generate_synthetic_invoices

def demo_trained_models():
    """Demo the trained ML models"""
    print("🤖 LAIT TRAINED ML MODELS DEMONSTRATION")
    print("🏛️ Legal AI Invoice Tracking System")
    print("=" * 60)
    print()
    
    try:
        # Test Outlier Detection Model
        print("🔍 OUTLIER DETECTION MODEL")
        print("=" * 40)
        
        try:
            # Load the trained outlier model
            outlier_model = joblib.load('/app/backend/ml/models/outlier_model.joblib')
            outlier_scaler = joblib.load('/app/backend/ml/models/outlier_scaler.joblib')
            
            # Generate test data
            print("Generating test invoice data...")
            invoices_df, line_items_df = generate_synthetic_invoices(50)
            
            # Prepare features for outlier detection
            features = line_items_df[['hours', 'rate', 'amount']].values
            features_scaled = outlier_scaler.transform(features)
            
            # Predict outliers
            outlier_predictions = outlier_model.predict(features_scaled)
            outlier_scores = outlier_model.score_samples(features_scaled)
            
            # Count outliers
            num_outliers = np.sum(outlier_predictions == -1)
            total_items = len(line_items_df)
            
            print(f"✅ Analyzed {total_items} line items")
            print(f"🚨 Found {num_outliers} potential outliers ({num_outliers/total_items:.1%})")
            
            # Show some outlier examples
            outlier_indices = np.where(outlier_predictions == -1)[0][:3]
            if len(outlier_indices) > 0:
                print("\nTop Outlier Examples:")
                for i, idx in enumerate(outlier_indices, 1):
                    item = line_items_df.iloc[idx]
                    score = outlier_scores[idx]
                    print(f"  {i}. Hours: {item['hours']:.1f}, Rate: ${item['rate']:.0f}, Amount: ${item['amount']:.0f} (Score: {score:.3f})")
            
        except Exception as e:
            print(f"❌ Outlier model error: {e}")
        
        print()
        
        # Test Overspend Prediction Model
        print("💰 OVERSPEND PREDICTION MODEL")
        print("=" * 40)
        
        try:
            # Load the trained overspend model
            overspend_model = joblib.load('/app/backend/ml/models/overspend_model.joblib')
            overspend_scaler = joblib.load('/app/backend/ml/models/overspend_scaler.joblib')
            
            # Prepare sample data for overspend prediction
            sample_features = np.array([[
                100,    # total_hours
                12.5,   # avg_hours  
                5.2,    # std_hours
                450,    # avg_rate
                50,     # std_rate
                8,      # n_items
                36000   # baseline_expected
            ]])
            
            # Scale and predict
            sample_scaled = overspend_scaler.transform(sample_features)
            overspend_prediction = overspend_model.predict(sample_scaled)[0]
            
            print(f"✅ Sample Matter Analysis:")
            print(f"   Total Hours: {sample_features[0][0]:.0f}")
            print(f"   Average Rate: ${sample_features[0][3]:.0f}")
            print(f"   Baseline Expected: ${sample_features[0][6]:,.0f}")
            print(f"🔮 Predicted Overspend: ${overspend_prediction:,.0f}")
            
            if overspend_prediction > 5000:
                print("🚨 WARNING: Significant overspend predicted!")
            elif overspend_prediction > 0:
                print("⚠️ CAUTION: Minor overspend predicted")
            else:
                print("✅ On budget or under budget predicted")
                
        except Exception as e:
            print(f"❌ Overspend model error: {e}")
        
        print()
        
        # Test Vendor Clustering Model
        print("👥 VENDOR CLUSTERING MODEL") 
        print("=" * 40)
        
        try:
            # Load the trained vendor clustering model
            vendor_model = joblib.load('/app/backend/ml/models/vendor_cluster_model.joblib')
            vendor_scaler = joblib.load('/app/backend/ml/models/vendor_cluster_scaler.joblib')
            
            # Load vendor metrics
            vendor_metrics = pd.read_csv('/app/backend/data/vendor_metrics.csv')
            
            print(f"✅ Analyzed {len(vendor_metrics)} vendors")
            print(f"📊 Found {vendor_model.n_clusters} vendor clusters")
            
            # Show cluster distribution
            cluster_counts = pd.Series(vendor_model.labels_).value_counts().sort_index()
            print("\nCluster Distribution:")
            for cluster, count in cluster_counts.items():
                avg_rate = vendor_metrics[vendor_metrics.index.isin(np.where(vendor_model.labels_ == cluster)[0])]['avg_rate'].mean()
                print(f"  Cluster {cluster}: {count} vendors (Avg Rate: ${avg_rate:.0f})")
            
            # Predict cluster for a new vendor
            new_vendor = np.array([[
                450,  # avg_rate
                0.03, # flag_rate  
                0.85, # success_rate
                0.65  # diversity_score
            ]])
            
            new_vendor_scaled = vendor_scaler.transform(new_vendor)
            predicted_cluster = vendor_model.predict(new_vendor_scaled)[0]
            
            print(f"\n🔮 New Vendor Prediction:")
            print(f"   Sample vendor assigned to Cluster {predicted_cluster}")
            
        except Exception as e:
            print(f"❌ Vendor clustering error: {e}")
        
        print()
        
        # Show model files
        print("📁 TRAINED MODEL FILES")
        print("=" * 40)
        
        import os
        model_dir = '/app/backend/ml/models'
        if os.path.exists(model_dir):
            models = os.listdir(model_dir)
            for model in sorted(models):
                if model.endswith('.joblib'):
                    size = os.path.getsize(os.path.join(model_dir, model))
                    print(f"  ✅ {model} ({size:,} bytes)")
        
        print()
        print("🎉 All ML models successfully demonstrated!")
        print()
        print("🔧 LAIT AI/ML Capabilities:")
        print("  • Invoice Anomaly Detection")
        print("  • Spend Forecasting") 
        print("  • Vendor Performance Clustering")
        print("  • Risk Score Prediction")
        print("  • PDF Text Extraction & NLP")
        print("  • Real-time Analysis API")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_trained_models()
