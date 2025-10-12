"""
Aplicación principal FastAPI
"""
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.error_handling import register_exception_handlers
from app.api.v1.api import api_router
from app.db.database import engine, Base
from app.utils.performance import PerformanceMiddleware
from app.utils.rate_limiting import RateLimitMiddleware
import logging
from datetime import datetime

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Detectar características disponibles
from app.utils.feature_detection import feature_detection
status = feature_detection.get_status()
logger.info(f"Estado de características: {status}")

# Crear tablas de base de datos
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos creadas exitosamente")
except Exception as e:
    logger.error(f"Error creando tablas de base de datos: {e}")
    raise

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Template profesional para APIs de negocio con WhatsApp Business API",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Agregar middleware de performance
app.add_middleware(PerformanceMiddleware)

# Agregar middleware de rate limiting
app.add_middleware(RateLimitMiddleware, default_rule="api_global")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=settings.STATIC_FILES_PATH), name="static")

# Registrar manejadores de excepciones
register_exception_handlers(app)

# Incluir routers de API
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production"
    }


@app.get("/performance")
async def performance_stats():
    """Performance statistics endpoint"""
    from app.utils.performance import get_performance_stats
    from app.utils.rate_limiting import get_rate_limit_stats
    
    return {
        "performance": get_performance_stats(),
        "rate_limiting": get_rate_limit_stats(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """Página de inicio"""
    return f"""
    <html>
        <head>
            <title>{settings.APP_NAME}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #333; }}
                .links {{ margin-top: 30px; }}
                .links a {{ display: inline-block; margin: 10px; padding: 10px 20px; 
                           background: #007bff; color: white; text-decoration: none; 
                           border-radius: 5px; }}
                .links a:hover {{ background: #0056b3; }}
                .company-info {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 {settings.APP_NAME}</h1>
                <p>Template profesional para APIs de negocio con WhatsApp Business API</p>
                
                <div class="company-info">
                    <h3>📋 Información de la Empresa</h3>
                    <p><strong>Nombre:</strong> {settings.COMPANY_NAME}</p>
                    <p><strong>Teléfono:</strong> {settings.COMPANY_PHONE}</p>
                    <p><strong>Email:</strong> {settings.COMPANY_EMAIL}</p>
                    <p><strong>Sitio Web:</strong> {settings.COMPANY_WEBSITE}</p>
                </div>
                
                <div class="links">
                    <a href="/docs">📚 Documentación Swagger</a>
                    <a href="/redoc">📖 Documentación ReDoc</a>
                    <a href="/api/v1/openapi.json">🔧 OpenAPI Schema</a>
                    <a href="/health">❤️ Health Check</a>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Endpoint de salud de la aplicación"""
    from app.utils.feature_detection import feature_detection
    
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "features": feature_detection.get_status()
    }


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware para agregar tiempo de procesamiento y logging"""
    import time
    import uuid
    
    # Generar ID único para la request
    request_id = str(uuid.uuid4())
    
    # Log de request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            'request_id': request_id,
            'method': request.method,
            'path': request.url.path,
            'client_ip': request.client.host if request.client else None
        }
    )
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # Log de response
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'process_time': process_time
            }
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} - {str(e)} ({process_time:.3f}s)",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'process_time': process_time,
                'error': str(e)
            },
            exc_info=True
        )
        raise


def main():
    """Main CLI entry point"""
    import argparse
    import sys
    from pathlib import Path
    
    parser = argparse.ArgumentParser(
        description="Business API Template - WhatsApp Flow Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --flow main.json                    # Set active flow
  python main.py --flow main.yaml --validate-only    # Validate flow only
  python main.py --list-flows                        # List available flows
  python main.py --flow-info main.json              # Show flow details
  python main.py --test-flow main.json              # Test flow with mock data
  python main.py --createsuperuser                   # Create admin user
  python main.py --server                           # Start web server
        """
    )
    
    # Flow management commands
    flow_group = parser.add_argument_group('Flow Management')
    flow_group.add_argument('--flow', '-f', help='Flow file to use (JSON/YAML/Python)')
    flow_group.add_argument('--validate-only', action='store_true', 
                           help='Only validate flow syntax without setting as active')
    flow_group.add_argument('--list-flows', '-l', action='store_true', 
                           help='List all available flows')
    flow_group.add_argument('--flow-info', help='Show detailed information about a flow')
    flow_group.add_argument('--test-flow', help='Test flow with mock data')
    flow_group.add_argument('--active-flow-info', action='store_true',
                           help='Show information about the currently active flow')
    
    # User management commands
    user_group = parser.add_argument_group('User Management')
    user_group.add_argument('--createsuperuser', action='store_true',
                           help='Create a superuser account')
    user_group.add_argument('--list-users', action='store_true',
                           help='List all users')
    user_group.add_argument('--promote-user', action='store_true',
                           help='Promote user to staff')
    user_group.add_argument('--demote-user', action='store_true',
                           help='Demote user from staff')
    user_group.add_argument('--reset-password', action='store_true',
                           help='Reset user password')
    user_group.add_argument('--user-stats', action='store_true',
                           help='Show user statistics')
    
    # Server commands
    server_group = parser.add_argument_group('Server Management')
    server_group.add_argument('--server', '-s', action='store_true',
                             help='Start the web server')
    server_group.add_argument('--host', default=settings.HOST,
                             help='Host to bind to (default: %(default)s)')
    server_group.add_argument('--port', type=int, default=settings.PORT,
                             help='Port to bind to (default: %(default)s)')
    server_group.add_argument('--reload', action='store_true', default=settings.DEBUG,
                             help='Enable auto-reload (default: %(default)s)')
    
    args = parser.parse_args()
    
    try:
        # Handle flow management commands
        if args.list_flows:
            return list_flows()
        elif args.flow_info:
            return show_flow_info(args.flow_info)
        elif args.active_flow_info:
            return show_active_flow_info()
        elif args.test_flow:
            return test_flow(args.test_flow)
        elif args.flow:
            return manage_flow(args.flow, args.validate_only)
        
        # Handle user management commands
        elif args.createsuperuser:
            return create_superuser()
        elif args.list_users:
            return list_users()
        elif args.promote_user:
            return promote_user()
        elif args.demote_user:
            return demote_user()
        elif args.reset_password:
            return reset_user_password()
        elif args.user_stats:
            return show_user_stats()
        
        # Handle server commands
        elif args.server:
            return start_server(args.host, args.port, args.reload)
        
        else:
            # Default behavior: start server with main.json flow
            print("🚀 Starting server with default flow (main.json)...")
            return start_server(args.host, args.port, args.reload)
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def list_flows():
    """List all available flows"""
    from app.services.flows.loader import create_unified_flow_loader
    
    print("📋 Available WhatsApp Flows")
    print("=" * 50)
    
    try:
        loader = create_unified_flow_loader("app/flows")
        flows = loader.load_all_flows()
        
        if not flows:
            print("❌ No flows found in app/flows/")
            return 1
        
        for flow_id, flow in flows.items():
            print(f"🔹 {flow_id}")
            print(f"   Name: {flow.name}")
            print(f"   Description: {flow.description}")
            print(f"   Steps: {len(flow.steps)}")
            print(f"   Start Step: {flow.start_step}")
            print()
        
        print(f"✅ Found {len(flows)} flow(s)")
        return 0
        
    except Exception as e:
        print(f"❌ Error loading flows: {e}")
        return 1


