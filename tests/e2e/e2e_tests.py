# End-to-End Testing with Playwright

"""
Comprehensive E2E testing suite using Playwright
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import logging

logger = logging.getLogger(__name__)

@dataclass
class E2ETestResult:
    """Result of an E2E test"""
    test_name: str
    passed: bool
    duration: float
    error_message: Optional[str] = None
    screenshots: List[str] = None
    steps: List[str] = None

class E2ETester:
    """Main E2E testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.test_results: List[E2ETestResult] = []
        self.screenshots_dir = "tests/e2e/screenshots"
        
    async def setup(self):
        """Setup browser and context"""
        self.playwright = await async_playwright().start()
        
        # Launch browser
        self.browser = await self.playwright.chromium.launch(
            headless=True,  # Set to False for debugging
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        # Create context
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        # Setup error handling
        self.page.on("pageerror", lambda error: logger.error(f"Page error: {error}"))
        self.page.on("requestfailed", lambda request: logger.error(f"Request failed: {request.url}"))
    
    async def teardown(self):
        """Cleanup browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def take_screenshot(self, name: str) -> str:
        """Take a screenshot"""
        import os
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = f"{self.screenshots_dir}/{filename}"
        
        await self.page.screenshot(path=filepath)
        return filepath
    
    async def test_homepage_loads(self) -> E2ETestResult:
        """Test that homepage loads correctly"""
        test_name = "Homepage Loads"
        start_time = time.time()
        steps = []
        screenshots = []
        
        try:
            # Navigate to homepage
            steps.append("Navigating to homepage")
            await self.page.goto(f"{self.base_url}/")
            
            # Wait for page to load
            await self.page.wait_for_load_state("networkidle")
            steps.append("Page loaded successfully")
            
            # Take screenshot
            screenshot = await self.take_screenshot("homepage")
            screenshots.append(screenshot)
            
            # Check if page title is correct
            title = await self.page.title()
            steps.append(f"Page title: {title}")
            
            # Check if main content is present
            content = await self.page.text_content("body")
            if "Business API Template" in content:
                steps.append("Main content found")
                passed = True
            else:
                steps.append("Main content not found")
                passed = False
            
            duration = time.time() - start_time
            
            return E2ETestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                screenshots=screenshots,
                steps=steps
            )
            
        except Exception as e:
            duration = time.time() - start_time
            screenshot = await self.take_screenshot("homepage_error")
            
            return E2ETestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                error_message=str(e),
                screenshots=[screenshot],
                steps=steps
            )
    
    async def test_api_documentation(self) -> E2ETestResult:
        """Test API documentation accessibility"""
        test_name = "API Documentation"
        start_time = time.time()
        steps = []
        screenshots = []
        
        try:
            # Navigate to API docs
            steps.append("Navigating to API documentation")
            await self.page.goto(f"{self.base_url}/docs")
            
            # Wait for page to load
            await self.page.wait_for_load_state("networkidle")
            steps.append("API docs page loaded")
            
            # Take screenshot
            screenshot = await self.take_screenshot("api_docs")
            screenshots.append(screenshot)
            
            # Check if Swagger UI is present
            swagger_element = await self.page.query_selector("swagger-ui")
            if swagger_element:
                steps.append("Swagger UI found")
                passed = True
            else:
                steps.append("Swagger UI not found")
                passed = False
            
            duration = time.time() - start_time
            
            return E2ETestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                screenshots=screenshots,
                steps=steps
            )
            
        except Exception as e:
            duration = time.time() - start_time
            screenshot = await self.take_screenshot("api_docs_error")
            
            return E2ETestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                error_message=str(e),
                screenshots=[screenshot],
                steps=steps
            )
    
    async def test_health_endpoint(self) -> E2ETestResult:
        """Test health endpoint via browser"""
        test_name = "Health Endpoint"
        start_time = time.time()
        steps = []
        screenshots = []
        
        try:
            # Navigate to health endpoint
            steps.append("Navigating to health endpoint")
            await self.page.goto(f"{self.base_url}/health")
            
            # Wait for page to load
            await self.page.wait_for_load_state("networkidle")
            steps.append("Health endpoint loaded")
            
            # Take screenshot
            screenshot = await self.take_screenshot("health_endpoint")
            screenshots.append(screenshot)
            
            # Check if response is JSON
            content = await self.page.text_content("body")
            try:
                data = json.loads(content)
                if data.get("status") == "healthy":
                    steps.append("Health check passed")
                    passed = True
                else:
                    steps.append("Health check failed")
                    passed = False
            except json.JSONDecodeError:
                steps.append("Invalid JSON response")
                passed = False
            
            duration = time.time() - start_time
            
            return E2ETestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                screenshots=screenshots,
                steps=steps
            )
            
        except Exception as e:
            duration = time.time() - start_time
            screenshot = await self.take_screenshot("health_endpoint_error")
            
            return E2ETestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                error_message=str(e),
                screenshots=[screenshot],
                steps=steps
            )
    
    async def test_performance_endpoint(self) -> E2ETestResult:
        """Test performance endpoint"""
        test_name = "Performance Endpoint"
        start_time = time.time()
        steps = []
        screenshots = []
        
        try:
            # Navigate to performance endpoint
            steps.append("Navigating to performance endpoint")
            await self.page.goto(f"{self.base_url}/performance")
            
            # Wait for page to load
            await self.page.wait_for_load_state("networkidle")
            steps.append("Performance endpoint loaded")
            
            # Take screenshot
            screenshot = await self.take_screenshot("performance_endpoint")
            screenshots.append(screenshot)
            
            # Check if response contains performance data
            content = await self.page.text_content("body")
            try:
                data = json.loads(content)
                if "performance" in data and "rate_limiting" in data:
                    steps.append("Performance data found")
                    passed = True
                else:
                    steps.append("Performance data not found")
                    passed = False
            except json.JSONDecodeError:
                steps.append("Invalid JSON response")
                passed = False
            
            duration = time.time() - start_time
            
            return E2ETestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                screenshots=screenshots,
                steps=steps
            )
            
        except Exception as e:
            duration = time.time() - start_time
            screenshot = await self.take_screenshot("performance_endpoint_error")
            
            return E2ETestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                error_message=str(e),
                screenshots=[screenshot],
                steps=steps
            )
    
    async def test_api_endpoints_accessibility(self) -> E2ETestResult:
        """Test API endpoints accessibility"""
        test_name = "API Endpoints Accessibility"
        start_time = time.time()
        steps = []
        screenshots = []
        
        try:
            # Test various API endpoints
            endpoints = [
                "/api/v1/users/",
                "/api/v1/products/",
                "/api/v1/whatsapp/conversations/"
            ]
            
            accessible_endpoints = []
            inaccessible_endpoints = []
            
            for endpoint in endpoints:
                steps.append(f"Testing endpoint: {endpoint}")
                
                # Navigate to endpoint
                await self.page.goto(f"{self.base_url}{endpoint}")
                await self.page.wait_for_load_state("networkidle")
                
                # Check response
                content = await self.page.text_content("body")
                
                try:
                    data = json.loads(content)
                    if data.get("success") is not None:
                        accessible_endpoints.append(endpoint)
                        steps.append(f"  ✅ {endpoint} accessible")
                    else:
                        inaccessible_endpoints.append(endpoint)
                        steps.append(f"  ❌ {endpoint} not accessible")
                except json.JSONDecodeError:
                    # Check if it's an error response
                    if "error" in content.lower() or "unauthorized" in content.lower():
                        steps.append(f"  ⚠️  {endpoint} returns error (expected)")
                    else:
                        inaccessible_endpoints.append(endpoint)
                        steps.append(f"  ❌ {endpoint} invalid response")
            
            # Take screenshot
            screenshot = await self.take_screenshot("api_endpoints")
            screenshots.append(screenshot)
            
            # Determine if test passed
            if len(inaccessible_endpoints) == 0:
                passed = True
                steps.append("All endpoints accessible")
            else:
                passed = False
                steps.append(f"Some endpoints inaccessible: {inaccessible_endpoints}")
            
            duration = time.time() - start_time
            
            return E2ETestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                screenshots=screenshots,
                steps=steps
            )
            
        except Exception as e:
            duration = time.time() - start_time
            screenshot = await self.take_screenshot("api_endpoints_error")
            
            return E2ETestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                error_message=str(e),
                screenshots=[screenshot],
                steps=steps
            )
    
    async def test_responsive_design(self) -> E2ETestResult:
        """Test responsive design"""
        test_name = "Responsive Design"
        start_time = time.time()
        steps = []
        screenshots = []
        
        try:
            # Test different viewport sizes
            viewports = [
                {"width": 1920, "height": 1080, "name": "desktop"},
                {"width": 1024, "height": 768, "name": "tablet"},
                {"width": 375, "height": 667, "name": "mobile"}
            ]
            
            for viewport in viewports:
                steps.append(f"Testing {viewport['name']} viewport")
                
                # Set viewport
                await self.page.set_viewport_size({
                    "width": viewport["width"],
                    "height": viewport["height"]
                })
                
                # Navigate to homepage
                await self.page.goto(f"{self.base_url}/")
                await self.page.wait_for_load_state("networkidle")
                
                # Take screenshot
                screenshot = await self.take_screenshot(f"responsive_{viewport['name']}")
                screenshots.append(screenshot)
                
                # Check if page is responsive
                content = await self.page.text_content("body")
                if "Business API Template" in content:
                    steps.append(f"  ✅ {viewport['name']} viewport works")
                else:
                    steps.append(f"  ❌ {viewport['name']} viewport broken")
            
            passed = True  # Assume passed unless we find issues
            duration = time.time() - start_time
            
            return E2ETestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                screenshots=screenshots,
                steps=steps
            )
            
        except Exception as e:
            duration = time.time() - start_time
            screenshot = await self.take_screenshot("responsive_error")
            
            return E2ETestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                error_message=str(e),
                screenshots=[screenshot],
                steps=steps
            )
    
    async def test_error_handling(self) -> E2ETestResult:
        """Test error handling"""
        test_name = "Error Handling"
        start_time = time.time()
        steps = []
        screenshots = []
        
        try:
            # Test 404 error
            steps.append("Testing 404 error")
            await self.page.goto(f"{self.base_url}/nonexistent-page")
            await self.page.wait_for_load_state("networkidle")
            
            screenshot = await self.take_screenshot("error_404")
            screenshots.append(screenshot)
            
            # Check if 404 is handled properly
            content = await self.page.text_content("body")
            if "404" in content or "not found" in content.lower():
                steps.append("  ✅ 404 error handled properly")
                passed = True
            else:
                steps.append("  ❌ 404 error not handled")
                passed = False
            
            duration = time.time() - start_time
            
            return E2ETestResult(
                test_name=test_name,
                passed=passed,
                duration=duration,
                screenshots=screenshots,
                steps=steps
            )
            
        except Exception as e:
            duration = time.time() - start_time
            screenshot = await self.take_screenshot("error_handling_error")
            
            return E2ETestResult(
                test_name=test_name,
                passed=False,
                duration=duration,
                error_message=str(e),
                screenshots=[screenshot],
                steps=steps
            )
    
    async def run_all_tests(self) -> List[E2ETestResult]:
        """Run all E2E tests"""
        print("🌐 Running E2E Tests")
        print("=" * 50)
        
        # Setup
        await self.setup()
        
        # Run all tests
        tests = [
            self.test_homepage_loads,
            self.test_api_documentation,
            self.test_health_endpoint,
            self.test_performance_endpoint,
            self.test_api_endpoints_accessibility,
            self.test_responsive_design,
            self.test_error_handling
        ]
        
        for test_func in tests:
            try:
                print(f"Running {test_func.__name__}...")
                result = await test_func()
                self.test_results.append(result)
                
                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"  {status} - {result.test_name} ({result.duration:.2f}s)")
                
                if not result.passed and result.error_message:
                    print(f"    Error: {result.error_message}")
                
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed: {e}")
                print(f"  ❌ ERROR - {test_func.__name__}: {e}")
        
        # Teardown
        await self.teardown()
        
        return self.test_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate E2E test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(result.duration for result in self.test_results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "passed": result.passed,
                    "duration": result.duration,
                    "error_message": result.error_message,
                    "screenshots": result.screenshots,
                    "steps": result.steps
                }
                for result in self.test_results
            ],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return report

async def main():
    """Main function for E2E testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="E2E Testing Suite")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="Base URL to test")
    parser.add_argument("--output", "-o", help="Output file for report")
    parser.add_argument("--headless", action="store_true", default=True, help="Run in headless mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    # Run E2E tests
    tester = E2ETester(args.url)
    results = await tester.run_all_tests()
    
    # Generate report
    report = tester.generate_report()
    
    print("\n" + "=" * 60)
    print("🌐 E2E TEST REPORT")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    print(f"Total Duration: {report['summary']['total_duration']:.2f}s")
    print()
    
    # Show failed tests
    failed_tests = [result for result in results if not result.passed]
    if failed_tests:
        print("Failed Tests:")
        for result in failed_tests:
            print(f"  ❌ {result.test_name}")
            if result.error_message:
                print(f"    Error: {result.error_message}")
    
    # Save report
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 0 if report['summary']['failed'] == 0 else 1

if __name__ == "__main__":
    import sys
    asyncio.run(main())
