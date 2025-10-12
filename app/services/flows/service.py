"""
WhatsApp Flow Service
Service for managing WhatsApp conversation flows using active flow configuration
"""
import logging
from app.services.flows.builder import create_flow_executor
from app.services.flows.loader import create_unified_flow_loader
from app.services.flows.active_flow_manager import active_flow_manager

logger = logging.getLogger(__name__)


class WhatsAppFlowService:
    """Service for managing WhatsApp conversation flows"""
    
    def __init__(self, whatsapp_service, persistence_service):
        self.whatsapp_service = whatsapp_service
        self.persistence_service = persistence_service
        self.flow_executor = create_flow_executor(whatsapp_service, persistence_service)
        self.unified_loader = create_unified_flow_loader("app/flows")
        
        # Load flows from JSON and YAML files
        self._load_config_flows()
    
    def _load_config_flows(self):
        """Load flows from JSON and YAML files"""
        try:
            config_flows = self.unified_loader.load_all_flows()
            for flow_id, flow in config_flows.items():
                self.flow_executor.register_flow(flow)
                logger.info(f"SUCCESS: Config flow loaded: {flow_id}")
        except Exception as e:
            logger.error(f"ERROR: Error loading config flows: {e}")
    
    def get_active_flow_id(self) -> str:
        """Get the currently active flow ID"""
        active_flow = active_flow_manager.get_active_flow()
        if active_flow and active_flow in self.flow_executor.active_flows:
            return active_flow
        
        # Fallback to main if active flow not found
        if "main" in self.flow_executor.active_flows:
            logger.warning(f"Active flow '{active_flow}' not found, using 'main'")
            return "main"
        
        # If no flows available, return the first one
        if self.flow_executor.active_flows:
            first_flow = list(self.flow_executor.active_flows.keys())[0]
            logger.warning(f"No 'main' flow found, using '{first_flow}'")
            return first_flow
        
        raise ValueError("No flows available")
    
    def start_conversation(self, phone_number: str, flow_id: str = None, 
                          initial_data: dict = None) -> dict:
        """Start a conversation with a specific flow or active flow"""
        try:
            # Use provided flow_id or active flow
            if flow_id is None:
                flow_id = self.get_active_flow_id()
            
            result = self.flow_executor.start_conversation(
                phone_number=phone_number,
                flow_id=flow_id,
                initial_data=initial_data or {}
            )
            
            # Log conversation start
            logger.info(f"SUCCESS: Conversation started: {phone_number} -> {flow_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"ERROR: Error starting conversation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_message(self, phone_number: str, message_content: str) -> dict:
        """Process incoming message using active flow"""
        try:
            logger.info(f"Processing message from {phone_number}: '{message_content}'")
            
            # Find active conversation
            conversation_id = self._find_conversation(phone_number)
            
            if not conversation_id:
                # Start conversation with active flow
                active_flow_id = self.get_active_flow_id()
                logger.info(f"Starting new conversation for {phone_number} with flow {active_flow_id}")
                return self.start_conversation(phone_number, active_flow_id)
            
            # Process message in existing conversation
            logger.info(f"Processing message in existing conversation {conversation_id}")
            result = self.flow_executor.execute_step(
                conversation_id=conversation_id,
                user_input=message_content
            )
            
            # Log message processing
            logger.info(f"SUCCESS: Message processed: {phone_number} -> {message_content}")
            
            return result
            
        except Exception as e:
            logger.error(f"ERROR: Error processing message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_conversation(self, phone_number: str) -> str:
        """Find active conversation for phone number"""
        try:
            # Query database for active conversation
            conversation_id = f"{phone_number}_flow_conversation"
            
            # Check if conversation exists in database
            if self.persistence_service:
                # Try to find existing conversation
                # For now, we'll use a simple approach
                # In a real implementation, you'd query the database
                return conversation_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding conversation for {phone_number}: {e}")
            return None
    
    def get_available_flows(self) -> list:
        """Get list of available flows"""
        return list(self.flow_executor.active_flows.keys())
    
    def get_flow_info(self, flow_id: str) -> dict:
        """Get information about a specific flow"""
        if flow_id not in self.flow_executor.active_flows:
            return {"error": "Flow not found"}
        
        flow = self.flow_executor.active_flows[flow_id]
        return {
            "id": flow.id,
            "name": flow.name,
            "description": flow.description,
            "start_step": flow.start_step,
            "steps_count": len(flow.steps),
            "variables": flow.variables,
            "error_handlers": flow.error_handling
        }
    
    def get_active_flow_info(self) -> dict:
        """Get information about the active flow"""
        try:
            active_flow_id = self.get_active_flow_id()
            return self.get_flow_info(active_flow_id)
        except Exception as e:
            return {"error": str(e)}