def show_flow_info(flow_id: str):
    """Show detailed information about a flow"""
    from app.services.flows.loader import create_unified_flow_loader
    
    print(f"📊 Flow Information: {flow_id}")
    print("=" * 50)
    
    try:
        loader = create_unified_flow_loader("app/flows")
        flow = loader.load_flow_from_file(flow_id)
        
        print(f"🆔 ID: {flow.id}")
        print(f"📝 Name: {flow.name}")
        print(f"📄 Description: {flow.description}")
        print(f"🚀 Start Step: {flow.start_step}")
        print(f"📊 Total Steps: {len(flow.steps)}")
        print()
        
        print("📋 Steps:")
        for i, step in enumerate(flow.steps, 1):
            print(f"  {i}. {step.id} ({step.type.value})")
            print(f"     Name: {step.name}")
            if step.message:
                print(f"     Message: {step.message[:50]}...")
            if step.next_step:
                print(f"     Next: {step.next_step}")
            print()
        
        print("🔧 Variables:")
        for key, value in flow.variables.items():
            print(f"  {key}: {value}")
        print()
        
        print("⚠️ Error Handling:")
        for error_type, handler in flow.error_handling.items():
            print(f"  {error_type}: {handler}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error loading flow {flow_id}: {e}")
        return 1


