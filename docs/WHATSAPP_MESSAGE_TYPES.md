# WhatsApp Message Types

Este documento describe el sistema completo de tipos de mensajes de WhatsApp Business API implementado en el template.

## 📋 Tabla de Contenidos

- [Tipos de Mensajes Disponibles](#tipos-de-mensajes-disponibles)
- [WhatsAppMessageBuilder](#whatsappmessagebuilder)
- [WhatsAppMessageTemplates](#whatsappmessagetemplates)
- [WhatsAppMessageSender](#whatsappmessagesender)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Integración con el Flujo de Conversación](#integración-con-el-flujo-de-conversación)

## Tipos de Mensajes Disponibles

### 1. Mensajes de Texto
Mensajes simples de texto plano.

```python
result = whatsapp_service.message_sender.send_text(
    phone_number="1234567890",
    text="¡Hola! ¿En qué puedo ayudarte?"
)
```

### 2. Mensajes Interactivos con Botones
Mensajes que incluyen hasta 3 botones interactivos.

```python
buttons = [
    {"id": "products", "title": "Ver Productos"},
    {"id": "services", "title": "Servicios"},
    {"id": "contact", "title": "Contacto"}
]

result = whatsapp_service.message_sender.send_buttons(
    phone_number="1234567890",
    text="¿Qué te interesa?",
    buttons=buttons
)
```

### 3. Mensajes de Lista Interactiva
Mensajes con listas desplegables para selección múltiple.

```python
sections = [{
    "title": "Productos",
    "rows": [
        {"id": "prod1", "title": "Producto 1", "description": "$100"},
        {"id": "prod2", "title": "Producto 2", "description": "$200"}
    ]
}]

result = whatsapp_service.message_sender.send_list(
    phone_number="1234567890",
    text="Selecciona un producto:",
    button_text="Ver Productos",
    sections=sections
)
```

### 4. Mensajes Multimedia
Soporte para imágenes, videos, audio y documentos.

```python
# Imagen con caption
result = whatsapp_service.message_sender.send_media(
    phone_number="1234567890",
    media_type="image",
    media_url="https://example.com/image.jpg",
    caption="¡Mira nuestro producto!"
)

# Video
result = whatsapp_service.message_sender.send_media(
    phone_number="1234567890",
    media_type="video",
    media_url="https://example.com/video.mp4",
    caption="Tutorial del producto"
)

# Documento PDF
result = whatsapp_service.message_sender.send_media(
    phone_number="1234567890",
    media_type="document",
    media_url="https://example.com/catalog.pdf",
    caption="Catálogo completo"
)
```

### 5. Mensajes de Ubicación
Envío de coordenadas geográficas.

```python
result = whatsapp_service.message_sender.send_location(
    phone_number="1234567890",
    latitude=40.7128,
    longitude=-74.0060,
    name="Mi Empresa",
    address="Calle Principal 123"
)
```

### 6. Mensajes de Contacto
Envío de tarjetas de contacto.

```python
contacts = [{
    "name": {
        "formatted_name": "Juan Pérez",
        "first_name": "Juan"
    },
    "phones": [{
        "phone": "+1234567890",
        "type": "WORK"
    }],
    "emails": [{
        "email": "juan@empresa.com",
        "type": "WORK"
    }]
}]

result = whatsapp_service.message_sender.send_contact(
    phone_number="1234567890",
    contacts=contacts
)
```

### 7. Mensajes de Sticker
Envío de stickers.

```python
result = whatsapp_service.message_sender.send_sticker(
    phone_number="1234567890",
    sticker_id="sticker_id_here"
)
```

### 8. Mensajes de Plantilla
Uso de plantillas pre-aprobadas por WhatsApp.

```python
components = [{
    "type": "body",
    "parameters": [{
        "type": "text",
        "text": "Juan"
    }]
}]

result = whatsapp_service.message_sender.send_template(
    phone_number="1234567890",
    template_name="hello_world",
    language_code="es",
    components=components
)
```

## WhatsAppMessageBuilder

Clase builder para construir mensajes de WhatsApp de forma programática.

```python
from app.services.whatsapp_message_types import WhatsAppMessageBuilder

builder = WhatsAppMessageBuilder("1234567890")

# Construir mensaje de texto
text_message = builder.text_message("Hola mundo")

# Construir mensaje con botones
button_message = builder.interactive_button_message(
    "Selecciona una opción:",
    [
        {"id": "option1", "title": "Opción 1"},
        {"id": "option2", "title": "Opción 2"}
    ]
)
```

## WhatsAppMessageTemplates

Plantillas predefinidas para escenarios comunes de negocio.

### Mensaje de Bienvenida
```python
from app.services.whatsapp_message_types import WhatsAppMessageTemplates

welcome_template = WhatsAppMessageTemplates.welcome_message("Mi Empresa")
# Retorna: {"body": "...", "buttons": [...]}
```

### Catálogo de Productos
```python
products = [
    {"id": "1", "name": "Producto 1", "price": "100"},
    {"id": "2", "name": "Producto 2", "price": "200"}
]

catalog_template = WhatsAppMessageTemplates.product_catalog_message(products)
# Retorna estructura para mensaje de lista
```

### Información de Contacto
```python
company_info = {
    "name": "Mi Empresa",
    "phone": "+1234567890",
    "email": "contacto@empresa.com",
    "address": "Calle Principal 123",
    "website": "https://empresa.com"
}

contact_text = WhatsAppMessageTemplates.contact_info_message(company_info)
# Retorna texto formateado con información de contacto
```

### Confirmación de Pedido
```python
order_data = {
    "order_id": "ORD-2024-001",
    "date": "2024-01-15",
    "total": "150.00",
    "status": "Procesando"
}

confirmation_text = WhatsAppMessageTemplates.order_confirmation_message(order_data)
# Retorna texto formateado de confirmación
```

### Confirmación de Cita
```python
appointment_data = {
    "client_name": "Juan Pérez",
    "date": "2024-01-20",
    "time": "10:00 AM",
    "location": "Oficina Principal",
    "service": "Consultoría"
}

confirmation_text = WhatsAppMessageTemplates.appointment_confirmation_message(appointment_data)
# Retorna texto formateado de confirmación de cita
```

## WhatsAppMessageSender

Servicio principal para enviar mensajes a través de la API de WhatsApp.

```python
# El sender se inicializa automáticamente en WhatsAppService
sender = whatsapp_service.message_sender

# Enviar diferentes tipos de mensajes
await sender.send_text(phone_number, "Hola")
await sender.send_buttons(phone_number, "Opciones:", buttons)
await sender.send_list(phone_number, "Selecciona:", "Ver", sections)
await sender.send_media(phone_number, "image", url, caption)
```

## Ejemplos de Uso

### Flujo de Conversación Completo
```python
async def handle_conversation_flow(phone_number: str, user_message: str):
    """Ejemplo de flujo de conversación usando diferentes tipos de mensajes"""
    
    if "hola" in user_message.lower():
        # Enviar mensaje de bienvenida con botones
        welcome_template = WhatsAppMessageTemplates.welcome_message("Mi Empresa")
        await whatsapp_service.message_sender.send_buttons(
            phone_number,
            welcome_template["body"],
            welcome_template["buttons"]
        )
    
    elif "productos" in user_message.lower():
        # Enviar catálogo de productos
        products = get_products_from_database()
        catalog_template = WhatsAppMessageTemplates.product_catalog_message(products)
        await whatsapp_service.message_sender.send_list(
            phone_number,
            catalog_template["body"],
            catalog_template["button_text"],
            catalog_template["sections"]
        )
    
    elif "contacto" in user_message.lower():
        # Enviar información de contacto
        company_info = get_company_info()
        contact_text = WhatsAppMessageTemplates.contact_info_message(company_info)
        await whatsapp_service.message_sender.send_text(phone_number, contact_text)
    
    elif "ubicacion" in user_message.lower():
        # Enviar ubicación
        await whatsapp_service.message_sender.send_location(
            phone_number,
            latitude=40.7128,
            longitude=-74.0060,
            name="Mi Empresa",
            address="Calle Principal 123"
        )
```

### Manejo de Respuestas de Botones
```python
async def handle_button_response(phone_number: str, button_id: str):
    """Manejar respuestas de botones interactivos"""
    
    if button_id == "products":
        # Mostrar productos
        products = get_products()
        catalog_template = WhatsAppMessageTemplates.product_catalog_message(products)
        await whatsapp_service.message_sender.send_list(
            phone_number,
            catalog_template["body"],
            catalog_template["button_text"],
            catalog_template["sections"]
        )
    
    elif button_id == "services":
        # Mostrar servicios
        services = get_services()
        service_template = WhatsAppMessageTemplates.service_menu_message(services)
        await whatsapp_service.message_sender.send_list(
            phone_number,
            service_template["body"],
            service_template["button_text"],
            service_template["sections"]
        )
    
    elif button_id == "contact":
        # Mostrar información de contacto
        company_info = get_company_info()
        contact_text = WhatsAppMessageTemplates.contact_info_message(company_info)
        await whatsapp_service.message_sender.send_text(phone_number, contact_text)
```

## Integración con el Flujo de Conversación

El sistema está integrado con el flujo de conversación existente a través del método `_send_interactive_response`:

```python
# En WhatsAppService
def _send_interactive_response(self, phone_number: str, conversation_state: str, contact_info: Dict[str, Any]):
    """Enviar respuesta interactiva basada en el estado de la conversación"""
    
    if conversation_state == "initial":
        # Mensaje de bienvenida con botones
        welcome_template = WhatsAppMessageTemplates.welcome_message(settings.COMPANY_NAME)
        return self.message_sender.send_buttons(
            phone_number,
            welcome_template["body"],
            welcome_template["buttons"]
        )
    
    elif conversation_state == "waiting_for_selection":
        # Menú de productos/servicios
        products = get_products_from_database()
        catalog_template = WhatsAppMessageTemplates.product_catalog_message(products)
        return self.message_sender.send_list(
            phone_number,
            catalog_template["body"],
            catalog_template["button_text"],
            catalog_template["sections"]
        )
    
    # ... más estados
```

## Configuración

### Variables de Entorno Requeridas
```env
COMPANY_NAME=Mi Empresa
COMPANY_PHONE=+1234567890
COMPANY_EMAIL=contacto@empresa.com
COMPANY_ADDRESS=Calle Principal 123
COMPANY_WEBSITE=https://empresa.com
```

### Personalización de Plantillas
Las plantillas pueden ser personalizadas modificando los métodos en `WhatsAppMessageTemplates` o creando nuevas plantillas específicas para tu negocio.

## Limitaciones de WhatsApp

- **Botones**: Máximo 3 botones por mensaje
- **Listas**: Máximo 10 elementos por sección
- **Secciones**: Máximo 10 secciones por mensaje
- **Plantillas**: Deben estar pre-aprobadas por WhatsApp
- **Medios**: URLs deben ser accesibles públicamente

## Mejores Prácticas

1. **Usa botones para opciones principales** (máximo 3)
2. **Usa listas para catálogos extensos** (hasta 10 elementos)
3. **Incluye captions descriptivos** en medios
4. **Personaliza las plantillas** según tu negocio
5. **Maneja errores** con fallbacks a mensajes de texto
6. **Usa logs de desarrollo** para debugging
7. **Guarda mensajes** en la base de datos para persistencia
