"""
Configuración de Celery para tareas asíncronas (OPCIONAL)
"""
from celery import Celery
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Crear instancia de Celery
celery_app = Celery(
    "cafe_api",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Tareas de Celery
@celery_app.task(bind=True)
def process_whatsapp_message_async(self, message_data: dict):
    """
    Procesar mensaje de WhatsApp de forma asíncrona
    """
    try:
        from app.services.whatsapp.service import whatsapp_service
        
        logger.info(f"Procesando mensaje asíncrono: {message_data.get('message_id')}")
        
        # Procesar mensaje
        result = whatsapp_service.process_incoming_message(message_data)
        
        logger.info(f"Mensaje procesado exitosamente: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error procesando mensaje asíncrono: {e}")
        # Reintentar la tarea
        raise self.retry(countdown=60, max_retries=3)

@celery_app.task
def send_scheduled_message(phone_number: str, message: str, scheduled_time: str):
    """
    Enviar mensaje programado
    """
    try:
        from app.services.whatsapp.service import whatsapp_service
        from datetime import datetime
        
        logger.info(f"Enviando mensaje programado a {phone_number}")
        
        result = whatsapp_service.send_message(phone_number, message)
        
        logger.info(f"Mensaje programado enviado: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error enviando mensaje programado: {e}")
        return {"success": False, "error": str(e)}

@celery_app.task
def cleanup_expired_conversations():
    """
    Limpiar conversaciones expiradas (tarea programada)
    """
    try:
        from app.services.business.conversation import conversation_manager
        
        logger.info("Limpiando conversaciones expiradas")
        
        conversation_manager.cleanup_expired_conversations()
        
        logger.info("Limpieza de conversaciones completada")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error limpiando conversaciones: {e}")
        return {"success": False, "error": str(e)}

# Configurar tareas programadas
celery_app.conf.beat_schedule = {
    "cleanup-expired-conversations": {
        "task": "app.celery_app.cleanup_expired_conversations",
        "schedule": 300.0,  # Cada 5 minutos
    },
}

# Para ejecutar Celery:
# celery -A app.celery_app worker --loglevel=info
# celery -A app.celery_app beat --loglevel=info
