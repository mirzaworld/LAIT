import time
import json
import pytest


def _auth_headers(client):
    # Register & login to get token
    reg = client.post('/api/auth/register', json={'email': 'notif@example.com', 'password': 'Password123', 'first_name': 'N', 'last_name': 'U'})
    assert reg.status_code in (200, 201)
    token = reg.get_json()['token']
    return {'Authorization': f'Bearer {token}'}


def test_notifications_auth_required(client):
    r = client.get('/api/notifications')
    assert r.status_code in (401, 422)  # missing auth


def test_notification_ack_flow(client):
    headers = _auth_headers(client)
    # Create test notifications
    create = client.post('/api/notifications/test', headers=headers)
    assert create.status_code == 200
    created = create.get_json()['created']
    assert len(created) >= 1

    # Unread count
    unread_resp = client.get('/api/notifications/unread-count', headers=headers)
    assert unread_resp.status_code == 200
    unread_initial = unread_resp.get_json()['unread']
    assert unread_initial >= 1

    # Ack first notification
    first_id = created[0]['id']
    ack1 = client.post(f'/api/notifications/{first_id}/ack', headers=headers)
    assert ack1.status_code == 200
    data1 = ack1.get_json()
    assert data1['success'] is True
    unread_after = data1['unread']
    assert unread_after == unread_initial - 1

    # Re-ack idempotent
    ack2 = client.post(f'/api/notifications/{first_id}/ack', headers=headers)
    assert ack2.status_code == 200
    data2 = ack2.get_json()
    assert data2['unread'] == unread_after

    # Mark all read
    mar = client.post('/api/notifications/read-all', headers=headers)
    assert mar.status_code == 200
    unread_final = client.get('/api/notifications/unread-count', headers=headers).get_json()['unread']
    assert unread_final == 0


def test_notification_rate_limit_ack(client, monkeypatch):
    headers = _auth_headers(client)
    # Ensure at least one notification exists
    client.post('/api/notifications/test', headers=headers)
    notif_id = client.get('/api/notifications', headers=headers).get_json()[0]['id']

    # Temporarily monkeypatch rate limit for faster test
    from routes import notification as notif_module
    notif_module.RATE_LIMITS['notifications_ack'] = (3, 60)  # 3 per 60s

    # Perform 3 acks (should pass)
    for _ in range(3):
        client.post(f'/api/notifications/{notif_id}/ack', headers=headers)

    # 4th should be limited
    limited = client.post(f'/api/notifications/{notif_id}/ack', headers=headers)
    assert limited.status_code == 429
    j = limited.get_json()
    assert j.get('error') == 'rate_limited'

@pytest.mark.parametrize('endpoint', ['/api/health', '/api/readiness'])
def test_health_and_readiness(client, endpoint):
    resp = client.get(endpoint)
    assert resp.status_code in (200, 503)
    data = resp.get_json()
    assert 'status' in data
