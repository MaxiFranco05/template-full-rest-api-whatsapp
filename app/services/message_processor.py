"""
Servicio para procesamiento inteligente de mensajes WhatsApp
- Solo procesa mensajes recibidos después de enviar uno desde la API
- Concatena mensajes consecutivos en un tiempo configurable
- Filtra mensajes antiguos que llegaron tarde
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class MessageBuffer:
    """Buffer para almacenar mensajes pendientes de procesamiento"""
    phone_number: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    last_api_message_time: Optional[datetime] = None
    processing_task: Optional[asyncio.Task] = None


class MessageProcessor:
    """Procesador inteligente de mensajes WhatsApp"""
    
    def __init__(self):
        self.message_buffers: Dict[str, MessageBuffer] = {}
        self.processing_delay = settings.MESSAGE_PROCESSING_DELAY_SECONDS
        self.concatenation_enabled = settings.MESSAGE_CONCATENATION_ENABLED
        self.time_tolerance = settings.MESSAGE_TIME_TOLERANCE_SECONDS
        
        logger.info(f"[MESSAGE PROCESSOR] Inicializado con delay: {self.processing_delay}s, concatenación: {self.concatenation_enabled}, tolerancia: {self.time_tolerance}s")
    
    def mark_api_message_sent(self, phone_number: str) -> None:
        """Marca que se envió un mensaje desde la API para este número"""
        if phone_number not in self.message_buffers:
            self.message_buffers[phone_number] = MessageBuffer(phone_number=phone_number)
        
        self.message_buffers[phone_number].last_api_message_time = datetime.utcnow()
        logger.info(f"[MESSAGE PROCESSOR] Marcado mensaje API enviado para {phone_number}")
    
    def add_incoming_message(self, message_data: Dict[str, Any]) -> None:
        """Agrega un mensaje entrante al buffer de procesamiento"""
        phone_number = message_data.get("from")
        if not phone_number:
            logger.warning("[MESSAGE PROCESSOR] Mensaje sin número de teléfono, ignorando")
            return
        
        # Crear buffer si no existe
        if phone_number not in self.message_buffers:
            self.message_buffers[phone_number] = MessageBuffer(phone_number=phone_number)
        
        buffer = self.message_buffers[phone_number]
        
        # Verificar si el mensaje es válido para procesar
        if not self._is_message_valid_for_processing(message_data, buffer):
            logger.info(f"[MESSAGE PROCESSOR] Mensaje ignorado para {phone_number} - no hay mensaje API previo")
            return
        
        # Agregar mensaje al buffer
        buffer.messages.append(message_data)
        logger.info(f"[MESSAGE PROCESSOR] Mensaje agregado al buffer para {phone_number}. Total: {len(buffer.messages)}")
        
        # Si no hay tarea de procesamiento activa, crear una nueva
        if buffer.processing_task is None or buffer.processing_task.done():
            buffer.processing_task = asyncio.create_task(
                self._process_messages_after_delay(phone_number)
            )
    
    def _is_message_valid_for_processing(self, message_data: Dict[str, Any], buffer: MessageBuffer) -> bool:
        """Verifica si un mensaje es válido para procesar"""
        phone_number = buffer.phone_number
        
        # Si no hay mensaje API previo, verificar si es un usuario nuevo
        if buffer.last_api_message_time is None:
            # Permitir procesar si es un usuario nuevo (primer mensaje)
            # Esto activará el sistema de bienvenida automática
            logger.info(f"[MESSAGE PROCESSOR] Usuario nuevo detectado para {phone_number} - permitiendo procesamiento")
            return True
        
        # Verificar si el mensaje llegó después del último mensaje API
        message_timestamp = message_data.get("timestamp")
        if isinstance(message_timestamp, datetime):
            message_time = message_timestamp
        else:
            # Si es timestamp Unix, convertir
            try:
                message_time = datetime.fromtimestamp(int(message_timestamp))
            except (ValueError, TypeError):
                logger.warning(f"[MESSAGE PROCESSOR] Timestamp inválido para {phone_number}: {message_timestamp}")
                return False
        
        # Calcular diferencia temporal
        time_diff = (message_time - buffer.last_api_message_time).total_seconds()
        
        # Aplicar tolerancia temporal: permitir mensajes que llegaron hasta X segundos antes del último mensaje API
        # Esto maneja casos donde mensajes llegan ligeramente tarde debido a latencia de red
        tolerance_threshold = -self.time_tolerance  # Negativo porque queremos permitir mensajes "antiguos" hasta cierto punto
        
        is_valid = time_diff >= tolerance_threshold
        
        # Logging detallado para debugging
        logger.info(f"[MESSAGE PROCESSOR] Validación temporal para {phone_number}:")
        logger.info(f"  - Último mensaje API: {buffer.last_api_message_time}")
        logger.info(f"  - Mensaje entrante: {message_time}")
        logger.info(f"  - Diferencia temporal: {time_diff:.2f} segundos")
        logger.info(f"  - Tolerancia: {tolerance_threshold} segundos")
        logger.info(f"  - Válido: {is_valid}")
        
        if not is_valid:
            logger.info(f"[MESSAGE PROCESSOR] Mensaje muy antiguo ignorado para {phone_number} - diferencia: {time_diff:.2f}s (límite: {tolerance_threshold}s)")
        
        return is_valid
    
    async def _process_messages_after_delay(self, phone_number: str) -> None:
        """Procesa mensajes después del delay configurado"""
        try:
            # Esperar el delay configurado
            await asyncio.sleep(self.processing_delay)
            
            buffer = self.message_buffers.get(phone_number)
            if not buffer or not buffer.messages:
                logger.info(f"[MESSAGE PROCESSOR] No hay mensajes para procesar para {phone_number}")
                return
            
            # Procesar mensajes concatenados
            await self._process_concatenated_messages(phone_number, buffer.messages)
            
            # Limpiar buffer después del procesamiento
            buffer.messages.clear()
            buffer.processing_task = None
            
        except Exception as e:
            logger.error(f"[MESSAGE PROCESSOR] Error procesando mensajes para {phone_number}: {e}")
            # Limpiar buffer en caso de error
            if phone_number in self.message_buffers:
                self.message_buffers[phone_number].messages.clear()
                self.message_buffers[phone_number].processing_task = None
    
    async def _process_concatenated_messages(self, phone_number: str, messages: List[Dict[str, Any]]) -> None:
        """Procesa mensajes concatenados como un solo mensaje"""
        if not messages:
            return
        
        logger.info(f"[MESSAGE PROCESSOR] Procesando {len(messages)} mensajes concatenados para {phone_number}")
        
        if self.concatenation_enabled and len(messages) > 1:
            # Concatenar contenido de mensajes
            concatenated_content = self._concatenate_message_content(messages)
            
            # Crear mensaje concatenado
            concatenated_message = {
                "from": phone_number,
                "content": concatenated_content,
                "message_type": "concatenated",
                "timestamp": messages[-1].get("timestamp"),  # Usar timestamp del último mensaje
                "message_id": f"concatenated_{len(messages)}_{messages[-1].get('message_id', '')}",
                "contact_info": messages[-1].get("contact_info", {}),
                "original_messages": messages,
                "concatenation_count": len(messages)
            }
            
            logger.info(f"[MESSAGE PROCESSOR] Mensaje concatenado creado: '{concatenated_content[:100]}...'")
            
            # Procesar mensaje concatenado
            await self._process_single_message(concatenated_message)
            
        else:
            # Procesar mensajes individualmente
            for message in messages:
                await self._process_single_message(message)
    
    def _concatenate_message_content(self, messages: List[Dict[str, Any]]) -> str:
        """Concatena el contenido de múltiples mensajes"""
        contents = []
        
        for message in messages:
            content = message.get("content", "").strip()
            if content:
                contents.append(content)
        
        # Unir con espacios, pero evitar espacios dobles
        concatenated = " ".join(contents)
        
        # Limpiar espacios múltiples
        while "  " in concatenated:
            concatenated = concatenated.replace("  ", " ")
        
        return concatenated.strip()
    
    async def _process_single_message(self, message_data: Dict[str, Any]) -> None:
        """Procesa un mensaje individual"""
        try:
            phone_number = message_data.get("from")
            logger.info(f"[MESSAGE PROCESSOR] Procesando mensaje individual para {phone_number}")
            
            # Importar aquí para evitar import circular
            from app.services.whatsapp.service import whatsapp_service
            from app.db.database import get_db
            from sqlalchemy.orm import Session
            
            # Obtener sesión de base de datos
            db_session = next(get_db())
            
            try:
                # Procesar mensaje usando el servicio existente
                result = await whatsapp_service.process_incoming_message(message_data, db_session)
                
                if result.get("success"):
                    logger.info(f"[MESSAGE PROCESSOR] Mensaje procesado exitosamente para {phone_number}")
                    
                    # Marcar que se envió una respuesta desde la API
                    self.mark_api_message_sent(phone_number)
                else:
                    logger.error(f"[MESSAGE PROCESSOR] Error procesando mensaje para {phone_number}: {result.get('error')}")
                    
            finally:
                db_session.close()
                
        except Exception as e:
            logger.error(f"[MESSAGE PROCESSOR] Error procesando mensaje individual: {e}")
    
    def get_buffer_status(self, phone_number: str) -> Dict[str, Any]:
        """Obtiene el estado del buffer para un número específico"""
        buffer = self.message_buffers.get(phone_number)
        if not buffer:
            return {"exists": False}
        
        return {
            "exists": True,
            "messages_count": len(buffer.messages),
            "last_api_message_time": buffer.last_api_message_time.isoformat() if buffer.last_api_message_time else None,
            "processing_task_active": buffer.processing_task is not None and not buffer.processing_task.done(),
            "processing_delay": self.processing_delay,
            "concatenation_enabled": self.concatenation_enabled,
            "time_tolerance_seconds": self.time_tolerance
        }
    
    def get_all_buffers_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene el estado de todos los buffers"""
        return {
            phone_number: self.get_buffer_status(phone_number)
            for phone_number in self.message_buffers.keys()
        }
    
    def clear_buffer(self, phone_number: str) -> bool:
        """Limpia el buffer para un número específico"""
        if phone_number in self.message_buffers:
            buffer = self.message_buffers[phone_number]
            
            # Cancelar tarea de procesamiento si está activa
            if buffer.processing_task and not buffer.processing_task.done():
                buffer.processing_task.cancel()
            
            # Limpiar buffer
            buffer.messages.clear()
            buffer.processing_task = None
            
            logger.info(f"[MESSAGE PROCESSOR] Buffer limpiado para {phone_number}")
            return True
        
        return False
    
    def clear_all_buffers(self) -> int:
        """Limpia todos los buffers"""
        cleared_count = 0
        for phone_number in list(self.message_buffers.keys()):
            if self.clear_buffer(phone_number):
                cleared_count += 1
        
        logger.info(f"[MESSAGE PROCESSOR] {cleared_count} buffers limpiados")
        return cleared_count


# Instancia global del procesador
message_processor = MessageProcessor()
