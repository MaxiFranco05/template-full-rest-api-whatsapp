# Guía de Desarrollo

## 🚀 Inicio Rápido

### 1. Configuración del Entorno

```bash
# Clonar repositorio
git clone <repository-url>
cd cafe-api

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
alembic upgrade head

# Ejecutar aplicación
python main.py
```

### 2. URLs de Desarrollo

- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🛠️ Comandos Útiles

### Desarrollo

```bash
# Ejecutar con recarga automática
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar con logs detallados
uvicorn main:app --log-level debug

# Ejecutar en modo desarrollo
DEBUG=True python main.py
```

### Base de Datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial de migraciones
alembic history

# Ver migración actual
alembic current
```

### Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=app

# Ejecutar tests específicos
pytest app/tests/test_whatsapp.py

# Ejecutar tests en modo verbose
pytest -v

# Ejecutar tests con logs
pytest -s
```

### Linting y Formateo

```bash
# Formatear código con Black
black app/

# Ordenar imports con isort
isort app/

# Verificar linting con flake8
flake8 app/

# Verificar tipos con mypy
mypy app/
```

## 🔧 Configuración de Desarrollo

### Variables de Entorno

```env
# Desarrollo
DEBUG=True
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./cafe_whatsapp.db

# WhatsApp (usar tokens de prueba)
WHATSAPP_ACCESS_TOKEN=test_token
WHATSAPP_PHONE_NUMBER_ID=test_phone_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=test_verify_token

# Logging
LOG_LEVEL=DEBUG
```

### Configuración de IDE

#### VS Code

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "files.associations": {
        "*.yaml": "yaml",
        "*.yml": "yaml"
    }
}
```

#### PyCharm

1. Configurar Python interpreter: `venv/Scripts/python.exe`
2. Habilitar inspections: PEP 8, PyLint
3. Configurar formatter: Black
4. Configurar imports: isort

## 🧪 Testing

### Estructura de Tests

```
app/tests/
├── __init__.py
├── conftest.py          # Configuración de pytest
├── test_main.py         # Tests de la aplicación principal
├── test_auth.py         # Tests de autenticación
├── test_products.py     # Tests de productos
├── test_whatsapp.py     # Tests de WhatsApp
└── test_services/       # Tests de servicios
    ├── test_message_service.py
    ├── test_conversation_service.py
    └── test_whatsapp_service.py
```

### Configuración de Tests

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.database import get_db, Base
from main import app

# Base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)
```

### Ejemplos de Tests

```python
# test_whatsapp.py
import pytest
from fastapi.testclient import TestClient

def test_webhook_verification(client: TestClient):
    response = client.get(
        "/api/v1/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge",
            "hub.verify_token": "test_token"
        }
    )
    assert response.status_code == 200
    assert response.text == "test_challenge"

def test_send_message(client: TestClient):
    response = client.post(
        "/api/v1/whatsapp/send-message",
        params={
            "to": "5511999999999",
            "message": "Test message"
        }
    )
    assert response.status_code == 200
    assert "message_id" in response.json()

def test_conversations_endpoint(client: TestClient):
    response = client.get("/api/v1/whatsapp/conversations")
    assert response.status_code == 200
    assert "stats" in response.json()
```

## 🔍 Debugging

### Logs de Desarrollo

```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)

# Log específico
logger = logging.getLogger(__name__)
logger.debug("Mensaje de debug")
logger.info("Mensaje informativo")
logger.warning("Mensaje de advertencia")
logger.error("Mensaje de error")
```

### Debugging con pdb

```python
import pdb

def my_function():
    pdb.set_trace()  # Punto de interrupción
    # Tu código aquí
```

### Debugging con VS Code

1. Crear archivo `.vscode/launch.json`:

```json
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
                "DEBUG": "True"
            }
        }
    ]
}
```

2. Presionar F5 para iniciar debugging

## 📦 Estructura de Código

### Convenciones

1. **Nombres de archivos**: snake_case
2. **Nombres de clases**: PascalCase
3. **Nombres de funciones**: snake_case
4. **Constantes**: UPPER_CASE
5. **Variables**: snake_case

### Imports

```python
# Orden de imports
import os
import sys
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.whatsapp_service import whatsapp_service
```

### Documentación

```python
def process_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesar mensaje de WhatsApp entrante.
    
    Args:
        message_data: Datos del mensaje parseado
        
    Returns:
        Dict con resultado del procesamiento
        
    Raises:
        WhatsAppException: Si hay error procesando el mensaje
    """
    pass
```

## 🚀 Despliegue de Desarrollo

### Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DATABASE_TYPE=sqlite
    volumes:
      - .:/app
      - ./logs:/app/logs
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Scripts de Desarrollo

```bash
# scripts/dev.sh
#!/bin/bash

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Ejecutar aplicación
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Herramientas de Desarrollo

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Makefile

```makefile
# Makefile
.PHONY: install test lint format run dev

install:
	pip install -r requirements.txt

test:
	pytest

lint:
	flake8 app/
	mypy app/

format:
	black app/
	isort app/

run:
	python main.py

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
```

## 📚 Recursos Adicionales

### Documentación

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

### Herramientas

- [Postman](https://www.postman.com/) - Testing de APIs
- [ngrok](https://ngrok.com/) - Tunneling para webhooks
- [DBeaver](https://dbeaver.io/) - Cliente de base de datos
- [VS Code](https://code.visualstudio.com/) - Editor recomendado

---

**Guía de Desarrollo** - Configuración completa para desarrollo eficiente y profesional.
