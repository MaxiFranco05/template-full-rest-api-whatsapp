# WhatsApp Business API Template

Template profesional para proyectos con integración de WhatsApp Business API construido con FastAPI.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para APIs
- **WhatsApp Business API**: Integración completa con webhook y máquina de estados
- **SQLAlchemy**: ORM para manejo de base de datos
- **Multi-DB Support**: SQLite, PostgreSQL, MySQL
- **JWT**: Autenticación con tokens
- **Pydantic**: Validación de datos
- **Alembic**: Migraciones de base de datos
- **Logging**: Sistema de logs profesional con formato JSON
- **Error Handling**: Manejo robusto de errores
- **Testing**: Suite de pruebas con pytest
- **Documentación**: Swagger UI automática

## 📁 Estructura del Proyecto

```
whatsapp-api-template/
├── app/
│   ├── api/v1/endpoints/        # Endpoints de la API
│   │   ├── auth.py             # Autenticación
│   │   ├── products.py         # Gestión de productos
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
│   │   └── product_service.py  # Gestión de productos
│   ├── data/
│   │   └── messages.yaml       # Mensajes con tags
│   └── utils/
│       └── helpers.py
├── alembic/                    # Migraciones de BD
├── docs/                       # Documentación
├── main.py                     # Aplicación principal
├── requirements.txt            # Dependencias
└── env.example                 # Variables de entorno
```

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd whatsapp-api-template
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

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` con las siguientes variables:

```env
# Base de datos
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./whatsapp_template.db

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token

# Seguridad
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Redis (opcional)
REDIS_URL=redis://localhost:6379
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

## 📚 API Endpoints

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/me` - Obtener usuario actual

### Productos
- `GET /api/v1/products/` - Listar productos
- `GET /api/v1/products/{id}` - Obtener producto
- `POST /api/v1/products/` - Crear producto
- `PUT /api/v1/products/{id}` - Actualizar producto
- `DELETE /api/v1/products/{id}` - Eliminar producto

### WhatsApp
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
docker build -t whatsapp-api-template .

# Ejecutar contenedor
docker run -p 8000:8000 whatsapp-api-template
```

### Producción

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar con gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
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

- **Tu Nombre** - *Trabajo inicial* - [tu-usuario](https://github.com/gastonfr24)

## 🙏 Agradecimientos

- FastAPI por el excelente framework
- WhatsApp Business API por la plataforma de mensajería
- SQLAlchemy por el ORM robusto