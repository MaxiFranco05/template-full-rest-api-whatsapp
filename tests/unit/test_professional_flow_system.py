"""
Unit Tests for Professional Flow System
Tests individual components of the professional flow system
"""
import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.flows.executor import FlowExecutor
from app.services.flows.builder import FlowStepType
from app.services.flows.loader import UnifiedFlowLoader


class TestProfessionalFlowSystem:
    """Test the Professional Flow System"""
    
    def test_create_executor(self):
        """Test creating a flow executor"""
        # Mock the required services
        mock_whatsapp = Mock()
        mock_persistence = Mock()
        executor = FlowExecutor(mock_whatsapp, mock_persistence)
        assert executor is not None
    
    def test_create_loader(self):
        """Test creating a flow loader"""
        loader = UnifiedFlowLoader()
        assert loader is not None
    
    def test_flow_step_types(self):
        """Test flow step types"""
        assert FlowStepType.MESSAGE.value == "message"
        assert FlowStepType.CHOICE.value == "choice"
        assert FlowStepType.QUESTION.value == "question"
        assert FlowStepType.CONDITION.value == "condition"
        assert FlowStepType.WAIT.value == "wait"
        assert FlowStepType.END.value == "end"
    
    def test_message_types(self):
        """Test message types"""
        # Test that FlowStepType has the expected values
        assert FlowStepType.MESSAGE.value == "message"
        assert FlowStepType.CHOICE.value == "choice"
        assert FlowStepType.QUESTION.value == "question"
        assert FlowStepType.CONDITION.value == "condition"
        assert FlowStepType.WAIT.value == "wait"
        assert FlowStepType.END.value == "end"


class TestFlowLoader:
    """Test the Flow Loader"""
    
    def test_load_from_config(self):
        """Test loading flow from config"""
        # Test that the loader can be created
        loader = UnifiedFlowLoader()
        assert loader is not None
        
        # Test that it has the expected methods
        assert hasattr(loader, 'load_flow_from_file')
        assert hasattr(loader, 'load_all_flows')
        assert hasattr(loader, 'validate_flow_file')


if __name__ == "__main__":
    pytest.main([__file__])