def show_active_flow_info():
    """Show information about the currently active flow"""
    from app.services.flows.active_flow_manager import active_flow_manager
    from app.services.flows.service import WhatsAppFlowService
    from app.services.whatsapp.service import whatsapp_service
    from app.services.whatsapp.persistence import get_whatsapp_persistence_service
    
    print("🎯 Active Flow Information")
    print("=" * 50)
    
    try:
        # Get active flow from manager
        active_flow_id = active_flow_manager.get_active_flow()
        config_info = active_flow_manager.get_config_info()
        
        print(f"🆔 Active Flow ID: {active_flow_id}")
        print(f"📅 Last Updated: {config_info.get('updated_at', 'Unknown')}")
        print(f"👤 Updated By: {config_info.get('updated_by', 'Unknown')}")
        print()
        
        # Get detailed flow information
        mock_persistence = get_whatsapp_persistence_service(None)
        flow_service = WhatsAppFlowService(whatsapp_service, mock_persistence)
        
        flow_info = flow_service.get_active_flow_info()
        
        if "error" in flow_info:
            print(f"❌ Error loading flow details: {flow_info['error']}")
            return 1
        
        print("📊 Flow Details:")
        print(f"  📝 Name: {flow_info['name']}")
        print(f"  📄 Description: {flow_info['description']}")
        print(f"  🚀 Start Step: {flow_info['start_step']}")
        print(f"  📊 Steps Count: {flow_info['steps_count']}")
        print()
        
        print("🔧 Variables:")
        for key, value in flow_info['variables'].items():
            print(f"  {key}: {value}")
        print()
        
        print("⚠️ Error Handlers:")
        for error_type, handler in flow_info['error_handlers'].items():
            print(f"  {error_type}: {handler}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error getting active flow info: {e}")
        return 1




def test_flow(flow_id: str):
    """Test a flow with mock data"""
    from app.services.flows.loader import create_unified_flow_loader
    from app.services.flows.builder import create_flow_executor
    from app.services.whatsapp.service import whatsapp_service
    from app.services.whatsapp.persistence import get_whatsapp_persistence_service
    
    print(f"🧪 Testing Flow: {flow_id}")
    print("=" * 50)
    
    try:
        # Load flow
        loader = create_unified_flow_loader("app/flows")
        flow = loader.load_flow_from_file(flow_id)
        
        # Create mock services
        mock_persistence = get_whatsapp_persistence_service(None)
        executor = create_flow_executor(whatsapp_service, mock_persistence)
        executor.register_flow(flow)
        
        # Test with mock phone number
        test_phone = "+1234567890"
        print(f"📱 Test Phone: {test_phone}")
        print()
        
        # Start conversation
        print("🚀 Starting conversation...")
        result = executor.start_conversation(test_phone, flow_id)
        
        if result.get("success"):
            print("✅ Flow started successfully!")
            print(f"📊 Result: {result}")
        else:
            print(f"❌ Flow failed: {result.get('error')}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error testing flow {flow_id}: {e}")
        return 1


