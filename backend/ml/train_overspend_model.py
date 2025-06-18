import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from generate_synthetic_data import generate_synthetic_invoices

def train_overspend_model(invoices_df=None, line_items_df=None):
    """Train a model to predict potential overspend in matters."""
    
    if invoices_df is None or line_items_df is None:
        invoices_df, line_items_df = generate_synthetic_invoices(200)
    
    # Aggregate line items by invoice
    invoice_features = line_items_df.groupby('invoice_id').agg({
        'hours': ['sum', 'mean', 'std'],
        'rate': ['mean', 'std'],
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    # Flatten column names
    invoice_features.columns = ['invoice_id', 'total_hours', 'avg_hours', 'std_hours',
                              'avg_rate', 'std_rate', 'total_amount', 'avg_amount', 'n_items']
    
    # Merge with invoice data
    data = pd.merge(invoices_df, invoice_features, on='invoice_id', suffixes=('_inv', ''))
    
    # Create target variable (simulated overspend - could be based on historical averages in real data)
    data['baseline_expected'] = data['total_hours'] * data['avg_rate'] * 0.8  # 80% of actual as "expected"
    data['overspend_amount'] = data['total_amount'] - data['baseline_expected']
    data['is_overspend'] = data['overspend_amount'] > 0
    
    # Select features for prediction
    features = ['total_hours', 'avg_hours', 'std_hours', 'avg_rate', 'std_rate', 
               'n_items', 'baseline_expected']
    X = data[features]
    y = data['overspend_amount']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    print(f"Model trained successfully")
    print(f"Training R² score: {train_score:.3f}")
    print(f"Test R² score: {test_score:.3f}")
    
    # Save model and scaler
    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(model, 'ml/models/overspend_model.joblib')
    joblib.dump(scaler, 'ml/models/overspend_scaler.joblib')
    
    return model, scaler

def predict_overspend(invoice_data, line_items, model=None, scaler=None):
    """Predict potential overspend for new invoices."""
    if model is None or scaler is None:
        model = joblib.load('ml/models/overspend_model.joblib')
        scaler = joblib.load('ml/models/overspend_scaler.joblib')
    
    # Prepare features
    features = pd.DataFrame([{
        'total_hours': sum(item['hours'] for item in line_items),
        'avg_hours': np.mean([item['hours'] for item in line_items]),
        'std_hours': np.std([item['hours'] for item in line_items]),
        'avg_rate': np.mean([item['rate'] for item in line_items]),
        'std_rate': np.std([item['rate'] for item in line_items]),
        'n_items': len(line_items),
        'baseline_expected': sum(item['hours'] * item['rate'] * 0.8 for item in line_items)
    }])
    
    # Scale and predict
    X_scaled = scaler.transform(features)
    predicted_overspend = model.predict(X_scaled)[0]
    
    return predicted_overspend

if __name__ == "__main__":
    print("Training overspend prediction model...")
    model, scaler = train_overspend_model()
    print("Model saved to ml/models/overspend_model.joblib")
