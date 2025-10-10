"""
WhatsApp Persistence Service
Handles WhatsApp data persistence to database
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
    """Convert non-serializable objects to JSON strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_serializable(item) for item in obj]
    else:
        return obj


class WhatsAppPersistenceService:
    """Service for handling WhatsApp data persistence"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, phone_number: str, user_data: Dict[str, Any] = None) -> WhatsAppUser:
        """Get or create WhatsApp user"""
        try:
            # Find existing user
            user = self.db.query(WhatsAppUser).filter(
                WhatsAppUser.phone_number == phone_number
            ).first()
            
            if user:
                # Update data if provided
                if user_data:
                    if 'name' in user_data:
                        user.name = user_data['name']
                    if 'profile_name' in user_data:
                        user.profile_name = user_data['profile_name']
                    user.user_metadata = user_data
                    user.last_message_at = datetime.utcnow()
                    self.db.commit()
                
                logger.info(f"User found: {phone_number}")
                return user
            
            # Create new user
            user = WhatsAppUser(
                phone_number=phone_number,
                name=user_data.get('name') if user_data else None,
                profile_name=user_data.get('name') if user_data else None,
                first_message_at=datetime.utcnow(),
                last_message_at=datetime.utcnow(),
                message_count=0,
                user_metadata=user_data or {}
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"New user created: {phone_number}")
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating user {phone_number}: {e}")
            # Try to get existing user
            return self.db.query(WhatsAppUser).filter(
                WhatsAppUser.phone_number == phone_number
            ).first()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user {phone_number}: {e}")
            raise
    
    def get_or_create_conversation(self, user_id: int, conversation_id: str, 
                                 initial_state: str = "initial") -> WhatsAppConversation:
        """Get or create WhatsApp conversation"""
        try:
            # Find existing conversation
            conversation = self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.conversation_id == conversation_id
            ).first()
            
            if conversation:
                # Update last activity
                conversation.last_activity_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Conversation found: {conversation_id}")
                return conversation
            
            # Create new conversation
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
            
            logger.info(f"New conversation created: {conversation_id}")
            return conversation
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating conversation {conversation_id}: {e}")
            # Try to get existing conversation
            return self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.conversation_id == conversation_id
            ).first()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating conversation {conversation_id}: {e}")
            raise
    
    def save_message(self, conversation_id: int, message_data: Dict[str, Any]) -> WhatsAppMessage:
        """Save WhatsApp message to database"""
        try:
            # Process timestamp to ensure it's datetime
            timestamp = message_data.get('timestamp')
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.utcnow()
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.utcnow()
            
            # Process metadata to ensure JSON serializable
            metadata = message_data.get('metadata', {})
            if metadata:
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
            
            logger.info(f"Message saved: {message_data.get('message_id')}")
            return message
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error saving message: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving message: {e}")
            raise
    
    def update_conversation_state(self, conversation_id: str, new_state: str, 
                                context: Dict[str, Any] = None) -> bool:
        """Update conversation state"""
        try:
            conversation = self.db.query(WhatsAppConversation).filter(
                WhatsAppConversation.conversation_id == conversation_id
            ).first()
            
            if not conversation:
                logger.warning(f"Conversation not found: {conversation_id}")
                return False
            
            conversation.current_state = new_state
            if context:
                if conversation.context is None:
                    conversation.context = {}
                conversation.context.update(context)
            
            self.db.commit()
            
            logger.info(f"Conversation state updated: {conversation_id} -> {new_state}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating conversation state {conversation_id}: {e}")
            return False


def get_whatsapp_persistence_service(db: Session = None) -> WhatsAppPersistenceService:
    """Get persistence service instance"""
    if db is None:
        db = next(get_db())
    
    return WhatsAppPersistenceService(db)