"""
Modelos de productos y categorías
"""
from sqlalchemy import Column, String, Integer, Boolean, Text
from .base import BaseModel


class Category(BaseModel):
    """Modelo de categoría de productos"""
    __tablename__ = "categories"
    
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)


class Product(BaseModel):
    """Modelo de producto"""
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Precio en centavos
    category_id = Column(Integer, nullable=True)
    image_url = Column(String(500), nullable=True)
    stock_quantity = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
