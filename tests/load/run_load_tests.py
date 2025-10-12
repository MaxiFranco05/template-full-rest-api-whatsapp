#!/usr/bin/env python3
"""
Load Testing Configuration and Runner
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class LoadTestScenario:
    """Load test scenario configuration"""
    name: str
    description: str
    users: int
    spawn_rate: int
    duration: str
    host: str
    user_class: str
    tags: List[str]

class LoadTestManager:
    """Manager for load testing scenarios"""
    
    def __init__(self):
        self.scenarios = self._load_scenarios()
        self.results_dir = Path("tests/load/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_scenarios(self) -> Dict[str, LoadTestScenario]:
        """Load predefined test scenarios"""
        return {
            "smoke": LoadTestScenario(
                name="smoke",
                description="Smoke test - basic functionality",
                users=5,
                spawn_rate=1,
                duration="2m",
                host="http://localhost:8000",
                user_class="APIUser",
                tags=["smoke", "basic"]
            ),
            "normal": LoadTestScenario(
                name="normal",
                description="Normal load test - typical usage",
                users=50,
                spawn_rate=5,
                duration="5m",
                host="http://localhost:8000",
                user_class="APIUser",
                tags=["normal", "typical"]
            ),
            "peak": LoadTestScenario(
                name="peak",
                description="Peak load test - high traffic",
                users=200,
                spawn_rate=10,
                duration="10m",
                host="http://localhost:8000",
                user_class="HeavyUser",
                tags=["peak", "high-traffic"]
            ),
            "stress": LoadTestScenario(
                name="stress",
                description="Stress test - maximum load",
                users=500,
                spawn_rate=20,
                duration="15m",
                host="http://localhost:8000",
                user_class="StressUser",
                tags=["stress", "maximum"]
            ),
            "whatsapp": LoadTestScenario(
                name="whatsapp",
                description="WhatsApp specific load test",
                users=100,
                spawn_rate=5,
                duration="10m",
                host="http://localhost:8000",
                user_class="WhatsAppLoadUser",
                tags=["whatsapp", "messaging"]
            ),
            "endurance": LoadTestScenario(
                name="endurance",
                description="Endurance test - long duration",
                users=100,
                spawn_rate=5,
                duration="1h",
                host="http://localhost:8000",
                user_class="APIUser",
                tags=["endurance", "long-duration"]
            )
        }
    
    def list_scenarios(self):
        """List available test scenarios"""
        print("📋 Available Load Test Scenarios:")
        print("=" * 60)
        
        for name, scenario in self.scenarios.items():
            print(f"🔹 {name.upper()}")
            print(f"   Description: {scenario.description}")
            print(f"   Users: {scenario.users}")
            print(f"   Spawn Rate: {scenario.spawn_rate}/sec")
            print(f"   Duration: {scenario.duration}")
            print(f"   User Class: {scenario.user_class}")
            print(f"   Tags: {', '.join(scenario.tags)}")
            print()
    
    def run_scenario(self, scenario_name: str, headless: bool = True, 
                    web_ui: bool = False, csv_output: bool = True,
                    html_report: bool = True) -> bool:
        """Run a specific load test scenario"""
        
        if scenario_name not in self.scenarios:
            print(f"❌ Scenario '{scenario_name}' not found")
            return False
        
        scenario = self.scenarios[scenario_name]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        print(f"🚀 Running Load Test: {scenario.name.upper()}")
        print("=" * 60)
        print(f"Description: {scenario.description}")
        print(f"Users: {scenario.users}")
        print(f"Spawn Rate: {scenario.spawn_rate}/sec")
        print(f"Duration: {scenario.duration}")
        print(f"Host: {scenario.host}")
        print(f"User Class: {scenario.user_class}")
        print()
        
        # Build locust command
        cmd = [
            "locust",
            "-f", "tests/load/locustfile.py",
            "--host", scenario.host,
            "--users", str(scenario.users),
            "--spawn-rate", str(scenario.spawn_rate),
            "--run-time", scenario.duration
        ]
        
        # Add output options
        if csv_output:
            csv_prefix = f"tests/load/results/{scenario_name}_{timestamp}"
            cmd.extend(["--csv", csv_prefix])
        
        if html_report:
            html_file = f"tests/load/results/{scenario_name}_{timestamp}.html"
            cmd.extend(["--html", html_file])
        
        # Add headless mode
        if headless and not web_ui:
            cmd.append("--headless")
        
        # Add tags if specified
        if scenario.tags:
            cmd.extend(["--tags", ",".join(scenario.tags)])
        
        print(f"Command: {' '.join(cmd)}")
        print()
        
        try:
            # Run the load test
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print("✅ Load test completed successfully!")
            print()
            
            if csv_output:
                print("📊 CSV Reports generated:")
                print(f"   - {scenario_name}_{timestamp}_stats.csv")
                print(f"   - {scenario_name}_{timestamp}_stats_history.csv")
                print(f"   - {scenario_name}_{timestamp}_failures.csv")
                print(f"   - {scenario_name}_{timestamp}_exceptions.csv")
            
            if html_report:
                print(f"📈 HTML Report: tests/load/results/{scenario_name}_{timestamp}.html")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Load test failed with error: {e}")
            print(f"Error output: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ Locust not found. Please install it with: pip install locust")
            return False
    
    def run_all_scenarios(self, exclude: List[str] = None) -> Dict[str, bool]:
        """Run all load test scenarios"""
        exclude = exclude or []
        results = {}
        
        print("🚀 Running All Load Test Scenarios")
        print("=" * 60)
        
        for name, scenario in self.scenarios.items():
            if name in exclude:
                print(f"⏭️  Skipping {name} (excluded)")
                continue
            
            print(f"\n🔄 Running scenario: {name}")
            success = self.run_scenario(name)
            results[name] = success
            
            if success:
                print(f"✅ {name} completed successfully")
            else:
                print(f"❌ {name} failed")
            
            # Wait between tests
            if name != list(self.scenarios.keys())[-1]:
                print("⏳ Waiting 30 seconds before next test...")
                time.sleep(30)
        
        return results
    
    def generate_summary_report(self, results: Dict[str, bool]):
        """Generate a summary report of all tests"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"load_test_summary_{timestamp}.json"
        
        summary = {
            "timestamp": timestamp,
            "total_scenarios": len(results),
            "passed": sum(1 for success in results.values() if success),
            "failed": sum(1 for success in results.values() if not success),
            "results": results,
            "scenarios": {name: {
                "description": scenario.description,
                "users": scenario.users,
                "spawn_rate": scenario.spawn_rate,
                "duration": scenario.duration,
                "user_class": scenario.user_class,
                "tags": scenario.tags
            } for name, scenario in self.scenarios.items()}
        }
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📋 Summary Report: {report_file}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📊 Total: {summary['total_scenarios']}")

