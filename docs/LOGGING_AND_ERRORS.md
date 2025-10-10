# Sistema de Logs y Manejo de Errores

## 📊 Sistema de Logging

### Configuración

El sistema de logging se configura automáticamente al iniciar la aplicación en `app/core/logging_config.py`:

```python
from app.core.logging_config import setup_logging

# Configurar logging al inicio de la aplicación
setup_logging()
```

### Estructura de Logs

```
logs/
├── app.log          # Logs generales de la aplicación
├── errors.log       # Solo errores y excepciones
└── whatsapp.log     # Logs específicos de WhatsApp
```

### Formato de Logs

Los logs se guardan en formato JSON estructurado:

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

#### WhatsApp Logger

```python
from app.core.logging_config import whatsapp_logger

# Log de mensaje procesado
whatsapp_logger.log_message_processed(
    message_id="wamid.xxx",
    phone_number="5511999999999",
    conversation_id="5511999999999",
    status="processed"
)

# Log de mensaje enviado
whatsapp_logger.log_message_sent(
    message_id="wamid.yyy",
    phone_number="5511999999999",
    success=True
)

# Log de cambio de estado
whatsapp_logger.log_conversation_state_change(
    conversation_id="5511999999999",
    old_state="initial",
    new_state="active"
)

# Log de error
whatsapp_logger.log_error(
    error=exception,
    context={"phone_number": "5511999999999", "operation": "send_message"}
)
```

#### API Logger

```python
from app.core.logging_config import api_logger

# Log de request
api_logger.log_request(
    method="POST",
    path="/api/v1/whatsapp/webhook",
    request_id="uuid-123"
)

# Log de response
api_logger.log_response(
    method="POST",
    path="/api/v1/whatsapp/webhook",
    status_code=200,
    response_time=0.125,
    request_id="uuid-123"
)

# Log de autenticación
api_logger.log_authentication(
    user_id="123",
    success=True,
    ip_address="192.168.1.1"
)
```

### Configuración de Niveles

```python
# En desarrollo
DEBUG = True
# Logs: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Incluye logs de desarrollo detallados para debugging

# En producción
DEBUG = False
# Logs: INFO, WARNING, ERROR, CRITICAL
# Solo logs esenciales para producción
```

### Logs de Desarrollo

Cuando `DEBUG=True`, el sistema incluye logs detallados para debugging:

#### WhatsApp Service Debugging

```json
{
  "timestamp": "2025-01-09T23:00:00Z",
  "level": "INFO",
  "logger": "app.services.whatsapp_service",
  "message": "[DESARROLLO] Webhook recibido completo: {...}",
  "module": "whatsapp_service",
  "function": "parse_webhook_data"
}
```

Los logs de desarrollo incluyen:

- **Webhook completo**: Estructura exacta de datos recibidos de WhatsApp
- **Mensaje individual**: Datos específicos de cada mensaje
- **Mensaje parseado**: Estructura interna del mensaje procesado
- **Estado de conversación**: Información detallada del estado actual
- **Errores detallados**: Contexto completo cuando ocurren errores
- **Payloads de envío**: Datos exactos enviados a WhatsApp API
- **Verificación de webhook**: Detalles de tokens y challenges

### Rotación de Archivos

Los archivos de log se rotan automáticamente:
- **Tamaño máximo**: 10MB por archivo
- **Archivos de respaldo**: 5 archivos
- **Compresión**: Automática

## ⚠️ Sistema de Manejo de Errores

### Tipos de Errores

#### 1. Errores de Aplicación

```python
from app.core.error_handling import AppException

class WhatsAppException(AppException):
    def __init__(self, message: str, error_code: str = None, 
                 phone_number: str = None):
        super().__init__(
            message=message,
            error_code=error_code or "WHATSAPP_ERROR",
            status_code=400,
            details={"phone_number": phone_number}
        )
```

#### 2. Errores de Validación

```python
from app.core.error_handling import ValidationException

raise ValidationException(
    "Email inválido",
    field="email",
    value="invalid-email"
)
```

#### 3. Errores de Autenticación

```python
from app.core.error_handling import AuthenticationException

raise AuthenticationException("Credenciales inválidas")
```

#### 4. Errores de Base de Datos

```python
from app.core.error_handling import DatabaseException

raise DatabaseException(
    "Error al guardar usuario",
    table="users",
    operation="insert"
)
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
      "phone_number": "5511999999999",
      "error_type": "invalid_phone_number"
    },
    "request_id": "uuid-123"
  }
}
```

### Manejadores de Excepciones

#### 1. Excepciones de Aplicación

```python
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.error(
        f"App Exception: {exc.message}",
        extra={
            'error_code': exc.error_code,
            'status_code': exc.status_code,
            'details': exc.details,
            'path': request.url.path,
            'method': request.method
        }
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )
```

#### 2. Excepciones de Validación

```python
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        status_code=422,
        message="Error de validación en los datos enviados",
        error_code="VALIDATION_ERROR",
        details={"validation_errors": errors}
    )
```

#### 3. Excepciones Generales

```python
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            'exception_type': type(exc).__name__,
            'path': request.url.path,
            'method': request.method,
            'traceback': traceback.format_exc()
        },
        exc_info=True
    )
    
    return create_error_response(
        status_code=500,
        message="Error interno del servidor",
        error_code="INTERNAL_SERVER_ERROR"
    )
```

