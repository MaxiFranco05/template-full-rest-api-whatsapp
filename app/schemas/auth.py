"""
Esquemas de autenticación
"""
from pydantic import Field
from typing import Optional
from .common import BaseSchema


class Token(BaseSchema):
    access_token: str
    token_type: str


class TokenData(BaseSchema):
    username: Optional[str] = None


class UserLogin(BaseSchema):
    username: str
    password: str
