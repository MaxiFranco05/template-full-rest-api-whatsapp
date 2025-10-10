"""
Endpoints para productos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import Product, ProductCreate, ProductUpdate, PaginatedResponse
from app.services.product_service import ProductService
from app.api.v1.endpoints.auth import get_current_user
from app.schemas import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def get_products(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de productos con paginación"""
    product_service = ProductService(db)
    return product_service.get_products_paginated(
        page=page, size=size, category_id=category_id, search=search
    )


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtener producto por ID"""
    product_service = ProductService(db)
    product = product_service.get_product(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.post("/", response_model=Product)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nuevo producto (requiere autenticación)"""
    product_service = ProductService(db)
    return product_service.create_product(product)


@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar producto (requiere autenticación)"""
    product_service = ProductService(db)
    product = product_service.update_product(product_id, product_update)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar producto (requiere autenticación)"""
    product_service = ProductService(db)
    success = product_service.delete_product(product_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {"message": "Product deleted successfully"}
