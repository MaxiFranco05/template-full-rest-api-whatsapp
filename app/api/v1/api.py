"""
Router principal de la API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth_router, products_router, whatsapp_router, users_router

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
