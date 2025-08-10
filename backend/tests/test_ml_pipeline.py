"""
Test suite for the ML pipeline components
"""
import pytest
import pandas as pd
import numpy as np

from ml.generate_synthetic_data import generate_synthetic_invoices
from ml.models.outlier_detector import OutlierDetector
from models.risk_predictor import RiskPredictor
from models.vendor_analyzer import VendorAnalyzer

@pytest.fixture
def synthetic_data():
    """Generate synthetic data for testing"""
    return generate_synthetic_invoices(n_invoices=50)

@pytest.mark.ml
def test_synthetic_data_generation():
    """Test synthetic data generation"""
    invoices, line_items = generate_synthetic_invoices(n_invoices=10)
    
    # Test invoice data
    assert isinstance(invoices, pd.DataFrame)
    assert len(invoices) == 10
    assert all(col in invoices.columns for col in [
        'invoice_id', 'vendor_name', 'total_amount', 'date', 'status'
    ])
    
    # Test line items data
    assert isinstance(line_items, pd.DataFrame)
    assert len(line_items) >= 30  # At least 3 line items per invoice
    assert all(col in line_items.columns for col in [
        'line_item_id', 'invoice_id', 'description', 'hours', 'rate', 'amount'
    ])

@pytest.mark.ml
def test_outlier_detection(synthetic_data):
    """Test outlier detection model"""
    invoices, line_items = synthetic_data
    detector = OutlierDetector()
    
    # Train the model
    detector.train(line_items)
    
    # Test prediction
    predictions = detector.predict(line_items)
    assert len(predictions) == len(line_items)
    assert all(isinstance(x, bool) for x in predictions)
    
    # Test anomaly scores
    scores = detector.get_anomaly_scores(line_items)
    assert len(scores) == len(line_items)
    assert all(isinstance(x, float) for x in scores)

@pytest.mark.ml
def test_risk_prediction(synthetic_data):
    """Test risk prediction model"""
    invoices, line_items = synthetic_data
    predictor = RiskPredictor()
    
    # Train the model
    predictor.train(invoices, line_items)
    
    # Test prediction
    new_invoice = invoices.iloc[0:1]
    risk_score = predictor.predict(new_invoice)
    assert isinstance(risk_score, float)
    assert 0 <= risk_score <= 1
    
    # Test risk factors
    risk_factors = predictor.explain_risk(new_invoice)
    assert isinstance(risk_factors, list)
    assert all(isinstance(x, dict) for x in risk_factors)

@pytest.mark.ml
def test_vendor_analysis(synthetic_data):
    """Test vendor analysis"""
    invoices, line_items = synthetic_data
    analyzer = VendorAnalyzer()
    
    # Train the model
    analyzer.train(invoices, line_items)
    
    # Test clustering
    clusters = analyzer.cluster_vendors(invoices)
    assert isinstance(clusters, dict)
    assert all(isinstance(v, int) for v in clusters.values())
    
    # Test performance metrics
    metrics = analyzer.calculate_vendor_metrics(invoices, line_items)
    assert isinstance(metrics, dict)
    assert all(isinstance(v, dict) for v in metrics.values())
    
@pytest.mark.ml
def test_data_validation(synthetic_data):
    """Test data validation functions"""
    invoices, line_items = synthetic_data
    
    # Test invoice validation
    assert all(invoices['total_amount'] >= 0)
    assert all(pd.to_datetime(invoices['date']))
    assert all(invoices['status'].isin(['paid', 'pending']))
    
    # Test line items validation
    assert all(line_items['hours'] > 0)
    assert all(line_items['rate'] > 0)
    assert all(abs(line_items['amount'] - line_items['hours'] * line_items['rate']) < 0.01)

@pytest.mark.ml
def test_edge_cases():
    """Test edge cases and error handling"""
    # Test with empty data
    with pytest.raises(ValueError):
        generate_synthetic_invoices(n_invoices=0)
    
    # Test with negative values
    with pytest.raises(ValueError):
        generate_synthetic_invoices(n_invoices=-1)
    
    # Test outlier detection with empty data
    from ml.models.outlier_detector import OutlierDetector as OD
    detector = OD()
    import pandas as pd
    with pytest.raises(ValueError):
        detector.train(pd.DataFrame())
