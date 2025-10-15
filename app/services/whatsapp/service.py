"""
Servicio para integración con WhatsApp Business API
"""
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.config import settings
from app.core.logging_config import whatsapp_logger
from app.core.error_handling import WhatsAppException, handle_errors
from app.services.business.conversation import conversation_manager, ConversationState
from app.services.whatsapp.persistence import get_whatsapp_persistence_service
from app.services.whatsapp.message_builder import create_message_sender, create_message_templates
from app.services.flows.builder import MessageType
from app.utils.helpers import (
    get_current_utc_time,
    parse_timestamp_to_utc,
    format_timestamp_for_logging
)

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Servicio para manejar integración con WhatsApp Business API"""
    
    def __init__(self):
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_url = settings.WHATSAPP_API_URL
        self.verify_token = settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN
        self.message_sender = create_message_sender(self)
        self.message_templates = create_message_templates()
        self._flow_service = None
    
    def get_flow_service(self, persistence_service):
        """Get or create WhatsAppFlowService instance"""
        if self._flow_service is None:
            from app.services.flows.service import WhatsAppFlowService
            self._flow_service = WhatsAppFlowService(self, persistence_service)
        return self._flow_service
    
    @handle_errors("WHATSAPP_SEND_ERROR")
    async def send_message(
        self, 
        to: str, 
        message: str, 
        message_type: str = "text",
        **kwargs
    ) -> Dict[str, Any]:
        """Send message through WhatsApp Business API"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Build payload based on message type
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": message_type
            }
            
            if message_type == "text":
                payload["text"] = {"body": message}
            elif message_type == "image":
                image_url = kwargs.get("image_url", "")
                caption = kwargs.get("caption", message)  # Use message as caption if no caption provided
                payload["image"] = {"link": image_url}
                if caption:
                    payload["image"]["caption"] = caption
            elif message_type == "document":
                document_url = kwargs.get("document_url", "")
                filename = kwargs.get("filename", "document.pdf")
                caption = kwargs.get("caption", message)
                payload["document"] = {
                    "link": document_url,
                    "filename": filename
                }
                if caption:
                    payload["document"]["caption"] = caption
            elif message_type == "audio":
                audio_url = kwargs.get("audio_url", "")
                payload["audio"] = {"link": audio_url}
            elif message_type == "video":
                video_url = kwargs.get("video_url", "")
                caption = kwargs.get("caption", message)
                payload["video"] = {"link": video_url}
                if caption:
                    payload["video"]["caption"] = caption
            elif message_type == "location":
                latitude = kwargs.get("latitude", 0)
                longitude = kwargs.get("longitude", 0)
                name = kwargs.get("name", "")
                address = kwargs.get("address", "")
                payload["location"] = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "name": name,
                    "address": address
                }
            elif message_type == "contacts":
                contacts = kwargs.get("contacts", [])
                payload["contacts"] = contacts
            elif message_type == "catalog":
                # Catalog message - use interactive product_list format
                catalog_id = kwargs.get("catalog_id", "")
                header_text = kwargs.get("header_text", "🛍️ Nuestro Catálogo de Productos")
                body_text = kwargs.get("body_text", "Elegí una opción para ver más detalles 👇")
                footer_text = kwargs.get("footer_text", "Productos disponibles")
                sections = kwargs.get("sections", [])
                
                # Validate catalog_id
                if not catalog_id:
                    logger.error("Catalog ID is required for catalog messages")
                    return {
                        "success": False,
                        "error": "Catalog ID is required for catalog messages"
                    }
                
                # Validate sections
                if not sections or not any(section.get("product_items") for section in sections):
                    logger.error("Catalog sections with product_items are required")
                    return {
                        "success": False,
                        "error": "Catalog sections with product_items are required"
                    }
                
                payload["type"] = "interactive"
                payload["interactive"] = {
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
                        "sections": sections
                    }
                }
            else:
                # Default to text if unknown type
                payload["text"] = {"body": message}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        message_id = result.get("messages", [{}])[0].get("id")
                        whatsapp_logger.log_message_sent(message_id, to, True)
                        
                        # Marcar que se envió un mensaje desde la API
                        try:
                            from app.services.message_processor import message_processor
                            message_processor.mark_api_message_sent(to)
                        except Exception as e:
                            logger.warning(f"Error marcando mensaje API: {e}")
                        
                        return {
                            "success": True,
                            "message_id": message_id,
                            "response": result
                        }
                    else:
                        whatsapp_logger.log_message_sent("unknown", to, False, str(result))
                        raise WhatsAppException(
                            f"Error enviando mensaje: {result}",
                            "SEND_MESSAGE_FAILED",
                            phone_number=to
                        )
                        
        except WhatsAppException:
            raise
        except Exception as e:
            whatsapp_logger.log_error(e, {"phone_number": to, "message_type": message_type})
            logger.error(f"Error inesperado enviando mensaje a {to}: {str(e)}")
            raise WhatsAppException(
                f"Error inesperado enviando mensaje: {str(e)}",
                "SEND_MESSAGE_UNEXPECTED_ERROR",
                phone_number=to
            )
    
    async def send_template_message(
        self, 
        to: str, 
        template_name: str, 
        language_code: str = "es",
        components: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Enviar mensaje de plantilla
        
        Args:
            to: Número de teléfono del destinatario
            template_name: Nombre de la plantilla
            language_code: Código de idioma
            components: Componentes de la plantilla
        
        Returns:
            Dict con respuesta de la API
        """
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"Plantilla enviada exitosamente a {to}")
                        return {
                            "success": True,
                            "message_id": result.get("messages", [{}])[0].get("id"),
                            "response": result
                        }
                    else:
                        logger.error(f"Error enviando plantilla: {result}")
                        return {
                            "success": False,
                            "error": result,
                            "status_code": response.status
                        }
                        
        except Exception as e:
            logger.error(f"Excepción enviando plantilla a {to}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @handle_errors("WHATSAPP_SEND_ERROR")
    async def send_interactive_message(
        self, 
        to: str, 
        header_text: str,
        body_text: str = None,
        buttons: List[Dict[str, str]] = None,
        button_text: str = None,
        sections: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send interactive message with buttons or list through WhatsApp Business API"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Determine if this is a button or list message
            if sections and button_text:
                # Send list message
                logger.info(f"Sending interactive list message to {to}")
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {
                            "type": "text",
                            "text": header_text
                        },
                        "body": {
                            "text": body_text or "Selecciona una opción:"
                        },
                        "action": {
                            "button": button_text,
                            "sections": sections
                        }
                    }
                }
            else:
                # Send button message
                logger.info(f"Sending interactive button message to {to}")
                
                # Format buttons for WhatsApp API
                formatted_buttons = []
                if buttons:
                    for button in buttons[:3]:  # WhatsApp allows max 3 buttons
                        formatted_buttons.append({
                            "type": "reply",
                            "reply": {
                                "id": button["id"],
                                "title": button["title"]
                            }
                        })
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "header": {
                            "type": "text",
                            "text": header_text
                        },
                        "body": {
                            "text": body_text or "Selecciona una opción:"
                        },
                        "action": {
                            "buttons": formatted_buttons
                        }
                    }
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"Interactive message sent successfully to {to}")
                        
                        # Marcar que se envió un mensaje desde la API
                        try:
                            from app.services.message_processor import message_processor
                            message_processor.mark_api_message_sent(to)
                        except Exception as e:
                            logger.warning(f"Error marcando mensaje interactivo API: {e}")
                        
                        return {
                            "success": True,
                            "message_id": response_data.get("messages", [{}])[0].get("id"),
                            "response": response_data
                        }
                    else:
                        error_info = response_data.get("error", {})
                        error_message = error_info.get("message", "Unknown error")
                        error_code = error_info.get("code", "Unknown code")
                        error_details = error_info.get("error_data", {}).get("details", "No details")
                        
                        logger.error(f"Failed to send interactive message:")
                        logger.error(f"  - Error: {error_message}")
                        logger.error(f"  - Code: {error_code}")
                        logger.error(f"  - Details: {error_details}")
                        logger.error(f"  - Full response: {response_data}")
                        
                        return {
                            "success": False,
                            "error": error_message,
                            "error_code": error_code,
                            "error_details": error_details,
                            "response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Error enviando mensaje interactivo a {to}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook token"""

        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook de WhatsApp verificado exitosamente")
            return challenge
        else:
            logger.warning("Verificación de webhook fallida")
            return None
    
    def parse_webhook_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse incoming webhook data"""
        messages = []
        
        try:
            entries = data.get("entry", [])
            
            for entry in entries:
                changes = entry.get("changes", [])
                
                for change in changes:
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        
                        # Procesar mensajes
                        for message in value.get("messages", []):
                            parsed_message = self._parse_message(message, value)
                            if parsed_message:
                                messages.append(parsed_message)
                        
                        # Procesar estados de mensaje
                        for status in value.get("statuses", []):
                            parsed_status = self._parse_status(status)
                            if parsed_status:
                                messages.append(parsed_status)
                                
        except Exception as e:
            logger.error(f"Error parseando webhook: {str(e)}")
        
        return messages
    
    def _parse_message(self, message: Dict[str, Any], value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse individual message from webhook"""
        try:
            
            from_number = message.get("from")
            message_id = message.get("id")
            timestamp = message.get("timestamp")
            message_type = message.get("type")
            
            # Extraer contenido según el tipo
            content = ""
            media_url = None
            
            if message_type == "text":
                content = message.get("text", {}).get("body", "")
            elif message_type == "interactive":
                # Process interactive messages (buttons, lists)
                interactive_data = message.get("interactive", {})
                interactive_type = interactive_data.get("type")
                
                logger.info(f"Processing interactive message: type={interactive_type}, data={interactive_data}")
                
                if interactive_type == "button_reply":
                    # User clicked a button
                    button_reply = interactive_data.get("button_reply", {})
                    content = button_reply.get("id", "")  # This is the button ID
                    logger.info(f"Button reply: id={content}")
                elif interactive_type == "list_reply":
                    # User selected from a list
                    list_reply = interactive_data.get("list_reply", {})
                    content = list_reply.get("id", "")  # This is the list item ID
                    logger.info(f"List reply: id={content}, full_reply={list_reply}")
                else:
                    content = ""
                    logger.warning(f"Unknown interactive type: {interactive_type}")
            elif message_type == "image":
                media_url = message.get("image", {}).get("id")
                content = message.get("image", {}).get("caption", "")
            elif message_type == "audio":
                media_url = message.get("audio", {}).get("id")
            elif message_type == "document":
                media_url = message.get("document", {}).get("id")
                content = message.get("document", {}).get("caption", "")
            
            # Información del contacto
            contacts = value.get("contacts", [])
            contact_info = {}
            if contacts:
                contact = contacts[0]
                contact_info = {
                    "name": contact.get("profile", {}).get("name", ""),
                    "wa_id": contact.get("wa_id", "")
                }
            
            parsed_message = {
                "type": "message",
                "message_id": message_id,
                "from": from_number,
                "timestamp": parse_timestamp_to_utc(timestamp),  # Usar función utilitaria para mantener UTC
                "message_type": message_type,
                "content": content,
                "media_url": media_url,
                "contact_info": contact_info
            }
            
            return parsed_message
            
        except Exception as e:
            logger.error(f"Error parseando mensaje: {str(e)}")
            return None
    
    def _parse_status(self, status: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse message status from webhook"""
        try:
            message_id = status.get("id")
            status_type = status.get("status")
            timestamp = status.get("timestamp")
            recipient_id = status.get("recipient_id")
            
            return {
                "type": "status",
                "message_id": message_id,
                "status": status_type,
                "timestamp": datetime.fromtimestamp(int(timestamp)),
                "recipient_id": recipient_id
            }
            
        except Exception as e:
            logger.error(f"Error parseando estado: {str(e)}")
            return None
    
    def _send_interactive_response(self, phone_number: str, conversation_state: str, 
                                 contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Send interactive response based on conversation state"""
        try:
            if conversation_state == "initial":
                # Send welcome message with buttons
                welcome_template = self.message_templates.welcome_message(settings.COMPANY_NAME)
                result = self.message_sender.send_buttons(
                    phone_number,
                    welcome_template["body"],
                    welcome_template["buttons"]
                )
                return result
            
            elif conversation_state == "waiting_for_selection":
                # Send product/service menu with validation
                catalog_template = self.message_templates.product_catalog_message()
                
                if catalog_template["type"] == "text":
                    # No products available, send fallback message
                    result = self.message_sender.send_text(phone_number, catalog_template["body"])
                else:
                    # Products available, send list
                    result = self.message_sender.send_list(
                        phone_number,
                        catalog_template["body"],
                        catalog_template["button_text"],
                        catalog_template["sections"]
                    )
                return result
            
            elif conversation_state == "contact_requested":
                # Send contact information with validation
                contact_text = self.message_templates.contact_info_message()
                result = self.message_sender.send_text(phone_number, contact_text)
                return result
            
            else:
                # Default text response
                default_message = "Gracias por tu mensaje. Lo procesaré pronto."
                result = self.message_sender.send_text(phone_number, default_message)
                return result
                
        except Exception as e:
            logger.error(f"Error sending interactive response: {e}")
            # Fallback to simple text
            fallback_message = "Gracias por tu mensaje. Lo procesaré pronto."
            return self.message_sender.send_text(phone_number, fallback_message)
    
    async def process_incoming_message(self, message_data: Dict[str, Any], db_session=None) -> Dict[str, Any]:
        """Process incoming WhatsApp message using active flow system"""
        try:
            from_number = message_data.get("from")
            content = message_data.get("content", "").strip()
            contact_info = message_data.get("contact_info", {})
            
            # Obtener servicio de persistencia
            persistence_service = get_whatsapp_persistence_service(db_session)
            
            # Obtener o crear usuario en base de datos
            user = persistence_service.get_or_create_user(from_number, contact_info)
            
            # Obtener o crear conversación en base de datos
            db_conversation = persistence_service.get_or_create_conversation(
                user_id=user.id,
                conversation_id=f"{from_number}_flow_conversation",
                initial_state="initial"
            )
            
            # Guardar mensaje entrante en base de datos
            inbound_message_data = {
                'message_id': message_data.get('message_id'),
                'direction': 'inbound',
                'message_type': message_data.get('message_type', 'text'),
                'content': content,
                'media_url': message_data.get('media_url'),
                'timestamp': message_data.get('timestamp'),
                'status': 'received',
                'metadata': {
                    'contact_info': contact_info,
                    'raw_message': message_data
                }
            }
            
            saved_message = persistence_service.save_message(db_conversation.id, inbound_message_data)
            
            # Usar el sistema de flows para procesar el mensaje
            flow_service = self.get_flow_service(persistence_service)
            
            # Procesar mensaje con el flow activo
            result = await flow_service.process_message(from_number, content)
            
            if result.get("success"):
                # Si el flow envió una respuesta, guardarla en base de datos
                if result.get("whatsapp_result") and result["whatsapp_result"].get("success"):
                    outbound_message_data = {
                        'message_id': result["whatsapp_result"].get('message_id'),
                        'direction': 'outbound',
                        'message_type': 'text',
                        'content': result.get("message", "Flow response"),
                        'timestamp': datetime.utcnow(),
                        'status': 'sent',
                        'metadata': {
                            'message_type': 'flow_response',
                            'flow_result': result
                        }
                    }
                    
                    persistence_service.save_message(db_conversation.id, outbound_message_data)
                
                return {
                    "success": True,
                    "response_sent": result.get("whatsapp_result", {}).get("success", False),
                    "message": result.get("message", "Flow processed"),
                    "conversation_state": result.get("conversation_state", "active"),
                    "user_id": user.id,
                    "conversation_id": db_conversation.id,
                    "flow_result": result
                }
            else:
                # Si el flow falló, ejecutar el nodo de error del flow
                logger.warning(f"Flow processing failed: {result.get('error')}")
                
                # Intentar ejecutar el nodo de error del flow
                try:
                    from app.services.flows.service import WhatsAppFlowService
                    flow_service = WhatsAppFlowService()
                    
                    # Obtener información del usuario y conversación
                    from_number = message_data.get("from")
                    conversation_id = f"whatsapp_{from_number}"
                    
                    # Ejecutar el nodo de error del flow
                    error_result = await flow_service.execute_error_fallback(
                        conversation_id, 
                        result.get("error", "Error desconocido")
                    )
                    
                    if error_result.get("success"):
                        return {
                            "success": True,
                            "response_sent": True,
                            "message": "Error handled by flow fallback",
                            "conversation_state": "error_handled",
                            "user_id": user.id,
                            "conversation_id": db_conversation.id,
                            "error_handled": True
                        }
                    else:
                        # Si el nodo de error también falla, usar fallback genérico
                        logger.warning(f"Flow error fallback failed: {error_result.get('error')}")
                        return await self._fallback_message_processing(message_data, db_session, user, db_conversation, persistence_service)
                        
                except Exception as error_fallback_error:
                    logger.error(f"Error en fallback del flow: {str(error_fallback_error)}")
                    # Último recurso: usar fallback genérico
                    return await self._fallback_message_processing(message_data, db_session, user, db_conversation, persistence_service)
                    
        except Exception as e:
            logger.error(f"Error procesando mensaje entrante: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _fallback_message_processing(self, message_data: Dict[str, Any], db_session, user, db_conversation, persistence_service) -> Dict[str, Any]:
        """Fallback message processing when flow system fails"""
        try:
            from_number = message_data.get("from")
            content = message_data.get("content", "").lower().strip()
            contact_info = message_data.get("contact_info", {})
            
            # Obtener o crear conversación en memoria (para máquina de estados)
            conversation = conversation_manager.get_or_create_conversation(from_number)
            
            # Determinar si es usuario nuevo
            is_new_user = conversation.message_count == 0
            
            if conversation.state == "initial":
                # Primer mensaje - enviar bienvenida
                conversation.receive_first_message({
                    "user_data": contact_info,
                    "content": content
                })
                
                welcome_message = "¿En qué puedo ayudarte?"
                
                # Enviar mensaje de bienvenida
                send_result = await self.send_message(from_number, welcome_message)
                
                if send_result["success"]:
                    # Guardar mensaje saliente en base de datos
                    outbound_message_data = {
                        'message_id': send_result.get('message_id'),
                        'direction': 'outbound',
                        'message_type': 'text',
                        'content': welcome_message,
                        'timestamp': datetime.utcnow(),
                        'status': 'sent',
                        'metadata': {
                            'message_type': 'welcome_fallback',
                            'is_new_user': is_new_user,
                            'user_name': contact_info.get('name', '')
                        }
                    }
                    
                    persistence_service.save_message(db_conversation.id, outbound_message_data)
                    
                    # Actualizar estado en memoria y base de datos
                    conversation.send_welcome()
                    persistence_service.update_conversation_state(
                        conversation.conversation_id, 
                        conversation.state,
                        {'welcome_sent': True, 'is_new_user': is_new_user}
                    )
                    
                    return {
                        "success": True,
                        "response_sent": True,
                        "message": welcome_message,
                        "conversation_state": conversation.state,
                        "user_id": user.id,
                        "conversation_id": db_conversation.id,
                        "fallback_used": True
                    }
                else:
                    return {
                        "success": False,
                        "error": "Error enviando mensaje de bienvenida de fallback",
                        "details": send_result
                    }
            
            else:
                # Usuario existente - procesar mensaje
                conversation.receive_message({
                    "user_data": contact_info,
                    "content": content
                })
                
                # Por ahora, solo confirmamos que recibimos el mensaje
                confirmation_message = "Gracias por tu mensaje. Lo procesaré pronto."
                
                send_result = await self.send_message(from_number, confirmation_message)
                
                if send_result["success"]:
                    # Guardar mensaje saliente en base de datos
                    outbound_message_data = {
                        'message_id': send_result.get('message_id'),
                        'direction': 'outbound',
                        'message_type': 'text',
                        'content': confirmation_message,
                        'timestamp': datetime.utcnow(),
                        'status': 'sent',
                        'metadata': {
                            'message_type': 'confirmation_fallback',
                            'user_state': conversation.state
                        }
                    }
                    
                    persistence_service.save_message(db_conversation.id, outbound_message_data)
                    
                    # Actualizar estado en memoria y base de datos
                    conversation.send_response()
                    persistence_service.update_conversation_state(
                        conversation.conversation_id, 
                        conversation.state,
                        {'last_response': confirmation_message}
                    )
                    
                    return {
                        "success": True,
                        "response_sent": True,
                        "message": confirmation_message,
                        "conversation_state": conversation.state,
                        "user_id": user.id,
                        "conversation_id": db_conversation.id,
                        "fallback_used": True
                    }
                else:
                    return {
                        "success": False,
                        "error": "Error enviando confirmación de fallback",
                        "details": send_result
                    }
                    
        except Exception as e:
            logger.error(f"Error en procesamiento de fallback: {str(e)}")
            return {
                "success": False,
                "error": f"Error en fallback: {str(e)}"
            }


# Instancia global del servicio
whatsapp_service = WhatsAppService()
