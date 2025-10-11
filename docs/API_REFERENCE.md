# 📚 API Reference

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Autenticación](#autenticación)
3. [Endpoints de Usuario](#endpoints-de-usuario)
4. [Endpoints de Productos](#endpoints-de-productos)
5. [Endpoints de WhatsApp](#endpoints-de-whatsapp)
6. [Códigos de Estado](#códigos-de-estado)
7. [Manejo de Errores](#manejo-de-errores)
8. [Rate Limiting](#rate-limiting)
9. [Ejemplos de Uso](#ejemplos-de-uso)
10. [SDKs y Herramientas](#sdks-y-herramientas)

## 🚀 Introducción

La Business API Template proporciona una API RESTful completa para la gestión de usuarios, productos y integración con WhatsApp Business API.

### **Base URL**
```
https://api.yourapp.com/api/v1
```

### **Formato de Respuesta**
Todas las respuestas están en formato JSON con la siguiente estructura:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Paginación**
Los endpoints que devuelven listas soportan paginación:

```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  }
}
```

## 🔐 Autenticación

La API utiliza **JWT (JSON Web Tokens)** para autenticación.

### **Obtener Token**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "tu_usuario",
  "password": "tu_password"
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "email": "usuario@ejemplo.com",
      "username": "usuario",
      "full_name": "Usuario Completo",
      "is_active": true,
      "is_superuser": false
    }
  }
}
```

### **Usar Token**

Incluye el token en el header `Authorization`:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Registrar Usuario**

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "nuevo@ejemplo.com",
  "username": "nuevo_usuario",
  "password": "password_seguro",
  "full_name": "Nombre Completo"
}
```

### **Obtener Usuario Actual**

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

## 👤 Endpoints de Usuario

### **Listar Usuarios**

```http
GET /api/v1/users/
Authorization: Bearer <token>
```

**Parámetros de Query:**
- `page` (int): Número de página (default: 1)
- `size` (int): Tamaño de página (default: 20)
- `search` (string): Búsqueda por nombre o email
- `is_active` (bool): Filtrar por estado activo

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "email": "usuario@ejemplo.com",
        "username": "usuario",
        "full_name": "Usuario Completo",
        "is_active": true,
        "is_superuser": false,
        "is_verified": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

### **Crear Usuario**

```http
POST /api/v1/users/
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "nuevo@ejemplo.com",
  "username": "nuevo_usuario",
  "password": "password_seguro",
  "full_name": "Nombre Completo"
}
```

### **Obtener Usuario**

```http
GET /api/v1/users/{user_id}
Authorization: Bearer <token>
```

### **Actualizar Usuario**

```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "actualizado@ejemplo.com",
  "full_name": "Nombre Actualizado",
  "is_active": true
}
```

### **Eliminar Usuario**

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <token>
```

## 📦 Endpoints de Productos

### **Listar Productos**

```http
GET /api/v1/products/
Authorization: Bearer <token>
```

**Parámetros de Query:**
- `page` (int): Número de página
- `size` (int): Tamaño de página
- `search` (string): Búsqueda por nombre
- `category_id` (int): Filtrar por categoría
- `is_available` (bool): Filtrar por disponibilidad
- `min_price` (int): Precio mínimo (en centavos)
- `max_price` (int): Precio máximo (en centavos)

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Producto Ejemplo",
        "description": "Descripción del producto",
        "price": 1000,
        "category_id": 1,
        "image_url": "https://ejemplo.com/imagen.jpg",
        "stock_quantity": 50,
        "is_available": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

### **Crear Producto**

```http
POST /api/v1/products/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Nuevo Producto",
  "description": "Descripción del nuevo producto",
  "price": 1500,
  "category_id": 1,
  "image_url": "https://ejemplo.com/nueva-imagen.jpg",
  "stock_quantity": 100,
  "is_available": true
}
```

### **Obtener Producto**

```http
GET /api/v1/products/{product_id}
Authorization: Bearer <token>
```

### **Actualizar Producto**

```http
PUT /api/v1/products/{product_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Producto Actualizado",
  "price": 2000,
  "stock_quantity": 75
}
```

### **Eliminar Producto**

```http
DELETE /api/v1/products/{product_id}
Authorization: Bearer <token>
```

## 📱 Endpoints de WhatsApp

### **Webhook de WhatsApp**

```http
POST /api/v1/whatsapp/webhook
Content-Type: application/json

{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "ENTRY_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "PHONE_NUMBER",
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "messages": [
              {
                "from": "PHONE_NUMBER",
                "id": "MESSAGE_ID",
                "timestamp": "TIMESTAMP",
                "text": {
                  "body": "MESSAGE_TEXT"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

### **Listar Conversaciones**

```http
GET /api/v1/whatsapp/conversations/
Authorization: Bearer <token>
```

**Parámetros de Query:**
- `page` (int): Número de página
- `size` (int): Tamaño de página
- `phone_number` (string): Filtrar por número de teléfono
- `state` (string): Filtrar por estado de conversación
- `active` (bool): Solo conversaciones activas

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "conversation_id": "conv_123",
        "current_state": "initial",
        "message_count": 5,
        "started_at": "2024-01-01T00:00:00Z",
        "last_activity_at": "2024-01-01T00:05:00Z",
        "ended_at": null,
        "context": {
          "user_name": "Usuario",
          "last_message": "Hola"
        },
        "user": {
          "phone_number": "+1234567890",
          "name": "Usuario",
          "profile_name": "Usuario Profile"
        }
      }
    ],
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

### **Obtener Conversación**

```http
GET /api/v1/whatsapp/conversations/{conversation_id}
Authorization: Bearer <token>
```

### **Listar Mensajes**

```http
GET /api/v1/whatsapp/messages/
Authorization: Bearer <token>
```

**Parámetros de Query:**
- `conversation_id` (int): Filtrar por conversación
- `direction` (string): 'inbound' o 'outbound'
- `message_type` (string): Tipo de mensaje
- `date_from` (string): Fecha desde (ISO format)
- `date_to` (string): Fecha hasta (ISO format)

### **Enviar Mensaje**

```http
POST /api/v1/whatsapp/send
Authorization: Bearer <token>
Content-Type: application/json

{
  "to": "+1234567890",
  "message_type": "text",
  "content": {
    "text": "Hola, este es un mensaje de prueba"
  }
}
```

**Tipos de Mensaje Soportados:**

#### **Mensaje de Texto**
```json
{
  "to": "+1234567890",
  "message_type": "text",
  "content": {
    "text": "Mensaje de texto"
  }
}
```

#### **Mensaje con Botones**
```json
{
  "to": "+1234567890",
  "message_type": "interactive",
  "content": {
    "type": "button",
    "header": {
      "type": "text",
      "text": "Título del mensaje"
    },
    "body": {
      "text": "Cuerpo del mensaje"
    },
    "footer": {
      "text": "Pie del mensaje"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "btn_1",
            "title": "Opción 1"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "btn_2",
            "title": "Opción 2"
          }
        }
      ]
    }
  }
}
```

#### **Mensaje de Lista**
```json
{
  "to": "+1234567890",
  "message_type": "interactive",
  "content": {
    "type": "list",
    "header": {
      "type": "text",
      "text": "Lista de opciones"
    },
    "body": {
      "text": "Selecciona una opción:"
    },
    "footer": {
      "text": "Footer opcional"
    },
    "action": {
      "button": "Ver opciones",
      "sections": [
        {
          "title": "Sección 1",
          "rows": [
            {
              "id": "row_1",
              "title": "Opción 1",
              "description": "Descripción opcional"
            }
          ]
        }
      ]
    }
  }
}
```

#### **Mensaje de Imagen**
```json
{
  "to": "+1234567890",
  "message_type": "image",
  "content": {
    "link": "https://ejemplo.com/imagen.jpg",
    "caption": "Descripción de la imagen"
  }
}
```

## 📊 Códigos de Estado

### **Éxito (2xx)**
- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Operación exitosa sin contenido

### **Error del Cliente (4xx)**
- `400 Bad Request`: Solicitud malformada
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: No autorizado
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación
- `429 Too Many Requests`: Rate limit excedido

### **Error del Servidor (5xx)**
- `500 Internal Server Error`: Error interno
- `502 Bad Gateway`: Error de gateway
- `503 Service Unavailable`: Servicio no disponible

## ❌ Manejo de Errores

### **Estructura de Error**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Error de validación",
    "details": [
      {
        "field": "email",
        "message": "Email inválido"
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Códigos de Error Comunes**

- `VALIDATION_ERROR`: Error de validación de datos
- `AUTHENTICATION_ERROR`: Error de autenticación
- `AUTHORIZATION_ERROR`: Error de autorización
- `NOT_FOUND`: Recurso no encontrado
- `DUPLICATE_ERROR`: Recurso duplicado
- `RATE_LIMIT_ERROR`: Límite de velocidad excedido
- `WHATSAPP_API_ERROR`: Error de WhatsApp API
- `DATABASE_ERROR`: Error de base de datos

## 🚦 Rate Limiting

La API implementa rate limiting para proteger contra abuso:

### **Límites por Endpoint**
- **Autenticación**: 5 requests/minuto por IP
- **Usuarios**: 100 requests/minuto por usuario
- **Productos**: 200 requests/minuto por usuario
- **WhatsApp**: 1000 requests/minuto por usuario

### **Headers de Rate Limit**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### **Respuesta de Rate Limit**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_ERROR",
    "message": "Rate limit exceeded",
    "retry_after": 60
  }
}
```

## 💡 Ejemplos de Uso

### **Ejemplo Completo: Crear Usuario y Producto**

```bash
# 1. Registrar usuario
curl -X POST "https://api.yourapp.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ejemplo.com",
    "username": "admin",
    "password": "password123",
    "full_name": "Administrador"
  }'

# 2. Iniciar sesión
curl -X POST "https://api.yourapp.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'

# 3. Crear producto (usando token del paso 2)
curl -X POST "https://api.yourapp.com/api/v1/products/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Producto de Prueba",
    "description": "Descripción del producto",
    "price": 2500,
    "stock_quantity": 100,
    "is_available": true
  }'
```

### **Ejemplo: Enviar Mensaje WhatsApp**

```bash
curl -X POST "https://api.yourapp.com/api/v1/whatsapp/send" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "message_type": "interactive",
    "content": {
      "type": "button",
      "header": {
        "type": "text",
        "text": "¡Bienvenido!"
      },
      "body": {
        "text": "Gracias por contactarnos. ¿En qué podemos ayudarte?"
      },
      "action": {
        "buttons": [
          {
            "type": "reply",
            "reply": {
              "id": "info",
              "title": "Información"
            }
          },
          {
            "type": "reply",
            "reply": {
              "id": "support",
              "title": "Soporte"
            }
          }
        ]
      }
    }
  }'
```

## 🛠️ SDKs y Herramientas

### **Postman Collection**
Descarga la colección de Postman para probar todos los endpoints:
[Descargar Collection](https://api.yourapp.com/docs/postman)

### **OpenAPI Specification**
Especificación completa en formato OpenAPI 3.0:
[Ver OpenAPI Spec](https://api.yourapp.com/api/v1/openapi.json)

### **SDKs Disponibles**
- **Python**: `pip install business-api-client`
- **JavaScript**: `npm install business-api-client`
- **PHP**: `composer require business/api-client`

### **Ejemplo de SDK Python**

```python
from business_api_client import BusinessAPIClient

# Inicializar cliente
client = BusinessAPIClient(
    base_url="https://api.yourapp.com/api/v1",
    api_key="tu_api_key"
)

# Autenticación
token = client.auth.login("usuario", "password")

# Crear producto
product = client.products.create({
    "name": "Nuevo Producto",
    "price": 1000,
    "stock_quantity": 50
})

# Enviar mensaje WhatsApp
message = client.whatsapp.send_message(
    to="+1234567890",
    message_type="text",
    content={"text": "Hola desde Python!"}
)
```

## 📞 Soporte

### **Documentación Interactiva**
- **Swagger UI**: https://api.yourapp.com/docs
- **ReDoc**: https://api.yourapp.com/redoc

### **Contacto**
- **Email**: api-support@yourapp.com
- **GitHub Issues**: [Reportar problemas](https://github.com/yourapp/issues)
- **Discord**: [Comunidad de desarrolladores](https://discord.gg/yourapp)

### **Estado del Servicio**
- **Status Page**: https://status.yourapp.com
- **Uptime**: 99.9%
- **SLA**: 99.5% uptime garantizado

---

*Esta documentación se actualiza con cada nueva versión de la API. Para la versión más reciente, consulta el repositorio del proyecto.*
