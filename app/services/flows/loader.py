"""
Unified Flow Loader
Support for both JSON and YAML flow configurations
"""
import json
import yaml
import logging
from typing import Dict, Any, List, Union
from pathlib import Path
from app.services.flows.builder import (
    create_flow_builder, FlowStepType, MessageType
)

logger = logging.getLogger(__name__)


class UnifiedFlowLoader:
    """Load conversation flows from JSON or YAML configuration files"""
    
    def __init__(self, flows_directory: str = "app/flows"):
        self.flows_directory = Path(flows_directory)
        self.loaded_flows: Dict[str, Any] = {}
    
    def load_flow_from_file(self, flow_file: str):
        """Load a flow from JSON or YAML file"""
        # Try JSON first
        json_path = self.flows_directory / f"{flow_file}.json"
        yaml_path = self.flows_directory / f"{flow_file}.yaml"
        
        if json_path.exists():
            return self._load_from_json(json_path)
        elif yaml_path.exists():
            return self._load_from_yaml(yaml_path)
        else:
            raise FileNotFoundError(f"Flow file {flow_file} not found in {self.flows_directory}")
    
    def load_all_flows(self):
        """Load all flows from the flows directory"""
        if not self.flows_directory.exists():
            return {}
        
        flows = {}
        
        # Load JSON files (exclude config files)
        for flow_file in self.flows_directory.glob("*.json"):
            flow_name = flow_file.stem
            # Skip configuration files
            if flow_name in ['active_flow']:
                continue
            try:
                flows[flow_name] = self._load_from_json(flow_file)
                logger.info(f"SUCCESS: JSON flow loaded: {flow_name}")
            except Exception as e:
                logger.error(f"ERROR: Error loading JSON flow {flow_name}: {e}")
        
        # Load YAML files (exclude config files)
        for flow_file in self.flows_directory.glob("*.yaml"):
            flow_name = flow_file.stem
            # Skip configuration files
            if flow_name in ['active_flow']:
                continue
            try:
                flows[flow_name] = self._load_from_yaml(flow_file)
                logger.info(f"SUCCESS: YAML flow loaded: {flow_name}")
            except Exception as e:
                logger.error(f"ERROR: Error loading YAML flow {flow_name}: {e}")
        
        return flows
    
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
        
        builder = create_flow_builder(flow_id, name, description)
        
        # Set start step
        if "start_step" in config:
            builder.start_with(config["start_step"])
        
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
            
            # Extract additional parameters for non-text messages
            metadata = {}
            if message_type.value != "text":
                if message_type.value == "image":
                    metadata["image_url"] = step_config.get("image_url", "")
                    metadata["caption"] = step_config.get("caption", message)
                elif message_type.value == "document":
                    metadata["document_url"] = step_config.get("document_url", "")
                    metadata["filename"] = step_config.get("filename", "document.pdf")
                    metadata["caption"] = step_config.get("caption", message)
                elif message_type.value == "audio":
                    metadata["audio_url"] = step_config.get("audio_url", "")
                elif message_type.value == "video":
                    metadata["video_url"] = step_config.get("video_url", "")
                    metadata["caption"] = step_config.get("caption", message)
                elif message_type.value == "location":
                    metadata["latitude"] = step_config.get("latitude", 0)
                    metadata["longitude"] = step_config.get("longitude", 0)
                    metadata["name"] = step_config.get("location_name", "")
                    metadata["address"] = step_config.get("address", "")
                elif message_type.value == "contacts":
                    metadata["contacts"] = step_config.get("contacts", [])
                elif message_type.value == "catalog":
                    # Catalog message - extract catalog parameters
                    metadata["catalog_id"] = step_config.get("catalog_id", "")
                    metadata["header_text"] = step_config.get("header_text", "🛍️ Nuestro Catálogo de Productos")
                    metadata["body_text"] = step_config.get("body_text", "Elegí una opción para ver más detalles 👇")
                    metadata["footer_text"] = step_config.get("footer_text", "Productos disponibles")
                    metadata["sections"] = step_config.get("sections", [])
            
            # Add error_fallback_step if present
            error_fallback_step = step_config.get("error_fallback_step")
            builder.add_message_step(step_id, name, message, message_type, next_step, metadata, error_fallback_step)
        
        elif step_type == "question":
            question = step_config["question"]
            validation = step_config.get("validation")
            next_step = step_config.get("next_step")
            
            builder.add_question_step(step_id, name, question, validation, next_step)
        
        elif step_type == "choice":
            message = step_config["message"]
            options = step_config["options"]
            choice_type = step_config.get("choice_type", "buttons")
            next_step = step_config.get("next_step")
            conditions = step_config.get("conditions", [])
            
            if choice_type == "buttons":
                builder.add_choice_step(step_id, name, message, options, next_step, conditions)
            elif choice_type == "list":
                button_text = step_config.get("button_text", "Ver opciones")
                builder.add_list_step(step_id, name, message, options, button_text, next_step, conditions)
        
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
    
    def convert_yaml_to_json(self, yaml_file: str, output_file: str = None):
        """Convert a YAML flow file to JSON"""
        yaml_path = self.flows_directory / f"{yaml_file}.yaml"
        
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file {yaml_path} not found")
        
        with open(yaml_path, 'r', encoding='utf-8') as file:
            yaml_config = yaml.safe_load(file)
        
        if output_file is None:
            output_file = yaml_file
        
        json_path = self.flows_directory / f"{output_file}.json"
        
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(yaml_config, file, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Converted {yaml_file}.yaml to {output_file}.json")
        return json_path
    
    def convert_json_to_yaml(self, json_file: str, output_file: str = None):
        """Convert a JSON flow file to YAML"""
        json_path = self.flows_directory / f"{json_file}.json"
        
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file {json_path} not found")
        
        with open(json_path, 'r', encoding='utf-8') as file:
            json_config = json.load(file)
        
        if output_file is None:
            output_file = json_file
        
        yaml_path = self.flows_directory / f"{output_file}.yaml"
        
        with open(yaml_path, 'w', encoding='utf-8') as file:
            yaml.dump(json_config, file, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"✅ Converted {json_file}.json to {output_file}.yaml")
        return yaml_path
    
    def validate_flow_file(self, flow_file: str) -> Dict[str, Any]:
        """Validate a flow file and return validation results"""
        try:
            flow = self.load_flow_from_file(flow_file)
            
            validation_result = {
                "valid": True,
                "flow_id": flow.id,
                "flow_name": flow.name,
                "steps_count": len(flow.steps),
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
            
            if validation_result["issues"]:
                validation_result["valid"] = False
            
            return validation_result
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "issues": [str(e)]
            }
    
    def get_flow_info(self, flow_file: str) -> Dict[str, Any]:
        """Get information about a flow file"""
        try:
            flow = self.load_flow_from_file(flow_file)
            
            return {
                "file": flow_file,
                "id": flow.id,
                "name": flow.name,
                "description": flow.description,
                "start_step": flow.start_step,
                "steps_count": len(flow.steps),
                "variables": flow.variables,
                "error_handlers": flow.error_handling,
                "metadata": flow.metadata,
                "steps": [
                    {
                        "id": step.id,
                        "type": step.type.value,
                        "name": step.name,
                        "next_step": step.next_step
                    }
                    for step in flow.steps.values()
                ]
            }
        except Exception as e:
            return {
                "file": flow_file,
                "error": str(e)
            }


# Factory function
def create_unified_flow_loader(flows_directory: str = "app/flows") -> UnifiedFlowLoader:
    """Create a unified flow loader"""
    return UnifiedFlowLoader(flows_directory)


# Example usage removed for production
