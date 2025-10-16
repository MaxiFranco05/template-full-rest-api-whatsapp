"""
Sistema de detección automática de Redis y Celery
"""
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class FeatureDetection:
    """Detectar qué características están disponibles"""
    
    def __init__(self):
        self.redis_available = self._check_redis()
        self.celery_available = self._check_celery()
        
        # Log del estado
        if self.redis_available:
            logger.info("Redis disponible - Cache habilitado")
        else:
            logger.info("Redis no disponible - Cache deshabilitado")
            
        if self.celery_available:
            logger.info("Celery disponible - Tareas asíncronas habilitadas")
        else:
            logger.info("Celery no disponible - Tareas síncronas")
    
    def _check_redis(self) -> bool:
        """Verificar si Redis está disponible"""
        if not settings.REDIS_URL:
            return False
        
        try:
            import redis
            client = redis.from_url(settings.REDIS_URL)
            client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis no disponible: {e}")
            return False
    
    def _check_celery(self) -> bool:
        """Verificar si Celery está disponible"""
        if not settings.CELERY_BROKER_URL or not settings.CELERY_RESULT_BACKEND:
            return False
        
        try:
            from celery import Celery
            # Verificar que Redis esté disponible para Celery
            return self.redis_available
        except Exception as e:
            logger.warning(f"Celery no disponible: {e}")
            return False
    
    def get_status(self) -> dict:
        """Obtener estado de las características"""
        return {
            "redis_available": self.redis_available,
            "celery_available": self.celery_available,
            "features": {
                "cache": self.redis_available,
                "async_tasks": self.celery_available,
                "background_processing": self.celery_available
            }
        }

# Instancia global
feature_detection = FeatureDetection()

# Funciones de utilidad
def use_redis() -> bool:
    """Verificar si se debe usar Redis"""
    return feature_detection.redis_available

def use_celery() -> bool:
    """Verificar si se debe usar Celery"""
    return feature_detection.celery_available

def get_cache():
    """Obtener instancia de cache usando el sistema consolidado"""
    try:
        from app.utils.cache import get_cache_manager
        return get_cache_manager()
    except ImportError:
        logger.warning("Sistema de cache no disponible")
        return None

def execute_task(task_func, *args, **kwargs):
    """Ejecutar tarea (asíncrona si Celery disponible, síncrona si no)"""
    if use_celery():
        try:
            from app.celery_app import celery_app
            # Ejecutar como tarea de Celery
            return task_func.delay(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Error ejecutando tarea con Celery: {e}")
    
    # Fallback: ejecutar síncronamente
    logger.info("Ejecutando tarea síncronamente (Celery no disponible)")
    return task_func(*args, **kwargs)
