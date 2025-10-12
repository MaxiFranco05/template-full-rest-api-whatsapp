# Security Testing Suite

"""
Comprehensive security testing suite for Business API Template
"""

import requests
import json
import time
import hashlib
import base64
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SecurityTestType(Enum):
    """Types of security tests"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    INPUT_VALIDATION = "input_validation"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    RATE_LIMITING = "rate_limiting"
    HEADERS = "headers"
    SSL_TLS = "ssl_tls"
    FILE_UPLOAD = "file_upload"

@dataclass
class SecurityTestResult:
    """Result of a security test"""
    test_type: SecurityTestType
    test_name: str
    passed: bool
    severity: str  # low, medium, high, critical
    description: str
    details: Dict[str, Any]
    recommendations: List[str]

class SecurityTester:
    """Main security testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.test_results: List[SecurityTestResult] = []
        
        # Common payloads for testing
        self.sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "1' OR 1=1 --",
            "admin'--",
            "' OR 1=1 #"
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        self.file_upload_payloads = [
            "test.php",
            "test.jsp",
            "test.asp",
            "test.exe",
            "test.bat",
            "test.sh"
        ]
    
    def authenticate(self, username: str = "testuser", password: str = "testpassword") -> bool:
        """Authenticate and get token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data["data"]["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.token}"
                    })
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def test_authentication_bypass(self) -> SecurityTestResult:
        """Test for authentication bypass vulnerabilities"""
        test_name = "Authentication Bypass"
        vulnerabilities = []
        
        # Test 1: Access protected endpoints without token
        protected_endpoints = [
            "/api/v1/users/",
            "/api/v1/products/",
            "/api/v1/whatsapp/conversations/"
        ]
        
        for endpoint in protected_endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code == 200:
                vulnerabilities.append(f"Endpoint {endpoint} accessible without authentication")
        
        # Test 2: Invalid token handling
        self.session.headers.update({"Authorization": "Bearer invalid_token"})
        for endpoint in protected_endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code == 200:
                vulnerabilities.append(f"Endpoint {endpoint} accessible with invalid token")
        
        # Test 3: Empty token
        self.session.headers.update({"Authorization": "Bearer "})
        for endpoint in protected_endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code == 200:
                vulnerabilities.append(f"Endpoint {endpoint} accessible with empty token")
        
        # Restore valid token
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        passed = len(vulnerabilities) == 0
        severity = "critical" if vulnerabilities else "low"
        
        return SecurityTestResult(
            test_type=SecurityTestType.AUTHENTICATION,
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=f"Tested authentication bypass vulnerabilities",
            details={"vulnerabilities": vulnerabilities},
            recommendations=[
                "Ensure all protected endpoints require valid authentication",
                "Implement proper token validation",
                "Return 401 for invalid or missing tokens"
            ]
        )
    
    def test_authorization_bypass(self) -> SecurityTestResult:
        """Test for authorization bypass vulnerabilities"""
        test_name = "Authorization Bypass"
        vulnerabilities = []
        
        if not self.token:
            return SecurityTestResult(
                test_type=SecurityTestType.AUTHORIZATION,
                test_name=test_name,
                passed=False,
                severity="high",
                description="Cannot test authorization without authentication",
                details={"error": "No authentication token"},
                recommendations=["Ensure authentication is working"]
            )
        
        # Test 1: Access other users' data
        response = self.session.get(f"{self.base_url}/api/v1/users/1")
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data["data"].get("id") != 1:
                vulnerabilities.append("Can access other users' data")
        
        # Test 2: Modify other users' data
        response = self.session.put(
            f"{self.base_url}/api/v1/users/1",
            json={"full_name": "Hacked User"}
        )
        if response.status_code == 200:
            vulnerabilities.append("Can modify other users' data")
        
        # Test 3: Delete other users' data
        response = self.session.delete(f"{self.base_url}/api/v1/users/1")
        if response.status_code == 200:
            vulnerabilities.append("Can delete other users' data")
        
        passed = len(vulnerabilities) == 0
        severity = "high" if vulnerabilities else "low"
        
        return SecurityTestResult(
            test_type=SecurityTestType.AUTHORIZATION,
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=f"Tested authorization bypass vulnerabilities",
            details={"vulnerabilities": vulnerabilities},
            recommendations=[
                "Implement proper user ownership checks",
                "Use user context in all operations",
                "Implement role-based access control"
            ]
        )
    
    def test_sql_injection(self) -> SecurityTestResult:
        """Test for SQL injection vulnerabilities"""
        test_name = "SQL Injection"
        vulnerabilities = []
        
        # Test endpoints with user input
        test_endpoints = [
            ("/api/v1/users/", "GET", {"page": "1"}),
            ("/api/v1/products/", "GET", {"search": "test"}),
            ("/api/v1/products/", "POST", {"name": "test", "price": "100"})
        ]
        
        for endpoint, method, params in test_endpoints:
            for payload in self.sql_payloads:
                try:
                    if method == "GET":
                        response = self.session.get(
                            f"{self.base_url}{endpoint}",
                            params={**params, "test": payload}
                        )
                    else:
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            json={**params, "test": payload}
                        )
                    
                    # Check for SQL error patterns
                    response_text = response.text.lower()
                    sql_errors = [
                        "sql syntax",
                        "mysql error",
                        "postgresql error",
                        "sqlite error",
                        "database error",
                        "sqlstate"
                    ]
                    
                    if any(error in response_text for error in sql_errors):
                        vulnerabilities.append(f"SQL injection in {endpoint} with payload: {payload}")
                
                except Exception as e:
                    logger.error(f"SQL injection test error: {e}")
        
        passed = len(vulnerabilities) == 0
        severity = "critical" if vulnerabilities else "low"
        
        return SecurityTestResult(
            test_type=SecurityTestType.SQL_INJECTION,
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=f"Tested SQL injection vulnerabilities",
            details={"vulnerabilities": vulnerabilities},
            recommendations=[
                "Use parameterized queries",
                "Implement input validation",
                "Use ORM with proper escaping",
                "Implement SQL injection detection"
            ]
        )
    
    def test_xss_vulnerabilities(self) -> SecurityTestResult:
        """Test for XSS vulnerabilities"""
        test_name = "Cross-Site Scripting (XSS)"
        vulnerabilities = []
        
        # Test XSS in various input fields
        test_data = {
            "name": "Test Product",
            "description": "Test Description",
            "full_name": "Test User",
            "email": "test@example.com"
        }
        
        for field, value in test_data.items():
            for payload in self.xss_payloads:
                try:
                    # Test in product creation
                    if field in ["name", "description"]:
                        response = self.session.post(
                            f"{self.base_url}/api/v1/products/",
                            json={field: payload, "price": 100, "stock_quantity": 10}
                        )
                    
                    # Test in user creation/update
                    elif field in ["full_name", "email"]:
                        response = self.session.post(
                            f"{self.base_url}/api/v1/users/",
                            json={field: payload, "username": "testuser", "password": "testpass"}
                        )
                    
                    # Check if payload is reflected in response
                    if response.status_code in [200, 201]:
                        response_text = response.text
                        if payload in response_text:
                            vulnerabilities.append(f"XSS vulnerability in {field} with payload: {payload}")
                
                except Exception as e:
                    logger.error(f"XSS test error: {e}")
        
        passed = len(vulnerabilities) == 0
        severity = "high" if vulnerabilities else "low"
        
        return SecurityTestResult(
            test_type=SecurityTestType.XSS,
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=f"Tested XSS vulnerabilities",
            details={"vulnerabilities": vulnerabilities},
            recommendations=[
                "Implement input sanitization",
                "Use output encoding",
                "Implement Content Security Policy (CSP)",
                "Validate and escape all user input"
            ]
        )
    
    def test_rate_limiting(self) -> SecurityTestResult:
        """Test rate limiting implementation"""
        test_name = "Rate Limiting"
        vulnerabilities = []
        
        # Test rate limiting on authentication endpoint
        auth_endpoint = f"{self.base_url}/api/v1/auth/login"
        rapid_requests = 20  # Try to exceed rate limit
        
        for i in range(rapid_requests):
            response = self.session.post(
                auth_endpoint,
                json={"username": "testuser", "password": "wrongpassword"}
            )
            
            if response.status_code == 429:
                break  # Rate limit working
        else:
            vulnerabilities.append("Authentication endpoint not rate limited")
        
        # Test rate limiting on API endpoints
        api_endpoints = [
            "/api/v1/users/",
            "/api/v1/products/",
            "/api/v1/whatsapp/conversations/"
        ]
        
        for endpoint in api_endpoints:
            rapid_requests = 100  # Try to exceed rate limit
            
            for i in range(rapid_requests):
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 429:
                    break  # Rate limit working
            else:
                vulnerabilities.append(f"API endpoint {endpoint} not rate limited")
        
        passed = len(vulnerabilities) == 0
        severity = "medium" if vulnerabilities else "low"
        
        return SecurityTestResult(
            test_type=SecurityTestType.RATE_LIMITING,
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=f"Tested rate limiting implementation",
            details={"vulnerabilities": vulnerabilities},
            recommendations=[
                "Implement rate limiting on all endpoints",
                "Use different limits for different endpoints",
                "Implement IP-based rate limiting",
                "Add rate limit headers to responses"
            ]
        )
    
    def test_security_headers(self) -> SecurityTestResult:
        """Test security headers implementation"""
        test_name = "Security Headers"
        vulnerabilities = []
        missing_headers = []
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        response = self.session.get(f"{self.base_url}/health")
        response_headers = response.headers
        
        for header in required_headers:
            if header not in response_headers:
                missing_headers.append(header)
        
        if missing_headers:
            vulnerabilities.append(f"Missing security headers: {', '.join(missing_headers)}")
        
        passed = len(vulnerabilities) == 0
        severity = "medium" if vulnerabilities else "low"
        
        return SecurityTestResult(
            test_type=SecurityTestType.HEADERS,
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=f"Tested security headers implementation",
            details={"missing_headers": missing_headers},
            recommendations=[
                "Implement all required security headers",
                "Use Content Security Policy (CSP)",
                "Enable HSTS for HTTPS",
                "Configure X-Frame-Options to prevent clickjacking"
            ]
        )
    
    def test_file_upload_security(self) -> SecurityTestResult:
        """Test file upload security"""
        test_name = "File Upload Security"
        vulnerabilities = []
        
        # Test malicious file uploads
        for payload in self.file_upload_payloads:
            try:
                # Create a fake file content
                file_content = b"<?php echo 'malicious code'; ?>"
                
                files = {
                    'file': (payload, file_content, 'application/octet-stream')
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/upload",
                    files=files
                )
                
                if response.status_code in [200, 201]:
                    vulnerabilities.append(f"Malicious file upload allowed: {payload}")
            
            except Exception as e:
                logger.error(f"File upload test error: {e}")
        
        passed = len(vulnerabilities) == 0
        severity = "high" if vulnerabilities else "low"
        
        return SecurityTestResult(
            test_type=SecurityTestType.FILE_UPLOAD,
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=f"Tested file upload security",
            details={"vulnerabilities": vulnerabilities},
            recommendations=[
                "Implement file type validation",
                "Scan uploaded files for malware",
                "Store files outside web root",
                "Implement file size limits",
                "Use whitelist of allowed file types"
            ]
        )
    
    def test_input_validation(self) -> SecurityTestResult:
        """Test input validation"""
        test_name = "Input Validation"
        vulnerabilities = []
        
        # Test various input validation scenarios
        test_cases = [
            # SQL injection attempts
            {"name": "'; DROP TABLE users; --", "expected": "rejected"},
            # XSS attempts
            {"name": "<script>alert('XSS')</script>", "expected": "sanitized"},
            # Path traversal
            {"name": "../../../etc/passwd", "expected": "rejected"},
            # Command injection
            {"name": "; rm -rf /", "expected": "rejected"},
            # Buffer overflow
            {"name": "A" * 10000, "expected": "truncated"},
            # Special characters
            {"name": "test\x00null", "expected": "sanitized"}
        ]
        
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/products/",
                    json={
                        "name": test_case["name"],
                        "price": 100,
                        "stock_quantity": 10
                    }
                )
                
                if response.status_code == 201:
                    data = response.json()
                    if data.get("success"):
                        # Check if input was properly handled
                        returned_name = data["data"].get("name", "")
                        if test_case["name"] in returned_name and test_case["expected"] == "rejected":
                            vulnerabilities.append(f"Input validation failed for: {test_case['name']}")
            
            except Exception as e:
                logger.error(f"Input validation test error: {e}")
        
        passed = len(vulnerabilities) == 0
        severity = "high" if vulnerabilities else "low"
        
        return SecurityTestResult(
            test_type=SecurityTestType.INPUT_VALIDATION,
            test_name=test_name,
            passed=passed,
            severity=severity,
            description=f"Tested input validation",
            details={"vulnerabilities": vulnerabilities},
            recommendations=[
                "Implement comprehensive input validation",
                "Use whitelist validation where possible",
                "Implement input sanitization",
                "Validate all user inputs on server side"
            ]
        )
    
    def run_all_tests(self) -> List[SecurityTestResult]:
        """Run all security tests"""
        print("🔒 Running Security Tests")
        print("=" * 50)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed, some tests may not work properly")
        
        # Run all tests
        tests = [
            self.test_authentication_bypass,
            self.test_authorization_bypass,
            self.test_sql_injection,
            self.test_xss_vulnerabilities,
            self.test_rate_limiting,
            self.test_security_headers,
            self.test_file_upload_security,
            self.test_input_validation
        ]
        
        for test_func in tests:
            try:
                print(f"Running {test_func.__name__}...")
                result = test_func()
                self.test_results.append(result)
                
                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"  {status} - {result.test_name} ({result.severity})")
                
                if not result.passed and result.details.get("vulnerabilities"):
                    for vuln in result.details["vulnerabilities"]:
                        print(f"    ⚠️  {vuln}")
                
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed: {e}")
                print(f"  ❌ ERROR - {test_func.__name__}: {e}")
        
        return self.test_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate security test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        
        # Count by severity
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for result in self.test_results:
            if not result.passed:
                severity_counts[result.severity] += 1
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "severity_breakdown": severity_counts,
            "test_results": [
                {
                    "test_type": result.test_type.value,
                    "test_name": result.test_name,
                    "passed": result.passed,
                    "severity": result.severity,
                    "description": result.description,
                    "details": result.details,
                    "recommendations": result.recommendations
                }
                for result in self.test_results
            ],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return report

def main():
    """Main function for security testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Testing Suite")
    parser.add_argument("--url", "-u", default="http://localhost:8000", help="Base URL to test")
    parser.add_argument("--output", "-o", help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    # Run security tests
    tester = SecurityTester(args.url)
    results = tester.run_all_tests()
    
    # Generate report
    report = tester.generate_report()
    
    print("\n" + "=" * 60)
    print("🔒 SECURITY TEST REPORT")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
    print()
    
    print("Severity Breakdown:")
    for severity, count in report['severity_breakdown'].items():
        if count > 0:
            print(f"  {severity.upper()}: {count}")
    
    # Save report
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 0 if report['summary']['failed'] == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
