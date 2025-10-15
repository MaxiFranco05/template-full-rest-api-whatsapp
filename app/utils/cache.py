# Advanced Caching System

"""
Advanced caching system with multiple backends and intelligent invalidation
"""

import json
import hashlib
import pickle
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import logging
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class CacheBackend(Enum):
    """Cache backend types"""
    MEMORY = "memory"
    REDIS = "redis"
    FILE = "file"
    DATABASE = "database"

@dataclass
class CacheConfig:
    """Cache configuration"""
    backend: CacheBackend = CacheBackend.MEMORY
    ttl: int = 3600  # Time to live in seconds
    max_size: int = 1000  # Maximum number of items
    compression: bool = False
    serialize_method: str = "json"  # json, pickle
    key_prefix: str = "cache"
    namespace: str = "default"

@dataclass
class CacheItem:
    """Cache item container"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
        if self.tags is None:
            self.tags = []
    
    def is_expired(self) -> bool:
        """Check if cache item is expired"""
        return datetime.now() > self.expires_at
    
    def touch(self):
        """Update access information"""
        self.access_count += 1
        self.last_accessed = datetime.now()

class BaseCacheBackend:
    """Base cache backend interface"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        raise NotImplementedError
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        raise NotImplementedError
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        raise NotImplementedError
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self._stats.copy()
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        if self.config.serialize_method == "json":
            return json.dumps(value, default=str).encode('utf-8')
        elif self.config.serialize_method == "pickle":
            return pickle.dumps(value)
        else:
            raise ValueError(f"Unsupported serialize method: {self.config.serialize_method}")
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        if self.config.serialize_method == "json":
            return json.loads(data.decode('utf-8'))
        elif self.config.serialize_method == "pickle":
            return pickle.loads(data)
        else:
            raise ValueError(f"Unsupported serialize method: {self.config.serialize_method}")

