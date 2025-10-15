#!/usr/bin/env python3
"""
Health Check Testing Suite
Tests all health check endpoints and validates monitoring functionality
"""

import requests
import json
import time
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Any

class HealthCheckTestSuite:
    """Comprehensive health check testing suite"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.ai_service_url = "http://localhost:8001"
        self.realtime_service_url = "http://localhost:3000"
        self.test_results = []
        
    def run_all_health_checks(self):
        """Run all health check tests"""
        print("🏥 Starting Health Check Test Suite")
        print("=" * 50)
        
        try:
            # Test Django health endpoints
            self.test_django_health_endpoints()
            
            # Test microservice health endpoints
            self.test_microservice_health_endpoints()
            
            # Test Docker health checks
            self.test_docker_health_checks()
            
            # Test monitoring endpoints
            self.test_monitoring_endpoints()
            
            # Test database connectivity
            self.test_database_connectivity()
            
            # Test Redis connectivity
            self.test_redis_connectivity()
            
            # Generate health report
            self.generate_health_report()
            
        except Exception as e:
            print(f"❌ Health check test suite failed: {e}")
            return False
            
        return True
    
    def test_django_health_endpoints(self):
        """Test Django health check endpoints"""
        print("\n🔍 Testing Django Health Endpoints...")
        
        django_endpoints = [
            {
                "name": "Basic Health Check",
                "url": f"{self.base_url}/health/",
                "expected_status": 200,
                "expected_keys": ["status", "timestamp"]
            },
            {
                "name": "System Status",
                "url": f"{self.base_url}/status/",
                "expected_status": 200,
                "expected_keys": ["status", "version", "uptime"]
            },
            {
                "name": "Detailed System Status",
                "url": f"{self.base_url}/api/v1/system/status/",
                "expected_status": 200,
                "expected_keys": ["status", "services", "performance"]
            },
            {
                "name": "Feature Status",
                "url": f"{self.base_url}/api/v1/features/status/",
                "expected_status": 200,
                "expected_keys": ["features"]
            },
            {
                "name": "Feature Connections",
                "url": f"{self.base_url}/api/v1/features/connections/",
                "expected_status": 200,
                "expected_keys": ["connections"]
            }
        ]
        
        for endpoint in django_endpoints:
            try:
                print(f"  Testing: {endpoint['name']}")
                
                response = requests.get(endpoint['url'], timeout=10)
                
                if response.status_code == endpoint['expected_status']:
                    print(f"    ✅ {endpoint['name']} - Status: {response.status_code}")
                    
                    # Check response content
                    try:
                        data = response.json()
                        print(f"    📊 Response keys: {list(data.keys())}")
                        
                        # Check for expected keys
                        missing_keys = []
                        for key in endpoint.get('expected_keys', []):
                            if key not in data:
                                missing_keys.append(key)
                        
                        if missing_keys:
                            print(f"    ⚠️ Missing expected keys: {missing_keys}")
                        else:
                            print(f"    ✅ All expected keys present")
                            
                    except json.JSONDecodeError:
                        print(f"    📄 Response: {response.text[:200]}...")
                    
                    self.test_results.append({
                        "test": endpoint['name'],
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    print(f"    ❌ {endpoint['name']} - Expected: {endpoint['expected_status']}, Got: {response.status_code}")
                    self.test_results.append({
                        "test": endpoint['name'],
                        "status": "FAILED",
                        "expected": endpoint['expected_status'],
                        "actual": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"    ❌ {endpoint['name']} - Request failed: {e}")
                self.test_results.append({
                    "test": endpoint['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_microservice_health_endpoints(self):
        """Test microservice health check endpoints"""
        print("\n🔍 Testing Microservice Health Endpoints...")
        
        microservice_endpoints = [
            {
                "name": "AI Service Health",
                "url": f"{self.ai_service_url}/health/",
                "expected_status": 200,
                "expected_keys": ["status", "service"]
            },
            {
                "name": "Real-time Service Health",
                "url": f"{self.realtime_service_url}/health/",
                "expected_status": 200,
                "expected_keys": ["status"]
            }
        ]
        
        for endpoint in microservice_endpoints:
            try:
                print(f"  Testing: {endpoint['name']}")
                
                response = requests.get(endpoint['url'], timeout=10)
                
                if response.status_code == endpoint['expected_status']:
                    print(f"    ✅ {endpoint['name']} - Status: {response.status_code}")
                    
                    # Check response content
                    try:
                        data = response.json()
                        print(f"    📊 Response: {data}")
                        
                        # Check for expected keys
                        missing_keys = []
                        for key in endpoint.get('expected_keys', []):
                            if key not in data:
                                missing_keys.append(key)
                        
                        if missing_keys:
                            print(f"    ⚠️ Missing expected keys: {missing_keys}")
                        else:
                            print(f"    ✅ All expected keys present")
                            
                    except json.JSONDecodeError:
                        print(f"    📄 Response: {response.text[:200]}...")
                    
                    self.test_results.append({
                        "test": endpoint['name'],
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    print(f"    ❌ {endpoint['name']} - Expected: {endpoint['expected_status']}, Got: {response.status_code}")
                    self.test_results.append({
                        "test": endpoint['name'],
                        "status": "FAILED",
                        "expected": endpoint['expected_status'],
                        "actual": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"    ❌ {endpoint['name']} - Request failed: {e}")
                self.test_results.append({
                    "test": endpoint['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_docker_health_checks(self):
        """Test Docker health checks"""
        print("\n🔍 Testing Docker Health Checks...")
        
        try:
            # Check if docker-compose is running
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("    ✅ Docker Compose is running")
                
                # Parse docker-compose output
                lines = result.stdout.strip().split('\n')
                services = []
                
                for line in lines[2:]:  # Skip header lines
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            service_name = parts[0]
                            status = parts[3] if len(parts) > 3 else "unknown"
                            services.append({
                                "name": service_name,
                                "status": status
                            })
                
                print(f"    📊 Services found: {len(services)}")
                for service in services:
                    print(f"      - {service['name']}: {service['status']}")
                
                # Check for unhealthy services
                unhealthy_services = [s for s in services if "unhealthy" in s['status'].lower()]
                if unhealthy_services:
                    print(f"    ⚠️ Unhealthy services: {[s['name'] for s in unhealthy_services]}")
                else:
                    print(f"    ✅ All services appear healthy")
                
                self.test_results.append({
                    "test": "Docker Health Checks",
                    "status": "PASSED",
                    "services": services,
                    "timestamp": datetime.now().isoformat()
                })
                
            else:
                print(f"    ❌ Docker Compose not running: {result.stderr}")
                self.test_results.append({
                    "test": "Docker Health Checks",
                    "status": "FAILED",
                    "error": result.stderr,
                    "timestamp": datetime.now().isoformat()
                })
                
        except subprocess.TimeoutExpired:
            print("    ❌ Docker health check timed out")
            self.test_results.append({
                "test": "Docker Health Checks",
                "status": "FAILED",
                "error": "Timeout",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"    ❌ Docker health check failed: {e}")
            self.test_results.append({
                "test": "Docker Health Checks",
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def test_monitoring_endpoints(self):
        """Test monitoring endpoints"""
        print("\n🔍 Testing Monitoring Endpoints...")
        
        monitoring_endpoints = [
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
        
        for endpoint in monitoring_endpoints:
            try:
                print(f"  Testing: {endpoint['name']}")
                
                response = requests.get(endpoint['url'], timeout=10)
                
                if response.status_code == endpoint['expected_status']:
                    print(f"    ✅ {endpoint['name']} - Status: {response.status_code}")
                    
                    # Check response content
                    try:
                        data = response.json()
                        print(f"    📊 Response keys: {list(data.keys())}")
                    except json.JSONDecodeError:
                        print(f"    📄 Response: {response.text[:200]}...")
                    
                    self.test_results.append({
                        "test": endpoint['name'],
                        "status": "PASSED",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    print(f"    ⚠️ {endpoint['name']} - Status: {response.status_code}")
                    self.test_results.append({
                        "test": endpoint['name'],
                        "status": "WARNING",
                        "response_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except requests.exceptions.RequestException as e:
                print(f"    ❌ {endpoint['name']} - Request failed: {e}")
                self.test_results.append({
                    "test": endpoint['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_database_connectivity(self):
        """Test database connectivity"""
        print("\n🔍 Testing Database Connectivity...")
        
        try:
            # Test database health endpoint
            response = requests.get(f"{self.base_url}/api/v1/health/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'services' in data and 'database' in data['services']:
                    db_status = data['services']['database']
                    print(f"    ✅ Database connectivity: {db_status}")
                    self.test_results.append({
                        "test": "Database Connectivity",
                        "status": "PASSED",
                        "database_status": db_status,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    print(f"    ⚠️ Database status not found in response")
                    self.test_results.append({
                        "test": "Database Connectivity",
                        "status": "WARNING",
                        "message": "Database status not found",
                        "timestamp": datetime.now().isoformat()
                    })
            else:
                print(f"    ❌ Database health check failed: {response.status_code}")
                self.test_results.append({
                    "test": "Database Connectivity",
                    "status": "FAILED",
                    "response_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Database connectivity test failed: {e}")
            self.test_results.append({
                "test": "Database Connectivity",
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def test_redis_connectivity(self):
        """Test Redis connectivity"""
        print("\n🔍 Testing Redis Connectivity...")
        
        try:
            # Test Redis health endpoint
            response = requests.get(f"{self.base_url}/api/v1/health/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'services' in data and 'redis' in data['services']:
                    redis_status = data['services']['redis']
                    print(f"    ✅ Redis connectivity: {redis_status}")
                    self.test_results.append({
                        "test": "Redis Connectivity",
                        "status": "PASSED",
                        "redis_status": redis_status,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    print(f"    ⚠️ Redis status not found in response")
                    self.test_results.append({
                        "test": "Redis Connectivity",
                        "status": "WARNING",
                        "message": "Redis status not found",
                        "timestamp": datetime.now().isoformat()
                    })
            else:
                print(f"    ❌ Redis health check failed: {response.status_code}")
                self.test_results.append({
                    "test": "Redis Connectivity",
                    "status": "FAILED",
                    "response_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
                
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Redis connectivity test failed: {e}")
            self.test_results.append({
                "test": "Redis Connectivity",
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        print("\n📊 Health Check Test Report")
        print("=" * 40)
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAILED'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARNING'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Save detailed report
        report = {
            "test_suite": "Health Check Test Suite",
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
        report_file = f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {report_file}")
        
        if success_rate >= 90:
            print("🎉 Excellent! All health checks are passing.")
        elif success_rate >= 75:
            print("✅ Good! Most health checks are passing.")
        elif success_rate >= 50:
            print("⚠️ Fair! Some health checks need attention.")
        else:
            print("❌ Poor! Many health checks are failing.")
        
        return report

def main():
    """Main function to run health check tests"""
    print("🏥 Health Check Test Suite")
    print("=" * 30)
    
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
    
    # Run health check suite
    test_suite = HealthCheckTestSuite()
    success = test_suite.run_all_health_checks()
    
    if success:
        print("\n✅ Health check test suite completed successfully!")
    else:
        print("\n❌ Health check test suite encountered errors!")
    
    return success

if __name__ == "__main__":
    main()
