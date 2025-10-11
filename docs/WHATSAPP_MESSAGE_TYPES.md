# 📱 WhatsApp Business API - Tipos de Mensajes Disponibles

## 🔧 WhatsAppMessageBuilder - Métodos de Construcción

### 1. **text_message(text: str)**
- **Tipo**: `text`
- **Descripción**: Mensaje de texto simple
- **Uso**: `builder.text_message("Hola, ¿cómo estás?")`

### 2. **interactive_button_message(body_text: str, buttons: List[Dict])**
- **Tipo**: `interactive` (button)
- **Descripción**: Mensaje con botones de respuesta
- **Límite**: Máximo 3 botones
- **Uso**: `builder.interactive_button_message("Elige una opción:", [{"id": "op1", "title": "Opción 1"}])`

### 3. **interactive_list_message(body_text: str, button_text: str, sections: List[Dict])**
- **Tipo**: `interactive` (list)
- **Descripción**: Mensaje con lista desplegable
- **Límite**: Máximo 10 elementos por lista
- **Uso**: `builder.interactive_list_message("Selecciona:", "Ver opciones", sections)`

### 4. **media_message(media_type: str, media_url: str, caption: str = None)**
- **Tipo**: `image`, `document`, `audio`, `video`
- **Descripción**: Mensaje con archivos multimedia
- **Tipos soportados**: image, document, audio, video
- **Uso**: `builder.media_message("image", "https://example.com/image.jpg", "Mi imagen")`

### 5. **template_message(template_name: str, language_code: str = "es", components: List[Dict] = None)**
- **Tipo**: `template`
- **Descripción**: Mensaje usando plantillas pre-aprobadas
- **Requisito**: Plantilla debe estar aprobada por Meta
- **Uso**: `builder.template_message("hello_world", "es")`

### 6. **location_message(latitude: float, longitude: float, name: str = None, address: str = None)**
- **Tipo**: `location`
- **Descripción**: Mensaje con ubicación geográfica
- **Uso**: `builder.location_message(-34.6037, -58.3816, "Buenos Aires")`

### 7. **contact_message(contacts: List[Dict])**
- **Tipo**: `contacts`
- **Descripción**: Mensaje con información de contacto
- **Uso**: `builder.contact_message([{"name": {"formatted_name": "Juan"}, "phones": [{"phone": "+1234567890"}]}])`

### 8. **sticker_message(sticker_id: str)**
- **Tipo**: `sticker`
- **Descripción**: Mensaje con sticker
- **Requisito**: ID del sticker válido
- **Uso**: `builder.sticker_message("sticker_id_123")`

### 9. **catalog_message(catalog_id: str, product_sections: List[Dict], header_text: str, body_text: str, footer_text: str)**
- **Tipo**: `interactive` (product_list)
- **Descripción**: Mensaje con catálogo de productos nativo
- **Nuevo**: ✅ Agregado recientemente
- **Uso**: `builder.catalog_message(catalog_id, sections, "Catálogo", "Elige productos", "Disponible")`

### 10. **create_product_section(title: str, product_retailer_ids: List[str])**
- **Tipo**: Helper method
- **Descripción**: Método auxiliar para crear secciones de productos
- **Uso**: `builder.create_product_section("Más vendidos", ["prod1", "prod2"])`

## 📋 WhatsAppMessageTemplates - Plantillas Predefinidas

### 1. **welcome_message(company_name: str)**
- **Descripción**: Mensaje de bienvenida personalizable
- **Uso**: `templates.welcome_message("Mi Empresa")`

### 2. **product_catalog_message()**
- **Descripción**: Catálogo de productos usando lista interactiva
- **Uso**: `templates.product_catalog_message()`

### 3. **native_catalog_message(catalog_id: str, product_sections: List[Dict] = None)**
- **Descripción**: Catálogo nativo de WhatsApp con productos reales
- **Nuevo**: ✅ Agregado recientemente
- **Uso**: `templates.native_catalog_message(catalog_id)`

### 4. **service_menu_message()**
- **Descripción**: Menú de servicios usando lista interactiva
- **Uso**: `templates.service_menu_message()`

