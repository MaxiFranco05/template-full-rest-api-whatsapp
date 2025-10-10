"""
Sistema de logging profesional para la aplicación
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Formateador JSON para logs estructurados"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar información adicional si existe
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'conversation_id'):
            log_entry['conversation_id'] = record.conversation_id
        if hasattr(record, 'phone_number'):
            log_entry['phone_number'] = record.phone_number
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        # Agregar excepción si existe
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class WhatsAppLogger:
    """Logger especializado para WhatsApp"""
    
    def __init__(self, name: str = "whatsapp"):
        self.logger = logging.getLogger(name)
    
    def log_webhook_received(self, data: Dict[str, Any], request_id: str = None):
        """Log cuando se recibe un webhook"""
        extra = {'request_id': request_id} if request_id else {}
        self.logger.info(
            f"Webhook recibido: {len(data.get('entry', []))} entradas",
            extra=extra
        )
    
    def log_message_processed(self, message_id: str, phone_number: str, 
                            conversation_id: str, status: str):
        """Log cuando se procesa un mensaje"""
        self.logger.info(
            f"Mensaje procesado: {message_id} para {phone_number}",
            extra={
                'message_id': message_id,
                'phone_number': phone_number,
                'conversation_id': conversation_id,
                'status': status
            }
        )
    
    def log_message_sent(self, message_id: str, phone_number: str, 
                        success: bool, error: str = None):
        """Log cuando se envía un mensaje"""
        level = logging.INFO if success else logging.ERROR
        message = f"Mensaje enviado: {message_id} a {phone_number}"
        if not success:
            message += f" - Error: {error}"
        
        self.logger.log(
            level,
            message,
            extra={
                'message_id': message_id,
                'phone_number': phone_number,
                'success': success,
                'error': error
            }
        )
    
    def log_conversation_state_change(self, conversation_id: str, 
                                    old_state: str, new_state: str):
        """Log cuando cambia el estado de una conversación"""
        self.logger.info(
            f"Estado de conversación cambiado: {old_state} -> {new_state}",
            extra={
                'conversation_id': conversation_id,
                'old_state': old_state,
                'new_state': new_state
            }
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log de errores con contexto"""
        extra = context or {}
        self.logger.error(
            f"Error en WhatsApp: {str(error)}",
            extra=extra,
            exc_info=True
        )


class APILogger:
    """Logger especializado para API"""
    
    def __init__(self, name: str = "api"):
        self.logger = logging.getLogger(name)
    
    def log_request(self, method: str, path: str, user_id: str = None, 
                   request_id: str = None):
        """Log de requests HTTP"""
        extra = {'request_id': request_id}
        if user_id:
            extra['user_id'] = user_id
        
        self.logger.info(
            f"Request: {method} {path}",
            extra=extra
        )
    
    def log_response(self, method: str, path: str, status_code: int, 
                    response_time: float, request_id: str = None):
        """Log de responses HTTP"""
        level = logging.INFO if status_code < 400 else logging.WARNING
        self.logger.log(
            level,
            f"Response: {method} {path} - {status_code} ({response_time:.3f}s)",
            extra={
                'request_id': request_id,
                'status_code': status_code,
                'response_time': response_time
            }
        )
    
    def log_authentication(self, user_id: str, success: bool, 
                          ip_address: str = None):
        """Log de autenticación"""
        level = logging.INFO if success else logging.WARNING
        message = f"Autenticación {'exitosa' if success else 'fallida'} para usuario {user_id}"
        
        extra = {'user_id': user_id, 'success': success}
        if ip_address:
            extra['ip_address'] = ip_address
        
        self.logger.log(level, message, extra=extra)


def setup_logging():
    """Configurar el sistema de logging"""
    
    # Crear directorio de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configuración de logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "json": {
                "()": JSONFormatter,
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": "logs/errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "whatsapp_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/whatsapp.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file", "error_file"],
                "level": "INFO",
                "propagate": False
            },
            "whatsapp": {
                "handlers": ["console", "whatsapp_file", "error_file"],
                "level": "INFO",
                "propagate": False
            },
            "api": {
                "handlers": ["console", "file", "error_file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.error": {
                "handlers": ["console", "error_file"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    
    # Aplicar configuración
    logging.config.dictConfig(logging_config)
    
    # Configurar nivel de logging según DEBUG
    if settings.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("whatsapp").setLevel(logging.DEBUG)
        logging.getLogger("api").setLevel(logging.DEBUG)


# Instancias globales de loggers
whatsapp_logger = WhatsAppLogger()
api_logger = APILogger()


def get_logger(name: str) -> logging.Logger:
    """Obtener logger por nombre"""
    return logging.getLogger(name)
