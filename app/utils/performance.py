"""
Utilidades de performance para monitoreo de funciones
"""
import time
import functools
import asyncio
from typing import Any, Callable, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Métricas de performance"""
    function_name: str
    execution_time: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PerformanceMonitor:
    """Monitor de métricas de performance"""
    
    def __init__(self):
        self.metrics: list[PerformanceMetrics] = []
        self.slow_threshold = 1.0  # 1 segundo
    
    def add_metric(self, metric: PerformanceMetrics):
        """Agregar métrica de performance"""
        self.metrics.append(metric)
        
        # Log operaciones lentas
        if metric.execution_time > self.slow_threshold:
            logger.warning(
                f"Operación lenta detectada: {metric.function_name} "
                f"tomó {metric.execution_time:.3f}s"
            )
    
    def get_stats(self, function_name: Optional[str] = None) -> dict[str, Any]:
        """Obtener estadísticas de performance"""
        if function_name:
            filtered_metrics = [m for m in self.metrics if m.function_name == function_name]
        else:
            filtered_metrics = self.metrics
        
        if not filtered_metrics:
            return {"count": 0}
        
        execution_times = [m.execution_time for m in filtered_metrics]
        
        return {
            "count": len(filtered_metrics),
            "avg_time": sum(execution_times) / len(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "total_time": sum(execution_times)
        }


# Monitor global de performance
performance_monitor = PerformanceMonitor()


def performance_timer(func_name: Optional[str] = None):
    """
    Decorador para medir tiempo de ejecución de funciones
    
    Args:
        func_name: Nombre personalizado para la función
        
    Returns:
        Decorador de función
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                name = func_name or f"{func.__module__}.{func.__name__}"
                
                metric = PerformanceMetrics(
                    function_name=name,
                    execution_time=execution_time
                )
                performance_monitor.add_metric(metric)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                name = func_name or f"{func.__module__}.{func.__name__}"
                
                metric = PerformanceMetrics(
                    function_name=name,
                    execution_time=execution_time
                )
                performance_monitor.add_metric(metric)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_performance_stats() -> dict[str, Any]:
    """
    Obtener estadísticas actuales de performance
    
    Returns:
        dict: Estadísticas de performance
    """
    return {
        "total_operations": len(performance_monitor.metrics),
        "slow_operations": len([m for m in performance_monitor.metrics if m.execution_time > performance_monitor.slow_threshold]),
        "stats": performance_monitor.get_stats()
    }


def clear_performance_metrics():
    """Limpiar métricas de performance"""
    performance_monitor.metrics.clear()


# Middleware para FastAPI
class PerformanceMiddleware:
    """FastAPI middleware para monitoreo de performance"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                execution_time = time.time() - start_time
                
                # Agregar headers de performance
                headers = list(message.get("headers", []))
                headers.append((b"x-response-time", f"{execution_time:.3f}".encode()))
                headers.append((b"x-performance-monitor", b"enabled"))
                
                message["headers"] = headers
                
                # Log requests lentos
                if execution_time > 1.0:
                    logger.warning(
                        f"Request lento: {scope['path']} tomó {execution_time:.3f}s"
                    )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)