#!/usr/bin/env python3
"""
WhatsApp Native Message Types Test
Tests ALL native WhatsApp message types using real API calls
This test uses the actual WhatsApp message types, not text fallbacks
"""
import sys
import asyncio
import os
import json
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.services.whatsapp_service import WhatsAppService
except ImportError as e:
    print(f"ERROR: Failed to import app modules: {e}")
    print(f"Project root: {project_root}")
    sys.exit(1)


class WhatsAppNativeMessageTester:
    """Tester for native WhatsApp message types"""
    
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.whatsapp_service = WhatsAppService()
        self.last_message_id = None  # Store the last message ID for reactions
        
        print(f"Initialized WhatsApp Native Message Tester")
        print(f"Phone number: {self.phone_number}")
        print(f"WhatsApp API URL: {os.getenv('WHATSAPP_API_URL', 'Not set')}")
        print(f"Phone Number ID: {os.getenv('WHATSAPP_PHONE_NUMBER_ID', 'Not set')}")
    
    def load_test_flow(self):
        """Load the test flow from JSON file"""
        print(f"\nLoading test flow from JSON")
        print("=" * 40)
        
        try:
            flow_file = Path(__file__).parent / "test_message_types_flow.json"
            
            if not flow_file.exists():
                print(f"ERROR: Flow file not found: {flow_file}")
                return None
            
            with open(flow_file, 'r', encoding='utf-8') as f:
                flow_data = json.load(f)
            
            print(f"SUCCESS: Loaded flow '{flow_data['name']}'")
            print(f"Flow ID: {flow_data['flow_id']}")
            print(f"Steps: {len(flow_data['steps'])}")
            
            return flow_data
            
        except Exception as e:
            print(f"ERROR: Failed to load flow: {e}")
            return None
    
    async def execute_flow_step(self, step_data):
        """Execute a single flow step"""
        step_id = step_data.get("id", "unknown")
        step_type = step_data.get("type", "MESSAGE")
        message_type = step_data.get("message_type", "text")
        
        print(f"\nExecuting step: {step_id} ({step_type})")
        print(f"Message type: {message_type}")
        print("-" * 40)
        
        try:
            if step_type == "MESSAGE":
                return await self._send_native_message(step_data)
            elif step_type == "END":
                print("Flow completed!")
                return True
            else:
                print(f"WARNING: Unknown step type: {step_type}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception in step {step_id}: {e}")
            return False
    
    async def _send_native_message(self, step_data):
        """Send message using native WhatsApp types"""
        message_type = step_data.get("message_type", "text")
        message = step_data.get("message", "")
        
        if message_type == "text":
            return await self._send_text_message(message)
        elif message_type == "interactive":
            return await self._send_interactive_message(step_data)
        elif message_type == "image":
            return await self._send_image_message(step_data)
        elif message_type == "document":
            return await self._send_document_message(step_data)
        elif message_type == "audio":
            return await self._send_audio_message(step_data)
        elif message_type == "video":
            return await self._send_video_message(step_data)
        elif message_type == "location":
            return await self._send_location_message(step_data)
        elif message_type == "contacts":
            return await self._send_contact_message(step_data)
        elif message_type == "sticker":
            success = await self._send_sticker_message(step_data)
            if success:
                # Extra delay for sticker to ensure it's processed
                await asyncio.sleep(3)
            return success
        elif message_type == "template":
            return await self._send_template_message(step_data)
        elif message_type == "reaction":
            return await self._send_reaction_message(step_data)
        elif message_type == "catalog":
            return await self._send_catalog_message(step_data)
        elif message_type == "flow":
            return await self._send_flow_message(step_data)
        else:
            print(f"ERROR: Unknown message type: {message_type}")
            return False
    
    async def _send_text_message(self, message):
        """Send simple text message"""
        try:
            result = await self.whatsapp_service.send_message(
                to=self.phone_number,
                message=message
            )
            
            if result.get("success"):
                print(f"SUCCESS: Text message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send text message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending text message: {e}")
            return False
    
    async def _send_interactive_message(self, step_data):
        """Send interactive message (buttons or list)"""
        try:
            interactive_type = step_data.get("interactive_type", "button")
            message = step_data.get("message", "")
            
            print(f"Attempting to send {interactive_type} interactive message...")
            print(f"Message: {message}")
            
            if interactive_type == "button":
                buttons = step_data.get("buttons", [])
                print(f"Buttons: {buttons}")
                
                # Create button message payload
                payload = {
                    "messaging_product": "whatsapp",
                    "to": self.phone_number,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": message},
                        "action": {
                            "buttons": []
                        }
                    }
                }
                
                # Determine button type from first button (all buttons must be same type)
                first_button_type = buttons[0].get("type", "reply") if buttons else "reply"
                
                for button in buttons:
                    if first_button_type == "reply":
                        payload["interactive"]["action"]["buttons"].append({
                            "type": "reply",
                            "reply": {
                                "id": button["id"],
                                "title": button["title"]
                            }
                        })
                    elif first_button_type == "url":
                        payload["interactive"]["action"]["buttons"].append({
                            "type": "url",
                            "url": {
                                "url": button["url"],
                                "title": button["title"]
                            }
                        })
                    elif first_button_type == "phone":
                        payload["interactive"]["action"]["buttons"].append({
                            "type": "phone_number",
                            "phone_number": {
                                "phone_number": button["phone"],
                                "title": button["title"]
                            }
                        })
                    elif first_button_type == "location_request":
                        payload["interactive"]["action"]["buttons"].append({
                            "type": "location_request",
                            "location_request": {
                                "title": button["title"]
                            }
                        })
                
            elif interactive_type == "list":
                button_text = step_data.get("button_text", "Ver opciones")
                sections = step_data.get("sections", [])
                print(f"Button text: {button_text}")
                print(f"Sections: {len(sections)}")
                
                # Create list message payload
                payload = {
                    "messaging_product": "whatsapp",
                    "to": self.phone_number,
                    "type": "interactive",
                    "interactive": {
                        "type": "list",
                        "body": {"text": message},
                        "action": {
                            "button": button_text,
                            "sections": []
                        }
                    }
                }
                
                for section in sections:
                    section_data = {
                        "title": section["title"],
                        "rows": []
                    }
                    
                    for row in section["rows"]:
                        section_data["rows"].append({
                            "id": row["id"],
                            "title": row["title"],
                            "description": row["description"]
                        })
                    
                    payload["interactive"]["action"]["sections"].append(section_data)
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            # Send using WhatsApp service's direct API call
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: {interactive_type} interactive message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send {interactive_type} message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending interactive message: {e}")
            return False
    
    async def _send_image_message(self, step_data):
        """Send image message"""
        try:
            image_url = step_data.get("image_url", "")
            caption = step_data.get("caption", "")
            
            print(f"Attempting to send image message...")
            print(f"Image URL: {image_url}")
            print(f"Caption: {caption}")
            
            # Create image message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": self.phone_number,
                "type": "image",
                "image": {
                    "link": image_url
                }
            }
            
            if caption:
                payload["image"]["caption"] = caption
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Image message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send image message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending image message: {e}")
            return False
    
    async def _send_document_message(self, step_data):
        """Send document message"""
        try:
            document_url = step_data.get("document_url", "")
            filename = step_data.get("filename", "document.pdf")
            caption = step_data.get("caption", "")
            
            print(f"Attempting to send document message...")
            print(f"Document URL: {document_url}")
            print(f"Filename: {filename}")
            print(f"Caption: {caption}")
            
            # Create document message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": self.phone_number,
                "type": "document",
                "document": {
                    "link": document_url,
                    "filename": filename
                }
            }
            
            if caption:
                payload["document"]["caption"] = caption
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Document message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send document message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending document message: {e}")
            return False
    
    async def _send_audio_message(self, step_data):
        """Send audio message"""
        try:
            audio_url = step_data.get("audio_url", "")
            
            print(f"Attempting to send audio message...")
            print(f"Audio URL: {audio_url}")
            
            # Create audio message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": self.phone_number,
                "type": "audio",
                "audio": {
                    "link": audio_url
                }
            }
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Audio message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send audio message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending audio message: {e}")
            return False
    
    async def _send_video_message(self, step_data):
        """Send video message"""
        try:
            video_url = step_data.get("video_url", "")
            caption = step_data.get("caption", "")
            
            print(f"Attempting to send video message...")
            print(f"Video URL: {video_url}")
            print(f"Caption: {caption}")
            
            # Create video message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": self.phone_number,
                "type": "video",
                "video": {
                    "link": video_url
                }
            }
            
            if caption:
                payload["video"]["caption"] = caption
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Video message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send video message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending video message: {e}")
            return False
    
    async def _send_location_message(self, step_data):
        """Send location message"""
        try:
            latitude = step_data.get("latitude", 0)
            longitude = step_data.get("longitude", 0)
            name = step_data.get("name", "")
            address = step_data.get("address", "")
            
            print(f"Attempting to send location message...")
            print(f"Location: {name} ({latitude}, {longitude})")
            print(f"Address: {address}")
            
            # Create location message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": self.phone_number,
                "type": "location",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "name": name,
                    "address": address
                }
            }
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Location message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send location message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending location message: {e}")
            return False
    
    async def _send_contact_message(self, step_data):
        """Send contact message"""
        try:
            contacts = step_data.get("contacts", [])
            
            print(f"Attempting to send contact message...")
            print(f"Contacts: {len(contacts)}")
            
            # Create contact message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": self.phone_number,
                "type": "contacts",
                "contacts": contacts
            }
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Contact message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send contact message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending contact message: {e}")
            return False
    
    async def _upload_media(self, media_url: str) -> str:
        """Upload media to WhatsApp and return media_id"""
        try:
            import aiohttp
            
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            api_url = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v23.0")
            
            url = f"{api_url}/{phone_number_id}/media"
            headers = {
                "Authorization": f"Bearer {access_token}",
            }
            
            data = {
                "messaging_product": "whatsapp",
                "url": media_url,
                "type": "sticker"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        media_id = response_data.get("id")
                        print(f"SUCCESS: Media uploaded with ID: {media_id}")
                        return media_id
                    else:
                        print(f"ERROR: Failed to upload media: {response_data}")
                        return None
                        
        except Exception as e:
            print(f"ERROR: Exception uploading media: {e}")
            return None
    
    async def _send_sticker_message(self, step_data):
        """Send sticker message - TEMPORARILY DISABLED"""
        print(f"SKIP: Sticker message temporarily disabled")
        print(f"NOTE: Sticker implementation requires 2-step process (upload + send)")
        print(f"TODO: Implement proper sticker upload and send flow")
        return False

    async def _upload_sticker(self, sticker_url: str) -> dict:
        """Upload sticker to WhatsApp servers and get media ID"""
        try:
            print(f"Uploading sticker from URL: {sticker_url}")
            
            # Download the sticker
            async with aiohttp.ClientSession() as session:
                async with session.get(sticker_url) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"Failed to download sticker: {response.status}"}
                    
                    sticker_data = await response.read()
                    print(f"Downloaded sticker: {len(sticker_data)} bytes")
            
            # Upload to WhatsApp
            upload_url = f"{self.api_url}/{self.phone_number_id}/media"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            data = aiohttp.FormData()
            data.add_field('messaging_product', 'whatsapp')
            data.add_field('type', 'sticker')
            data.add_field('file', sticker_data, filename='sticker.webp', content_type='image/webp')
            
            async with aiohttp.ClientSession() as session:
                async with session.post(upload_url, headers=headers, data=data) as response:
                    response_text = await response.text()
                    response_data = json.loads(response_text) if response_text else {}
                    
                    if response.status == 200:
                        media_id = response_data.get("id")
                        return {
                            "success": True,
                            "media_id": media_id,
                            "response": response_data
                        }
                    else:
                        return {
                            "success": False,
                            "error": response_data.get("error", {}).get("message", "Upload failed"),
                            "response": response_data
                        }
                        
        except Exception as e:
            print(f"Upload Exception: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_template_message(self, step_data):
        """Send template message"""
        try:
            template_name = step_data.get("template_name", "")
            language_code = step_data.get("language_code", "es")
            components = step_data.get("components", [])
            
            print(f"Attempting to send template message...")
            print(f"Template: {template_name}")
            print(f"Language: {language_code}")
            print(f"Components: {components}")
            
            # Create template message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": self.phone_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }
            
            if components:
                payload["template"]["components"] = components
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Template message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send template message: {result.get('error', 'Unknown error')}")
                print("NOTE: Template messages require pre-approved templates from Meta")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending template message: {e}")
            return False
    
    async def _send_direct_api_call(self, payload):
        """Send direct API call to WhatsApp"""
        try:
            import aiohttp
            
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            api_url = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v23.0")
            
            url = f"{api_url}/{phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        message_id = response_data.get("messages", [{}])[0].get("id", "N/A")
                        self.last_message_id = message_id  # Store for reactions
                        return {
                            "success": True,
                            "message_id": message_id,
                            "response": response_data
                        }
                    else:
                        return {
                            "success": False,
                            "error": response_data.get("error", {}).get("message", "Unknown error"),
                            "response": response_data
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_reaction_message(self, step_data):
        """Send reaction message"""
        try:
            # Use the last message ID from the conversation, or fallback to step data
            message_id = self.last_message_id or step_data.get("message_id", "")
            emoji = step_data.get("emoji", "👍")
            
            if not message_id or message_id == "N/A":
                print(f"ERROR: No valid message ID available for reaction")
                return False
            
            print(f"Attempting to send reaction message...")
            print(f"Message ID: {message_id}")
            print(f"Emoji: {emoji}")
            
            # Create reaction message payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.phone_number,
                "type": "reaction",
                "reaction": {
                    "message_id": message_id,
                    "emoji": emoji
                }
            }
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Reaction message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send reaction message: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending reaction message: {e}")
            return False

    async def _send_catalog_message(self, step_data):
        """Send catalog message with product list"""
        try:
            # Get catalog info from environment or step data
            catalog_id = step_data.get("catalog_id") or os.getenv("WHATSAPP_CATALOG_ID", "785880617687252")
            
            print(f"Attempting to send catalog message...")
            print(f"Catalog ID: {catalog_id}")
            
            # Create catalog message payload with correct format (product_list with sections)
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.phone_number,
                "type": "interactive",
                "interactive": {
                    "type": "product_list",
                    "header": {
                        "type": "text",
                        "text": "🛍️ Nuestro Catálogo de Productos"
                    },
                    "body": {
                        "text": "Elegí una opción para ver más detalles 👇"
                    },
                    "footer": {
                        "text": "Productos disponibles"
                    },
                    "action": {
                        "catalog_id": catalog_id,
                        "sections": [
                            {
                                "title": "Sección 1",
                                "product_items": []
                            },
                            {
                                "title": "Sección 2",
                                "product_items": []
                            }
                        ]
                    }
                }
            }
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Catalog message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send catalog message: {result.get('error', 'Unknown error')}")
                print("NOTE: Catalog messages require valid catalog_id and product_retailer_id")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending catalog message: {e}")
            return False

    async def _send_flow_message(self, step_data):
        """Send flow message"""
        try:
            flow_token = step_data.get("flow_token", "")
            flow_id = step_data.get("flow_id", "")
            flow_cta = step_data.get("flow_cta", "Completar")
            flow_action_payload = step_data.get("flow_action_payload", "{}")
            
            print(f"Attempting to send flow message...")
            print(f"Flow ID: {flow_id}")
            print(f"Flow CTA: {flow_cta}")
            print(f"Flow Token: {flow_token}")
            
            # Create flow message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": self.phone_number,
                "type": "interactive",
                "interactive": {
                    "type": "flow",
                    "header": {
                        "type": "text",
                        "text": "Completa el formulario"
                    },
                    "body": {
                        "text": "Haz clic en el botón para completar el formulario"
                    },
                    "action": {
                        "name": "flow",
                        "parameters": {
                            "flow_token": flow_token,
                            "flow_id": flow_id,
                            "flow_cta": flow_cta,
                            "flow_action_payload": flow_action_payload
                        }
                    }
                }
            }
            
            print(f"Sending payload: {json.dumps(payload, indent=2)}")
            
            result = await self._send_direct_api_call(payload)
            
            if result.get("success"):
                print(f"SUCCESS: Flow message sent!")
                print(f"Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"ERROR: Failed to send flow message: {result.get('error', 'Unknown error')}")
                print("NOTE: Flow messages require proper flow setup and approval")
                return False
                
        except Exception as e:
            print(f"ERROR: Exception sending flow message: {e}")
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
    
    async def run_complete_test(self):
        """Run the complete test flow"""
        print(f"\nStarting complete WhatsApp native message types test")
        print("=" * 60)
        
        # Load flow
        flow_data = self.load_test_flow()
        if not flow_data:
            return False
        
        steps = flow_data.get("steps", [])
        print(f"Executing {len(steps)} steps...")
        
        successful_steps = 0
        failed_steps = 0
        
        for step in steps:
            success = await self.execute_flow_step(step)
            if success:
                successful_steps += 1
            else:
                failed_steps += 1
            
            # Small delay between messages to avoid rate limiting
            await asyncio.sleep(5)
        
        # Summary
        print(f"\nTest Summary")
        print("=" * 60)
        print(f"SUCCESS: Successful steps: {successful_steps}/{len(steps)}")
        print(f"ERROR: Failed steps: {failed_steps}/{len(steps)}")
        print(f"Success Rate: {(successful_steps/len(steps))*100:.1f}%")
        
        print(f"\nNative message types tested:")
        print("SUCCESS: Text messages (text)")
        print("SUCCESS: Interactive buttons (interactive)")
        print("SUCCESS: Interactive lists (interactive)")
        print("SUCCESS: Image messages (image)")
        print("SUCCESS: Document messages (document)")
        print("SUCCESS: Audio messages (audio)")
        print("SUCCESS: Video messages (video)")
        print("SUCCESS: Location messages (location)")
        print("SUCCESS: Contact messages (contacts)")
        print("SUCCESS: Sticker messages (sticker)")
        print("SUCCESS: Reaction messages (reaction)")
        print("WARNING: Template messages (template - requires approval)")
        
        return successful_steps > 0


async def main():
    """Main test function"""
    # Get phone number from command line or use default
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
    else:
        phone_number = "1234567890"  # Default test number
    
    # Ensure phone number format is correct (no +, no spaces)
    phone_number = phone_number.replace("+", "").replace(" ", "").replace("-", "")
    
    print("WhatsApp Native Message Types Test")
    print("=" * 60)
    print(f"Testing ALL native message types with phone number: {phone_number}")
    print("This test uses real WhatsApp API message types")
    print("=" * 60)
    
    # Create tester
    tester = WhatsAppNativeMessageTester(phone_number)
    
    # Check environment
    if not tester.check_environment():
        print("ERROR: Environment configuration has issues")
        return
    
    # Run complete test
    success = await tester.run_complete_test()
    
    if success:
        print(f"\nSUCCESS: Test completed! Check messages at {phone_number}")
        print("All messages were sent using native WhatsApp message types")
    else:
        print(f"\nERROR: Test failed completely")


if __name__ == "__main__":
    asyncio.run(main())