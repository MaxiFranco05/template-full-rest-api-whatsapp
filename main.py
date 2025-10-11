"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.error_handling import register_exception_handlers
from app.api.v1.api import api_router
from app.db.database import engine, Base
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
