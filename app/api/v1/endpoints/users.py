"""
Endpoints de API para gestión de usuarios
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.user_service import user_service
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, UserPasswordReset, UserStats
from app.core.security import create_access_token, get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    try:
        # Solo permitir usuarios regulares en registro público
        user_data.is_superuser = False
        user_data.is_staff = False
        user_data.is_verified = False
        
        user = user_service.create_user(user_data)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en registro de usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/login")
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login de usuario"""
    try:
        user = user_service.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear token de acceso
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Actualizar información del usuario actual"""
    try:
        # No permitir cambios de permisos por el propio usuario
        user_data.is_superuser = None
        user_data.is_staff = None
        
        updated_user = user_service.update_user(
            current_user.id, 
            user_data, 
            updated_by=current_user.username
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return UserResponse.from_orm(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error al actualizar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/me/password", response_model=dict)
async def change_password(
    password_data: UserPasswordReset,
    current_user: User = Depends(get_current_user)
):
    """Cambiar contraseña del usuario actual"""
    try:
        success = user_service.reset_password(
            current_user.id,
            password_data.new_password,
            reset_by=current_user.username
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {"message": "Contraseña actualizada exitosamente"}
    except Exception as e:
        logger.error(f"Error al cambiar contraseña: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# Endpoints de administración (requieren permisos de staff)
@router.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Listar usuarios (solo staff)"""
    if not current_user.has_permission('admin.access'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta función"
        )
    
    users = user_service.list_users(skip=skip, limit=limit, active_only=active_only)
    return [UserResponse.from_orm(user) for user in users]


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Obtener usuario por ID (solo staff)"""
    if not current_user.has_permission('admin.access'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta función"
        )
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return UserResponse.from_orm(user)


@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Actualizar usuario (solo staff)"""
    if not current_user.has_permission('user.manage'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para gestionar usuarios"
        )
    
    try:
        updated_user = user_service.update_user(
            user_id,
            user_data,
            updated_by=current_user.username
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return UserResponse.from_orm(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error al actualizar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Eliminar usuario (solo superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los superusuarios pueden eliminar usuarios"
        )
    
    success = user_service.delete_user(user_id, deleted_by=current_user.username)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario eliminado exitosamente"}


@router.post("/admin/users/{user_id}/promote")
async def promote_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Promover usuario a staff (solo superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los superusuarios pueden promover usuarios"
        )
    
    success = user_service.promote_to_staff(user_id, promoted_by=current_user.username)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario promovido a staff exitosamente"}


@router.post("/admin/users/{user_id}/demote")
async def demote_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Degradar usuario de staff (solo superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los superusuarios pueden degradar usuarios"
        )
    
    success = user_service.demote_from_staff(user_id, demoted_by=current_user.username)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario degradado de staff exitosamente"}


@router.get("/admin/stats", response_model=UserStats)
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """Obtener estadísticas de usuarios (solo staff)"""
    if not current_user.has_permission('admin.access'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta función"
        )
    
    stats = user_service.get_user_stats()
    return UserStats(**stats)
