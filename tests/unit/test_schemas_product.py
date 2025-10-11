"""
Tests unitarios para schemas de productos
"""
import pytest
from pydantic import ValidationError
from app.schemas.product import (
    CategoryBase, CategoryCreate, CategoryUpdate, Category,
    ProductBase, ProductCreate, ProductUpdate, Product
)


class TestCategorySchemas:
    """Test Category schemas functionality"""
    
    def test_category_base_valid(self):
        """Test valid CategoryBase"""
        category = CategoryBase(
            name="Electronics",
            description="Electronic products"
        )
        
        assert category.name == "Electronics"
        assert category.description == "Electronic products"
    
    def test_category_base_minimal(self):
        """Test CategoryBase with minimal data"""
        category = CategoryBase(name="Electronics")
        
        assert category.name == "Electronics"
        assert category.description is None
    
    def test_category_base_invalid_name(self):
        """Test CategoryBase with invalid name"""
        with pytest.raises(ValidationError):
            CategoryBase(name="")  # Empty name
        
        with pytest.raises(ValidationError):
            CategoryBase(name="a" * 101)  # Too long
    
    def test_category_create_valid(self):
        """Test valid CategoryCreate"""
        category = CategoryCreate(
            name="Electronics",
            description="Electronic products",
            slug="electronics"
        )
        
        assert category.name == "Electronics"
        assert category.description == "Electronic products"
        assert category.slug == "electronics"
    
    def test_category_update_partial(self):
        """Test CategoryUpdate with partial data"""
        category = CategoryUpdate(
            name="Updated Electronics",
            slug="updated-electronics"
        )
        
        assert category.name == "Updated Electronics"
        assert category.slug == "updated-electronics"
        assert category.description is None
    
    def test_category_with_id(self):
        """Test Category with ID"""
        from datetime import datetime
        
        category = Category(
            id=1,
            name="Electronics",
            description="Electronic products",
            slug="electronics",
            created_at=datetime.now()
        )
        
        assert category.id == 1
        assert category.name == "Electronics"
        assert category.slug == "electronics"


class TestProductSchemas:
    """Test Product schemas functionality"""
    
    def test_product_base_valid(self):
        """Test valid ProductBase"""
        product = ProductBase(
            name="Smartphone",
            description="Latest smartphone",
            price=50000,  # $500.00 in cents
            category_id=1,
            image_url="https://example.com/image.jpg",
            stock_quantity=10,
            is_available=True
        )
        
        assert product.name == "Smartphone"
        assert product.description == "Latest smartphone"
        assert product.price == 50000
        assert product.category_id == 1
        assert product.image_url == "https://example.com/image.jpg"
        assert product.stock_quantity == 10
        assert product.is_available is True
    
    def test_product_base_minimal(self):
        """Test ProductBase with minimal data"""
        product = ProductBase(
            name="Smartphone",
            price=50000
        )
        
        assert product.name == "Smartphone"
        assert product.price == 50000
        assert product.description is None
        assert product.category_id is None
        assert product.image_url is None
        assert product.stock_quantity == 0
        assert product.is_available is True
    
    def test_product_base_invalid_price(self):
        """Test ProductBase with invalid price"""
        with pytest.raises(ValidationError):
            ProductBase(
                name="Smartphone",
                price=0  # Price must be > 0
            )
        
        with pytest.raises(ValidationError):
            ProductBase(
                name="Smartphone",
                price=-100  # Negative price
            )
    
    def test_product_base_invalid_stock(self):
        """Test ProductBase with invalid stock"""
        with pytest.raises(ValidationError):
            ProductBase(
                name="Smartphone",
                price=50000,
                stock_quantity=-1  # Negative stock
            )
    
    def test_product_create_valid(self):
        """Test valid ProductCreate"""
        product = ProductCreate(
            name="Smartphone",
            description="Latest smartphone",
            price=50000,
            category_id=1,
            image_url="https://example.com/image.jpg",
            stock_quantity=10
        )
        
        assert product.name == "Smartphone"
        assert product.price == 50000
        assert product.stock_quantity == 10
    
    def test_product_update_partial(self):
        """Test ProductUpdate with partial data"""
        product = ProductUpdate(
            name="Updated Smartphone",
            price=45000,
            is_available=False
        )
        
        assert product.name == "Updated Smartphone"
        assert product.price == 45000
        assert product.is_available is False
        assert product.description is None
    
    def test_product_with_id(self):
        """Test Product with ID"""
        from datetime import datetime
        
        product = Product(
            id=1,
            name="Smartphone",
            description="Latest smartphone",
            price=50000,
            category_id=1,
            image_url="https://example.com/image.jpg",
            stock_quantity=10,
            is_available=True,
            created_at=datetime.now()
        )
        
        assert product.id == 1
        assert product.name == "Smartphone"
        assert product.price == 50000
        assert product.stock_quantity == 10
