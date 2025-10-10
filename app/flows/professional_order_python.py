"""
Professional Order Flow - Python Example
Shows how to create a professional flow using Python code
"""
from app.services.professional_flow_system import (
    create_professional_flow_builder, MessageType, DataSourceType
)


def create_flow():
    """Create the professional order flow using Python builder"""
    return (create_professional_flow_builder(
        "professional_order_python", 
        "Professional Order Flow (Python)", 
        "Complete order flow with functions, data sources, and error handling"
    )
    .start_with("greeting")
    
    # Add data sources
    .add_data_source(
        name="products_db",
        source_type=DataSourceType.DATABASE,
        config={
            "table": "products",
            "query": "SELECT * FROM products WHERE active = true"
        },
        cache_ttl=300
    )
    .add_data_source(
        name="customer_api",
        source_type=DataSourceType.API,
        config={
            "url": "https://api.example.com/customers",
            "method": "GET",
            "headers": {
                "Authorization": "Bearer {{api_token}}"
            }
        },
        cache_ttl=600
    )
    .add_data_source(
        name="pricing_config",
        source_type=DataSourceType.FILE,
        config={
            "path": "config/pricing.json"
        },
        cache_ttl=3600
    )
    
    # Add functions
    .add_function(
        name="validate_email",
        module="app.utils.validators",
        function="validate_email",
        parameters={
            "email": "{{user_email}}"
        },
        timeout=5,
        retry_count=2,
        error_handler="email_validation_error",
        cache_result=False
    )
    .add_function(
        name="calculate_total",
        module="app.services.pricing",
        function="calculate_order_total",
        parameters={
            "items": "{{order_items}}",
            "delivery_fee": "{{delivery_fee}}",
            "tax_rate": "{{tax_rate}}"
        },
        timeout=10,
        retry_count=3,
        error_handler="pricing_error",
        cache_result=True
    )
    .add_function(
        name="create_order",
        module="app.services.order_service",
        function="create_order",
        parameters={
            "customer_data": "{{customer_info}}",
            "items": "{{order_items}}",
            "total": "{{calculated_total}}"
        },
        timeout=30,
        retry_count=3,
        error_handler="order_creation_error",
        cache_result=False
    )
    .add_function(
        name="send_confirmation",
        module="app.services.notification_service",
        function="send_order_confirmation",
        parameters={
            "order_id": "{{order_id}}",
            "customer_email": "{{customer_email}}",
            "order_details": "{{order_summary}}"
        },
        timeout=15,
        retry_count=2,
        error_handler="notification_error",
        cache_result=False
    )
    
    # Add steps
    .add_message_step(
        step_id="greeting",
        name="Greeting",
        message="¡Hola! Bienvenido a {{company_name}}. Te ayudo con tu pedido. 🛍️",
        next_step="product_selection"
    )
    .add_choice_step(
        step_id="product_selection",
        name="Product Selection",
        message="Selecciona el producto que deseas:",
        options=[
            {"id": "product_1", "title": "Café Premium", "description": "$15.99"},
            {"id": "product_2", "title": "Café Orgánico", "description": "$18.99"},
            {"id": "product_3", "title": "Café Especial", "description": "$22.99"}
        ],
        next_step="collect_quantity",
        data_sources=["products_db"]
    )
    .add_question_step(
        step_id="collect_quantity",
        name="Collect Quantity",
        question="¿Cuántas unidades deseas?",
        validation={
            "required": True,
            "min_value": 1,
            "max_value": 10,
            "error_message": "Por favor, ingresa una cantidad entre 1 y 10."
        },
        next_step="collect_customer_info"
    )
    .add_question_step(
        step_id="collect_customer_info",
        name="Collect Customer Info",
        question="Por favor, proporciona la siguiente información:\n\n• Nombre completo\n• Email\n• Teléfono\n• Dirección de entrega\n\nResponde con 'listo' cuando hayas enviado toda la información.",
        validation={
            "required": True,
            "min_length": 20,
            "error_message": "Por favor, proporciona información completa."
        },
        next_step="calculate_pricing",
        functions=["validate_email"]
    )
    .add_function_step(
        step_id="calculate_pricing",
        name="Calculate Pricing",
        functions=["calculate_total"],
        next_step="confirm_order"
    )
    .add_message_step(
        step_id="confirm_order",
        name="Confirm Order",
        message="📋 Resumen del pedido:\n\n🛍️ Producto: {{selected_product}}\n📦 Cantidad: {{quantity}}\n👤 Cliente: {{customer_name}}\n📧 Email: {{customer_email}}\n📱 Teléfono: {{customer_phone}}\n📍 Dirección: {{delivery_address}}\n💰 Subtotal: ${{subtotal}}\n🚚 Delivery: ${{delivery_fee}}\n💳 Total: ${{total}}\n\n¿Confirmas este pedido?",
        next_step="process_confirmation"
    )
    .add_condition_step(
        step_id="process_confirmation",
        name="Process Confirmation",
        conditions=[
            {
                "condition": "confirmation == 'sí'",
                "next_step": "create_order"
            },
            {
                "condition": "confirmation == 'si'",
                "next_step": "create_order"
            },
            {
                "condition": "confirmation == 'yes'",
                "next_step": "create_order"
            },
            {
                "condition": "confirmation == 'no'",
                "next_step": "cancel_order"
            },
            {
                "condition": "confirmation == 'cancelar'",
                "next_step": "cancel_order"
            }
        ]
    )
    .add_function_step(
        step_id="create_order",
        name="Create Order",
        functions=["create_order"],
        next_step="send_confirmation"
    )
    .add_function_step(
        step_id="send_confirmation",
        name="Send Confirmation",
        functions=["send_confirmation"],
        next_step="final_confirmation"
    )
    .add_message_step(
        step_id="final_confirmation",
        name="Final Confirmation",
        message="✅ ¡Pedido confirmado!\n\n📋 Número de pedido: {{order_id}}\n📅 Fecha: {{order_date}}\n💰 Total: ${{total}}\n🚚 Estado: Procesando\n⏰ Tiempo estimado: 30-45 minutos\n📧 Confirmación enviada a: {{customer_email}}\n\n¡Gracias por tu compra! Te contactaremos pronto.",
        next_step="end"
    )
    .add_message_step(
        step_id="cancel_order",
        name="Cancel Order",
        message="❌ Pedido cancelado. ¿Hay algo más en lo que pueda ayudarte?",
        next_step="end"
    )
    
    # Error handling steps
    .add_message_step(
        step_id="show_validation_error",
        name="Show Validation Error",
        message="❌ Lo siento, el formato no es correcto. Por favor, intenta nuevamente.",
        next_step="collect_quantity"
    )
    .add_message_step(
        step_id="show_email_error",
        name="Show Email Error",
        message="❌ El email proporcionado no es válido. Por favor, ingresa un email válido.",
        next_step="collect_customer_info"
    )
    .add_message_step(
        step_id="show_pricing_error",
        name="Show Pricing Error",
        message="❌ Error al calcular el precio. Por favor, intenta nuevamente o contacta soporte.",
        next_step="collect_quantity"
    )
    .add_message_step(
        step_id="show_order_error",
        name="Show Order Error",
        message="❌ Error al crear el pedido. Por favor, contacta soporte técnico.",
        next_step="end"
    )
    .add_message_step(
        step_id="show_notification_error",
        name="Show Notification Error",
        message="⚠️ El pedido se creó correctamente, pero hubo un problema enviando la confirmación por email. Te contactaremos pronto.",
        next_step="end"
    )
    .add_message_step(
        step_id="show_timeout",
        name="Show Timeout",
        message="⏰ La conversación ha expirado. ¿Te gustaría empezar de nuevo?",
        next_step="greeting"
    )
    .add_message_step(
        step_id="show_invalid_choice",
        name="Show Invalid Choice",
        message="❌ Opción no válida. Por favor, selecciona una de las opciones disponibles.",
        next_step="product_selection"
    )
    .add_end_step(
        step_id="end",
        name="End",
        message="¡Gracias por contactarnos! 😊"
    )
    
    # Set variables
    .set_variable("order_id", "ORD-{timestamp}")
    .set_variable("company_name", "Mi Empresa")
    .set_variable("delivery_fee", 5.00)
    .set_variable("tax_rate", 0.10)
    .set_variable("currency", "USD")
    
    # Set error handlers
    .set_error_handler("validation_failed", "show_validation_error")
    .set_error_handler("timeout", "show_timeout")
    .set_error_handler("invalid_choice", "show_invalid_choice")
    .set_error_handler("email_validation_error", "show_email_error")
    .set_error_handler("pricing_error", "show_pricing_error")
    .set_error_handler("order_creation_error", "show_order_error")
    .set_error_handler("notification_error", "show_notification_error")
    
    # Set metadata
    .set_metadata("version", "2.0")
    .set_metadata("author", "Template Creator")
    .set_metadata("last_updated", "2024-10-10")
    .set_metadata("tags", ["order", "ecommerce", "payment", "professional"])
    .set_metadata("features", ["functions", "data_sources", "error_handling", "validation"])
    .set_metadata("complexity", "high")
    
    .build()
    )


# Export the flow
flow = create_flow()
