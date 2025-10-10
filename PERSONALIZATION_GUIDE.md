# Guía de Personalización - Business API Template

## 🎯 Cómo Personalizar el Template para tu Negocio

Este template está diseñado para ser fácilmente adaptable a cualquier tipo de negocio. Aquí te mostramos cómo personalizarlo paso a paso.

## 📋 Pasos de Personalización

### 1. **Información Básica de la Empresa**

Edita el archivo `.env` con la información de tu empresa:

```env
# Información de la empresa (personalizable)
COMPANY_NAME=Mi Restaurante
COMPANY_PHONE=+1234567890
COMPANY_EMAIL=contacto@mirestaurante.com
COMPANY_ADDRESS=123 Calle Principal, Ciudad, Estado
COMPANY_WEBSITE=www.mirestaurante.com
COMPANY_DESCRIPTION=El mejor restaurante de la ciudad
```

### 2. **Personalizar Mensajes de WhatsApp**

Edita `app/data/messages.yaml` para adaptar los mensajes a tu negocio:

```yaml
messages:
  welcome:
    new_user: |
      ¡Hola! 👋 
      
      Bienvenido/a a Mi Restaurante 🍽️
      
      Soy tu asistente virtual y estoy aquí para ayudarte con:
      • Ver nuestro menú
      • Hacer reservas
      • Consultar horarios
      • Información de contacto
      
      ¿En qué puedo ayudarte hoy? 😊
```

### 3. **Adaptar el Modelo de Productos/Servicios**

Para diferentes tipos de negocios, puedes modificar `app/models/__init__.py`:

#### **Restaurante/Café:**
```python
class Product(BaseModel):
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    # Campos específicos para restaurante
    ingredients: Optional[str]  # Ingredientes
    allergens: Optional[str]    # Alérgenos
    preparation_time: Optional[int]  # Tiempo de preparación en minutos
    is_vegetarian: bool = False
    is_vegan: bool = False
    spice_level: Optional[int]  # Nivel de picante (1-5)
```

#### **Tienda Online:**
```python
class Product(BaseModel):
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    # Campos específicos para e-commerce
    sku: Optional[str]         # Código de producto
    weight: Optional[float]    # Peso en kg
    dimensions: Optional[str]  # Dimensiones
    brand: Optional[str]       # Marca
    color: Optional[str]       # Color
    size: Optional[str]        # Talla/Tamaño
```

#### **Servicios Profesionales:**
```python
class Product(BaseModel):
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    # Campos específicos para servicios
    duration: Optional[int]    # Duración en minutos
    service_type: Optional[str] # Tipo de servicio
    requires_appointment: bool = True
    available_days: Optional[str] # Días disponibles
    max_capacity: Optional[int]   # Capacidad máxima
```

### 4. **Personalizar Categorías**

Modifica las categorías según tu negocio en las migraciones de base de datos:

#### **Restaurante:**
- Entradas
- Platos Principales
- Postres
- Bebidas
- Especialidades

#### **Tienda Online:**
- Ropa
- Electrónicos
- Hogar
- Deportes
- Libros

#### **Servicios:**
- Consultoría
- Diseño
- Desarrollo
- Marketing
- Soporte Técnico

### 5. **Configurar WhatsApp Business API**

1. **Crear aplicación en Facebook Developers**
2. **Configurar WhatsApp Business API**
3. **Obtener credenciales:**
   ```env
   WHATSAPP_ACCESS_TOKEN=tu-access-token
   WHATSAPP_PHONE_NUMBER_ID=tu-phone-number-id
   WHATSAPP_WEBHOOK_VERIFY_TOKEN=tu-verify-token
   ```

### 6. **Personalizar la Página de Inicio**

El archivo `main.py` ya incluye una página de inicio personalizable que muestra la información de tu empresa automáticamente.

### 7. **Agregar Campos Específicos**

Si necesitas campos adicionales específicos de tu negocio:

1. **Crear nueva migración:**
   ```bash
   alembic revision --autogenerate -m "Add custom fields for my business"
   ```

2. **Aplicar migración:**
   ```bash
   alembic upgrade head
   ```

## 🎨 Ejemplos de Personalización por Tipo de Negocio

### **Restaurante/Café**
- **Productos:** Platos, bebidas, postres
- **Categorías:** Por tipo de comida
- **Mensajes:** Enfoque en menú y reservas
- **Campos adicionales:** Ingredientes, alérgenos, tiempo de preparación

### **Tienda Online**
- **Productos:** Artículos físicos
- **Categorías:** Por tipo de producto
- **Mensajes:** Enfoque en catálogo y compras
- **Campos adicionales:** SKU, peso, dimensiones, inventario

### **Servicios Profesionales**
- **Productos:** Servicios
- **Categorías:** Por tipo de servicio
- **Mensajes:** Enfoque en citas y consultas
- **Campos adicionales:** Duración, disponibilidad, capacidad

### **Clínica/Consultorio**
- **Productos:** Servicios médicos
- **Categorías:** Por especialidad
- **Mensajes:** Enfoque en citas y consultas médicas
- **Campos adicionales:** Duración de consulta, especialidad, urgencia

