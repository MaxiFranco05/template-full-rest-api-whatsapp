# Business API Template - Documentación Completa

## 📚 Índice de Documentación

### 📖 Documentación Principal

1. **[README.md](README.md)** - Documentación completa del template
   - Instalación y configuración
   - Estructura del proyecto
   - API endpoints
   - Sistema de WhatsApp
   - Base de datos
   - Despliegue

2. **[WHATSAPP.md](WHATSAPP.md)** - Sistema de WhatsApp Business API
   - Configuración inicial
   - Flujo de mensajes
   - Estados de conversación
   - Personalización de mensajes
   - API de WhatsApp
   - Monitoreo y estadísticas

3. **[LOGGING_AND_ERRORS.md](LOGGING_AND_ERRORS.md)** - Sistema de Logs y Manejo de Errores
   - Configuración de logging
   - Formato de logs
   - Loggers especializados
   - Manejo de errores
   - Monitoreo y debugging

4. **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guía de Desarrollo
   - Configuración del entorno
   - Comandos útiles
   - Testing
   - Debugging
   - Herramientas de desarrollo

5. **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Guía de Migración Redis/Celery
   - Cómo funciona sin Redis/Celery
   - Cuándo necesitar Redis/Celery
   - Instalación paso a paso
   - Configuración gradual
   - Troubleshooting

## 🚀 Inicio Rápido

### Instalación

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd business-api-template

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# 6. Ejecutar migraciones
alembic upgrade head

# 7. Ejecutar aplicación
python main.py
```

### URLs de Desarrollo

- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📋 Características Principales

### ✅ API RESTful
- Autenticación JWT completa
- Gestión de usuarios y productos/servicios
- Paginación y filtros
- Validación de datos con Pydantic
- Documentación automática con Swagger

### ✅ Sistema de WhatsApp Business
- Webhook para recibir mensajes
- Máquina de estados para conversaciones
- Mensajes personalizables con tags
- Integración completa con WhatsApp Business API
- Manejo de diferentes tipos de mensajes

### ✅ Base de Datos Multi-Soporte
- SQLite para desarrollo
- PostgreSQL y MySQL para producción
- Migraciones con Alembic
- Modelos SQLAlchemy con relaciones

### ✅ Sistema de Logs Profesional
- Logs estructurados en formato JSON
- Rotación automática de archivos
- Loggers especializados por módulo
- Monitoreo de performance y errores

### ✅ Manejo de Errores Robusto
- Excepciones personalizadas
- Respuestas de error estandarizadas
- Logging automático de errores
- Recuperación y reintentos

## 🔧 Configuración

### Variables de Entorno Principales

```env
# Base de datos
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./business_api.db

# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token

# Seguridad
SECRET_KEY=your-secret-key
DEBUG=True

# Empresa (personalizable)
COMPANY_NAME=Tu Empresa
COMPANY_PHONE=+1234567890
COMPANY_EMAIL=contacto@tuempresa.com
```

## 📊 Monitoreo

### Logs Disponibles

- `logs/app.log` - Logs generales de la aplicación
- `logs/errors.log` - Solo errores y excepciones
- `logs/whatsapp.log` - Logs específicos de WhatsApp

### Comandos de Monitoreo

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Ver solo errores
tail -f logs/errors.log

# Ver logs de WhatsApp
tail -f logs/whatsapp.log

# Verificar estado de la API
curl http://localhost:8000/health
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=app

# Tests específicos
pytest app/tests/test_whatsapp.py
```

### Testing de WhatsApp

```bash
# Verificar webhook
curl "http://localhost:8000/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test&hub.verify_token=tu_token"

# Enviar mensaje de prueba
curl -X POST "http://localhost:8000/api/v1/whatsapp/send-message" \
  -H "Content-Type: application/json" \
  -d '{"to": "5511999999999", "message": "Mensaje de prueba"}'
```

## 🚀 Despliegue

### Desarrollo

```bash
python main.py
```

### Producción

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
docker build -t cafe-api .
docker run -p 8000:8000 cafe-api
```

## 📞 Soporte

### Recursos

- **Documentación API**: http://localhost:8000/docs
- **Issues**: Crear issue en el repositorio
- **Email**: soporte@cafeapi.com

### Troubleshooting

1. **Error de importación**: Activar entorno virtual
2. **Error de base de datos**: Ejecutar `alembic upgrade head`
3. **Webhook no funciona**: Verificar variables de entorno y URL accesible
4. **Logs no se generan**: Verificar permisos de escritura en `logs/`

## 📈 Roadmap

### Próximas Características

- [ ] Integración con más plataformas de mensajería
- [ ] Dashboard de administración
- [ ] Análisis de sentimientos en mensajes
- [ ] Respuestas automáticas con IA
- [ ] Integración con CRM
- [ ] Métricas avanzadas y analytics
- [ ] Sistema de citas y reservas
- [ ] Integración con sistemas de pago
- [ ] Notificaciones push
- [ ] API de terceros

### Versiones

- **v1.0.0** - Versión inicial con WhatsApp Business API
- **v1.1.0** - Mejoras en máquina de estados
- **v1.2.0** - Dashboard de administración
- **v2.0.0** - Múltiples plataformas de mensajería

---

**Business API Template v1.0.0** - Template profesional para APIs de negocio con WhatsApp Business API

Para más información, consulta la documentación específica en cada archivo.
