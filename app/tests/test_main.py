"""
Tests básicos para la aplicación
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.database import get_db, Base
from main import app

# Crear base de datos de prueba
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL_TEST
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Configurar base de datos de prueba"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """Probar endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Cafe API" in response.text


def test_health_check():
    """Probar endpoint de salud"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == settings.APP_NAME


def test_register_user(setup_database):
    """Probar registro de usuario"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data


def test_login_user(setup_database):
    """Probar login de usuario"""
    # Primero registrar un usuario
    user_data = {
        "email": "login@example.com",
        "username": "loginuser",
        "password": "loginpassword123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Luego hacer login
    login_data = {
        "username": "loginuser",
        "password": "loginpassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_products():
    """Probar obtener productos"""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
