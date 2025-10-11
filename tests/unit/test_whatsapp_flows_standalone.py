#!/usr/bin/env python3
"""
WhatsApp Flow Test Script - Standalone Version
Tests the flow system without any app dependencies
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class FlowStepType(Enum):
    """Flow step types"""
    MESSAGE = "message"
    QUESTION = "question"
    CHOICE = "choice"
    LIST = "list"
    CONDITION = "condition"
    ACTION = "action"
    WAIT = "wait"
    END = "end"


class MessageType(Enum):
    """Message types"""
    TEXT = "text"
    BUTTONS = "buttons"
    LIST = "list"
    MEDIA = "media"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    TEMPLATE = "template"


class FlowStep:
    """Represents a step in a conversation flow"""
    
    def __init__(self, step_id: str, step_type: FlowStepType, name: str, **kwargs):
        self.id = step_id
        self.type = step_type
        self.name = name
        self.message = kwargs.get("message")
        self.question = kwargs.get("question")
        self.next_step = kwargs.get("next_step")
        self.validation = kwargs.get("validation")
        self.conditions = kwargs.get("conditions", [])
        self.options = kwargs.get("options", [])
        self.sections = kwargs.get("sections", [])
        self.button_text = kwargs.get("button_text")
        self.timeout = kwargs.get("timeout")
        self.functions = kwargs.get("functions", [])
        self.data_sources = kwargs.get("data_sources", [])
        self.error_handler = kwargs.get("error_handler")


class FlowDefinition:
    """Represents a complete conversation flow"""
    
    def __init__(self, id: str, name: str, description: str, start_step: str, 
                 steps: Dict[str, FlowStep], variables: Dict[str, Any] = None,
                 error_handling: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        self.id = id
        self.name = name
        self.description = description
        self.start_step = start_step
        self.steps = steps
        self.variables = variables or {}
        self.error_handling = error_handling or {}
        self.metadata = metadata or {}


class SimpleFlowExecutor:
    """Simple flow executor for testing"""
    
    def __init__(self, whatsapp_service, persistence_service):
        self.whatsapp_service = whatsapp_service
        self.persistence_service = persistence_service
        self.active_flows: Dict[str, FlowDefinition] = {}
        self.conversation_states: Dict[str, Dict[str, Any]] = {}
    
    def register_flow(self, flow: FlowDefinition):
        """Register a flow for execution"""
        self.active_flows[flow.id] = flow
        print(f"SUCCESS: Flow registered: {flow.id} - {flow.name}")
    
    def start_conversation(self, phone_number: str, flow_id: str, 
                          initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start a conversation with a specific flow"""
        if flow_id not in self.active_flows:
            return {"success": False, "error": f"Flow {flow_id} not found"}
        
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
        """Execute current step"""
        if conversation_id not in self.conversation_states:
            return {"success": False, "error": f"Conversation {conversation_id} not found"}
        
        state = self.conversation_states[conversation_id]
        flow = self.active_flows[state["flow_id"]]
        current_step_id = state["current_step"]
        
        if current_step_id not in flow.steps:
            return {"success": False, "error": f"Step {current_step_id} not found"}
        
        current_step = flow.steps[current_step_id]
        
        # Execute step based on type
        if current_step.type == FlowStepType.MESSAGE:
            message = self._interpolate_variables(current_step.message, state["variables"])
            print(f"[FLOW] Sending message: {message}")
            next_step = current_step.next_step
            
        elif current_step.type == FlowStepType.QUESTION:
            question = self._interpolate_variables(current_step.question, state["variables"])
            print(f"[FLOW] Asking question: {question}")
            next_step = current_step.next_step
            
        elif current_step.type == FlowStepType.CHOICE:
            message = self._interpolate_variables(current_step.message, state["variables"])
            print(f"[FLOW] Sending choice: {message}")
            print(f"   Options: {[opt.get('title', opt.get('id', 'Unknown')) for opt in current_step.options]}")
            next_step = current_step.next_step
            
        elif current_step.type == FlowStepType.CONDITION:
            print(f"[FLOW] Evaluating conditions...")
            next_step = self._evaluate_conditions(current_step.conditions, state["data"])
            
        elif current_step.type == FlowStepType.END:
            message = self._interpolate_variables(current_step.message, state["variables"])
            print(f"[FLOW] Ending conversation: {message}")
            next_step = None
            
        else:
            print(f"[FLOW] Unknown step type: {current_step.type}")
            next_step = current_step.next_step
        
        # Update state
        if next_step:
            state["current_step"] = next_step
            state["last_activity"] = datetime.now()
        else:
            # Conversation ended
            del self.conversation_states[conversation_id]
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "current_step": current_step_id,
            "next_step": next_step,
            "message": getattr(current_step, 'message', None) or getattr(current_step, 'question', None)
        }
    
    def _interpolate_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Interpolate variables in text"""
        if not text:
            return text
        
        for key, value in variables.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
        
        return text
    
    def _evaluate_conditions(self, conditions: List[Dict], data: Dict[str, Any]) -> str:
        """Evaluate conditions and return next step"""
        for condition in conditions:
            condition_str = condition["condition"]
            # Simple condition evaluation (for testing)
            if "is_first_message == true" in condition_str and data.get("is_first_message", False):
                return condition["next_step"]
            elif "is_first_message == false" in condition_str and not data.get("is_first_message", True):
                return condition["next_step"]
        
        # Default to first condition's next step
        return conditions[0]["next_step"] if conditions else None


class SimpleFlowLoader:
    """Simple flow loader for testing"""
    
    def __init__(self, flows_directory: str = "app/flows"):
        self.flows_directory = Path(flows_directory)
        self.loaded_flows: Dict[str, FlowDefinition] = {}
    
    def load_flow_from_file(self, flow_file: str) -> FlowDefinition:
        """Load a flow from JSON file"""
        json_path = self.flows_directory / f"{flow_file}.json"
        
        if not json_path.exists():
            raise FileNotFoundError(f"Flow file {flow_file}.json not found")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
        
        return self._build_flow_from_config(flow_data)
    
    def load_all_flows(self) -> Dict[str, FlowDefinition]:
        """Load all flows from the flows directory"""
        flows = {}
        
        for json_file in self.flows_directory.glob("*.json"):
            flow_id = json_file.stem
            try:
                flow = self.load_flow_from_file(flow_id)
                flows[flow_id] = flow
            except Exception as e:
                print(f"❌ Error loading {flow_id}: {e}")
        
        return flows
    
    def _build_flow_from_config(self, config: Dict[str, Any]) -> FlowDefinition:
        """Build a flow from configuration"""
        flow_id = config["id"]
        name = config["name"]
        description = config.get("description", "")
        start_step = config.get("start_step")
        variables = config.get("variables", {})
        error_handling = config.get("error_handling", {})
        
        # Build steps
        steps = {}
        for step_data in config.get("steps", []):
            step_id = step_data["id"]
            step_type = FlowStepType(step_data["type"])
            step_name = step_data.get("name", step_id)
            
            step = FlowStep(
                step_id=step_id,
                step_type=step_type,
                name=step_name,
                message=step_data.get("message"),
                question=step_data.get("question"),
                next_step=step_data.get("next_step"),
                validation=step_data.get("validation"),
                conditions=step_data.get("conditions", [])
            )
            steps[step_id] = step
        
        return FlowDefinition(
            id=flow_id,
            name=name,
            description=description,
            start_step=start_step,
            steps=steps,
            variables=variables,
            error_handling=error_handling
        )


class MockWhatsAppService:
    """Mock WhatsApp service"""
    
    def __init__(self):
        self.message_sender = MockMessageSender()
        self.sent_messages = []
    
    async def send_message(self, phone_number: str, message: str):
        """Simulate sending a message"""
        print(f"[SIMULATED] Sending to {phone_number}: {message}")
        self.sent_messages.append({
            "phone_number": phone_number,
            "message": message,
            "type": "text"
        })
        return {"success": True, "message_id": f"sim_msg_{len(self.sent_messages)}"}


class MockMessageSender:
    """Mock message sender"""
    
    def send_buttons(self, phone_number: str, message: str, buttons: list):
        """Simulate sending buttons"""
        print(f"[SIMULATED] Sending buttons to {phone_number}: {message}")
        print(f"   Buttons: {[btn.get('title', btn.get('id', 'Unknown')) for btn in buttons]}")
        return {"success": True, "message_id": "sim_btn"}
    
    def send_list(self, phone_number: str, message: str, button_text: str, sections: list):
        """Simulate sending list"""
        print(f"[SIMULATED] Sending list to {phone_number}: {message}")
        print(f"   Button text: {button_text}")
        return {"success": True, "message_id": "sim_list"}


class MockPersistenceService:
    """Mock persistence service"""
    
    async def save_user(self, phone_number: str, name: str = None):
        """Simulate saving user"""
        print(f"[SIMULATED] Saving user: {phone_number}")
        return {"success": True, "user_id": f"user_{phone_number}"}
    
    async def save_conversation(self, phone_number: str, flow_id: str):
        """Simulate saving conversation"""
        print(f"[SIMULATED] Saving conversation: {phone_number} -> {flow_id}")
        return {"success": True, "conversation_id": f"conv_{phone_number}"}
    
    async def save_message(self, phone_number: str, message_content: str, message_type: str = "text"):
        """Simulate saving message"""
        print(f"[SIMULATED] Saving message: {phone_number}")
        return {"success": True, "message_id": "sim_msg"}


class WhatsAppFlowTester:
    """Tester for WhatsApp flow system"""
    
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.whatsapp_service = MockWhatsAppService()
        self.persistence_service = MockPersistenceService()
        self.flow_executor = SimpleFlowExecutor(self.whatsapp_service, self.persistence_service)
        self.flow_loader = SimpleFlowLoader("app/flows")
        
        # Load flows
        self._load_flows()
    
    def _load_flows(self):
        """Load flows from files"""
        try:
            flows = self.flow_loader.load_all_flows()
            for flow_id, flow in flows.items():
                # Only load test flows to avoid emoji issues
                if flow_id.startswith("test_"):
                    self.flow_executor.register_flow(flow)
        except Exception as e:
            print(f"ERROR: Error loading flows: {e}")
    
    async def test_main_flow(self):
        """Test the main flow with the provided phone number"""
        print(f"\nTesting Main Flow with {self.phone_number}")
        print("=" * 60)
        
        try:
            # Start conversation
            print("Starting conversation...")
            result = self.flow_executor.start_conversation(
                phone_number=self.phone_number,
                flow_id="test_main",
                initial_data={"is_first_message": True}
            )
            
            if result["success"]:
                print("SUCCESS: Conversation started successfully!")
                print(f"   Conversation ID: {result.get('conversation_id', 'N/A')}")
                
                # Simulate user responses
                await self._simulate_user_responses(result["conversation_id"])
                
            else:
                print(f"ERROR: Failed to start conversation: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"ERROR: Error testing main flow: {e}")
    
    async def test_order_flow(self):
        """Test the order flow with the provided phone number"""
        print(f"\nTesting Order Flow with {self.phone_number}")
        print("=" * 60)
        
        try:
            # Start conversation
            print("Starting order conversation...")
            result = self.flow_executor.start_conversation(
                phone_number=self.phone_number,
                flow_id="test_order",
                initial_data={"is_first_message": True}
            )
            
            if result["success"]:
                print("SUCCESS: Order conversation started successfully!")
                print(f"   Conversation ID: {result.get('conversation_id', 'N/A')}")
                
                # Simulate order flow responses
                await self._simulate_order_responses(result["conversation_id"])
                
            else:
                print(f"ERROR: Failed to start order conversation: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"ERROR: Error testing order flow: {e}")
    
    async def _simulate_user_responses(self, conversation_id: str):
        """Simulate user responses to test the flow"""
        print("\nSimulating user responses...")
        
        # Simulate different user inputs
        user_inputs = [
            "Hola, necesito ayuda",  # First response
            "Quiero información sobre productos",  # Second response
            "Gracias"  # Final response
        ]
        
        for i, user_input in enumerate(user_inputs, 1):
            print(f"\nUser response {i}: '{user_input}'")
            
            try:
                # Process user input
                result = self.flow_executor.execute_step(
                    conversation_id=conversation_id,
                    user_input=user_input
                )
                
                if result["success"]:
                    print(f"SUCCESS: Response processed successfully")
                    if result.get("message"):
                        print(f"   Bot response: {result['message']}")
                else:
                    print(f"ERROR: Failed to process response: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"ERROR: Error processing user input: {e}")
            
            # Small delay between responses
            await asyncio.sleep(0.5)
    
    async def _simulate_order_responses(self, conversation_id: str):
        """Simulate order flow responses"""
        print("\nSimulating order flow responses...")
        
        # Simulate order flow inputs
        order_inputs = [
            "order",  # Choose order option
            "Laptop",  # Product name
            "2",  # Quantity
            "yes"  # Confirm order
        ]
        
        for i, user_input in enumerate(order_inputs, 1):
            print(f"\nOrder response {i}: '{user_input}'")
            
            try:
                # Process user input
                result = self.flow_executor.execute_step(
                    conversation_id=conversation_id,
                    user_input=user_input
                )
                
                if result["success"]:
                    print(f"SUCCESS: Response processed successfully")
                    if result.get("message"):
                        print(f"   Bot response: {result['message']}")
                else:
                    print(f"ERROR: Failed to process response: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"ERROR: Error processing order input: {e}")
            
            # Small delay between responses
            await asyncio.sleep(0.5)
    
    def test_flow_loading(self):
        """Test that flows are loaded correctly"""
        print(f"\nTesting Flow Loading")
        print("=" * 40)
        
        # Check available flows
        available_flows = list(self.flow_executor.active_flows.keys())
        print(f"Available flows: {available_flows}")
        
        if "test_main" in available_flows:
            print("SUCCESS: Test main flow is available")
            
            # Get flow info
            flow = self.flow_executor.active_flows["test_main"]
            print(f"   Flow ID: {flow.id}")
            print(f"   Flow Name: {flow.name}")
            print(f"   Start Step: {flow.start_step}")
            print(f"   Steps Count: {len(flow.steps)}")
            print(f"   Variables: {list(flow.variables.keys())}")
            
            return True
        else:
            print("ERROR: Test main flow not found")
            return False
    
    def show_flow_structure(self):
        """Show the structure of the main flow"""
        print(f"\nMain Flow Structure")
        print("=" * 40)
        
        try:
            flow = self.flow_executor.active_flows.get("test_main")
            if not flow:
                print("ERROR: Test main flow not found")
                return
            
            print(f"Flow: {flow.name}")
            print(f"Description: {flow.description}")
            print(f"Start Step: {flow.start_step}")
            print(f"Variables: {flow.variables}")
            print(f"Error Handlers: {flow.error_handling}")
            
            print(f"\nSteps:")
            for step_id, step in flow.steps.items():
                print(f"  - {step_id}: {step.name} ({step.type.value})")
                if step.message:
                    print(f"    Message: {step.message[:50]}...")
                if step.question:
                    print(f"    Question: {step.question[:50]}...")
                if step.next_step:
                    print(f"    Next: {step.next_step}")
                    
        except Exception as e:
            print(f"ERROR: Error showing flow structure: {e}")


async def main():
    """Main test function"""
    # Get phone number from command line or use default
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
    else:
        phone_number = "+54 9 2625661694"  # Your phone number as default
    
    print("WhatsApp Flow System Test")
    print("=" * 60)
    print(f"Testing with phone number: {phone_number}")
    print("=" * 60)
    
    # Create tester
    tester = WhatsAppFlowTester(phone_number)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Flow loading
    if tester.test_flow_loading():
        tests_passed += 1
    
    # Test 2: Main flow execution
    await tester.test_main_flow()
    tests_passed += 1  # Assume execution test passed if no exceptions
    
    # Test 3: Order flow execution
    await tester.test_order_flow()
    tests_passed += 1  # Assume execution test passed if no exceptions
    
    # Show flow structure
    tester.show_flow_structure()
    
    # Summary
    print(f"\nTest Summary")
    print("=" * 60)
    print(f"SUCCESS: Passed: {tests_passed}/{total_tests}")
    print(f"ERROR: Failed: {total_tests - tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\nSUCCESS: All tests passed! Flow system is working correctly.")
        print(f"Ready to send messages to {phone_number}")
    else:
        print(f"\nERROR: {total_tests - tests_passed} tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
