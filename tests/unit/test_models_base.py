"""
Tests unitarios para modelos base
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import BaseModel
from app.db.database import Base


class TestBaseModel:
    """Test BaseModel functionality"""
    
    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_base_model_has_required_fields(self):
        """Test that BaseModel has all required fields"""
        # Check that BaseModel is abstract
        assert BaseModel.__abstract__ is True
        
        # Check that BaseModel has the expected attributes
        assert hasattr(BaseModel, 'id')
        assert hasattr(BaseModel, 'created_at')
        assert hasattr(BaseModel, 'updated_at')
        assert hasattr(BaseModel, 'is_active')
    
    def test_base_model_column_types(self):
        """Test BaseModel column types"""
        # Test that BaseModel can be used as a base class
        from sqlalchemy import Column, Integer, DateTime, Boolean
        from sqlalchemy.sql import func
        
        class TestModel(BaseModel):
            __tablename__ = "test_model"
            extra_field = Column(Integer)
        
        # Check that TestModel has all BaseModel fields
        columns = TestModel.__table__.columns
        assert 'id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
        assert 'is_active' in columns
        assert 'extra_field' in columns
    
    def test_base_model_defaults(self):
        """Test BaseModel default values"""
        # Test that BaseModel provides proper defaults
        from sqlalchemy import Column, Integer
        
        class TestModel(BaseModel):
            __tablename__ = "test_model2"
            extra_field = Column(Integer)
        
        columns = TestModel.__table__.columns
        
        # Check default values
        assert columns['is_active'].default.arg is True
        assert columns['created_at'].server_default is not None
