#!/usr/bin/env python3
"""Train tiny deterministic ML models for local dev/test runs.

This produces small model files under ./models/ expected by the app:
- models/vendor_cluster_model.joblib
- models/vendor_scaler.joblib
- models/vendor_outlier_model.joblib
- models/vendor_risk_scaler.joblib

These are intentionally tiny and fast to train so the dev bootstrap can run quickly.
"""
import os
import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def train_and_save_models(out_dir='models'):
    ensure_dir(out_dir)

    # Small synthetic vendor features: total_spend, invoice_count, avg_rate
    X = np.array([
        [1000.0, 3, 200.0],
        [1500.0, 5, 150.0],
        [200.0, 1, 200.0],
        [5000.0, 10, 500.0],
        [300.0, 2, 150.0],
    ])

    # Scaler
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    # KMeans: choose clusters <= n_samples
    n_clusters = min(4, X.shape[0])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(Xs)

    # Isolation forest for outlier detection
    iso = IsolationForest(random_state=42, contamination=0.2)
    iso.fit(X)

    # risk scaler — simple StandardScaler on spend and rate
    risk_scaler = StandardScaler()
    risk_scaler.fit(X[:, [0, 2]])

    # Save
    joblib.dump(kmeans, os.path.join(out_dir, 'vendor_cluster_model.joblib'))
    joblib.dump(scaler, os.path.join(out_dir, 'vendor_scaler.joblib'))
    joblib.dump(iso, os.path.join(out_dir, 'vendor_outlier_model.joblib'))
    joblib.dump(risk_scaler, os.path.join(out_dir, 'vendor_risk_scaler.joblib'))

    print('Saved tiny models to', out_dir)


if __name__ == '__main__':
    train_and_save_models()
