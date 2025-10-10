"""
Archivo __init__.py para endpoints
"""
from .auth import router as auth_router
from .products import router as products_router
from .whatsapp import router as whatsapp_router

__all__ = ["auth_router", "products_router", "whatsapp_router"]
