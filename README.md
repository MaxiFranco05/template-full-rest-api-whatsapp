# Cafe API

API profesional para gestión de café construida con FastAPI.

## 🚀 Características

- **FastAPI**: Framework moderno y rápido para APIs
- **SQLAlchemy**: ORM para manejo de base de datos
- **PostgreSQL**: Base de datos principal
- **JWT**: Autenticación con tokens
- **Pydantic**: Validación de datos
- **Alembic**: Migraciones de base de datos
- **Testing**: Suite de pruebas con pytest
- **Documentación**: Swagger UI automática

## 📁 Estructura del Proyecto

```
cafe-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           └── products.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   ├── user_service.py
│   │   └── product_service.py
│   ├── utils/
│   │   └── helpers.py
│   ├── static/
│   └── templates/
├── venv/
├── main.py
├── requirements.txt
└── README.md
```

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd cafe-api
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
cp .env.example .env
# Editar .env con tus configuraciones
```

6. **Configurar base de datos**
```bash
# Crear base de datos PostgreSQL
createdb cafe_db

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
DATABASE_URL=postgresql://user:password@localhost:5432/cafe_db

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

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=app

# Ejecutar pruebas específicas
pytest app/tests/test_auth.py
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
docker build -t cafe-api .

# Ejecutar contenedor
docker run -p 8000:8000 cafe-api
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

- **Tu Nombre** - *Trabajo inicial* - [tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- FastAPI por el excelente framework
- SQLAlchemy por el ORM robusto
- PostgreSQL por la base de datos confiable
