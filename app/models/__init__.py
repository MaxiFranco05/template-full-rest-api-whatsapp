"""
Modelos base para la aplicación
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class BaseModel(Base):
    """Modelo base con campos comunes"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)


class User(BaseModel):
    """Modelo de usuario"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)


class WhatsAppUser(BaseModel):
    """Modelo de usuario de WhatsApp"""
    __tablename__ = "whatsapp_users"
    
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    profile_name = Column(String(255), nullable=True)
    is_business = Column(Boolean, default=False)
    first_message_at = Column(DateTime(timezone=True), nullable=True)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    message_count = Column(Integer, default=0)
    is_blocked = Column(Boolean, default=False)
    user_metadata = Column(JSON, nullable=True)  # Datos adicionales del usuario
    
    # Relación con conversaciones
    conversations = relationship("WhatsAppConversation", back_populates="user")


class WhatsAppConversation(BaseModel):
    """Modelo de conversación de WhatsApp"""
    __tablename__ = "whatsapp_conversations"
    
    user_id = Column(Integer, ForeignKey("whatsapp_users.id"), nullable=False)
    conversation_id = Column(String(100), unique=True, index=True, nullable=False)
    current_state = Column(String(50), default="initial")
    message_count = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    context = Column(JSON, nullable=True)  # Contexto de la conversación
    
    # Relación con usuario
    user = relationship("WhatsAppUser", back_populates="conversations")
    
    # Relación con mensajes
    messages = relationship("WhatsAppMessage", back_populates="conversation")


class WhatsAppMessage(BaseModel):
    """Modelo de mensaje de WhatsApp"""
    __tablename__ = "whatsapp_messages"
    
    conversation_id = Column(Integer, ForeignKey("whatsapp_conversations.id"), nullable=False)
    message_id = Column(String(100), unique=True, index=True, nullable=False)
    direction = Column(String(10), nullable=False)  # 'inbound' o 'outbound'
    message_type = Column(String(20), nullable=False)  # 'text', 'image', 'audio', etc.
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="sent")  # 'sent', 'delivered', 'read', 'failed'
    message_metadata = Column(JSON, nullable=True)  # Datos adicionales del mensaje
    
    # Relación con conversación
    conversation = relationship("WhatsAppConversation", back_populates="messages")


class Category(BaseModel):
    """Modelo de categoría de productos"""
    __tablename__ = "categories"
    
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)


class Product(BaseModel):
    """Modelo de producto"""
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Precio en centavos
    category_id = Column(Integer, nullable=True)
    image_url = Column(String(500), nullable=True)
    stock_quantity = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