### **Gimnasio/Deportes**
- **Productos:** Clases, membresías
- **Categorías:** Por tipo de actividad
- **Mensajes:** Enfoque en horarios y clases
- **Campos adicionales:** Nivel de dificultad, capacidad, instructor

## 🔧 Configuración Avanzada

### **Variables de Entorno Personalizadas**

Puedes agregar nuevas variables en `app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... variables existentes ...
    
    # Variables específicas de tu negocio
    BUSINESS_TYPE: str = "restaurant"  # restaurant, ecommerce, services, etc.
    TIMEZONE: str = "America/Mexico_City"
    CURRENCY: str = "MXN"
    LANGUAGE: str = "es"
    
    # Configuración específica del negocio
    OPENING_HOURS: str = "8:00-18:00"
    CLOSING_DAYS: str = "Sunday"
    MAX_RESERVATIONS_PER_DAY: int = 50
```

### **Mensajes Dinámicos**

Los mensajes pueden usar variables dinámicas:

```yaml
messages:
  welcome:
    new_user: |
      ¡Hola! 👋 
      
      Bienvenido/a a {company_name}
      
      Nuestros horarios son: {opening_hours}
      
      ¿En qué puedo ayudarte hoy? 😊
```

### **Integración con Sistemas Externos**

Puedes agregar integraciones con:
- **Sistemas de pago:** Stripe, PayPal, MercadoPago
- **CRM:** HubSpot, Salesforce
- **Inventario:** Sistemas de gestión de stock
- **Reservas:** Sistemas de citas online

## 📱 Personalización de WhatsApp

### **Flujo de Conversación Personalizado**

Modifica `app/services/conversation_service.py` para crear flujos específicos:

```python
class ConversationService:
    def process_message(self, message: str, conversation_state: str):
        if conversation_state == "menu_request":
            return self.handle_menu_request(message)
        elif conversation_state == "reservation":
            return self.handle_reservation(message)
        elif conversation_state == "order":
            return self.handle_order(message)
        # ... más estados específicos
```

### **Respuestas Automáticas Inteligentes**

Implementa lógica específica para tu negocio:

```python
def get_auto_response(self, message: str, business_type: str):
    if business_type == "restaurant":
        if "menú" in message.lower():
            return "Aquí está nuestro menú actual..."
        elif "reserva" in message.lower():
            return "Te ayudo con tu reserva..."
    
    elif business_type == "ecommerce":
        if "producto" in message.lower():
            return "Aquí están nuestros productos..."
        elif "envío" in message.lower():
            return "Información sobre envíos..."
```

## 🚀 Despliegue Personalizado

### **Docker Personalizado**

Crea un `Dockerfile` específico para tu negocio:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Variables específicas del negocio
ENV BUSINESS_TYPE=restaurant
ENV COMPANY_NAME="Mi Restaurante"

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Variables de Producción**

Configura variables específicas para producción:

```env
# Producción
DEBUG=False
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:password@db:5432/mi_negocio_db

# WhatsApp Business API (producción)
WHATSAPP_ACCESS_TOKEN=tu-token-de-produccion
WHATSAPP_PHONE_NUMBER_ID=tu-phone-id-de-produccion
WHATSAPP_WEBHOOK_VERIFY_TOKEN=tu-verify-token-seguro

# Empresa
COMPANY_NAME=Mi Empresa Real
COMPANY_PHONE=+1234567890
COMPANY_EMAIL=contacto@miempresa.com
```

## 📊 Monitoreo Personalizado

### **Métricas Específicas del Negocio**

Agrega métricas relevantes para tu tipo de negocio:

```python
@app.get("/api/v1/metrics/business")
async def get_business_metrics():
    if settings.BUSINESS_TYPE == "restaurant":
        return {
            "orders_today": count_orders_today(),
            "popular_items": get_popular_items(),
            "reservations_today": count_reservations_today()
        }
    elif settings.BUSINESS_TYPE == "ecommerce":
        return {
            "sales_today": calculate_sales_today(),
            "top_products": get_top_products(),
            "cart_abandonment_rate": get_cart_abandonment_rate()
        }
```

## 🎯 Checklist de Personalización

- [ ] Actualizar información de la empresa en `.env`
- [ ] Personalizar mensajes en `messages.yaml`
- [ ] Adaptar modelo de productos según el negocio
- [ ] Configurar categorías específicas
- [ ] Configurar WhatsApp Business API
- [ ] Personalizar página de inicio
- [ ] Agregar campos específicos si es necesario
- [ ] Configurar variables de producción
- [ ] Implementar métricas específicas del negocio
- [ ] Probar flujo completo de WhatsApp
- [ ] Desplegar en producción

## 📞 Soporte

Si necesitas ayuda con la personalización:

1. **Revisa la documentación** en `docs/`
2. **Consulta los ejemplos** en este archivo
3. **Revisa el código** en `app/services/` para entender la lógica
4. **Prueba cambios** en desarrollo antes de producción

---

**¡Tu Business API Template está listo para ser personalizado para cualquier tipo de negocio!** 🚀
