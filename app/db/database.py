"""
Configuración de base de datos SQLAlchemy con soporte multi-DB
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os


def get_database_url():
    """Obtener URL de base de datos según configuración"""
    if settings.DATABASE_TYPE.lower() == "sqlite":
        return settings.SQLITE_DATABASE_URL
    elif settings.DATABASE_TYPE.lower() == "postgresql":
        return settings.DATABASE_URL
    elif settings.DATABASE_TYPE.lower() == "mysql":
        return settings.DATABASE_URL.replace("postgresql://", "mysql://")
    else:
        return settings.SQLITE_DATABASE_URL


# Crear motor de base de datos
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=settings.DEBUG,
    # Configuración específica para SQLite
    connect_args={"check_same_thread": False} if settings.DATABASE_TYPE.lower() == "sqlite" else {}
)

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db():
    """Dependencia para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
