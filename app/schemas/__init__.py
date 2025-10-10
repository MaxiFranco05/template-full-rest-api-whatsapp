"""
Esquemas Pydantic para validación de datos
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Esquemas base
class BaseSchema(BaseModel):
    """Esquema base con configuración común"""
    class Config:
        from_attributes = True


# Esquemas de Usuario
class UserBase(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class User(UserInDB):
    pass


# Esquemas de Autenticación
class Token(BaseSchema):
    access_token: str
    token_type: str


class TokenData(BaseSchema):
    username: Optional[str] = None


class UserLogin(BaseSchema):
    username: str
    password: str


# Esquemas de Categoría
class CategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    slug: str = Field(..., min_length=1, max_length=100)


class CategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=100)


class Category(CategoryBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# Esquemas de Producto
class ProductBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: int = Field(..., gt=0)  # Precio en centavos
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    stock_quantity: int = Field(default=0, ge=0)
    is_available: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Esquemas de respuesta con paginación
class PaginatedResponse(BaseSchema):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int
