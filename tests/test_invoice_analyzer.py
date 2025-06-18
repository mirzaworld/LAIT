import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from backend.models.invoice_analyzer import InvoiceAnalyzer

@pytest.fixture
def sample_line_items():
    return [
        {
            'id': 1,
            'description': 'Legal research regarding contract terms',
            'hours': 5.0,
            'rate': 300.0,
            'task_code': 'L110'
        },
        {
            'id': 2,
            'description': 'Multiple tasks including research, drafting and client calls',
            'hours': 8.0,
            'rate': 400.0,
            'task_code': 'L120'
        },
        {
            'id': 3,
            'description': 'Review',  # Intentionally vague
            'hours': 2.0,
            'rate': 350.0,
            'task_code': 'L110'
        },
        {
            'id': 4,
            'description': 'Draft motion for summary judgment',
            'hours': 12.0,  # Unusually high hours
            'rate': 600.0,  # Unusually high rate
            'task_code': 'L130'
        }
    ]

@pytest.fixture
def sample_invoice():
    return {
        'id': 1,
        'vendor_id': 1,
        'matter_id': 1,
        'amount': 8000.0,
        'date': datetime.now(),
        'line_items': sample_line_items()
    }

@pytest.fixture
def analyzer():
    return InvoiceAnalyzer()

def test_initialize_analyzer(analyzer):
    assert analyzer is not None
    assert hasattr(analyzer, 'isolation_forest')
    assert hasattr(analyzer, 'vectorizer')
    assert hasattr(analyzer, 'scaler')

def test_analyze_line_items(analyzer, sample_line_items):
    results = analyzer._analyze_line_items(sample_line_items)
    
    assert len(results) == len(sample_line_items)
    for result in results:
        assert 'risk_score' in result
        assert 'anomalies' in result
        assert 'recommendations' in result
        
        assert isinstance(result['risk_score'], float)
        assert 0 <= result['risk_score'] <= 1
        assert isinstance(result['anomalies'], list)

def test_detect_rate_anomalies(analyzer):
    df = pd.DataFrame({
        'rate': [300, 350, 400, 800]  # 800 is an anomaly
    })
    
    anomalies = analyzer._detect_rate_anomalies(df)
    assert len(anomalies) == 4
    assert anomalies[-1]  # Last rate should be flagged
    assert not anomalies[0]  # First rate should not be flagged

def test_detect_hours_anomalies(analyzer):
    df = pd.DataFrame({
        'hours': [2, 4, 6, 20]  # 20 is an anomaly
    })
    
    anomalies = analyzer._detect_hours_anomalies(df)
    assert len(anomalies) == 4
    assert anomalies[-1]  # Last hours should be flagged
    assert not anomalies[0]  # First hours should not be flagged

def test_analyze_descriptions(analyzer):
    descriptions = [
        'Legal research regarding contract terms',  # Normal
        'Various matters and miscellaneous tasks',  # Vague
        'Rev',  # Too brief
        'Multiple tasks including research, drafting, and client communications'  # Block billing
    ]
    
    results = analyzer._analyze_descriptions(descriptions)
    
    assert len(results) == 4
    assert not results[0]['is_suspicious']  # First description is normal
    assert results[1]['is_suspicious']  # Second description is vague
    assert results[2]['is_suspicious']  # Third description is too brief
    assert results[3]['is_suspicious']  # Fourth description shows block billing

def test_extract_numeric_features(analyzer, sample_line_items):
    df = pd.DataFrame(sample_line_items)
    features = analyzer._extract_numeric_features(df)
    
    assert isinstance(features, np.ndarray)
    assert features.shape[0] == len(sample_line_items)
    assert features.shape[1] >= 3  # Should have at least hours, rate, and total

def test_get_line_item_recommendations(analyzer):
    anomalies = [
        {'type': 'high_rate', 'severity': 'high'},
        {'type': 'suspicious_description', 'severity': 'medium'}
    ]
    
    recommendations = analyzer._get_line_item_recommendations(anomalies)
    
    assert len(recommendations) == 2
    assert all('action' in rec and 'message' in rec for rec in recommendations)
    
    actions = [rec['action'] for rec in recommendations]
    assert 'review_rate' in actions
    assert 'improve_description' in actions

def test_invoice_analysis_with_historical_data(analyzer, sample_invoice, monkeypatch):
    # Mock the database session
    class MockSession:
        def query(self, _):
            return self
            
        def filter(self, *args):
            return self
            
        def all(self):
            # Return some mock historical invoices
            class MockInvoice:
                def __init__(self, amount, date):
                    self.amount = amount
                    self.date = date
                    self.line_items = [
                        type('LineItem', (), {'rate': 300, 'hours': 5})(),
                        type('LineItem', (), {'rate': 350, 'hours': 4})()
                    ]
            
            return [
                MockInvoice(7000, datetime.now() - timedelta(days=60)),
                MockInvoice(7500, datetime.now() - timedelta(days=30)),
                MockInvoice(8000, datetime.now())
            ]
            
        def close(self):
            pass
    
    monkeypatch.setattr('backend.models.invoice_analyzer.get_db_session',
                        lambda: MockSession())
    
    # Prepare test data
    processed_data = {
        'vendor_id': 1,
        'matter_id': 1,
        'total_amount': 8000.0,
        'avg_rate': 350.0,
        'total_hours': 20.0
    }
    
    # Test historical comparison
    comparison = analyzer._compare_with_historical(processed_data, MockSession())
    
    assert comparison['comparison_available']
    assert 'rates' in comparison
    assert 'hours' in comparison
    assert 'total' in comparison
    assert 'trend' in comparison
    
    # Verify trend analysis
    trend = comparison['trend']
    assert 'duration_months' in trend
    assert 'monthly_change_pct' in trend
    assert 'direction' in trend
    assert 'significant' in trend

def test_analyze_trends(analyzer):
    class MockInvoice:
        def __init__(self, amount, date):
            self.amount = amount
            self.date = date
    
    historical_invoices = [
        MockInvoice(5000, datetime.now() - timedelta(days=90)),
        MockInvoice(6000, datetime.now() - timedelta(days=60)),
        MockInvoice(7000, datetime.now() - timedelta(days=30)),
        MockInvoice(8000, datetime.now())
    ]
    
    trend = analyzer._analyze_trends(historical_invoices)
    
    assert trend is not None
    assert 'duration_months' in trend
    assert 'monthly_change_pct' in trend
    assert 'direction' in trend
    assert 'significant' in trend
    assert trend['direction'] == 'increasing'  # Should be increasing in this case
