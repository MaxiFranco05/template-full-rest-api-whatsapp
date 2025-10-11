#!/usr/bin/env python3
"""
Real WhatsApp Flow Test Script
Tests the flow system with real WhatsApp API calls
"""
import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.services.whatsapp_service import WhatsAppService
    from app.services.whatsapp_persistence_service import WhatsAppPersistenceService
    from app.services.whatsapp_flow_service import WhatsAppFlowService
    from app.db.database import get_db
except ImportError as e:
    print(f"ERROR: Failed to import app modules: {e}")
    print(f"Current directory: {Path.cwd()}")
    sys.exit(1)


class RealWhatsAppTester:
    """Tester for real WhatsApp flow system"""
    
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.db = next(get_db())
        
        # Initialize real services
        self.whatsapp_service = WhatsAppService()
        self.persistence_service = WhatsAppPersistenceService(self.db)
        self.flow_service = WhatsAppFlowService(
            self.whatsapp_service, 
            self.persistence_service
        )
        
        print(f"Initialized real WhatsApp services")
        print(f"Phone number: {self.phone_number}")
        print(f"WhatsApp API URL: {os.getenv('WHATSAPP_API_URL', 'Not set')}")
        print(f"Phone Number ID: {os.getenv('WHATSAPP_PHONE_NUMBER_ID', 'Not set')}")
    
    async def test_simple_message(self):
        """Test sending a simple message"""
        print(f"\nTesting simple message to {self.phone_number}")
        print("=" * 60)
        
        try:
            message = "Hola! Este es un mensaje de prueba del sistema de flows. ¿Puedes confirmar que lo recibiste?"
            
            result = await self.whatsapp_service.send_message(
                to=self.phone_number,
                message=message
            )
            
            if result.get("success"):
                print("SUCCESS: Message sent successfully!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending message: {e}")
            return False
    
    async def test_flow_conversation(self):
        """Test starting a flow conversation"""
        print(f"\nTesting flow conversation with {self.phone_number}")
        print("=" * 60)
        
        try:
            # Start main flow conversation
            result = self.flow_service.start_conversation(
                phone_number=self.phone_number,
                flow_id="main",
                initial_data={"is_first_message": True}
            )
            
            if result.get("success"):
                print("SUCCESS: Flow conversation started!")
                print(f"Conversation ID: {result.get('conversation_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to start flow: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception starting flow: {e}")
            return False
    
    def check_environment(self):
        """Check if environment variables are properly set"""
        print(f"\nChecking environment configuration")
        print("=" * 40)
        
        required_vars = [
            "WHATSAPP_ACCESS_TOKEN",
            "WHATSAPP_PHONE_NUMBER_ID", 
            "WHATSAPP_WEBHOOK_VERIFY_TOKEN",
            "WHATSAPP_API_URL"
        ]
        
        all_set = True
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if "TOKEN" in var or "ACCESS" in var:
                    masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                    print(f"SUCCESS: {var} = {masked_value}")
                else:
                    print(f"SUCCESS: {var} = {value}")
            else:
                print(f"ERROR: {var} is not set")
                all_set = False
        
        return all_set


async def main():
    """Main test function"""
    # Get phone number from command line or use default
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
    else:
        phone_number = "5492625661694"  # Your phone number without + for WhatsApp API
    
    # Ensure phone number format is correct (no +, no spaces)
    phone_number = phone_number.replace("+", "").replace(" ", "").replace("-", "")
    
    print("Real WhatsApp Flow System Test")
    print("=" * 60)
    print(f"Testing with phone number: {phone_number}")
    print("=" * 60)
    
    # Create tester
    tester = RealWhatsAppTester(phone_number)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Environment check
    if tester.check_environment():
        tests_passed += 1
        print("SUCCESS: Environment configuration is correct")
    else:
        print("ERROR: Environment configuration has issues")
        return
    
    # Test 2: Simple message
    if await tester.test_simple_message():
        tests_passed += 1
    
    # Test 3: Flow conversation
    if await tester.test_flow_conversation():
        tests_passed += 1
    
    # Summary
    print(f"\nTest Summary")
    print("=" * 60)
    print(f"SUCCESS: Passed: {tests_passed}/{total_tests}")
    print(f"ERROR: Failed: {total_tests - tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print(f"\nSUCCESS: All tests passed! Messages should arrive at {phone_number}")
    else:
        print(f"\nERROR: {total_tests - tests_passed} tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
