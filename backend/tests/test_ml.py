"""Test ML model training and predictions."""
import pytest
import numpy as np
from datetime import datetime
import pandas as pd
from sklearn.ensemble import IsolationForest

from ml.models.invoice_analyzer import InvoiceAnalyzer
from ml.models.risk_predictor import RiskPredictor
from ml.models.vendor_analyzer import VendorAnalyzer
from ml.model_manager import ModelManager

@pytest.fixture
def sample_invoice_data():
    """Generate sample invoice data for testing."""
    return pd.DataFrame({
        'hours': [5.0, 8.0, 50.0, 3.0, 4.0],  # 50.0 is an obvious outlier
        'rate': [300.0, 350.0, 400.0, 300.0, 325.0],
        'line_total': [1500.0, 2800.0, 20000.0, 900.0, 1300.0]
    })

@pytest.fixture
def sample_vendor_data():
    """Generate sample vendor data for testing."""
    return pd.DataFrame({
        'average_rate': [300.0, 500.0, 400.0, 450.0, 350.0],
        'diversity_score': [75, 85, 60, 90, 70],
        'success_rate': [0.8, 0.9, 0.75, 0.85, 0.8],
        'total_spend': [100000.0, 500000.0, 300000.0, 400000.0, 200000.0]
    })

def test_outlier_detection(sample_invoice_data):
    """Test that the outlier detection model correctly identifies anomalies."""
    analyzer = InvoiceAnalyzer()
    analyzer.train(sample_invoice_data)
    
    # Test prediction on a normal entry
    normal_entry = np.array([[4.0, 300.0, 1200.0]])
    assert analyzer.predict(normal_entry)[0] == 1  # 1 means inlier
    
    # Test prediction on an obvious outlier
    outlier_entry = np.array([[100.0, 1000.0, 100000.0]])
    assert analyzer.predict(outlier_entry)[0] == -1  # -1 means outlier

def test_risk_prediction(sample_invoice_data):
    """Test the overspend risk prediction model."""
    predictor = RiskPredictor()
    # Add target column for training
    data = sample_invoice_data.copy()
    data['overspend'] = data['line_total'].apply(lambda x: 1 if x > 5000 else 0)
    
    predictor.train(data, target='overspend')
    
    # Test prediction on a low-risk entry
    low_risk = np.array([[4.0, 300.0, 1200.0]])
    assert predictor.predict_proba(low_risk)[0][1] < 0.5
    
    # Test prediction on a high-risk entry
    high_risk = np.array([[20.0, 500.0, 10000.0]])
    assert predictor.predict_proba(high_risk)[0][1] > 0.5

def test_vendor_clustering(sample_vendor_data):
    """Test vendor clustering model."""
    analyzer = VendorAnalyzer()
    analyzer.train(sample_vendor_data)
    
    # Test that we get the expected number of clusters
    n_clusters = len(set(analyzer.predict(sample_vendor_data)))
    assert 2 <= n_clusters <= 5  # We expect 2-5 clusters of vendors

def test_model_versioning(tmp_path):
    """Test model versioning system."""
    model_dir = tmp_path / "models"
    manager = ModelManager(str(model_dir))
    
    # Create and save a simple model
    model = IsolationForest()
    metrics = {'accuracy': 0.95, 'precision': 0.92}
    
    # Save the model
    version_id = manager.save_model(
        model=model,
        model_type='outlier_detector',
        metrics=metrics
    )
    
    # Verify we can load it back
    loaded_model = manager.load_model('outlier_detector')
    assert isinstance(loaded_model, IsolationForest)
    
    # Check metrics are stored correctly
    stored_metrics = manager.get_model_metrics('outlier_detector')
    assert stored_metrics == metrics

def test_model_evaluation(sample_invoice_data):
    """Test model evaluation metrics."""
    analyzer = InvoiceAnalyzer()
    
    # Split data into train/test
    train_data = sample_invoice_data.iloc[:-1]
    test_data = sample_invoice_data.iloc[-1:]
    
    # Train and evaluate
    analyzer.train(train_data)
    metrics = analyzer.evaluate(test_data)
    
    # Check that we have the expected metrics
    assert 'anomaly_ratio' in metrics
    assert isinstance(metrics['anomaly_ratio'], float)
    assert 0 <= metrics['anomaly_ratio'] <= 1
