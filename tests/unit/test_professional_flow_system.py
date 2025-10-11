"""
Unit Tests for Professional Flow System
Tests individual components of the professional flow system
"""
import pytest
import json
import yaml
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.flows.executor import (
    create_professional_flow_builder, FlowStepType, MessageType, DataSourceType,
    DataSource, FunctionConfig, FlowStep, FlowDefinition, FunctionExecutor, DataSourceManager
)
from app.services.flows.loader import create_unified_flow_loader


class TestProfessionalFlowBuilder:
    """Test the Professional Flow Builder"""
    
    def test_create_builder(self):
        """Test creating a flow builder"""
        builder = create_professional_flow_builder("test", "Test Flow", "Test description")
        assert builder.flow_id == "test"
        assert builder.name == "Test Flow"
        assert builder.description == "Test description"
    
    def test_add_data_source(self):
        """Test adding data sources"""
        builder = create_professional_flow_builder("test", "Test Flow")
        builder.add_data_source(
            name="test_db",
            source_type=DataSourceType.DATABASE,
            config={"table": "test"},
            cache_ttl=300
        )
        
        assert "test_db" in builder.data_sources
        assert builder.data_sources["test_db"].type == DataSourceType.DATABASE
        assert builder.data_sources["test_db"].config == {"table": "test"}
        assert builder.data_sources["test_db"].cache_ttl == 300
    
    def test_add_function(self):
        """Test adding functions"""
        builder = create_professional_flow_builder("test", "Test Flow")
        builder.add_function(
            name="test_func",
            module="test.module",
            function="test_function",
            parameters={"param1": "value1"},
            timeout=10,
            retry_count=2,
            error_handler="error_handler",
            cache_result=True
        )
        
        assert "test_func" in builder.functions
        func = builder.functions["test_func"]
        assert func.module == "test.module"
        assert func.function == "test_function"
        assert func.parameters == {"param1": "value1"}
        assert func.timeout == 10
        assert func.retry_count == 2
        assert func.error_handler == "error_handler"
        assert func.cache_result == True
    
    def test_add_message_step(self):
        """Test adding message steps"""
        builder = create_professional_flow_builder("test", "Test Flow")
        builder.add_message_step(
            step_id="greeting",
            name="Greeting",
            message="Hello!",
            message_type=MessageType.TEXT,
            next_step="next_step",
            data_sources=["test_db"],
            functions=["test_func"]
        )
        
        assert "greeting" in builder.steps
        step = builder.steps["greeting"]
        assert step.type == FlowStepType.MESSAGE
        assert step.message == "Hello!"
        assert step.message_type == MessageType.TEXT
        assert step.next_step == "next_step"
    
    def test_add_function_step(self):
        """Test adding function steps"""
        builder = create_professional_flow_builder("test", "Test Flow")
        builder.add_function("test_func", "test.module", "test_function")
        builder.add_function_step(
            step_id="execute_func",
            name="Execute Function",
            functions=["test_func"],
            next_step="next_step",
            error_handler="error_handler"
        )
        
        assert "execute_func" in builder.steps
        step = builder.steps["execute_func"]
        assert step.type == FlowStepType.FUNCTION
        assert len(step.functions) == 1
        assert step.functions[0].name == "test_func"
        assert step.next_step == "next_step"
        assert step.error_handler == "error_handler"
    
    def test_add_question_step(self):
        """Test adding question steps"""
        builder = create_professional_flow_builder("test", "Test Flow")
        builder.add_question_step(
            step_id="ask_question",
            name="Ask Question",
            question="What is your name?",
            validation={"required": True, "min_length": 2},
            next_step="next_step",
            functions=["test_func"]
        )
        
        assert "ask_question" in builder.steps
        step = builder.steps["ask_question"]
        assert step.type == FlowStepType.QUESTION
        assert step.message == "What is your name?"
        assert step.validation == {"required": True, "min_length": 2}
        assert step.next_step == "next_step"
    
    def test_add_condition_step(self):
        """Test adding condition steps"""
        builder = create_professional_flow_builder("test", "Test Flow")
        builder.add_condition_step(
            step_id="check_condition",
            name="Check Condition",
            conditions=[
                {"condition": "value == 'test'", "next_step": "step1"},
                {"condition": "value == 'other'", "next_step": "step2"}
            ]
        )
        
        assert "check_condition" in builder.steps
        step = builder.steps["check_condition"]
        assert step.type == FlowStepType.CONDITION
        assert len(step.conditions) == 2
        assert step.conditions[0]["condition"] == "value == 'test'"
        assert step.conditions[0]["next_step"] == "step1"
    
    def test_build_flow(self):
        """Test building a complete flow"""
        builder = create_professional_flow_builder("test", "Test Flow")
        builder.start_with("greeting")
        builder.add_message_step("greeting", "Greeting", "Hello!")
        builder.add_end_step("end", "End", "Goodbye!")
        builder.set_variable("test_var", "test_value")
        builder.set_error_handler("test_error", "error_step")
        builder.set_metadata("version", "1.0")
        
        flow = builder.build()
        
        assert isinstance(flow, FlowDefinition)
        assert flow.id == "test"
        assert flow.name == "Test Flow"
        assert flow.start_step == "greeting"
        assert len(flow.steps) == 2
        assert flow.variables["test_var"] == "test_value"
        assert flow.error_handling["test_error"] == "error_step"
        assert flow.metadata["version"] == "1.0"
    
    def test_build_flow_without_start_step(self):
        """Test building flow without start step should raise error"""
        builder = create_professional_flow_builder("test", "Test Flow")
        builder.add_message_step("greeting", "Greeting", "Hello!")
        
        with pytest.raises(ValueError, match="Flow must have a start step"):
            builder.build()


