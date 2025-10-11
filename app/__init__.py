"""
Archivo __init__.py principal de la aplicación
"""
from .core.config import settings
from .models import BaseModel, User, Category, Product
from .schemas import User, Product, Token, UserCreate, ProductCreate
from .services import UserService, ProductService

__all__ = [
    "settings",
    "BaseModel", "User", "Category", "Product",
    "Token", "UserCreate", "ProductCreate",
    "UserService", "ProductService"
]