def manage_flow(flow_file: str, validate_only: bool = False):
    """Manage flow (set active or validate)"""
    from app.services.flows.loader import create_unified_flow_loader
    from pathlib import Path
    
    print(f"🔧 Managing Flow: {flow_file}")
    print("=" * 50)
    
    try:
        # Check if flow file exists
        flows_dir = Path("app/flows")
        flow_paths = [
            flows_dir / f"{flow_file}.json",
            flows_dir / f"{flow_file}.yaml", 
            flows_dir / f"{flow_file}.yml",
            flows_dir / f"{flow_file}.py"
        ]
        
        existing_path = None
        for path in flow_paths:
            if path.exists():
                existing_path = path
                break
        
        if not existing_path:
            print(f"❌ Flow file not found: {flow_file}")
            print("Available formats: .json, .yaml, .yml, .py")
            return 1
        
        print(f"📁 Found flow file: {existing_path}")
        
        # Load and validate flow
        loader = create_unified_flow_loader("app/flows")
        flow = loader.load_flow_from_file(flow_file)
        
        print(f"✅ Flow loaded successfully!")
        print(f"🆔 ID: {flow.id}")
        print(f"📝 Name: {flow.name}")
        print(f"📊 Steps: {len(flow.steps)}")
        
        if validate_only:
            print("✅ Flow validation completed!")
            return 0
        
        # Set as active flow (save to config)
        set_active_flow(flow_file)
        print(f"🎯 Flow '{flow_file}' set as active!")
        print("💡 Restart the server to apply changes")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error managing flow {flow_file}: {e}")
        return 1


def set_active_flow(flow_id: str):
    """Set active flow in configuration"""
    from app.services.flows.active_flow_manager import active_flow_manager
    
    success = active_flow_manager.set_active_flow(flow_id)
    if not success:
        raise Exception(f"Failed to set active flow to {flow_id}")


