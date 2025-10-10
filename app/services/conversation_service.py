"""
Máquina de estados para el sistema de mensajería WhatsApp
"""
from transitions import Machine
from transitions.extensions import GraphMachine
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Estados posibles de una conversación"""
    INITIAL = "initial"
    WAITING_WELCOME = "waiting_welcome"
    ACTIVE = "active"
    WAITING_RESPONSE = "waiting_response"
    PROCESSING = "processing"
    IDLE = "idle"
    ENDED = "ended"


class ConversationMachine:
    """Máquina de estados para manejar conversaciones de WhatsApp"""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.state = ConversationState.INITIAL
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.message_count = 0
        self.is_new_user = True
        self.user_data = {}
        self.context = {}
        
        # Configurar la máquina de estados
        self._setup_state_machine()
    
    def _setup_state_machine(self):
        """Configurar la máquina de estados"""
        states = [state.value for state in ConversationState]
        
        transitions = [
            # Transiciones desde INITIAL
            {
                'trigger': 'receive_first_message',
                'source': ConversationState.INITIAL.value,
                'dest': ConversationState.WAITING_WELCOME.value,
                'before': 'on_first_message'
            },
            
            # Transiciones desde WAITING_WELCOME
            {
                'trigger': 'send_welcome',
                'source': ConversationState.WAITING_WELCOME.value,
                'dest': ConversationState.ACTIVE.value,
                'after': 'on_welcome_sent'
            },
            
            # Transiciones desde ACTIVE
            {
                'trigger': 'receive_message',
                'source': ConversationState.ACTIVE.value,
                'dest': ConversationState.PROCESSING.value,
                'before': 'on_message_received'
            },
            {
                'trigger': 'go_idle',
                'source': ConversationState.ACTIVE.value,
                'dest': ConversationState.IDLE.value,
                'after': 'on_go_idle'
            },
            
            # Transiciones desde PROCESSING
            {
                'trigger': 'send_response',
                'source': ConversationState.PROCESSING.value,
                'dest': ConversationState.ACTIVE.value,
                'after': 'on_response_sent'
            },
            {
                'trigger': 'wait_for_response',
                'source': ConversationState.PROCESSING.value,
                'dest': ConversationState.WAITING_RESPONSE.value,
                'after': 'on_waiting_response'
            },
            
            # Transiciones desde WAITING_RESPONSE
            {
                'trigger': 'receive_message',
                'source': ConversationState.WAITING_RESPONSE.value,
                'dest': ConversationState.PROCESSING.value,
                'before': 'on_message_received'
            },
            {
                'trigger': 'timeout',
                'source': ConversationState.WAITING_RESPONSE.value,
                'dest': ConversationState.IDLE.value,
                'after': 'on_timeout'
            },
            
            # Transiciones desde IDLE
            {
                'trigger': 'receive_message',
                'source': ConversationState.IDLE.value,
                'dest': ConversationState.ACTIVE.value,
                'before': 'on_message_received'
            },
            {
                'trigger': 'end_conversation',
                'source': ConversationState.IDLE.value,
                'dest': ConversationState.ENDED.value,
                'after': 'on_conversation_ended'
            },
            
            # Transiciones hacia ENDED
            {
                'trigger': 'end_conversation',
                'source': [ConversationState.ACTIVE.value, ConversationState.PROCESSING.value],
                'dest': ConversationState.ENDED.value,
                'after': 'on_conversation_ended'
            }
        ]
        
        # Crear la máquina de estados
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=ConversationState.INITIAL.value,
            auto_transitions=False
        )
    
    # Callbacks de transiciones
    def on_first_message(self, message_data: Dict[str, Any]):
        """Callback cuando se recibe el primer mensaje"""
        self.message_count = 1
        self.last_activity = datetime.now()
        self.user_data.update(message_data.get('user_data', {}))
        logger.info(f"Primer mensaje recibido para conversación {self.conversation_id}")
    
    def on_welcome_sent(self):
        """Callback cuando se envía mensaje de bienvenida"""
        logger.info(f"Mensaje de bienvenida enviado para conversación {self.conversation_id}")
    
    def on_message_received(self, message_data: Dict[str, Any]):
        """Callback cuando se recibe un mensaje"""
        self.message_count += 1
        self.last_activity = datetime.now()
        self.user_data.update(message_data.get('user_data', {}))
        logger.info(f"Mensaje #{self.message_count} recibido para conversación {self.conversation_id}")
    
    def on_response_sent(self):
        """Callback cuando se envía una respuesta"""
        logger.info(f"Respuesta enviada para conversación {self.conversation_id}")
    
    def on_waiting_response(self):
        """Callback cuando se espera respuesta del usuario"""
        logger.info(f"Esperando respuesta del usuario para conversación {self.conversation_id}")
    
    def on_go_idle(self):
        """Callback cuando la conversación se vuelve inactiva"""
        logger.info(f"Conversación {self.conversation_id} se volvió inactiva")
    
    def on_timeout(self):
        """Callback cuando ocurre timeout"""
        logger.info(f"Timeout en conversación {self.conversation_id}")
    
    def on_conversation_ended(self):
        """Callback cuando termina la conversación"""
        logger.info(f"Conversación {self.conversation_id} terminada")
    
    # Métodos de utilidad
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Verificar si la conversación ha expirado"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)
    
    def get_duration(self) -> timedelta:
        """Obtener duración de la conversación"""
        return datetime.now() - self.created_at
    
    def update_context(self, **kwargs):
        """Actualizar contexto de la conversación"""
        self.context.update(kwargs)
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Obtener valor del contexto"""
        return self.context.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'conversation_id': self.conversation_id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'message_count': self.message_count,
            'is_new_user': self.is_new_user,
            'user_data': self.user_data,
            'context': self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMachine':
        """Crear instancia desde diccionario"""
        instance = cls(data['conversation_id'])
        instance.state = ConversationState(data['state'])
        instance.created_at = datetime.fromisoformat(data['created_at'])
        instance.last_activity = datetime.fromisoformat(data['last_activity'])
        instance.message_count = data['message_count']
        instance.is_new_user = data['is_new_user']
        instance.user_data = data['user_data']
        instance.context = data['context']
        return instance


class ConversationManager:
    """Gestor de conversaciones con máquinas de estados"""
    
    def __init__(self):
        self.conversations: Dict[str, ConversationMachine] = {}
        self.timeout_minutes = 30
    
    def get_or_create_conversation(self, conversation_id: str) -> ConversationMachine:
        """Obtener o crear conversación"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationMachine(conversation_id)
            logger.info(f"Nueva conversación creada: {conversation_id}")
        
        return self.conversations[conversation_id]
    
    def cleanup_expired_conversations(self):
        """Limpiar conversaciones expiradas"""
        expired_ids = []
        for conv_id, conversation in self.conversations.items():
            if conversation.is_expired(self.timeout_minutes):
                expired_ids.append(conv_id)
        
        for conv_id in expired_ids:
            conversation = self.conversations[conv_id]
            if conversation.state != ConversationState.ENDED:
                conversation.end_conversation()
            del self.conversations[conv_id]
            logger.info(f"Conversación expirada eliminada: {conv_id}")
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de conversaciones"""
        total = len(self.conversations)
        active = sum(1 for conv in self.conversations.values() 
                    if conv.state in [ConversationState.ACTIVE, ConversationState.PROCESSING])
        
        return {
            'total_conversations': total,
            'active_conversations': active,
            'idle_conversations': total - active
        }


# Instancia global del gestor
conversation_manager = ConversationManager()
