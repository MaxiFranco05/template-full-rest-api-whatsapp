# Sistema de Flujos Conversacionales Profesional

## 🎯 **Visión General**

El Sistema de Flujos Conversacionales Profesional es una solución completa para crear, gestionar y ejecutar flujos de conversación complejos en WhatsApp Business API. Utiliza un enfoque basado en **Domain Specific Language (DSL)** que permite definir flujos de forma declarativa y profesional.

## 🚀 **Características Principales**

### ✅ **Ventajas del Nuevo Sistema**

- **🔧 Fácil de usar**: Definir flujos con código Python simple, JSON o YAML
- **📊 Escalable**: Soporte para flujos complejos con subflujos y ramificaciones
- **🛡️ Robusto**: Manejo de errores y validaciones integradas
- **🔄 Reutilizable**: Componentes modulares y reutilizables
- **📝 Declarativo**: Configuración clara y mantenible
- **🧪 Testeable**: Fácil de probar y debuggear
- **📈 Monitoreable**: Logs detallados y métricas

### ❌ **Problemas Resueltos del Sistema Anterior**

- ❌ Estados hardcodeados → ✅ Estados dinámicos
- ❌ Transiciones manuales → ✅ Transiciones automáticas
- ❌ Lógica dispersa → ✅ Lógica centralizada
- ❌ Difícil mantenimiento → ✅ Fácil mantenimiento
- ❌ No reutilizable → ✅ Altamente reutilizable

## 🏗️ **Arquitectura del Sistema**

```
┌─────────────────────────────────────────────────────────────┐
│                    Flow Builder DSL                         │
├─────────────────────────────────────────────────────────────┤
│  Python Builder  │  JSON/YAML Loader  │  Flow Registry         │
├─────────────────────────────────────────────────────────────┤
│                    Flow Executor                            │
├─────────────────────────────────────────────────────────────┤
│  Step Executor  │  Condition Evaluator  │  Action Handler    │
├─────────────────────────────────────────────────────────────┤
│              WhatsApp Service Integration                    │
└─────────────────────────────────────────────────────────────┘
```

## 📋 **Tipos de Pasos Disponibles**

### 1. **MESSAGE** - Mensaje Simple
```python
.add_message_step(
    step_id="welcome",
    name="Welcome Message",
    message="¡Hola! Bienvenido a nuestra empresa.",
    message_type=MessageType.TEXT,
    next_step="main_menu"
)
```

### 2. **QUESTION** - Pregunta con Validación
```python
.add_question_step(
    step_id="collect_email",
    name="Collect Email",
    question="Por favor, proporciona tu email:",
    validation={
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "required": True,
        "error_message": "Email inválido. Por favor, ingresa un email válido."
    },
    next_step="confirm_email"
)
```

### 3. **CHOICE** - Opciones con Botones
```python
.add_choice_step(
    step_id="main_menu",
    name="Main Menu",
    message="Selecciona una opción:",
    options=[
        {"id": "products", "title": "Ver Productos"},
        {"id": "services", "title": "Servicios"},
        {"id": "contact", "title": "Contacto"}
    ],
    next_step="process_choice"
)
```

### 4. **LIST** - Lista Desplegable
```python
.add_list_step(
    step_id="product_list",
    name="Product List",
    message="Selecciona un producto:",
    options=[
        {"id": "prod_1", "title": "Café Premium", "description": "$15.99"},
        {"id": "prod_2", "title": "Café Orgánico", "description": "$18.99"}
    ],
    button_text="Ver Productos",
    next_step="product_selected"
)
```

### 5. **CONDITION** - Lógica Condicional
```python
.add_condition_step(
    step_id="process_choice",
    name="Process Choice",
    conditions=[
        {
            "condition": "choice == 'products'",
            "next_step": "show_products"
        },
        {
            "condition": "choice == 'services'",
            "next_step": "show_services"
        },
        {
            "condition": "choice == 'contact'",
            "next_step": "show_contact"
        }
    ]
)
```

### 6. **ACTION** - Ejecutar Acciones
```python
.add_action_step(
    step_id="save_order",
    name="Save Order",
    actions=[
        "create_order",
        "send_confirmation_email",
        "update_inventory"
    ],
    next_step="order_saved"
)
```

### 7. **WAIT** - Esperar con Timeout
```python
.add_wait_step(
    step_id="wait_payment",
    name="Wait Payment",
    timeout=300  # 5 minutos
)
```

