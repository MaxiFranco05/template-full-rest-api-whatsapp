# Optimization Configuration

"""
Configuration settings for performance optimizations
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum

class CacheBackend(str, Enum):
    """Cache backend options"""
    MEMORY = "memory"
    REDIS = "redis"
    FILE = "file"

class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithm options"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

class OptimizationSettings(BaseModel):
    """Optimization configuration settings"""
    
    # Performance monitoring
    ENABLE_PERFORMANCE_MONITORING: bool = True
    PERFORMANCE_LOG_SLOW_OPERATIONS: bool = True
    PERFORMANCE_SLOW_THRESHOLD: float = 1.0  # seconds
    
    # Caching
    ENABLE_CACHING: bool = True
    CACHE_BACKEND: CacheBackend = CacheBackend.MEMORY
    CACHE_DEFAULT_TTL: int = 3600  # 1 hour
    CACHE_MAX_SIZE: int = 1000
    CACHE_COMPRESSION: bool = False
    CACHE_SERIALIZE_METHOD: str = "json"  # json, pickle
    
    # Redis cache settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Rate limiting
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_ALGORITHM: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    
    # API rate limits
    API_RATE_LIMIT: int = 1000  # requests per hour
    API_RATE_WINDOW: int = 3600  # 1 hour
    
    # User rate limits
    USER_RATE_LIMIT: int = 100  # requests per hour
    USER_RATE_WINDOW: int = 3600  # 1 hour
    USER_RATE_BURST: int = 20  # burst capacity
    
    # IP rate limits
    IP_RATE_LIMIT: int = 200  # requests per hour
    IP_RATE_WINDOW: int = 3600  # 1 hour
    
    # Authentication rate limits
    AUTH_RATE_LIMIT: int = 5  # attempts per 15 minutes
    AUTH_RATE_WINDOW: int = 900  # 15 minutes
    
    # WhatsApp webhook rate limits
    WEBHOOK_RATE_LIMIT: int = 1000  # requests per hour
    WEBHOOK_RATE_WINDOW: int = 3600  # 1 hour
    WEBHOOK_RATE_BURST: int = 100  # burst capacity
    
    # Database optimization
    ENABLE_DB_CONNECTION_POOLING: bool = True
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # Query optimization
    ENABLE_QUERY_OPTIMIZATION: bool = True
    QUERY_TIMEOUT: int = 30  # seconds
    QUERY_CACHE_TTL: int = 300  # 5 minutes
    
    # Response optimization
    ENABLE_RESPONSE_COMPRESSION: bool = True
    RESPONSE_COMPRESSION_LEVEL: int = 6
    ENABLE_RESPONSE_PAGINATION: bool = True
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Memory optimization
    ENABLE_MEMORY_OPTIMIZATION: bool = True
    MEMORY_CHUNK_SIZE: int = 1000
    MEMORY_CLEANUP_INTERVAL: int = 3600  # 1 hour
    
    # Async optimization
    ENABLE_ASYNC_OPTIMIZATION: bool = True
    ASYNC_BATCH_SIZE: int = 10
    ASYNC_TIMEOUT: int = 30  # seconds
    ASYNC_MAX_RETRIES: int = 3
    ASYNC_RETRY_DELAY: float = 1.0  # seconds
    
    # Logging optimization
    ENABLE_STRUCTURED_LOGGING: bool = True
    LOG_PERFORMANCE_METRICS: bool = True
    LOG_CACHE_STATS: bool = True
    LOG_RATE_LIMIT_STATS: bool = True

# Global optimization settings instance
optimization_settings = OptimizationSettings()

# Cache configuration
CACHE_CONFIG = {
    "backend": optimization_settings.CACHE_BACKEND.value,
    "ttl": optimization_settings.CACHE_DEFAULT_TTL,
    "max_size": optimization_settings.CACHE_MAX_SIZE,
    "compression": optimization_settings.CACHE_COMPRESSION,
    "serialize_method": optimization_settings.CACHE_SERIALIZE_METHOD,
    "namespace": "business_api"
}

# Rate limiting configuration
RATE_LIMIT_RULES = {
    "api_global": {
        "algorithm": optimization_settings.RATE_LIMIT_ALGORITHM.value,
        "limit": optimization_settings.API_RATE_LIMIT,
        "window": optimization_settings.API_RATE_WINDOW,
        "scope": "global",
        "message": "API rate limit exceeded. Please try again later."
    },
    "user_requests": {
        "algorithm": "token_bucket",
        "limit": optimization_settings.USER_RATE_LIMIT,
        "window": optimization_settings.USER_RATE_WINDOW,
        "burst": optimization_settings.USER_RATE_BURST,
        "scope": "per_user",
        "message": "User rate limit exceeded. Please slow down your requests."
    },
    "ip_requests": {
        "algorithm": "sliding_window",
        "limit": optimization_settings.IP_RATE_LIMIT,
        "window": optimization_settings.IP_RATE_WINDOW,
        "scope": "per_ip",
        "message": "IP rate limit exceeded. Please try again later."
    },
    "auth_attempts": {
        "algorithm": "fixed_window",
        "limit": optimization_settings.AUTH_RATE_LIMIT,
        "window": optimization_settings.AUTH_RATE_WINDOW,
        "scope": "per_ip",
        "message": "Too many authentication attempts. Please try again later."
    },
    "whatsapp_webhook": {
        "algorithm": "token_bucket",
        "limit": optimization_settings.WEBHOOK_RATE_LIMIT,
        "window": optimization_settings.WEBHOOK_RATE_WINDOW,
        "burst": optimization_settings.WEBHOOK_RATE_BURST,
        "scope": "per_ip",
        "message": "WhatsApp webhook rate limit exceeded."
    }
}

# Database optimization configuration
DB_OPTIMIZATION_CONFIG = {
    "pool_size": optimization_settings.DB_POOL_SIZE,
    "max_overflow": optimization_settings.DB_MAX_OVERFLOW,
    "pool_timeout": optimization_settings.DB_POOL_TIMEOUT,
    "pool_recycle": optimization_settings.DB_POOL_RECYCLE,
    "query_timeout": optimization_settings.QUERY_TIMEOUT,
    "query_cache_ttl": optimization_settings.QUERY_CACHE_TTL
}

# Response optimization configuration
RESPONSE_OPTIMIZATION_CONFIG = {
    "compression_enabled": optimization_settings.ENABLE_RESPONSE_COMPRESSION,
    "compression_level": optimization_settings.RESPONSE_COMPRESSION_LEVEL,
    "pagination_enabled": optimization_settings.ENABLE_RESPONSE_PAGINATION,
    "default_page_size": optimization_settings.DEFAULT_PAGE_SIZE,
    "max_page_size": optimization_settings.MAX_PAGE_SIZE
}

# Memory optimization configuration
MEMORY_OPTIMIZATION_CONFIG = {
    "chunk_size": optimization_settings.MEMORY_CHUNK_SIZE,
    "cleanup_interval": optimization_settings.MEMORY_CLEANUP_INTERVAL,
    "enable_optimization": optimization_settings.ENABLE_MEMORY_OPTIMIZATION
}

# Async optimization configuration
ASYNC_OPTIMIZATION_CONFIG = {
    "batch_size": optimization_settings.ASYNC_BATCH_SIZE,
    "timeout": optimization_settings.ASYNC_TIMEOUT,
    "max_retries": optimization_settings.ASYNC_MAX_RETRIES,
    "retry_delay": optimization_settings.ASYNC_RETRY_DELAY,
    "enable_optimization": optimization_settings.ENABLE_ASYNC_OPTIMIZATION
}

# Performance monitoring configuration
PERFORMANCE_MONITORING_CONFIG = {
    "enabled": optimization_settings.ENABLE_PERFORMANCE_MONITORING,
    "log_slow_operations": optimization_settings.PERFORMANCE_LOG_SLOW_OPERATIONS,
    "slow_threshold": optimization_settings.PERFORMANCE_SLOW_THRESHOLD,
    "log_metrics": optimization_settings.LOG_PERFORMANCE_METRICS
}

# Logging optimization configuration
LOGGING_OPTIMIZATION_CONFIG = {
    "structured_logging": optimization_settings.ENABLE_STRUCTURED_LOGGING,
    "log_performance": optimization_settings.LOG_PERFORMANCE_METRICS,
    "log_cache_stats": optimization_settings.LOG_CACHE_STATS,
    "log_rate_limit_stats": optimization_settings.LOG_RATE_LIMIT_STATS
}

def get_optimization_config() -> Dict[str, Any]:
    """Get complete optimization configuration"""
    return {
        "cache": CACHE_CONFIG,
        "rate_limiting": RATE_LIMIT_RULES,
        "database": DB_OPTIMIZATION_CONFIG,
        "response": RESPONSE_OPTIMIZATION_CONFIG,
        "memory": MEMORY_OPTIMIZATION_CONFIG,
        "async": ASYNC_OPTIMIZATION_CONFIG,
        "performance": PERFORMANCE_MONITORING_CONFIG,
        "logging": LOGGING_OPTIMIZATION_CONFIG
    }

def is_optimization_enabled(feature: str) -> bool:
    """Check if specific optimization feature is enabled"""
    feature_map = {
        "performance": optimization_settings.ENABLE_PERFORMANCE_MONITORING,
        "caching": optimization_settings.ENABLE_CACHING,
        "rate_limiting": optimization_settings.ENABLE_RATE_LIMITING,
        "db_pooling": optimization_settings.ENABLE_DB_CONNECTION_POOLING,
        "query_optimization": optimization_settings.ENABLE_QUERY_OPTIMIZATION,
        "response_compression": optimization_settings.ENABLE_RESPONSE_COMPRESSION,
        "response_pagination": optimization_settings.ENABLE_RESPONSE_PAGINATION,
        "memory_optimization": optimization_settings.ENABLE_MEMORY_OPTIMIZATION,
        "async_optimization": optimization_settings.ENABLE_ASYNC_OPTIMIZATION,
        "structured_logging": optimization_settings.ENABLE_STRUCTURED_LOGGING
    }
    
    return feature_map.get(feature, False)
