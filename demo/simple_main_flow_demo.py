"""
Simple Main Flow Demo
Demonstrates the main flow functionality
"""
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock
from app.services.professional_unified_flow_loader import create_professional_unified_flow_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleMainFlowDemo:
    """Simple demo for the main flow"""
    
    def __init__(self):
        self.flow_loader = create_professional_unified_flow_loader("app/flows")
        self.active_conversations = {}
    
    async def simulate_main_flow(self, phone_number: str, is_first_message: bool = True):
        """Simulate the main flow execution"""
        logger.info(f"🎭 Simulating main flow for {phone_number} (first message: {is_first_message})")
        
        # Load main flow
        flow = self.flow_loader.load_flow_from_file("main")
        if not flow:
            logger.error("❌ Could not load main flow")
            return
        
        logger.info(f"✅ Loaded flow: {flow.name} ({flow.id})")
        
        # Initialize conversation context
        context = {
            "is_first_message": is_first_message,
            "company_name": "Mi Empresa",
            "support_hours": "9:00 - 18:00"
        }
        
        # Simulate flow execution
        current_step_id = flow.start_step
        step_count = 0
        max_steps = 10  # Prevent infinite loops
        
        while current_step_id and step_count < max_steps:
            step = flow.steps.get(current_step_id)
            if not step:
                logger.error(f"❌ Step {current_step_id} not found")
                break
            
            logger.info(f"📋 Step {step_count + 1}: {step.name} ({step.type.value})")
            
            # Execute step based on type
            if step.type.value == "condition":
                # Evaluate conditions
                for condition in step.conditions:
                    if self.evaluate_condition(condition["condition"], context):
                        current_step_id = condition["next_step"]
                        logger.info(f"🔍 Condition '{condition['condition']}' is True -> {current_step_id}")
                        break
                else:
                    logger.warning(f"⚠️ No condition matched for step {current_step_id}")
                    break
                    
            elif step.type.value == "message":
                message = self.interpolate_variables(step.message, context)
                logger.info(f"💬 Message: {message}")
                current_step_id = step.next_step
                
            elif step.type.value == "question":
                question = self.interpolate_variables(step.question, context)
                logger.info(f"❓ Question: {question}")
                # Simulate user response
                user_response = "Esta es mi consulta de prueba"
                logger.info(f"👤 User response: {user_response}")
                context["user_response"] = user_response
                current_step_id = step.next_step
                
            elif step.type.value == "end":
                message = self.interpolate_variables(step.message, context)
                logger.info(f"🏁 End message: {message}")
                break
                
            else:
                logger.warning(f"⚠️ Unknown step type: {step.type.value}")
                break
            
            step_count += 1
        
        logger.info(f"✅ Main flow simulation completed in {step_count} steps")
    
    def evaluate_condition(self, condition: str, context: dict) -> bool:
        """Evaluate a condition string"""
        try:
            # Replace context variables in condition
            for key, value in context.items():
                condition = condition.replace(key, repr(value))
            
            # Evaluate condition (simplified for demo)
            if "is_first_message == true" in condition:
                return context.get("is_first_message", False)
            elif "is_first_message == false" in condition:
                return not context.get("is_first_message", True)
            else:
                return False
        except Exception as e:
            logger.error(f"❌ Error evaluating condition '{condition}': {e}")
            return False
    
    def interpolate_variables(self, text: str, context: dict) -> str:
        """Interpolate variables in text"""
        if not text:
            return text
        
        for key, value in context.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
        
        return text
    
    def demonstrate_flow_loading(self):
        """Demonstrate loading different flow formats"""
        logger.info("📁 Demonstrating flow loading...")
        
        # Test loading different formats
        formats = ["main", "main_python", "main_yaml"]
        
        for flow_name in formats:
            logger.info(f"📁 Loading {flow_name}...")
            flow = self.flow_loader.load_flow_from_file(flow_name)
            
            if flow:
                logger.info(f"✅ Loaded: {flow.name} ({flow.id})")
                logger.info(f"   - Steps: {len(flow.steps)}")
                logger.info(f"   - Variables: {list(flow.variables.keys())}")
                logger.info(f"   - Start step: {flow.start_step}")
                
                # Validate flow
                validation = self.flow_loader.validate_flow_file(flow_name)
                logger.info(f"   - Valid: {validation['valid']}")
                if validation['issues']:
                    logger.info(f"   - Issues: {validation['issues']}")
            else:
                logger.warning(f"⚠️ Could not load {flow_name}")
            
            logger.info("-" * 40)
    
    def run_demo(self):
        """Run the complete demo"""
        logger.info("🚀 Starting Simple Main Flow Demo")
        logger.info("=" * 50)
        
        # Demonstrate flow loading
        self.demonstrate_flow_loading()
        
        # Simulate first-time user
        logger.info("👤 Simulating first-time user...")
        asyncio.run(self.simulate_main_flow("+1234567890", is_first_message=True))
        
        logger.info("-" * 50)
        
        # Simulate returning user
        logger.info("👤 Simulating returning user...")
        asyncio.run(self.simulate_main_flow("+1234567890", is_first_message=False))
        
        logger.info("=" * 50)
        logger.info("🎉 Simple Main Flow Demo Completed!")


def main():
    """Main demo function"""
    demo = SimpleMainFlowDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