### 8. **END** - Finalizar Conversación
```python
.add_end_step(
    step_id="end",
    name="End",
    message="¡Gracias por contactarnos! 😊"
)
```

## 🔧 **Cómo Crear un Flujo**

### **Método 1: Python Builder**

```python
from app.services.conversation_flow_builder import create_flow_builder, MessageType

def create_order_flow():
    return (create_flow_builder("order", "Order Flow", "Complete order process")
        .start_with("greeting")
        .add_message_step(
            step_id="greeting",
            name="Greeting",
            message="¡Perfecto! Te ayudo con tu pedido. 🛍️",
            next_step="product_selection"
        )
        .add_choice_step(
            step_id="product_selection",
            name="Product Selection",
            message="Selecciona el producto:",
            options=[
                {"id": "product_1", "title": "Café Premium"},
                {"id": "product_2", "title": "Café Orgánico"}
            ],
            next_step="collect_info"
        )
        .add_question_step(
            step_id="collect_info",
            name="Collect Information",
            question="Proporciona tu información de contacto:",
            validation={"required": True},
            next_step="confirm_order"
        )
        .add_message_step(
            step_id="confirm_order",
            name="Confirm Order",
            message="¿Confirmas este pedido?",
            next_step="end"
        )
        .add_end_step(
            step_id="end",
            name="End",
            message="¡Pedido confirmado! Gracias."
        )
        .set_variable("order_id", "ORD-{timestamp}")
        .set_error_handler("validation_failed", "show_error")
        .build()
    )
```

### **Método 2: JSON Configuration**

```json
{
  "id": "order",
  "name": "Order Flow",
  "description": "Complete order process",
  "start_step": "greeting",
  "variables": {
    "order_id": "ORD-{timestamp}"
  },
  "error_handling": {
    "validation_failed": "show_error"
  },
  "steps": [
    {
      "id": "greeting",
      "type": "message",
      "name": "Greeting",
      "message": "¡Perfecto! Te ayudo con tu pedido. 🛍️",
      "next_step": "product_selection"
    },
    {
      "id": "product_selection",
      "type": "choice",
      "name": "Product Selection",
      "message": "Selecciona el producto:",
      "choice_type": "buttons",
      "options": [
        {
          "id": "product_1",
          "title": "Café Premium"
        },
        {
          "id": "product_2",
          "title": "Café Orgánico"
        }
      ],
      "next_step": "collect_info"
    },
    {
      "id": "collect_info",
      "type": "question",
      "name": "Collect Information",
      "question": "Proporciona tu información de contacto:",
      "validation": {
        "required": true
      },
      "next_step": "confirm_order"
    },
    {
      "id": "confirm_order",
      "type": "message",
      "name": "Confirm Order",
      "message": "¿Confirmas este pedido?",
      "next_step": "end"
    },
    {
      "id": "end",
      "type": "end",
      "name": "End",
      "message": "¡Pedido confirmado! Gracias."
    }
  ]
}
```

### **Método 3: YAML Configuration**

```yaml
# app/flows/order.yaml
id: order
name: Order Flow
description: Complete order process
start_step: greeting

variables:
  order_id: "ORD-{timestamp}"

error_handling:
  validation_failed: show_error

steps:
  - id: greeting
    type: message
    name: Greeting
    message: "¡Perfecto! Te ayudo con tu pedido. 🛍️"
    next_step: product_selection

  - id: product_selection
    type: choice
    name: Product Selection
    message: "Selecciona el producto:"
    choice_type: buttons
    options:
      - id: product_1
        title: "Café Premium"
      - id: product_2
        title: "Café Orgánico"
    next_step: collect_info

  - id: collect_info
    type: question
    name: Collect Information
    question: "Proporciona tu información de contacto:"
    validation:
      required: true
    next_step: confirm_order

  - id: confirm_order
    type: message
    name: Confirm Order
    message: "¿Confirmas este pedido?"
    next_step: end

  - id: end
    type: end
    name: End
    message: "¡Pedido confirmado! Gracias."
```

## 📊 **JSON vs YAML: ¿Cuál Elegir?**

### **JSON - Ventajas:**
- ✅ **Estándar universal**: Soporte nativo en todos los lenguajes
- ✅ **Validación**: Esquemas JSON para validación estricta
- ✅ **Herramientas**: Editores con autocompletado y validación
- ✅ **APIs**: Fácil integración con APIs REST
- ✅ **Performance**: Parsing más rápido
- ✅ **Compatibilidad**: Funciona en cualquier entorno

