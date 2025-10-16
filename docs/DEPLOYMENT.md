# 🚀 Deployment Guide

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Deployment Local](#deployment-local)
4. [Deployment con Docker](#deployment-con-docker)
5. [Deployment en Producción](#deployment-en-producción)
6. [Configuración de Base de Datos](#configuración-de-base-de-datos)
7. [Configuración de WhatsApp](#configuración-de-whatsapp)
8. [Monitoreo y Logs](#monitoreo-y-logs)
9. [Troubleshooting](#troubleshooting)
10. [Mantenimiento](#mantenimiento)

## 🎯 Introducción

Esta guía te ayudará a desplegar Business API Template en diferentes entornos, desde desarrollo local hasta producción en la nube.

### **Entornos Soportados**
- **Desarrollo Local**: Para desarrollo y testing
- **Staging**: Para pruebas pre-producción
- **Producción**: Para usuarios finales

## 💻 Requisitos del Sistema

### **Mínimos**
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.11 o 3.12
- **RAM**: 2GB mínimo, 4GB recomendado
- **CPU**: 2 cores mínimo, 4 cores recomendado
- **Disco**: 10GB espacio libre

### **Recomendados para Producción**
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.12
- **RAM**: 8GB+
- **CPU**: 4+ cores
- **Disco**: 50GB+ SSD
- **Red**: Conexión estable con baja latencia

### **Dependencias**
- **PostgreSQL**: 13+ (producción)
- **Redis**: 6+ (opcional, para cache)
- **Nginx**: 1.18+ (proxy reverso)
- **Docker**: 20+ (containerización)

## 🏠 Deployment Local

### **1. Clonar Repositorio**

```bash
git clone https://github.com/yourusername/business-api-template.git
cd business-api-template
```

### **2. Crear Entorno Virtual**

```bash
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
# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de testing (opcional)
pip install -r tests/requirements-testing.txt
```

### **4. Configurar Variables de Entorno**

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar configuración
nano .env
```

**Configuración mínima para desarrollo:**
```env
# Base de datos
DATABASE_TYPE=sqlite
SQLITE_DATABASE_URL=sqlite:///./business_api.db

# Seguridad
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# WhatsApp (opcional para desarrollo)
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_WEBHOOK_VERIFY_TOKEN=
```

### **5. Inicializar Base de Datos**

```bash
# Ejecutar migraciones
alembic upgrade head

# Crear usuario administrador (opcional)
python scripts/create_admin_user.py
```

### **6. Ejecutar Aplicación**

```bash
# Modo desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# O usando Python directamente
python main.py
```

### **7. Verificar Deployment**

```bash
# Verificar que la aplicación funciona
curl http://localhost:8000/health

# Verificar documentación
# Abrir en navegador: http://localhost:8000/docs
```

## 🐳 Deployment con Docker

### **1. Build de Imagen**

```bash
# Build de imagen
docker build -t business-api-template .

# Verificar imagen
docker images business-api-template
```

### **2. Ejecutar Contenedor**

```bash
# Ejecutar contenedor
docker run -d \
  --name business-api \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./business_api.db \
  -e SECRET_KEY=tu-clave-secreta \
  business-api-template

# Verificar logs
docker logs business-api
```

### **3. Docker Compose (Recomendado)**

```bash
# Ejecutar con docker-compose
docker-compose up -d

# Verificar servicios
docker-compose ps

# Ver logs
docker-compose logs -f app
```

**docker-compose.yml para desarrollo:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./business_api.db
      - DEBUG=True
      - SECRET_KEY=dev-secret-key
    volumes:
      - .:/app
      - /app/__pycache__
    depends_on:
      - redis
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app

volumes:
  redis_data:
```

### **4. Verificar Deployment Docker**

```bash
# Verificar contenedor
docker ps

# Verificar aplicación
curl http://localhost:8000/health

# Verificar logs
docker logs business-api
```

## 🌐 Deployment en Producción

### **1. Preparación del Servidor**

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3.12 python3.12-venv python3-pip nginx postgresql redis-server

# Crear usuario para la aplicación
sudo useradd -m -s /bin/bash appuser
sudo usermod -aG sudo appuser
```

### **2. Configuración de Base de Datos**

```bash
# Configurar PostgreSQL
sudo -u postgres psql

# En PostgreSQL:
CREATE DATABASE business_api;
CREATE USER appuser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE business_api TO appuser;
\q
```

### **3. Despliegue de Aplicación**

```bash
# Cambiar a usuario de aplicación
sudo su - appuser

# Clonar repositorio
git clone https://github.com/yourusername/business-api-template.git
cd business-api-template

# Crear entorno virtual
python3.12 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
nano .env
```

**Configuración de producción (.env):**
```env
# Base de datos
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://appuser:secure_password@localhost:5432/business_api

# Seguridad
SECRET_KEY=clave-super-secreta-de-produccion-muy-larga
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False

# WhatsApp
WHATSAPP_ACCESS_TOKEN=tu_token_whatsapp
WHATSAPP_PHONE_NUMBER_ID=tu_phone_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=tu_verify_token

# Redis (opcional)
REDIS_URL=redis://localhost:6379

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
```

### **4. Configuración de Nginx**

```bash
# Crear configuración de Nginx
sudo nano /etc/nginx/sites-available/business-api
```

**Configuración de Nginx:**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # Proxy to FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static/ {
        alias /home/appuser/business-api-template/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/business-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **5. Configuración de Systemd**

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/business-api.service
```

**Configuración de systemd:**
```ini
[Unit]
Description=Business API Template
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=appuser
Group=appuser
WorkingDirectory=/home/appuser/business-api-template
Environment=PATH=/home/appuser/business-api-template/venv/bin
ExecStart=/home/appuser/business-api-template/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable business-api
sudo systemctl start business-api
sudo systemctl status business-api
```

### **6. Configuración de SSL**

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

## 🗄️ Configuración de Base de Datos

### **PostgreSQL (Producción)**

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Configurar PostgreSQL
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE business_api;
CREATE USER appuser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE business_api TO appuser;
ALTER USER appuser CREATEDB;
\q
```

### **Migraciones**

```bash
# Ejecutar migraciones
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migración
alembic upgrade head
```

### **Backup y Restore**

```bash
# Backup
pg_dump -h localhost -U appuser business_api > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql -h localhost -U appuser business_api < backup_file.sql
```

## 📱 Configuración de WhatsApp

### **1. Configurar Webhook**

```bash
# Verificar webhook
curl -X GET "https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/subscribed_apps" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"

# Suscribir a webhook
curl -X POST "https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/subscribed_apps" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"subscribed_fields": "messages,messaging_postbacks"}'
```

### **2. Configurar Webhook URL**

En el panel de Meta for Developers:
- **Webhook URL**: `https://tu-dominio.com/api/v1/whatsapp/webhook`
- **Verify Token**: El mismo que configuraste en `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
- **Webhook Fields**: `messages`, `messaging_postbacks`

### **3. Verificar Configuración**

```bash
# Probar webhook
curl -X POST "https://tu-dominio.com/api/v1/whatsapp/webhook" \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'
```

## 📊 Monitoreo y Logs

### **1. Configuración de Logs**

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/business-api
sudo chown appuser:appuser /var/log/business-api

# Configurar logrotate
sudo nano /etc/logrotate.d/business-api
```

**Configuración de logrotate:**
```
/var/log/business-api/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 appuser appuser
    postrotate
        systemctl reload business-api
    endscript
}
```

### **2. Monitoreo con Prometheus**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'business-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### **3. Health Checks**

```bash
# Script de health check
#!/bin/bash
curl -f http://localhost:8000/health || exit 1
```

## 🔧 Troubleshooting

### **Problemas Comunes**

#### **1. Error de Conexión a Base de Datos**
```bash
# Verificar conexión PostgreSQL
sudo -u postgres psql -c "SELECT version();"

# Verificar configuración
psql -h localhost -U appuser -d business_api -c "SELECT 1;"
```

#### **2. Error de Permisos**
```bash
# Verificar permisos de archivos
ls -la /home/appuser/business-api-template/

# Corregir permisos
sudo chown -R appuser:appuser /home/appuser/business-api-template/
```

#### **3. Error de Puerto en Uso**
```bash
# Verificar puerto
sudo netstat -tlnp | grep :8000

# Matar proceso
sudo kill -9 $(sudo lsof -t -i:8000)
```

#### **4. Error de SSL**
```bash
# Verificar certificado
sudo certbot certificates

# Renovar certificado
sudo certbot renew
```

### **Logs de Debugging**

```bash
# Ver logs de aplicación
sudo journalctl -u business-api -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

## 🔄 Mantenimiento

### **1. Actualizaciones**

```bash
# Backup antes de actualizar
pg_dump -h localhost -U appuser business_api > backup_before_update.sql

# Actualizar código
git pull origin main

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Reiniciar servicio
sudo systemctl restart business-api
```

### **2. Limpieza de Logs**

```bash
# Limpiar logs antiguos
sudo find /var/log/business-api -name "*.log" -mtime +30 -delete

# Limpiar logs de Nginx
sudo find /var/log/nginx -name "*.log" -mtime +30 -delete
```

### **3. Monitoreo de Recursos**

```bash
# Verificar uso de CPU y memoria
htop

# Verificar espacio en disco
df -h

# Verificar conexiones de red
sudo netstat -tulpn
```

### **4. Backup Automático**

```bash
# Crear script de backup
sudo nano /usr/local/bin/backup-business-api.sh
```

**Script de backup:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/business-api"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Crear backup
pg_dump -h localhost -U appuser business_api > $BACKUP_FILE

# Comprimir backup
gzip $BACKUP_FILE

# Eliminar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

```bash
# Hacer ejecutable
sudo chmod +x /usr/local/bin/backup-business-api.sh

# Agregar a crontab
sudo crontab -e
# Agregar línea:
# 0 2 * * * /usr/local/bin/backup-business-api.sh
```

---

## 📞 Soporte

### **Recursos Adicionales**
- **Documentación**: [docs/README.md](docs/README.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### **Contacto**
- **Email**: support@yourapp.com
- **GitHub Issues**: [Reportar problemas](https://github.com/yourusername/issues)
- **Discord**: [Comunidad](https://discord.gg/yourapp)

---

*Esta guía se actualiza con cada nueva versión. Para la versión más reciente, consulta el repositorio del proyecto.*
