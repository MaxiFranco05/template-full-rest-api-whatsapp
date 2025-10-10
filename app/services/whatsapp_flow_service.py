"""
Integration Example
Example of how to integrate the new conversation flow system
"""
from app.services.conversation_flow_builder import create_flow_executor
from app.services.conversation_flow_examples import get_flow
from app.services.unified_flow_loader import create_unified_flow_loader


class WhatsAppFlowService:
    """Service for managing WhatsApp conversation flows"""
    
    def __init__(self, whatsapp_service, persistence_service):
        self.whatsapp_service = whatsapp_service
        self.persistence_service = persistence_service
        self.flow_executor = create_flow_executor(whatsapp_service, persistence_service)
        self.unified_loader = create_unified_flow_loader("app/flows")
        
        # Register default flows
        self._register_default_flows()
        
        # Load flows from JSON and YAML files
        self._load_config_flows()
    
    def _register_default_flows(self):
        """Register default flows"""
        try:
            # Register example flows
            self.flow_executor.register_flow(get_flow("welcome"))
            self.flow_executor.register_flow(get_flow("order"))
            self.flow_executor.register_flow(get_flow("appointment"))
            self.flow_executor.register_flow(get_flow("support"))
            
            print("✅ Default flows registered successfully")
        except Exception as e:
            print(f"❌ Error registering default flows: {e}")
    
    def _load_config_flows(self):
        """Load flows from JSON and YAML files"""
        try:
            config_flows = self.unified_loader.load_all_flows()
            for flow_id, flow in config_flows.items():
                self.flow_executor.register_flow(flow)
                print(f"✅ Config flow loaded: {flow_id}")
        except Exception as e:
            print(f"❌ Error loading config flows: {e}")
    
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
            print(f"🚀 Conversation started: {phone_number} -> {flow_id}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error starting conversation: {e}")
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
                # Start default welcome flow
                return self.start_conversation(phone_number, "welcome")
            
            # Process message in existing conversation
            result = self.flow_executor.execute_step(
                conversation_id=conversation_id,
                user_input=message_content
            )
            
            # Log message processing
            print(f"📨 Message processed: {phone_number} -> {message_content}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
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


# Example usage
def example_usage():
    """Example of how to use the WhatsApp Flow Service"""
    
    # Mock services (replace with real services)
    class MockWhatsAppService:
        def __init__(self):
            self.message_sender = MockMessageSender()
    
    class MockMessageSender:
        def send_text(self, phone_number, message):
            print(f"📱 Sending text to {phone_number}: {message}")
            return {"success": True, "message_id": "msg_123"}
        
        def send_buttons(self, phone_number, message, buttons):
            print(f"📱 Sending buttons to {phone_number}: {message}")
            print(f"🔘 Buttons: {buttons}")
            return {"success": True, "message_id": "msg_124"}
        
        def send_list(self, phone_number, message, button_text, sections):
            print(f"📱 Sending list to {phone_number}: {message}")
            print(f"📋 List: {sections}")
            return {"success": True, "message_id": "msg_125"}
    
    class MockPersistenceService:
        pass
    
    # Create services
    whatsapp_service = MockWhatsAppService()
    persistence_service = MockPersistenceService()
    
    # Create flow service
    flow_service = WhatsAppFlowService(whatsapp_service, persistence_service)
    
    # Example conversation
    phone_number = "+1234567890"
    
    print("🚀 Starting conversation...")
    result = flow_service.start_conversation(phone_number, "welcome")
    print(f"Result: {result}")
    
    print("\n📨 Processing user response...")
    result = flow_service.process_message(phone_number, "products")
    print(f"Result: {result}")
    
    print("\n📨 Processing another response...")
    result = flow_service.process_message(phone_number, "product_1")
    print(f"Result: {result}")
    
    print("\n📊 Available flows:")
    flows = flow_service.get_available_flows()
    for flow_id in flows:
        info = flow_service.get_flow_info(flow_id)
        print(f"  - {flow_id}: {info['name']} ({info['steps_count']} steps)")


if __name__ == "__main__":
    example_usage()
