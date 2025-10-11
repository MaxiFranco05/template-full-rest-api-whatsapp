# Performance Optimization Module

"""
Performance optimization utilities and middleware for Business API Template
"""

import time
import functools
import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import asynccontextmanager
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    function_name: str
    execution_time: float
    memory_usage: Optional[float] = None
    cache_hit: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.thresholds = {
            'slow_query': 1.0,  # 1 second
            'slow_api': 0.5,    # 500ms
            'slow_function': 0.1 # 100ms
        }
    
    def add_metric(self, metric: PerformanceMetrics):
        """Add performance metric"""
        self.metrics.append(metric)
        
        # Log slow operations
        if metric.execution_time > self.thresholds.get('slow_function', 0.1):
            logger.warning(
                f"Slow operation detected: {metric.function_name} "
                f"took {metric.execution_time:.3f}s"
            )
    
    def get_stats(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics"""
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
            "total_time": sum(execution_times),
            "cache_hit_rate": sum(1 for m in filtered_metrics if m.cache_hit) / len(filtered_metrics)
        }
    
    def get_slow_operations(self, threshold: float = 1.0) -> List[PerformanceMetrics]:
        """Get operations slower than threshold"""
        return [m for m in self.metrics if m.execution_time > threshold]

# Global performance monitor
performance_monitor = PerformanceMonitor()

def performance_timer(func_name: Optional[str] = None, cache_hit: bool = False):
    """Decorator to measure function execution time"""
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
                    execution_time=execution_time,
                    cache_hit=cache_hit
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
                    execution_time=execution_time,
                    cache_hit=cache_hit
                )
                performance_monitor.add_metric(metric)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class ConnectionPool:
    """Optimized connection pool for database operations"""
    
    def __init__(self, max_connections: int = 20, min_connections: int = 5):
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connections: List[Any] = []
        self.available_connections: List[Any] = []
        self.busy_connections: List[Any] = []
        self._lock = asyncio.Lock()
    
    async def get_connection(self):
        """Get a connection from the pool"""
        async with self._lock:
            if self.available_connections:
                conn = self.available_connections.pop()
                self.busy_connections.append(conn)
                return conn
            
            if len(self.connections) < self.max_connections:
                # Create new connection
                conn = await self._create_connection()
                self.connections.append(conn)
                self.busy_connections.append(conn)
                return conn
            
            # Wait for available connection
            while not self.available_connections:
                await asyncio.sleep(0.01)
            
            conn = self.available_connections.pop()
            self.busy_connections.append(conn)
            return conn
    
    async def return_connection(self, conn):
        """Return connection to the pool"""
        async with self._lock:
            if conn in self.busy_connections:
                self.busy_connections.remove(conn)
                self.available_connections.append(conn)
    
    async def _create_connection(self):
        """Create a new database connection"""
        # This would be implemented based on your database driver
        pass

class QueryOptimizer:
    """Optimize database queries"""
    
    @staticmethod
    def optimize_select_query(query: str, limit: Optional[int] = None, 
                            offset: Optional[int] = None) -> str:
        """Optimize SELECT queries"""
        # Add LIMIT if not present and limit is specified
        if limit and "LIMIT" not in query.upper():
            query += f" LIMIT {limit}"
        
        # Add OFFSET if specified
        if offset and "OFFSET" not in query.upper():
            query += f" OFFSET {offset}"
        
        return query
    
    @staticmethod
    def add_index_hints(query: str, table: str, index: str) -> str:
        """Add index hints to queries"""
        # This would be database-specific
        return query
    
    @staticmethod
    def optimize_joins(query: str) -> str:
        """Optimize JOIN operations"""
        # Add query optimization logic here
        return query

class MemoryOptimizer:
    """Memory optimization utilities"""
    
    @staticmethod
    def optimize_list_comprehension(data: List[Any], 
                                  filter_func: Optional[Callable] = None,
                                  map_func: Optional[Callable] = None) -> List[Any]:
        """Optimize list operations"""
        if filter_func and map_func:
            return [map_func(item) for item in data if filter_func(item)]
        elif filter_func:
            return [item for item in data if filter_func(item)]
        elif map_func:
            return [map_func(item) for item in data]
        else:
            return data
    
    @staticmethod
    def chunked_processing(data: List[Any], chunk_size: int = 1000) -> List[List[Any]]:
        """Process data in chunks to reduce memory usage"""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
    
    @staticmethod
    def optimize_dict_operations(data: Dict[str, Any], 
                                keys_to_keep: Optional[List[str]] = None) -> Dict[str, Any]:
        """Optimize dictionary operations"""
        if keys_to_keep:
            return {k: v for k, v in data.items() if k in keys_to_keep}
        return data

class AsyncOptimizer:
    """Async operation optimizations"""
    
    @staticmethod
    async def batch_async_operations(operations: List[Callable], 
                                   batch_size: int = 10) -> List[Any]:
        """Execute async operations in batches"""
        results = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        
        return results
    
    @staticmethod
    async def timeout_async_operation(operation: Callable, 
                                    timeout: float = 30.0) -> Any:
        """Execute async operation with timeout"""
        try:
            return await asyncio.wait_for(operation(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Operation timed out after {timeout}s")
            raise
    
    @staticmethod
    async def retry_async_operation(operation: Callable, 
                                  max_retries: int = 3,
                                  delay: float = 1.0) -> Any:
        """Retry async operation on failure"""
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                logger.warning(f"Operation failed (attempt {attempt + 1}): {e}")
                await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff

class ResponseOptimizer:
    """Optimize API responses"""
    
    @staticmethod
    def compress_response(data: Any, compression_level: int = 6) -> bytes:
        """Compress response data"""
        import gzip
        import json
        
        if isinstance(data, (dict, list)):
            json_data = json.dumps(data).encode('utf-8')
        else:
            json_data = str(data).encode('utf-8')
        
        return gzip.compress(json_data, compresslevel=compression_level)
    
    @staticmethod
    def paginate_response(data: List[Any], page: int = 1, 
                         size: int = 20) -> Dict[str, Any]:
        """Paginate response data"""
        total = len(data)
        start = (page - 1) * size
        end = start + size
        
        return {
            "items": data[start:end],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    @staticmethod
    def filter_response_fields(data: Dict[str, Any], 
                             fields: List[str]) -> Dict[str, Any]:
        """Filter response fields"""
        return {k: v for k, v in data.items() if k in fields}

# Performance middleware for FastAPI
class PerformanceMiddleware:
    """FastAPI middleware for performance monitoring"""
    
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
                
                # Add performance headers
                headers = list(message.get("headers", []))
                headers.append((b"x-response-time", f"{execution_time:.3f}".encode()))
                headers.append((b"x-performance-monitor", b"enabled"))
                
                message["headers"] = headers
                
                # Log slow requests
                if execution_time > 1.0:
                    logger.warning(
                        f"Slow request: {scope['path']} took {execution_time:.3f}s"
                    )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# Utility functions
def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics"""
    return {
        "total_operations": len(performance_monitor.metrics),
        "slow_operations": len(performance_monitor.get_slow_operations()),
        "stats": performance_monitor.get_stats()
    }

def clear_performance_metrics():
    """Clear performance metrics"""
    performance_monitor.metrics.clear()

def log_performance_summary():
    """Log performance summary"""
    stats = get_performance_stats()
    logger.info(f"Performance Summary: {stats}")
