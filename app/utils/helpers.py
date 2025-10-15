"""
Utilidades y helpers para la aplicación
"""
import re
import secrets
import string
from typing import Optional, Union
from datetime import datetime
from fastapi import HTTPException, status


def generate_random_string(length: int = 32) -> str:
    """Generar string aleatorio"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_slug(text: str) -> str:
    """Generar slug a partir de texto"""
    # Convertir a minúsculas
    text = text.lower()
    # Reemplazar espacios y caracteres especiales con guiones
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    # Eliminar guiones al inicio y final
    return text.strip('-')


def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def cents_to_dollars(cents: int) -> float:
    """Convertir centavos a dólares"""
    return cents / 100


def dollars_to_cents(dollars: float) -> int:
    """Convertir dólares a centavos"""
    return int(dollars * 100)


def create_http_exception(
    status_code: int = status.HTTP_400_BAD_REQUEST,
    detail: str = "Bad Request"
) -> HTTPException:
    """Crear excepción HTTP personalizada"""
    return HTTPException(status_code=status_code, detail=detail)


def paginate_query(query, page: int = 1, size: int = 10):
    """Paginación de consultas"""
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
    """Format phone number for WhatsApp"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Add country code if missing
    if not digits.startswith('54') and len(digits) == 10:
        digits = '54' + digits
    
    return '+' + digits


def validate_phone_format(phone: str) -> bool:
    """Validate phone number format"""
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