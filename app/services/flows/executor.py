"""
Flow Executor
Handles the execution of conversation flows
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.flows.builder import FlowDefinition, FlowStep, FlowStepType

logger = logging.getLogger(__name__)


class FlowExecutor:
    """Executes conversation flows and manages conversation state"""
    
    def __init__(self, whatsapp_service, persistence_service):
        self.whatsapp_service = whatsapp_service
        self.persistence_service = persistence_service
        self.active_flows: Dict[str, FlowDefinition] = {}
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
    
    def register_flow(self, flow: FlowDefinition):
        """Register a flow for execution"""
        self.active_flows[flow.id] = flow
        logger.info(f"Flow registered: {flow.id} - {flow.name}")
    
    async def start_conversation(self, phone_number: str, flow_id: str, initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start a new conversation with a flow"""
        try:
            if flow_id not in self.active_flows:
                return {
                    "success": False,
                    "error": f"Flow {flow_id} not found"
                }
            
            flow = self.active_flows[flow_id]
            conversation_id = f"{phone_number}_flow_conversation"
            
            # Initialize conversation state
            conversation_state = {
                "conversation_id": conversation_id,
                "phone_number": phone_number,
                "flow_id": flow_id,
                "current_step": flow.start_step,
                "step_history": [],
                "user_data": initial_data or {},
                "variables": flow.variables.copy(),
                "started_at": datetime.now(),
                "last_activity": datetime.now()
            }
            
            self.active_conversations[conversation_id] = conversation_state
            
            # Execute the first step
            result = await self._execute_step(conversation_id, None)
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "flow_id": flow_id,
                "current_step": flow.start_step,
                "whatsapp_result": result.get("whatsapp_result"),
                "message": result.get("message", "Conversation started"),
                "conversation_state": "active",
                "next_step_result": result.get("next_step_result"),
                "next_step_error": result.get("next_step_error")
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_step(self, conversation_id: str, user_input: str = None) -> Dict[str, Any]:
        """Execute the current step in a conversation"""
        try:
            if conversation_id not in self.active_conversations:
                return {
                    "success": False,
                    "error": f"Conversation {conversation_id} not found"
                }
            
            return await self._execute_step(conversation_id, user_input)
            
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_step(self, conversation_id: str, user_input: str = None) -> Dict[str, Any]:
        """Internal method to execute a step"""
        conversation = self.active_conversations[conversation_id]
        flow = self.active_flows[conversation["flow_id"]]
        current_step_id = conversation["current_step"]
        
        if current_step_id not in flow.steps:
            return {
                "success": False,
                "error": f"Step {current_step_id} not found in flow {flow.id}"
            }
        
        step = flow.steps[current_step_id]
        conversation["last_activity"] = datetime.now()
        
        # Add step to history
        conversation["step_history"].append({
            "step_id": current_step_id,
            "timestamp": datetime.now(),
            "user_input": user_input
        })
        
        # Execute step based on type
        if step.type == FlowStepType.MESSAGE:
            return await self._execute_message_step(conversation, step)
        elif step.type == FlowStepType.QUESTION:
            return await self._execute_question_step(conversation, step)
        elif step.type == FlowStepType.CHOICE:
            return await self._execute_choice_step(conversation, step, user_input)
        elif step.type == FlowStepType.CONDITION:
            return await self._execute_condition_step(conversation, step, user_input)
        elif step.type == FlowStepType.END:
            return await self._execute_end_step(conversation, step)
        else:
            return {
                "success": False,
                "error": f"Unsupported step type: {step.type}"
            }
    
    async def _execute_message_step(self, conversation: Dict[str, Any], step: FlowStep) -> Dict[str, Any]:
        """Execute a message step"""
        try:
            # Process message template with variables
            message = self._process_template(step.message, conversation["variables"])
            
            # Send message via WhatsApp
            send_result = await self.whatsapp_service.send_message(
                to=conversation["phone_number"],
                message=message
            )
            
            # Move to next step and execute it automatically
            if step.next_step:
                conversation["current_step"] = step.next_step
                logger.info(f"Moving to next step: {step.next_step}")
                # Execute the next step automatically
                try:
                    next_result = await self._execute_step(conversation["conversation_id"], None)
                    logger.info(f"Next step executed successfully: {next_result}")
                    return {
                        "success": True,
                        "message": message,
                        "whatsapp_result": send_result,
                        "next_step": step.next_step,
                        "next_step_result": next_result
                    }
                except Exception as e:
                    logger.error(f"Error executing next step {step.next_step}: {e}")
                    return {
                        "success": True,
                        "message": message,
                        "whatsapp_result": send_result,
                        "next_step": step.next_step,
                        "next_step_error": str(e)
                    }
            else:
                conversation["current_step"] = "end"
                return {
                    "success": True,
                    "message": message,
                    "whatsapp_result": send_result,
                    "next_step": "end"
                }
            
        except Exception as e:
            logger.error(f"Error executing message step: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_question_step(self, conversation: Dict[str, Any], step: FlowStep) -> Dict[str, Any]:
        """Execute a question step"""
        try:
            # Process question template
            question = self._process_template(step.question, conversation["variables"])
            
            # Send question via WhatsApp
            send_result = await self.whatsapp_service.send_message(
                to=conversation["phone_number"],
                message=question
            )
            
            # Stay on same step to wait for user input
            return {
                "success": True,
                "message": question,
                "whatsapp_result": send_result,
                "waiting_for_input": True,
                "current_step": conversation["current_step"]
            }
            
        except Exception as e:
            logger.error(f"Error executing question step: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_choice_step(self, conversation: Dict[str, Any], step: FlowStep, user_input: str = None) -> Dict[str, Any]:
        """Execute a choice step"""
        try:
            logger.info(f"Executing choice step with user_input: '{user_input}'")
            logger.info(f"Step conditions: {step.conditions}")
            
            # If user input is provided, process conditions
            if user_input:
                logger.info(f"Processing conditions for user input: '{user_input}'")
                # Process conditions to determine next step
                for condition in step.conditions:
                    logger.info(f"Checking condition: {condition}")
                    if self._evaluate_condition(condition["condition"], conversation, user_input):
                        logger.info(f"Condition matched: {condition['condition']} -> {condition['next_step']}")
                        conversation["current_step"] = condition["next_step"]
                        # Execute the next step
                        return await self._execute_step(conversation["conversation_id"], None)
                
                # No condition matched, stay on same step
                logger.info("No condition matched, staying on same step")
                
                # Send error message to user
                error_message = "Opción no válida. Por favor selecciona una opción válida."
                await self.whatsapp_service.send_message(
                    to=conversation["phone_number"],
                    message=error_message
                )
                
                return {
                    "success": True,
                    "message": error_message,
                    "waiting_for_input": True,
                    "current_step": conversation["current_step"]
                }
            
            # No user input, send interactive buttons
            logger.info("No user input, sending interactive buttons")
            message = self._process_template(step.message, conversation["variables"])
            
            # Validate message length for WhatsApp interactive messages
            if len(message) > 60:
                logger.warning(f"Message too long for WhatsApp interactive header: {len(message)} chars (max 60)")
                logger.warning(f"Message content: {message}")
                # Truncate message to fit WhatsApp limits
                message = message[:57] + "..."
                logger.info(f"Truncated message to: {message}")
            
            # Create interactive buttons
            buttons = []
            for option in step.options:
                buttons.append({
                    "id": option["id"],
                    "title": option["title"]
                })
            
            # Send interactive message
            send_result = await self.whatsapp_service.send_interactive_message(
                to=conversation["phone_number"],
                header_text=message,
                body_text="Selecciona una opción:",
                buttons=buttons
            )
            
            # Stay on same step to wait for user choice
            return {
                "success": True,
                "message": message,
                "whatsapp_result": send_result,
                "waiting_for_input": True,
                "current_step": conversation["current_step"]
            }
            
        except Exception as e:
            logger.error(f"Error executing choice step: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_condition_step(self, conversation: Dict[str, Any], step: FlowStep, user_input: str) -> Dict[str, Any]:
        """Execute a condition step"""
        try:
            # Evaluate conditions
            for condition in step.conditions:
                if self._evaluate_condition(condition["condition"], conversation, user_input):
                    conversation["current_step"] = condition["next_step"]
                    return await self._execute_step(conversation["conversation_id"], user_input)
            
            # No condition matched, use default next step
            if step.next_step:
                conversation["current_step"] = step.next_step
                return await self._execute_step(conversation["conversation_id"], user_input)
            else:
                return {
                    "success": False,
                    "error": "No condition matched and no default next step"
                }
                
        except Exception as e:
            logger.error(f"Error executing condition step: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_end_step(self, conversation: Dict[str, Any], step: FlowStep) -> Dict[str, Any]:
        """Execute an end step"""
        try:
            # Process end message template
            message = self._process_template(step.message, conversation["variables"])
            
            # Send final message
            send_result = await self.whatsapp_service.send_message(
                to=conversation["phone_number"],
                message=message
            )
            
            # Mark conversation as ended
            conversation["current_step"] = "ended"
            conversation["ended_at"] = datetime.now()
            
            return {
                "success": True,
                "message": message,
                "whatsapp_result": send_result,
                "conversation_state": "ended"
            }
            
        except Exception as e:
            logger.error(f"Error executing end step: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Process template with variables"""
        try:
            result = template
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                result = result.replace(placeholder, str(value))
            return result
        except Exception as e:
            logger.error(f"Error processing template: {e}")
            return template
    
    def _evaluate_condition(self, condition: str, conversation: Dict[str, Any], user_input: str) -> bool:
        """Evaluate a condition string"""
        try:
            logger.info(f"Evaluating condition: '{condition}' with user_input: '{user_input}'")
            
            # Simple condition evaluation
            if "is_first_message" in condition:
                return len(conversation["step_history"]) == 1
            
            # Handle user choice conditions
            if "user_choice" in condition:
                # Extract the expected value from condition like "user_choice == 'help'"
                if "==" in condition:
                    expected_value = condition.split("==")[1].strip().strip("'\"")
                    result = user_input.lower().strip() == expected_value.lower().strip()
                    logger.info(f"Condition '{condition}' evaluated to: {result} (expected: '{expected_value}', got: '{user_input}')")
                    return result
            
            # Handle other conditions as needed
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False


def create_flow_executor(whatsapp_service, persistence_service) -> FlowExecutor:
    """Create a new FlowExecutor instance"""
    return FlowExecutor(whatsapp_service, persistence_service)