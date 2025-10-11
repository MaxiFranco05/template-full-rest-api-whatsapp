"""
Esquemas base y comunes
"""
from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Esquema base con configuración común"""
    class Config:
        from_attributes = True


class PaginatedResponse(BaseSchema):
    """Esquema de respuesta con paginación"""
    items: list
    total: int
    page: int
    size: int
    pages: int
