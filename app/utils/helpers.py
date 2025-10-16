"""
Utilidades y helpers para la aplicación
"""
import re
import secrets
import string
from typing import Optional, Union
from datetime import datetime


def generate_random_string(length: int = 32) -> str:
    """
    Generar string aleatorio seguro
    
    Args:
        length: Longitud del string a generar (default: 32)
        
    Returns:
        str: String aleatorio generado
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_slug(text: str) -> str:
    """
    Generar slug URL-friendly a partir de texto
    
    Args:
        text: Texto a convertir en slug
        
    Returns:
        str: Slug generado
    """
    # Convertir a minúsculas
    text = text.lower()
    # Reemplazar espacios y caracteres especiales con guiones
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    # Eliminar guiones al inicio y final
    return text.strip('-')


def validate_email(email: str) -> bool:
    """
    Validar formato de email usando regex
    
    Args:
        email: Email a validar
        
    Returns:
        bool: True si el email es válido, False en caso contrario
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_http_exception(
    status_code: int = 400,
    detail: str = "Bad Request"
):
    """
    Crear excepción HTTP personalizada
    
    Args:
        status_code: Código de estado HTTP (default: 400)
        detail: Mensaje de detalle del error
        
    Returns:
        HTTPException: Excepción HTTP configurada
    """
    try:
        from fastapi import HTTPException, status
        return HTTPException(status_code=status_code, detail=detail)
    except ImportError:
        # Si FastAPI no está disponible, crear una excepción básica
        class BasicHTTPException(Exception):
            def __init__(self, status_code: int, detail: str):
                self.status_code = status_code
                self.detail = detail
                super().__init__(detail)
        
        return BasicHTTPException(status_code=status_code, detail=detail)


def paginate_query(query, page: int = 1, size: int = 10):
    """
    Paginar consultas de base de datos
    
    Args:
        query: Consulta SQLAlchemy a paginar
        page: Número de página (default: 1)
        size: Tamaño de página (default: 10, max: 100)
        
    Returns:
        dict: Diccionario con items, total, página, tamaño y páginas
    """
    if page < 1:
        page = 1
    if size < 1 or size > 100:
        size = 10
    
    offset = (page - 1) * size
    total = query.count()
    items = query.offset(offset).limit(size).all()
    pages = (total + size - 1) // size
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }


def format_phone_number(phone: str) -> str:
    """
    Formatear número de teléfono para WhatsApp
    
    Args:
        phone: Número de teléfono a formatear
        
    Returns:
        str: Número formateado con código de país
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Add country code if missing
    if not digits.startswith('54') and len(digits) == 10:
        digits = '54' + digits
    
    return '+' + digits


def validate_phone_format(phone: str) -> bool:
    """
    Validar formato de número de teléfono
    
    Args:
        phone: Número de teléfono a validar
        
    Returns:
        bool: True si el formato es válido, False en caso contrario
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits) <= 15


# =============================================================================
# TIMESTAMP UTILITIES - Funciones para manejo consistente de timestamps
# =============================================================================

def get_current_utc_time() -> datetime:
    """
    Obtener el tiempo actual en UTC de manera consistente
    
    Returns:
        datetime: Timestamp actual en UTC
    """
    return datetime.utcnow()


def parse_timestamp_to_utc(timestamp: Union[str, int, datetime]) -> datetime:
    """
    Convertir cualquier formato de timestamp a UTC de manera consistente
    
    Args:
        timestamp: Puede ser string ISO, int Unix timestamp, o datetime
        
    Returns:
        datetime: Timestamp en UTC
        
    Raises:
        ValueError: Si el timestamp no es válido
    """
    if isinstance(timestamp, datetime):
        # Si ya es datetime, asegurar que esté en UTC
        if timestamp.tzinfo is None:
            # Si no tiene timezone info, asumir que es UTC
            return timestamp
        else:
            # Convertir a UTC
            return timestamp.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    
    elif isinstance(timestamp, str):
        try:
            # Intentar parsear como ISO format
            if timestamp.endswith('Z'):
                timestamp = timestamp.replace('Z', '+00:00')
            return datetime.fromisoformat(timestamp).astimezone(datetime.timezone.utc).replace(tzinfo=None)
        except ValueError:
            try:
                # Intentar como Unix timestamp
                return datetime.utcfromtimestamp(int(timestamp))
            except (ValueError, TypeError):
                raise ValueError(f"Timestamp string inválido: {timestamp}")
    
    elif isinstance(timestamp, (int, float)):
        try:
            # Unix timestamp
            return datetime.utcfromtimestamp(int(timestamp))
        except (ValueError, TypeError):
            raise ValueError(f"Timestamp numérico inválido: {timestamp}")
    
    else:
        raise ValueError(f"Tipo de timestamp no soportado: {type(timestamp)}")


def format_timestamp_for_logging(timestamp: datetime) -> str:
    """
    Formatear timestamp para logging de manera consistente
    
    Args:
        timestamp: datetime object
        
    Returns:
        str: Timestamp formateado para logs
    """
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def calculate_time_difference_seconds(timestamp1: datetime, timestamp2: datetime) -> float:
    """
    Calcular diferencia temporal entre dos timestamps en segundos
    
    Args:
        timestamp1: Primer timestamp
        timestamp2: Segundo timestamp
        
    Returns:
        float: Diferencia en segundos (timestamp2 - timestamp1)
    """
    return (timestamp2 - timestamp1).total_seconds()


def is_timestamp_within_tolerance(
    message_timestamp: datetime, 
    reference_timestamp: datetime, 
    tolerance_seconds: int
) -> bool:
    """
    Verificar si un timestamp está dentro de la tolerancia temporal
    
    Args:
        message_timestamp: Timestamp del mensaje
        reference_timestamp: Timestamp de referencia (ej: último mensaje API)
        tolerance_seconds: Tolerancia en segundos (ej: 300 para 5 minutos)
        
    Returns:
        bool: True si está dentro de la tolerancia
    """
    time_diff = calculate_time_difference_seconds(reference_timestamp, message_timestamp)
    tolerance_threshold = -tolerance_seconds  # Negativo para permitir mensajes "antiguos"
    
    return time_diff >= tolerance_threshold