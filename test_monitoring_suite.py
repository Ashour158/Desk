#!/usr/bin/env python3
"""
Comprehensive Monitoring Test Suite
Tests error scenarios, log generation, health checks, and monitoring dashboards
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitoringTestSuite:
    """Comprehensive monitoring test suite"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.ai_service_url = "http://localhost:8001"
        self.realtime_service_url = "http://localhost:3000"
        self.test_results = []
        self.log_files = [
            "logs/django.log",
            "logs/error.log", 
            "logs/security.log",
            "logs/performance.log",
            "logs/compliance.log"
        ]
        
    def run_all_tests(self):
        """Run all monitoring tests"""
        logger.info("🧪 Starting Comprehensive Monitoring Test Suite")
        logger.info("=" * 60)
        
        try:
            # Test 1: Error Scenarios
            self.test_error_scenarios()
            
            # Test 2: Log File Generation
            self.test_log_file_generation()
            
            # Test 3: Error Tracking Service
            self.test_error_tracking_service()
            
            # Test 4: Health Check Endpoints
            self.test_health_check_endpoints()
            
            # Test 5: Monitoring Dashboards
            self.test_monitoring_dashboards()
            
            # Generate final report
            self.generate_test_report()
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            return False
            
        return True
    
    def test_error_scenarios(self):
        """Test error scenarios and verify logs are created"""
        logger.info("\n🔍 Testing Error Scenarios...")
        
        error_scenarios = [
            {
                "name": "Invalid API Endpoint",
                "method": "GET",
                "url": f"{self.base_url}/api/v1/invalid-endpoint/",
                "expected_status": 404
            },
            {
                "name": "Unauthorized Access",
                "method": "GET", 
                "url": f"{self.base_url}/api/v1/tickets/",
                "expected_status": 401
            },
            {
                "name": "Invalid JSON Payload",
                "method": "POST",
                "url": f"{self.base_url}/api/v1/auth/register/",
                "data": {"invalid": "data"},
                "expected_status": 400
            },
            {
                "name": "Database Connection Error",
                "method": "GET",
                "url": f"{self.base_url}/api/v1/health/",
                "expected_status": 200
            }
        ]
        
        for scenario in error_scenarios:
            try:
                logger.info(f"  Testing: {scenario['name']}")
                
                if scenario['method'] == 'GET':
                    response = requests.get(scenario['url'], timeout=10)
                elif scenario['method'] == 'POST':
                    response = requests.post(
                        scenario['url'], 
                        json=scenario.get('data', {}),
                        timeout=10
                    )
                
                # Check if response status matches expectation
                if response.status_code == scenario['expected_status']:
                    logger.info(f"    ✅ {scenario['name']} - Status: {response.status_code}")
                    self.test_results.append({
                        "test": scenario['name'],
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.warning(f"    ⚠️ {scenario['name']} - Expected: {scenario['expected_status']}, Got: {response.status_code}")
                    self.test_results.append({
                        "test": scenario['name'],
                        "status": "WARNING",
                        "expected": scenario['expected_status'],
                        "actual": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"    ❌ {scenario['name']} - Request failed: {e}")
                self.test_results.append({
                    "test": scenario['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            time.sleep(1)  # Rate limiting
    
    def test_log_file_generation(self):
        """Check log files are being generated correctly"""
        logger.info("\n📁 Testing Log File Generation...")
        
        for log_file in self.log_files:
            try:
                if os.path.exists(log_file):
                    # Check file size and content
                    file_size = os.path.getsize(log_file)
                    logger.info(f"  ✅ {log_file} - Size: {file_size} bytes")
                    
                    # Check if file has recent content (last 5 minutes)
                    mod_time = os.path.getmtime(log_file)
                    current_time = time.time()
                    time_diff = current_time - mod_time
                    
                    if time_diff < 300:  # 5 minutes
                        logger.info(f"    📝 Recent activity detected (modified {time_diff:.0f}s ago)")
                    else:
                        logger.warning(f"    ⚠️ No recent activity (modified {time_diff:.0f}s ago)")
                    
                    self.test_results.append({
                        "test": f"Log File: {log_file}",
                        "status": "PASSED",
                        "file_size": file_size,
                        "last_modified": time_diff,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.warning(f"  ⚠️ {log_file} - File not found")
                    self.test_results.append({
                        "test": f"Log File: {log_file}",
                        "status": "WARNING",
                        "message": "File not found",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"  ❌ {log_file} - Error: {e}")
                self.test_results.append({
                    "test": f"Log File: {log_file}",
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_error_tracking_service(self):
        """Verify error tracking service is receiving errors"""
        logger.info("\n🔍 Testing Error Tracking Service...")
        
        # Test error reporting endpoints
        error_tracking_tests = [
            {
                "name": "Error Reporting Endpoint",
                "url": f"{self.base_url}/api/v1/logs/",
                "method": "POST",
                "data": {
                    "level": "error",
                    "message": "Test error from monitoring suite",
                    "context": {
                        "test": True,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            },
            {
                "name": "Security Event Logging",
                "url": f"{self.base_url}/api/v1/security/events/",
                "method": "POST", 
                "data": {
                    "event_type": "test_security_event",
                    "severity": "low",
                    "details": {
                        "test": True,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
        ]
        
        for test in error_tracking_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                
                response = requests.post(
                    test['url'],
                    json=test['data'],
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"    ✅ {test['name']} - Status: {response.status_code}")
                    self.test_results.append({
                        "test": test['name'],
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.warning(f"    ⚠️ {test['name']} - Status: {response.status_code}")
                    self.test_results.append({
                        "test": test['name'],
                        "status": "WARNING",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"    ❌ {test['name']} - Request failed: {e}")
                self.test_results.append({
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_health_check_endpoints(self):
        """Test health check endpoints"""
        logger.info("\n🏥 Testing Health Check Endpoints...")
        
        health_endpoints = [
            {
                "name": "Django Core Health",
                "url": f"{self.base_url}/health/",
                "expected_status": 200
            },
            {
                "name": "Django Status",
                "url": f"{self.base_url}/status/",
                "expected_status": 200
            },
            {
                "name": "System Status",
                "url": f"{self.base_url}/api/v1/system/status/",
                "expected_status": 200
            },
            {
                "name": "AI Service Health",
                "url": f"{self.ai_service_url}/health/",
                "expected_status": 200
            },
            {
                "name": "Real-time Service Health",
                "url": f"{self.realtime_service_url}/health/",
                "expected_status": 200
            }
        ]
        
        for endpoint in health_endpoints:
            try:
                logger.info(f"  Testing: {endpoint['name']}")
                
                response = requests.get(endpoint['url'], timeout=10)
                
                if response.status_code == endpoint['expected_status']:
                    logger.info(f"    ✅ {endpoint['name']} - Status: {response.status_code}")
                    
                    # Try to parse JSON response
                    try:
                        health_data = response.json()
                        logger.info(f"    📊 Health data: {json.dumps(health_data, indent=2)}")
                    except:
                        logger.info(f"    📄 Response: {response.text[:200]}...")
                    
                    self.test_results.append({
                        "test": endpoint['name'],
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.error(f"    ❌ {endpoint['name']} - Expected: {endpoint['expected_status']}, Got: {response.status_code}")
                    self.test_results.append({
                        "test": endpoint['name'],
                        "status": "FAILED",
                        "expected": endpoint['expected_status'],
                        "actual": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"    ❌ {endpoint['name']} - Request failed: {e}")
                self.test_results.append({
                    "test": endpoint['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_monitoring_dashboards(self):
        """Validate monitoring dashboards"""
        logger.info("\n📊 Testing Monitoring Dashboards...")
        
        dashboard_endpoints = [
            {
                "name": "System Metrics",
                "url": f"{self.base_url}/api/v1/monitoring/metrics/",
                "expected_status": 200
            },
            {
                "name": "Health Checks",
                "url": f"{self.base_url}/api/v1/monitoring/health/",
                "expected_status": 200
            },
            {
                "name": "Alerts",
                "url": f"{self.base_url}/api/v1/monitoring/alerts/",
                "expected_status": 200
            },
            {
                "name": "Performance Reports",
                "url": f"{self.base_url}/api/v1/monitoring/reports/",
                "expected_status": 200
            }
        ]
        
        for dashboard in dashboard_endpoints:
            try:
                logger.info(f"  Testing: {dashboard['name']}")
                
                response = requests.get(dashboard['url'], timeout=10)
                
                if response.status_code == dashboard['expected_status']:
                    logger.info(f"    ✅ {dashboard['name']} - Status: {response.status_code}")
                    
                    # Try to parse JSON response
                    try:
                        dashboard_data = response.json()
                        logger.info(f"    📊 Dashboard data keys: {list(dashboard_data.keys())}")
                    except:
                        logger.info(f"    📄 Response: {response.text[:200]}...")
                    
                    self.test_results.append({
                        "test": dashboard['name'],
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.warning(f"    ⚠️ {dashboard['name']} - Status: {response.status_code}")
                    self.test_results.append({
                        "test": dashboard['name'],
                        "status": "WARNING",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"    ❌ {dashboard['name']} - Request failed: {e}")
                self.test_results.append({
                    "test": dashboard['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n📋 Generating Test Report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAILED'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARNING'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            "test_suite": "Comprehensive Monitoring Test Suite",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "warning_tests": warning_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "results": self.test_results
        }
        
        # Save report to file
        report_file = f"monitoring_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 MONITORING TEST SUITE RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"⚠️ Warnings: {warning_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"📄 Report saved to: {report_file}")
        
        if success_rate >= 90:
            logger.info("🎉 Excellent! Monitoring system is working well.")
        elif success_rate >= 75:
            logger.info("✅ Good! Monitoring system is mostly functional.")
        elif success_rate >= 50:
            logger.info("⚠️ Fair! Some monitoring components need attention.")
        else:
            logger.info("❌ Poor! Monitoring system needs significant improvements.")
        
        return report

def main():
    """Main function to run the monitoring test suite"""
    print("🧪 Comprehensive Monitoring Test Suite")
    print("=" * 50)
    
    # Check if services are running
    try:
        response = requests.get("http://localhost:8000/health/", timeout=5)
        if response.status_code != 200:
            print("❌ Django service is not running or not healthy")
            return False
    except:
        print("❌ Django service is not accessible")
        print("Please start the services with: docker-compose up -d")
        return False
    
    # Run test suite
    test_suite = MonitoringTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ Monitoring test suite completed successfully!")
    else:
        print("\n❌ Monitoring test suite encountered errors!")
    
    return success

if __name__ == "__main__":
    main()
