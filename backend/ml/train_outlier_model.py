import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from generate_synthetic_data import generate_synthetic_invoices

def train_outlier_model(line_items_df=None):
    """Train an Isolation Forest model for detecting anomalous line items."""
    
    if line_items_df is None:
        # Generate synthetic data if not provided
        _, line_items_df = generate_synthetic_invoices(200)
    
    # Select features for outlier detection
    features = ['hours', 'rate', 'amount']
    X = line_items_df[features].values
    
    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train the Isolation Forest
    model = IsolationForest(
        contamination=0.05,  # Expect about 5% anomalies
        random_state=42,
        n_estimators=100
    )
    
    model.fit(X_scaled)
    
    # Save the model and scaler
    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(model, 'ml/models/outlier_model.joblib')
    joblib.dump(scaler, 'ml/models/outlier_scaler.joblib')
    
    # Test the model
    predictions = model.predict(X_scaled)
    anomaly_scores = model.score_samples(X_scaled)
    
    # Add predictions to the DataFrame for analysis
    line_items_df['predicted_anomaly'] = predictions == -1
    line_items_df['anomaly_score'] = anomaly_scores
    
    # Print some statistics
    n_anomalies = sum(predictions == -1)
    print(f"Model trained successfully.")
    print(f"Detected {n_anomalies} anomalies out of {len(line_items_df)} line items ({n_anomalies/len(line_items_df)*100:.1f}%)")
    
    # Calculate accuracy against synthetic labels (if available)
    if 'is_flagged' in line_items_df.columns:
        accuracy = sum((predictions == -1) == line_items_df['is_flagged']) / len(line_items_df)
        print(f"Accuracy against synthetic labels: {accuracy*100:.1f}%")
    
    return model, scaler

def predict_anomalies(line_items, model=None, scaler=None):
    """Predict anomalies for new line items."""
    if model is None or scaler is None:
        model = joblib.load('ml/models/outlier_model.joblib')
        scaler = joblib.load('ml/models/outlier_scaler.joblib')
    
    # Extract features
    features = ['hours', 'rate', 'amount']
    X = pd.DataFrame(line_items)[features].values
    
    # Scale and predict
    X_scaled = scaler.transform(X)
    predictions = model.predict(X_scaled)
    scores = model.score_samples(X_scaled)
    
    return predictions == -1, scores

if __name__ == "__main__":
    print("Training outlier detection model...")
    model, scaler = train_outlier_model()
    print("Model saved to ml/models/outlier_model.joblib")