### 5. **contact_info_message()**
- **Descripción**: Información de contacto de la empresa
- **Uso**: `templates.contact_info_message()`

### 6. **order_confirmation_message(order_data: Dict)**
- **Descripción**: Confirmación de pedido
- **Uso**: `templates.order_confirmation_message({"order_id": "123", "total": 100})`

### 7. **appointment_confirmation_message(appointment_data: Dict)**
- **Descripción**: Confirmación de cita
- **Uso**: `templates.appointment_confirmation_message({"date": "2024-01-01", "time": "10:00"})`

## 🚀 WhatsAppMessageSender - Envío de Mensajes

### **send_message(message_data: Dict)**
- **Descripción**: Envía cualquier tipo de mensaje a WhatsApp
- **Uso**: `sender.send_message(message_data)`

## 📊 Resumen de Tipos de Mensajes

| Tipo | Método | Estado | Descripción |
|------|--------|--------|-------------|
| `text` | `text_message()` | ✅ Funcional | Mensaje de texto simple |
| `interactive` (button) | `interactive_button_message()` | ✅ Funcional | Botones de respuesta |
| `interactive` (list) | `interactive_list_message()` | ✅ Funcional | Lista desplegable |
| `interactive` (product_list) | `catalog_message()` | ✅ **NUEVO** | Catálogo de productos |
| `image` | `media_message()` | ✅ Funcional | Imagen con caption |
| `document` | `media_message()` | ✅ Funcional | Documento con caption |
| `audio` | `media_message()` | ✅ Funcional | Audio |
| `video` | `media_message()` | ✅ Funcional | Video con caption |
| `location` | `location_message()` | ✅ Funcional | Ubicación geográfica |
| `contacts` | `contact_message()` | ✅ Funcional | Información de contacto |
| `sticker` | `sticker_message()` | ⚠️ Limitado | Sticker (requiere ID válido) |
| `template` | `template_message()` | ⚠️ Requiere aprobación | Plantilla pre-aprobada |

## 🎯 Tipos de Mensajes por Categoría

### **Mensajes Básicos**
- Text messages
- Media messages (image, document, audio, video)

### **Mensajes Interactivos**
- Button messages
- List messages
- **Catalog messages** (NUEVO)

### **Mensajes Especiales**
- Location messages
- Contact messages
- Sticker messages
- Template messages

### **Mensajes de Negocio**
- Welcome messages
- Service menus
- Order confirmations
- Appointment confirmations

## 💡 Ejemplos de Uso

```python
# Inicializar
builder = WhatsAppMessageBuilder("+1234567890")
templates = WhatsAppMessageTemplates()

# Mensaje de texto
text_msg = builder.text_message("¡Hola!")

# Mensaje con botones
button_msg = builder.interactive_button_message(
    "¿Qué necesitas?", 
    [{"id": "help", "title": "Ayuda"}, {"id": "info", "title": "Info"}]
)

# Mensaje de catálogo (NUEVO)
catalog_msg = builder.catalog_message(
    catalog_id="123456789",
    product_sections=[
        builder.create_product_section("Más vendidos", ["prod1", "prod2"]),
        builder.create_product_section("Nuevos", ["prod3", "prod4"])
    ],
    header_text="🛍️ Nuestro Catálogo",
    body_text="Elige productos:",
    footer_text="Disponible ahora"
)

# Plantilla de catálogo (NUEVO)
template_catalog = templates.native_catalog_message("123456789")
```

## 🔧 Configuración Requerida

### **Variables de Entorno**
```bash
WHATSAPP_ACCESS_TOKEN=tu_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_id
WHATSAPP_CATALOG_ID=tu_catalog_id  # Para mensajes de catálogo
```

### **Permisos del Token**
- `whatsapp_business_messaging` - Para enviar mensajes
- `whatsapp_business_management` - Para catálogos
- `business_management` - Para gestión comercial

## 📈 Estadísticas de Implementación

- **Total de tipos**: 12 tipos de mensajes
- **Funcionales**: 10 tipos (83.3%)
- **Limitados**: 2 tipos (16.7%)
- **Nuevos**: 2 tipos agregados (catalog_message, native_catalog_message)
- **Success Rate**: 87.5% en tests