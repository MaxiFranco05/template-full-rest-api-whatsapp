"""
WhatsApp Flow Service
Service for managing WhatsApp conversation flows using main.json as primary flow
"""
from app.services.flows.builder import create_flow_executor
from app.services.flows.loader import create_unified_flow_loader


class WhatsAppFlowService:
    """Service for managing WhatsApp conversation flows"""
    
    def __init__(self, whatsapp_service, persistence_service):
        self.whatsapp_service = whatsapp_service
        self.persistence_service = persistence_service
        self.flow_executor = create_flow_executor(whatsapp_service, persistence_service)
        self.unified_loader = create_unified_flow_loader("app/flows")
        
        # Load flows from JSON and YAML files (main.json is primary)
        self._load_config_flows()
    
    def _load_config_flows(self):
        """Load flows from JSON and YAML files"""
        try:
            config_flows = self.unified_loader.load_all_flows()
            for flow_id, flow in config_flows.items():
                self.flow_executor.register_flow(flow)
                print(f"SUCCESS: Config flow loaded: {flow_id}")
        except Exception as e:
            print(f"ERROR: Error loading config flows: {e}")
    
    def start_conversation(self, phone_number: str, flow_id: str, 
                          initial_data: dict = None) -> dict:
        """Start a conversation with a specific flow"""
        try:
            result = self.flow_executor.start_conversation(
                phone_number=phone_number,
                flow_id=flow_id,
                initial_data=initial_data or {}
            )
            
            # Log conversation start
            print(f"SUCCESS: Conversation started: {phone_number} -> {flow_id}")
            
            return result
            
        except Exception as e:
            print(f"ERROR: Error starting conversation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_message(self, phone_number: str, message_content: str) -> dict:
        """Process incoming message"""
        try:
            # Find active conversation
            conversation_id = self._find_conversation(phone_number)
            
            if not conversation_id:
                # Start default main flow from main.json
                return self.start_conversation(phone_number, "main")
            
            # Process message in existing conversation
            result = self.flow_executor.execute_step(
                conversation_id=conversation_id,
                user_input=message_content
            )
            
            # Log message processing
            print(f"SUCCESS: Message processed: {phone_number} -> {message_content}")
            
            return result
            
        except Exception as e:
            print(f"ERROR: Error processing message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_conversation(self, phone_number: str) -> str:
        """Find active conversation for phone number"""
        # This would typically query the database
        # For now, return a simple conversation ID
        return f"{phone_number}_conversation"
    
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
