import json
from io import BytesIO

def test_invoice_upload_flow(client, monkeypatch):
    # Register & login to get token
    reg = client.post('/api/auth/register', json={'email':'invtester@example.com','password':'StrongPass123'})
    token = reg.get_json()['token']

    # Patch analyzer to deterministic output
    from enhanced_app import app as global_app
    class DummyAnalyzer:
        def analyze_invoice(self, data):
            return {'risk_score': 42}
    global_app.invoice_analyzer = DummyAnalyzer()

    data = {
        'file': (BytesIO(b'%PDF-1.4 test'), 'invoice.pdf'),
        'amount': '1500',
        'vendor': 'Test Vendor',
        'description': 'Test invoice upload'
    }
    resp = client.post('/api/upload-invoice', data=data, headers={'Authorization': f'Bearer {token}'}, content_type='multipart/form-data')
    assert resp.status_code in (200,201)
    payload = resp.get_json()
    assert 'id' in payload or 'invoice_id' in payload
