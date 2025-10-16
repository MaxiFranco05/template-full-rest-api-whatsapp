"""
Tests unitarios para schemas de autenticación
"""
import pytest
from pydantic import ValidationError
from app.schemas.auth import Token, TokenData, UserLogin


class TestAuthSchemas:
    """Test Auth schemas functionality"""
    
    def test_token_valid(self):
        """Test valid Token"""
        token = Token(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer"
        )
        
        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.token_type == "bearer"
    
    def test_token_missing_fields(self):
        """Test Token with missing fields"""
        with pytest.raises(ValidationError):
            Token(access_token="token")  # Missing token_type
    
    def test_token_data_with_username(self):
        """Test TokenData with username"""
        token_data = TokenData(username="testuser")
        
        assert token_data.username == "testuser"
    
    def test_token_data_empty(self):
        """Test TokenData without username"""
        token_data = TokenData()
        
        assert token_data.username is None
    
    def test_user_login_valid(self):
        """Test valid UserLogin"""
        login = UserLogin(
            username="testuser",
            password="password123"
        )
        
        assert login.username == "testuser"
        assert login.password == "password123"
    
    def test_user_login_missing_fields(self):
        """Test UserLogin with missing fields"""
        with pytest.raises(ValidationError):
            UserLogin(username="testuser")  # Missing password
        
        with pytest.raises(ValidationError):
            UserLogin(password="password123")  # Missing username
    
    def test_user_login_empty_strings(self):
        """Test UserLogin with empty strings"""
        # Note: Pydantic v2 allows empty strings by default
        # This test verifies the behavior rather than expecting validation errors
        login = UserLogin(
            username="",  # Empty string is allowed
            password=""   # Empty string is allowed
        )
        
        assert login.username == ""
        assert login.password == ""
