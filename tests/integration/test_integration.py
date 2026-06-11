import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_healthcheck_endpoint(client):
    """Prueba de integración básica para verificar que la API responde"""
    response = client.get('/healthcheck')
    assert response.status_code == 200
    assert response.json == {"status": "ok", "message": "API funcionando correctamente"}
