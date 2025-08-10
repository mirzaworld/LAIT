import json

def test_register_and_login_flow(client):
    # Register
    reg_resp = client.post('/api/auth/register', json={
        'email': 'testuser@example.com',
        'password': 'StrongPass123',
        'first_name': 'Test',
        'last_name': 'User'
    })
    assert reg_resp.status_code in (200,201)
    reg_data = reg_resp.get_json()
    assert 'token' in reg_data

    # Login
    login_resp = client.post('/api/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'StrongPass123'
    })
    assert login_resp.status_code == 200
    login_data = login_resp.get_json()
    assert 'token' in login_data

    # Use token to access protected endpoint
    token = login_data['token']
    me_resp = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me_resp.status_code == 200
    me_data = me_resp.get_json()
    assert 'user' in me_data and me_data['user']['email'] == 'testuser@example.com'
