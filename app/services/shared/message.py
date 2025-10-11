"""
Servicio para gestión de mensajes con tags
"""
import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MessageService:
    """Servicio para manejar mensajes con tags desde archivo YAML"""
    
    def __init__(self):
        self.messages_file = Path(settings.MESSAGES_FILE_PATH)
        self._messages_cache = None
        self._last_modified = None
    
    def _load_messages(self) -> Dict[str, Any]:
        """Cargar mensajes desde archivo YAML"""
        try:
            # Verificar si el archivo existe
            if not self.messages_file.exists():
                logger.error(f"Archivo de mensajes no encontrado: {self.messages_file}")
                return self._get_default_messages()
            
            # Verificar si necesitamos recargar el archivo
            current_modified = self.messages_file.stat().st_mtime
            if (self._messages_cache is None or 
                self._last_modified is None or 
                current_modified > self._last_modified):
                
                with open(self.messages_file, 'r', encoding='utf-8') as file:
                    self._messages_cache = yaml.safe_load(file)
                    self._last_modified = current_modified
                    logger.info("Mensajes recargados desde archivo")
            
            return self._messages_cache
            
        except Exception as e:
            logger.error(f"Error cargando mensajes: {e}")
            return self._get_default_messages()
    
    def _get_default_messages(self) -> Dict[str, Any]:
        """Mensajes por defecto en caso de error"""
        return {
            "messages": {
                "welcome": {
                    "new_user": "¡Hola! Bienvenido/a. ¿En qué puedo ayudarte?",
                    "returning_user": "¡Hola de nuevo! ¿Cómo puedo ayudarte hoy?"
                },
                "error": {
                    "general": "Lo siento, ha ocurrido un error. Intenta de nuevo."
                }
            }
        }
    
    def get_message(self, *keys: str, **variables: str) -> str:
        """
        Obtener mensaje usando keys anidadas
        
        Args:
            *keys: Claves anidadas para acceder al mensaje (ej: 'welcome', 'new_user')
            **variables: Variables para reemplazar en el mensaje
        
        Returns:
            str: Mensaje formateado
        """
        try:
            messages_data = self._load_messages()
            
            # Navegar por las claves anidadas
            current = messages_data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    logger.warning(f"Clave no encontrada: {key} en {keys}")
                    return self._get_fallback_message(keys)
            
            # Si llegamos aquí, current debería ser el mensaje
            if isinstance(current, str):
                return self._format_message(current, **variables)
            else:
                logger.warning(f"Mensaje no es string: {current}")
                return self._get_fallback_message(keys)
                
        except Exception as e:
            logger.error(f"Error obteniendo mensaje {keys}: {e}")
            return self._get_fallback_message(keys)
    
    def _format_message(self, message: str, **variables: str) -> str:
        """Formatear mensaje reemplazando variables"""
        try:
            # Reemplazar variables en el mensaje
            formatted_message = message
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                formatted_message = formatted_message.replace(placeholder, str(value))
            
            return formatted_message
        except Exception as e:
            logger.error(f"Error formateando mensaje: {e}")
            return message
    
    def _get_fallback_message(self, keys: tuple) -> str:
        """Mensaje de respaldo cuando no se encuentra el mensaje"""
        return f"Mensaje no disponible: {' -> '.join(keys)}"
    
    def get_welcome_message(self, is_new_user: bool = True, **variables: str) -> str:
        """Obtener mensaje de bienvenida"""
        message_key = "new_user" if is_new_user else "returning_user"
        return self.get_message("messages", "welcome", message_key, **variables)
    
    def get_error_message(self, error_type: str = "general", **variables: str) -> str:
        """Obtener mensaje de error"""
        return self.get_message("messages", "error", error_type, **variables)
    
    def get_info_message(self, info_type: str, **variables: str) -> str:
        """Obtener mensaje informativo"""
        return self.get_message("messages", "info", info_type, **variables)
    
    def get_state_message(self, state: str, **variables: str) -> str:
        """Obtener mensaje de estado"""
        return self.get_message("messages", "states", state, **variables)
    
    def get_goodbye_message(self, goodbye_type: str = "default", **variables: str) -> str:
        """Obtener mensaje de despedida"""
        return self.get_message("messages", "goodbye", goodbye_type, **variables)
    
    def get_confirmation_message(self, confirmation_type: str, **variables: str) -> str:
        """Obtener mensaje de confirmación"""
        return self.get_message("messages", "confirmation", confirmation_type, **variables)
    
    def reload_messages(self) -> bool:
        """Forzar recarga de mensajes desde archivo"""
        try:
            self._messages_cache = None
            self._last_modified = None
            self._load_messages()
            logger.info("Mensajes recargados exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error recargando mensajes: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Obtener configuración de mensajes"""
        try:
            messages_data = self._load_messages()
            return messages_data.get("config", {})
        except Exception as e:
            logger.error(f"Error obteniendo configuración: {e}")
            return {}


# Instancia global del servicio
message_service = MessageService()
