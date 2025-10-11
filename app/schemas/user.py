"""
Esquemas de usuario
"""
from pydantic import Field
from typing import Optional
from datetime import datetime
from .common import BaseSchema


class UserBase(BaseSchema):
    email: str
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseSchema):
    email: Optional[str] = None
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
