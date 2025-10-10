"""
Professional Unified Flow Loader
Supports Python, JSON, and YAML with function execution and data sources
"""
import json
import yaml
import importlib
from typing import Dict, Any, List, Union
from pathlib import Path
from app.services.professional_flow_system import (
    create_professional_flow_builder, FlowStepType, MessageType, DataSourceType,
    DataSource, FunctionConfig, FlowStep, FlowDefinition
)


class ProfessionalUnifiedFlowLoader:
    """Professional loader supporting Python, JSON, and YAML with advanced features"""
    
    def __init__(self, flows_directory: str = "app/flows"):
        self.flows_directory = Path(flows_directory)
        self.loaded_flows: Dict[str, Any] = {}
        self.function_executor = None
        self.data_source_manager = None
    
    def load_flow_from_file(self, flow_file: str):
        """Load a flow from Python, JSON, or YAML file"""
        # Try different extensions
        extensions = ['.py', '.json', '.yaml', '.yml']
        
        for ext in extensions:
            file_path = self.flows_directory / f"{flow_file}{ext}"
            if file_path.exists():
                if ext == '.py':
                    return self._load_from_python(file_path)
                elif ext in ['.json']:
                    return self._load_from_json(file_path)
                elif ext in ['.yaml', '.yml']:
                    return self._load_from_yaml(file_path)
        
        raise FileNotFoundError(f"Flow file {flow_file} not found in {self.flows_directory}")
    
    def load_all_flows(self):
        """Load all flows from the flows directory"""
        if not self.flows_directory.exists():
            return {}
        
        flows = {}
        
        # Load Python files
        for flow_file in self.flows_directory.glob("*.py"):
            if not flow_file.name.startswith('__'):
                flow_name = flow_file.stem
                try:
                    flows[flow_name] = self._load_from_python(flow_file)
                    print(f"✅ Python flow loaded: {flow_name}")
                except Exception as e:
                    print(f"❌ Error loading Python flow {flow_name}: {e}")
        
        # Load JSON files
        for flow_file in self.flows_directory.glob("*.json"):
            flow_name = flow_file.stem
            try:
                flows[flow_name] = self._load_from_json(flow_file)
                print(f"✅ JSON flow loaded: {flow_name}")
            except Exception as e:
                print(f"❌ Error loading JSON flow {flow_name}: {e}")
        
        # Load YAML files
        for flow_file in self.flows_directory.glob("*.yaml"):
            flow_name = flow_file.stem
            try:
                flows[flow_name] = self._load_from_yaml(flow_file)
                print(f"✅ YAML flow loaded: {flow_name}")
            except Exception as e:
                print(f"❌ Error loading YAML flow {flow_name}: {e}")
        
        for flow_file in self.flows_directory.glob("*.yml"):
            flow_name = flow_file.stem
            try:
                flows[flow_name] = self._load_from_yaml(flow_file)
                print(f"✅ YAML flow loaded: {flow_name}")
            except Exception as e:
                print(f"❌ Error loading YAML flow {flow_name}: {e}")
        
        return flows
    
    def _load_from_python(self, file_path: Path):
        """Load flow from Python file"""
        # Import the module
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for a function that returns a FlowDefinition
        if hasattr(module, 'create_flow'):
            return module.create_flow()
        elif hasattr(module, 'flow'):
            return module.flow
        else:
            raise ValueError(f"Python file {file_path} must contain 'create_flow()' function or 'flow' variable")
    
    def _load_from_json(self, file_path: Path):
        """Load flow from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            flow_config = json.load(file)
        return self._build_flow_from_config(flow_config)
    
    def _load_from_yaml(self, file_path: Path):
        """Load flow from YAML file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            flow_config = yaml.safe_load(file)
        return self._build_flow_from_config(flow_config)
    
    def _build_flow_from_config(self, config: Dict[str, Any]):
        """Build a flow from configuration (works for both JSON and YAML)"""
        flow_id = config["id"]
        name = config["name"]
        description = config.get("description", "")
        
        builder = create_professional_flow_builder(flow_id, name, description)
        
        # Set start step
        if "start_step" in config:
            builder.start_with(config["start_step"])
        
        # Add data sources
        for ds_name, ds_config in config.get("data_sources", {}).items():
            ds_type = DataSourceType(ds_config["type"])
            builder.add_data_source(
                name=ds_name,
                source_type=ds_type,
                config=ds_config.get("config", {}),
                cache_ttl=ds_config.get("cache_ttl")
            )
        
        # Add functions
        for func_name, func_config in config.get("functions", {}).items():
            builder.add_function(
                name=func_name,
                module=func_config["module"],
                function=func_config["function"],
                parameters=func_config.get("parameters", {}),
                timeout=func_config.get("timeout", 30),
                retry_count=func_config.get("retry_count", 3),
                error_handler=func_config.get("error_handler"),
                cache_result=func_config.get("cache_result", False)
            )
        
        # Add steps
        for step_config in config.get("steps", []):
            self._add_step_to_builder(builder, step_config)
        
        # Set variables
        for key, value in config.get("variables", {}).items():
            builder.set_variable(key, value)
        
        # Set error handlers
        for error_type, handler_step in config.get("error_handling", {}).items():
            builder.set_error_handler(error_type, handler_step)
        
        # Set metadata
        for key, value in config.get("metadata", {}).items():
            builder.set_metadata(key, value)
        
        return builder.build()
    
    def _add_step_to_builder(self, builder, step_config: Dict[str, Any]):
        """Add a step to the builder based on configuration"""
        step_id = step_config["id"]
        step_type = step_config["type"]
        name = step_config["name"]
        
        if step_type == "message":
            message = step_config["message"]
            message_type = MessageType(step_config.get("message_type", "text"))
            next_step = step_config.get("next_step")
            data_sources = step_config.get("data_sources", [])
            functions = step_config.get("functions", [])
            
            builder.add_message_step(
                step_id, name, message, message_type, next_step, data_sources, functions
            )
        
        elif step_type == "function":
            functions = step_config["functions"]
            next_step = step_config.get("next_step")
            error_handler = step_config.get("error_handler")
            
            builder.add_function_step(step_id, name, functions, next_step, error_handler)
        
        elif step_type == "question":
            question = step_config["question"]
            validation = step_config.get("validation")
            next_step = step_config.get("next_step")
            functions = step_config.get("functions", [])
            
            builder.add_question_step(step_id, name, question, validation, next_step, functions)
        
        elif step_type == "choice":
            message = step_config["message"]
            options = step_config["options"]
            next_step = step_config.get("next_step")
            data_sources = step_config.get("data_sources", [])
            
            builder.add_choice_step(step_id, name, message, options, next_step, data_sources)
        
        elif step_type == "condition":
            conditions = step_config["conditions"]
            builder.add_condition_step(step_id, name, conditions)
        
        elif step_type == "action":
            actions = step_config["actions"]
            next_step = step_config.get("next_step")
            builder.add_action_step(step_id, name, actions, next_step)
        
        elif step_type == "wait":
            timeout = step_config.get("timeout", 300)
            builder.add_wait_step(step_id, name, timeout)
        
        elif step_type == "end":
            message = step_config.get("message", "Conversación finalizada")
            builder.add_end_step(step_id, name, message)
    
    def convert_format(self, source_file: str, target_format: str, output_file: str = None):
        """Convert between Python, JSON, and YAML formats"""
        # Load source flow
        source_flow = self.load_flow_from_file(source_file)
        
        if output_file is None:
            output_file = source_file
        
        if target_format.lower() == 'json':
            output_path = self.flows_directory / f"{output_file}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self._flow_to_dict(source_flow), f, indent=2, ensure_ascii=False)
            print(f"✅ Converted to JSON: {output_path}")
        
        elif target_format.lower() == 'yaml':
            output_path = self.flows_directory / f"{output_file}.yaml"
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._flow_to_dict(source_flow), f, default_flow_style=False, allow_unicode=True)
            print(f"✅ Converted to YAML: {output_path}")
        
        elif target_format.lower() == 'python':
            output_path = self.flows_directory / f"{output_file}.py"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._flow_to_python(source_flow))
            print(f"✅ Converted to Python: {output_path}")
        
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
    
    def _flow_to_dict(self, flow: FlowDefinition) -> Dict[str, Any]:
        """Convert flow to dictionary for JSON/YAML export"""
        return {
            "id": flow.id,
            "name": flow.name,
            "description": flow.description,
            "start_step": flow.start_step,
            "variables": flow.variables,
            "data_sources": {
                name: {
                    "type": ds.type.value,
                    "config": ds.config,
                    "cache_ttl": ds.cache_ttl
                }
                for name, ds in flow.data_sources.items()
            },
            "functions": {
                name: {
                    "module": func.module,
                    "function": func.function,
                    "parameters": func.parameters,
                    "timeout": func.timeout,
                    "retry_count": func.retry_count,
                    "error_handler": func.error_handler,
                    "cache_result": func.cache_result
                }
                for name, func in flow.functions.items()
            },
            "error_handling": flow.error_handling,
            "steps": [
                {
                    "id": step.id,
                    "type": step.type.value,
                    "name": step.name,
                    "message": step.message,
                    "message_type": step.message_type.value if step.message_type else None,
                    "options": step.options,
                    "validation": step.validation,
                    "next_step": step.next_step,
                    "conditions": step.conditions,
                    "actions": step.actions,
                    "functions": [f.name for f in step.functions],
                    "data_sources": [ds.name for ds in step.data_sources],
                    "timeout": step.timeout,
                    "retry_count": step.retry_count,
                    "error_handler": step.error_handler,
                    "metadata": step.metadata
                }
                for step in flow.steps.values()
            ],
            "metadata": flow.metadata
        }
    
    def _flow_to_python(self, flow: FlowDefinition) -> str:
        """Convert flow to Python code"""
        python_code = f'''"""
{flow.name}
{flow.description}
"""
from app.services.professional_flow_system import (
    create_professional_flow_builder, MessageType, DataSourceType
)


def create_flow():
    """Create the {flow.id} flow"""
    return (create_professional_flow_builder("{flow.id}", "{flow.name}", "{flow.description}")
'''
        
        # Add start step
        python_code += f'        .start_with("{flow.start_step}")\n'
        
        # Add data sources
        for name, ds in flow.data_sources.items():
            python_code += f'        .add_data_source(\n'
            python_code += f'            name="{name}",\n'
            python_code += f'            source_type=DataSourceType.{ds.type.name},\n'
            python_code += f'            config={ds.config},\n'
            if ds.cache_ttl:
                python_code += f'            cache_ttl={ds.cache_ttl}\n'
            python_code += f'        )\n'
        
        # Add functions
        for name, func in flow.functions.items():
            python_code += f'        .add_function(\n'
            python_code += f'            name="{name}",\n'
            python_code += f'            module="{func.module}",\n'
            python_code += f'            function="{func.function}",\n'
            python_code += f'            parameters={func.parameters},\n'
            python_code += f'            timeout={func.timeout},\n'
            python_code += f'            retry_count={func.retry_count},\n'
            if func.error_handler:
                python_code += f'            error_handler="{func.error_handler}",\n'
            python_code += f'            cache_result={func.cache_result}\n'
            python_code += f'        )\n'
        
        # Add steps
        for step in flow.steps.values():
            if step.type == FlowStepType.MESSAGE:
                python_code += f'        .add_message_step(\n'
                python_code += f'            step_id="{step.id}",\n'
                python_code += f'            name="{step.name}",\n'
                python_code += f'            message="{step.message}",\n'
                if step.message_type != MessageType.TEXT:
                    python_code += f'            message_type=MessageType.{step.message_type.name},\n'
                if step.next_step:
                    python_code += f'            next_step="{step.next_step}",\n'
                if step.data_sources:
                    python_code += f'            data_sources={[ds.name for ds in step.data_sources]},\n'
                if step.functions:
                    python_code += f'            functions={[f.name for f in step.functions]}\n'
                python_code += f'        )\n'
            
            elif step.type == FlowStepType.FUNCTION:
                python_code += f'        .add_function_step(\n'
                python_code += f'            step_id="{step.id}",\n'
                python_code += f'            name="{step.name}",\n'
                python_code += f'            functions={[f.name for f in step.functions]},\n'
                if step.next_step:
                    python_code += f'            next_step="{step.next_step}",\n'
                if step.error_handler:
                    python_code += f'            error_handler="{step.error_handler}"\n'
                python_code += f'        )\n'
            
            # Add other step types as needed...
        
        # Add variables
        for key, value in flow.variables.items():
            python_code += f'        .set_variable("{key}", {repr(value)})\n'
        
        # Add error handlers
        for error_type, handler_step in flow.error_handling.items():
            python_code += f'        .set_error_handler("{error_type}", "{handler_step}")\n'
        
        # Add metadata
        for key, value in flow.metadata.items():
            python_code += f'        .set_metadata("{key}", {repr(value)})\n'
        
        python_code += '        .build()\n    )\n\n\n# Export the flow\nflow = create_flow()\n'
        
        return python_code
    
    def validate_flow_file(self, flow_file: str) -> Dict[str, Any]:
        """Validate a flow file and return validation results"""
        try:
            flow = self.load_flow_from_file(flow_file)
            
            validation_result = {
                "valid": True,
                "flow_id": flow.id,
                "flow_name": flow.name,
                "steps_count": len(flow.steps),
                "data_sources_count": len(flow.data_sources),
                "functions_count": len(flow.functions),
                "start_step": flow.start_step,
                "variables": list(flow.variables.keys()),
                "error_handlers": list(flow.error_handling.keys()),
                "issues": []
            }
            
            # Check for common issues
            if not flow.start_step:
                validation_result["issues"].append("No start step defined")
            
            if flow.start_step not in flow.steps:
                validation_result["issues"].append(f"Start step '{flow.start_step}' not found in steps")
            
            # Check for orphaned steps
            referenced_steps = set()
            for step in flow.steps.values():
                if step.next_step:
                    referenced_steps.add(step.next_step)
                for condition in step.conditions:
                    if condition.get("next_step"):
                        referenced_steps.add(condition["next_step"])
            
            for step_id in flow.steps.keys():
                if step_id != flow.start_step and step_id not in referenced_steps:
                    validation_result["issues"].append(f"Step '{step_id}' is not referenced")
            
            # Check data sources
            for step in flow.steps.values():
                for ds in step.data_sources:
                    if ds.name not in flow.data_sources:
                        validation_result["issues"].append(f"Step '{step.id}' references undefined data source '{ds.name}'")
            
            # Check functions
            for step in flow.steps.values():
                for func in step.functions:
                    if func.name not in flow.functions:
                        validation_result["issues"].append(f"Step '{step.id}' references undefined function '{func.name}'")
            
            if validation_result["issues"]:
                validation_result["valid"] = False
            
            return validation_result
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "issues": [str(e)]
            }


# Factory function
def create_professional_unified_flow_loader(flows_directory: str = "app/flows") -> ProfessionalUnifiedFlowLoader:
    """Create a professional unified flow loader"""
    return ProfessionalUnifiedFlowLoader(flows_directory)
