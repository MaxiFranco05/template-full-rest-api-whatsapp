#!/usr/bin/env python3
"""
Test Runner for Professional Flow System
Runs all tests with proper configuration and reporting
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner function"""
    print("🧪 Professional Flow System Test Runner")
    print("=" * 60)
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check if pytest is installed
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pytest is not installed. Installing...")
        subprocess.run(["pip", "install", "pytest"], check=True)
    
    # Run different test suites
    test_suites = [
        {
            "command": "python -m pytest tests/unit/ -v --tb=short",
            "description": "Unit Tests"
        },
        {
            "command": "python -m pytest tests/integration/ -v --tb=short",
            "description": "Integration Tests"
        },
        {
            "command": "python -m pytest tests/flows/ -v --tb=short",
            "description": "Flow Tests"
        },
        {
            "command": "python -m pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term",
            "description": "All Tests with Coverage"
        }
    ]
    
    success_count = 0
    total_tests = len(test_suites)
    
    for test_suite in test_suites:
        if run_command(test_suite["command"], test_suite["description"]):
            success_count += 1
    
    # Run demos
    print(f"\n{'='*60}")
    print("🎭 Running Demos")
    print(f"{'='*60}")
    
    demos = [
        {
            "command": "python demo/simple_main_flow_demo.py",
            "description": "Simple Main Flow Demo"
        },
        {
            "command": "python demo/professional_flow_demo.py",
            "description": "Professional Flow Demo"
        }
    ]
    
    for demo in demos:
        if run_command(demo["command"], demo["description"]):
            success_count += 1
        total_tests += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {total_tests - success_count}")
    print(f"📈 Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 All tests and demos passed successfully!")
        return 0
    else:
        print(f"\n⚠️ {total_tests - success_count} tests/demos failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
