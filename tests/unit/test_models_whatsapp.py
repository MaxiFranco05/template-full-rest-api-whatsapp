"""
Tests unitarios para modelos de WhatsApp
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.whatsapp import WhatsAppUser, WhatsAppConversation, WhatsAppMessage
from app.db.database import Base


class TestWhatsAppModels:
    """Test WhatsApp models functionality"""
    
    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_whatsapp_user_table_name(self):
        """Test WhatsAppUser table name"""
        assert WhatsAppUser.__tablename__ == "whatsapp_users"
    
    def test_whatsapp_user_fields(self):
        """Test WhatsAppUser has all required fields"""
        columns = WhatsAppUser.__table__.columns
        
        # BaseModel fields
        assert 'id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
        assert 'is_active' in columns
        
        # WhatsAppUser specific fields
        assert 'phone_number' in columns
        assert 'name' in columns
        assert 'profile_name' in columns
        assert 'is_business' in columns
        assert 'first_message_at' in columns
        assert 'last_message_at' in columns
        assert 'message_count' in columns
        assert 'is_blocked' in columns
        assert 'user_metadata' in columns
    
    def test_whatsapp_user_constraints(self):
        """Test WhatsAppUser field constraints"""
        columns = WhatsAppUser.__table__.columns
        
        # Check nullable constraints
        assert columns['phone_number'].nullable is False
        assert columns['name'].nullable is True
        assert columns['profile_name'].nullable is True
        
        # Check unique constraints
        assert columns['phone_number'].unique is True
        
        # Check default values
        assert columns['is_business'].default.arg is False
        assert columns['message_count'].default.arg == 0
        assert columns['is_blocked'].default.arg is False
    
    def test_whatsapp_conversation_table_name(self):
        """Test WhatsAppConversation table name"""
        assert WhatsAppConversation.__tablename__ == "whatsapp_conversations"
    
    def test_whatsapp_conversation_fields(self):
        """Test WhatsAppConversation has all required fields"""
        columns = WhatsAppConversation.__table__.columns
        
        # BaseModel fields
        assert 'id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
        assert 'is_active' in columns
        
        # WhatsAppConversation specific fields
        assert 'user_id' in columns
        assert 'conversation_id' in columns
        assert 'current_state' in columns
        assert 'message_count' in columns
        assert 'started_at' in columns
        assert 'last_activity_at' in columns
        assert 'ended_at' in columns
        assert 'context' in columns
    
    def test_whatsapp_message_table_name(self):
        """Test WhatsAppMessage table name"""
        assert WhatsAppMessage.__tablename__ == "whatsapp_messages"
    
    def test_whatsapp_message_fields(self):
        """Test WhatsAppMessage has all required fields"""
        columns = WhatsAppMessage.__table__.columns
        
        # BaseModel fields
        assert 'id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
        assert 'is_active' in columns
        
        # WhatsAppMessage specific fields
        assert 'conversation_id' in columns
        assert 'message_id' in columns
        assert 'direction' in columns
        assert 'message_type' in columns
        assert 'content' in columns
        assert 'media_url' in columns
        assert 'timestamp' in columns
        assert 'status' in columns
        assert 'message_metadata' in columns
    
    def test_create_whatsapp_user(self, db_session):
        """Test creating a WhatsApp user"""
        user = WhatsAppUser(
            phone_number="+1234567890",
            name="Test User",
            profile_name="TestProfile"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        assert user.id is not None
        assert user.phone_number == "+1234567890"
        assert user.name == "Test User"
        assert user.profile_name == "TestProfile"
        assert user.is_business is False
        assert user.message_count == 0
        assert user.is_blocked is False
    
    def test_whatsapp_relationships(self, db_session):
        """Test WhatsApp model relationships"""
        # Create WhatsApp user
        user = WhatsAppUser(
            phone_number="+1234567890",
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create conversation
        conversation = WhatsAppConversation(
            user_id=user.id,
            conversation_id="conv_123",
            current_state="initial"
        )
        db_session.add(conversation)
        db_session.commit()
        
        # Create message
        message = WhatsAppMessage(
            conversation_id=conversation.id,
            message_id="msg_123",
            direction="inbound",
            message_type="text",
            content="Hello",
            timestamp=conversation.created_at
        )
        db_session.add(message)
        db_session.commit()
        
        # Test relationships
        assert len(user.conversations) == 1
        assert user.conversations[0].id == conversation.id
        assert len(conversation.messages) == 1
        assert conversation.messages[0].id == message.id
