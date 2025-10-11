"""
Tests unitarios para schemas comunes
"""
import pytest
from pydantic import ValidationError
from app.schemas.common import BaseSchema, PaginatedResponse


class TestBaseSchema:
    """Test BaseSchema functionality"""
    
    def test_base_schema_config(self):
        """Test BaseSchema configuration"""
        assert BaseSchema.model_config['from_attributes'] is True
    
    def test_base_schema_inheritance(self):
        """Test BaseSchema can be inherited"""
        class TestSchema(BaseSchema):
            name: str
            age: int
        
        schema = TestSchema(name="Test", age=25)
        assert schema.name == "Test"
        assert schema.age == 25


class TestPaginatedResponse:
    """Test PaginatedResponse functionality"""
    
    def test_paginated_response_valid(self):
        """Test valid paginated response"""
        response = PaginatedResponse(
            items=[{"id": 1, "name": "Item 1"}],
            total=1,
            page=1,
            size=10,
            pages=1
        )
        
        assert len(response.items) == 1
        assert response.total == 1
        assert response.page == 1
        assert response.size == 10
        assert response.pages == 1
    
    def test_paginated_response_empty(self):
        """Test empty paginated response"""
        response = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=0
        )
        
        assert len(response.items) == 0
        assert response.total == 0
        assert response.pages == 0
    
    def test_paginated_response_invalid(self):
        """Test invalid paginated response"""
        with pytest.raises(ValidationError):
            PaginatedResponse(
                items="not_a_list",  # Should be a list
                total=1,
                page=1,
                size=10,
                pages=1
            )
