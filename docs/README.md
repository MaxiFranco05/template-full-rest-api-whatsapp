# Business API Template - Documentación Completa

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Instalación y Configuración](#instalación-y-configuración)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [API Endpoints](#api-endpoints)
5. [Sistema de WhatsApp](#sistema-de-whatsapp)
6. [Base de Datos](#base-de-datos)
7. [Sistema de Logs](#sistema-de-logs)
8. [Manejo de Errores](#manejo-de-errores)
9. [Despliegue](#despliegue)
10. [Troubleshooting](#troubleshooting)

## 🚀 Introducción

Business API Template es una aplicación profesional construida con FastAPI que incluye:

- **API RESTful** para gestión de productos/servicios y usuarios
- **Sistema de WhatsApp Business** con webhook y máquina de estados inteligente
- **Base de datos multi-soporte** (SQLite, PostgreSQL, MySQL)
- **Sistema de logs profesional** con formato JSON y debugging avanzado
- **Manejo de errores robusto** con respuestas estandarizadas
- **Autenticación JWT** completa
- **Documentación automática** con Swagger UI
- **Logs de desarrollo** para debugging detallado

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- Git
- (Opcional) PostgreSQL o MySQL para producción

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd business-api-template
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

6. **Ejecutar migraciones**
```bash
alembic upgrade head
```

7. **Ejecutar la aplicación**
```bash
python main.py
```

La aplicación estará disponible en:
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Estructura del Proyecto

```
business-api-template/
├── app/
│   ├── api/v1/endpoints/        # Endpoints de la API
│   │   ├── auth.py             # Autenticación
│   │   ├── products.py         # Gestión de productos/servicios
│   │   └── whatsapp.py         # Webhook de WhatsApp
│   ├── core/
│   │   ├── config.py           # Configuración
│   │   ├── security.py         # JWT y seguridad
│   │   ├── logging_config.py   # Sistema de logs
│   │   └── error_handling.py   # Manejo de errores
│   ├── db/
│   │   └── database.py         # Configuración de BD
│   ├── models/
│   │   └── __init__.py         # Modelos SQLAlchemy
│   ├── schemas/
│   │   └── __init__.py         # Esquemas Pydantic
│   ├── services/
│   │   ├── message_service.py  # Gestión de mensajes
│   │   ├── conversation_service.py # Máquina de estados
│   │   ├── whatsapp_service.py # Integración WhatsApp
│   │   ├── user_service.py     # Gestión de usuarios
│   │   └── product_service.py  # Gestión de productos/servicios
│   ├── data/
│   │   └── messages.yaml       # Mensajes con tags
│   ├── utils/
│   │   ├── helpers.py          # Utilidades generales
│   │   ├── feature_detection.py # Detección de características
│   │   └── simple_cache.py     # Cache simple
│   ├── static/                 # Archivos estáticos
│   └── templates/              # Templates HTML
├── alembic/                    # Migraciones de BD
├── logs/                       # Archivos de logs
├── docs/                       # Documentación
├── main.py                     # Aplicación principal
├── requirements.txt            # Dependencias
├── pyproject.toml              # Configuración del proyecto
└── env.example                 # Variables de entorno
```

## 🔌 API Endpoints

### Autenticación

#### `POST /api/v1/auth/register`
Registrar nuevo usuario

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "Full Name"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "created_at": "2025-01-09T23:00:00Z"
}
```

#### `POST /api/v1/auth/login`
Iniciar sesión

**Request Body:**
```
username=username&password=password123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### `GET /api/v1/auth/me`
Obtener información del usuario actual

**Headers:**
```
Authorization: Bearer <token>
```

### Productos/Servicios

#### `GET /api/v1/products/`
Listar productos/servicios con paginación

**Query Parameters:**
- `page`: Número de página (default: 1)
- `size`: Tamaño de página (default: 10, max: 100)
- `category_id`: Filtrar por categoría
- `search`: Buscar por nombre o descripción

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Producto/Servicio",
      "description": "Descripción del producto/servicio",
      "price": 250,
      "category_id": 1,
      "stock_quantity": 100,
      "is_available": true,
      "created_at": "2025-01-09T23:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

#### `POST /api/v1/products/`
Crear nuevo producto/servicio (requiere autenticación)

**Request Body:**
```json
{
  "name": "Nuevo Producto/Servicio",
  "description": "Descripción del producto/servicio",
  "price": 500,
  "category_id": 1,
  "stock_quantity": 50,
  "is_available": true
}
```

### WhatsApp

#### `GET /api/v1/whatsapp/webhook`
Verificación del webhook de WhatsApp

**Query Parameters:**
- `hub.mode`: Debe ser "subscribe"
- `hub.challenge`: Challenge string de WhatsApp
- `hub.verify_token`: Token de verificación

#### `POST /api/v1/whatsapp/webhook`
Recibir webhooks de WhatsApp

**Request Body:** (JSON enviado por WhatsApp)
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15550559999",
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "messages": [
              {
                "from": "5511999999999",
                "id": "wamid.xxx",
                "timestamp": "1234567890",
                "text": {
                  "body": "Hola"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

#### `GET /api/v1/whatsapp/conversations`
Obtener estadísticas de conversaciones

**Response:**
```json
{
  "stats": {
    "total_conversations": 5,
    "active_conversations": 2,
    "idle_conversations": 3
  },
  "active_conversations": [
    {
      "conversation_id": "5511999999999",
      "state": "active",
      "message_count": 3,
      "last_activity": "2025-01-09T23:00:00Z",
      "is_new_user": false
    }
  ]
}
```

## 📱 Sistema de WhatsApp

### Configuración

1. **Crear aplicación en Facebook Developers**
2. **Configurar WhatsApp Business API**
3. **Obtener credenciales:**
   - Access Token
   - Phone Number ID
   - Webhook Verify Token

4. **Configurar variables de entorno:**
```env
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token
```

### Flujo de Mensajes

1. **Usuario envía mensaje** → WhatsApp Business API
2. **WhatsApp envía webhook** → Nuestra API
3. **Sistema procesa mensaje** → Máquina de estados
4. **Respuesta automática** → WhatsApp Business API
5. **Usuario recibe respuesta** → WhatsApp

### Estados de Conversación

- `initial`: Estado inicial
- `waiting_welcome`: Esperando enviar bienvenida
- `active`: Conversación activa
- `processing`: Procesando mensaje
- `waiting_response`: Esperando respuesta del usuario
- `idle`: Conversación inactiva
- `ended`: Conversación terminada

### Mensajes Personalizables

Los mensajes se configuran en `app/data/messages.yaml`:

```yaml
messages:
  welcome:
    new_user: |
      ¡Hola! 👋 
      
      Bienvenido/a a nuestro servicio de atención al cliente. 
      
      Soy tu asistente virtual y estoy aquí para ayudarte con cualquier consulta que tengas sobre nuestros productos y servicios.
      
      ¿En qué puedo ayudarte hoy? 😊
    
    returning_user: |
      ¡Hola de nuevo! 👋
      
      Me alegra verte otra vez. 
      
      ¿Hay algo en lo que pueda ayudarte hoy? Estoy aquí para resolver cualquier duda que tengas.
  
  error:
    general: |
      Lo siento, ha ocurrido un error técnico. 😔
      
      Por favor, intenta de nuevo en unos minutos o contacta con nuestro equipo de soporte.
```

## 🗄️ Base de Datos

### Modelos

#### Usuario
```python
class User(BaseModel):
    email: str
    username: str
    full_name: Optional[str]
    hashed_password: str
    is_superuser: bool
    is_verified: bool
```

#### Usuario de WhatsApp
```python
class WhatsAppUser(BaseModel):
    phone_number: str
    name: Optional[str]
    profile_name: Optional[str]
    is_business: bool
    first_message_at: Optional[datetime]
    last_message_at: Optional[datetime]
    message_count: int
    is_blocked: bool
    user_metadata: Optional[dict]
```

#### Conversación de WhatsApp
```python
class WhatsAppConversation(BaseModel):
    user_id: int
    conversation_id: str
    current_state: str
    message_count: int
    started_at: datetime
    last_activity_at: datetime
    ended_at: Optional[datetime]
    context: Optional[dict]
```

#### Mensaje de WhatsApp
```python
class WhatsAppMessage(BaseModel):
    conversation_id: int
    message_id: str
    direction: str  # 'inbound' o 'outbound'
    message_type: str  # 'text', 'image', 'audio', etc.
    content: Optional[str]
    media_url: Optional[str]
    timestamp: datetime
    status: str  # 'sent', 'delivered', 'read', 'failed'
    message_metadata: Optional[dict]
```

### Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

## 📊 Sistema de Logs

### Configuración

Los logs se configuran automáticamente al iniciar la aplicación:

- **Console**: Logs en tiempo real
- **Archivo**: `logs/app.log` (rotación automática)
- **Errores**: `logs/errors.log`
- **WhatsApp**: `logs/whatsapp.log`

### Logs de Desarrollo

Cuando `DEBUG=True`, el sistema incluye logs detallados para debugging:

- **Webhook completo**: Estructura exacta de datos recibidos de WhatsApp
- **Mensaje individual**: Datos específicos de cada mensaje
- **Estado de conversación**: Información detallada del estado actual
- **Errores detallados**: Contexto completo cuando ocurren errores
- **Payloads de envío**: Datos exactos enviados a WhatsApp API

### Formato de Logs

Los logs se guardan en formato JSON:

```json
{
  "timestamp": "2025-01-09T23:00:00Z",
  "level": "INFO",
  "logger": "whatsapp",
  "message": "Mensaje procesado: wamid.xxx para 5511999999999",
  "module": "whatsapp_service",
  "function": "process_incoming_message",
  "line": 245,
  "message_id": "wamid.xxx",
  "phone_number": "5511999999999",
  "conversation_id": "5511999999999",
  "status": "processed"
}
```

### Loggers Especializados

```python
from app.core.logging_config import whatsapp_logger, api_logger

# Log de WhatsApp
whatsapp_logger.log_message_processed(
    message_id="wamid.xxx",
    phone_number="5511999999999",
    conversation_id="5511999999999",
    status="processed"
)

# Log de API
api_logger.log_request("POST", "/api/v1/whatsapp/webhook", request_id="uuid")
```

## ⚠️ Manejo de Errores

### Tipos de Errores

#### Errores de Aplicación
```python
from app.core.error_handling import WhatsAppException

raise WhatsAppException(
    "Error enviando mensaje",
    "SEND_MESSAGE_FAILED",
    phone_number="5511999999999"
)
```

#### Errores de Validación
```python
from app.core.error_handling import ValidationException

raise ValidationException(
    "Email inválido",
    field="email",
    value="invalid-email"
)
```

#### Errores de Autenticación
```python
from app.core.error_handling import AuthenticationException

raise AuthenticationException("Credenciales inválidas")
```

### Respuesta de Error Estándar

```json
{
  "error": {
    "code": "WHATSAPP_SEND_ERROR",
    "message": "Error enviando mensaje",
    "timestamp": "2025-01-09T23:00:00Z",
    "status_code": 400,
    "details": {
      "phone_number": "5511999999999"
    }
  }
}
```

### Decorador de Manejo de Errores

```python
from app.core.error_handling import handle_errors

@handle_errors("FUNCTION_ERROR")
async def my_function():
    # Tu código aquí
    pass
```

## 🚀 Despliegue

### Desarrollo

```bash
python main.py
```

### Producción con Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Variables de Entorno de Producción

```env
# Base de datos
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./business_api.db
# Para producción usar PostgreSQL:
# DATABASE_TYPE=postgresql
# DATABASE_URL=postgresql://user:password@localhost:5432/business_db

# Seguridad
SECRET_KEY=your-super-secret-key-here
DEBUG=False

# WhatsApp
WHATSAPP_ACCESS_TOKEN=your-production-token
WHATSAPP_PHONE_NUMBER_ID=your-production-phone-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-production-verify-token

# Empresa (personalizable)
COMPANY_NAME=Tu Empresa
COMPANY_PHONE=+1234567890
COMPANY_EMAIL=contacto@tuempresa.com
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Importación
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solución:** Activar el entorno virtual
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

#### 2. Error de Base de Datos
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table
```
**Solución:** Ejecutar migraciones
```bash
alembic upgrade head
```

#### 3. Webhook de WhatsApp no funciona
**Verificar:**
- Variables de entorno configuradas
- URL del webhook accesible desde internet
- Token de verificación correcto

#### 4. Logs no se generan
**Verificar:**
- Permisos de escritura en directorio `logs/`
- Configuración de logging en `app/core/logging_config.py`

### Comandos Útiles

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Ver solo errores
tail -f logs/errors.log

# Ver logs de WhatsApp
tail -f logs/whatsapp.log

# Reiniciar aplicación
pkill -f "python main.py"
python main.py

# Verificar estado de la API
curl http://localhost:8000/health
```

### Contacto y Soporte

Para soporte técnico o preguntas:
- **Email**: soporte@cafeapi.com
- **Documentación**: http://localhost:8000/docs
- **Issues**: Crear issue en el repositorio

---

**Business API Template v1.0.0** - Template profesional para APIs de negocio con WhatsApp Business API
