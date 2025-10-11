"""
Modelos de usuario
"""
from sqlalchemy import Column, String, Boolean
from .base import BaseModel


class User(BaseModel):
    """Modelo de usuario"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
