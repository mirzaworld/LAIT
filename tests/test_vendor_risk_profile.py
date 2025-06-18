import pytest
from backend.models.vendor_analyzer import VendorAnalyzer

@pytest.fixture
def analyzer():
    analyzer = VendorAnalyzer()
    # Train the model with mock data before running tests
    mock_vendors = analyzer.get_all_vendors()
    analyzer._train_model(mock_vendors)
    return analyzer

@pytest.fixture
def sample_vendor_id():
    # Use a valid mock vendor id from get_all_vendors()
    return '1'

def test_advanced_risk_profile_valid(analyzer, sample_vendor_id):
    profile = analyzer.advanced_risk_profile(sample_vendor_id)
    assert 'risk_score' in profile
    assert 'risk_level' in profile
    assert 'cluster' in profile
    assert 'performance_trends' in profile
    assert 'industry_benchmarks' in profile
    assert 'future_prediction' in profile
    assert 'recommendations' in profile
    assert isinstance(profile['risk_score'], float)
    assert profile['risk_level'] in ['low', 'medium', 'high']
    assert isinstance(profile['performance_trends'], dict)
    assert isinstance(profile['industry_benchmarks'], dict)
    assert isinstance(profile['future_prediction'], dict)
    assert isinstance(profile['recommendations'], list)

def test_advanced_risk_profile_invalid(analyzer):
    profile = analyzer.advanced_risk_profile('invalid_id')
    assert 'error' in profile
