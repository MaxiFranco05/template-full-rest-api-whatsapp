"""
Servicio de gestión de usuarios Django-style
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate, UserUpdate, UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """Servicio para gestión de usuarios con funcionalidades Django-style"""
    
    def __init__(self):
        self.db = next(get_db())
    
    def create_user(self, user_data: UserCreate, created_by: Optional[str] = None) -> User:
        """Crear un nuevo usuario"""
        try:
            # Verificar si el usuario ya existe
            if self.get_user_by_email(user_data.email):
                raise ValueError(f"Usuario con email {user_data.email} ya existe")
            
            if self.get_user_by_username(user_data.username):
                raise ValueError(f"Usuario con username {user_data.username} ya existe")
            
            # Crear usuario
            hashed_password = get_password_hash(user_data.password)
            
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                is_superuser=user_data.is_superuser,
                is_staff=user_data.is_staff,
                is_active=user_data.is_active,
                is_verified=user_data.is_verified,
                phone_number=user_data.phone_number,
                bio=user_data.bio,
                timezone=user_data.timezone or "UTC",
                language=user_data.language or "es",
                created_by=created_by
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"Usuario creado: {db_user.username} ({db_user.email})")
            return db_user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error de integridad al crear usuario: {e}")
            raise ValueError("Error al crear usuario: datos duplicados")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear usuario: {e}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autenticar usuario con email y contraseña"""
        user = self.get_user_by_email(email)
        if not user:
            logger.warning(f"Intento de login con email inexistente: {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Intento de login con usuario inactivo: {email}")
            return None
        
        if not verify_password(password, user.hashed_password):
            # Incrementar contador de intentos fallidos
            user.failed_login_attempts += 1
            self.db.commit()
            logger.warning(f"Contraseña incorrecta para usuario: {email}")
            return None
        
        # Login exitoso - actualizar estadísticas
        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        user.login_count += 1
        user.failed_login_attempts = 0  # Reset failed attempts
        self.db.commit()
        
        logger.info(f"Login exitoso para usuario: {email}")
        return user
    
    def update_user(self, user_id: int, user_data: UserUpdate, updated_by: Optional[str] = None) -> Optional[User]:
        """Actualizar usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        try:
            # Actualizar campos proporcionados
            update_data = user_data.dict(exclude_unset=True)
            
            # Si se actualiza la contraseña, hashearla
            if 'password' in update_data:
                update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
            
            # Actualizar campos
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_by = updated_by
            user.last_activity = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Usuario actualizado: {user.username}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al actualizar usuario {user_id}: {e}")
            raise
    
    def delete_user(self, user_id: int, deleted_by: Optional[str] = None) -> bool:
        """Eliminar usuario (soft delete)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        try:
            # Soft delete - marcar como inactivo
            user.is_active = False
            user.updated_by = deleted_by
            user.last_activity = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Usuario eliminado (soft delete): {user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al eliminar usuario {user_id}: {e}")
            raise
    
    def list_users(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[User]:
        """Listar usuarios con paginación"""
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de usuarios"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        superusers = self.db.query(User).filter(User.is_superuser == True).count()
        staff_users = self.db.query(User).filter(User.is_staff == True).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "superusers": superusers,
            "staff_users": staff_users,
            "verified_users": verified_users,
            "unverified_users": total_users - verified_users
        }
    
    def promote_to_staff(self, user_id: int, promoted_by: Optional[str] = None) -> bool:
        """Promover usuario a staff"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_staff = True
        user.updated_by = promoted_by
        user.last_activity = datetime.utcnow()
        
        self.db.commit()
        logger.info(f"Usuario promovido a staff: {user.username}")
        return True
    
    def demote_from_staff(self, user_id: int, demoted_by: Optional[str] = None) -> bool:
        """Degradar usuario de staff"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # No permitir degradar superusers
        if user.is_superuser:
            logger.warning(f"Intento de degradar superuser: {user.username}")
            return False
        
        user.is_staff = False
        user.updated_by = demoted_by
        user.last_activity = datetime.utcnow()
        
        self.db.commit()
        logger.info(f"Usuario degradado de staff: {user.username}")
        return True
    
    def create_superuser(self, email: str, username: str, password: str, full_name: Optional[str] = None) -> User:
        """Crear superusuario (equivalente a Django's createsuperuser)"""
        user_data = UserCreate(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            is_superuser=True,
            is_staff=True,
            is_active=True,
            is_verified=True
        )
        
        return self.create_user(user_data, created_by="system")
    
    def reset_password(self, user_id: int, new_password: str, reset_by: Optional[str] = None) -> bool:
        """Resetear contraseña de usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.hashed_password = get_password_hash(new_password)
        user.updated_by = reset_by
        user.last_activity = datetime.utcnow()
        user.failed_login_attempts = 0  # Reset failed attempts
        
        self.db.commit()
        logger.info(f"Contraseña reseteada para usuario: {user.username}")
        return True


# Instancia global del servicio
user_service = UserService()
