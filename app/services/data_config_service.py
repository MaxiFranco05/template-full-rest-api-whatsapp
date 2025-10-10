"""
Data Configuration Service
Handles dynamic data configuration for WhatsApp messages using existing services
"""
from typing import Dict, Any, List, Optional
import logging
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)


class DataConfigService:
    """Service for managing dynamic data configuration using existing database services"""
    
    def __init__(self):
        self.db = next(get_db())
        self.product_service = ProductService(self.db)
        self.services = []  # Services can be added later if needed
        self.company_info = {}
    
    def set_services(self, services: List[Dict[str, Any]]):
        """Set services catalog (for future use)"""
        self.services = services
        logger.info(f"Services catalog updated: {len(services)} items")
    
    def set_company_info(self, company_info: Dict[str, str]):
        """Set company information"""
        self.company_info = company_info
        logger.info("Company information updated")
    
    def get_products(self) -> List[Dict[str, Any]]:
        """Get products from database"""
        try:
            products_response = self.product_service.get_products_paginated(page=1, size=100)
            products = []
            
            for product in products_response.items:
                products.append({
                    "id": str(product.id),
                    "name": product.name,
                    "price": str(product.price),
                    "description": product.description or ""
                })
            
            return products
        except Exception as e:
            logger.error(f"Error getting products from database: {e}")
            return []
    
    def get_services(self) -> List[Dict[str, Any]]:
        """Get services catalog"""
        return self.services
    
    def get_company_info(self) -> Dict[str, str]:
        """Get company information"""
        return self.company_info
    
    def has_products(self) -> bool:
        """Check if products exist in database"""
        try:
            products_response = self.product_service.get_products_paginated(page=1, size=1)
            return products_response.total > 0
        except Exception as e:
            logger.error(f"Error checking products: {e}")
            return False
    
    def has_services(self) -> bool:
        """Check if services catalog exists"""
        return len(self.services) > 0
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID from database"""
        try:
            product = self.product_service.get_product(int(product_id))
            if product:
                return {
                    "id": str(product.id),
                    "name": product.name,
                    "price": str(product.price),
                    "description": product.description or ""
                }
            return None
        except Exception as e:
            logger.error(f"Error getting product by ID {product_id}: {e}")
            return None
    
    def get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get service by ID"""
        for service in self.services:
            if service.get('id') == service_id:
                return service
        return None


# Global instance
data_config = DataConfigService()


def get_data_config() -> DataConfigService:
    """Get data configuration service instance"""
    return data_config