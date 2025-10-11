"""
Main Flow - Python Version
Simple main flow that greets differently for first message vs returning users
"""
from app.services.flows.executor import (
    create_professional_flow_builder, MessageType, FlowStepType
)


def create_flow():
    """Create the main flow using Python builder"""
    return (create_professional_flow_builder(
        "main_python", 
        "Main Flow (Python)", 
        "Simple main flow that greets differently for first message vs returning users"
    )
    .start_with("check_user_status")
    
    # Add steps
    .add_condition_step(
        step_id="check_user_status",
        name="Check User Status",
        conditions=[
            {
                "condition": "is_first_message == true",
                "next_step": "first_time_greeting"
            },
            {
                "condition": "is_first_message == false",
                "next_step": "returning_user_greeting"
            }
        ]
    )
    .add_message_step(
        step_id="first_time_greeting",
        name="First Time Greeting",
        message="¡Hola! 👋 Bienvenido a {{company_name}}. Soy tu asistente virtual y estoy aquí para ayudarte. ¿En qué puedo asistirte hoy?",
        next_step="wait_for_response"
    )
    .add_message_step(
        step_id="returning_user_greeting",
        name="Returning User Greeting",
        message="¡Hola de nuevo! 😊 Me alegra verte otra vez. ¿En qué más puedo ayudarte hoy?",
        next_step="wait_for_response"
    )
    .add_question_step(
        step_id="wait_for_response",
        name="Wait for Response",
        question="Escribe tu consulta o pregunta:",
        validation={
            "required": True,
            "min_length": 2,
            "error_message": "Por favor, escribe tu consulta."
        },
        next_step="process_response"
    )
    .add_message_step(
        step_id="process_response",
        name="Process Response",
        message="Gracias por tu mensaje. He recibido tu consulta y la procesaré pronto. ¿Hay algo más en lo que pueda ayudarte?",
        next_step="end"
    )
    .add_message_step(
        step_id="show_error",
        name="Show Error",
        message="❌ Lo siento, hubo un error. Por favor, intenta nuevamente.",
        next_step="wait_for_response"
    )
    .add_message_step(
        step_id="show_timeout",
        name="Show Timeout",
        message="⏰ La conversación ha expirado. ¿Te gustaría empezar de nuevo?",
        next_step="check_user_status"
    )
    .add_end_step(
        step_id="end",
        name="End",
        message="¡Gracias por contactarnos! 😊"
    )
    
    # Set variables
    .set_variable("company_name", "{{company_name}}")
    .set_variable("support_hours", "9:00 - 18:00")
    
    # Set error handlers
    .set_error_handler("validation_failed", "show_error")
    .set_error_handler("timeout", "show_timeout")
    
    # Set metadata
    .set_metadata("version", "1.0")
    .set_metadata("author", "Template Creator")
    .set_metadata("last_updated", "2024-10-10")
    .set_metadata("tags", ["main", "simple", "greeting"])
    .set_metadata("complexity", "low")
    
    .build()
    )


# Export the flow
flow = create_flow()