### Decorador de Manejo de Errores

```python
from app.core.error_handling import handle_errors

@handle_errors("WHATSAPP_SEND_ERROR")
async def send_whatsapp_message(to: str, message: str):
    # Tu código aquí
    # Si ocurre una excepción, se maneja automáticamente
    pass
```

### Middleware de Logging

```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    import time
    import uuid
    
    # Generar ID único para la request
    request_id = str(uuid.uuid4())
    
    # Log de request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            'request_id': request_id,
            'method': request.method,
            'path': request.url.path,
            'client_ip': request.client.host
        }
    )
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log de response
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)",
            extra={
                'request_id': request_id,
                'status_code': response.status_code,
                'process_time': process_time
            }
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} - {str(e)} ({process_time:.3f}s)",
            extra={
                'request_id': request_id,
                'error': str(e)
            },
            exc_info=True
        )
        raise
```

## 🔍 Monitoreo y Debugging

### Comandos de Monitoreo

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Ver solo errores
tail -f logs/errors.log

# Ver logs de WhatsApp
tail -f logs/whatsapp.log

# Ver solo logs de desarrollo
tail -f logs/app.log | grep "\[DESARROLLO\]"

# Buscar errores específicos
grep "ERROR" logs/app.log

# Buscar por request ID
grep "uuid-123" logs/app.log

# Ver estadísticas de logs
wc -l logs/*.log
```

### Análisis de Logs

#### 1. Análisis de Errores

```bash
# Contar errores por tipo
grep -o '"error_code":"[^"]*"' logs/errors.log | sort | uniq -c

# Errores más frecuentes
grep -o '"message":"[^"]*"' logs/errors.log | sort | uniq -c | sort -nr

# Errores por endpoint
grep -o '"path":"[^"]*"' logs/errors.log | sort | uniq -c
```

#### 2. Análisis de Performance

```bash
# Requests más lentos
grep '"process_time":' logs/app.log | jq -r '.process_time' | sort -nr | head -10

# Promedio de tiempo de respuesta
grep '"process_time":' logs/app.log | jq -r '.process_time' | awk '{sum+=$1; count++} END {print sum/count}'
```

#### 3. Análisis de WhatsApp

```bash
# Mensajes procesados por día
grep "$(date +%Y-%m-%d)" logs/whatsapp.log | grep "Mensaje procesado" | wc -l

# Estados de conversación más comunes
grep -o '"new_state":"[^"]*"' logs/whatsapp.log | sort | uniq -c

# Errores de envío
grep '"success":false' logs/whatsapp.log | wc -l
```

### Alertas y Notificaciones

#### 1. Script de Monitoreo

```bash
#!/bin/bash
# monitor.sh

# Verificar si hay muchos errores
ERROR_COUNT=$(grep "$(date +%Y-%m-%d)" logs/errors.log | wc -l)
if [ $ERROR_COUNT -gt 100 ]; then
    echo "ALERTA: $ERROR_COUNT errores hoy"
    # Enviar notificación
fi

# Verificar si la API está respondiendo
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "ALERTA: API no responde"
    # Enviar notificación
fi
```

#### 2. Configuración de Cron

```bash
# Ejecutar monitoreo cada 5 minutos
*/5 * * * * /path/to/monitor.sh
```

## 🛠️ Configuración Avanzada

### Personalización de Logs

```python
# En app/core/logging_config.py

# Cambiar formato de logs
"formatters": {
    "custom": {
        "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s - %(extra)s"
    }
}

# Cambiar nivel de logging
"loggers": {
    "whatsapp": {
        "level": "DEBUG",  # Cambiar a DEBUG para más detalles
        "handlers": ["console", "whatsapp_file"]
    }
}
```

### Filtros Personalizados

```python
class PhoneNumberFilter(logging.Filter):
    def filter(self, record):
        # Ocultar números de teléfono en logs
        if hasattr(record, 'phone_number'):
            record.phone_number = record.phone_number[:3] + "****" + record.phone_number[-2:]
        return True

# Aplicar filtro
logger.addFilter(PhoneNumberFilter())
```

### Integración con Servicios Externos

#### 1. Sentry para Errores

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1
)
```

#### 2. ELK Stack

```python
# Configurar handler para Elasticsearch
"handlers": {
    "elasticsearch": {
        "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        "formatter": "json",
        "host": "localhost",
        "port": 9200,
        "index": "cafe-api-logs"
    }
}
```

## 📈 Métricas y KPIs

### Métricas Importantes

1. **Tiempo de Respuesta Promedio**
2. **Tasa de Errores**
3. **Mensajes de WhatsApp Procesados**
4. **Conversaciones Activas**
5. **Errores por Tipo**

### Dashboard de Monitoreo

```python
# Endpoint para métricas
@app.get("/api/v1/metrics")
async def get_metrics():
    return {
        "response_time_avg": calculate_avg_response_time(),
        "error_rate": calculate_error_rate(),
        "whatsapp_messages_today": count_whatsapp_messages_today(),
        "active_conversations": len(conversation_manager.conversations),
        "errors_by_type": get_errors_by_type()
    }
```

---

**Sistema de Logs y Manejo de Errores** - Monitoreo profesional con formato JSON estructurado y manejo robusto de excepciones.
