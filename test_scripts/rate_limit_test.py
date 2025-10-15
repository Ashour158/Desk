#!/usr/bin/env python3
"""
Rate Limiting Test Script - Comprehensive rate limiting validation.
"""

import requests
import time
import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import threading
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    """Rate limit test result."""
    request_number: int
    status_code: int
    response_time: float
    rate_limit_headers: Dict[str, str]
    success: bool
    timestamp: datetime


class RateLimitTester:
    """
    Comprehensive rate limiting tester.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.results = []
        
        # Rate limit configurations to test
        self.rate_limit_configs = {
            'general_api': {'requests': 100, 'window': 60},  # 100 requests per minute
            'authentication': {'requests': 10, 'window': 60},  # 10 requests per minute
            'bulk_operations': {'requests': 20, 'window': 60},  # 20 requests per minute
            'file_upload': {'requests': 50, 'window': 60},  # 50 requests per minute
        }
    
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
    
    def make_request(self, endpoint: str, method: str = "GET", **kwargs) -> RateLimitResult:
        """Make a single request and capture rate limit information."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=30,
                **kwargs
            )
            
            response_time = time.time() - start_time
            
            # Extract rate limit headers
            rate_limit_headers = {
                'X-RateLimit-Limit': response.headers.get('X-RateLimit-Limit'),
                'X-RateLimit-Remaining': response.headers.get('X-RateLimit-Remaining'),
                'X-RateLimit-Reset': response.headers.get('X-RateLimit-Reset'),
                'X-RateLimit-Burst-Remaining': response.headers.get('X-RateLimit-Burst-Remaining'),
            }
            
            result = RateLimitResult(
                request_number=len(self.results) + 1,
                status_code=response.status_code,
                response_time=response_time,
                rate_limit_headers=rate_limit_headers,
                success=200 <= response.status_code < 400,
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Request error: {e}")
            
            return RateLimitResult(
                request_number=len(self.results) + 1,
                status_code=0,
                response_time=response_time,
                rate_limit_headers={},
                success=False,
                timestamp=datetime.now()
            )
    
    def test_general_api_rate_limiting(self) -> List[RateLimitResult]:
        """Test general API rate limiting."""
        logger.info("🔍 Testing General API Rate Limiting...")
        results = []
        
        # Make requests to test rate limiting
        for i in range(150):  # Make 150 requests to exceed 100/minute limit
            result = self.make_request("/tickets/")
            results.append(result)
            
            # Log every 10th request
            if (i + 1) % 10 == 0:
                logger.info(f"Request {i + 1}: Status {result.status_code}, "
                          f"Remaining: {result.rate_limit_headers.get('X-RateLimit-Remaining', 'N/A')}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        return results
    
    def test_authentication_rate_limiting(self) -> List[RateLimitResult]:
        """Test authentication rate limiting."""
        logger.info("🔐 Testing Authentication Rate Limiting...")
        results = []
        
        # Test login rate limiting
        for i in range(15):  # Make 15 login attempts to exceed 10/minute limit
            result = self.make_request(
                "/auth/login/",
                method="POST",
                json={"email": "test@example.com", "password": "wrong_password"}
            )
            results.append(result)
            
            if (i + 1) % 5 == 0:
                logger.info(f"Login attempt {i + 1}: Status {result.status_code}")
            
            time.sleep(0.1)
        
        return results
    
    def test_bulk_operation_rate_limiting(self) -> List[RateLimitResult]:
        """Test bulk operation rate limiting."""
        logger.info("📦 Testing Bulk Operation Rate Limiting...")
        results = []
        
        # Test bulk create operations
        bulk_data = {
            "tickets": [
                {"subject": f"Bulk Ticket {i}", "description": f"Description {i}"}
                for i in range(5)  # 5 items per request
            ]
        }
        
        for i in range(10):  # Make 10 bulk requests
            result = self.make_request(
                "/tickets/bulk_create/",
                method="POST",
                json=bulk_data
            )
            results.append(result)
            
            if (i + 1) % 3 == 0:
                logger.info(f"Bulk request {i + 1}: Status {result.status_code}")
            
            time.sleep(0.1)
        
        return results
    
    def test_file_upload_rate_limiting(self) -> List[RateLimitResult]:
        """Test file upload rate limiting."""
        logger.info("📁 Testing File Upload Rate Limiting...")
        results = []
        
        # Create a small test file
        test_file_content = b"This is a test file for rate limiting"
        
        for i in range(60):  # Make 60 file upload requests
            files = {'file': ('test.txt', test_file_content, 'text/plain')}
            data = {'description': f'Test file {i}'}
            
            result = self.make_request(
                "/tickets/1/attachments/",
                method="POST",
                files=files,
                data=data
            )
            results.append(result)
            
            if (i + 1) % 10 == 0:
                logger.info(f"File upload {i + 1}: Status {result.status_code}")
            
            time.sleep(0.1)
        
        return results
    
    def test_concurrent_rate_limiting(self) -> List[RateLimitResult]:
        """Test concurrent request rate limiting."""
        logger.info("⚡ Testing Concurrent Rate Limiting...")
        results = []
        
        def make_concurrent_request(request_id: int) -> RateLimitResult:
            """Make a concurrent request."""
            return self.make_request(f"/tickets/?request_id={request_id}")
        
        # Make 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(make_concurrent_request, i)
                for i in range(50)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Concurrent request error: {e}")
        
        return results
    
    def test_user_specific_rate_limiting(self) -> List[RateLimitResult]:
        """Test user-specific rate limiting."""
        logger.info("👤 Testing User-Specific Rate Limiting...")
        results = []
        
        # Test with different user contexts
        test_users = [
            {"email": "user1@example.com", "password": "Password123!"},
            {"email": "user2@example.com", "password": "Password123!"},
            {"email": "user3@example.com", "password": "Password123!"},
        ]
        
        for user in test_users:
            # Authenticate as different user
            user_session = requests.Session()
            try:
                auth_response = user_session.post(
                    f"{self.base_url}/auth/login/",
                    json=user,
                    timeout=30
                )
                
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    user_token = auth_data.get('data', {}).get('access_token')
                    user_session.headers.update({
                        'Authorization': f'Bearer {user_token}'
                    })
                    
                    # Make requests as this user
                    for i in range(20):
                        response = user_session.get(f"{self.base_url}/tickets/", timeout=30)
                        result = RateLimitResult(
                            request_number=len(results) + 1,
                            status_code=response.status_code,
                            response_time=0,
                            rate_limit_headers={
                                'X-RateLimit-Limit': response.headers.get('X-RateLimit-Limit'),
                                'X-RateLimit-Remaining': response.headers.get('X-RateLimit-Remaining'),
                            },
                            success=200 <= response.status_code < 400,
                            timestamp=datetime.now()
                        )
                        results.append(result)
                        
                        time.sleep(0.1)
                        
            except Exception as e:
                logger.error(f"User-specific test error: {e}")
        
        return results
    
    def analyze_rate_limit_results(self, results: List[RateLimitResult]) -> Dict[str, Any]:
        """Analyze rate limit test results."""
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.success)
        rate_limited_requests = sum(1 for r in results if r.status_code == 429)
        
        # Analyze rate limit headers
        rate_limit_headers = [r.rate_limit_headers for r in results if r.rate_limit_headers]
        
        # Calculate statistics
        response_times = [r.response_time for r in results if r.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Find rate limit violations
        rate_limit_violations = []
        for result in results:
            if result.status_code == 429:
                rate_limit_violations.append({
                    'request_number': result.request_number,
                    'timestamp': result.timestamp,
                    'headers': result.rate_limit_headers
                })
        
        analysis = {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'rate_limited_requests': rate_limited_requests,
            'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            'rate_limit_rate': (rate_limited_requests / total_requests * 100) if total_requests > 0 else 0,
            'average_response_time': avg_response_time,
            'rate_limit_violations': rate_limit_violations,
            'rate_limit_headers_analysis': self._analyze_rate_limit_headers(rate_limit_headers)
        }
        
        return analysis
    
    def _analyze_rate_limit_headers(self, headers_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze rate limit headers."""
        if not headers_list:
            return {}
        
        # Extract rate limit values
        limits = [h.get('X-RateLimit-Limit') for h in headers_list if h.get('X-RateLimit-Limit')]
        remaining = [h.get('X-RateLimit-Remaining') for h in headers_list if h.get('X-RateLimit-Remaining')]
        
        return {
            'rate_limits_detected': len(set(limits)),
            'average_limit': sum(int(l) for l in limits if l.isdigit()) / len(limits) if limits else 0,
            'minimum_remaining': min(int(r) for r in remaining if r.isdigit()) if remaining else 0,
            'headers_present': len([h for h in headers_list if any(h.values())])
        }
    
    def run_all_rate_limit_tests(self) -> Dict[str, Any]:
        """Run all rate limiting tests."""
        logger.info("🚀 Starting Comprehensive Rate Limiting Tests...")
        start_time = time.time()
        
        all_results = []
        
        # Test categories
        test_categories = [
            ("General API Rate Limiting", self.test_general_api_rate_limiting),
            ("Authentication Rate Limiting", self.test_authentication_rate_limiting),
            ("Bulk Operation Rate Limiting", self.test_bulk_operation_rate_limiting),
            ("File Upload Rate Limiting", self.test_file_upload_rate_limiting),
            ("Concurrent Rate Limiting", self.test_concurrent_rate_limiting),
            ("User-Specific Rate Limiting", self.test_user_specific_rate_limiting),
        ]
        
        # Run tests for each category
        for category_name, test_function in test_categories:
            try:
                logger.info(f"Running {category_name}...")
                category_results = test_function()
                all_results.extend(category_results)
                logger.info(f"✅ {category_name} completed: {len(category_results)} requests")
            except Exception as e:
                logger.error(f"❌ {category_name} failed: {e}")
        
        # Analyze results
        analysis = self.analyze_rate_limit_results(all_results)
        
        total_time = time.time() - start_time
        
        # Create summary
        summary = {
            "test_execution_time": total_time,
            "total_requests": analysis['total_requests'],
            "successful_requests": analysis['successful_requests'],
            "rate_limited_requests": analysis['rate_limited_requests'],
            "success_rate": analysis['success_rate'],
            "rate_limit_rate": analysis['rate_limit_rate'],
            "average_response_time": analysis['average_response_time'],
            "rate_limit_violations": analysis['rate_limit_violations'],
            "rate_limit_headers_analysis": analysis['rate_limit_headers_analysis'],
            "detailed_results": [
                {
                    "request_number": r.request_number,
                    "status_code": r.status_code,
                    "response_time": r.response_time,
                    "rate_limit_headers": r.rate_limit_headers,
                    "success": r.success,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in all_results
            ]
        }
        
        # Log summary
        logger.info("📊 Rate Limiting Test Summary:")
        logger.info(f"   Total Requests: {analysis['total_requests']}")
        logger.info(f"   Successful Requests: {analysis['successful_requests']}")
        logger.info(f"   Rate Limited Requests: {analysis['rate_limited_requests']}")
        logger.info(f"   Success Rate: {analysis['success_rate']:.1f}%")
        logger.info(f"   Rate Limit Rate: {analysis['rate_limit_rate']:.1f}%")
        logger.info(f"   Average Response Time: {analysis['average_response_time']:.2f}s")
        logger.info(f"   Rate Limit Violations: {len(analysis['rate_limit_violations'])}")
        
        return summary
    
    def save_results(self, results: Dict[str, Any], filename: str = "rate_limit_test_results.json"):
        """Save test results to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"📁 Rate limiting test results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rate Limiting Test Script")
    parser.add_argument("--base-url", default="http://localhost:8000/api/v1", help="Base API URL")
    parser.add_argument("--email", default="test@example.com", help="Test user email")
    parser.add_argument("--password", default="TestPassword123!", help="Test user password")
    parser.add_argument("--output", default="rate_limit_test_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    # Create rate limit tester
    tester = RateLimitTester(args.base_url)
    
    # Authenticate
    if not tester.authenticate(args.email, args.password):
        logger.error("❌ Authentication failed. Exiting.")
        return
    
    # Run all rate limiting tests
    try:
        results = tester.run_all_rate_limit_tests()
        tester.save_results(results, args.output)
        
        # Check if rate limiting is working
        if results['rate_limited_requests'] > 0:
            logger.info("✅ Rate limiting is working correctly!")
        else:
            logger.warning("⚠️ No rate limiting detected - may need configuration")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Rate limiting tests interrupted by user")
    except Exception as e:
        logger.error(f"💥 Rate limiting tests failed with error: {e}")


if __name__ == "__main__":
    main()