### **YAML - Ventajas:**
- ✅ **Legibilidad**: Sintaxis más limpia y legible
- ✅ **Comentarios**: Soporte para comentarios
- ✅ **Multilínea**: Texto multilínea más fácil
- ✅ **Menos verboso**: Menos caracteres que JSON
- ✅ **Configuración**: Ideal para archivos de configuración

### **Recomendación:**
- **JSON**: Para flujos complejos, APIs, y entornos de producción
- **YAML**: Para configuración simple, documentación, y desarrollo

### **Conversión Automática:**
```python
# Convertir YAML a JSON
loader = create_unified_flow_loader()
loader.convert_yaml_to_json("welcome")

# Convertir JSON a YAML  
loader.convert_json_to_yaml("order")
```

## 🚀 **Cómo Usar el Sistema**

### **1. Registrar Flujos**

```python
from app.services.conversation_flow_builder import create_flow_executor
from app.services.unified_flow_loader import create_unified_flow_loader

# Crear executor
executor = create_flow_executor(whatsapp_service, persistence_service)

# Crear loader unificado (soporta JSON y YAML)
loader = create_unified_flow_loader("app/flows")

# Cargar todos los flujos automáticamente
flows = loader.load_all_flows()
for flow_id, flow in flows.items():
    executor.register_flow(flow)
    print(f"✅ Flow loaded: {flow_id}")
```

### **2. Iniciar Conversación**

```python
# Iniciar conversación con flujo específico
result = executor.start_conversation(
    phone_number="+1234567890",
    flow_id="order",
    initial_data={"customer_type": "premium"}
)
```

### **3. Procesar Respuestas**

```python
# Procesar respuesta del usuario
result = executor.execute_step(
    conversation_id="conversation_123",
    user_input="product_1"
)
```

## 🛡️ **Manejo de Errores**

### **Validaciones Integradas**

```python
validation = {
    "required": True,
    "min_length": 3,
    "max_length": 50,
    "pattern": r"^[a-zA-Z\s]+$",
    "error_message": "Nombre inválido. Solo letras y espacios."
}
```

### **Manejo de Errores por Tipo**

```python
.set_error_handler("validation_failed", "show_validation_error")
.set_error_handler("timeout", "show_timeout_message")
.set_error_handler("network_error", "show_network_error")
```

### **Pasos de Error**

```python
.add_message_step(
    step_id="show_validation_error",
    name="Show Validation Error",
    message="Lo siento, el formato no es correcto. Por favor, intenta nuevamente.",
    next_step="retry_step"
)
```

## 📊 **Variables y Contexto**

### **Variables de Flujo**

```python
.set_variable("order_id", "ORD-{timestamp}")
.set_variable("company_name", "Mi Empresa")
.set_variable("support_hours", "9:00 - 18:00")
```

### **Uso en Mensajes**

```python
message="¡Hola! Bienvenido a {{company_name}}. Horario: {{support_hours}}"
```

### **Datos de Usuario**

```python
# Los datos se almacenan automáticamente
state["data"]["customer_name"] = "Juan Pérez"
state["data"]["email"] = "juan@email.com"
state["data"]["selected_product"] = "product_1"
```

## 🔄 **Subflujos y Ramificaciones**

### **Subflujos**

```python
# Flujo principal
.add_condition_step(
    step_id="check_user_type",
    name="Check User Type",
    conditions=[
        {
            "condition": "user_type == 'premium'",
            "next_step": "premium_flow"
        },
        {
            "condition": "user_type == 'regular'",
            "next_step": "regular_flow"
        }
    ]
)

# Subflujo premium
.add_message_step(
    step_id="premium_flow",
    name="Premium Flow",
    message="Como usuario premium, tienes acceso a...",
    next_step="premium_options"
)
```

### **Ramificaciones Complejas**

```python
.add_condition_step(
    step_id="complex_routing",
    name="Complex Routing",
    conditions=[
        {
            "condition": "product_type == 'digital' and user_type == 'premium'",
            "next_step": "digital_premium_flow"
        },
        {
            "condition": "product_type == 'digital' and user_type == 'regular'",
            "next_step": "digital_regular_flow"
        },
        {
            "condition": "product_type == 'physical'",
            "next_step": "physical_flow"
        },
        {
            "condition": "product_type == 'service'",
            "next_step": "service_flow"
        }
    ]
)
```

