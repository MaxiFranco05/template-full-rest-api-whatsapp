"""
Endpoints para webhook de WhatsApp
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, Query
from fastapi.responses import PlainTextResponse
from typing import Dict, Any, Optional
import logging
from app.services.whatsapp.service import whatsapp_service
from app.services.whatsapp.persistence import get_whatsapp_persistence_service
from app.services.business.conversation import conversation_manager
from app.services.message_processor import message_processor
from app.db.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """
    Endpoint para verificar el webhook de WhatsApp
    
    WhatsApp enviará una solicitud GET a este endpoint para verificar
    que el webhook está configurado correctamente.
    """
    try:
        challenge = whatsapp_service.verify_webhook(
            mode=hub_mode,
            token=hub_verify_token,
            challenge=hub_challenge
        )
        
        if challenge:
            logger.info("Webhook verificado exitosamente")
            return PlainTextResponse(content=challenge)
        else:
            logger.warning("Verificación de webhook fallida")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token de verificación inválido"
            )
            
    except Exception as e:
        logger.error(f"Error en verificación de webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/webhook")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para recibir webhooks de WhatsApp
    
    WhatsApp enviará notificaciones a este endpoint cuando:
    - Se reciba un mensaje
    - Cambie el estado de un mensaje enviado
    - Ocurra algún evento relacionado con la cuenta
    
    Los mensajes se procesan usando el MessageProcessor que:
    - Solo procesa mensajes recibidos después de enviar uno desde la API
    - Concatena mensajes consecutivos en un tiempo configurable
    - Filtra mensajes antiguos que llegaron tarde
    """
    try:
        # Obtener datos del webhook
        data = await request.json()
        logger.info(f"Webhook recibido: {data}")
        
        # Parsear datos del webhook
        messages = whatsapp_service.parse_webhook_data(data)
        
        processed_count = 0
        status_updates = 0
        
        # Procesar cada mensaje usando el MessageProcessor
        for message_data in messages:
            if message_data.get("type") == "message":
                # Agregar mensaje al procesador inteligente
                message_processor.add_incoming_message(message_data)
                processed_count += 1
                logger.info(f"Mensaje agregado al procesador para {message_data.get('from')}")
                
            elif message_data.get("type") == "status":
                # Procesar cambio de estado
                logger.info(f"Estado de mensaje actualizado: {message_data}")
                status_updates += 1
                # TODO: Actualizar estado en base de datos
                # await update_message_status(db, message_data)
        
        return {
            "status": "success",
            "messages_added_to_processor": processed_count,
            "status_updates": status_updates,
            "message": f"{processed_count} mensajes agregados al procesador inteligente"
        }
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando webhook"
        )


@router.post("/send-message")
async def send_message(
    to: str,
    message: str,
    message_type: str = "text"
):
    """
    Endpoint para enviar mensaje manualmente (para testing)
    
    Args:
        to: Número de teléfono del destinatario
        message: Contenido del mensaje
        message_type: Tipo de mensaje
    """
    try:
        result = await whatsapp_service.send_message(to, message, message_type)
        
        if result["success"]:
            # Marcar que se envió un mensaje desde la API para este número
            message_processor.mark_api_message_sent(to)
            logger.info(f"Mensaje API enviado marcado para {to}")
            
            return {
                "status": "success",
                "message_id": result.get("message_id"),
                "message": "Mensaje enviado exitosamente",
                "api_message_marked": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error enviando mensaje: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/conversations")
async def get_conversations():
    """
    Obtener estadísticas de conversaciones activas
    """
    try:
        stats = conversation_manager.get_conversation_stats()
        
        # Obtener detalles de conversaciones activas
        active_conversations = []
        for conv_id, conversation in conversation_manager.conversations.items():
            if conversation.state.value in ["active", "processing", "waiting_response"]:
                active_conversations.append({
                    "conversation_id": conv_id,
                    "state": conversation.state.value,
                    "message_count": conversation.message_count,
                    "last_activity": conversation.last_activity.isoformat(),
                    "is_new_user": conversation.is_new_user
                })
        
        return {
            "stats": stats,
            "active_conversations": active_conversations
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo conversaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/conversations/{conversation_id}/end")
async def end_conversation(conversation_id: str):
    """
    Terminar una conversación específica
    """
    try:
        if conversation_id in conversation_manager.conversations:
            conversation = conversation_manager.conversations[conversation_id]
            conversation.end_conversation()
            
            return {
                "status": "success",
                "message": f"Conversación {conversation_id} terminada"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversación no encontrada"
            )
            
    except Exception as e:
        logger.error(f"Error terminando conversación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/cleanup")
async def cleanup_conversations():
    """
    Limpiar conversaciones expiradas
    """
    try:
        conversation_manager.cleanup_expired_conversations()
        
        return {
            "status": "success",
            "message": "Conversaciones expiradas limpiadas"
        }
        
    except Exception as e:
        logger.error(f"Error limpiando conversaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/message-processor/status")
async def get_message_processor_status():
    """
    Obtener estado del procesador de mensajes
    """
    try:
        status = message_processor.get_all_buffers_status()
        
        return {
            "status": "success",
            "processor_config": {
                "processing_delay_seconds": message_processor.processing_delay,
                "concatenation_enabled": message_processor.concatenation_enabled,
                "time_tolerance_seconds": message_processor.time_tolerance
            },
            "buffers": status,
            "total_buffers": len(status)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del procesador: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/message-processor/status/{phone_number}")
async def get_message_processor_status_for_number(phone_number: str):
    """
    Obtener estado del procesador de mensajes para un número específico
    """
    try:
        status = message_processor.get_buffer_status(phone_number)
        
        return {
            "status": "success",
            "phone_number": phone_number,
            "buffer_status": status
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del procesador para {phone_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/message-processor/clear/{phone_number}")
async def clear_message_buffer(phone_number: str):
    """
    Limpiar buffer de mensajes para un número específico
    """
    try:
        cleared = message_processor.clear_buffer(phone_number)
        
        if cleared:
            return {
                "status": "success",
                "message": f"Buffer limpiado para {phone_number}"
            }
        else:
            return {
                "status": "not_found",
                "message": f"No hay buffer para {phone_number}"
            }
        
    except Exception as e:
        logger.error(f"Error limpiando buffer para {phone_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/message-processor/clear-all")
async def clear_all_message_buffers():
    """
    Limpiar todos los buffers de mensajes
    """
    try:
        cleared_count = message_processor.clear_all_buffers()
        
        return {
            "status": "success",
            "message": f"{cleared_count} buffers limpiados"
        }
        
    except Exception as e:
        logger.error(f"Error limpiando todos los buffers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
