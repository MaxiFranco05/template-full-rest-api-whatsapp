# Load Testing with Locust

"""
Professional load testing suite for Business API Template
"""

from locust import HttpUser, task, between
import json
import random
import time
from typing import Dict, Any

class APIUser(HttpUser):
    """Base API user for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        self.token = None
        self.user_id = None
        self.product_ids = []
        self.whatsapp_conversations = []
        
        # Login to get token
        self.login()
        
        # Load some test data
        self.load_test_data()
    
    def login(self):
        """Login and get authentication token"""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        with self.client.post("/api/v1/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data["data"]["access_token"]
                    self.user_id = data["data"]["user"]["id"]
                    response.success()
                else:
                    response.failure("Login failed: " + str(data))
            else:
                response.failure(f"Login failed with status {response.status_code}")
    
    def load_test_data(self):
        """Load test data for use in tests"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get products
        with self.client.get("/api/v1/products/", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.product_ids = [p["id"] for p in data["data"]["items"][:10]]
        
        # Get WhatsApp conversations
        with self.client.get("/api/v1/whatsapp/conversations/", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.whatsapp_conversations = [c["id"] for c in data["data"]["items"][:5]]
    
    @task(3)
    def get_health_check(self):
        """Health check endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(2)
    def get_performance_stats(self):
        """Performance statistics endpoint"""
        with self.client.get("/performance", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Performance stats failed: {response.status_code}")
    
    @task(5)
    def get_users(self):
        """Get users list"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "page": random.randint(1, 5),
            "size": random.randint(10, 50)
        }
        
        with self.client.get("/api/v1/users/", headers=headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Get users failed: " + str(data))
            else:
                response.failure(f"Get users failed: {response.status_code}")
    
    @task(4)
    def get_products(self):
        """Get products list"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "page": random.randint(1, 3),
            "size": random.randint(10, 30),
            "is_available": random.choice([True, False, None])
        }
        
        with self.client.get("/api/v1/products/", headers=headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Get products failed: " + str(data))
            else:
                response.failure(f"Get products failed: {response.status_code}")
    
    @task(2)
    def get_specific_product(self):
        """Get specific product by ID"""
        if not self.token or not self.product_ids:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        product_id = random.choice(self.product_ids)
        
        with self.client.get(f"/api/v1/products/{product_id}", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Get product failed: " + str(data))
            else:
                response.failure(f"Get product failed: {response.status_code}")
    
    @task(1)
    def create_product(self):
        """Create new product"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        product_data = {
            "name": f"Load Test Product {random.randint(1000, 9999)}",
            "description": f"Product created during load test {time.time()}",
            "price": random.randint(100, 5000),
            "stock_quantity": random.randint(1, 100),
            "is_available": random.choice([True, False])
        }
        
        with self.client.post("/api/v1/products/", headers=headers, json=product_data, catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                if data.get("success"):
                    # Add new product to our list
                    self.product_ids.append(data["data"]["id"])
                    response.success()
                else:
                    response.failure("Create product failed: " + str(data))
            else:
                response.failure(f"Create product failed: {response.status_code}")
    
    @task(1)
    def update_product(self):
        """Update existing product"""
        if not self.token or not self.product_ids:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        product_id = random.choice(self.product_ids)
        update_data = {
            "price": random.randint(100, 5000),
            "stock_quantity": random.randint(1, 100)
        }
        
        with self.client.put(f"/api/v1/products/{product_id}", headers=headers, json=update_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Update product failed: " + str(data))
            else:
                response.failure(f"Update product failed: {response.status_code}")
    
    @task(2)
    def get_whatsapp_conversations(self):
        """Get WhatsApp conversations"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "page": random.randint(1, 3),
            "size": random.randint(5, 20),
            "active": random.choice([True, False, None])
        }
        
        with self.client.get("/api/v1/whatsapp/conversations/", headers=headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Get conversations failed: " + str(data))
            else:
                response.failure(f"Get conversations failed: {response.status_code}")
    
    @task(1)
    def get_whatsapp_messages(self):
        """Get WhatsApp messages"""
        if not self.token or not self.whatsapp_conversations:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        conversation_id = random.choice(self.whatsapp_conversations)
        params = {
            "conversation_id": conversation_id,
            "page": random.randint(1, 2),
            "size": random.randint(10, 30)
        }
        
        with self.client.get("/api/v1/whatsapp/messages/", headers=headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Get messages failed: " + str(data))
            else:
                response.failure(f"Get messages failed: {response.status_code}")
    
    @task(1)
    def send_whatsapp_message(self):
        """Send WhatsApp message"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        message_data = {
            "to": f"+123456789{random.randint(0, 9)}",
            "message_type": "text",
            "content": {
                "text": f"Load test message {time.time()}"
            }
        }
        
        with self.client.post("/api/v1/whatsapp/send", headers=headers, json=message_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Send message failed: " + str(data))
            else:
                response.failure(f"Send message failed: {response.status_code}")

class HeavyUser(APIUser):
    """Heavy user that performs more intensive operations"""
    
    wait_time = between(0.5, 1.5)  # Faster requests
    
    @task(10)
    def intensive_product_operations(self):
        """Perform intensive product operations"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create multiple products
        for _ in range(3):
            product_data = {
                "name": f"Heavy Test Product {random.randint(1000, 9999)}",
                "description": f"Intensive load test product {time.time()}",
                "price": random.randint(100, 5000),
                "stock_quantity": random.randint(1, 100),
                "is_available": True
            }
            
            with self.client.post("/api/v1/products/", headers=headers, json=product_data, catch_response=True) as response:
                if response.status_code == 201:
                    response.success()
                else:
                    response.failure(f"Heavy product creation failed: {response.status_code}")
    
    @task(5)
    def bulk_user_operations(self):
        """Perform bulk user operations"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get users with different parameters
        for page in range(1, 4):
            params = {"page": page, "size": 50}
            with self.client.get("/api/v1/users/", headers=headers, params=params, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Bulk user operations failed: {response.status_code}")

class StressUser(APIUser):
    """Stress test user for maximum load"""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task(20)
    def rapid_fire_requests(self):
        """Send rapid fire requests to stress test the system"""
        endpoints = [
            "/health",
            "/performance",
            "/api/v1/users/",
            "/api/v1/products/"
        ]
        
        endpoint = random.choice(endpoints)
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        with self.client.get(endpoint, headers=headers, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Rapid fire request failed: {response.status_code}")

class WhatsAppLoadUser(HttpUser):
    """Specialized user for WhatsApp load testing"""
    
    wait_time = between(2, 5)  # Simulate real user behavior
    
    def on_start(self):
        """Setup for WhatsApp testing"""
        self.token = None
        self.login()
    
    def login(self):
        """Login for WhatsApp testing"""
        login_data = {
            "username": "whatsapp_test_user",
            "password": "whatsapp_password"
        }
        
        with self.client.post("/api/v1/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data["data"]["access_token"]
                    response.success()
                else:
                    response.failure("WhatsApp user login failed")
            else:
                response.failure(f"WhatsApp login failed: {response.status_code}")
    
    @task(5)
    def webhook_simulation(self):
        """Simulate WhatsApp webhook calls"""
        webhook_data = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": f"entry_{random.randint(1000, 9999)}",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": f"+123456789{random.randint(0, 9)}",
                            "phone_number_id": f"phone_{random.randint(1000, 9999)}"
                        },
                        "messages": [{
                            "from": f"+123456789{random.randint(0, 9)}",
                            "id": f"msg_{random.randint(10000, 99999)}",
                            "timestamp": str(int(time.time())),
                            "text": {
                                "body": f"Load test message {time.time()}"
                            },
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        with self.client.post("/api/v1/whatsapp/webhook", json=webhook_data, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Webhook simulation failed: {response.status_code}")
    
    @task(3)
    def send_message_load_test(self):
        """Send messages for load testing"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        message_types = ["text", "interactive", "image"]
        message_type = random.choice(message_types)
        
        if message_type == "text":
            content = {"text": f"Load test text message {time.time()}"}
        elif message_type == "interactive":
            content = {
                "type": "button",
                "header": {"type": "text", "text": "Load Test"},
                "body": {"text": "This is a load test message"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "test_btn", "title": "Test"}}
                    ]
                }
            }
        else:  # image
            content = {
                "link": "https://via.placeholder.com/300x200.png",
                "caption": f"Load test image {time.time()}"
            }
        
        message_data = {
            "to": f"+123456789{random.randint(0, 9)}",
            "message_type": message_type,
            "content": content
        }
        
        with self.client.post("/api/v1/whatsapp/send", headers=headers, json=message_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Send message load test failed: {response.status_code}")
    
    @task(2)
    def get_conversation_load_test(self):
        """Get conversations for load testing"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "page": random.randint(1, 3),
            "size": random.randint(10, 50),
            "active": random.choice([True, False, None])
        }
        
        with self.client.get("/api/v1/whatsapp/conversations/", headers=headers, params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get conversations load test failed: {response.status_code}")

# Load test scenarios
class NormalLoadTest(APIUser):
    """Normal load test scenario"""
    pass

class PeakLoadTest(HeavyUser):
    """Peak load test scenario"""
    pass

class StressTest(StressUser):
    """Stress test scenario"""
    pass

class WhatsAppLoadTest(WhatsAppLoadUser):
    """WhatsApp specific load test"""
    pass
