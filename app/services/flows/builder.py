"""
Conversation Flow Builder
Professional DSL-based system for creating conversational flows
"""
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class FlowStepType(Enum):
    """Types of flow steps"""
    MESSAGE = "message"
    QUESTION = "question"
    CHOICE = "choice"
    INPUT = "input"
    CONDITION = "condition"
    ACTION = "action"
    WAIT = "wait"
    END = "end"


class MessageType(Enum):
    """Types of WhatsApp messages"""
    TEXT = "text"
    BUTTONS = "buttons"
    LIST = "list"
    MEDIA = "media"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    TEMPLATE = "template"


@dataclass
class FlowStep:
    """Represents a step in the conversation flow"""
    id: str
    type: FlowStepType
    name: str
    message: Optional[str] = None
    message_type: MessageType = MessageType.TEXT
    options: List[Dict[str, str]] = field(default_factory=list)
    validation: Optional[Dict[str, Any]] = None
    next_step: Optional[str] = None
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowDefinition:
    """Represents a complete conversation flow"""
    id: str
    name: str
    description: str
    start_step: str
    steps: Dict[str, FlowStep] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    error_handling: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FlowBuilder:
    """Builder class for creating conversation flows"""
    
    def __init__(self, flow_id: str, name: str, description: str = ""):
        self.flow_id = flow_id
        self.name = name
        self.description = description
        self.steps: Dict[str, FlowStep] = {}
        self.start_step: Optional[str] = None
        self.variables: Dict[str, Any] = {}
        self.error_handling: Dict[str, str] = {}
        self.metadata: Dict[str, Any] = {}
    
    def start_with(self, step_id: str) -> 'FlowBuilder':
        """Set the starting step"""
        self.start_step = step_id
        return self
    
    def add_step(self, step: FlowStep) -> 'FlowBuilder':
        """Add a step to the flow"""
        self.steps[step.id] = step
        return self
    
    def add_message_step(self, step_id: str, name: str, message: str, 
                        message_type: MessageType = MessageType.TEXT,
                        next_step: Optional[str] = None) -> 'FlowBuilder':
        """Add a message step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.MESSAGE,
            name=name,
            message=message,
            message_type=message_type,
            next_step=next_step
        )
        return self.add_step(step)
    
    def add_question_step(self, step_id: str, name: str, question: str,
                         validation: Optional[Dict[str, Any]] = None,
                         next_step: Optional[str] = None) -> 'FlowBuilder':
        """Add a question step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.QUESTION,
            name=name,
            message=question,
            validation=validation,
            next_step=next_step
        )
        return self.add_step(step)
    
    def add_choice_step(self, step_id: str, name: str, message: str,
                       options: List[Dict[str, str]],
                       next_step: Optional[str] = None,
                       conditions: Optional[List[Dict[str, Any]]] = None) -> 'FlowBuilder':
        """Add a choice step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.CHOICE,
            name=name,
            message=message,
            message_type=MessageType.BUTTONS,
            options=options,
            next_step=next_step,
            conditions=conditions or []
        )
        return self.add_step(step)
    
    def add_list_step(self, step_id: str, name: str, message: str,
                     options: List[Dict[str, str]],
                     button_text: str = "Ver opciones",
                     next_step: Optional[str] = None,
                     conditions: Optional[List[Dict[str, Any]]] = None) -> 'FlowBuilder':
        """Add a list step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.CHOICE,
            name=name,
            message=message,
            message_type=MessageType.LIST,
            options=options,
            metadata={"button_text": button_text},
            next_step=next_step,
            conditions=conditions or []
        )
        return self.add_step(step)
    
    def add_condition_step(self, step_id: str, name: str,
                          conditions: List[Dict[str, Any]]) -> 'FlowBuilder':
        """Add a condition step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.CONDITION,
            name=name,
            conditions=conditions
        )
        return self.add_step(step)
    
    def add_action_step(self, step_id: str, name: str, actions: List[str],
                       next_step: Optional[str] = None) -> 'FlowBuilder':
        """Add an action step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.ACTION,
            name=name,
            actions=actions,
            next_step=next_step
        )
        return self.add_step(step)
    
    def add_wait_step(self, step_id: str, name: str, timeout: int = 300) -> 'FlowBuilder':
        """Add a wait step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.WAIT,
            name=name,
            timeout=timeout
        )
        return self.add_step(step)
    
    def add_end_step(self, step_id: str, name: str, message: str = "Conversación finalizada") -> 'FlowBuilder':
        """Add an end step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.END,
            name=name,
            message=message
        )
        return self.add_step(step)
    
    def set_variable(self, key: str, value: Any) -> 'FlowBuilder':
        """Set a flow variable"""
        self.variables[key] = value
        return self
    
    def set_error_handler(self, error_type: str, handler_step: str) -> 'FlowBuilder':
        """Set error handler"""
        self.error_handling[error_type] = handler_step
        return self
    
    def set_metadata(self, key: str, value: Any) -> 'FlowBuilder':
        """Set flow metadata"""
        self.metadata[key] = value
        return self
    
    def build(self) -> FlowDefinition:
        """Build the flow definition"""
        if not self.start_step:
            raise ValueError("Flow must have a start step")
        
        return FlowDefinition(
            id=self.flow_id,
            name=self.name,
            description=self.description,
            start_step=self.start_step,
            steps=self.steps,
            variables=self.variables,
            error_handling=self.error_handling,
            metadata=self.metadata
        )


