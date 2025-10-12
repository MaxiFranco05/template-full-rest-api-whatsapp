#!/usr/bin/env python3
"""
Advanced Testing Suite Master Runner
"""

import asyncio
import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import argparse

class TestType(Enum):
    """Types of advanced tests"""
    LOAD_TESTING = "load_testing"
    SECURITY_TESTING = "security_testing"
    E2E_TESTING = "e2e_testing"
    PERFORMANCE_BENCHMARKING = "performance_benchmarking"
    CHAOS_ENGINEERING = "chaos_engineering"

@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    test_type: TestType
    script_path: str
    description: str
    estimated_duration: int  # minutes
    dependencies: List[str]
    output_file: str

class AdvancedTestRunner:
    """Master runner for all advanced tests"""
    
    def __init__(self):
        self.test_suites = self._load_test_suites()
        self.results: Dict[str, Any] = {}
        self.start_time = None
        
    def _load_test_suites(self) -> List[TestSuite]:
        """Load all available test suites"""
        return [
            TestSuite(
                name="Load Testing",
                test_type=TestType.LOAD_TESTING,
                script_path="tests/load/run_load_tests.py",
                description="Comprehensive load testing with Locust",
                estimated_duration=30,
                dependencies=["locust"],
                output_file="tests/results/load_test_results.json"
            ),
            TestSuite(
                name="Security Testing",
                test_type=TestType.SECURITY_TESTING,
                script_path="tests/security/security_tests.py",
                description="Security vulnerability testing",
                estimated_duration=10,
                dependencies=["requests"],
                output_file="tests/results/security_test_results.json"
            ),
            TestSuite(
                name="E2E Testing",
                test_type=TestType.E2E_TESTING,
                script_path="tests/e2e/e2e_tests.py",
                description="End-to-end testing with Playwright",
                estimated_duration=15,
                dependencies=["playwright"],
                output_file="tests/results/e2e_test_results.json"
            ),
            TestSuite(
                name="Performance Benchmarking",
                test_type=TestType.PERFORMANCE_BENCHMARKING,
                script_path="tests/benchmarks/performance_benchmark.py",
                description="Performance benchmarking and metrics",
                estimated_duration=20,
                dependencies=["aiohttp"],
                output_file="tests/results/benchmark_results.json"
            ),
            TestSuite(
                name="Chaos Engineering",
                test_type=TestType.CHAOS_ENGINEERING,
                script_path="tests/chaos/chaos_engineering.py",
                description="Chaos engineering resilience testing",
                estimated_duration=25,
                dependencies=["psutil"],
                output_file="tests/results/chaos_results.json"
            )
        ]
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if all dependencies are installed"""
        dependencies = {}
        
        for suite in self.test_suites:
            for dep in suite.dependencies:
                try:
                    __import__(dep)
                    dependencies[dep] = True
                except ImportError:
                    dependencies[dep] = False
        
        return dependencies
    
    def install_dependencies(self, dependencies: Dict[str, bool]) -> bool:
        """Install missing dependencies"""
        missing_deps = [dep for dep, installed in dependencies.items() if not installed]
        
        if not missing_deps:
            return True
        
        print(f"📦 Installing missing dependencies: {', '.join(missing_deps)}")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + missing_deps, check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    def list_test_suites(self):
        """List all available test suites"""
        print("🧪 Available Advanced Test Suites")
        print("=" * 60)
        
        for suite in self.test_suites:
            print(f"🔹 {suite.name}")
            print(f"   Type: {suite.test_type.value}")
            print(f"   Description: {suite.description}")
            print(f"   Estimated Duration: {suite.estimated_duration} minutes")
            print(f"   Dependencies: {', '.join(suite.dependencies)}")
            print(f"   Output: {suite.output_file}")
            print()
    
    async def run_test_suite(self, suite: TestSuite, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test suite"""
        print(f"🚀 Running {suite.name}")
        print("=" * 50)
        print(f"Description: {suite.description}")
        print(f"Script: {suite.script_path}")
        print()
        
        start_time = time.time()
        
        try:
            # Build command
            cmd = [sys.executable, suite.script_path]
            
            # Add common arguments
            if args.get("url"):
                cmd.extend(["--url", args["url"]])
            
            if args.get("verbose"):
                cmd.extend(["--verbose"])
            
            # Add type-specific arguments
            if suite.test_type == TestType.LOAD_TESTING:
                if args.get("scenario"):
                    cmd.extend(["--scenario", args["scenario"]])
                elif args.get("all_scenarios"):
                    cmd.append("--all")
            
            elif suite.test_type == TestType.SECURITY_TESTING:
                if args.get("output"):
                    cmd.extend(["--output", suite.output_file])
            
            elif suite.test_type == TestType.E2E_TESTING:
                if args.get("headless"):
                    cmd.append("--headless")
                if args.get("output"):
                    cmd.extend(["--output", suite.output_file])
            
            elif suite.test_type == TestType.PERFORMANCE_BENCHMARKING:
                if args.get("output"):
                    cmd.extend(["--output", suite.output_file])
            
            elif suite.test_type == TestType.CHAOS_ENGINEERING:
                if args.get("experiment"):
                    cmd.extend(["--experiment", args["experiment"]])
                if args.get("output"):
                    cmd.extend(["--output", suite.output_file])
            
            # Run the test
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            duration = time.time() - start_time
            
            # Parse results
            success = result.returncode == 0
            
            # Try to load output file if it exists
            output_data = {}
            if Path(suite.output_file).exists():
                try:
                    with open(suite.output_file, 'r') as f:
                        output_data = json.load(f)
                except Exception as e:
                    print(f"⚠️  Could not load output file: {e}")
            
            return {
                "suite_name": suite.name,
                "test_type": suite.test_type.value,
                "success": success,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output_data": output_data
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                "suite_name": suite.name,
                "test_type": suite.test_type.value,
                "success": False,
                "duration": duration,
                "error": str(e)
            }
    
    async def run_all_tests(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run all test suites"""
        print("🧪 Running All Advanced Test Suites")
        print("=" * 60)
        
        self.start_time = time.time()
        results = {}
        
        for suite in self.test_suites:
            try:
                result = await self.run_test_suite(suite, args)
                results[suite.test_type.value] = result
                
                status = "✅ PASSED" if result["success"] else "❌ FAILED"
                print(f"{status} - {suite.name} ({result['duration']:.1f}s)")
                
                if not result["success"] and result.get("error"):
                    print(f"   Error: {result['error']}")
                
                # Wait between test suites
                print("⏳ Waiting 10 seconds before next test suite...")
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"❌ ERROR - {suite.name}: {e}")
                results[suite.test_type.value] = {
                    "suite_name": suite.name,
                    "test_type": suite.test_type.value,
                    "success": False,
                    "error": str(e)
                }
        
        total_duration = time.time() - self.start_time
        
        # Generate summary
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result.get("success", False))
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return summary
    
    async def run_specific_test(self, test_type: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific test suite"""
        suite = next((s for s in self.test_suites if s.test_type.value == test_type), None)
        
        if not suite:
            print(f"❌ Test suite '{test_type}' not found")
            return {"error": f"Test suite '{test_type}' not found"}
        
        print(f"🎯 Running Specific Test Suite: {suite.name}")
        print("=" * 60)
        
        self.start_time = time.time()
        
        result = await self.run_test_suite(suite, args)
        
        total_duration = time.time() - self.start_time
        
        return {
            "test_type": test_type,
            "duration": total_duration,
            "result": result
        }
    
    def save_summary(self, summary: Dict[str, Any], filename: str = "tests/results/advanced_tests_summary.json"):
        """Save test summary to file"""
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Test summary saved to: {filename}")
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🧪 ADVANCED TESTING SUITE SUMMARY")
        print("=" * 60)
        print(f"Total Test Suites: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.1f}s")
        print()
        
        # Print individual results
        print("Individual Results:")
        for test_type, result in summary['results'].items():
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            duration = result.get("duration", 0)
            print(f"  {status} - {result.get('suite_name', test_type)} ({duration:.1f}s)")
            
            if not result.get("success", False) and result.get("error"):
                print(f"    Error: {result['error']}")

async def main():
    """Main function for advanced testing"""
    parser = argparse.ArgumentParser(description="Advanced Testing Suite Master Runner")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="Base URL to test")
    parser.add_argument("--list", "-l", action="store_true", help="List available test suites")
    parser.add_argument("--all", "-a", action="store_true", help="Run all test suites")
    parser.add_argument("--test", "-t", help="Run specific test suite")
    parser.add_argument("--scenario", "-s", help="Load test scenario (for load testing)")
    parser.add_argument("--experiment", "-e", help="Chaos experiment name (for chaos engineering)")
    parser.add_argument("--output", "-o", help="Output file for summary")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--headless", action="store_true", help="Run E2E tests in headless mode")
    parser.add_argument("--install-deps", action="store_true", help="Install missing dependencies")
    
    args = parser.parse_args()
    
    runner = AdvancedTestRunner()
    
    # Check dependencies
    dependencies = runner.check_dependencies()
    missing_deps = [dep for dep, installed in dependencies.items() if not installed]
    
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        if args.install_deps:
            if not runner.install_dependencies(dependencies):
                return 1
        else:
            print("Use --install-deps to install missing dependencies")
            return 1
    
    # List test suites
    if args.list:
        runner.list_test_suites()
        return 0
    
    # Prepare arguments
    test_args = {
        "url": args.url,
        "verbose": args.verbose,
        "headless": args.headless,
        "scenario": args.scenario,
        "experiment": args.experiment,
        "output": args.output
    }
    
    # Run tests
    if args.all:
        summary = await runner.run_all_tests(test_args)
        runner.print_summary(summary)
        
        # Save summary
        output_file = args.output or "tests/results/advanced_tests_summary.json"
        runner.save_summary(summary, output_file)
        
        return 0 if summary['success_rate'] == 100 else 1
    
    elif args.test:
        result = await runner.run_specific_test(args.test, test_args)
        
        if "error" in result:
            print(f"❌ {result['error']}")
            return 1
        
        print(f"\n🎯 Test completed in {result['duration']:.1f}s")
        
        test_result = result['result']
        status = "✅ PASSED" if test_result['success'] else "❌ FAILED"
        print(f"Status: {status}")
        
        if not test_result['success'] and test_result.get('error'):
            print(f"Error: {test_result['error']}")
        
        return 0 if test_result['success'] else 1
    
    else:
        # Default: list test suites
        runner.list_test_suites()
        print("\nUse --all to run all tests or --test <type> to run specific test")
        return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
