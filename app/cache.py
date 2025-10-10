"""
Sistema de Cache con Redis (OPCIONAL)
"""
import redis
import json
from typing import Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Clase para manejar cache con Redis"""
    
    def __init__(self):
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                # Probar conexión
                self.redis_client.ping()
                logger.info("Conexión a Redis establecida")
            except Exception as e:
                logger.warning(f"No se pudo conectar a Redis: {e}")
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error obteniendo del cache: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Guardar valor en cache"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.setex(
                key, 
                expire, 
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Error guardando en cache: {e}")
            return False

# Instancia global del cache
cache = RedisCache()
