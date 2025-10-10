"""
Archivo __init__.py principal de la aplicación
"""
from .core import settings
from .models import BaseModel, User, Category, Product
from .schemas import *
from .services import UserService, ProductService
from .utils import *

__all__ = [
    "settings",
    "BaseModel", "User", "Category", "Product",
    "UserService", "ProductService"
]
