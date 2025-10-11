"""
Professional Flow System Demo
Demonstrates the capabilities of the professional flow system
"""
import asyncio
import json
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from app.services.professional_flow_system import (
    create_professional_flow_builder, FlowStepType, MessageType, DataSourceType,
    FunctionExecutor, DataSourceManager
)
from app.services.professional_unified_flow_loader import create_professional_unified_flow_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockWhatsAppService:
    """Mock WhatsApp service for demo purposes"""
    
    def __init__(self):
        self.message_sender = Mock()
        self.message_sender.send_buttons = AsyncMock(return_value={"success": True, "message_id": "demo_id"})
        self.message_sender.send_list = AsyncMock(return_value={"success": True, "message_id": "demo_id"})
    
    async def send_message(self, phone_number: str, message: str):
        """Mock send message"""
        logger.info(f"📱 [DEMO] Sending message to {phone_number}: {message}")
        return {"success": True, "message_id": "demo_id"}


class MockPersistenceService:
    """Mock persistence service for demo purposes"""
    
    def __init__(self):
        self.users = {}
        self.conversations = {}
        self.messages = []
    
    async def save_user(self, phone_number: str, name: str = None):
        """Mock save user"""
        user_id = f"user_{phone_number}"
        self.users[phone_number] = {"id": user_id, "name": name, "phone": phone_number}
        logger.info(f"💾 [DEMO] Saved user: {phone_number}")
        return {"success": True, "user_id": user_id}
    
    async def save_conversation(self, phone_number: str, flow_id: str):
        """Mock save conversation"""
        conv_id = f"conv_{phone_number}_{flow_id}"
        self.conversations[phone_number] = {"id": conv_id, "flow_id": flow_id, "phone": phone_number}
        logger.info(f"💾 [DEMO] Saved conversation: {conv_id}")
        return {"success": True, "conversation_id": conv_id}
    
    async def save_message(self, phone_number: str, message_content: str, message_type: str = "text"):
        """Mock save message"""
        msg_id = f"msg_{len(self.messages)}"
        self.messages.append({
            "id": msg_id, 
            "phone": phone_number, 
            "content": message_content, 
            "type": message_type
        })
        logger.info(f"💾 [DEMO] Saved message: {msg_id}")
        return {"success": True, "message_id": msg_id}


