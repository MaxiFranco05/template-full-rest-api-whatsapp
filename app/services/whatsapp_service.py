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
from app.services.message_service import message_service
from app.services.conversation_service import conversation_manager

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Servicio para manejar integración con WhatsApp Business API"""
    
    def __init__(self):
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_url = settings.WHATSAPP_API_URL
        self.verify_token = settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN
    
    @handle_errors("WHATSAPP_SEND_ERROR")
    async def send_message(
        self, 
        to: str, 
        message: str, 
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Enviar mensaje a través de WhatsApp Business API
        
        Args:
            to: Número de teléfono del destinatario
            message: Contenido del mensaje
            message_type: Tipo de mensaje (text, template, etc.)
        
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
                "type": message_type,
                "text": {
                    "body": message
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        message_id = result.get("messages", [{}])[0].get("id")
                        whatsapp_logger.log_message_sent(message_id, to, True)
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
            logger.error(f"Excepción enviando plantilla: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verificar webhook de WhatsApp
        
        Args:
            mode: Modo de verificación
            token: Token de verificación
            challenge: Challenge string
        
        Returns:
            Challenge string si es válido, None si no
        """

        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook de WhatsApp verificado exitosamente")
            return challenge
        else:
            logger.warning("Verificación de webhook fallida")
            return None
    
    def parse_webhook_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parsear datos del webhook de WhatsApp
        
        Args:
            data: Datos del webhook
        
        Returns:
            Lista de mensajes procesados
        """
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
            logger.error(f"Error parseando webhook: {e}")
        
        return messages
    
    def _parse_message(self, message: Dict[str, Any], value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parsear mensaje individual"""
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
            
            return {
                "type": "message",
                "message_id": message_id,
                "from": from_number,
                "timestamp": datetime.fromtimestamp(int(timestamp)),
                "message_type": message_type,
                "content": content,
                "media_url": media_url,
                "contact_info": contact_info
            }
            
        except Exception as e:
            logger.error(f"Error parseando mensaje: {e}")
            return None
    
    def _parse_status(self, status: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parsear estado de mensaje"""
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
            logger.error(f"Error parseando estado: {e}")
            return None
    
    async def process_incoming_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar mensaje entrante y generar respuesta
        
        Args:
            message_data: Datos del mensaje parseado
        
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            from_number = message_data.get("from")
            content = message_data.get("content", "").lower().strip()
            contact_info = message_data.get("contact_info", {})
            
            # Obtener o crear conversación
            conversation = conversation_manager.get_or_create_conversation(from_number)
            
            # Determinar si es usuario nuevo
            is_new_user = conversation.message_count == 0
            
            # Procesar según el estado actual
            if conversation.state.value == "initial":
                # Primer mensaje - enviar bienvenida
                conversation.receive_first_message({
                    "user_data": contact_info,
                    "content": content
                })
                
                welcome_message = message_service.get_welcome_message(
                    is_new_user=is_new_user,
                    user_name=contact_info.get("name", ""),
                    company_name="Cafe API"
                )
                
                # Enviar mensaje de bienvenida
                send_result = await self.send_message(from_number, welcome_message)
                
                if send_result["success"]:
                    conversation.send_welcome()
                    return {
                        "success": True,
                        "response_sent": True,
                        "message": welcome_message,
                        "conversation_state": conversation.state.value
                    }
                else:
                    return {
                        "success": False,
                        "error": "Error enviando mensaje de bienvenida",
                        "details": send_result
                    }
            
            else:
                # Usuario existente - procesar mensaje
                conversation.receive_message({
                    "user_data": contact_info,
                    "content": content
                })
                
                # Por ahora, solo confirmamos que recibimos el mensaje
                confirmation_message = message_service.get_confirmation_message("received")
                
                send_result = await self.send_message(from_number, confirmation_message)
                
                if send_result["success"]:
                    conversation.send_response()
                    return {
                        "success": True,
                        "response_sent": True,
                        "message": confirmation_message,
                        "conversation_state": conversation.state.value
                    }
                else:
                    return {
                        "success": False,
                        "error": "Error enviando confirmación",
                        "details": send_result
                    }
                    
        except Exception as e:
            logger.error(f"Error procesando mensaje entrante: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Instancia global del servicio
whatsapp_service = WhatsAppService()
