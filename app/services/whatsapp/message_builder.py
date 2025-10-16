"""
WhatsApp Message Types Service
Handles all types of WhatsApp Business API messages
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

from app.services.shared.config import get_data_config
from app.services.shared.validation import get_message_validator

logger = logging.getLogger(__name__)


class WhatsAppMessageBuilder:
    """Builder class for creating different types of WhatsApp messages"""
    
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.message_data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text"
        }
    
    def text_message(self, text: str) -> Dict[str, Any]:
        """Create a simple text message"""
        # Debug: check if text is actually a string
        if not isinstance(text, str):
            print(f"DEBUG: text is not a string, it's {type(text)}: {text}")
            text = str(text)
        
        return {
            "messaging_product": "whatsapp",
            "to": self.phone_number,
            "type": "text",
            "text": {"body": text}
        }
    
    def interactive_button_message(self, body_text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Create an interactive message with buttons
        
        Args:
            body_text: Main text content
            buttons: List of button dictionaries with 'id' and 'title' keys
        """
        if len(buttons) > 3:
            raise ValueError("WhatsApp allows maximum 3 buttons per message")
        
        button_components = []
        for button in buttons:
            button_components.append({
                "type": "reply",
                "reply": {
                    "id": button["id"],
                    "title": button["title"]
                }
            })
        
        return {
            "messaging_product": "whatsapp",
            "to": self.phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {
                    "buttons": button_components
                }
            }
        }
    
    def interactive_list_message(self, body_text: str, button_text: str, 
                                sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create an interactive list message
        
        Args:
            body_text: Main text content
            button_text: Text for the list button
            sections: List of sections with 'title' and 'rows' keys
        """
        return {
            "messaging_product": "whatsapp",
            "to": self.phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body_text},
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
    
    def media_message(self, media_type: str, media_url: str, 
                     caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a media message (image, video, audio, document)
        
        Args:
            media_type: Type of media (image, video, audio, document)
            media_url: URL of the media file
            caption: Optional caption text
        """
        message = {
            "messaging_product": "whatsapp",
            "to": self.phone_number,
            "type": media_type,
            media_type: {"link": media_url}
        }
        
        if caption and media_type in ["image", "video", "document"]:
            message[media_type]["caption"] = caption
        
        return message
    
    def template_message(self, template_name: str, language_code: str = "es",
                        components: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create a template message
        
        Args:
            template_name: Name of the WhatsApp template
            language_code: Language code (default: es)
            components: Optional template components
        """
        message = {
            "messaging_product": "whatsapp",
            "to": self.phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        
        if components:
            message["template"]["components"] = components
        
        return message
    
    def location_message(self, latitude: float, longitude: float, 
                        name: Optional[str] = None, address: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a location message
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            name: Optional location name
            address: Optional location address
        """
        location_data = {
            "latitude": latitude,
            "longitude": longitude
        }
        
        if name:
            location_data["name"] = name
        if address:
            location_data["address"] = address
        
        return {
            "messaging_product": "whatsapp",
            "to": self.phone_number,
            "type": "location",
            "location": location_data
        }
    
    def contact_message(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a contact message
        
        Args:
            contacts: List of contact dictionaries with name, phones, etc.
        """
        return {
            "messaging_product": "whatsapp",
            "to": self.phone_number,
            "type": "contacts",
            "contacts": contacts
        }
    
    def sticker_message(self, sticker_id: str) -> Dict[str, Any]:
        """
        Create a sticker message
        
        Args:
            sticker_id: ID of the sticker
        """
        return {
            "messaging_product": "whatsapp",
            "to": self.phone_number,
            "type": "sticker",
            "sticker": {"id": sticker_id}
        }
    
    def catalog_message(self, catalog_id: str, product_sections: List[Dict[str, Any]], 
                       header_text: str = None, body_text: str = None, footer_text: str = None) -> Dict[str, Any]:
        """
        Create a native WhatsApp catalog message with product list
        
        Args:
            catalog_id: WhatsApp catalog ID
            product_sections: List of sections (REQUIRED - no default hardcoded data)
            header_text: Header text for the message (default: "🛍️ Nuestro Catálogo de Productos")
            body_text: Body text for the message (default: "Elegí una opción para ver más detalles 👇")
            footer_text: Footer text for the message (default: "Productos disponibles")
        """
        if not product_sections:
            # Return error message instead of hardcoded data
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.phone_number,
                "type": "text",
                "text": {"body": "❌ Error: No hay productos disponibles en el catálogo. Por favor, contacta con soporte."}
            }
        
        # Set default values if not provided
        header_text = header_text or "🛍️ Nuestro Catálogo de Productos"
        body_text = body_text or "Elegí una opción para ver más detalles 👇"
        footer_text = footer_text or "Productos disponibles"
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.phone_number,
            "type": "interactive",
            "interactive": {
                "type": "product_list",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "catalog_id": catalog_id,
                    "sections": product_sections
                }
            }
        }
    
    def create_product_section(self, title: str, product_retailer_ids: List[str]) -> Dict[str, Any]:
        """
        Helper method to create a product section for catalog messages
        
        Args:
            title: Section title
            product_retailer_ids: List of product retailer IDs
        """
        return {
            "title": title,
            "product_items": [
                {"product_retailer_id": product_id} 
                for product_id in product_retailer_ids
            ]
        }


class WhatsAppMessageTemplates:
    """Predefined message templates for common business scenarios"""
    
    def __init__(self):
        self.data_config = get_data_config()
        self.validator = get_message_validator()
    
    def welcome_message(self, company_name: str) -> Dict[str, str]:
        """Generate welcome message with buttons"""
        return {
            "body": f"¡Hola! Bienvenido a {company_name}. ¿En qué puedo ayudarte hoy?",
            "buttons": [
                {"id": "products", "title": "Ver Productos"},
                {"id": "services", "title": "Servicios"},
                {"id": "contact", "title": "Contacto"}
            ]
        }
    
    def product_catalog_message(self) -> Dict[str, Any]:
        """Generate product catalog message with validation"""
        validation = self.validator.validate_catalog_message("products")
        
        if not validation["valid"]:
            return {
                "type": "text",
                "body": validation["fallback_message"]
            }
        
        products = validation["data"]
        sections = [{
            "title": "Productos Disponibles",
            "rows": []
        }]
        
        for product in products[:10]:  # WhatsApp limit
            sections[0]["rows"].append({
                "id": f"product_{product['id']}",
                "title": product["name"],
                "description": f"${product['price']}"
            })
        
        return {
            "type": "list",
            "body": "Aquí tienes nuestros productos disponibles:",
            "button_text": "Ver Productos",
            "sections": sections
        }
    
    def native_catalog_message(self, catalog_id: str, product_sections: List[Dict[str, Any]] = None,
                              header_text: str = None, body_text: str = None, footer_text: str = None) -> Dict[str, Any]:
        """
        Generate native WhatsApp catalog message
        
        Args:
            catalog_id: WhatsApp catalog ID
            product_sections: List of product sections (REQUIRED - no default hardcoded data)
            header_text: Header text (default: "🛍️ Nuestro Catálogo de Productos")
            body_text: Body text (default: "Elegí una opción para ver más detalles 👇")
            footer_text: Footer text (default: "Productos disponibles")
        """
        if product_sections is None or not product_sections:
            return {
                "type": "text",
                "body": "❌ Error: No hay productos disponibles en el catálogo. Por favor, contacta con soporte."
            }
        
        # Set default values if not provided
        header_text = header_text or "🛍️ Nuestro Catálogo de Productos"
        body_text = body_text or "Elegí una opción para ver más detalles 👇"
        footer_text = footer_text or "Productos disponibles"
        
        return {
            "type": "catalog",
            "catalog_id": catalog_id,
            "product_sections": product_sections,
            "header_text": header_text,
            "body_text": body_text,
            "footer_text": footer_text
        }
    
    def service_menu_message(self) -> Dict[str, Any]:
        """Generate service menu message with validation"""
        validation = self.validator.validate_catalog_message("services")
        
        if not validation["valid"]:
            return {
                "type": "text",
                "body": validation["fallback_message"]
            }
        
        services = validation["data"]
        sections = [{
            "title": "Servicios Disponibles",
            "rows": []
        }]
        
        for service in services[:10]:  # WhatsApp limit
            sections[0]["rows"].append({
                "id": f"service_{service['id']}",
                "title": service["name"],
                "description": service.get("description", "")
            })
        
        return {
            "type": "list",
            "body": "Estos son nuestros servicios:",
            "button_text": "Ver Servicios",
            "sections": sections
        }
    
    def contact_info_message(self) -> str:
        """Generate contact information message with validation"""
        validation = self.validator.validate_company_info()
        
        if not validation["valid"]:
            return validation["fallback_message"]
        
        company_info = validation["data"]
        return f"""
📞 *Información de Contacto*

🏢 *Empresa:* {company_info.get('name', 'N/A')}
📱 *Teléfono:* {company_info.get('phone', 'N/A')}
📧 *Email:* {company_info.get('email', 'N/A')}
📍 *Dirección:* {company_info.get('address', 'N/A')}
🌐 *Web:* {company_info.get('website', 'N/A')}

¿Necesitas más información?
        """.strip()
    
    def order_confirmation_message(self, order_data: Dict[str, Any]) -> str:
        """Generate order confirmation message"""
        return f"""
✅ *Pedido Confirmado*

📋 *Número de Pedido:* {order_data.get('order_id', 'N/A')}
📅 *Fecha:* {order_data.get('date', 'N/A')}
💰 *Total:* ${order_data.get('total', 'N/A')}
🚚 *Estado:* {order_data.get('status', 'Procesando')}

¡Gracias por tu compra!
        """.strip()
    
    def appointment_confirmation_message(self, appointment_data: Dict[str, Any]) -> str:
        """Generate appointment confirmation message"""
        return f"""
📅 *Cita Confirmada*

👤 *Cliente:* {appointment_data.get('client_name', 'N/A')}
📅 *Fecha:* {appointment_data.get('date', 'N/A')}
⏰ *Hora:* {appointment_data.get('time', 'N/A')}
📍 *Ubicación:* {appointment_data.get('location', 'N/A')}
📝 *Servicio:* {appointment_data.get('service', 'N/A')}

¡Te esperamos!
        """.strip()


class WhatsAppMessageSender:
    """Service for sending WhatsApp messages through the API"""
    
    def __init__(self, whatsapp_service):
        self.whatsapp_service = whatsapp_service
    
    def send_text(self, phone_number: str, text: str) -> Dict[str, Any]:
        """Send a simple text message"""
        import asyncio
        builder = WhatsAppMessageBuilder(phone_number)
        message = builder.text_message(text)
        return asyncio.run(self.whatsapp_service.send_message(phone_number, message))
    
    def send_buttons(self, phone_number: str, text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send an interactive button message"""
        import asyncio
        builder = WhatsAppMessageBuilder(phone_number)
        message = builder.interactive_button_message(text, buttons)
        return asyncio.run(self.whatsapp_service.send_message(phone_number, message))
    
    def send_list(self, phone_number: str, text: str, button_text: str, 
                  sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send an interactive list message"""
        import asyncio
        builder = WhatsAppMessageBuilder(phone_number)
        message = builder.interactive_list_message(text, button_text, sections)
        return asyncio.run(self.whatsapp_service.send_message(phone_number, message))
    
    def send_media(self, phone_number: str, media_type: str, media_url: str, 
                   caption: Optional[str] = None) -> Dict[str, Any]:
        """Send a media message"""
        builder = WhatsAppMessageBuilder(phone_number)
        message = builder.media_message(media_type, media_url, caption)
        return self.whatsapp_service.send_message(phone_number, message)
    
    def send_template(self, phone_number: str, template_name: str, 
                      language_code: str = "es", components: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Send a template message"""
        builder = WhatsAppMessageBuilder(phone_number)
        message = builder.template_message(template_name, language_code, components)
        return self.whatsapp_service.send_message(phone_number, message)
    
    def send_location(self, phone_number: str, latitude: float, longitude: float, 
                      name: Optional[str] = None, address: Optional[str] = None) -> Dict[str, Any]:
        """Send a location message"""
        builder = WhatsAppMessageBuilder(phone_number)
        message = builder.location_message(latitude, longitude, name, address)
        return self.whatsapp_service.send_message(phone_number, message)
    
    def send_contact(self, phone_number: str, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send a contact message"""
        builder = WhatsAppMessageBuilder(phone_number)
        message = builder.contact_message(contacts)
        return self.whatsapp_service.send_message(phone_number, message)
    
    def send_sticker(self, phone_number: str, sticker_id: str) -> Dict[str, Any]:
        """Send a sticker message"""
        builder = WhatsAppMessageBuilder(phone_number)
        message = builder.sticker_message(sticker_id)
        return self.whatsapp_service.send_message(phone_number, message)


# Factory function to create message sender
def create_message_sender(whatsapp_service) -> WhatsAppMessageSender:
    """Create a WhatsApp message sender instance"""
    return WhatsAppMessageSender(whatsapp_service)


# Factory function to create message templates
def create_message_templates() -> WhatsAppMessageTemplates:
    """Create a WhatsApp message templates instance"""
    return WhatsAppMessageTemplates()
