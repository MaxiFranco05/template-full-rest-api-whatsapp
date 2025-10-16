"""
Active Flow Manager
Manages the currently active flow configuration
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ActiveFlowManager:
    """Manages the active flow configuration"""
    
    def __init__(self, flows_directory: str = "app/flows"):
        self.flows_directory = Path(flows_directory)
        self.config_file = self.flows_directory / "active_flow.json"
        self._active_flow: Optional[str] = None
        self._config: Optional[Dict[str, Any]] = None
    
    def get_active_flow(self) -> Optional[str]:
        """Get the currently active flow ID"""
        if self._active_flow is None:
            self._load_config()
        return self._active_flow
    
    def set_active_flow(self, flow_id: str) -> bool:
        """Set the active flow"""
        try:
            config = {
                "active_flow": flow_id,
                "updated_at": datetime.now().isoformat(),
                "updated_by": "system"
            }
            
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self._active_flow = flow_id
            self._config = config
            
            logger.info(f"Active flow set to: {flow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting active flow: {e}")
            return False
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
                self._active_flow = self._config.get("active_flow")
            else:
                # Default to main.json if no config exists
                self._active_flow = "main"
                self._config = {
                    "active_flow": "main",
                    "updated_at": datetime.now().isoformat(),
                    "updated_by": "default"
                }
                logger.info("No active flow config found, defaulting to 'main'")
                
        except Exception as e:
            logger.error(f"Error loading active flow config: {e}")
            self._active_flow = "main"
            self._config = {
                "active_flow": "main",
                "updated_at": datetime.now().isoformat(),
                "updated_by": "fallback"
            }
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information"""
        if self._config is None:
            self._load_config()
        return self._config or {}
    
    def reset_to_default(self) -> bool:
        """Reset to default flow (main)"""
        return self.set_active_flow("main")


# Global instance
active_flow_manager = ActiveFlowManager()