class ProfessionalFlowDemo:
    """Demo class for professional flow system"""
    
    def __init__(self):
        self.whatsapp_service = MockWhatsAppService()
        self.persistence_service = MockPersistenceService()
        self.function_executor = FunctionExecutor()
        self.data_source_manager = DataSourceManager()
        self.flow_loader = create_professional_unified_flow_loader("app/flows")
        self.active_conversations = {}
    
    def create_demo_flow(self):
        """Create a demo flow using the builder"""
        logger.info("🏗️ Creating demo flow using Professional Flow Builder...")
        
        return (create_professional_flow_builder(
            "demo_flow", 
            "Professional Demo Flow", 
            "Demonstrates all features of the professional flow system"
        )
        .start_with("welcome")
        
        # Add data sources
        .add_data_source(
            name="products_db",
            source_type=DataSourceType.STATIC,
            config={"data": {
                "products": [
                    {"id": "1", "name": "Premium Product", "price": 99.99, "category": "premium"},
                    {"id": "2", "name": "Standard Product", "price": 49.99, "category": "standard"},
                    {"id": "3", "name": "Basic Product", "price": 19.99, "category": "basic"}
                ]
            }},
            cache_ttl=300
        )
        .add_data_source(
            name="user_preferences",
            source_type=DataSourceType.STATIC,
            config={"data": {
                "preferences": {
                    "language": "es",
                    "notifications": True,
                    "theme": "dark"
                }
            }},
            cache_ttl=600
        )
        
        # Add functions
        .add_function(
            name="process_order",
            module="demo_functions",
            function="process_order",
            parameters={"product_id": "{{selected_product}}", "user_id": "{{user_id}}"},
            timeout=10,
            retry_count=2,
            cache_result=True
        )
        .add_function(
            name="send_confirmation",
            module="demo_functions",
            function="send_confirmation",
            parameters={"order_id": "{{order_id}}", "user_email": "{{user_email}}"},
            timeout=5,
            retry_count=1,
            cache_result=False
        )
        
        # Add steps
        .add_message_step(
            step_id="welcome",
            name="Welcome",
            message="🎉 Welcome to our Professional Flow Demo! This demonstrates all the advanced features.",
            next_step="check_user_type"
        )
        .add_condition_step(
            step_id="check_user_type",
            name="Check User Type",
            conditions=[
                {"condition": "is_first_message == true", "next_step": "first_time_greeting"},
                {"condition": "is_first_message == false", "next_step": "returning_greeting"}
            ]
        )
        .add_message_step(
            step_id="first_time_greeting",
            name="First Time Greeting",
            message="👋 Hello! This is your first time here. Let me show you what we can do!",
            next_step="show_features"
        )
        .add_message_step(
            step_id="returning_greeting",
            name="Returning Greeting",
            message="😊 Welcome back! Ready to explore more features?",
            next_step="show_features"
        )
        .add_message_step(
            step_id="show_features",
            name="Show Features",
            message="🚀 Our system supports:\n• Dynamic data sources\n• Function execution\n• Complex conditions\n• Error handling\n• Caching\n• Multiple message types",
            next_step="product_selection"
        )
        .add_list_step(
            step_id="product_selection",
            name="Product Selection",
            message="🛍️ Choose a product from our catalog:",
            button_text="View Products",
            sections=[
                {
                    "title": "Premium Products",
                    "rows": [
                        {"id": "1", "title": "Premium Product", "description": "High-quality premium product - $99.99"}
                    ]
                },
                {
                    "title": "Standard Products", 
                    "rows": [
                        {"id": "2", "title": "Standard Product", "description": "Good quality standard product - $49.99"}
                    ]
                },
                {
                    "title": "Basic Products",
                    "rows": [
                        {"id": "3", "title": "Basic Product", "description": "Affordable basic product - $19.99"}
                    ]
                }
            ],
            data_sources=["products_db"],
            next_step="collect_quantity"
        )
        .add_question_step(
            step_id="collect_quantity",
            name="Collect Quantity",
            question="📊 How many units would you like to order?",
            validation={
                "required": True,
                "type": "number",
                "min": 1,
                "max": 10,
                "error_message": "Please enter a valid quantity (1-10)."
            },
            next_step="process_order_step"
        )
        .add_function_step(
            step_id="process_order_step",
            name="Process Order",
            functions=["process_order"],
            next_step="send_confirmation_step"
        )
        .add_function_step(
            step_id="send_confirmation_step",
            name="Send Confirmation",
            functions=["send_confirmation"],
            next_step="show_success"
        )
        .add_message_step(
            step_id="show_success",
            name="Show Success",
            message="✅ Order processed successfully! Confirmation sent to {{user_email}}",
            next_step="ask_feedback"
        )
        .add_choice_step(
            step_id="ask_feedback",
            name="Ask Feedback",
            message="💬 How was your experience?",
            choice_type="buttons",
            options=[
                {"id": "excellent", "title": "Excellent ⭐⭐⭐⭐⭐"},
                {"id": "good", "title": "Good ⭐⭐⭐⭐"},
                {"id": "average", "title": "Average ⭐⭐⭐"},
                {"id": "poor", "title": "Poor ⭐⭐"}
            ],
            next_step="process_feedback"
        )
        .add_message_step(
            step_id="process_feedback",
            name="Process Feedback",
            message="📝 Thank you for your feedback! We'll use it to improve our service.",
            next_step="end"
        )
        .add_end_step(
            step_id="end",
            name="End",
            message="🎯 Demo completed! Thank you for exploring our Professional Flow System!"
        )
        
        # Error handling steps
        .add_message_step(
            step_id="show_error",
            name="Show Error",
            message="❌ An error occurred. Please try again.",
            next_step="welcome"
        )
        .add_message_step(
            step_id="show_timeout",
            name="Show Timeout",
            message="⏰ Timeout occurred. Let's start over.",
            next_step="welcome"
        )
        
        # Set variables
        .set_variable("company_name", "Professional Flow Demo")
        .set_variable("support_email", "support@demo.com")
        .set_variable("max_retries", 3)
        
        # Set error handlers
        .set_error_handler("validation_failed", "show_error")
        .set_error_handler("timeout", "show_timeout")
        .set_error_handler("function_error", "show_error")
        
        # Set metadata
        .set_metadata("version", "1.0")
        .set_metadata("author", "Professional Flow System")
        .set_metadata("last_updated", "2024-10-10")
        .set_metadata("tags", ["demo", "professional", "comprehensive"])
        .set_metadata("complexity", "high")
        
        .build()
        )
    
    async def simulate_conversation(self, phone_number: str, flow_id: str = "demo_flow"):
        """Simulate a complete conversation"""
        logger.info(f"🎭 Starting conversation simulation for {phone_number}")
        
        # Create demo flow
        flow = self.create_demo_flow()
        
        # Initialize conversation
        self.active_conversations[phone_number] = {
            "flow_id": flow_id,
            "current_step_id": flow.start_step,
            "context": {
                "is_first_message": True,
                "user_id": f"user_{phone_number}",
                "user_email": f"user_{phone_number}@demo.com"
            },
            "variables": flow.variables.copy()
        }
        
        # Simulate conversation steps
        conversation_steps = [
            ("welcome", "Welcome message"),
            ("check_user_type", "Check if first message"),
            ("first_time_greeting", "First time greeting"),
            ("show_features", "Show system features"),
            ("product_selection", "Show product list"),
            ("collect_quantity", "Ask for quantity"),
            ("process_order_step", "Process order"),
            ("send_confirmation_step", "Send confirmation"),
            ("show_success", "Show success message"),
            ("ask_feedback", "Ask for feedback"),
            ("process_feedback", "Process feedback"),
            ("end", "End conversation")
        ]
        
        for step_id, description in conversation_steps:
            logger.info(f"📋 Executing step: {step_id} - {description}")
            await self.execute_step(phone_number, flow, step_id)
            await asyncio.sleep(0.5)  # Simulate processing time
        
        logger.info(f"✅ Conversation simulation completed for {phone_number}")
    
    async def execute_step(self, phone_number: str, flow, step_id: str):
        """Execute a specific step"""
        conversation = self.active_conversations.get(phone_number)
        if not conversation:
            logger.error(f"No active conversation for {phone_number}")
            return
        
        step = flow.steps.get(step_id)
        if not step:
            logger.error(f"Step {step_id} not found")
            return
        
        logger.info(f"🔄 Executing step: {step.name} ({step.type.value})")
        
        # Simulate step execution based on type
        if step.type == FlowStepType.MESSAGE:
            message = self.interpolate_variables(step.message, conversation["variables"])
            await self.whatsapp_service.send_message(phone_number, message)
            
        elif step.type == FlowStepType.QUESTION:
            question = self.interpolate_variables(step.question, conversation["variables"])
            await self.whatsapp_service.send_message(phone_number, question)
            
        elif step.type == FlowStepType.CHOICE:
            await self.whatsapp_service.message_sender.send_buttons(
                phone_number, step.message, step.options
            )
            
        elif step.type == FlowStepType.LIST:
            await self.whatsapp_service.message_sender.send_list(
                phone_number, step.message, step.button_text, step.sections
            )
            
        elif step.type == FlowStepType.CONDITION:
            # Simulate condition evaluation
            logger.info(f"🔍 Evaluating conditions: {step.conditions}")
            
        elif step.type == FlowStepType.FUNCTION:
            # Simulate function execution
            logger.info(f"⚙️ Executing functions: {step.functions}")
            
        elif step.type == FlowStepType.END:
            message = self.interpolate_variables(step.message, conversation["variables"])
            await self.whatsapp_service.send_message(phone_number, message)
            logger.info(f"🏁 Flow ended for {phone_number}")
    
    def interpolate_variables(self, text: str, variables: dict) -> str:
        """Interpolate variables in text"""
        if not text:
            return text
        
        for key, value in variables.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
        
        return text
    
    def demonstrate_data_sources(self):
        """Demonstrate data source functionality"""
        logger.info("📊 Demonstrating Data Sources...")
        
        # Create sample data sources
        static_source = DataSource(
            name="demo_static",
            type=DataSourceType.STATIC,
            config={"data": {"message": "Hello from static data!"}},
            cache_ttl=300
        )
        
        # Test data source manager
        result = self.data_source_manager.get_data(static_source)
        logger.info(f"📊 Static data result: {result}")
    
    def demonstrate_functions(self):
        """Demonstrate function execution"""
        logger.info("⚙️ Demonstrating Function Execution...")
        
        # Create mock function
        def demo_function(param1, param2):
            return {"result": f"{param1}_{param2}", "success": True}
        
        # Mock module import
        import sys
        from types import ModuleType
        
        demo_module = ModuleType('demo_functions')
        demo_module.process_order = demo_function
        demo_module.send_confirmation = demo_function
        sys.modules['demo_functions'] = demo_module
        
        # Test function execution
        from app.services.professional_flow_system import FunctionConfig
        
        func_config = FunctionConfig(
            name="demo_func",
            module="demo_functions",
            function="process_order",
            parameters={"param1": "test", "param2": "demo"}
        )
        
        result = self.function_executor.execute_function(func_config, {})
        logger.info(f"⚙️ Function execution result: {result}")
    
    def demonstrate_flow_loading(self):
        """Demonstrate flow loading from files"""
        logger.info("📁 Demonstrating Flow Loading...")
        
        # Load flows from files
        flows = self.flow_loader.load_all_flows()
        logger.info(f"📁 Loaded {len(flows)} flows: {list(flows.keys())}")
        
        # Validate flows
        for flow_id in flows.keys():
            validation = self.flow_loader.validate_flow_file(flow_id)
            logger.info(f"📁 Flow {flow_id} validation: {validation}")
    
    def run_complete_demo(self):
        """Run the complete demonstration"""
        logger.info("🚀 Starting Professional Flow System Demo")
        logger.info("=" * 60)
        
        # Demonstrate data sources
        self.demonstrate_data_sources()
        logger.info("-" * 40)
        
        # Demonstrate functions
        self.demonstrate_functions()
        logger.info("-" * 40)
        
        # Demonstrate flow loading
        self.demonstrate_flow_loading()
        logger.info("-" * 40)
        
        # Run conversation simulation
        asyncio.run(self.simulate_conversation("+1234567890"))
        
        logger.info("=" * 60)
        logger.info("🎉 Professional Flow System Demo Completed!")


def main():
    """Main demo function"""
    demo = ProfessionalFlowDemo()
    demo.run_complete_demo()


if __name__ == "__main__":
    main()
