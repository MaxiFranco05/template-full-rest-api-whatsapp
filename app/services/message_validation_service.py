"""
Message Validation Service
Validates message data availability before sending
"""
from typing import Dict, Any, Optional
import logging

from app.services.data_config_service import get_data_config

logger = logging.getLogger(__name__)


class MessageValidationService:
    """Service for validating message data availability"""
    
    def __init__(self):
        self.data_config = get_data_config()
    
    def validate_catalog_message(self, catalog_type: str) -> Dict[str, Any]:
        """Validate catalog message data availability"""
        if catalog_type == "products":
            if not self.data_config.has_products():
                return {
                    "valid": False,
                    "error": "No products catalog available",
                    "fallback_message": "Lo siento, no tenemos productos disponibles en este momento. Por favor, contacta con nosotros para más información."
                }
            return {
                "valid": True,
                "data": self.data_config.get_products()
            }
        
        elif catalog_type == "services":
            if not self.data_config.has_services():
                return {
                    "valid": False,
                    "error": "No services catalog available",
                    "fallback_message": "Lo siento, no tenemos servicios disponibles en este momento. Por favor, contacta con nosotros para más información."
                }
            return {
                "valid": True,
                "data": self.data_config.get_services()
            }
        
        return {
            "valid": False,
            "error": f"Unknown catalog type: {catalog_type}",
            "fallback_message": "Lo siento, no puedo procesar esa solicitud en este momento."
        }
    
    def validate_company_info(self) -> Dict[str, Any]:
        """Validate company information availability"""
        company_info = self.data_config.get_company_info()
        
        if not company_info or not any(company_info.values()):
            return {
                "valid": False,
                "error": "No company information available",
                "fallback_message": "Lo siento, no tengo información de contacto disponible en este momento."
            }
        
        return {
            "valid": True,
            "data": company_info
        }
    
    def get_fallback_message(self, message_type: str) -> str:
        """Get fallback message for different scenarios"""
        fallback_messages = {
            "no_products": "No tenemos productos disponibles en este momento. ¿Te gustaría conocer nuestros servicios?",
            "no_services": "No tenemos servicios disponibles en este momento. ¿Te gustaría ver nuestros productos?",
            "no_contact": "No tengo información de contacto disponible. Por favor, intenta más tarde.",
            "generic_error": "Lo siento, no puedo procesar tu solicitud en este momento. Por favor, intenta más tarde.",
            "catalog_unavailable": "El catálogo no está disponible en este momento. ¿Hay algo más en lo que pueda ayudarte?"
        }
        
        return fallback_messages.get(message_type, fallback_messages["generic_error"])


# Global instance
message_validator = MessageValidationService()


def get_message_validator() -> MessageValidationService:
    """Get message validation service instance"""
    return message_validator