## 📈 **Monitoreo y Logs**

### **Logs Automáticos**

```python
# El sistema genera logs automáticamente
logger.info(f"Flow started: {flow_id} for {phone_number}")
logger.info(f"Step executed: {step_id} - {step_type}")
logger.info(f"Flow completed: {flow_id} - Duration: {duration}")
```

### **Métricas Disponibles**

- ✅ Tiempo de ejecución por paso
- ✅ Tasa de finalización de flujos
- ✅ Puntos de abandono
- ✅ Errores por tipo
- ✅ Validaciones fallidas

## 🧪 **Testing**

### **Test de Flujos**

```python
def test_order_flow():
    executor = create_flow_executor(mock_whatsapp_service, mock_persistence_service)
    executor.register_flow(get_flow("order"))
    
    # Test inicio
    result = executor.start_conversation("+1234567890", "order")
    assert result["success"] == True
    assert result["step_id"] == "greeting"
    
    # Test selección de producto
    result = executor.execute_step("conversation_123", "product_1")
    assert result["success"] == True
    assert result["user_choice"]["id"] == "product_1"
```

## 🎯 **Casos de Uso Avanzados**

### **1. Flujo de Pedidos Complejo**

```python
def create_complex_order_flow():
    return (create_flow_builder("complex_order", "Complex Order Flow")
        .start_with("greeting")
        .add_message_step("greeting", "Greeting", "¡Hola! Te ayudo con tu pedido.")
        .add_choice_step("product_category", "Product Category", "¿Qué tipo de producto?", [
            {"id": "food", "title": "Comida"},
            {"id": "drinks", "title": "Bebidas"},
            {"id": "desserts", "title": "Postres"}
        ])
        .add_condition_step("route_by_category", "Route by Category", [
            {"condition": "category == 'food'", "next_step": "food_menu"},
            {"condition": "category == 'drinks'", "next_step": "drinks_menu"},
            {"condition": "category == 'desserts'", "next_step": "desserts_menu"}
        ])
        .add_list_step("food_menu", "Food Menu", "Selecciona tu comida:", [
            {"id": "pizza", "title": "Pizza", "description": "$12.99"},
            {"id": "burger", "title": "Hamburguesa", "description": "$9.99"},
            {"id": "pasta", "title": "Pasta", "description": "$11.99"}
        ])
        .add_question_step("quantity", "Quantity", "¿Cuántas unidades?")
        .add_question_step("delivery_info", "Delivery Info", "Información de entrega:")
        .add_choice_step("payment_method", "Payment Method", "Método de pago:", [
            {"id": "cash", "title": "Efectivo"},
            {"id": "card", "title": "Tarjeta"},
            {"id": "transfer", "title": "Transferencia"}
        ])
        .add_action_step("process_order", "Process Order", [
            "calculate_total",
            "create_order",
            "send_confirmation"
        ])
        .add_end_step("end", "End", "¡Pedido confirmado!")
        .build()
    )
```

### **2. Flujo de Soporte Multi-Nivel**

```python
def create_support_flow():
    return (create_flow_builder("support", "Support Flow")
        .start_with("greeting")
        .add_message_step("greeting", "Greeting", "¡Hola! Soy tu asistente de soporte.")
        .add_choice_step("issue_type", "Issue Type", "¿Cuál es el problema?", [
            {"id": "technical", "title": "Problema Técnico"},
            {"id": "billing", "title": "Facturación"},
            {"id": "account", "title": "Cuenta"},
            {"id": "other", "title": "Otro"}
        ])
        .add_condition_step("route_issue", "Route Issue", [
            {"condition": "issue_type == 'technical'", "next_step": "technical_support"},
            {"condition": "issue_type == 'billing'", "next_step": "billing_support"},
            {"condition": "issue_type == 'account'", "next_step": "account_support"},
            {"condition": "issue_type == 'other'", "next_step": "general_support"}
        ])
        .add_question_step("issue_details", "Issue Details", "Describe el problema:")
        .add_choice_step("priority", "Priority", "¿Qué tan urgente es?", [
            {"id": "high", "title": "Muy Urgente"},
            {"id": "medium", "title": "Urgente"},
            {"id": "low", "title": "No Urgente"}
        ])
        .add_action_step("create_ticket", "Create Ticket", [
            "generate_ticket_id",
            "assign_priority",
            "notify_support_team"
        ])
        .add_message_step("ticket_created", "Ticket Created", 
                         "Ticket creado: #{ticket_id}. Tiempo estimado: {estimated_time}")
        .add_end_step("end", "End", "¡Gracias! Te contactaremos pronto.")
        .set_variable("ticket_id", "TKT-{timestamp}")
        .build()
    )
```

