"""
Professional Conversation Flow System
Complete system supporting Python, JSON, YAML with function execution and error handling
"""
import json
import yaml
import importlib
import inspect
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class FlowStepType(Enum):
    """Types of flow steps"""
    MESSAGE = "message"
    QUESTION = "question"
    CHOICE = "choice"
    INPUT = "input"
    CONDITION = "condition"
    ACTION = "action"
    FUNCTION = "function"
    WAIT = "wait"
    END = "end"


class MessageType(Enum):
    """Types of WhatsApp messages"""
    TEXT = "text"
    BUTTONS = "buttons"
    LIST = "list"
    MEDIA = "media"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    TEMPLATE = "template"


class DataSourceType(Enum):
    """Types of data sources"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    MEMORY = "memory"
    CACHE = "cache"
    STATIC = "static"


@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    type: DataSourceType
    config: Dict[str, Any]
    cache_ttl: Optional[int] = None
    retry_count: int = 3
    timeout: int = 30


@dataclass
class FunctionConfig:
    """Function execution configuration"""
    name: str
    module: str
    function: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    error_handler: Optional[str] = None
    cache_result: bool = False
    cache_ttl: int = 300


@dataclass
class FlowStep:
    """Represents a step in the conversation flow"""
    id: str
    type: FlowStepType
    name: str
    message: Optional[str] = None
    message_type: MessageType = MessageType.TEXT
    options: List[Dict[str, str]] = field(default_factory=list)
    validation: Optional[Dict[str, Any]] = None
    next_step: Optional[str] = None
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    functions: List[FunctionConfig] = field(default_factory=list)
    data_sources: List[DataSource] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_count: int = 3
    error_handler: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowDefinition:
    """Represents a complete conversation flow"""
    id: str
    name: str
    description: str
    start_step: str
    steps: Dict[str, FlowStep] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    data_sources: Dict[str, DataSource] = field(default_factory=dict)
    functions: Dict[str, FunctionConfig] = field(default_factory=dict)
    error_handling: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FunctionExecutor:
    """Executes functions with error handling and caching"""
    
    def __init__(self):
        self.function_cache: Dict[str, Any] = {}
        self.loaded_modules: Dict[str, Any] = {}
    
    def execute_function(self, func_config: FunctionConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function with error handling"""
        try:
            # Check cache first
            cache_key = f"{func_config.name}_{hash(str(func_config.parameters))}"
            if func_config.cache_result and cache_key in self.function_cache:
                logger.info(f"Function {func_config.name} result retrieved from cache")
                return {
                    "success": True,
                    "result": self.function_cache[cache_key],
                    "cached": True
                }
            
            # Load module if not already loaded
            if func_config.module not in self.loaded_modules:
                self.loaded_modules[func_config.module] = importlib.import_module(func_config.module)
            
            module = self.loaded_modules[func_config.module]
            function = getattr(module, func_config.function)
            
            # Prepare parameters
            params = self._prepare_parameters(func_config.parameters, context)
            
            # Execute function
            logger.info(f"Executing function {func_config.name} with params: {params}")
            result = function(**params)
            
            # Cache result if enabled
            if func_config.cache_result:
                self.function_cache[cache_key] = result
            
            return {
                "success": True,
                "result": result,
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"Error executing function {func_config.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _prepare_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare function parameters with context substitution"""
        prepared_params = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Context variable substitution
                var_name = value[2:-2].strip()
                prepared_params[key] = context.get(var_name, value)
            elif isinstance(value, dict):
                # Recursive substitution for nested objects
                prepared_params[key] = self._prepare_parameters(value, context)
            elif isinstance(value, list):
                # Handle lists with context substitution
                prepared_params[key] = []
                for item in value:
                    if isinstance(item, str) and item.startswith("{{") and item.endswith("}}"):
                        # Context variable substitution for list items
                        var_name = item[2:-2].strip()
                        prepared_params[key].append(context.get(var_name, item))
                    elif isinstance(item, dict):
                        prepared_params[key].append(self._prepare_parameters(item, context))
                    else:
                        prepared_params[key].append(item)
            else:
                prepared_params[key] = value
        
        return prepared_params


class DataSourceManager:
    """Manages data sources with caching and error handling"""
    
    def __init__(self):
        self.data_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
    
    def get_data(self, source: DataSource, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data from a source with caching"""
        try:
            # Check cache first
            if source.cache_ttl and source.name in self.data_cache:
                cache_time = self.cache_timestamps.get(source.name)
                if cache_time and (datetime.now() - cache_time).seconds < source.cache_ttl:
                    logger.info(f"Data retrieved from cache: {source.name}")
                    return {
                        "success": True,
                        "data": self.data_cache[source.name],
                        "cached": True
                    }
            
            # Get data from source
            data = self._fetch_from_source(source, context or {})
            
            # Cache data if TTL is set
            if source.cache_ttl:
                self.data_cache[source.name] = data
                self.cache_timestamps[source.name] = datetime.now()
            
            return {
                "success": True,
                "data": data,
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"Error getting data from source {source.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _fetch_from_source(self, source: DataSource, context: Dict[str, Any]) -> Any:
        """Fetch data from the actual source"""
        if source.type == DataSourceType.DATABASE:
            return self._fetch_from_database(source, context)
        elif source.type == DataSourceType.API:
            return self._fetch_from_api(source, context)
        elif source.type == DataSourceType.FILE:
            return self._fetch_from_file(source, context)
        elif source.type == DataSourceType.MEMORY:
            return self._fetch_from_memory(source, context)
        elif source.type == DataSourceType.STATIC:
            return source.config.get("data", {})
        else:
            raise ValueError(f"Unsupported data source type: {source.type}")
    
    def _fetch_from_database(self, source: DataSource, context: Dict[str, Any]) -> Any:
        """Fetch data from database"""
        # This would integrate with your existing database services
        # For now, return mock data
        return {"message": "Database data not implemented yet"}
    
    def _fetch_from_api(self, source: DataSource, context: Dict[str, Any]) -> Any:
        """Fetch data from API"""
        # This would make HTTP requests
        # For now, return mock data
        return {"message": "API data not implemented yet"}
    
    def _fetch_from_file(self, source: DataSource, context: Dict[str, Any]) -> Any:
        """Fetch data from file"""
        file_path = Path(source.config.get("path", ""))
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _fetch_from_memory(self, source: DataSource, context: Dict[str, Any]) -> Any:
        """Fetch data from memory"""
        return source.config.get("data", {})


class ProfessionalFlowBuilder:
    """Professional builder for creating conversation flows"""
    
    def __init__(self, flow_id: str, name: str, description: str = ""):
        self.flow_id = flow_id
        self.name = name
        self.description = description
        self.steps: Dict[str, FlowStep] = {}
        self.start_step: Optional[str] = None
        self.variables: Dict[str, Any] = {}
        self.data_sources: Dict[str, DataSource] = {}
        self.functions: Dict[str, FunctionConfig] = {}
        self.error_handling: Dict[str, str] = {}
        self.metadata: Dict[str, Any] = {}
    
    def start_with(self, step_id: str) -> 'ProfessionalFlowBuilder':
        """Set the starting step"""
        self.start_step = step_id
        return self
    
    def add_data_source(self, name: str, source_type: DataSourceType, 
                       config: Dict[str, Any], cache_ttl: int = None) -> 'ProfessionalFlowBuilder':
        """Add a data source"""
        self.data_sources[name] = DataSource(
            name=name,
            type=source_type,
            config=config,
            cache_ttl=cache_ttl
        )
        return self
    
    def add_function(self, name: str, module: str, function: str,
                    parameters: Dict[str, Any] = None, timeout: int = 30,
                    retry_count: int = 3, error_handler: str = None,
                    cache_result: bool = False) -> 'ProfessionalFlowBuilder':
        """Add a function configuration"""
        self.functions[name] = FunctionConfig(
            name=name,
            module=module,
            function=function,
            parameters=parameters or {},
            timeout=timeout,
            retry_count=retry_count,
            error_handler=error_handler,
            cache_result=cache_result
        )
        return self
    
    def add_step(self, step: FlowStep) -> 'ProfessionalFlowBuilder':
        """Add a step to the flow"""
        self.steps[step.id] = step
        return self
    
    def add_message_step(self, step_id: str, name: str, message: str,
                        message_type: MessageType = MessageType.TEXT,
                        next_step: Optional[str] = None,
                        data_sources: List[str] = None,
                        functions: List[str] = None) -> 'ProfessionalFlowBuilder':
        """Add a message step with data sources and functions"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.MESSAGE,
            name=name,
            message=message,
            message_type=message_type,
            next_step=next_step,
            data_sources=[self.data_sources[ds] for ds in (data_sources or [])],
            functions=[self.functions[f] for f in (functions or [])]
        )
        return self.add_step(step)
    
    def add_function_step(self, step_id: str, name: str, functions: List[str],
                         next_step: Optional[str] = None,
                         error_handler: str = None) -> 'ProfessionalFlowBuilder':
        """Add a function execution step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.FUNCTION,
            name=name,
            functions=[self.functions[f] for f in functions],
            next_step=next_step,
            error_handler=error_handler
        )
        return self.add_step(step)
    
    def add_question_step(self, step_id: str, name: str, question: str,
                         validation: Optional[Dict[str, Any]] = None,
                         next_step: Optional[str] = None,
                         functions: List[str] = None) -> 'ProfessionalFlowBuilder':
        """Add a question step with validation and functions"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.QUESTION,
            name=name,
            message=question,
            validation=validation,
            next_step=next_step,
            functions=[self.functions[f] for f in (functions or [])]
        )
        return self.add_step(step)
    
    def add_choice_step(self, step_id: str, name: str, message: str,
                       options: List[Dict[str, str]],
                       next_step: Optional[str] = None,
                       data_sources: List[str] = None) -> 'ProfessionalFlowBuilder':
        """Add a choice step with dynamic options"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.CHOICE,
            name=name,
            message=message,
            message_type=MessageType.BUTTONS,
            options=options,
            next_step=next_step,
            data_sources=[self.data_sources[ds] for ds in (data_sources or [])]
        )
        return self.add_step(step)
    
    def add_condition_step(self, step_id: str, name: str,
                          conditions: List[Dict[str, Any]]) -> 'ProfessionalFlowBuilder':
        """Add a condition step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.CONDITION,
            name=name,
            conditions=conditions
        )
        return self.add_step(step)
    
    def add_action_step(self, step_id: str, name: str, actions: List[str],
                       next_step: Optional[str] = None) -> 'ProfessionalFlowBuilder':
        """Add an action step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.ACTION,
            name=name,
            actions=actions,
            next_step=next_step
        )
        return self.add_step(step)
    
    def add_wait_step(self, step_id: str, name: str, timeout: int = 300) -> 'ProfessionalFlowBuilder':
        """Add a wait step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.WAIT,
            name=name,
            timeout=timeout
        )
        return self.add_step(step)
    
    def add_end_step(self, step_id: str, name: str, message: str = "Conversación finalizada") -> 'ProfessionalFlowBuilder':
        """Add an end step"""
        step = FlowStep(
            id=step_id,
            type=FlowStepType.END,
            name=name,
            message=message
        )
        return self.add_step(step)
    
    def set_variable(self, key: str, value: Any) -> 'ProfessionalFlowBuilder':
        """Set a flow variable"""
        self.variables[key] = value
        return self
    
    def set_error_handler(self, error_type: str, handler_step: str) -> 'ProfessionalFlowBuilder':
        """Set error handler"""
        self.error_handling[error_type] = handler_step
        return self
    
    def set_metadata(self, key: str, value: Any) -> 'ProfessionalFlowBuilder':
        """Set flow metadata"""
        self.metadata[key] = value
        return self
    
    def build(self) -> FlowDefinition:
        """Build the flow definition"""
        if not self.start_step:
            raise ValueError("Flow must have a start step")
        
        return FlowDefinition(
            id=self.flow_id,
            name=self.name,
            description=self.description,
            start_step=self.start_step,
            steps=self.steps,
            variables=self.variables,
            data_sources=self.data_sources,
            functions=self.functions,
            error_handling=self.error_handling,
            metadata=self.metadata
        )


# Factory functions
def create_professional_flow_builder(flow_id: str, name: str, description: str = "") -> ProfessionalFlowBuilder:
    """Create a new professional flow builder"""
    return ProfessionalFlowBuilder(flow_id, name, description)


def create_function_executor() -> FunctionExecutor:
    """Create a new function executor"""
    return FunctionExecutor()


def create_data_source_manager() -> DataSourceManager:
    """Create a new data source manager"""
    return DataSourceManager()
