"""
Conversation Flow Examples
Examples of how to create conversation flows using the Flow Builder
"""
from app.services.conversation_flow_builder import (
    create_flow_builder, FlowStepType, MessageType
)


def create_welcome_flow():
    """Create a simple welcome flow"""
    return (create_flow_builder("welcome", "Welcome Flow", "Simple welcome conversation")
        .start_with("welcome_message")
        .add_message_step(
            step_id="welcome_message",
            name="Welcome Message",
            message="¡Hola! 👋 Bienvenido a nuestra empresa. ¿En qué puedo ayudarte hoy?",
            message_type=MessageType.TEXT,
            next_step="main_menu"
        )
        .add_choice_step(
            step_id="main_menu",
            name="Main Menu",
            message="Selecciona una opción:",
            options=[
                {"id": "products", "title": "Ver Productos"},
                {"id": "services", "title": "Servicios"},
                {"id": "contact", "title": "Contacto"},
                {"id": "help", "title": "Ayuda"}
            ],
            next_step="process_choice"
        )
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
                },
                {
                    "condition": "choice == 'help'",
                    "next_step": "show_help"
                }
            ]
        )
        .add_message_step(
            step_id="show_products",
            name="Show Products",
            message="Aquí tienes nuestros productos disponibles...",
            next_step="end"
        )
        .add_message_step(
            step_id="show_services",
            name="Show Services",
            message="Estos son nuestros servicios...",
            next_step="end"
        )
        .add_message_step(
            step_id="show_contact",
            name="Show Contact",
            message="📞 Información de contacto:\nTeléfono: +1234567890\nEmail: contacto@empresa.com",
            next_step="end"
        )
        .add_message_step(
            step_id="show_help",
            name="Show Help",
            message="¿Necesitas ayuda? Puedes contactarnos directamente.",
            next_step="end"
        )
        .add_end_step(
            step_id="end",
            name="End",
            message="¡Gracias por contactarnos! 😊"
        )
        .build()
    )


def create_order_flow():
    """Create an order flow"""
    return (create_flow_builder("order", "Order Flow", "Complete order process")
        .start_with("greeting")
        .add_message_step(
            step_id="greeting",
            name="Greeting",
            message="¡Perfecto! Te ayudo con tu pedido. 🛍️",
            next_step="product_selection"
        )
        .add_list_step(
            step_id="product_selection",
            name="Product Selection",
            message="Selecciona el producto que deseas:",
            options=[
                {"id": "product_1", "title": "Café Premium", "description": "$15.99"},
                {"id": "product_2", "title": "Café Orgánico", "description": "$18.99"},
                {"id": "product_3", "title": "Café Especial", "description": "$22.99"}
            ],
            button_text="Ver Productos",
            next_step="collect_info"
        )
        .add_question_step(
            step_id="collect_info",
            name="Collect Information",
            question="Por favor, proporciona la siguiente información:\n\n• Nombre completo\n• Dirección de entrega\n• Teléfono de contacto\n\nResponde con 'listo' cuando hayas enviado toda la información.",
            validation={
                "required": True,
                "min_length": 10
            },
            next_step="confirm_order"
        )
        .add_message_step(
            step_id="confirm_order",
            name="Confirm Order",
            message="📋 Resumen del pedido:\n\nProducto: {selected_product}\nCliente: {customer_name}\nDirección: {address}\nTeléfono: {phone}\n\n¿Confirmas este pedido? Responde 'sí' para confirmar.",
            next_step="process_confirmation"
        )
        .add_condition_step(
            step_id="process_confirmation",
            name="Process Confirmation",
            conditions=[
                {
                    "condition": "confirmation == 'sí'",
                    "next_step": "payment_info"
                },
                {
                    "condition": "confirmation == 'no'",
                    "next_step": "cancel_order"
                }
            ]
        )
        .add_question_step(
            step_id="payment_info",
            name="Payment Information",
            question="💳 Información de pago:\n\n• Método de pago (efectivo/tarjeta/transferencia)\n• Si es tarjeta: últimos 4 dígitos\n\nResponde 'listo' cuando hayas enviado la información.",
            next_step="final_confirmation"
        )
        .add_message_step(
            step_id="final_confirmation",
            name="Final Confirmation",
            message="✅ ¡Pedido confirmado!\n\n📋 Número de pedido: #{order_id}\n📅 Fecha: {date}\n💰 Total: ${total}\n🚚 Estado: Procesando\n\n¡Gracias por tu compra! Te contactaremos pronto.",
            next_step="end"
        )
        .add_message_step(
            step_id="cancel_order",
            name="Cancel Order",
            message="Pedido cancelado. ¿Hay algo más en lo que pueda ayudarte?",
            next_step="end"
        )
        .add_end_step(
            step_id="end",
            name="End",
            message="¡Gracias por contactarnos! 😊"
        )
        .set_variable("order_id", "ORD-{timestamp}")
        .set_error_handler("validation_failed", "show_error")
        .add_message_step(
            step_id="show_error",
            name="Show Error",
            message="Lo siento, hubo un error. Por favor, intenta nuevamente.",
            next_step="collect_info"
        )
        .build()
    )