## 🚀 **Migración del Sistema Anterior**

### **Paso 1: Crear Flujos Nuevos**

```python
# Reemplazar el sistema anterior
# ANTES: Estados hardcodeados en conversation_service.py
# DESPUÉS: Flujos definidos con Flow Builder

def migrate_welcome_flow():
    return (create_flow_builder("welcome", "Welcome Flow")
        .start_with("welcome_message")
        .add_message_step("welcome_message", "Welcome", "¡Hola! Bienvenido.")
        .add_choice_step("main_menu", "Main Menu", "Selecciona:", [
            {"id": "products", "title": "Productos"},
            {"id": "services", "title": "Servicios"}
        ])
        .add_end_step("end", "End", "¡Gracias!")
        .build()
    )
```

### **Paso 2: Integrar con WhatsApp Service**

```python
# Modificar whatsapp_service.py
class WhatsAppService:
    def __init__(self):
        # ... código existente ...
        self.flow_executor = create_flow_executor(self, persistence_service)
        self.flow_executor.register_flow(migrate_welcome_flow())
    
    async def process_incoming_message(self, message_data, db_session=None):
        # ... código existente ...
        
        # Usar flow executor en lugar de lógica hardcodeada
        if conversation.state == "initial":
            result = self.flow_executor.start_conversation(
                phone_number=from_number,
                flow_id="welcome",
                initial_data=contact_info
            )
        else:
            result = self.flow_executor.execute_step(
                conversation_id=conversation.conversation_id,
                user_input=content
            )
        
        return result
```

## 📚 **Documentación de Referencia**

### **API Completa**

```python
# FlowBuilder Methods
builder.start_with(step_id: str) -> FlowBuilder
builder.add_message_step(step_id, name, message, message_type, next_step) -> FlowBuilder
builder.add_question_step(step_id, name, question, validation, next_step) -> FlowBuilder
builder.add_choice_step(step_id, name, message, options, next_step) -> FlowBuilder
builder.add_list_step(step_id, name, message, options, button_text, next_step) -> FlowBuilder
builder.add_condition_step(step_id, name, conditions) -> FlowBuilder
builder.add_action_step(step_id, name, actions, next_step) -> FlowBuilder
builder.add_wait_step(step_id, name, timeout) -> FlowBuilder
builder.add_end_step(step_id, name, message) -> FlowBuilder
builder.set_variable(key, value) -> FlowBuilder
builder.set_error_handler(error_type, handler_step) -> FlowBuilder
builder.set_metadata(key, value) -> FlowBuilder
builder.build() -> FlowDefinition

# FlowExecutor Methods
executor.register_flow(flow: FlowDefinition)
executor.start_conversation(phone_number, flow_id, initial_data) -> Dict[str, Any]
executor.execute_step(conversation_id, user_input) -> Dict[str, Any]
```

### **Tipos de Datos**

```python
FlowStepType.MESSAGE
FlowStepType.QUESTION
FlowStepType.CHOICE
FlowStepType.CONDITION
FlowStepType.ACTION
FlowStepType.WAIT
FlowStepType.END

MessageType.TEXT
MessageType.BUTTONS
MessageType.LIST
MessageType.MEDIA
MessageType.LOCATION
MessageType.CONTACT
MessageType.STICKER
MessageType.TEMPLATE
```

## 🎉 **Conclusión**

El Sistema de Flujos Conversacionales Profesional proporciona:

- ✅ **Simplicidad**: Crear flujos complejos con código simple
- ✅ **Flexibilidad**: Soporte para cualquier tipo de conversación
- ✅ **Mantenibilidad**: Código limpio y fácil de mantener
- ✅ **Escalabilidad**: Crecer sin límites
- ✅ **Profesionalismo**: Solución enterprise-ready

¡Con este sistema, crear flujos conversacionales complejos es tan fácil como escribir unas pocas líneas de código! 🚀