class TestFunctionExecutor:
    """Test the Function Executor"""
    
    def test_create_executor(self):
        """Test creating function executor"""
        executor = FunctionExecutor()
        assert executor.function_cache == {}
        assert executor.loaded_modules == {}
    
    @patch('importlib.import_module')
    def test_execute_function_success(self, mock_import):
        """Test successful function execution"""
        # Mock module and function
        mock_module = Mock()
        mock_function = Mock(return_value="test_result")
        mock_module.test_function = mock_function
        mock_import.return_value = mock_module
        
        executor = FunctionExecutor()
        func_config = FunctionConfig(
            name="test_func",
            module="test.module",
            function="test_function",
            parameters={"param1": "value1"}
        )
        
        result = executor.execute_function(func_config, {"param1": "value1"})
        
        assert result["success"] == True
        assert result["result"] == "test_result"
        assert result["cached"] == False
        mock_function.assert_called_once_with(param1="value1")
    
    @patch('importlib.import_module')
    def test_execute_function_with_cache(self, mock_import):
        """Test function execution with caching"""
        mock_module = Mock()
        mock_function = Mock(return_value="test_result")
        mock_module.test_function = mock_function
        mock_import.return_value = mock_module
        
        executor = FunctionExecutor()
        func_config = FunctionConfig(
            name="test_func",
            module="test.module",
            function="test_function",
            parameters={"param1": "value1"},
            cache_result=True
        )
        
        # First execution
        result1 = executor.execute_function(func_config, {"param1": "value1"})
        assert result1["success"] == True
        assert result1["cached"] == False
        
        # Second execution (should be cached)
        result2 = executor.execute_function(func_config, {"param1": "value1"})
        assert result2["success"] == True
        assert result2["cached"] == True
        
        # Function should only be called once
        assert mock_function.call_count == 1
    
    @patch('importlib.import_module')
    def test_execute_function_error(self, mock_import):
        """Test function execution with error"""
        mock_module = Mock()
        mock_function = Mock(side_effect=Exception("Test error"))
        mock_module.test_function = mock_function
        mock_import.return_value = mock_module
        
        executor = FunctionExecutor()
        func_config = FunctionConfig(
            name="test_func",
            module="test.module",
            function="test_function",
            parameters={}
        )
        
        result = executor.execute_function(func_config, {})
        
        assert result["success"] == False
        assert result["error"] == "Test error"
        assert result["error_type"] == "Exception"
    
    def test_prepare_parameters(self):
        """Test parameter preparation with context substitution"""
        executor = FunctionExecutor()
        
        parameters = {
            "param1": "{{user_name}}",
            "param2": "static_value",
            "param3": {
                "nested": "{{user_email}}"
            },
            "param4": ["{{user_phone}}", "static_item"]
        }
        
        context = {
            "user_name": "John",
            "user_email": "john@example.com",
            "user_phone": "+1234567890"
        }
        
        prepared = executor._prepare_parameters(parameters, context)
        
        assert prepared["param1"] == "John"
        assert prepared["param2"] == "static_value"
        assert prepared["param3"]["nested"] == "john@example.com"
        assert prepared["param4"][0] == "+1234567890"
        assert prepared["param4"][1] == "static_item"


