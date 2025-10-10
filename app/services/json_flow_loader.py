"""
JSON Flow Configuration
Define conversation flows using JSON configuration files
"""
import json
from typing import Dict, Any, List
from pathlib import Path
from app.services.conversation_flow_builder import (
    create_flow_builder, FlowStepType, MessageType
)


class JSONFlowLoader:
    """Load conversation flows from JSON configuration files"""
    
    def __init__(self, flows_directory: str = "app/flows"):
        self.flows_directory = Path(flows_directory)
        self.loaded_flows: Dict[str, Any] = {}
    
    def load_flow_from_json(self, flow_file: str):
        """Load a flow from JSON file"""
        flow_path = self.flows_directory / f"{flow_file}.json"
        
        if not flow_path.exists():
            raise FileNotFoundError(f"Flow file {flow_path} not found")
        
        with open(flow_path, 'r', encoding='utf-8') as file:
            flow_config = json.load(file)
        
        return self._build_flow_from_config(flow_config)
    
    def load_all_flows(self):
        """Load all flows from the flows directory"""
        if not self.flows_directory.exists():
            return {}
        
        flows = {}
        for flow_file in self.flows_directory.glob("*.json"):
            flow_name = flow_file.stem
            try:
                flows[flow_name] = self.load_flow_from_json(flow_name)
            except Exception as e:
                print(f"Error loading flow {flow_name}: {e}")
        
        return flows
    
    def _build_flow_from_config(self, config: Dict[str, Any]):
        """Build a flow from configuration"""
        flow_id = config["id"]
        name = config["name"]
        description = config.get("description", "")
        
        builder = create_flow_builder(flow_id, name, description)
        
        # Set start step
        if "start_step" in config:
            builder.start_with(config["start_step"])
        
        # Add steps
        for step_config in config.get("steps", []):
            self._add_step_to_builder(builder, step_config)
        
        # Set variables
        for key, value in config.get("variables", {}).items():
            builder.set_variable(key, value)
        
        # Set error handlers
        for error_type, handler_step in config.get("error_handling", {}).items():
            builder.set_error_handler(error_type, handler_step)
        
        # Set metadata
        for key, value in config.get("metadata", {}).items():
            builder.set_metadata(key, value)
        
        return builder.build()
    
    def _add_step_to_builder(self, builder, step_config: Dict[str, Any]):
        """Add a step to the builder based on configuration"""
        step_id = step_config["id"]
        step_type = step_config["type"]
        name = step_config["name"]
        
        if step_type == "message":
            message = step_config["message"]
            message_type = MessageType(step_config.get("message_type", "text"))
            next_step = step_config.get("next_step")
            
            builder.add_message_step(step_id, name, message, message_type, next_step)
        
        elif step_type == "question":
            question = step_config["question"]
            validation = step_config.get("validation")
            next_step = step_config.get("next_step")
            
            builder.add_question_step(step_id, name, question, validation, next_step)
        
        elif step_type == "choice":
            message = step_config["message"]
            options = step_config["options"]
            choice_type = step_config.get("choice_type", "buttons")
            next_step = step_config.get("next_step")
            
            if choice_type == "buttons":
                builder.add_choice_step(step_id, name, message, options, next_step)
            elif choice_type == "list":
                button_text = step_config.get("button_text", "Ver opciones")
                builder.add_list_step(step_id, name, message, options, button_text, next_step)
        
        elif step_type == "condition":
            conditions = step_config["conditions"]
            builder.add_condition_step(step_id, name, conditions)
        
        elif step_type == "action":
            actions = step_config["actions"]
            next_step = step_config.get("next_step")
            builder.add_action_step(step_id, name, actions, next_step)
        
        elif step_type == "wait":
            timeout = step_config.get("timeout", 300)
            builder.add_wait_step(step_id, name, timeout)
        
        elif step_type == "end":
            message = step_config.get("message", "Conversación finalizada")
            builder.add_end_step(step_id, name, message)


# Example JSON configuration
EXAMPLE_FLOW_JSON = {
    "id": "welcome",
    "name": "Welcome Flow",
    "description": "Simple welcome conversation",
    "start_step": "welcome_message",
    "variables": {
        "company_name": "Mi Empresa",
        "support_hours": "9:00 - 18:00"
    },
    "error_handling": {
        "validation_failed": "show_error",
        "timeout": "show_timeout"
    },
    "steps": [
        {
            "id": "welcome_message",
            "type": "message",
            "name": "Welcome Message",
            "message": "¡Hola! 👋 Bienvenido a {{company_name}}. ¿En qué puedo ayudarte hoy?",
            "message_type": "text",
            "next_step": "main_menu"
        },
        {
            "id": "main_menu",
            "type": "choice",
            "name": "Main Menu",
            "message": "Selecciona una opción:",
            "choice_type": "buttons",
            "options": [
                {
                    "id": "products",
                    "title": "Ver Productos"
                },
                {
                    "id": "services",
                    "title": "Servicios"
                },
                {
                    "id": "contact",
                    "title": "Contacto"
                },
                {
                    "id": "help",
                    "title": "Ayuda"
                }
            ],
            "next_step": "process_choice"
        },
        {
            "id": "process_choice",
            "type": "condition",
            "name": "Process Choice",
            "conditions": [
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
        },
        {
            "id": "show_products",
            "type": "message",
            "name": "Show Products",
            "message": "Aquí tienes nuestros productos disponibles...",
            "next_step": "end"
        },
        {
            "id": "show_services",
            "type": "message",
            "name": "Show Services",
            "message": "Estos son nuestros servicios...",
            "next_step": "end"
        },
        {
            "id": "show_contact",
            "type": "message",
            "name": "Show Contact",
            "message": "📞 Información de contacto:\nTeléfono: +1234567890\nEmail: contacto@empresa.com\nHorario: {{support_hours}}",
            "next_step": "end"
        },
        {
            "id": "show_help",
            "type": "message",
            "name": "Show Help",
            "message": "¿Necesitas ayuda? Puedes contactarnos directamente.",
            "next_step": "end"
        },
        {
            "id": "show_error",
            "type": "message",
            "name": "Show Error",
            "message": "Lo siento, hubo un error. Por favor, intenta nuevamente.",
            "next_step": "main_menu"
        },
        {
            "id": "show_timeout",
            "type": "message",
            "name": "Show Timeout",
            "message": "La conversación ha expirado. ¿Te gustaría empezar de nuevo?",
            "next_step": "welcome_message"
        },
        {
            "id": "end",
            "type": "end",
            "name": "End",
            "message": "¡Gracias por contactarnos! 😊"
        }
    ],
    "metadata": {
        "version": "1.0",
        "author": "Template Creator",
        "last_updated": "2024-01-01"
    }
}


def create_example_flow_file():
    """Create an example flow JSON file"""
    flows_dir = Path("app/flows")
    flows_dir.mkdir(exist_ok=True)
    
    example_file = flows_dir / "welcome.json"
    with open(example_file, 'w', encoding='utf-8') as file:
        json.dump(EXAMPLE_FLOW_JSON, file, indent=2, ensure_ascii=False)
    
    print(f"Example flow file created: {example_file}")


# Factory function
def create_json_flow_loader(flows_directory: str = "app/flows") -> JSONFlowLoader:
    """Create a JSON flow loader"""
    return JSONFlowLoader(flows_directory)
