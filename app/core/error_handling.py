"""
Sistema de manejo de errores profesional
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import traceback
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Excepción base de la aplicación"""
    
    def __init__(self, message: str, error_code: str = None, 
                 status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
                 details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class WhatsAppException(AppException):
    """Excepción específica para WhatsApp"""
    
    def __init__(self, message: str, error_code: str = None, 
                 phone_number: str = None, conversation_id: str = None):
        details = {}
        if phone_number:
            details['phone_number'] = phone_number
        if conversation_id:
            details['conversation_id'] = conversation_id
        
        super().__init__(
            message=message,
            error_code=error_code or "WHATSAPP_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class DatabaseException(AppException):
    """Excepción específica para base de datos"""
    
    def __init__(self, message: str, error_code: str = None, 
                 table: str = None, operation: str = None):
        details = {}
        if table:
            details['table'] = table
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message=message,
            error_code=error_code or "DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ValidationException(AppException):
    """Excepción específica para validación"""
    
    def __init__(self, message: str, field: str = None, 
                 value: Any = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationException(AppException):
    """Excepción específica para autenticación"""
    
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(AppException):
    """Excepción específica para autorización"""
    
    def __init__(self, message: str = "No tienes permisos para realizar esta acción"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )


class RateLimitException(AppException):
    """Excepción específica para límite de velocidad"""
    
    def __init__(self, message: str = "Límite de velocidad excedido", 
                 retry_after: int = None):
        details = {}
        if retry_after:
            details['retry_after'] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Dict[str, Any] = None,
    request_id: str = None
) -> JSONResponse:
    """Crear respuesta de error estandarizada"""
    
    error_response = {
        "error": {
            "code": error_code or "UNKNOWN_ERROR",
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status_code": status_code
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    if request_id:
        error_response["error"]["request_id"] = request_id
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Manejador de excepciones de la aplicación"""
    
    # Log del error
    logger.error(
        f"App Exception: {exc.message}",
        extra={
            'error_code': exc.error_code,
            'status_code': exc.status_code,
            'details': exc.details,
            'path': request.url.path,
            'method': request.method
        }
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Manejador de excepciones HTTP"""
    
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            'status_code': exc.status_code,
            'path': request.url.path,
            'method': request.method
        }
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}"
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Manejador de excepciones de validación"""
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation Error: {len(errors)} errores de validación",
        extra={
            'errors': errors,
            'path': request.url.path,
            'method': request.method
        }
    )
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Error de validación en los datos enviados",
        error_code="VALIDATION_ERROR",
        details={"validation_errors": errors}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador de excepciones generales"""
    
    # Log del error completo
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            'exception_type': type(exc).__name__,
            'path': request.url.path,
            'method': request.method,
            'traceback': traceback.format_exc()
        },
        exc_info=True
    )
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Error interno del servidor",
        error_code="INTERNAL_SERVER_ERROR"
    )


def register_exception_handlers(app):
    """Registrar todos los manejadores de excepciones"""
    
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


# Decorador para manejo de errores en funciones
def handle_errors(error_code: str = None, status_code: int = None):
    """Decorador para manejo automático de errores"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AppException:
                raise
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    extra={
                        'function': func.__name__,
                        'error_type': type(e).__name__
                    },
                    exc_info=True
                )
                raise AppException(
                    message=f"Error en {func.__name__}: {str(e)}",
                    error_code=error_code or "FUNCTION_ERROR",
                    status_code=status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return decorator