def list_users():
    """List all users"""
    from app.services.user_service import user_service
    
    print("👥 User List")
    print("=" * 50)
    
    try:
        users = user_service.list_users(active_only=False)
        
        if not users:
            print("📭 No users found")
            return 0
        
        print(f"📊 Total users: {len(users)}")
        print()
        
        for user in users:
            status_icon = "✅" if user.is_active else "❌"
            superuser_icon = "👑" if user.is_superuser else "👤"
            staff_icon = "👥" if user.is_staff else "👤"
            
            print(f"{status_icon} {superuser_icon}{staff_icon} {user.username}")
            print(f"   📧 Email: {user.email}")
            print(f"   👤 Name: {user.display_name}")
            print(f"   📅 Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   🔐 Superuser: {user.is_superuser}")
            print(f"   👥 Staff: {user.is_staff}")
            print(f"   ✅ Active: {user.is_active}")
            print(f"   📊 Logins: {user.login_count}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return 1


def promote_user():
    """Promote user to staff"""
    from app.services.user_service import user_service
    
    print("👥 Promote User to Staff")
    print("=" * 50)
    
    try:
        username = input("Username to promote: ").strip()
        if not username:
            print("❌ Username is required")
            return 1
        
        user = user_service.get_user_by_username(username)
        if not user:
            print(f"❌ User '{username}' not found")
            return 1
        
        if user.is_staff:
            print(f"ℹ️ User '{username}' is already staff")
            return 0
        
        success = user_service.promote_to_staff(user.id, promoted_by="cli")
        if success:
            print(f"✅ User '{username}' promoted to staff successfully")
        else:
            print(f"❌ Failed to promote user '{username}'")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error promoting user: {e}")
        return 1


def demote_user():
    """Demote user from staff"""
    from app.services.user_service import user_service
    
    print("👥 Demote User from Staff")
    print("=" * 50)
    
    try:
        username = input("Username to demote: ").strip()
        if not username:
            print("❌ Username is required")
            return 1
        
        user = user_service.get_user_by_username(username)
        if not user:
            print(f"❌ User '{username}' not found")
            return 1
        
        if not user.is_staff:
            print(f"ℹ️ User '{username}' is not staff")
            return 0
        
        if user.is_superuser:
            print(f"❌ Cannot demote superuser '{username}'")
            return 1
        
        success = user_service.demote_from_staff(user.id, demoted_by="cli")
        if success:
            print(f"✅ User '{username}' demoted from staff successfully")
        else:
            print(f"❌ Failed to demote user '{username}'")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error demoting user: {e}")
        return 1


def reset_user_password():
    """Reset user password"""
    from app.services.user_service import user_service
    import getpass
    
    print("🔑 Reset User Password")
    print("=" * 50)
    
    try:
        username = input("Username: ").strip()
        if not username:
            print("❌ Username is required")
            return 1
        
        user = user_service.get_user_by_username(username)
        if not user:
            print(f"❌ User '{username}' not found")
            return 1
        
        new_password = getpass.getpass("New Password: ")
        if not new_password:
            print("❌ Password is required")
            return 1
        
        password_confirm = getpass.getpass("Confirm Password: ")
        if new_password != password_confirm:
            print("❌ Passwords do not match")
            return 1
        
        success = user_service.reset_password(user.id, new_password, reset_by="cli")
        if success:
            print(f"✅ Password reset successfully for user '{username}'")
        else:
            print(f"❌ Failed to reset password for user '{username}'")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return 1


def show_user_stats():
    """Show user statistics"""
    from app.services.user_service import user_service
    
    print("📊 User Statistics")
    print("=" * 50)
    
    try:
        stats = user_service.get_user_stats()
        
        print(f"👥 Total Users: {stats['total_users']}")
        print(f"✅ Active Users: {stats['active_users']}")
        print(f"❌ Inactive Users: {stats['inactive_users']}")
        print(f"👑 Superusers: {stats['superusers']}")
        print(f"👥 Staff Users: {stats['staff_users']}")
        print(f"📧 Verified Users: {stats['verified_users']}")
        print(f"❓ Unverified Users: {stats['unverified_users']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error getting user stats: {e}")
        return 1


def create_superuser():
    """Create a superuser account (Django-style)"""
    import getpass
    from app.services.user_service import user_service
    
    print("👤 Create Superuser Account (Django-style)")
    print("=" * 50)
    
    try:
        # Get user input
        username = input("Username: ").strip()
        if not username:
            print("❌ Username is required")
            return 1
        
        email = input("Email: ").strip()
        if not email:
            print("❌ Email is required")
            return 1
        
        full_name = input("Full Name (optional): ").strip()
        
        password = getpass.getpass("Password: ")
        if not password:
            print("❌ Password is required")
            return 1
        
        password_confirm = getpass.getpass("Confirm Password: ")
        if password != password_confirm:
            print("❌ Passwords do not match")
            return 1
        
        # Create superuser using the service
        user = user_service.create_superuser(
            email=email,
            username=username,
            password=password,
            full_name=full_name or None
        )
        
        print(f"✅ Superuser created successfully!")
        print(f"🆔 User ID: {user.id}")
        print(f"👤 Username: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Is Superuser: {user.is_superuser}")
        print(f"👥 Is Staff: {user.is_staff}")
        print(f"✅ Is Active: {user.is_active}")
        print(f"📅 Created: {user.created_at}")
        
        return 0
        
    except ValueError as e:
        print(f"❌ Validation error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return 1


def start_server(host: str, port: int, reload: bool):
    """Start the web server"""
    import uvicorn
    from app.services.flows.active_flow_manager import active_flow_manager
    
    print(f"🚀 Starting Business API Template Server")
    print("=" * 50)
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    
    # Set main.json as active flow by default
    try:
        active_flow = active_flow_manager.get_active_flow()
        if active_flow != "main":
            print(f"🎯 Setting active flow to 'main' (was: {active_flow})")
            active_flow_manager.set_active_flow("main")
        else:
            print(f"🎯 Active flow: main")
    except Exception as e:
        print(f"⚠️ Warning: Could not set active flow: {e}")
    
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload
        )
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
