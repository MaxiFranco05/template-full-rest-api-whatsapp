"""
Servicio para manejo de productos
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate, PaginatedResponse
from app.utils import paginate_query


class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Obtener producto por ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtener lista de productos"""
        return self.db.query(Product).offset(skip).limit(limit).all()
    
    def get_products_paginated(
        self, 
        page: int = 1, 
        size: int = 10,
        category_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> PaginatedResponse:
        """Obtener productos con paginación y filtros"""
        query = self.db.query(Product).filter(Product.is_active == True)
        
        # Filtrar por categoría
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # Buscar por nombre o descripción
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        return paginate_query(query, page, size)
    
    def create_product(self, product: ProductCreate) -> Product:
        """Crear nuevo producto"""
        db_product = Product(**product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def update_product(self, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        """Actualizar producto"""
        db_product = self.get_product(product_id)
        if not db_product:
            return None
        
        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def delete_product(self, product_id: int) -> bool:
        """Eliminar producto (soft delete)"""
        db_product = self.get_product(product_id)
        if not db_product:
            return False
        
        db_product.is_active = False
        self.db.commit()
        return True
    
    def get_available_products(self) -> List[Product]:
        """Obtener productos disponibles"""
        return self.db.query(Product).filter(
            Product.is_active == True,
            Product.is_available == True,
            Product.stock_quantity > 0
        ).all()
