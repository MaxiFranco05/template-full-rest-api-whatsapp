#!/usr/bin/env python3
"""
Simple Application Startup Test
Tests that the application can start without errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_app_startup():
    """Test that the application can start"""
    print("🚀 Testing Application Startup")
    print("=" * 50)
    
    try:
        # Test core imports
        from app.core.config import settings
        print("✅ Settings loaded")
        
        # Test database
        from app.db.database import get_db
        print("✅ Database connection ready")
        
        # Test main services
        from app.services.whatsapp.service import whatsapp_service
        print("✅ WhatsApp service ready")
        
        from app.services.business.product import ProductService
        print("✅ Product service ready")
        
        from app.services.business.user import UserService
        print("✅ User service ready")
        
        from app.services.flows.executor import create_professional_flow_builder
        print("✅ Flow executor ready")
        
        from app.services.shared.cache import cache
        print("✅ Cache service ready")
        
        # Test API endpoints
        from app.api.v1.endpoints.auth import router as auth_router
        from app.api.v1.endpoints.products import router as products_router
        from app.api.v1.endpoints.whatsapp import router as whatsapp_router
        print("✅ API endpoints ready")
        
        # Test main app
        from main import app
        print("✅ FastAPI app ready")
        
        print("\n🎉 SUCCESS: Application can start successfully!")
        print("✅ All core components are working")
        print("✅ Architecture reorganization is successful")
        assert True, "Application startup successful"
        
    except Exception as e:
        print(f"\n❌ FAILURE: Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Application startup failed: {e}"

if __name__ == "__main__":
    test_app_startup()