class FlowExecutor:
    """Executes conversation flows"""
    
    def __init__(self, whatsapp_service, persistence_service):
        self.whatsapp_service = whatsapp_service
        self.persistence_service = persistence_service
        self.active_flows: Dict[str, FlowDefinition] = {}
        self.conversation_states: Dict[str, Dict[str, Any]] = {}
    
    def register_flow(self, flow: FlowDefinition):
        """Register a flow for execution"""
        self.active_flows[flow.id] = flow
        logger.info(f"Flow registered: {flow.id} - {flow.name}")
    
    def start_conversation(self, phone_number: str, flow_id: str, 
                          initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start a conversation with a specific flow"""
        if flow_id not in self.active_flows:
            raise ValueError(f"Flow {flow_id} not found")
        
        flow = self.active_flows[flow_id]
        conversation_id = f"{phone_number}_{flow_id}_{datetime.now().timestamp()}"
        
        # Initialize conversation state
        self.conversation_states[conversation_id] = {
            "phone_number": phone_number,
            "flow_id": flow_id,
            "current_step": flow.start_step,
            "variables": flow.variables.copy(),
            "data": initial_data or {},
            "started_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        # Execute first step
        return self.execute_step(conversation_id)
    
    def execute_step(self, conversation_id: str, user_input: str = None) -> Dict[str, Any]:
        """Execute current step in conversation"""
        if conversation_id not in self.conversation_states:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        state = self.conversation_states[conversation_id]
        flow = self.active_flows[state["flow_id"]]
        current_step_id = state["current_step"]
        
        if current_step_id not in flow.steps:
            raise ValueError(f"Step {current_step_id} not found in flow {flow.id}")
        
        current_step = flow.steps[current_step_id]
        
        try:
            # Execute step based on type
            result = self._execute_step_by_type(conversation_id, current_step, user_input)
            
            # Update conversation state
            state["last_activity"] = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing step {current_step_id}: {e}")
            return self._handle_error(conversation_id, e)
    
    def _execute_step_by_type(self, conversation_id: str, step: FlowStep, 
                             user_input: str = None) -> Dict[str, Any]:
        """Execute step based on its type"""
        state = self.conversation_states[conversation_id]
        phone_number = state["phone_number"]
        
        if step.type == FlowStepType.MESSAGE:
            return self._execute_message_step(conversation_id, step)
        
        elif step.type == FlowStepType.QUESTION:
            return self._execute_question_step(phone_number, step, user_input)
        
        elif step.type == FlowStepType.CHOICE:
            return self._execute_choice_step(phone_number, step, user_input)
        
        elif step.type == FlowStepType.CONDITION:
            return self._execute_condition_step(conversation_id, step)
        
        elif step.type == FlowStepType.ACTION:
            return self._execute_action_step(conversation_id, step)
        
        elif step.type == FlowStepType.WAIT:
            return self._execute_wait_step(conversation_id, step)
        
        elif step.type == FlowStepType.END:
            return self._execute_end_step(phone_number, step)
        
        else:
            raise ValueError(f"Unknown step type: {step.type}")
    
    def _execute_message_step(self, conversation_id: str, step: FlowStep) -> Dict[str, Any]:
        """Execute a message step"""
        state = self.conversation_states[conversation_id]
        phone_number = state["phone_number"]
        
        # Process template variables
        message = self._process_template(step.message, state["variables"])
        
        # Send message using WhatsApp service
        if step.message_type == MessageType.TEXT:
            result = self.whatsapp_service.message_sender.send_text(phone_number, message)
        elif step.message_type == MessageType.BUTTONS:
            buttons = [{"id": opt["id"], "title": opt["title"]} for opt in step.options]
            result = self.whatsapp_service.message_sender.send_buttons(phone_number, message, buttons)
        elif step.message_type == MessageType.LIST:
            sections = [{"title": "Opciones", "rows": step.options}]
            button_text = step.metadata.get("button_text", "Ver opciones")
            result = self.whatsapp_service.message_sender.send_list(phone_number, message, button_text, sections)
        else:
            result = self.whatsapp_service.message_sender.send_text(phone_number, message)
        
        # Move to next step if defined
        if step.next_step:
            state["current_step"] = step.next_step
        
        return {
            "success": True,
            "step_id": step.id,
            "step_type": step.type.value,
            "next_step": step.next_step,
            "whatsapp_result": result
        }
    
    def _process_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Process template variables in message"""
        import re
        logger.info(f"Processing template: '{template}' with variables: {variables}")
        processed_message = template
        for key, value in variables.items():
            placeholder = r"{{" + re.escape(key) + r"}}"
            processed_message = re.sub(placeholder, str(value), processed_message)
        logger.info(f"Processed message: '{processed_message}'")
        return processed_message
    
    def _execute_question_step(self, phone_number: str, step: FlowStep, 
                              user_input: str = None) -> Dict[str, Any]:
        """Execute a question step"""
        if user_input is None:
            # Send question and wait for response
            result = self.whatsapp_service.message_sender.send_text(phone_number, step.message)
            return {
                "success": True,
                "step_id": step.id,
                "step_type": step.type.value,
                "waiting_for_input": True,
                "whatsapp_result": result
            }
        else:
            # Validate input if validation rules exist
            if step.validation:
                validation_result = self._validate_input(user_input, step.validation)
                if not validation_result["valid"]:
                    error_message = validation_result.get("error_message", "Entrada inválida")
                    self.whatsapp_service.message_sender.send_text(phone_number, error_message)
                    return {
                        "success": False,
                        "step_id": step.id,
                        "error": "validation_failed",
                        "error_message": error_message
                    }
            
            # Store user input
            self.conversation_states[phone_number]["data"][step.id] = user_input
            
            # Move to next step
            if step.next_step:
                self.conversation_states[phone_number]["current_step"] = step.next_step
            
            return {
                "success": True,
                "step_id": step.id,
                "step_type": step.type.value,
                "next_step": step.next_step,
                "user_input": user_input
            }
    
    def _execute_choice_step(self, phone_number: str, step: FlowStep, 
                            user_input: str = None) -> Dict[str, Any]:
        """Execute a choice step"""
        if user_input is None:
            # Send choice options
            if step.message_type == MessageType.BUTTONS:
                buttons = [{"id": opt["id"], "title": opt["title"]} for opt in step.options]
                result = self.whatsapp_service.message_sender.send_buttons(phone_number, step.message, buttons)
            elif step.message_type == MessageType.LIST:
                sections = [{"title": "Opciones", "rows": step.options}]
                button_text = step.metadata.get("button_text", "Ver opciones")
                result = self.whatsapp_service.message_sender.send_list(phone_number, step.message, button_text, sections)
            else:
                result = self.whatsapp_service.message_sender.send_text(phone_number, step.message)
            
            return {
                "success": True,
                "step_id": step.id,
                "step_type": step.type.value,
                "waiting_for_input": True,
                "whatsapp_result": result
            }
        else:
            # Process user choice
            choice = self._find_choice_by_input(user_input, step.options)
            if not choice:
                error_message = "Opción no válida. Por favor, selecciona una de las opciones disponibles."
                self.whatsapp_service.message_sender.send_text(phone_number, error_message)
                return {
                    "success": False,
                    "step_id": step.id,
                    "error": "invalid_choice",
                    "error_message": error_message
                }
            
            # Store choice
            self.conversation_states[phone_number]["data"][step.id] = choice
            
            # Move to next step
            if step.next_step:
                self.conversation_states[phone_number]["current_step"] = step.next_step
            
            return {
                "success": True,
                "step_id": step.id,
                "step_type": step.type.value,
                "next_step": step.next_step,
                "user_choice": choice
            }
    
    def _execute_condition_step(self, conversation_id: str, step: FlowStep) -> Dict[str, Any]:
        """Execute a condition step"""
        state = self.conversation_states[conversation_id]
        
        for condition in step.conditions:
            if self._evaluate_condition(condition, state):
                next_step = condition.get("next_step")
                if next_step:
                    state["current_step"] = next_step
                return {
                    "success": True,
                    "step_id": step.id,
                    "step_type": step.type.value,
                    "condition_matched": condition,
                    "next_step": next_step
                }
        
        # No condition matched, use default next step
        if step.next_step:
            state["current_step"] = step.next_step
        
        return {
            "success": True,
            "step_id": step.id,
            "step_type": step.type.value,
            "next_step": step.next_step
        }
    
    def _execute_action_step(self, conversation_id: str, step: FlowStep) -> Dict[str, Any]:
        """Execute an action step"""
        state = self.conversation_states[conversation_id]
        
        # Execute actions
        for action in step.actions:
            self._execute_action(action, state)
        
        # Move to next step
        if step.next_step:
            state["current_step"] = step.next_step
        
        return {
            "success": True,
            "step_id": step.id,
            "step_type": step.type.value,
            "next_step": step.next_step,
            "actions_executed": step.actions
        }
    
    def _execute_wait_step(self, conversation_id: str, step: FlowStep) -> Dict[str, Any]:
        """Execute a wait step"""
        # Set timeout
        state = self.conversation_states[conversation_id]
        state["timeout"] = step.timeout
        state["wait_started"] = datetime.now()
        
        return {
            "success": True,
            "step_id": step.id,
            "step_type": step.type.value,
            "waiting": True,
            "timeout": step.timeout
        }
    
    def _execute_end_step(self, phone_number: str, step: FlowStep) -> Dict[str, Any]:
        """Execute an end step"""
        if step.message:
            self.whatsapp_service.message_sender.send_text(phone_number, step.message)
        
        return {
            "success": True,
            "step_id": step.id,
            "step_type": step.type.value,
            "conversation_ended": True,
            "final_message": step.message
        }
    
    def _validate_input(self, user_input: str, validation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user input based on validation rules"""
        # Implement validation logic here
        # This is a placeholder - you can implement specific validation rules
        return {"valid": True}
    
    def _find_choice_by_input(self, user_input: str, options: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Find choice option by user input"""
        user_input_lower = user_input.lower().strip()
        
        for option in options:
            if (option.get("id", "").lower() == user_input_lower or 
                option.get("title", "").lower() == user_input_lower):
                return option
        
        return None
    
    def _evaluate_condition(self, condition: Dict[str, Any], state: Dict[str, Any]) -> bool:
        """Evaluate a condition"""
        # Implement condition evaluation logic here
        # This is a placeholder - you can implement specific condition logic
        return True
    
    def _execute_action(self, action: str, state: Dict[str, Any]):
        """Execute an action"""
        # Implement action execution logic here
        # This is a placeholder - you can implement specific actions
        pass
    
    def _handle_error(self, conversation_id: str, error: Exception) -> Dict[str, Any]:
        """Handle errors in conversation flow"""
        state = self.conversation_states[conversation_id]
        flow = self.active_flows[state["flow_id"]]
        
        # Check for error handler
        error_type = type(error).__name__
        if error_type in flow.error_handling:
            handler_step = flow.error_handling[error_type]
            state["current_step"] = handler_step
            return self.execute_step(conversation_id)
        
        # Default error handling
        return {
            "success": False,
            "error": str(error),
            "error_type": error_type
        }


# Factory functions
def create_flow_builder(flow_id: str, name: str, description: str = "") -> FlowBuilder:
    """Create a new flow builder"""
    return FlowBuilder(flow_id, name, description)


def create_flow_executor(whatsapp_service, persistence_service) -> FlowExecutor:
    """Create a new flow executor"""
    return FlowExecutor(whatsapp_service, persistence_service)
