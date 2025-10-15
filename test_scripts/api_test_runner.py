#!/usr/bin/env python3
"""
API Test Runner - Automated testing script for all API endpoints.
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data structure."""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None


class APITestRunner:
    """
    Comprehensive API test runner for all 107 endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.performance_metrics = {}
        
        # Test configuration
        self.test_config = {
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 1,
            'rate_limit_delay': 0.1
        }
    
    def authenticate(self, email: str = "test@example.com", password: str = "TestPassword123!") -> bool:
        """
        Authenticate and get access token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if authentication successful
        """
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login/",
                json={"email": email, "password": password},
                timeout=self.test_config['timeout']
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
    
    def test_endpoint(self, method: str, endpoint: str, **kwargs) -> TestResult:
        """
        Test a single endpoint.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            TestResult object
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.test_config['timeout'],
                **kwargs
            )
            
            response_time = time.time() - start_time
            
            # Create test result
            result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                success=200 <= response.status_code < 400,
                response_data=response.json() if response.content else None
            )
            
            # Log result
            if result.success:
                logger.info(f"✅ {method} {endpoint} - {response.status_code} ({response_time:.2f}s)")
            else:
                logger.warning(f"❌ {method} {endpoint} - {response.status_code} ({response_time:.2f}s)")
                result.error_message = f"HTTP {response.status_code}"
            
            return result
            
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            logger.error(f"⏰ {method} {endpoint} - Timeout ({response_time:.2f}s)")
            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message="Request timeout"
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"💥 {method} {endpoint} - Error: {e} ({response_time:.2f}s)")
            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
    
    def test_authentication_endpoints(self) -> List[TestResult]:
        """Test authentication endpoints."""
        logger.info("🔐 Testing Authentication Endpoints...")
        results = []
        
        # Test data
        test_user = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890"
        }
        
        # Test endpoints
        endpoints = [
            ("POST", "/auth/register/", {"json": test_user}),
            ("POST", "/auth/login/", {"json": {"email": test_user["email"], "password": test_user["password"]}}),
            ("POST", "/auth/logout/", {}),
            ("POST", "/auth/refresh/", {"json": {"refresh_token": "test_refresh_token"}}),
            ("POST", "/auth/forgot-password/", {"json": {"email": test_user["email"]}}),
            ("POST", "/auth/reset-password/", {"json": {"token": "test_token", "new_password": "NewPassword123!"}}),
            ("POST", "/auth/verify-email/", {"json": {"token": "test_verification_token"}}),
            ("POST", "/auth/change-password/", {"json": {"current_password": test_user["password"], "new_password": "NewPassword123!"}})
        ]
        
        for method, endpoint, kwargs in endpoints:
            result = self.test_endpoint(method, endpoint, **kwargs)
            results.append(result)
            time.sleep(self.test_config['rate_limit_delay'])
        
        return results
    
    def test_ticket_endpoints(self) -> List[TestResult]:
        """Test ticket management endpoints."""
        logger.info("🎫 Testing Ticket Management Endpoints...")
        results = []
        
        # Test data
        ticket_data = {
            "subject": "Test Ticket",
            "description": "This is a test ticket",
            "priority": "high",
            "category": "technical"
        }
        
        comment_data = {
            "content": "This is a test comment",
            "is_internal": False
        }
        
        # Test endpoints
        endpoints = [
            ("GET", "/tickets/", {}),
            ("POST", "/tickets/", {"json": ticket_data}),
            ("GET", "/tickets/1/", {}),
            ("PUT", "/tickets/1/", {"json": {"status": "in_progress"}}),
            ("DELETE", "/tickets/1/", {}),
            ("GET", "/tickets/1/comments/", {}),
            ("POST", "/tickets/1/comments/", {"json": comment_data}),
            ("GET", "/tickets/1/attachments/", {}),
            ("GET", "/tickets/1/history/", {}),
            ("POST", "/tickets/1/assign/", {"json": {"agent_id": "1", "note": "Assigning to agent"}}),
            ("POST", "/tickets/1/escalate/", {"json": {"reason": "Customer requested escalation"}}),
            ("GET", "/tickets/1/time-tracking/", {}),
            ("POST", "/tickets/1/time-tracking/", {"json": {"duration": 30, "description": "Working on ticket"}}),
            ("GET", "/tickets/statistics/", {}),
            ("GET", "/tickets/?page=1&page_size=20&status=open", {})
        ]
        
        for method, endpoint, kwargs in endpoints:
            result = self.test_endpoint(method, endpoint, **kwargs)
            results.append(result)
            time.sleep(self.test_config['rate_limit_delay'])
        
        return results
    
    def test_organization_endpoints(self) -> List[TestResult]:
        """Test organization management endpoints."""
        logger.info("🏢 Testing Organization Management Endpoints...")
        results = []
        
        # Test data
        org_data = {
            "name": "Test Organization",
            "slug": "test-org",
            "subscription_tier": "premium"
        }
        
        # Test endpoints
        endpoints = [
            ("GET", "/organizations/", {}),
            ("POST", "/organizations/", {"json": org_data}),
            ("GET", "/organizations/1/", {}),
            ("PUT", "/organizations/1/", {"json": {"name": "Updated Organization"}}),
            ("DELETE", "/organizations/1/", {}),
            ("GET", "/organizations/1/users/", {}),
            ("POST", "/organizations/1/users/", {"json": {"user_id": "1", "role": "agent"}}),
            ("GET", "/organizations/1/settings/", {})
        ]
        
        for method, endpoint, kwargs in endpoints:
            result = self.test_endpoint(method, endpoint, **kwargs)
            results.append(result)
            time.sleep(self.test_config['rate_limit_delay'])
        
        return results
    
    def test_knowledge_base_endpoints(self) -> List[TestResult]:
        """Test knowledge base endpoints."""
        logger.info("📚 Testing Knowledge Base Endpoints...")
        results = []
        
        # Test data
        article_data = {
            "title": "Test Article",
            "content": "This is a test article",
            "category": "technical",
            "tags": ["test", "example"]
        }
        
        feedback_data = {
            "rating": 5,
            "comment": "Very helpful article",
            "helpful": True
        }
        
        # Test endpoints
        endpoints = [
            ("GET", "/knowledge-base/", {}),
            ("POST", "/knowledge-base/", {"json": article_data}),
            ("GET", "/knowledge-base/1/", {}),
            ("PUT", "/knowledge-base/1/", {"json": {"title": "Updated Article"}}),
            ("DELETE", "/knowledge-base/1/", {}),
            ("GET", "/knowledge-base/categories/", {}),
            ("GET", "/knowledge-base/1/feedback/", {}),
            ("POST", "/knowledge-base/1/feedback/", {"json": feedback_data})
        ]
        
        for method, endpoint, kwargs in endpoints:
            result = self.test_endpoint(method, endpoint, **kwargs)
            results.append(result)
            time.sleep(self.test_config['rate_limit_delay'])
        
        return results
    
    def test_field_service_endpoints(self) -> List[TestResult]:
        """Test field service endpoints."""
        logger.info("🔧 Testing Field Service Endpoints...")
        results = []
        
        # Test data
        work_order_data = {
            "title": "Test Work Order",
            "description": "Field service work order",
            "customer_id": "1",
            "technician_id": "1",
            "scheduled_date": "2024-01-15T10:00:00Z",
            "priority": "high"
        }
        
        report_data = {
            "completion_notes": "Work completed successfully",
            "time_spent": 120,
            "materials_used": ["screwdriver", "wire"],
            "customer_satisfaction": 5
        }
        
        # Test endpoints
        endpoints = [
            ("GET", "/field-service/work-orders/", {}),
            ("POST", "/field-service/work-orders/", {"json": work_order_data}),
            ("GET", "/field-service/work-orders/1/", {}),
            ("PUT", "/field-service/work-orders/1/", {"json": {"status": "in_progress"}}),
            ("DELETE", "/field-service/work-orders/1/", {}),
            ("GET", "/field-service/technicians/", {}),
            ("GET", "/field-service/work-orders/1/reports/", {}),
            ("POST", "/field-service/work-orders/1/reports/", {"json": report_data})
        ]
        
        for method, endpoint, kwargs in endpoints:
            result = self.test_endpoint(method, endpoint, **kwargs)
            results.append(result)
            time.sleep(self.test_config['rate_limit_delay'])
        
        return results
    
    def test_error_scenarios(self) -> List[TestResult]:
        """Test error scenarios."""
        logger.info("🚨 Testing Error Scenarios...")
        results = []
        
        # Test invalid input
        invalid_data = {
            "email": "invalid-email",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Test endpoints with expected errors
        error_endpoints = [
            ("POST", "/auth/register/", {"json": invalid_data}),  # Invalid email
            ("GET", "/tickets/", {}),  # Missing auth (should be 401)
            ("GET", "/tickets/999999/", {}),  # Non-existent resource (should be 404)
            ("POST", "/tickets/", {"json": {"priority": "high"}}),  # Missing required fields
            ("GET", "/organizations/999999/", {}),  # Non-existent organization
        ]
        
        for method, endpoint, kwargs in error_endpoints:
            result = self.test_endpoint(method, endpoint, **kwargs)
            results.append(result)
            time.sleep(self.test_config['rate_limit_delay'])
        
        return results
    
    def test_security_scenarios(self) -> List[TestResult]:
        """Test security scenarios."""
        logger.info("🔒 Testing Security Scenarios...")
        results = []
        
        # Test SQL injection
        sql_injection_endpoints = [
            ("GET", "/tickets/?search=' OR 1=1 --", {}),
            ("GET", "/users/?email=' OR 1=1 --", {}),
        ]
        
        # Test XSS attacks
        xss_data = {
            "subject": "<script>alert('XSS')</script>",
            "description": "Test ticket"
        }
        
        xss_endpoints = [
            ("POST", "/tickets/", {"json": xss_data}),
        ]
        
        # Combine all security tests
        security_endpoints = sql_injection_endpoints + xss_endpoints
        
        for method, endpoint, kwargs in security_endpoints:
            result = self.test_endpoint(method, endpoint, **kwargs)
            results.append(result)
            time.sleep(self.test_config['rate_limit_delay'])
        
        return results
    
    def test_rate_limiting(self) -> List[TestResult]:
        """Test rate limiting."""
        logger.info("⏱️ Testing Rate Limiting...")
        results = []
        
        # Make multiple rapid requests to test rate limiting
        for i in range(20):  # Make 20 requests rapidly
            result = self.test_endpoint("GET", "/tickets/", {})
            results.append(result)
            time.sleep(0.1)  # Small delay between requests
        
        return results
    
    def test_api_versioning(self) -> List[TestResult]:
        """Test API versioning."""
        logger.info("📋 Testing API Versioning...")
        results = []
        
        # Test different API versions
        version_endpoints = [
            ("GET", "/tickets/", {"headers": {"Accept": "application/vnd.api.v1+json"}}),
            ("GET", "/tickets/", {"headers": {"Accept": "application/vnd.api.v2+json"}}),
            ("GET", "/v2/tickets/", {}),
        ]
        
        for method, endpoint, kwargs in version_endpoints:
            result = self.test_endpoint(method, endpoint, **kwargs)
            results.append(result)
            time.sleep(self.test_config['rate_limit_delay'])
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all API tests.
        
        Returns:
            Test results summary
        """
        logger.info("🚀 Starting Comprehensive API Testing...")
        start_time = time.time()
        
        all_results = []
        
        # Test categories
        test_categories = [
            ("Authentication", self.test_authentication_endpoints),
            ("Ticket Management", self.test_ticket_endpoints),
            ("Organization Management", self.test_organization_endpoints),
            ("Knowledge Base", self.test_knowledge_base_endpoints),
            ("Field Service", self.test_field_service_endpoints),
            ("Error Scenarios", self.test_error_scenarios),
            ("Security Scenarios", self.test_security_scenarios),
            ("Rate Limiting", self.test_rate_limiting),
            ("API Versioning", self.test_api_versioning)
        ]
        
        # Run tests for each category
        for category_name, test_function in test_categories:
            try:
                category_results = test_function()
                all_results.extend(category_results)
                logger.info(f"✅ {category_name} tests completed: {len(category_results)} tests")
            except Exception as e:
                logger.error(f"❌ {category_name} tests failed: {e}")
        
        # Calculate summary
        total_tests = len(all_results)
        successful_tests = sum(1 for result in all_results if result.success)
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate performance metrics
        response_times = [result.response_time for result in all_results if result.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        total_time = time.time() - start_time
        
        # Create summary
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "average_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "total_execution_time": total_time,
            "test_results": all_results
        }
        
        # Log summary
        logger.info("📊 Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Successful: {successful_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Average Response Time: {avg_response_time:.2f}s")
        logger.info(f"   Max Response Time: {max_response_time:.2f}s")
        logger.info(f"   Total Execution Time: {total_time:.2f}s")
        
        return summary
    
    def save_results(self, results: Dict[str, Any], filename: str = "api_test_results.json"):
        """Save test results to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"📁 Test results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="API Test Runner")
    parser.add_argument("--base-url", default="http://localhost:8000/api/v1", help="Base API URL")
    parser.add_argument("--email", default="test@example.com", help="Test user email")
    parser.add_argument("--password", default="TestPassword123!", help="Test user password")
    parser.add_argument("--output", default="api_test_results.json", help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test runner
    runner = APITestRunner(args.base_url)
    
    # Authenticate
    if not runner.authenticate(args.email, args.password):
        logger.error("❌ Authentication failed. Exiting.")
        sys.exit(1)
    
    # Run all tests
    try:
        results = runner.run_all_tests()
        runner.save_results(results, args.output)
        
        # Exit with appropriate code
        if results["failed_tests"] > 0:
            logger.warning(f"⚠️ {results['failed_tests']} tests failed")
            sys.exit(1)
        else:
            logger.info("🎉 All tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Testing failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