def main():
    """Main function for load testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load Testing Manager")
    parser.add_argument("--scenario", "-s", help="Run specific scenario")
    parser.add_argument("--list", "-l", action="store_true", help="List available scenarios")
    parser.add_argument("--all", "-a", action="store_true", help="Run all scenarios")
    parser.add_argument("--exclude", "-e", nargs="+", help="Exclude scenarios")
    parser.add_argument("--web-ui", "-w", action="store_true", help="Use web UI instead of headless")
    parser.add_argument("--no-csv", action="store_true", help="Disable CSV output")
    parser.add_argument("--no-html", action="store_true", help="Disable HTML report")
    
    args = parser.parse_args()
    
    manager = LoadTestManager()
    
    if args.list:
        manager.list_scenarios()
        return 0
    
    if args.all:
        results = manager.run_all_scenarios(exclude=args.exclude or [])
        manager.generate_summary_report(results)
        return 0 if all(results.values()) else 1
    
    if args.scenario:
        success = manager.run_scenario(
            args.scenario,
            headless=not args.web_ui,
            csv_output=not args.no_csv,
            html_report=not args.no_html
        )
        return 0 if success else 1
    
    # Default: list scenarios
    manager.list_scenarios()
    return 0

if __name__ == "__main__":
    sys.exit(main())
