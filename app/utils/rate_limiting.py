"""
Sistema básico de rate limiting para FastAPI
"""
import time
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Middleware básico de rate limiting para FastAPI"""
    
    def __init__(self, app, default_rule: str = "api_global"):
        self.app = app
        self.default_rule = default_rule
        self.requests: Dict[str, list] = {}
        self.limit = 1000  # requests per hour
        self.window = 3600  # 1 hour
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extraer IP del cliente
        client_ip = self._get_client_ip(scope)
        current_time = time.time()
        
        # Limpiar requests antiguos
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < self.window
            ]
        else:
            self.requests[client_ip] = []
        
        # Verificar rate limit
        if len(self.requests[client_ip]) >= self.limit:
            # Enviar respuesta de rate limit
            response_body = b'{"error": "Rate limit exceeded", "message": "Too many requests. Please try again later."}'
            
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"retry-after", b"3600")
                ]
            })
            
            await send({
                "type": "http.response.body",
                "body": response_body
            })
            return
        
        # Agregar request actual
        self.requests[client_ip].append(current_time)
        
        # Agregar headers de rate limit
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                remaining = self.limit - len(self.requests[client_ip])
                headers.extend([
                    (b"x-rate-limit-limit", str(self.limit).encode()),
                    (b"x-rate-limit-remaining", str(remaining).encode()),
                    (b"x-rate-limit-reset", str(int(current_time + self.window)).encode())
                ])
                message["headers"] = headers
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
    
    def _get_client_ip(self, scope) -> str:
        """Extraer IP del cliente"""
        headers = dict(scope.get("headers", []))
        
        # Verificar IP forwarded
        if b"x-forwarded-for" in headers:
            return headers[b"x-forwarded-for"].decode().split(",")[0].strip()
        
        # Verificar IP real
        if b"x-real-ip" in headers:
            return headers[b"x-real-ip"].decode()
        
        # Fallback a dirección del cliente
        client = scope.get("client")
        if client:
            return client[0]
        
        return "unknown"
