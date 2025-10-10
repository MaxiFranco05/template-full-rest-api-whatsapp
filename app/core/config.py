"""
Configuración de la aplicación FastAPI
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # Información básica de la aplicación
    APP_NAME: str = "Cafe API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/cafe_db"
    DATABASE_URL_TEST: str = "postgresql://user:password@localhost:5432/cafe_test_db"
    
    # Seguridad
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: list = ["*"]
    
    # Redis (OPCIONAL - Solo necesario para cache y tareas asíncronas)
    REDIS_URL: Optional[str] = None
    
    # Celery (OPCIONAL - Solo necesario para tareas en background)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Archivos estáticos
    STATIC_FILES_PATH: str = "app/static"
    
    # WhatsApp Business API
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = ""
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    
    # Sistema de mensajes
    MESSAGES_FILE_PATH: str = "app/data/messages.yaml"
    
    # Base de datos (SQLite por defecto, pero configurable)
    DATABASE_TYPE: str = "sqlite"  # sqlite, postgresql, mysql
    SQLITE_DATABASE_URL: str = "sqlite:///./cafe_whatsapp.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()