class TestDataSourceManager:
    """Test the Data Source Manager"""
    
    def test_create_manager(self):
        """Test creating data source manager"""
        manager = DataSourceManager()
        assert manager.data_cache == {}
        assert manager.cache_timestamps == {}
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    def test_get_data_from_file(self, mock_open, mock_exists):
        """Test getting data from file source"""
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = '{"test": "data"}'
        mock_open.return_value.__enter__.return_value = mock_file
        
        manager = DataSourceManager()
        source = DataSource(
            name="test_file",
            type=DataSourceType.FILE,
            config={"path": "test.json"}
        )
        
        result = manager.get_data(source)
        
        assert result["success"] == True
        assert result["data"] == {"test": "data"}
        assert result["cached"] == False
    
    def test_get_data_from_static(self):
        """Test getting data from static source"""
        manager = DataSourceManager()
        source = DataSource(
            name="test_static",
            type=DataSourceType.STATIC,
            config={"data": {"key": "value"}}
        )
        
        result = manager.get_data(source)
        
        assert result["success"] == True
        assert result["data"] == {"key": "value"}
        assert result["cached"] == False
    
    def test_get_data_with_cache(self):
        """Test getting data with caching"""
        manager = DataSourceManager()
        source = DataSource(
            name="test_cache",
            type=DataSourceType.STATIC,
            config={"data": {"key": "value"}},
            cache_ttl=300
        )
        
        # First call
        result1 = manager.get_data(source)
        assert result1["success"] == True
        assert result1["cached"] == False
        
        # Second call (should be cached)
        result2 = manager.get_data(source)
        assert result2["success"] == True
        assert result2["cached"] == True
    
    def test_get_data_error(self):
        """Test getting data with error"""
        manager = DataSourceManager()
        source = DataSource(
            name="test_error",
            type=DataSourceType.FILE,
            config={"path": "nonexistent.json"}
        )
        
        result = manager.get_data(source)
        
        assert result["success"] == False
        assert "error" in result


class TestProfessionalUnifiedFlowLoader:
    """Test the Professional Unified Flow Loader"""
    
    def test_create_loader(self):
        """Test creating flow loader"""
        loader = create_unified_flow_loader("test/flows")
        assert loader.flows_directory == Path("test/flows")
        assert loader.loaded_flows == {}
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    def test_load_flow_from_json(self, mock_open, mock_exists):
        """Test loading flow from JSON file"""
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = json.dumps({
            "id": "test",
            "name": "Test Flow",
            "start_step": "greeting",
            "steps": [
                {
                    "id": "greeting",
                    "type": "message",
                    "name": "Greeting",
                    "message": "Hello!"
                }
            ]
        })
        mock_open.return_value.__enter__.return_value = mock_file
        
        loader = create_unified_flow_loader("test/flows")
        flow = loader.load_flow_from_file("test")
        
        assert isinstance(flow, FlowDefinition)
        assert flow.id == "test"
        assert flow.name == "Test Flow"
        assert flow.start_step == "greeting"
        assert len(flow.steps) == 1
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    def test_load_flow_from_yaml(self, mock_open, mock_exists):
        """Test loading flow from YAML file"""
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = yaml.dump({
            "id": "test",
            "name": "Test Flow",
            "start_step": "greeting",
            "steps": [
                {
                    "id": "greeting",
                    "type": "message",
                    "name": "Greeting",
                    "message": "Hello!"
                }
            ]
        })
        mock_open.return_value.__enter__.return_value = mock_file
        
        loader = create_unified_flow_loader("test/flows")
        flow = loader.load_flow_from_file("test")
        
        assert isinstance(flow, FlowDefinition)
        assert flow.id == "test"
        assert flow.name == "Test Flow"
    
    def test_validate_flow_file(self):
        """Test flow validation"""
        # Create a mock flow
        flow = FlowDefinition(
            id="test",
            name="Test Flow",
            description="Test",
            start_step="greeting",
            steps={
                "greeting": FlowStep(
                    id="greeting",
                    type=FlowStepType.MESSAGE,
                    name="Greeting",
                    message="Hello!"
                )
            }
        )
        
        loader = create_unified_flow_loader("test/flows")
        
        # Mock the load_flow_from_file method
        with patch.object(loader, 'load_flow_from_file', return_value=flow):
            validation = loader.validate_flow_file("test")
            
            assert validation["valid"] == True
            assert validation["flow_id"] == "test"
            assert validation["steps_count"] == 1
            assert validation["issues"] == []
    
    def test_validate_flow_file_invalid(self):
        """Test flow validation with invalid flow"""
        # Create an invalid flow (no start step)
        flow = FlowDefinition(
            id="test",
            name="Test Flow",
            description="Test",
            start_step="nonexistent",
            steps={
                "greeting": FlowStep(
                    id="greeting",
                    type=FlowStepType.MESSAGE,
                    name="Greeting",
                    message="Hello!"
                )
            }
        )
        
        loader = create_unified_flow_loader("test/flows")
        
        # Mock the load_flow_from_file method
        with patch.object(loader, 'load_flow_from_file', return_value=flow):
            validation = loader.validate_flow_file("test")
            
            assert validation["valid"] == False
            assert "Start step 'nonexistent' not found in steps" in validation["issues"]


if __name__ == "__main__":
    pytest.main([__file__])
