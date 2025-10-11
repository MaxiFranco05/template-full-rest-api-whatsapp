"""
Tests unitarios para modelos de productos
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.product import Category, Product
from app.db.database import Base


class TestProductModels:
    """Test Product models functionality"""
    
    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_category_table_name(self):
        """Test Category table name"""
        assert Category.__tablename__ == "categories"
    
    def test_category_fields(self):
        """Test Category has all required fields"""
        columns = Category.__table__.columns
        
        # BaseModel fields
        assert 'id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
        assert 'is_active' in columns
        
        # Category specific fields
        assert 'name' in columns
        assert 'description' in columns
        assert 'slug' in columns
    
    def test_category_constraints(self):
        """Test Category field constraints"""
        columns = Category.__table__.columns
        
        # Check nullable constraints
        assert columns['name'].nullable is False
        assert columns['slug'].nullable is False
        assert columns['description'].nullable is True
        
        # Check unique constraints
        assert columns['name'].unique is True
        assert columns['slug'].unique is True
    
    def test_product_table_name(self):
        """Test Product table name"""
        assert Product.__tablename__ == "products"
    
    def test_product_fields(self):
        """Test Product has all required fields"""
        columns = Product.__table__.columns
        
        # BaseModel fields
        assert 'id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
        assert 'is_active' in columns
        
        # Product specific fields
        assert 'name' in columns
        assert 'description' in columns
        assert 'price' in columns
        assert 'category_id' in columns
        assert 'image_url' in columns
        assert 'stock_quantity' in columns
        assert 'is_available' in columns
    
    def test_product_constraints(self):
        """Test Product field constraints"""
        columns = Product.__table__.columns
        
        # Check nullable constraints
        assert columns['name'].nullable is False
        assert columns['price'].nullable is False
        assert columns['description'].nullable is True
        assert columns['category_id'].nullable is True
        assert columns['image_url'].nullable is True
        
        # Check default values
        assert columns['stock_quantity'].default.arg == 0
        assert columns['is_available'].default.arg is True
    
    def test_create_category(self, db_session):
        """Test creating a category"""
        category = Category(
            name="Test Category",
            description="Test Description",
            slug="test-category"
        )
        
        db_session.add(category)
        db_session.commit()
        
        # Verify category was created
        assert category.id is not None
        assert category.name == "Test Category"
        assert category.description == "Test Description"
        assert category.slug == "test-category"
        assert category.is_active is True
    
    def test_create_product(self, db_session):
        """Test creating a product"""
        product = Product(
            name="Test Product",
            description="Test Product Description",
            price=1000,  # Price in cents
            image_url="https://example.com/image.jpg",
            stock_quantity=10
        )
        
        db_session.add(product)
        db_session.commit()
        
        # Verify product was created
        assert product.id is not None
        assert product.name == "Test Product"
        assert product.description == "Test Product Description"
        assert product.price == 1000
        assert product.image_url == "https://example.com/image.jpg"
        assert product.stock_quantity == 10
        assert product.is_available is True
        assert product.is_active is True
    
    def test_product_category_relationship(self, db_session):
        """Test product-category relationship"""
        # Create category
        category = Category(
            name="Electronics",
            description="Electronic products",
            slug="electronics"
        )
        db_session.add(category)
        db_session.commit()
        
        # Create product with category
        product = Product(
            name="Smartphone",
            description="Latest smartphone",
            price=50000,  # $500.00
            category_id=category.id,
            stock_quantity=5
        )
        db_session.add(product)
        db_session.commit()
        
        # Verify relationship
        assert product.category_id == category.id
        assert product.name == "Smartphone"
        assert product.price == 50000