def create_appointment_flow():
    """Create an appointment booking flow"""
    return (create_flow_builder("appointment", "Appointment Flow", "Book an appointment")
        .start_with("greeting")
        .add_message_step(
            step_id="greeting",
            name="Greeting",
            message="¡Hola! Te ayudo a agendar una cita. 📅",
            next_step="service_selection"
        )
        .add_choice_step(
            step_id="service_selection",
            name="Service Selection",
            message="¿Qué servicio necesitas?",
            options=[
                {"id": "consultation", "title": "Consultoría"},
                {"id": "development", "title": "Desarrollo"},
                {"id": "design", "title": "Diseño"},
                {"id": "support", "title": "Soporte"}
            ],
            next_step="date_selection"
        )
        .add_question_step(
            step_id="date_selection",
            name="Date Selection",
            question="¿Qué fecha prefieres para tu cita?\n\nFormato: DD/MM/YYYY\nEjemplo: 15/12/2024",
            validation={
                "pattern": r"\d{2}/\d{2}/\d{4}",
                "required": True
            },
            next_step="time_selection"
        )
        .add_question_step(
            step_id="time_selection",
            name="Time Selection",
            question="¿A qué hora prefieres?\n\nHorarios disponibles:\n• 09:00 - 10:00\n• 10:00 - 11:00\n• 11:00 - 12:00\n• 14:00 - 15:00\n• 15:00 - 16:00\n\nResponde con la hora deseada (ej: 10:00)",
            validation={
                "pattern": r"\d{2}:\d{2}",
                "required": True
            },
            next_step="contact_info"
        )
        .add_question_step(
            step_id="contact_info",
            name="Contact Information",
            question="Por favor, proporciona tu información de contacto:\n\n• Nombre completo\n• Teléfono\n• Email\n\nResponde con 'listo' cuando hayas enviado toda la información.",
            next_step="confirm_appointment"
        )
        .add_message_step(
            step_id="confirm_appointment",
            name="Confirm Appointment",
            message="📅 Resumen de la cita:\n\nServicio: {selected_service}\nFecha: {selected_date}\nHora: {selected_time}\nCliente: {customer_name}\nTeléfono: {phone}\nEmail: {email}\n\n¿Confirmas esta cita? Responde 'sí' para confirmar.",
            next_step="process_appointment_confirmation"
        )
        .add_condition_step(
            step_id="process_appointment_confirmation",
            name="Process Appointment Confirmation",
            conditions=[
                {
                    "condition": "confirmation == 'sí'",
                    "next_step": "appointment_confirmed"
                },
                {
                    "condition": "confirmation == 'no'",
                    "next_step": "appointment_cancelled"
                }
            ]
        )
        .add_message_step(
            step_id="appointment_confirmed",
            name="Appointment Confirmed",
            message="✅ ¡Cita confirmada!\n\n📅 Fecha: {selected_date}\n⏰ Hora: {selected_time}\n📍 Ubicación: Oficina Principal\n📝 Servicio: {selected_service}\n\n¡Te esperamos! 😊",
            next_step="end"
        )
        .add_message_step(
            step_id="appointment_cancelled",
            name="Appointment Cancelled",
            message="Cita cancelada. ¿Te gustaría agendar para otra fecha?",
            next_step="end"
        )
        .add_end_step(
            step_id="end",
            name="End",
            message="¡Gracias por contactarnos! 😊"
        )
        .set_error_handler("validation_failed", "show_error")
        .add_message_step(
            step_id="show_error",
            name="Show Error",
            message="Lo siento, el formato no es correcto. Por favor, intenta nuevamente.",
            next_step="date_selection"
        )
        .build()
    )


