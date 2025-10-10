# Guía de Migración: Cómo Agregar Redis y Celery

## 🚀 **Estado Actual (Sin Redis/Celery)**

Tu aplicación funciona **perfectamente** sin Redis ni Celery:

- ✅ **Webhook de WhatsApp**: Funciona síncronamente
- ✅ **Máquina de estados**: En memoria (se reinicia con la app)
- ✅ **Base de datos**: SQLite funciona bien
- ✅ **Cache**: Cache simple en memoria
- ✅ **Logs**: Archivos locales

## 🔧 **Cuándo Necesitar Redis/Celery**

### **Redis es útil cuando:**
- Tienes **>1000 conversaciones activas**
- Necesitas **cache persistente** entre reinicios
- Quieres **rate limiting** por usuario
- Necesitas **sesiones compartidas** entre múltiples instancias

### **Celery es útil cuando:**
- Procesas **>100 mensajes/minuto**
- Necesitas **tareas programadas** (mensajes automáticos)
- Quieres **procesamiento en background**
- Implementas **IA o análisis complejo**

## 📦 **Instalación de Redis**

### **Windows**

#### Opción 1: Docker (Recomendado)
```bash
# Instalar Docker Desktop
# Luego ejecutar:
docker run -d -p 6379:6379 --name redis redis:alpine
```

#### Opción 2: WSL2
```bash
# En WSL2
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

#### Opción 3: Chocolatey
```bash
choco install redis-64
redis-server
```

### **Linux/Mac**
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis
```

## 🔧 **Configuración Paso a Paso**

### **1. Instalar Redis**
```bash
# Verificar que Redis esté funcionando
redis-cli ping
# Debe responder: PONG
```

### **2. Actualizar Variables de Entorno**
```env
# Descomentar estas líneas en tu .env
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### **3. Reiniciar la Aplicación**
```bash
# La app detectará automáticamente Redis
python main.py
```

### **4. Verificar que Funcione**
```bash
# Verificar en el endpoint de health
curl http://localhost:8000/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "features": {
    "redis_available": true,
    "celery_available": true,
    "cache": true,
    "async_tasks": true
  }
}
```

## 🚀 **Usar Celery (Opcional)**

### **1. Instalar Celery**
```bash
pip install celery
```

### **2. Ejecutar Worker de Celery**
```bash
# En una terminal separada
celery -A app.celery_app worker --loglevel=info
```

### **3. Ejecutar Scheduler de Celery (Opcional)**
```bash
# En otra terminal separada
celery -A app.celery_app beat --loglevel=info
```

### **4. Usar Tareas Asíncronas**
```python
from app.utils.feature_detection import execute_task
from app.celery_app import process_whatsapp_message_async

# Esto se ejecutará asíncronamente si Celery está disponible
# O síncronamente si no está disponible
result = execute_task(process_whatsapp_message_async, message_data)
```

## 📊 **Beneficios de la Migración**

### **Con Redis:**
- ✅ **Cache persistente** entre reinicios
- ✅ **Mejor performance** para datos frecuentes
- ✅ **Rate limiting** por usuario
- ✅ **Sesiones compartidas**

### **Con Celery:**
- ✅ **Procesamiento asíncrono** de mensajes
- ✅ **Tareas programadas** (mensajes automáticos)
- ✅ **Mejor escalabilidad** con múltiples workers
- ✅ **Procesamiento en background**

## 🔄 **Migración Gradual**

### **Fase 1: Solo Redis (Recomendado)**
```env
# Solo Redis
REDIS_URL=redis://localhost:6379
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### **Fase 2: Redis + Celery**
```env
# Redis + Celery
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🛠️ **Comandos Útiles**

### **Redis**
```bash
# Conectar a Redis
redis-cli

# Ver todas las claves
KEYS *

# Ver información del servidor
INFO

# Limpiar todo
FLUSHALL
```

### **Celery**
```bash
# Ver workers activos
celery -A app.celery_app inspect active

# Ver tareas programadas
celery -A app.celery_app inspect scheduled

# Ver estadísticas
celery -A app.celery_app inspect stats
```

## 🚨 **Troubleshooting**

### **Redis no se conecta**
```bash
# Verificar que Redis esté corriendo
redis-cli ping

# Verificar puerto
netstat -an | grep 6379

# Verificar logs de Redis
redis-cli monitor
```

### **Celery no funciona**
```bash
# Verificar que Redis esté disponible
redis-cli ping

# Verificar worker
celery -A app.celery_app status

# Ver logs detallados
celery -A app.celery_app worker --loglevel=debug
```

## 📈 **Monitoreo**

### **Redis**
```bash
# Ver estadísticas
redis-cli info stats

# Ver memoria usada
redis-cli info memory

# Ver conexiones
redis-cli info clients
```

### **Celery**
```bash
# Ver workers
celery -A app.celery_app inspect active_queues

# Ver tareas completadas
celery -A app.celery_app inspect reserved
```

## 🎯 **Recomendación**

### **Para Empezar:**
1. ✅ **Usa la app sin Redis/Celery** (funciona perfectamente)
2. 🔄 **Cuando tengas >100 conversaciones activas**, agrega Redis
3. 🔄 **Cuando necesites tareas programadas**, agrega Celery

### **Configuración Mínima:**
```env
# Para empezar, deja todo comentado
# REDIS_URL=redis://localhost:6379
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### **Configuración Completa:**
```env
# Cuando necesites escalar
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

**La app funciona perfectamente sin Redis/Celery. Agrégalos solo cuando necesites escalar!** 🚀
