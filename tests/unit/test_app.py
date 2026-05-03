import pytest
from app.app import app, db, User

@pytest.fixture
def client():
    # Configuramos la app para testing con una base de datos en memoria (SQLite)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        # Limpieza de la base de datos después de cada test
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_healthcheck(client):
    """Prueba el endpoint de healthcheck requerido por el TP"""
    response = client.get('/healthcheck')
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "message": "API funcionando correctamente"}

def test_create_and_get_user(client):
    """Prueba la creación de un usuario y que se liste correctamente"""
    # 1. Crear usuario
    new_user_data = {"nombre": "Eduardo Miguez", "email": "eduardo@empresa-ias.com"}
    response_post = client.post('/users', json=new_user_data)
    assert response_post.status_code == 201
    
    # 2. Obtener usuarios para verificar que se guardó
    response_get = client.get('/users')
    assert response_get.status_code == 200
    data = response_get.get_json()
    assert len(data) == 1
    assert data[0]['nombre'] == "Eduardo Miguez"

def test_create_user_missing_data(client):
    """Prueba de validación: error al crear usuario sin el email"""
    response = client.post('/users', json={"nombre": "Solo Nombre sin Email"})
    assert response.status_code == 400
    assert "error" in response.get_json()