class MemoryCacheBackend(BaseCacheBackend):
    """In-memory cache backend"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache: Dict[str, CacheItem] = {}
        self._access_order: List[str] = []
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        full_key = f"{self.config.namespace}:{key}"
        
        if full_key not in self._cache:
            self._stats["misses"] += 1
            return None
        
        item = self._cache[full_key]
        
        if item.is_expired():
            await self.delete(key)
            self._stats["misses"] += 1
            return None
        
        item.touch()
        self._stats["hits"] += 1
        
        # Update access order for LRU
        if full_key in self._access_order:
            self._access_order.remove(full_key)
        self._access_order.append(full_key)
        
        return item.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache"""
        full_key = f"{self.config.namespace}:{key}"
        ttl = ttl or self.config.ttl
        
        # Check if we need to evict items
        if len(self._cache) >= self.config.max_size:
            await self._evict_lru()
        
        expires_at = datetime.now() + timedelta(seconds=ttl)
        item = CacheItem(
            key=full_key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        self._cache[full_key] = item
        self._access_order.append(full_key)
        self._stats["sets"] += 1
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache"""
        full_key = f"{self.config.namespace}:{key}"
        
        if full_key in self._cache:
            del self._cache[full_key]
            if full_key in self._access_order:
                self._access_order.remove(full_key)
            self._stats["deletes"] += 1
            return True
        
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache"""
        full_key = f"{self.config.namespace}:{key}"
        return full_key in self._cache and not self._cache[full_key].is_expired()
    
    async def clear(self) -> bool:
        """Clear all memory cache entries"""
        self._cache.clear()
        self._access_order.clear()
        return True
    
    async def _evict_lru(self):
        """Evict least recently used item"""
        if not self._access_order:
            return
        
        oldest_key = self._access_order[0]
        if oldest_key in self._cache:
            del self._cache[oldest_key]
            self._access_order.remove(oldest_key)
            self._stats["evictions"] += 1

class RedisCacheBackend(BaseCacheBackend):
    """Redis cache backend"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._redis = None
        self._connection_pool = None
    
    async def _get_redis(self):
        """Get Redis connection"""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                from app.core.config import settings
                
                # Usar URL de configuración o fallback
                redis_url = settings.REDIS_URL or "redis://localhost:6379"
                self._redis = redis.from_url(redis_url)
                await self._redis.ping()
                logger.info(f"Conectado a Redis: {redis_url}")
            except ImportError:
                logger.error("Redis not available. Install redis package.")
                raise
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            redis = await self._get_redis()
            full_key = f"{self.config.namespace}:{key}"
            
            data = await redis.get(full_key)
            if data is None:
                self._stats["misses"] += 1
                return None
            
            self._stats["hits"] += 1
            return self._deserialize(data)
        
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self._stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        try:
            redis = await self._get_redis()
            full_key = f"{self.config.namespace}:{key}"
            ttl = ttl or self.config.ttl
            
            data = self._serialize(value)
            await redis.setex(full_key, ttl, data)
            self._stats["sets"] += 1
            return True
        
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            redis = await self._get_redis()
            full_key = f"{self.config.namespace}:{key}"
            
            result = await redis.delete(full_key)
            self._stats["deletes"] += 1
            return result > 0
        
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        try:
            redis = await self._get_redis()
            full_key = f"{self.config.namespace}:{key}"
            return await redis.exists(full_key) > 0
        
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all Redis cache entries"""
        try:
            redis = await self._get_redis()
            pattern = f"{self.config.namespace}:*"
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
            return True
        
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False

class FileCacheBackend(BaseCacheBackend):
    """File-based cache backend"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        import os
        self.cache_dir = os.path.join(os.getcwd(), "cache", config.namespace)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key"""
        import os
        # Use hash to avoid filesystem issues with special characters
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from file cache"""
        try:
            import os
            file_path = self._get_file_path(key)
            
            if not os.path.exists(file_path):
                self._stats["misses"] += 1
                return None
            
            # Check if file is expired
            file_time = os.path.getmtime(file_path)
            if time.time() - file_time > self.config.ttl:
                os.remove(file_path)
                self._stats["misses"] += 1
                return None
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            self._stats["hits"] += 1
            return self._deserialize(data)
        
        except Exception as e:
            logger.error(f"File cache get error: {e}")
            self._stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in file cache"""
        try:
            import os
            file_path = self._get_file_path(key)
            
            data = self._serialize(value)
            with open(file_path, 'wb') as f:
                f.write(data)
            
            self._stats["sets"] += 1
            return True
        
        except Exception as e:
            logger.error(f"File cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from file cache"""
        try:
            import os
            file_path = self._get_file_path(key)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                self._stats["deletes"] += 1
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"File cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in file cache"""
        try:
            import os
            file_path = self._get_file_path(key)
            return os.path.exists(file_path)
        
        except Exception as e:
            logger.error(f"File cache exists error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all file cache entries"""
        try:
            import os
            import shutil
            
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
            
            return True
        
        except Exception as e:
            logger.error(f"File cache clear error: {e}")
            return False

class CacheManager:
    """Advanced cache manager with multiple backends"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.backend = self._create_backend()
        self._tags: Dict[str, List[str]] = {}  # tag -> list of keys
    
    def _create_backend(self) -> BaseCacheBackend:
        """Create cache backend based on config"""
        if self.config.backend == CacheBackend.MEMORY:
            return MemoryCacheBackend(self.config)
        elif self.config.backend == CacheBackend.REDIS:
            return RedisCacheBackend(self.config)
        elif self.config.backend == CacheBackend.FILE:
            return FileCacheBackend(self.config)
        else:
            raise ValueError(f"Unsupported cache backend: {self.config.backend}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return await self.backend.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  tags: Optional[List[str]] = None) -> bool:
        """Set value in cache with optional tags"""
        success = await self.backend.set(key, value, ttl)
        
        if success and tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = []
                if key not in self._tags[tag]:
                    self._tags[tag].append(key)
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        return await self.backend.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return await self.backend.exists(key)
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        self._tags.clear()
        return await self.backend.clear()
    
    async def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with specific tag"""
        if tag not in self._tags:
            return 0
        
        keys = self._tags[tag]
        deleted_count = 0
        
        for key in keys:
            if await self.delete(key):
                deleted_count += 1
        
        del self._tags[tag]
        return deleted_count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        backend_stats = await self.backend.get_stats()
        return {
            **backend_stats,
            "backend": self.config.backend.value,
            "namespace": self.config.namespace,
            "tags_count": len(self._tags)
        }

# Cache decorators
def cached(ttl: int = 3600, key_prefix: str = "", tags: Optional[List[str]] = None):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            
            # Try to get from cache
            cache_manager = get_cache_manager()
            cached_result = await cache_manager.get(cache_key)
            
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = await func(*args, **kwargs)
            
            await cache_manager.set(cache_key, result, ttl, tags)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_prefix)
            
            # Try to get from cache
            cache_manager = get_cache_manager()
            cached_result = asyncio.run(cache_manager.get(cache_key))
            
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            
            asyncio.run(cache_manager.set(cache_key, result, ttl, tags))
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def cache_invalidate(tags: Optional[List[str]] = None):
    """Decorator to invalidate cache after function execution"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if tags:
                cache_manager = get_cache_manager()
                for tag in tags:
                    await cache_manager.invalidate_by_tag(tag)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if tags:
                cache_manager = get_cache_manager()
                for tag in tags:
                    asyncio.run(cache_manager.invalidate_by_tag(tag))
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def _generate_cache_key(func: Callable, args: tuple, kwargs: dict, prefix: str) -> str:
    """Generate cache key from function and arguments"""
    # Create a hash of function name, args, and kwargs
    key_data = {
        "func": f"{func.__module__}.{func.__name__}",
        "args": args,
        "kwargs": kwargs
    }
    
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"{prefix}:{key_hash}" if prefix else key_hash

# Global cache manager instance
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        # Importar configuración para detectar Redis
        from app.core.config import settings
        
        # Determinar backend basado en configuración
        if settings.REDIS_URL:
            config = CacheConfig(
                backend=CacheBackend.REDIS,
                ttl=3600,
                max_size=1000,
                namespace="whatsapp_api"
            )
            logger.info("Cache configurado para usar Redis")
        else:
            config = CacheConfig(
                backend=CacheBackend.MEMORY,
                ttl=3600,
                max_size=1000,
                namespace="whatsapp_api"
            )
            logger.info("Cache configurado para usar memoria (Redis no disponible)")
        
        _cache_manager = CacheManager(config)
    return _cache_manager

def set_cache_manager(cache_manager: CacheManager):
    """Set global cache manager instance"""
    global _cache_manager
    _cache_manager = cache_manager

# Cache utilities
async def warm_cache(keys_and_values: Dict[str, Any], ttl: int = 3600):
    """Warm cache with multiple key-value pairs"""
    cache_manager = get_cache_manager()
    
    for key, value in keys_and_values.items():
        await cache_manager.set(key, value, ttl)

async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    cache_manager = get_cache_manager()
    return await cache_manager.get_stats()

async def clear_all_cache():
    """Clear all cache entries"""
    cache_manager = get_cache_manager()
    return await cache_manager.clear()
