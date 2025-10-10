# Business API Template

Template profesional para APIs de negocio construido con FastAPI. Incluye sistema completo de WhatsApp Business API para cualquier tipo de empresa.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para APIs
- **WhatsApp Business API**: Integración completa con webhook y máquina de estados
- **SQLAlchemy**: ORM para manejo de base de datos
- **Multi-DB**: Soporte para SQLite, PostgreSQL y MySQL
- **JWT**: Autenticación con tokens
- **Pydantic**: Validación de datos
- **Alembic**: Migraciones de base de datos
- **Logging Profesional**: Sistema de logs JSON estructurado
- **Testing**: Suite de pruebas con pytest
- **Documentación**: Swagger UI automática

## 📁 Estructura del Proyecto

```
business-api-template/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── products.py
│   │           └── whatsapp.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging_config.py
│   │   └── error_handling.py
│   ├── db/
│   │   └── database.py         # Configuración de BD
│   ├── models/
│   │   └── __init__.py         # Modelos SQLAlchemy
│   ├── schemas/
│   │   └── __init__.py         # Esquemas Pydantic
│   ├── services/
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── whatsapp_service.py
│   │   ├── conversation_service.py
│   │   ├── message_service.py
│   │   ├── data_config_service.py
│   │   ├── message_validation_service.py
│   │   ├── whatsapp_message_types.py
│   │   └── whatsapp_persistence_service.py
│   ├── data/
│   │   └── messages.yaml
│   ├── utils/
│   │   ├── helpers.py
│   │   ├── feature_detection.py
│   │   └── simple_cache.py
│   ├── static/
│   └── templates/
├── alembic/
├── docs/
├── logs/
├── main.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🛠️ Instalación

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
# Para SQLite (desarrollo - automático)
# La base de datos se crea automáticamente

# Para PostgreSQL (producción)
createdb business_db

# Ejecutar migraciones
alembic upgrade head
```

7. **Ejecutar la aplicación**
```bash
python main.py
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` con las siguientes variables:

```env
# Base de datos
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./business_api.db
# Para producción usar PostgreSQL:
# DATABASE_TYPE=postgresql
# DATABASE_URL=postgresql://user:password@localhost:5432/business_db

# Seguridad
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token

# Información de la empresa
COMPANY_NAME=Tu Empresa
COMPANY_PHONE=+1234567890
COMPANY_EMAIL=contacto@tuempresa.com
COMPANY_ADDRESS=Tu Dirección
COMPANY_WEBSITE=https://tuempresa.com
COMPANY_DESCRIPTION=Descripción de tu empresa

# Redis (opcional)
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 📱 Sistema de WhatsApp

### Configuración de WhatsApp Business API

1. Crear aplicación en [Facebook Developers](https://developers.facebook.com/)
2. Configurar WhatsApp Business API
3. Obtener credenciales:
   - Access Token
   - Phone Number ID
   - Webhook Verify Token
4. Configurar webhook URL: `https://tu-dominio.com/api/v1/whatsapp/webhook`

### Estados de Conversación

- `initial` → `waiting_welcome` → `active` → `processing` → `idle` → `ended`

### Tipos de Mensajes Soportados

- **Texto**: Mensajes simples
- **Botones**: Botones interactivos
- **Listas**: Menús desplegables
- **Media**: Imágenes, videos, documentos
- **Ubicación**: Compartir ubicación
- **Contactos**: Información de contacto
- **Stickers**: Stickers de WhatsApp
- **Plantillas**: Mensajes preaprobados

## 📚 API Endpoints

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/me` - Obtener usuario actual

### Productos/Servicios
- `GET /api/v1/products/` - Listar productos/servicios
- `GET /api/v1/products/{id}` - Obtener producto/servicio
- `POST /api/v1/products/` - Crear producto/servicio
- `PUT /api/v1/products/{id}` - Actualizar producto/servicio
- `DELETE /api/v1/products/{id}` - Eliminar producto/servicio

### WhatsApp Business
- `GET /api/v1/whatsapp/webhook` - Verificar webhook
- `POST /api/v1/whatsapp/webhook` - Recibir mensajes
- `GET /api/v1/whatsapp/conversations` - Estadísticas de conversaciones

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=app

# Ejecutar pruebas específicas
pytest app/tests/test_whatsapp.py
```

## 📖 Documentación

Una vez que la aplicación esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

## 🚀 Despliegue

### Docker

```bash
# Construir imagen
docker build -t business-api .

# Ejecutar contenedor
docker run -p 8000:8000 business-api
```

### Producción

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar con gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🎯 Casos de Uso

Este template es perfecto para:

- **Restaurantes**: Gestión de menús y pedidos por WhatsApp
- **Tiendas Online**: Catálogo de productos y atención al cliente
- **Servicios Profesionales**: Consultorías, clínicas, estudios
- **E-commerce**: Ventas y soporte al cliente
- **Startups**: MVP rápido con WhatsApp Business
- **Empresas**: Sistema interno de gestión y comunicación

## 🔧 Personalización

### 1. Cambiar el Modelo de Productos
Edita `app/models/__init__.py` para adaptar los campos a tu negocio:
```python
class Product(BaseModel):
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    # Agregar campos específicos de tu negocio
    sku: Optional[str]  # Para inventario
    service_duration: Optional[int]  # Para servicios
    availability: Optional[str]  # Para citas
```

### 2. Personalizar Mensajes de WhatsApp
Edita `app/data/messages.yaml`:
```yaml
messages:
  welcome:
    new_user: |
      ¡Hola! 👋 
      Bienvenido/a a [TU EMPRESA]
      ¿En qué puedo ayudarte hoy?
```

### 3. Configurar Variables de Entorno
Personaliza `.env` con tu información:
```env
COMPANY_NAME=Tu Empresa
COMPANY_PHONE=+1234567890
COMPANY_EMAIL=contacto@tuempresa.com
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Template Creator** - *Template inicial* - [tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- FastAPI por el excelente framework
- SQLAlchemy por el ORM robusto
- WhatsApp Business API por la integración
- Comunidad de desarrolladores por las mejores prácticas