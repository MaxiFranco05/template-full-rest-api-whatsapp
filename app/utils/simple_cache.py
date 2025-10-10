"""
Cache simple en memoria como fallback cuando Redis no está disponible
"""
import time
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """Cache simple en memoria como fallback"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info("Usando cache simple en memoria (Redis no disponible)")
    
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        
        # Verificar si expiró
        if item['expires_at'] < time.time():
            del self._cache[key]
            return None
        
        return item['value']
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Guardar valor en cache"""
        try:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + expire
            }
            return True
        except Exception as e:
            logger.error(f"Error guardando en cache simple: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Eliminar valor del cache"""
        try:
            if key in self._cache:
                del self._cache[key]
            return True
        except Exception as e:
            logger.error(f"Error eliminando del cache simple: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verificar si existe una clave"""
        if key not in self._cache:
            return False
        
        # Verificar si expiró
        if self._cache[key]['expires_at'] < time.time():
            del self._cache[key]
            return False
        
        return True
    
    def clear(self):
        """Limpiar todo el cache"""
        self._cache.clear()
        logger.info("Cache simple limpiado")
    
    def cleanup_expired(self):
        """Limpiar elementos expirados"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if item['expires_at'] < current_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Limpiados {len(expired_keys)} elementos expirados del cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        self.cleanup_expired()
        return {
            "type": "simple_memory",
            "total_items": len(self._cache),
            "redis_available": False
        }
