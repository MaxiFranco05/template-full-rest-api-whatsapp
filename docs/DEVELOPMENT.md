# 👨‍💻 Development Guide

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Configuración del Entorno](#configuración-del-entorno)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Estándares de Código](#estándares-de-código)
5. [Flujo de Desarrollo](#flujo-de-desarrollo)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Contribución](#contribución)
9. [Herramientas de Desarrollo](#herramientas-de-desarrollo)
10. [Mejores Prácticas](#mejores-prácticas)

## 🎯 Introducción

Esta guía está diseñada para desarrolladores que quieren contribuir al proyecto Business API Template. Cubre desde la configuración inicial hasta las mejores prácticas de desarrollo.

### **Audiencia**
- **Desarrolladores Backend**: Python, FastAPI, SQLAlchemy
- **Desarrolladores DevOps**: Docker, CI/CD, Deployment
- **Desarrolladores Full-Stack**: APIs, Integraciones
- **Contribuidores**: Nuevos desarrolladores al proyecto

## ⚙️ Configuración del Entorno

### **1. Requisitos Previos**

```bash
# Verificar versiones
python --version  # 3.11 o 3.12
git --version     # 2.30+
node --version    # 16+ (opcional, para herramientas)
```

### **2. Clonar y Configurar**

```bash
# Clonar repositorio
git clone https://github.com/yourusername/business-api-template.git
cd business-api-template

# Crear rama de desarrollo
git checkout -b feature/nueva-funcionalidad

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### **3. Instalar Dependencias**

```bash
# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install -r tests/requirements-testing.txt

# Instalar herramientas de desarrollo
pip install black isort flake8 mypy bandit safety pre-commit
```

### **4. Configurar Pre-commit Hooks**

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install

# Ejecutar en todos los archivos
pre-commit run --all-files
```

### **5. Configurar Variables de Entorno**

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Configurar para desarrollo
cat > .env << EOF
# Base de datos
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./business_api_dev.db

# Seguridad
SECRET_KEY=dev-secret-key-not-for-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# WhatsApp (opcional para desarrollo)
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_WEBHOOK_VERIFY_TOKEN=

# Logging
LOG_LEVEL=DEBUG
EOF
```

### **6. Inicializar Base de Datos**

```bash
# Ejecutar migraciones
alembic upgrade head

# Crear datos de prueba (opcional)
python scripts/create_sample_data.py
```

### **7. Verificar Configuración**

```bash
# Ejecutar tests básicos
pytest tests/unit/test_models_base.py -v

# Ejecutar aplicación
python main.py

# Verificar en navegador
# http://localhost:8000/docs
```

## 📁 Estructura del Proyecto

### **Organización de Archivos**

```
business-api-template/
├── app/                          # Código fuente principal
│   ├── api/                      # Capa de API
│   │   └── v1/                   # Versión 1 de la API
│   │       ├── endpoints/        # Endpoints específicos
│   │       │   ├── auth.py       # Autenticación
│   │       │   ├── users.py      # Usuarios
│   │       │   ├── products.py   # Productos
│   │       │   └── whatsapp.py   # WhatsApp
│   │       └── api.py            # Router principal
│   ├── core/                     # Configuración central
│   │   ├── config.py             # Configuración de la app
│   │   ├── security.py           # Seguridad y JWT
│   │   ├── logging_config.py     # Configuración de logs
│   │   └── error_handling.py     # Manejo de errores
│   ├── db/                       # Base de datos
│   │   └── database.py           # Conexión y configuración
│   ├── models/                   # Modelos de datos
│   │   ├── base.py               # Modelo base
│   │   ├── user.py               # Modelos de usuario
│   │   ├── whatsapp.py           # Modelos de WhatsApp
│   │   └── product.py            # Modelos de productos
│   ├── schemas/                  # Esquemas Pydantic
│   │   ├── common.py             # Esquemas comunes
│   │   ├── user.py               # Esquemas de usuario
│   │   ├── auth.py               # Esquemas de autenticación
│   │   └── product.py            # Esquemas de productos
│   ├── services/                 # Lógica de negocio
│   │   ├── business/             # Servicios de negocio
│   │   ├── whatsapp/             # Servicios de WhatsApp
│   │   ├── flows/                # Motor de flujos
│   │   └── shared/               # Servicios compartidos
│   ├── utils/                    # Utilidades
│   │   ├── helpers.py            # Funciones auxiliares
│   │   ├── flow_functions.py     # Funciones de flujos
│   │   └── feature_detection.py # Detección de características
│   └── flows/                    # Definiciones de flujos
│       ├── main.json             # Flujo principal
│       ├── main.yaml             # Flujo en YAML
│       └── main_python.py        # Flujo en Python
├── tests/                        # Tests
│   ├── unit/                     # Tests unitarios
│   ├── integration/              # Tests de integración
│   ├── e2e/                      # Tests end-to-end
│   └── fixtures/                 # Datos de prueba
├── docs/                         # Documentación
├── .github/                      # GitHub Actions
├── alembic/                      # Migraciones de DB
├── scripts/                      # Scripts de utilidad
├── main.py                       # Punto de entrada
├── requirements.txt              # Dependencias
├── pyproject.toml                # Configuración del proyecto
├── Dockerfile                    # Imagen Docker
└── docker-compose.yml            # Orquestación Docker
```

### **Convenciones de Nomenclatura**

#### **Archivos y Directorios**
- **Snake_case**: Para archivos Python (`user_service.py`)
- **kebab-case**: Para archivos de configuración (`docker-compose.yml`)
- **UPPERCASE**: Para archivos de configuración (`.env`, `README.md`)

#### **Clases y Funciones**
- **PascalCase**: Para clases (`UserService`, `WhatsAppMessageBuilder`)
- **snake_case**: Para funciones y variables (`create_user`, `user_data`)
- **UPPERCASE**: Para constantes (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)

#### **APIs y Endpoints**
- **kebab-case**: Para URLs (`/api/v1/user-profiles`)
- **snake_case**: Para parámetros (`user_id`, `page_size`)

## 📝 Estándares de Código

### **1. Formato de Código**

#### **Black (Formateo)**
```bash
# Formatear código
black app/

# Verificar formato
black --check app/
```

#### **isort (Importaciones)**
```bash
# Organizar importaciones
isort app/

# Verificar importaciones
isort --check-only app/
```

#### **Configuración en pyproject.toml**
```toml
[tool.black]
line-length = 88
target-version = ['py311', 'py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["app"]
```

### **2. Linting**

#### **flake8 (Linting)**
```bash
# Ejecutar flake8
flake8 app/

# Con configuración específica
flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
```

#### **mypy (Type Checking)**
```bash
# Verificar tipos
mypy app/

# Con configuración
mypy app/ --ignore-missing-imports --strict
```

### **3. Documentación**

#### **Docstrings (Google Style)**
```python
def create_user(user_data: UserCreate, db: Session) -> User:
    """
    Create a new user in the database.
    
    Args:
        user_data: User data from request
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        ValueError: If user already exists
        DatabaseError: If database operation fails
    """
    pass
```

#### **Type Hints**
```python
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None
) -> List[User]:
    """Get users with pagination and search."""
    pass
```

### **4. Estructura de Archivos**

#### **Imports (Orden)**
```python
# 1. Standard library imports
import os
import sys
from typing import List, Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 3. Local application imports
from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
```

## 🔄 Flujo de Desarrollo

### **1. Git Workflow**

#### **Ramas**
- **main**: Producción estable
- **dev**: Desarrollo principal
- **feature/***: Nuevas funcionalidades
- **bugfix/***: Corrección de bugs
- **hotfix/***: Correcciones urgentes

#### **Commits**
```bash
# Formato de commits
git commit -m "feat: add user authentication endpoint"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
git commit -m "test: add unit tests for user service"
```

**Tipos de commits:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato de código
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Tareas de mantenimiento

### **2. Desarrollo de Features**

#### **Paso 1: Crear Rama**
```bash
git checkout dev
git pull origin dev
git checkout -b feature/user-profile-management
```

#### **Paso 2: Desarrollo**
```bash
# Hacer cambios
# Ejecutar tests frecuentemente
pytest tests/unit/test_user_service.py -v

# Formatear código
black app/
isort app/

# Verificar linting
flake8 app/
mypy app/
```

#### **Paso 3: Tests**
```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/test_user_service.py::TestUserService::test_create_user -v
```

#### **Paso 4: Commit y Push**
```bash
# Agregar cambios
git add .

# Commit con mensaje descriptivo
git commit -m "feat: add user profile management endpoints"

# Push a rama remota
git push origin feature/user-profile-management
```

#### **Paso 5: Pull Request**
```bash
# Crear PR en GitHub
# Revisar código
# Aprobar cambios
# Merge a dev
```

### **3. Code Review**

#### **Checklist para Reviewers**
- [ ] **Funcionalidad**: ¿El código hace lo que debe?
- [ ] **Tests**: ¿Hay tests adecuados?
- [ ] **Documentación**: ¿Está documentado?
- [ ] **Performance**: ¿Es eficiente?
- [ ] **Seguridad**: ¿Hay vulnerabilidades?
- [ ] **Estándares**: ¿Sigue las convenciones?

#### **Checklist para Authors**
- [ ] **Tests**: Todos los tests pasan
- [ ] **Linting**: Sin errores de linting
- [ ] **Documentación**: Docstrings actualizados
- [ ] **Commits**: Mensajes descriptivos
- [ ] **PR**: Descripción clara del cambio

## 🧪 Testing

### **1. Estructura de Tests**

```
tests/
├── unit/                         # Tests unitarios
│   ├── test_models_*.py          # Tests de modelos
│   ├── test_schemas_*.py         # Tests de schemas
│   ├── test_services_*.py        # Tests de servicios
│   └── test_utils_*.py           # Tests de utilidades
├── integration/                  # Tests de integración
│   ├── test_api_*.py             # Tests de API
│   ├── test_database_*.py        # Tests de DB
│   └── test_whatsapp_*.py        # Tests de WhatsApp
├── e2e/                          # Tests end-to-end
│   ├── test_user_flows.py        # Flujos de usuario
│   ├── test_whatsapp_flows.py     # Flujos de WhatsApp
│   └── test_message_types.py     # Tipos de mensaje
└── fixtures/                     # Datos de prueba
    ├── users.json                # Usuarios de prueba
    ├── products.json              # Productos de prueba
    └── conversations.json         # Conversaciones de prueba
```

### **2. Escribir Tests**

#### **Test Unitario**
```python
import pytest
from app.services.business.user import UserService
from app.schemas.user import UserCreate

class TestUserService:
    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        user_service = UserService(db_session)
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        
        user = user_service.create_user(user_data)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
    
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
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(user_data)
```

#### **Test de Integración**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_endpoint():
    """Test user creation via API."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "test@example.com"
```

#### **Test E2E**
```python
import pytest
import asyncio
from app.services.whatsapp.service import WhatsAppService

@pytest.mark.asyncio
async def test_whatsapp_message_flow():
    """Test complete WhatsApp message flow."""
    whatsapp_service = WhatsAppService()
    
    # Simulate incoming message
    message_data = {
        "from": "+1234567890",
        "text": {"body": "Hola"},
        "type": "text"
    }
    
    # Process message
    response = await whatsapp_service.process_message(message_data)
    
    assert response["success"] is True
    assert "response_message" in response
```

### **3. Ejecutar Tests**

```bash
# Todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/unit/test_user_service.py -v

# Con coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term

# Tests en paralelo
pytest tests/ -n auto

# Tests con markers
pytest tests/ -m "not slow" -v
```

### **4. Fixtures**

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.models.user import User

@pytest.fixture
def db_session():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def sample_user(db_session):
    """Create sample user for testing."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user
```

## 🐛 Debugging

### **1. Logging**

#### **Configuración de Logs**
```python
import logging
from app.core.logging_config import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Usar en código
logger.info("User created successfully", extra={"user_id": user.id})
logger.error("Database connection failed", extra={"error": str(e)})
logger.debug("Processing message", extra={"message_id": message.id})
```

#### **Niveles de Log**
- **DEBUG**: Información detallada para debugging
- **INFO**: Información general del flujo
- **WARNING**: Situaciones inesperadas pero manejables
- **ERROR**: Errores que no detienen la aplicación
- **CRITICAL**: Errores críticos que detienen la aplicación

### **2. Debugging Tools**

#### **pdb (Python Debugger)**
```python
import pdb

def problematic_function():
    # Código problemático
    pdb.set_trace()  # Breakpoint
    # Más código
```

#### **ipdb (IPython Debugger)**
```python
import ipdb

def debug_function():
    # Código
    ipdb.set_trace()  # Breakpoint interactivo
    # Más código
```

#### **VS Code Debugging**
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### **3. Profiling**

#### **cProfile**
```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Código a perfilar
    your_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

#### **memory_profiler**
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Código que usa mucha memoria
    pass
```

## 🤝 Contribución

### **1. Proceso de Contribución**

#### **Paso 1: Fork del Repositorio**
```bash
# Fork en GitHub
# Clonar tu fork
git clone https://github.com/tu-usuario/business-api-template.git
cd business-api-template

# Agregar upstream
git remote add upstream https://github.com/original/business-api-template.git
```

#### **Paso 2: Crear Rama**
```bash
git checkout dev
git pull upstream dev
git checkout -b feature/tu-funcionalidad
```

#### **Paso 3: Desarrollo**
```bash
# Hacer cambios
# Ejecutar tests
pytest tests/ -v

# Formatear código
black app/
isort app/

# Verificar linting
flake8 app/
mypy app/
```

#### **Paso 4: Pull Request**
```bash
git add .
git commit -m "feat: add new functionality"
git push origin feature/tu-funcionalidad

# Crear PR en GitHub
```

### **2. Guidelines de Contribución**

#### **Código**
- Sigue los estándares de código establecidos
- Escribe tests para nueva funcionalidad
- Documenta cambios importantes
- Mantén compatibilidad hacia atrás

#### **Commits**
- Usa mensajes descriptivos
- Un commit por cambio lógico
- Incluye tests en el mismo commit
- Referencia issues cuando aplique

#### **Pull Requests**
- Descripción clara del cambio
- Lista de cambios realizados
- Screenshots si aplica
- Referencia a issues relacionados

### **3. Reportar Bugs**

#### **Template de Bug Report**
```markdown
## Descripción del Bug
Descripción clara del problema.

## Pasos para Reproducir
1. Ir a '...'
2. Hacer click en '....'
3. Scroll hasta '....'
4. Ver error

## Comportamiento Esperado
Descripción de lo que debería pasar.

## Screenshots
Si aplica, agregar screenshots.

## Información del Sistema
- OS: [e.g. Windows, macOS, Linux]
- Python: [e.g. 3.12]
- Versión: [e.g. 1.0.0]

## Logs
```
Pegar logs relevantes aquí
```
```

## 🛠️ Herramientas de Desarrollo

### **1. IDE/Editor**

#### **VS Code (Recomendado)**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### **PyCharm**
- Configurar interpretador Python
- Habilitar inspections
- Configurar formatters (Black, isort)
- Configurar linters (flake8, mypy)

### **2. Herramientas de Línea de Comandos**

#### **Scripts Útiles**
```bash
# scripts/dev-setup.sh
#!/bin/bash
echo "Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements-testing.txt

# Install pre-commit hooks
pre-commit install

# Run initial tests
pytest tests/unit/ -v

echo "Development environment ready!"
```

#### **Makefile**
```makefile
# Makefile
.PHONY: install test lint format clean

install:
	pip install -r requirements.txt
	pip install -r tests/requirements-testing.txt
	pre-commit install

test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=app --cov-report=html

lint:
	flake8 app/
	mypy app/
	bandit -r app/

format:
	black app/
	isort app/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
```

### **3. Docker para Desarrollo**

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./business_api.db
      - DEBUG=True
    volumes:
      - .:/app
      - /app/__pycache__
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=business_api
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 📚 Mejores Prácticas

### **1. Código Limpio**

#### **Principios SOLID**
- **S**: Single Responsibility Principle
- **O**: Open/Closed Principle
- **L**: Liskov Substitution Principle
- **I**: Interface Segregation Principle
- **D**: Dependency Inversion Principle

#### **DRY (Don't Repeat Yourself)**
```python
# ❌ Malo
def create_user_endpoint():
    # Validación duplicada
    if not email:
        raise HTTPException(400, "Email required")
    if not username:
        raise HTTPException(400, "Username required")

def update_user_endpoint():
    # Validación duplicada
    if not email:
        raise HTTPException(400, "Email required")
    if not username:
        raise HTTPException(400, "Username required")

# ✅ Bueno
def validate_user_data(data: dict):
    if not data.get("email"):
        raise HTTPException(400, "Email required")
    if not data.get("username"):
        raise HTTPException(400, "Username required")
```

### **2. Manejo de Errores**

#### **Excepciones Específicas**
```python
# ❌ Malo
try:
    user = create_user(data)
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(500, "Internal error")

# ✅ Bueno
try:
    user = create_user(data)
except ValueError as e:
    logger.warning(f"Validation error: {e}")
    raise HTTPException(400, str(e))
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(500, "Database error")
```

### **3. Performance**

#### **Consultas Eficientes**
```python
# ❌ Malo (N+1 queries)
users = db.query(User).all()
for user in users:
    print(user.profile.name)  # Query adicional por usuario

# ✅ Bueno (1 query con join)
users = db.query(User).join(Profile).all()
for user in users:
    print(user.profile.name)  # Sin queries adicionales
```

#### **Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_by_id(user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()
```

### **4. Seguridad**

#### **Validación de Entrada**
```python
from pydantic import BaseModel, validator

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password too short')
        return v
```

#### **Sanitización**
```python
import html

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    return html.escape(text.strip())
```

---

## 📞 Soporte

### **Recursos Adicionales**
- **Documentación**: [docs/README.md](docs/README.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Deployment**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### **Contacto**
- **Email**: dev@yourapp.com
- **GitHub Issues**: [Reportar problemas](https://github.com/yourusername/issues)
- **Discord**: [Comunidad de desarrolladores](https://discord.gg/yourapp)
- **Stack Overflow**: Tag `business-api-template`

---

*Esta guía se actualiza con cada nueva versión. Para la versión más reciente, consulta el repositorio del proyecto.*