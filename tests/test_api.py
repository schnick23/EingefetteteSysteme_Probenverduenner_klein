import json
from app.main import create_app
from app.config import TestConfig

def test_ping():
    app = create_app(TestConfig)
    client = app.test_client()
    resp = client.get('/api/ping')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'
