#!/usr/bin/env python3
"""
Security Test Script - Comprehensive security testing for all API endpoints.
"""

import requests
import time
import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import base64
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityTestResult:
    """Security test result."""
    test_name: str
    endpoint: str
    payload: str
    status_code: int
    response_time: float
    security_headers: Dict[str, str]
    threat_detected: bool
    success: bool
    timestamp: datetime


class SecurityTester:
    """
    Comprehensive security tester for API endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.results = []
        
        # Security test payloads
        self.sql_injection_payloads = [
            "' OR 1=1 --",
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "1' OR '1'='1' --",
            "admin'--",
            "admin'/*",
            "' OR 1=1#",
            "' OR 1=1/*",
            "') OR 1=1 --"
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>"
        ]
        
        self.command_injection_payloads = [
            "; ls -la",
            "| whoami",
            "& dir",
            "` cat /etc/passwd `",
            "$(id)",
            "| cat /etc/passwd",
            "; cat /etc/passwd",
            "& cat /etc/passwd",
            "` whoami `",
            "$(whoami)"
        ]
        
        self.path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd"
        ]
        
        self.ldap_injection_payloads = [
            "*",
            "*)(uid=*",
            "*)(|(uid=*",
            "*)(|(objectClass=*",
            "*)(|(cn=*",
            "*)(|(mail=*",
            "*)(|(telephoneNumber=*",
            "*)(|(userPassword=*",
            "*)(|(description=*",
            "*)(|(title=*"
        ]
        
        self.no_sql_injection_payloads = [
            "{$ne: null}",
            "{$gt: ''}",
            "{$regex: '.*'}",
            "{$where: '1==1'}",
            "{$exists: true}",
            "{$in: []}",
            "{$nin: []}",
            "{$or: []}",
            "{$and: []}",
            "{$not: {}}"
        ]
    
    def authenticate(self, email: str = "test@example.com", password: str = "TestPassword123!") -> bool:
        """Authenticate and get access token."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login/",
                json={"email": email, "password": password},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('data', {}).get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def make_security_request(self, method: str, endpoint: str, payload: str, 
                            parameter: str = "search", **kwargs) -> SecurityTestResult:
        """Make a security test request."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        # Prepare request based on method
        if method.upper() == "GET":
            # Add payload as query parameter
            params = {parameter: payload}
            kwargs['params'] = params
        elif method.upper() == "POST":
            # Add payload to JSON body
            if 'json' not in kwargs:
                kwargs['json'] = {}
            kwargs['json'][parameter] = payload
        elif method.upper() == "PUT":
            # Add payload to JSON body
            if 'json' not in kwargs:
                kwargs['json'] = {}
            kwargs['json'][parameter] = payload
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=30,
                **kwargs
            )
            
            response_time = time.time() - start_time
            
            # Extract security headers
            security_headers = {
                'X-Content-Type-Options': response.headers.get('X-Content-Type-Options'),
                'X-Frame-Options': response.headers.get('X-Frame-Options'),
                'X-XSS-Protection': response.headers.get('X-XSS-Protection'),
                'Strict-Transport-Security': response.headers.get('Strict-Transport-Security'),
                'Content-Security-Policy': response.headers.get('Content-Security-Policy'),
                'X-SQL-Injection-Protection': response.headers.get('X-SQL-Injection-Protection'),
            }
            
            # Check if threat was detected
            threat_detected = (
                response.status_code == 400 or 
                response.status_code == 403 or
                'SECURITY_THREAT_DETECTED' in str(response.text) or
                'security' in str(response.text).lower()
            )
            
            result = SecurityTestResult(
                test_name=f"{method} {endpoint}",
                endpoint=endpoint,
                payload=payload,
                status_code=response.status_code,
                response_time=response_time,
                security_headers=security_headers,
                threat_detected=threat_detected,
                success=threat_detected,  # Success means threat was detected
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Security test error: {e}")
            
            return SecurityTestResult(
                test_name=f"{method} {endpoint}",
                endpoint=endpoint,
                payload=payload,
                status_code=0,
                response_time=response_time,
                security_headers={},
                threat_detected=False,
                success=False,
                timestamp=datetime.now()
            )
    
    def test_sql_injection(self) -> List[SecurityTestResult]:
        """Test SQL injection vulnerabilities."""
        logger.info("🔍 Testing SQL Injection...")
        results = []
        
        # Test endpoints
        test_endpoints = [
            ("GET", "/tickets/", "search"),
            ("GET", "/users/", "email"),
            ("GET", "/organizations/", "name"),
            ("GET", "/knowledge-base/", "title"),
        ]
        
        for method, endpoint, parameter in test_endpoints:
            for payload in self.sql_injection_payloads:
                result = self.make_security_request(method, endpoint, payload, parameter)
                results.append(result)
                
                if result.threat_detected:
                    logger.info(f"✅ SQL injection detected: {payload}")
                else:
                    logger.warning(f"⚠️ SQL injection not detected: {payload}")
                
                time.sleep(0.1)  # Small delay between requests
        
        return results
    
    def test_xss_attacks(self) -> List[SecurityTestResult]:
        """Test XSS vulnerabilities."""
        logger.info("🔍 Testing XSS Attacks...")
        results = []
        
        # Test endpoints with POST data
        test_endpoints = [
            ("POST", "/tickets/", "subject"),
            ("POST", "/tickets/", "description"),
            ("POST", "/knowledge-base/", "title"),
            ("POST", "/knowledge-base/", "content"),
            ("POST", "/users/", "first_name"),
            ("POST", "/users/", "last_name"),
        ]
        
        for method, endpoint, parameter in test_endpoints:
            for payload in self.xss_payloads:
                # Create base data
                base_data = {
                    "subject": "Test",
                    "description": "Test description",
                    "title": "Test title",
                    "content": "Test content",
                    "first_name": "Test",
                    "last_name": "User"
                }
                
                result = self.make_security_request(
                    method, endpoint, payload, parameter, json=base_data
                )
                results.append(result)
                
                if result.threat_detected:
                    logger.info(f"✅ XSS attack detected: {payload[:50]}...")
                else:
                    logger.warning(f"⚠️ XSS attack not detected: {payload[:50]}...")
                
                time.sleep(0.1)
        
        return results
    
    def test_command_injection(self) -> List[SecurityTestResult]:
        """Test command injection vulnerabilities."""
        logger.info("🔍 Testing Command Injection...")
        results = []
        
        # Test endpoints
        test_endpoints = [
            ("GET", "/tickets/", "search"),
            ("GET", "/users/", "email"),
            ("POST", "/tickets/", "subject"),
        ]
        
        for method, endpoint, parameter in test_endpoints:
            for payload in self.command_injection_payloads:
                if method == "POST":
                    base_data = {"subject": "Test", "description": "Test"}
                    result = self.make_security_request(
                        method, endpoint, payload, parameter, json=base_data
                    )
                else:
                    result = self.make_security_request(method, endpoint, payload, parameter)
                
                results.append(result)
                
                if result.threat_detected:
                    logger.info(f"✅ Command injection detected: {payload}")
                else:
                    logger.warning(f"⚠️ Command injection not detected: {payload}")
                
                time.sleep(0.1)
        
        return results
    
    def test_path_traversal(self) -> List[SecurityTestResult]:
        """Test path traversal vulnerabilities."""
        logger.info("🔍 Testing Path Traversal...")
        results = []
        
        # Test endpoints with file parameters
        test_endpoints = [
            ("GET", "/tickets/1/attachments/", "file"),
            ("GET", "/users/1/avatar/", "file"),
            ("GET", "/knowledge-base/1/attachments/", "file"),
        ]
        
        for method, endpoint, parameter in test_endpoints:
            for payload in self.path_traversal_payloads:
                result = self.make_security_request(method, endpoint, payload, parameter)
                results.append(result)
                
                if result.threat_detected:
                    logger.info(f"✅ Path traversal detected: {payload}")
                else:
                    logger.warning(f"⚠️ Path traversal not detected: {payload}")
                
                time.sleep(0.1)
        
        return results
    
    def test_ldap_injection(self) -> List[SecurityTestResult]:
        """Test LDAP injection vulnerabilities."""
        logger.info("🔍 Testing LDAP Injection...")
        results = []
        
        # Test endpoints
        test_endpoints = [
            ("GET", "/users/", "search"),
            ("GET", "/organizations/", "search"),
        ]
        
        for method, endpoint, parameter in test_endpoints:
            for payload in self.ldap_injection_payloads:
                result = self.make_security_request(method, endpoint, payload, parameter)
                results.append(result)
                
                if result.threat_detected:
                    logger.info(f"✅ LDAP injection detected: {payload}")
                else:
                    logger.warning(f"⚠️ LDAP injection not detected: {payload}")
                
                time.sleep(0.1)
        
        return results
    
    def test_no_sql_injection(self) -> List[SecurityTestResult]:
        """Test NoSQL injection vulnerabilities."""
        logger.info("🔍 Testing NoSQL Injection...")
        results = []
        
        # Test endpoints
        test_endpoints = [
            ("GET", "/tickets/", "filter"),
            ("GET", "/users/", "filter"),
            ("POST", "/tickets/", "filter"),
        ]
        
        for method, endpoint, parameter in test_endpoints:
            for payload in self.no_sql_injection_payloads:
                if method == "POST":
                    base_data = {"subject": "Test", "description": "Test"}
                    result = self.make_security_request(
                        method, endpoint, payload, parameter, json=base_data
                    )
                else:
                    result = self.make_security_request(method, endpoint, payload, parameter)
                
                results.append(result)
                
                if result.threat_detected:
                    logger.info(f"✅ NoSQL injection detected: {payload}")
                else:
                    logger.warning(f"⚠️ NoSQL injection not detected: {payload}")
                
                time.sleep(0.1)
        
        return results
    
    def test_file_upload_security(self) -> List[SecurityTestResult]:
        """Test file upload security."""
        logger.info("🔍 Testing File Upload Security...")
        results = []
        
        # Test malicious file uploads
        malicious_files = [
            ("malicious.exe", b"MZ\x90\x00", "application/octet-stream"),
            ("script.php", b"<?php system($_GET['cmd']); ?>", "application/x-php"),
            ("shell.jsp", b"<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>", "application/x-jsp"),
            ("backdoor.asp", b"<% eval request(\"cmd\") %>", "application/x-asp"),
            ("virus.bat", b"@echo off\ndel C:\\Windows\\System32\\*", "application/x-bat"),
        ]
        
        for filename, content, content_type in malicious_files:
            try:
                files = {'file': (filename, content, content_type)}
                data = {'description': 'Test file'}
                
                response = self.session.post(
                    f"{self.base_url}/tickets/1/attachments/",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                threat_detected = (
                    response.status_code == 400 or 
                    response.status_code == 403 or
                    'FILE_UPLOAD_ERROR' in str(response.text) or
                    'security' in str(response.text).lower()
                )
                
                result = SecurityTestResult(
                    test_name="File Upload Security",
                    endpoint="/tickets/1/attachments/",
                    payload=filename,
                    status_code=response.status_code,
                    response_time=0,
                    security_headers={},
                    threat_detected=threat_detected,
                    success=threat_detected,
                    timestamp=datetime.now()
                )
                
                results.append(result)
                
                if threat_detected:
                    logger.info(f"✅ Malicious file upload blocked: {filename}")
                else:
                    logger.warning(f"⚠️ Malicious file upload not blocked: {filename}")
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"File upload test error: {e}")
        
        return results
    
    def test_authentication_security(self) -> List[SecurityTestResult]:
        """Test authentication security."""
        logger.info("🔍 Testing Authentication Security...")
        results = []
        
        # Test weak passwords
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "qwerty",
            "1234567890",
            "abc123",
            "password123",
            "12345678",
            "welcome",
            "monkey"
        ]
        
        for password in weak_passwords:
            try:
                response = self.session.post(
                    f"{self.base_url}/auth/register/",
                    json={
                        "email": f"test{time.time()}@example.com",
                        "password": password,
                        "first_name": "Test",
                        "last_name": "User"
                    },
                    timeout=30
                )
                
                threat_detected = (
                    response.status_code == 400 or 
                    'weak password' in str(response.text).lower() or
                    'password strength' in str(response.text).lower()
                )
                
                result = SecurityTestResult(
                    test_name="Authentication Security",
                    endpoint="/auth/register/",
                    payload=password,
                    status_code=response.status_code,
                    response_time=0,
                    security_headers={},
                    threat_detected=threat_detected,
                    success=threat_detected,
                    timestamp=datetime.now()
                )
                
                results.append(result)
                
                if threat_detected:
                    logger.info(f"✅ Weak password rejected: {password}")
                else:
                    logger.warning(f"⚠️ Weak password accepted: {password}")
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Authentication test error: {e}")
        
        return results
    
    def test_authorization_security(self) -> List[SecurityTestResult]:
        """Test authorization security."""
        logger.info("🔍 Testing Authorization Security...")
        results = []
        
        # Test unauthorized access to protected endpoints
        protected_endpoints = [
            ("GET", "/organizations/999999/"),
            ("PUT", "/organizations/999999/"),
            ("DELETE", "/organizations/999999/"),
            ("GET", "/users/999999/"),
            ("PUT", "/users/999999/"),
            ("DELETE", "/users/999999/"),
        ]
        
        for method, endpoint in protected_endpoints:
            try:
                response = self.session.request(
                    method=method,
                    url=f"{self.base_url}{endpoint}",
                    timeout=30
                )
                
                threat_detected = (
                    response.status_code == 403 or 
                    response.status_code == 404 or
                    'INSUFFICIENT_PERMISSIONS' in str(response.text) or
                    'permission' in str(response.text).lower()
                )
                
                result = SecurityTestResult(
                    test_name="Authorization Security",
                    endpoint=endpoint,
                    payload="",
                    status_code=response.status_code,
                    response_time=0,
                    security_headers={},
                    threat_detected=threat_detected,
                    success=threat_detected,
                    timestamp=datetime.now()
                )
                
                results.append(result)
                
                if threat_detected:
                    logger.info(f"✅ Unauthorized access blocked: {method} {endpoint}")
                else:
                    logger.warning(f"⚠️ Unauthorized access allowed: {method} {endpoint}")
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Authorization test error: {e}")
        
        return results
    
    def analyze_security_results(self, results: List[SecurityTestResult]) -> Dict[str, Any]:
        """Analyze security test results."""
        total_tests = len(results)
        threats_detected = sum(1 for r in results if r.threat_detected)
        security_score = (threats_detected / total_tests * 100) if total_tests > 0 else 0
        
        # Analyze by test type
        test_types = {}
        for result in results:
            test_name = result.test_name
            if test_name not in test_types:
                test_types[test_name] = {'total': 0, 'detected': 0}
            test_types[test_name]['total'] += 1
            if result.threat_detected:
                test_types[test_name]['detected'] += 1
        
        # Calculate security headers coverage
        security_headers = [r.security_headers for r in results if r.security_headers]
        header_coverage = {}
        for headers in security_headers:
            for header, value in headers.items():
                if value:
                    header_coverage[header] = header_coverage.get(header, 0) + 1
        
        analysis = {
            'total_tests': total_tests,
            'threats_detected': threats_detected,
            'security_score': security_score,
            'test_types': test_types,
            'header_coverage': header_coverage,
            'vulnerabilities': [
                {
                    'test_name': r.test_name,
                    'endpoint': r.endpoint,
                    'payload': r.payload,
                    'threat_detected': r.threat_detected,
                    'status_code': r.status_code,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in results if not r.threat_detected
            ]
        }
        
        return analysis
    
    def run_all_security_tests(self) -> Dict[str, Any]:
        """Run all security tests."""
        logger.info("🚀 Starting Comprehensive Security Tests...")
        start_time = time.time()
        
        all_results = []
        
        # Test categories
        test_categories = [
            ("SQL Injection", self.test_sql_injection),
            ("XSS Attacks", self.test_xss_attacks),
            ("Command Injection", self.test_command_injection),
            ("Path Traversal", self.test_path_traversal),
            ("LDAP Injection", self.test_ldap_injection),
            ("NoSQL Injection", self.test_no_sql_injection),
            ("File Upload Security", self.test_file_upload_security),
            ("Authentication Security", self.test_authentication_security),
            ("Authorization Security", self.test_authorization_security),
        ]
        
        # Run tests for each category
        for category_name, test_function in test_categories:
            try:
                logger.info(f"Running {category_name} tests...")
                category_results = test_function()
                all_results.extend(category_results)
                logger.info(f"✅ {category_name} completed: {len(category_results)} tests")
            except Exception as e:
                logger.error(f"❌ {category_name} failed: {e}")
        
        # Analyze results
        analysis = self.analyze_security_results(all_results)
        
        total_time = time.time() - start_time
        
        # Create summary
        summary = {
            "test_execution_time": total_time,
            "total_tests": analysis['total_tests'],
            "threats_detected": analysis['threats_detected'],
            "security_score": analysis['security_score'],
            "test_types": analysis['test_types'],
            "header_coverage": analysis['header_coverage'],
            "vulnerabilities": analysis['vulnerabilities'],
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "endpoint": r.endpoint,
                    "payload": r.payload,
                    "status_code": r.status_code,
                    "response_time": r.response_time,
                    "security_headers": r.security_headers,
                    "threat_detected": r.threat_detected,
                    "success": r.success,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in all_results
            ]
        }
        
        # Log summary
        logger.info("📊 Security Test Summary:")
        logger.info(f"   Total Tests: {analysis['total_tests']}")
        logger.info(f"   Threats Detected: {analysis['threats_detected']}")
        logger.info(f"   Security Score: {analysis['security_score']:.1f}%")
        logger.info(f"   Vulnerabilities Found: {len(analysis['vulnerabilities'])}")
        logger.info(f"   Test Execution Time: {total_time:.2f}s")
        
        return summary
    
    def save_results(self, results: Dict[str, Any], filename: str = "security_test_results.json"):
        """Save test results to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"📁 Security test results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Test Script")
    parser.add_argument("--base-url", default="http://localhost:8000/api/v1", help="Base API URL")
    parser.add_argument("--email", default="test@example.com", help="Test user email")
    parser.add_argument("--password", default="TestPassword123!", help="Test user password")
    parser.add_argument("--output", default="security_test_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    # Create security tester
    tester = SecurityTester(args.base_url)
    
    # Authenticate
    if not tester.authenticate(args.email, args.password):
        logger.error("❌ Authentication failed. Exiting.")
        return
    
    # Run all security tests
    try:
        results = tester.run_all_security_tests()
        tester.save_results(results, args.output)
        
        # Check security score
        if results['security_score'] >= 80:
            logger.info("✅ Security tests passed - Good security posture!")
        elif results['security_score'] >= 60:
            logger.warning("⚠️ Security tests partially passed - Some vulnerabilities found")
        else:
            logger.error("❌ Security tests failed - Multiple vulnerabilities found")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Security tests interrupted by user")
    except Exception as e:
        logger.error(f"💥 Security tests failed with error: {e}")


if __name__ == "__main__":
    main()
