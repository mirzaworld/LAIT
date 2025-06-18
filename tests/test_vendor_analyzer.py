import pytest
import numpy as np
from backend.models.vendor_analyzer import VendorAnalyzer

@pytest.fixture
def sample_vendors():
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

@pytest.fixture
def analyzer():
    return VendorAnalyzer()

def test_vendor_analyzer_initialization(analyzer):
    assert analyzer is not None
    assert analyzer.n_clusters == 4

def test_feature_extraction(analyzer, sample_vendors):
    features = analyzer._extract_features(sample_vendors)
    assert features.shape == (3, 9)  # 3 vendors, 9 features
    assert not np.any(np.isnan(features))  # No NaN values

def test_model_training(analyzer, sample_vendors):
    analyzer._train_model(sample_vendors)
    assert analyzer.model is not None
    assert analyzer.scaler is not None
    assert analyzer.outlier_model is not None
    assert analyzer.risk_scaler is not None

def test_vendor_analysis(analyzer, sample_vendors):
    # Train models first
    analyzer._train_model(sample_vendors)
    
    # Analyze a vendor
    analysis = analyzer.analyze_vendor(sample_vendors[0])
    
    assert 'cluster' in analysis
    assert 'risk_score' in analysis
    assert 'risk_level' in analysis
    assert 'performance' in analysis
    assert 'recommendations' in analysis
    
    assert isinstance(analysis['cluster'], int)
    assert 0 <= analysis['risk_score'] <= 1
    assert analysis['risk_level'] in ['low', 'medium', 'high']

def test_cluster_stats(analyzer, sample_vendors):
    # Train models first
    analyzer._train_model(sample_vendors)
    
    # Get cluster stats
    stats = analyzer.get_cluster_stats(0)  # Test first cluster
    
    assert 'size' in stats
    assert 'avg_rate' in stats
    assert 'total_spend' in stats
    assert 'performance_score' in stats
    
    assert isinstance(stats['size'], int)
    assert all(key in stats['avg_rate'] for key in ['mean', 'std', 'median'])

def test_vendor_benchmarks(analyzer, sample_vendors):
    # Train models first
    analyzer._train_model(sample_vendors)
    
    # Get benchmarks for a vendor
    benchmarks = analyzer.get_vendor_benchmarks('1')
    
    assert 'current_performance' in benchmarks
    assert 'cluster_comparison' in benchmarks
    assert 'trend' in benchmarks
    assert 'risk_assessment' in benchmarks
    
    performance = benchmarks['current_performance']
    assert all(key in performance for key in ['avg_rate', 'performance_score', 'diversity_score', 'on_time_rate'])

def test_risk_factors(analyzer, sample_vendors):
    # Train models first
    analyzer._train_model(sample_vendors)
    
    # Get cluster stats
    cluster_stats = analyzer.get_cluster_stats(0)
    
    # Test risk factor identification
    risk_factors = analyzer._identify_risk_factors(sample_vendors[0], cluster_stats)
    
    assert isinstance(risk_factors, list)
    for factor in risk_factors:
        assert all(key in factor for key in ['factor', 'severity', 'description'])
        assert factor['severity'] in ['low', 'medium', 'high']

def test_invalid_vendor_id(analyzer, sample_vendors):
    # Train models first
    analyzer._train_model(sample_vendors)
    
    # Test invalid vendor ID
    with pytest.raises(ValueError):
        analyzer.get_vendor_benchmarks('invalid_id')
