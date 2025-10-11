"""
Utilidades y helpers para la aplicación
"""
import re
import secrets
import string
from typing import Optional
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