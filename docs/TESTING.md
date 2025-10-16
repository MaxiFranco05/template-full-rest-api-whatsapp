# 🧪 Testing Guide

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Estructura de Tests](#estructura-de-tests)
3. [Configuración del Entorno](#configuración-del-entorno)
4. [Tests Unitarios](#tests-unitarios)
5. [Tests de Integración](#tests-de-integración)
6. [Tests End-to-End](#tests-end-to-end)
7. [Tests de WhatsApp](#tests-de-whatsapp)
8. [Coverage y Métricas](#coverage-y-métricas)
9. [CI/CD Testing](#cicd-testing)
10. [Troubleshooting](#troubleshooting)

## 🎯 Introducción

Esta guía cubre todo lo relacionado con testing en Business API Template, desde tests unitarios básicos hasta tests complejos de integración con WhatsApp.

### **Filosofía de Testing**
- **Test Pyramid**: Más tests unitarios, menos tests E2E
- **Test-Driven Development**: Escribir tests antes del código
- **Continuous Testing**: Tests automáticos en CI/CD
- **Quality Gates**: No deploy sin tests que pasen

### **Tipos de Tests**
- **Unit Tests**: Funciones y clases individuales
- **Integration Tests**: Interacción entre componentes
- **E2E Tests**: Flujos completos de usuario
- **Performance Tests**: Rendimiento y carga
- **Security Tests**: Vulnerabilidades y seguridad

## 📁 Estructura de Tests

### **Organización de Archivos**

```
tests/
├── unit/                         # Tests unitarios
│   ├── test_models_base.py        # Tests de modelo base
│   ├── test_models_user.py        # Tests de modelo usuario
│   ├── test_models_whatsapp.py    # Tests de modelos WhatsApp
│   ├── test_models_product.py     # Tests de modelos producto
│   ├── test_schemas_common.py     # Tests de schemas comunes
│   ├── test_schemas_user.py       # Tests de schemas usuario
│   ├── test_schemas_auth.py       # Tests de schemas auth
│   ├── test_schemas_product.py    # Tests de schemas producto
│   ├── test_services_user.py     # Tests de servicios usuario
│   ├── test_services_product.py   # Tests de servicios producto
│   ├── test_services_whatsapp.py  # Tests de servicios WhatsApp
│   ├── test_utils_helpers.py      # Tests de utilidades
│   └── test_utils_flow_functions.py # Tests de funciones de flujo
├── integration/                  # Tests de integración
│   ├── test_api_auth.py           # Tests de API auth
│   ├── test_api_users.py          # Tests de API usuarios
│   ├── test_api_products.py       # Tests de API productos
│   ├── test_api_whatsapp.py       # Tests de API WhatsApp
│   ├── test_database_operations.py # Tests de operaciones DB
│   └── test_whatsapp_integration.py # Tests de integración WhatsApp
├── e2e/                          # Tests end-to-end
│   ├── test_user_registration_flow.py # Flujo de registro
│   ├── test_product_management_flow.py # Flujo de productos
│   ├── test_whatsapp_conversation_flow.py # Flujo de conversación
│   └── test_message_types.py      # Tests de tipos de mensaje
├── fixtures/                     # Datos de prueba
│   ├── users.json                 # Usuarios de prueba
│   ├── products.json              # Productos de prueba
│   ├── conversations.json          # Conversaciones de prueba
│   └── messages.json              # Mensajes de prueba
├── conftest.py                    # Configuración pytest
├── test_app_startup.py            # Test de inicio de app
└── requirements-testing.txt        # Dependencias de testing
```

### **Convenciones de Nomenclatura**

#### **Archivos de Test**
- **test_*.py**: Archivos de test
- **conftest.py**: Configuración pytest
- **fixtures/**: Datos de prueba

#### **Funciones de Test**
- **test_***: Funciones de test
- **test_*_success**: Tests de éxito
- **test_*_failure**: Tests de fallo
- **test_*_edge_case**: Tests de casos límite

#### **Clases de Test**
- **Test***: Clases de test
- **Test*Service**: Tests de servicios
- **Test*Model**: Tests de modelos

## ⚙️ Configuración del Entorno

### **1. Instalar Dependencias**

```bash
# Instalar dependencias de testing
pip install -r tests/requirements-testing.txt

# O instalar individualmente
pip install pytest pytest-asyncio pytest-cov httpx
```

### **2. Configuración de pytest**

```python
# conftest.py
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Base, get_db
from app.models import User, Product, WhatsAppUser

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create test client."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user(db_session):
    """Create sample user for testing."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_product(db_session):
    """Create sample product for testing."""
    product = Product(
        name="Test Product",
        description="Test Description",
        price=1000,
        stock_quantity=50,
        is_available=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product

@pytest.fixture
def sample_whatsapp_user(db_session):
    """Create sample WhatsApp user for testing."""
    whatsapp_user = WhatsAppUser(
        phone_number="+1234567890",
        name="Test User",
        profile_name="Test Profile"
    )
    db_session.add(whatsapp_user)
    db_session.commit()
    db_session.refresh(whatsapp_user)
    return whatsapp_user
```

### **3. Configuración de Variables de Entorno**

```bash
# .env.test
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./test.db
SECRET_KEY=test-secret-key
DEBUG=True
LOG_LEVEL=DEBUG
WHATSAPP_ACCESS_TOKEN=test_token
WHATSAPP_PHONE_NUMBER_ID=test_phone_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=test_verify_token
```

### **4. Scripts de Testing**

```bash
# scripts/run-tests.sh
#!/bin/bash

echo "🧪 Running Tests"
echo "=================="

# Set test environment
export ENV=test

# Run unit tests
echo "📋 Running unit tests..."
pytest tests/unit/ -v --cov=app --cov-report=term-missing

# Run integration tests
echo "🔗 Running integration tests..."
pytest tests/integration/ -v

# Run E2E tests
echo "🌐 Running E2E tests..."
pytest tests/e2e/ -v

# Generate coverage report
echo "📊 Generating coverage report..."
pytest tests/ --cov=app --cov-report=html --cov-report=xml

echo "✅ All tests completed!"
```

## 🔬 Tests Unitarios

### **1. Tests de Modelos**

#### **Test de Modelo Base**
```python
# tests/unit/test_models_base.py
import pytest
from sqlalchemy import create_engine, Column, Integer, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.base import BaseModel

class TestBaseModel:
    def test_base_model_has_required_fields(self):
        """Test that BaseModel has all required fields."""
        assert BaseModel.__abstract__ is True
        assert hasattr(BaseModel, 'id')
        assert hasattr(BaseModel, 'created_at')
        assert hasattr(BaseModel, 'updated_at')
        assert hasattr(BaseModel, 'is_active')

    def test_base_model_column_types(self):
        """Test BaseModel column types by using it as a base class."""
        class TestModel(BaseModel):
            __tablename__ = "test_model"
            extra_field = Column(Integer)
        
        columns = TestModel.__table__.columns
        assert str(columns['id'].type) == 'INTEGER'
        assert 'TIMESTAMP' in str(columns['created_at'].type)
        assert 'TIMESTAMP' in str(columns['updated_at'].type)
        assert str(columns['is_active'].type) == 'BOOLEAN'
        assert str(columns['extra_field'].type) == 'INTEGER'

    def test_base_model_defaults(self):
        """Test BaseModel default values by using it as a base class."""
        class TestModel(BaseModel):
            __tablename__ = "test_model2"
            extra_field = Column(Integer)
        
        columns = TestModel.__table__.columns
        assert columns['is_active'].default.arg is True
        assert columns['created_at'].server_default is not None
```

#### **Test de Modelo Usuario**
```python
# tests/unit/test_models_user.py
import pytest
from app.models.user import User
from app.schemas.user import UserCreate

class TestUserModel:
    def test_user_creation(self, db_session):
        """Test user model creation."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.is_verified is False

    def test_user_unique_email(self, db_session):
        """Test user email uniqueness."""
        user1 = User(
            email="test@example.com",
            username="testuser1",
            hashed_password="hashed_password"
        )
        user2 = User(
            email="test@example.com",  # Same email
            username="testuser2",
            hashed_password="hashed_password"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

    def test_user_unique_username(self, db_session):
        """Test user username uniqueness."""
        user1 = User(
            email="test1@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        user2 = User(
            email="test2@example.com",
            username="testuser",  # Same username
            hashed_password="hashed_password"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
```

### **2. Tests de Schemas**

#### **Test de Schema Usuario**
```python
# tests/unit/test_schemas_user.py
import pytest
from pydantic import ValidationError
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserInDB, User

class TestUserSchemas:
    def test_user_base_valid(self):
        """Test UserBase with valid data."""
        user = UserBase(
            email="test@example.com",
            username="testuser",
            full_name="Test User"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        user = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password == "password123"
        assert user.full_name == "Test User"

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                username="testuser",
                password="password123"
            )

    def test_user_update_partial(self):
        """Test UserUpdate with partial data."""
        user = UserUpdate(
            email="new@example.com",
            full_name="New Name"
        )
        
        assert user.email == "new@example.com"
        assert user.full_name == "New Name"
        assert user.username is None

    def test_user_in_db_valid(self):
        """Test UserInDB with valid data."""
        user = UserInDB(
            id=1,
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            is_superuser=False,
            is_verified=True,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.is_verified is True
```

### **3. Tests de Servicios**

#### **Test de Servicio Usuario**
```python
# tests/unit/test_services_user.py
import pytest
from unittest.mock import Mock, patch
from app.services.business.user import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User

class TestUserService:
    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        user_service = UserService(db_session)
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )
        
        user = user_service.create_user(user_data)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.is_verified is False

    def test_create_user_duplicate_email(self, db_session):
        """Test user creation with duplicate email."""
        user_service = UserService(db_session)
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        
        # Create first user
        user_service.create_user(user_data)
        
        # Try to create second user with same email
        user_data2 = UserCreate(
            email="test@example.com",  # Same email
            username="testuser2",
            password="password123"
        )
        
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(user_data2)

    def test_get_user_by_id_success(self, db_session, sample_user):
        """Test getting user by ID."""
        user_service = UserService(db_session)
        
        user = user_service.get_user_by_id(sample_user.id)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    def test_get_user_by_id_not_found(self, db_session):
        """Test getting non-existent user by ID."""
        user_service = UserService(db_session)
        
        user = user_service.get_user_by_id(999)
        
        assert user is None

    def test_update_user_success(self, db_session, sample_user):
        """Test successful user update."""
        user_service = UserService(db_session)
        update_data = UserUpdate(
            email="updated@example.com",
            full_name="Updated Name"
        )
        
        updated_user = user_service.update_user(sample_user.id, update_data)
        
        assert updated_user.email == "updated@example.com"
        assert updated_user.full_name == "Updated Name"
        assert updated_user.username == sample_user.username  # Unchanged

    def test_delete_user_success(self, db_session, sample_user):
        """Test successful user deletion."""
        user_service = UserService(db_session)
        
        result = user_service.delete_user(sample_user.id)
        
        assert result is True
        
        # Verify user is deleted
        deleted_user = user_service.get_user_by_id(sample_user.id)
        assert deleted_user is None

    def test_authenticate_user_success(self, db_session):
        """Test successful user authentication."""
        user_service = UserService(db_session)
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        
        # Create user
        user = user_service.create_user(user_data)
        
        # Authenticate
        authenticated_user = user_service.authenticate_user("testuser", "password123")
        
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.username == "testuser"

    def test_authenticate_user_invalid_credentials(self, db_session):
        """Test authentication with invalid credentials."""
        user_service = UserService(db_session)
        
        authenticated_user = user_service.authenticate_user("testuser", "wrongpassword")
        
        assert authenticated_user is None
```

## 🔗 Tests de Integración

### **1. Tests de API**

#### **Test de API de Autenticación**
```python
# tests/integration/test_api_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestAuthAPI:
    def test_register_user_success(self, client):
        """Test successful user registration."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "test@example.com"
        assert data["data"]["username"] == "testuser"
        assert "id" in data["data"]

    def test_register_user_duplicate_email(self, client):
        """Test registration with duplicate email."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        
        # Register first user
        client.post("/api/v1/auth/register", json=user_data)
        
        # Try to register second user with same email
        user_data2 = {
            "email": "test@example.com",  # Same email
            "username": "testuser2",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data2)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "email" in data["error"]["message"].lower()

    def test_login_success(self, client):
        """Test successful login."""
        # Register user first
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "user" in data["data"]

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "credentials" in data["error"]["message"].lower()

    def test_get_current_user_success(self, client, sample_user):
        """Test getting current user with valid token."""
        # Login to get token
        login_data = {
            "username": sample_user.username,
            "password": "password123"  # Assuming we know the password
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["data"]["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sample_user.id
        assert data["data"]["email"] == sample_user.email

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
```

#### **Test de API de Usuarios**
```python
# tests/integration/test_api_users.py
import pytest
from fastapi.testclient import TestClient

class TestUsersAPI:
    def test_get_users_success(self, client, sample_user):
        """Test getting users list."""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["items"]) >= 1

    def test_get_users_with_pagination(self, client):
        """Test users list with pagination."""
        response = client.get("/api/v1/users/?page=1&size=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "page" in data["data"]
        assert "size" in data["data"]
        assert "pages" in data["data"]

    def test_get_user_by_id_success(self, client, sample_user):
        """Test getting user by ID."""
        response = client.get(f"/api/v1/users/{sample_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sample_user.id
        assert data["data"]["email"] == sample_user.email

    def test_get_user_by_id_not_found(self, client):
        """Test getting non-existent user by ID."""
        response = client.get("/api/v1/users/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"]["message"].lower()

    def test_create_user_success(self, client):
        """Test creating new user."""
        user_data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "new@example.com"
        assert data["data"]["username"] == "newuser"

    def test_update_user_success(self, client, sample_user):
        """Test updating user."""
        update_data = {
            "email": "updated@example.com",
            "full_name": "Updated Name"
        }
        
        response = client.put(f"/api/v1/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "updated@example.com"
        assert data["data"]["full_name"] == "Updated Name"

    def test_delete_user_success(self, client, sample_user):
        """Test deleting user."""
        response = client.delete(f"/api/v1/users/{sample_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_delete_user_not_found(self, client):
        """Test deleting non-existent user."""
        response = client.delete("/api/v1/users/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
```

### **2. Tests de Base de Datos**

#### **Test de Operaciones de Base de Datos**
```python
# tests/integration/test_database_operations.py
import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.product import Product
from app.models.whatsapp import WhatsAppUser

class TestDatabaseOperations:
    def test_user_crud_operations(self, db_session):
        """Test complete CRUD operations for User."""
        # Create
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        
        # Read
        found_user = db_session.query(User).filter(User.id == user.id).first()
        assert found_user is not None
        assert found_user.email == "test@example.com"
        
        # Update
        found_user.full_name = "Updated Name"
        db_session.commit()
        db_session.refresh(found_user)
        
        assert found_user.full_name == "Updated Name"
        
        # Delete
        db_session.delete(found_user)
        db_session.commit()
        
        deleted_user = db_session.query(User).filter(User.id == user.id).first()
        assert deleted_user is None

    def test_product_crud_operations(self, db_session):
        """Test complete CRUD operations for Product."""
        # Create
        product = Product(
            name="Test Product",
            description="Test Description",
            price=1000,
            stock_quantity=50,
            is_available=True
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        assert product.id is not None
        
        # Read
        found_product = db_session.query(Product).filter(Product.id == product.id).first()
        assert found_product is not None
        assert found_product.name == "Test Product"
        
        # Update
        found_product.price = 1500
        found_product.stock_quantity = 75
        db_session.commit()
        db_session.refresh(found_product)
        
        assert found_product.price == 1500
        assert found_product.stock_quantity == 75
        
        # Delete
        db_session.delete(found_product)
        db_session.commit()
        
        deleted_product = db_session.query(Product).filter(Product.id == product.id).first()
        assert deleted_product is None

    def test_whatsapp_user_crud_operations(self, db_session):
        """Test complete CRUD operations for WhatsAppUser."""
        # Create
        whatsapp_user = WhatsAppUser(
            phone_number="+1234567890",
            name="Test User",
            profile_name="Test Profile"
        )
        db_session.add(whatsapp_user)
        db_session.commit()
        db_session.refresh(whatsapp_user)
        
        assert whatsapp_user.id is not None
        
        # Read
        found_user = db_session.query(WhatsAppUser).filter(WhatsAppUser.id == whatsapp_user.id).first()
        assert found_user is not None
        assert found_user.phone_number == "+1234567890"
        
        # Update
        found_user.name = "Updated Name"
        found_user.message_count = 10
        db_session.commit()
        db_session.refresh(found_user)
        
        assert found_user.name == "Updated Name"
        assert found_user.message_count == 10
        
        # Delete
        db_session.delete(found_user)
        db_session.commit()
        
        deleted_user = db_session.query(WhatsAppUser).filter(WhatsAppUser.id == whatsapp_user.id).first()
        assert deleted_user is None

    def test_database_constraints(self, db_session):
        """Test database constraints and relationships."""
        # Test unique email constraint
        user1 = User(
            email="test@example.com",
            username="testuser1",
            hashed_password="hashed_password"
        )
        user2 = User(
            email="test@example.com",  # Same email
            username="testuser2",
            hashed_password="hashed_password"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
        
        # Rollback for next test
        db_session.rollback()
        
        # Test unique username constraint
        user3 = User(
            email="test3@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        user4 = User(
            email="test4@example.com",
            username="testuser",  # Same username
            hashed_password="hashed_password"
        )
        
        db_session.add(user3)
        db_session.commit()
        
        db_session.add(user4)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
```

## 🌐 Tests End-to-End

### **1. Tests de Flujos de Usuario**

#### **Test de Flujo de Registro**
```python
# tests/e2e/test_user_registration_flow.py
import pytest
from fastapi.testclient import TestClient

class TestUserRegistrationFlow:
    def test_complete_user_registration_flow(self, client):
        """Test complete user registration flow."""
        # Step 1: Register user
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        }
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        register_data = register_response.json()
        assert register_data["success"] is True
        user_id = register_data["data"]["id"]
        
        # Step 2: Login with new user
        login_data = {
            "username": "newuser",
            "password": "password123"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        token = login_data["data"]["access_token"]
        
        # Step 3: Get current user info
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        me_data = me_response.json()
        assert me_data["data"]["id"] == user_id
        assert me_data["data"]["email"] == "newuser@example.com"
        
        # Step 4: Update user profile
        update_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com"
        }
        
        update_response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        update_data = update_response.json()
        assert update_data["data"]["full_name"] == "Updated Name"
        assert update_data["data"]["email"] == "updated@example.com"
        
        # Step 5: Verify changes
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        me_data = me_response.json()
        assert me_data["data"]["full_name"] == "Updated Name"
        assert me_data["data"]["email"] == "updated@example.com"
```

#### **Test de Flujo de Gestión de Productos**
```python
# tests/e2e/test_product_management_flow.py
import pytest
from fastapi.testclient import TestClient

class TestProductManagementFlow:
    def test_complete_product_management_flow(self, client, sample_user):
        """Test complete product management flow."""
        # Step 1: Login as user
        login_data = {
            "username": sample_user.username,
            "password": "password123"  # Assuming we know the password
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Create product
        product_data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 1000,
            "stock_quantity": 50,
            "is_available": True
        }
        
        create_response = client.post("/api/v1/products/", json=product_data, headers=headers)
        assert create_response.status_code == 201
        
        create_data = create_response.json()
        product_id = create_data["data"]["id"]
        
        # Step 3: Get product
        get_response = client.get(f"/api/v1/products/{product_id}", headers=headers)
        assert get_response.status_code == 200
        
        get_data = get_response.json()
        assert get_data["data"]["name"] == "Test Product"
        assert get_data["data"]["price"] == 1000
        
        # Step 4: Update product
        update_data = {
            "name": "Updated Product",
            "price": 1500,
            "stock_quantity": 75
        }
        
        update_response = client.put(f"/api/v1/products/{product_id}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        update_data = update_response.json()
        assert update_data["data"]["name"] == "Updated Product"
        assert update_data["data"]["price"] == 1500
        assert update_data["data"]["stock_quantity"] == 75
        
        # Step 5: List products
        list_response = client.get("/api/v1/products/", headers=headers)
        assert list_response.status_code == 200
        
        list_data = list_response.json()
        assert len(list_data["data"]["items"]) >= 1
        
        # Find our product in the list
        our_product = next((p for p in list_data["data"]["items"] if p["id"] == product_id), None)
        assert our_product is not None
        assert our_product["name"] == "Updated Product"
        
        # Step 6: Delete product
        delete_response = client.delete(f"/api/v1/products/{product_id}", headers=headers)
        assert delete_response.status_code == 200
        
        # Step 7: Verify deletion
        get_response = client.get(f"/api/v1/products/{product_id}", headers=headers)
        assert get_response.status_code == 404
```

### **2. Tests de WhatsApp**

#### **Test de Flujo de Conversación**
```python
# tests/e2e/test_whatsapp_conversation_flow.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from app.services.whatsapp.service import WhatsAppService
from app.services.flows.service import WhatsAppFlowService

class TestWhatsAppConversationFlow:
    @pytest.mark.asyncio
    async def test_complete_whatsapp_conversation_flow(self):
        """Test complete WhatsApp conversation flow."""
        # Mock WhatsApp API calls
        with patch('app.services.whatsapp.service.aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json.return_value = {
                "messaging_product": "whatsapp",
                "contacts": [{"input": "+1234567890", "wa_id": "1234567890"}],
                "messages": [{"id": "test_message_id"}]
            }
            
            whatsapp_service = WhatsAppService()
            flow_service = WhatsAppFlowService(whatsapp_service, Mock())
            
            # Step 1: Process incoming message
            incoming_message = {
                "from": "+1234567890",
                "text": {"body": "Hola"},
                "type": "text",
                "id": "incoming_message_id"
            }
            
            response = await whatsapp_service.process_message(incoming_message)
            
            assert response["success"] is True
            assert "response_message" in response
            
            # Step 2: Process button response
            button_message = {
                "from": "+1234567890",
                "interactive": {
                    "type": "button_reply",
                    "button_reply": {
                        "id": "info",
                        "title": "Información"
                    }
                },
                "type": "interactive",
                "id": "button_message_id"
            }
            
            response = await whatsapp_service.process_message(button_message)
            
            assert response["success"] is True
            assert "response_message" in response
            
            # Step 3: Process list selection
            list_message = {
                "from": "+1234567890",
                "interactive": {
                    "type": "list_reply",
                    "list_reply": {
                        "id": "product_1",
                        "title": "Producto 1"
                    }
                },
                "type": "interactive",
                "id": "list_message_id"
            }
            
            response = await whatsapp_service.process_message(list_message)
            
            assert response["success"] is True
            assert "response_message" in response
```

#### **Test de Tipos de Mensaje**
```python
# tests/e2e/test_message_types.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from app.services.whatsapp.service import WhatsAppService

class TestMessageTypes:
    @pytest.mark.asyncio
    async def test_text_message_sending(self):
        """Test sending text message."""
        with patch('app.services.whatsapp.service.aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json.return_value = {
                "messaging_product": "whatsapp",
                "contacts": [{"input": "+1234567890", "wa_id": "1234567890"}],
                "messages": [{"id": "test_message_id"}]
            }
            
            whatsapp_service = WhatsAppService()
            
            response = await whatsapp_service.send_message(
                to="+1234567890",
                message_type="text",
                content={"text": "Hello, this is a test message"}
            )
            
            assert response["success"] is True
            assert "message_id" in response

    @pytest.mark.asyncio
    async def test_button_message_sending(self):
        """Test sending button message."""
        with patch('app.services.whatsapp.service.aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json.return_value = {
                "messaging_product": "whatsapp",
                "contacts": [{"input": "+1234567890", "wa_id": "1234567890"}],
                "messages": [{"id": "test_message_id"}]
            }
            
            whatsapp_service = WhatsAppService()
            
            response = await whatsapp_service.send_message(
                to="+1234567890",
                message_type="interactive",
                content={
                    "type": "button",
                    "header": {"type": "text", "text": "Welcome!"},
                    "body": {"text": "Choose an option:"},
                    "action": {
                        "buttons": [
                            {"type": "reply", "reply": {"id": "info", "title": "Info"}},
                            {"type": "reply", "reply": {"id": "support", "title": "Support"}}
                        ]
                    }
                }
            )
            
            assert response["success"] is True
            assert "message_id" in response

    @pytest.mark.asyncio
    async def test_list_message_sending(self):
        """Test sending list message."""
        with patch('app.services.whatsapp.service.aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json.return_value = {
                "messaging_product": "whatsapp",
                "contacts": [{"input": "+1234567890", "wa_id": "1234567890"}],
                "messages": [{"id": "test_message_id"}]
            }
            
            whatsapp_service = WhatsAppService()
            
            response = await whatsapp_service.send_message(
                to="+1234567890",
                message_type="interactive",
                content={
                    "type": "list",
                    "header": {"type": "text", "text": "Products"},
                    "body": {"text": "Select a product:"},
                    "action": {
                        "button": "View Products",
                        "sections": [
                            {
                                "title": "Electronics",
                                "rows": [
                                    {"id": "product_1", "title": "Product 1", "description": "Description 1"},
                                    {"id": "product_2", "title": "Product 2", "description": "Description 2"}
                                ]
                            }
                        ]
                    }
                }
            )
            
            assert response["success"] is True
            assert "message_id" in response

    @pytest.mark.asyncio
    async def test_image_message_sending(self):
        """Test sending image message."""
        with patch('app.services.whatsapp.service.aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json.return_value = {
                "messaging_product": "whatsapp",
                "contacts": [{"input": "+1234567890", "wa_id": "1234567890"}],
                "messages": [{"id": "test_message_id"}]
            }
            
            whatsapp_service = WhatsAppService()
            
            response = await whatsapp_service.send_message(
                to="+1234567890",
                message_type="image",
                content={
                    "link": "https://example.com/image.jpg",
                    "caption": "Check out this image!"
                }
            )
            
            assert response["success"] is True
            assert "message_id" in response
```

## 📊 Coverage y Métricas

### **1. Configuración de Coverage**

```python
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = -ra -q --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    whatsapp: marks tests as WhatsApp specific tests
```

### **2. Ejecutar Tests con Coverage**

```bash
# Ejecutar todos los tests con coverage
pytest tests/ --cov=app --cov-report=html --cov-report=xml

# Ejecutar tests específicos con coverage
pytest tests/unit/ --cov=app.services --cov-report=html

# Ejecutar tests excluyendo los lentos
pytest tests/ -m "not slow" --cov=app

# Generar reporte de coverage
coverage html
coverage xml
```

### **3. Configuración de Coverage**

```python
# .coveragerc
[run]
source = app
omit = 
    */tests/*
    */venv/*
    */env/*
    */__pycache__/*
    */migrations/*
    */alembic/*
    */conftest.py
    */test_*.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

### **4. Métricas de Calidad**

#### **Script de Métricas**
```bash
# scripts/quality-metrics.sh
#!/bin/bash

echo "📊 Quality Metrics Report"
echo "========================="

# Run tests with coverage
echo "🧪 Running tests..."
pytest tests/ --cov=app --cov-report=term-missing --cov-report=xml

# Run linting
echo "🔍 Running linting..."
flake8 app/ --count --statistics
black --check app/
isort --check-only app/
mypy app/ --ignore-missing-imports

# Run security checks
echo "🔒 Running security checks..."
bandit -r app/ -f json -o bandit-report.json
safety check --json --output safety-report.json

# Generate report
echo "📋 Generating quality report..."
python scripts/generate_quality_report.py

echo "✅ Quality metrics completed!"
```

## 🚀 CI/CD Testing

### **1. GitHub Actions para Testing**

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r tests/requirements-testing.txt
        
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=app --cov-report=xml
        
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
        
    - name: Run E2E tests
      run: |
        pytest tests/e2e/ -v
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        
    - name: Upload coverage reports
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: htmlcov/
```

### **2. Tests de Performance**

```python
# tests/performance/test_performance.py
import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

class TestPerformance:
    def test_api_response_time(self, client):
        """Test API response time is acceptable."""
        start_time = time.time()
        
        response = client.get("/api/v1/users/")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

    def test_database_query_performance(self, db_session):
        """Test database query performance."""
        from app.models.user import User
        
        # Create test data
        for i in range(100):
            user = User(
                email=f"test{i}@example.com",
                username=f"testuser{i}",
                hashed_password="hashed_password"
            )
            db_session.add(user)
        db_session.commit()
        
        # Test query performance
        start_time = time.time()
        
        users = db_session.query(User).limit(50).all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert len(users) == 50
        assert query_time < 0.1  # Should query within 100ms

    def test_concurrent_requests(self, client):
        """Test handling concurrent requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = client.get("/api/v1/users/")
            results.put(response.status_code)
        
        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check all requests succeeded
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        assert len(status_codes) == 10
        assert all(code == 200 for code in status_codes)
```

## 🔧 Troubleshooting

### **1. Problemas Comunes**

#### **Error de Base de Datos**
```bash
# Error: Database is locked
# Solución: Verificar que no hay otras conexiones activas
pytest tests/ --tb=short

# Error: Table doesn't exist
# Solución: Ejecutar migraciones
alembic upgrade head
```

#### **Error de Importación**
```bash
# Error: Module not found
# Solución: Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

#### **Error de Timeout**
```bash
# Error: Test timeout
# Solución: Aumentar timeout o marcar como slow
pytest tests/ --timeout=300
```

### **2. Debugging de Tests**

#### **Ejecutar Tests con Debug**
```bash
# Ejecutar con output detallado
pytest tests/ -v -s

# Ejecutar test específico con debug
pytest tests/unit/test_user_service.py::TestUserService::test_create_user -v -s

# Ejecutar con pdb
pytest tests/ --pdb
```

#### **Logs de Debug**
```python
# En tests, usar logging para debug
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_debug():
    logger = logging.getLogger(__name__)
    logger.debug("Debug information")
    # Test code
```

### **3. Optimización de Tests**

#### **Tests Paralelos**
```bash
# Instalar pytest-xdist
pip install pytest-xdist

# Ejecutar tests en paralelo
pytest tests/ -n auto

# Ejecutar tests en paralelo con coverage
pytest tests/ -n auto --cov=app
```

#### **Tests Incrementales**
```bash
# Instalar pytest-cache
pip install pytest-cache

# Ejecutar solo tests que fallaron
pytest tests/ --lf

# Ejecutar solo tests nuevos
pytest tests/ --ff
```

---

## 📞 Soporte

### **Recursos Adicionales**
- **Documentación**: [docs/README.md](docs/README.md)
- **Development Guide**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

### **Contacto**
- **Email**: testing@yourapp.com
- **GitHub Issues**: [Reportar problemas](https://github.com/yourusername/issues)
- **Discord**: [Comunidad de testing](https://discord.gg/yourapp)

---

*Esta guía se actualiza con cada nueva versión. Para la versión más reciente, consulta el repositorio del proyecto.*