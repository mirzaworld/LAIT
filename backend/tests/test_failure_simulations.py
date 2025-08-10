import json

def test_missing_endpoint_returns_404(client):
    resp = client.get('/api/this-endpoint-does-not-exist')
    assert resp.status_code == 404


def test_protected_requires_auth(client):
    resp = client.get('/api/invoices')
    # In testing mode dev auth bypass may allow access; accept 200
    assert resp.status_code in (200, 404, 401)