def create_support_flow():
    """Create a customer support flow"""
    return (create_flow_builder("support", "Support Flow", "Customer support flow")
        .start_with("greeting")
        .add_message_step(
            step_id="greeting",
            name="Greeting",
            message="¡Hola! Soy tu asistente de soporte. ¿En qué puedo ayudarte? 🛠️",
            next_step="issue_type"
        )
        .add_choice_step(
            step_id="issue_type",
            name="Issue Type",
            message="¿Cuál es el tipo de problema?",
            options=[
                {"id": "technical", "title": "Problema Técnico"},
                {"id": "billing", "title": "Facturación"},
                {"id": "account", "title": "Cuenta"},
                {"id": "other", "title": "Otro"}
            ],
            next_step="collect_details"
        )
        .add_question_step(
            step_id="collect_details",
            name="Collect Details",
            question="Por favor, describe el problema en detalle:\n\n• ¿Qué está pasando?\n• ¿Cuándo comenzó?\n• ¿Qué has intentado para solucionarlo?\n\nResponde con 'listo' cuando hayas enviado toda la información.",
            next_step="priority_assessment"
        )
        .add_condition_step(
            step_id="priority_assessment",
            name="Priority Assessment",
            conditions=[
                {
                    "condition": "issue_type == 'technical'",
                    "next_step": "technical_support"
                },
                {
                    "condition": "issue_type == 'billing'",
                    "next_step": "billing_support"
                },
                {
                    "condition": "issue_type == 'account'",
                    "next_step": "account_support"
                },
                {
                    "condition": "issue_type == 'other'",
                    "next_step": "general_support"
                }
            ]
        )
        .add_message_step(
            step_id="technical_support",
            name="Technical Support",
            message="🔧 Tu problema técnico ha sido registrado.\n\nTicket: #{ticket_id}\nPrioridad: Alta\nTiempo estimado: 2-4 horas\n\nUn técnico se pondrá en contacto contigo pronto.",
            next_step="end"
        )
        .add_message_step(
            step_id="billing_support",
            name="Billing Support",
            message="💳 Tu consulta de facturación ha sido registrada.\n\nTicket: #{ticket_id}\nPrioridad: Media\nTiempo estimado: 24 horas\n\nEl equipo de facturación revisará tu caso.",
            next_step="end"
        )
        .add_message_step(
            step_id="account_support",
            name="Account Support",
            message="👤 Tu consulta de cuenta ha sido registrada.\n\nTicket: #{ticket_id}\nPrioridad: Media\nTiempo estimado: 24 horas\n\nEl equipo de cuentas te contactará pronto.",
            next_step="end"
        )
        .add_message_step(
            step_id="general_support",
            name="General Support",
            message="📋 Tu consulta ha sido registrada.\n\nTicket: #{ticket_id}\nPrioridad: Baja\nTiempo estimado: 48 horas\n\nUn agente revisará tu caso.",
            next_step="end"
        )
        .add_end_step(
            step_id="end",
            name="End",
            message="¡Gracias por contactarnos! Te mantendremos informado sobre el progreso. 😊"
        )
        .set_variable("ticket_id", "TKT-{timestamp}")
        .build()
    )


# Flow registry
AVAILABLE_FLOWS = {
    "welcome": create_welcome_flow,
    "order": create_order_flow,
    "appointment": create_appointment_flow,
    "support": create_support_flow
}


def get_flow(flow_id: str):
    """Get a flow by ID"""
    if flow_id not in AVAILABLE_FLOWS:
        raise ValueError(f"Flow {flow_id} not found")
    
    return AVAILABLE_FLOWS[flow_id]()
