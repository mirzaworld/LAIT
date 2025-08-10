import json

def test_self_test_endpoint(client):
    resp = client.get('/api/self-test')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'status' in data
    assert 'checks' in data
    assert 'database' in data['checks']
    assert 'ml_models' in data['checks']
    assert 'realtime' in data['checks']
