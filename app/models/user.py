"""
Modelos de usuario
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.sql import func
from .base import BaseModel


class User(BaseModel):
    """Modelo de usuario con sistema de administración Django-style"""
    __tablename__ = "users"
    
    # Información básica
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Estados del usuario
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Permisos de administración
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    
    # Información adicional
    phone_number = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Timestamps de actividad
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Configuración de usuario
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="es", nullable=False)
    
    # Contadores
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    
    # Metadatos
    user_metadata = Column(Text, nullable=True)  # JSON string para datos adicionales
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.is_superuser or self.is_staff
    
    @property
    def display_name(self):
        """Get display name (full_name or username)"""
        return self.full_name or self.username
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.is_superuser:
            return True
        
        # Add specific permission checks here
        permission_map = {
            'admin.access': self.is_staff,
            'user.manage': self.is_staff,
            'flow.manage': self.is_staff,
            'whatsapp.manage': self.is_staff,
        }
        
        return permission_map.get(permission, False)
