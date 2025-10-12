"""
Schemas de usuario para validación de datos
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


class UserBase(BaseModel):
    """Schema base para usuario"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "es"
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username debe tener al menos 3 caracteres')
        if not v.isalnum():
            raise ValueError('Username solo puede contener letras y números')
        return v.lower()
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Número de teléfono debe empezar con +')
        return v


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str
    is_superuser: bool = False
    is_staff: bool = False
    is_active: bool = True
    is_verified: bool = False
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Contraseña debe tener al menos 8 caracteres')
        return v


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    is_superuser: Optional[bool] = None
    is_staff: Optional[bool] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v and len(v) < 3:
            raise ValueError('Username debe tener al menos 3 caracteres')
        if v and not v.isalnum():
            raise ValueError('Username solo puede contener letras y números')
        return v.lower() if v else v
    
    @validator('password')
    def validate_password(cls, v):
        if v and len(v) < 8:
            raise ValueError('Contraseña debe tener al menos 8 caracteres')
        return v


class UserResponse(UserBase):
    """Schema para respuesta de usuario"""
    id: int
    is_superuser: bool
    is_staff: bool
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema para login de usuario"""
    email: EmailStr
    password: str


class UserPasswordReset(BaseModel):
    """Schema para reset de contraseña"""
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Contraseña debe tener al menos 8 caracteres')
        return v


class UserInDB(UserResponse):
    """Schema para usuario en base de datos (incluye contraseña hasheada)"""
    hashed_password: str


# Alias para compatibilidad
User = UserResponse


class UserStats(BaseModel):
    """Schema para estadísticas de usuarios"""
    total_users: int
    active_users: int
    inactive_users: int
    superusers: int
    staff_users: int
    verified_users: int
    unverified_users: int