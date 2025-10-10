"""
Servicio para persistencia de datos de WhatsApp
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from app.models import WhatsAppUser, WhatsAppConversation, WhatsAppMessage
from app.db.database import get_db

logger = logging.getLogger(__name__)


def _make_json_serializable(obj):
    """
    Convertir objetos no serializables a JSON en strings
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_serializable(item) for item in obj]
    else:
        return obj


class WhatsAppPersistenceService:
    """Servicio para manejar persistencia de datos de WhatsApp"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, phone_number: str, user_data: Dict[str, Any] = None) -> WhatsAppUser:
        """
        Obtener o crear usuario de WhatsApp
        
        Args:
            phone_number: Número de teléfono del usuario
            user_data: Datos adicionales del usuario
        
        Returns:
            WhatsAppUser: Usuario encontrado o creado
        """
        try:
            # Buscar usuario existente
            user = self.db.query(WhatsAppUser).filter(
                WhatsAppUser.phone_number == phone_number
            ).first()
            
            if user:
                # Actualizar datos si se proporcionan
                if user_data:
                    if 'name' in user_data:
                        user.name = user_data['name']
                    if 'profile_name' in user_data:
                        user.profile_name = user_data['profile_name']
                    user.user_metadata = user_data
                    user.last_message_at = datetime.utcnow()
                    self.db.commit()
                
                logger.info(f"Usuario encontrado: {phone_number}")
                return user
            
            # Crear nuevo usuario
            user = WhatsAppUser(
                phone_number=phone_number,
                name=user_data.get('name') if user_data else None,
                profile_name=user_data.get('profile_name') if user_data else None,
                first_message_at=datetime.utcnow(),
                last_message_at=datetime.utcnow(),
                user_metadata=user_data or {}
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Nuevo usuario creado: {phone_number}")
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error de integridad creando usuario {phone_number}: {e}")
            # Intentar obtener el usuario que ya existe
            return self.db.query(WhatsAppUser).filter(
                WhatsAppUser.phone_number == phone_number
            ).first()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creando usuario {phone_number}: {e}")
            raise
    
    def get_or_create_conversation(self, user_id: int, conversation_id: str, 
                                 initial_state: str = "initial") -> WhatsAppConversation:
        """
        Obtener o crear conversación de WhatsApp
        
        Args:
            user_id: ID del usuario
            conversation_id: ID único de la conversación
            initial_state: Estado inicial de la conversación
        
        Returns:
            WhatsAppConversation: Conversación encontrada o creada
        """
        try:
            # Buscar conversación existente
            conversation = self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.conversation_id == conversation_id
            ).first()
            
            if conversation:
                # Actualizar última actividad
                conversation.last_activity_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Conversación encontrada: {conversation_id}")
                return conversation
            
            # Crear nueva conversación
            conversation = WhatsAppConversation(
                user_id=user_id,
                conversation_id=conversation_id,
                current_state=initial_state,
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
                context={}
            )
            
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            
            logger.info(f"Nueva conversación creada: {conversation_id}")
            return conversation
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error de integridad creando conversación {conversation_id}: {e}")
            # Intentar obtener la conversación que ya existe
            return self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.conversation_id == conversation_id
            ).first()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creando conversación {conversation_id}: {e}")
            raise
    
    def save_message(self, conversation_id: int, message_data: Dict[str, Any]) -> WhatsAppMessage:
        """
        Guardar mensaje de WhatsApp
        
        Args:
            conversation_id: ID de la conversación
            message_data: Datos del mensaje
        
        Returns:
            WhatsAppMessage: Mensaje guardado
        """
        try:
            # Procesar timestamp para asegurar que sea datetime
            timestamp = message_data.get('timestamp')
            if isinstance(timestamp, str):
                # Si es string, convertir a datetime
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.utcnow()
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.utcnow()
            
            # Procesar metadata para asegurar que sea JSON serializable
            metadata = message_data.get('metadata', {})
            if metadata:
                # Convertir cualquier datetime en metadata a string
                metadata = _make_json_serializable(metadata)
            
            message = WhatsAppMessage(
                conversation_id=conversation_id,
                message_id=message_data.get('message_id'),
                direction=message_data.get('direction', 'inbound'),
                message_type=message_data.get('message_type', 'text'),
                content=message_data.get('content'),
                media_url=message_data.get('media_url'),
                timestamp=timestamp,
                status=message_data.get('status', 'sent'),
                message_metadata=metadata
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Mensaje guardado: {message_data.get('message_id')}")
            return message
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error de integridad guardando mensaje: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error guardando mensaje: {e}")
            raise
    
    def update_conversation_state(self, conversation_id: str, new_state: str, 
                                context: Dict[str, Any] = None) -> bool:
        """
        Actualizar estado de conversación
        
        Args:
            conversation_id: ID de la conversación
            new_state: Nuevo estado
            context: Contexto adicional
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            conversation = self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.conversation_id == conversation_id
            ).first()
            
            if not conversation:
                logger.warning(f"Conversación no encontrada: {conversation_id}")
                return False
            
            conversation.current_state = new_state
            conversation.last_activity_at = datetime.utcnow()
            
            if context:
                if conversation.context:
                    conversation.context.update(context)
                else:
                    conversation.context = context
            
            self.db.commit()
            
            logger.info(f"Estado de conversación actualizado: {conversation_id} -> {new_state}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error actualizando estado de conversación {conversation_id}: {e}")
            return False
    
    def increment_message_count(self, conversation_id: str) -> bool:
        """
        Incrementar contador de mensajes de una conversación
        
        Args:
            conversation_id: ID de la conversación
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            conversation = self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.conversation_id == conversation_id
            ).first()
            
            if not conversation:
                logger.warning(f"Conversación no encontrada: {conversation_id}")
                return False
            
            conversation.message_count += 1
            conversation.last_activity_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Contador de mensajes incrementado: {conversation_id} -> {conversation.message_count}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error incrementando contador de mensajes {conversation_id}: {e}")
            return False
    
    def update_message_status(self, message_id: str, status: str) -> bool:
        """
        Actualizar estado de un mensaje
        
        Args:
            message_id: ID del mensaje
            status: Nuevo estado
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            message = self.db.query(WhatsAppMessage).filter(
                WhatsAppMessage.message_id == message_id
            ).first()
            
            if not message:
                logger.warning(f"Mensaje no encontrado: {message_id}")
                return False
            
            message.status = status
            self.db.commit()
            
            logger.info(f"Estado de mensaje actualizado: {message_id} -> {status}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error actualizando estado de mensaje {message_id}: {e}")
            return False
    
    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[WhatsAppMessage]:
        """
        Obtener historial de mensajes de una conversación
        
        Args:
            conversation_id: ID de la conversación
            limit: Límite de mensajes
        
        Returns:
            List[WhatsAppMessage]: Lista de mensajes
        """
        try:
            conversation = self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.conversation_id == conversation_id
            ).first()
            
            if not conversation:
                logger.warning(f"Conversación no encontrada: {conversation_id}")
                return []
            
            messages = self.db.query(WhatsAppMessage).filter(
                WhatsAppMessage.conversation_id == conversation.id
            ).order_by(WhatsAppMessage.timestamp.desc()).limit(limit).all()
            
            return messages
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de conversación {conversation_id}: {e}")
            return []
    
    def get_user_conversations(self, phone_number: str) -> List[WhatsAppConversation]:
        """
        Obtener conversaciones de un usuario
        
        Args:
            phone_number: Número de teléfono del usuario
        
        Returns:
            List[WhatsAppConversation]: Lista de conversaciones
        """
        try:
            user = self.db.query(WhatsAppUser).filter(
                WhatsAppUser.phone_number == phone_number
            ).first()
            
            if not user:
                return []
            
            conversations = self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.user_id == user.id
            ).order_by(WhatsAppConversation.last_activity_at.desc()).all()
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error obteniendo conversaciones de usuario {phone_number}: {e}")
            return []
    
    def cleanup_expired_conversations(self, timeout_minutes: int = 30) -> int:
        """
        Limpiar conversaciones expiradas
        
        Args:
            timeout_minutes: Tiempo de timeout en minutos
        
        Returns:
            int: Número de conversaciones limpiadas
        """
        try:
            from datetime import timedelta
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
            
            expired_conversations = self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.last_activity_at < cutoff_time,
                WhatsAppConversation.ended_at.is_(None)
            ).all()
            
            count = 0
            for conversation in expired_conversations:
                conversation.ended_at = datetime.utcnow()
                conversation.current_state = "ended"
                count += 1
            
            self.db.commit()
            
            logger.info(f"Conversaciones expiradas limpiadas: {count}")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error limpiando conversaciones expiradas: {e}")
            return 0


# Función de utilidad para obtener el servicio
def get_whatsapp_persistence_service(db: Session = None) -> WhatsAppPersistenceService:
    """
    Obtener instancia del servicio de persistencia
    
    Args:
        db: Sesión de base de datos (opcional)
    
    Returns:
        WhatsAppPersistenceService: Instancia del servicio
    """
    if db is None:
        db = next(get_db())
    
    return WhatsAppPersistenceService(db)
