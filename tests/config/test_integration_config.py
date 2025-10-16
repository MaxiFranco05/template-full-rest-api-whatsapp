"""
Configuración para tests de integración de WhatsApp
"""
import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent.parent

# Configuración de testing
TEST_CONFIG = {
    "test_phone_number": "5492625661694",  # Número para testing (no hardcodeado en código)
    "test_message_id_prefix": "test_msg_",
    "test_conversation_prefix": "test_conv_",
    "flows_directory": BASE_DIR / "app" / "flows",
    "test_timeout": 30,
    "max_retries": 3
}

# Configuración de base de datos para testing
TEST_DATABASE_CONFIG = {
    "database_url": "sqlite:///test_whatsapp.db",
    "echo": False,
    "pool_pre_ping": True
}

# Configuración de logging para tests
TEST_LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "handlers": ["console"]
}
