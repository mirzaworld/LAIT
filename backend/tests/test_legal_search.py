import json

def test_legal_search_requires_query(client):
    resp = client.post('/api/legal/search', json={})
    assert resp.status_code == 400


def test_legal_search_minimal_query(client, monkeypatch):
    # Patch collector to avoid real external calls
    from backend.enhanced_app import app as global_app
    collector = global_app.data_collector

    def fake_courtlistener(query, limit=20):
        return {'results': [{'id': 1, 'caseName': 'Test Case', 'court': {'name': 'Test Court', 'jurisdiction': 'Federal'}, 'dateFiled': '2024-01-01'}]}
    monkeypatch.setattr(collector, 'fetch_courtlistener_data', fake_courtlistener)
    monkeypatch.setattr(collector, 'search_justia_cases', lambda q: [])
    monkeypatch.setattr(collector, 'search_google_scholar_cases', lambda q: [])

    resp = client.post('/api/legal/search', json={'query': 'contract'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'cases' in data
    assert data['metadata']['total_results'] >= 1
