"""
Tests unitarios para modelos de usuario
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.db.database import Base


class TestUserModel:
    """Test User model functionality"""
    
    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_user_table_name(self):
        """Test User table name"""
        assert User.__tablename__ == "users"
    
    def test_user_has_required_fields(self):
        """Test that User has all required fields"""
        columns = User.__table__.columns
        
        # BaseModel fields
        assert 'id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
        assert 'is_active' in columns
        
        # User specific fields
        assert 'email' in columns
        assert 'username' in columns
        assert 'full_name' in columns
        assert 'hashed_password' in columns
        assert 'is_superuser' in columns
        assert 'is_verified' in columns
    
    def test_user_field_constraints(self):
        """Test User field constraints"""
        columns = User.__table__.columns
        
        # Check nullable constraints
        assert columns['email'].nullable is False
        assert columns['username'].nullable is False
        assert columns['hashed_password'].nullable is False
        assert columns['full_name'].nullable is True
        
        # Check unique constraints
        assert columns['email'].unique is True
        assert columns['username'].unique is True
        
        # Check default values
        assert columns['is_superuser'].default.arg is False
        assert columns['is_verified'].default.arg is False
    
    def test_user_field_types(self):
        """Test User field types"""
        columns = User.__table__.columns
        
        # Check field types
        assert str(columns['email'].type) == 'VARCHAR(255)'
        assert str(columns['username'].type) == 'VARCHAR(100)'
        assert str(columns['full_name'].type) == 'VARCHAR(255)'
        assert str(columns['hashed_password'].type) == 'VARCHAR(255)'
        assert str(columns['is_superuser'].type) == 'BOOLEAN'
        assert str(columns['is_verified'].type) == 'BOOLEAN'
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed_password_here"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.is_verified is False
