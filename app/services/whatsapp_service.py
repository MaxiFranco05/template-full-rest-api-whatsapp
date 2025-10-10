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
from app.services.conversation_service import conversation_manager, ConversationState
from app.services.whatsapp_persistence_service import get_whatsapp_persistence_service

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
            # Log de desarrollo: mostrar error detallado del envío
            if settings.DEBUG:
                logger.error(f"[DESARROLLO] Error enviando mensaje - Destinatario: {to}")
                logger.error(f"[DESARROLLO] Error enviando mensaje - Tipo: {message_type}")
                logger.error(f"[DESARROLLO] Error enviando mensaje - Payload: {json.dumps(payload, indent=2, ensure_ascii=False, default=str)}")
                logger.error(f"[DESARROLLO] Error enviando mensaje - Excepción completa: {str(e)}")
                logger.error(f"[DESARROLLO] Error enviando mensaje - Tipo de excepción: {type(e).__name__}")
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
            # Log de desarrollo: mostrar error detallado del envío de plantilla
            if settings.DEBUG:
                logger.error(f"[DESARROLLO] Error enviando plantilla - Destinatario: {to}")
                logger.error(f"[DESARROLLO] Error enviando plantilla - Nombre: {template_name}")
                logger.error(f"[DESARROLLO] Error enviando plantilla - Idioma: {language_code}")
                logger.error(f"[DESARROLLO] Error enviando plantilla - Payload: {json.dumps(payload, indent=2, ensure_ascii=False, default=str)}")
                logger.error(f"[DESARROLLO] Error enviando plantilla - Excepción completa: {str(e)}")
                logger.error(f"[DESARROLLO] Error enviando plantilla - Tipo de excepción: {type(e).__name__}")
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
            # Log de desarrollo: mostrar detalles de verificación exitosa
            if settings.DEBUG:
                logger.info(f"[DESARROLLO] Webhook verificado - Modo: {mode}")
                logger.info(f"[DESARROLLO] Webhook verificado - Token recibido: {token}")
                logger.info(f"[DESARROLLO] Webhook verificado - Token esperado: {self.verify_token}")
                logger.info(f"[DESARROLLO] Webhook verificado - Challenge: {challenge}")
            return challenge
        else:
            logger.warning("Verificación de webhook fallida")
            # Log de desarrollo: mostrar detalles de verificación fallida
            if settings.DEBUG:
                logger.warning(f"[DESARROLLO] Webhook fallido - Modo: {mode}")
                logger.warning(f"[DESARROLLO] Webhook fallido - Token recibido: {token}")
                logger.warning(f"[DESARROLLO] Webhook fallido - Token esperado: {self.verify_token}")
                logger.warning(f"[DESARROLLO] Webhook fallido - Challenge: {challenge}")
            return None
    
    def parse_webhook_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parsear datos del webhook de WhatsApp
        
        Args:
            data: Datos del webhook
        
        Returns:
            Lista de mensajes procesados
        """
        # Log de desarrollo: mostrar JSON completo del webhook
        if settings.DEBUG:
            logger.info(f"[DESARROLLO] Webhook recibido completo: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
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
            # Log de desarrollo: mostrar error detallado del webhook
            if settings.DEBUG:
                logger.error(f"[DESARROLLO] Error parseando webhook - Datos recibidos: {json.dumps(data, indent=2, ensure_ascii=False, default=str)}")
                logger.error(f"[DESARROLLO] Error parseando webhook - Excepción completa: {str(e)}")
        
        return messages
    
    def _parse_message(self, message: Dict[str, Any], value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parsear mensaje individual"""
        try:
            # Log de desarrollo: mostrar datos del mensaje individual
            if settings.DEBUG:
                logger.info(f"[DESARROLLO] Parseando mensaje individual: {json.dumps(message, indent=2, ensure_ascii=False)}")
                logger.info(f"[DESARROLLO] Datos del value: {json.dumps(value, indent=2, ensure_ascii=False)}")
            
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
            
            parsed_message = {
                "type": "message",
                "message_id": message_id,
                "from": from_number,
                "timestamp": datetime.fromtimestamp(int(timestamp)),
                "message_type": message_type,
                "content": content,
                "media_url": media_url,
                "contact_info": contact_info
            }
            
            # Log de desarrollo: mostrar mensaje parseado final
            if settings.DEBUG:
                logger.info(f"[DESARROLLO] Mensaje parseado final: {json.dumps(parsed_message, indent=2, ensure_ascii=False, default=str)}")
            
            return parsed_message
            
        except Exception as e:
            logger.error(f"Error parseando mensaje: {e}")
            # Log de desarrollo: mostrar error detallado del mensaje
            if settings.DEBUG:
                logger.error(f"[DESARROLLO] Error parseando mensaje - Mensaje original: {json.dumps(message, indent=2, ensure_ascii=False, default=str)}")
                logger.error(f"[DESARROLLO] Error parseando mensaje - Value original: {json.dumps(value, indent=2, ensure_ascii=False, default=str)}")
                logger.error(f"[DESARROLLO] Error parseando mensaje - Excepción completa: {str(e)}")
                logger.error(f"[DESARROLLO] Error parseando mensaje - Tipo de excepción: {type(e).__name__}")
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
            # Log de desarrollo: mostrar error detallado del estado
            if settings.DEBUG:
                logger.error(f"[DESARROLLO] Error parseando estado - Status original: {json.dumps(status, indent=2, ensure_ascii=False, default=str)}")
                logger.error(f"[DESARROLLO] Error parseando estado - Excepción completa: {str(e)}")
                logger.error(f"[DESARROLLO] Error parseando estado - Tipo de excepción: {type(e).__name__}")
            return None
    
    async def process_incoming_message(self, message_data: Dict[str, Any], db_session=None) -> Dict[str, Any]:
        """
        Procesar mensaje entrante y generar respuesta
        
        Args:
            message_data: Datos del mensaje parseado
            db_session: Sesión de base de datos (opcional)
        
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            # Log de desarrollo: mostrar JSON completo del mensaje
            if settings.DEBUG:
                logger.info(f"[DESARROLLO] Mensaje recibido completo: {json.dumps(message_data, indent=2, ensure_ascii=False, default=str)}")
            
            from_number = message_data.get("from")
            content = message_data.get("content", "").lower().strip()
            contact_info = message_data.get("contact_info", {})
            
            # Obtener servicio de persistencia
            persistence_service = get_whatsapp_persistence_service(db_session)
            
            # Obtener o crear usuario en base de datos
            user = persistence_service.get_or_create_user(from_number, contact_info)
            
            # Obtener o crear conversación en memoria (para máquina de estados)
            conversation = conversation_manager.get_or_create_conversation(from_number)
            
            # Obtener o crear conversación en base de datos
            db_conversation = persistence_service.get_or_create_conversation(
                user_id=user.id,
                conversation_id=conversation.conversation_id,
                initial_state=conversation.state
            )
            
            # Log de desarrollo: mostrar estado de la conversación
            if settings.DEBUG:
                logger.info(f"[DESARROLLO] Estado de conversación - ID: {conversation.conversation_id}")
                logger.info(f"[DESARROLLO] Estado de conversación - Estado actual: {conversation.state}")
                logger.info(f"[DESARROLLO] Estado de conversación - Contador de mensajes: {conversation.message_count}")
                logger.info(f"[DESARROLLO] Estado de conversación - Usuario nuevo: {conversation.is_new_user}")
                logger.info(f"[DESARROLLO] Estado de conversación - Datos del usuario: {json.dumps(conversation.user_data, indent=2, ensure_ascii=False, default=str)}")
            
            # Determinar si es usuario nuevo
            is_new_user = conversation.message_count == 0
            
            # Guardar mensaje entrante en base de datos
            inbound_message_data = {
                'message_id': message_data.get('message_id'),
                'direction': 'inbound',
                'message_type': message_data.get('message_type', 'text'),
                'content': message_data.get('content'),
                'media_url': message_data.get('media_url'),
                'timestamp': message_data.get('timestamp'),
                'status': 'received',
                'metadata': {
                    'contact_info': contact_info,
                    'raw_message': message_data
                }
            }
            
            saved_message = persistence_service.save_message(db_conversation.id, inbound_message_data)
            
            # Procesar según el estado actual
            if conversation.state == "initial":
                # Log de desarrollo: mostrar procesamiento de mensaje inicial
                if settings.DEBUG:
                    logger.info(f"[DESARROLLO] Procesando mensaje inicial - Contenido: '{content}'")
                    logger.info(f"[DESARROLLO] Procesando mensaje inicial - Información de contacto: {json.dumps(contact_info, indent=2, ensure_ascii=False, default=str)}")
                
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
                
                # Log de desarrollo: mostrar mensaje de bienvenida generado
                if settings.DEBUG:
                    logger.info(f"[DESARROLLO] Mensaje de bienvenida generado: '{welcome_message}'")
                    logger.info(f"[DESARROLLO] Mensaje de bienvenida - Usuario nuevo: {is_new_user}")
                    logger.info(f"[DESARROLLO] Mensaje de bienvenida - Nombre del usuario: '{contact_info.get('name', '')}'")
                
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
                            'message_type': 'welcome',
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
                        "conversation_id": db_conversation.id
                    }
                else:
                    return {
                        "success": False,
                        "error": "Error enviando mensaje de bienvenida",
                        "details": send_result
                    }
            
            else:
                # Log de desarrollo: mostrar procesamiento de mensaje de usuario existente
                if settings.DEBUG:
                    logger.info(f"[DESARROLLO] Procesando mensaje de usuario existente - Contenido: '{content}'")
                    logger.info(f"[DESARROLLO] Procesando mensaje de usuario existente - Estado actual: {conversation.state}")
                    logger.info(f"[DESARROLLO] Procesando mensaje de usuario existente - Contador de mensajes: {conversation.message_count}")
                
                # Usuario existente - procesar mensaje
                conversation.receive_message({
                    "user_data": contact_info,
                    "content": content
                })
                
                # Por ahora, solo confirmamos que recibimos el mensaje
                confirmation_message = message_service.get_confirmation_message("received")
                
                # Log de desarrollo: mostrar mensaje de confirmación generado
                if settings.DEBUG:
                    logger.info(f"[DESARROLLO] Mensaje de confirmación generado: '{confirmation_message}'")
                
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
                            'message_type': 'confirmation',
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
                        "conversation_id": db_conversation.id
                    }
                else:
                    return {
                        "success": False,
                        "error": "Error enviando confirmación",
                        "details": send_result
                    }
                    
        except Exception as e:
            logger.error(f"Error procesando mensaje entrante: {e}")
            # Log de desarrollo: mostrar error detallado del procesamiento
            if settings.DEBUG:
                logger.error(f"[DESARROLLO] Error procesando mensaje - Datos del mensaje: {json.dumps(message_data, indent=2, ensure_ascii=False, default=str)}")
                logger.error(f"[DESARROLLO] Error procesando mensaje - Excepción completa: {str(e)}")
                logger.error(f"[DESARROLLO] Error procesando mensaje - Tipo de excepción: {type(e).__name__}")
                logger.error(f"[DESARROLLO] Error procesando mensaje - Traceback: {e.__traceback__}")
            return {
                "success": False,
                "error": str(e)
            }


# Instancia global del servicio
whatsapp_service = WhatsAppService()
