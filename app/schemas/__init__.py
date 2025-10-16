"""
Esquemas Pydantic para validación de datos
"""
from .common import BaseSchema, PaginatedResponse
from .user import User, UserCreate, UserUpdate, UserInDB
from .auth import Token, TokenData, UserLogin
from .product import Category, CategoryCreate, CategoryUpdate, Product, ProductCreate, ProductUpdate

__all__ = [
    "BaseSchema",
    "PaginatedResponse",
    "User",
    "UserCreate", 
    "UserUpdate",
    "UserInDB",
    "Token",
    "TokenData",
    "UserLogin",
    "Category",
    "CategoryCreate",
    "CategoryUpdate", 
    "Product",
    "ProductCreate",
    "ProductUpdate"
]