"""
Servicio para manejo de usuarios
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.utils import generate_slug
from app.utils.performance import performance_timer
from app.utils.cache import cached, cache_invalidate
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    @performance_timer("user_service.get_user")
    @cached(ttl=300, tags=["users"])  # Cache for 5 minutes
    def get_user(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    @performance_timer("user_service.get_user_by_email")
    @cached(ttl=300, tags=["users"])
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    @performance_timer("user_service.get_user_by_username")
    @cached(ttl=300, tags=["users"])
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        return self.db.query(User).filter(User.username == username).first()
    
    @performance_timer("user_service.create_user")
    @cache_invalidate(tags=["users"])
    def create_user(self, user: UserCreate) -> User:
        """Crear nuevo usuario"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    @performance_timer("user_service.update_user")
    @cache_invalidate(tags=["users"])
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Actualizar usuario"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    @performance_timer("user_service.authenticate_user")
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @performance_timer("user_service.delete_user")
    @cache_invalidate(tags=["users"])
    def delete_user(self, user_id: int) -> bool:
        """Eliminar usuario (soft delete)"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        db_user.is_active = False
        self.db.commit()
        return True
