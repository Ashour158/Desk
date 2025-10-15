"""
Comprehensive Test Runner
Orchestrates all testing capabilities including security, load, integration, and accessibility testing
"""

import os
import sys
import json
import time
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import psutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class ComprehensiveTestRunner:
    """Comprehensive test runner for all testing capabilities"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.performance_metrics = {}
        self.security_score = 0
        self.coverage_score = 0
        
    def run_all_tests(self):
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Comprehensive Test Suite")
        logger.info("=" * 80)
        
        try:
            # Check if services are running
            if not self.check_services():
                logger.error("❌ Services are not running. Please start the application first.")
                return False
            
            # Run all test suites
            test_suites = [
                ("Unit Tests", self.run_unit_tests),
                ("Integration Tests", self.run_integration_tests),
                ("API Tests", self.run_api_tests),
                ("Security Tests", self.run_security_tests),
                ("Load Tests", self.run_load_tests),
                ("Penetration Tests", self.run_penetration_tests),
                ("Third-Party Integration Tests", self.run_third_party_tests),
                ("Accessibility Tests", self.run_accessibility_tests),
                ("Mobile Device Tests", self.run_mobile_tests),
                ("Performance Tests", self.run_performance_tests)
            ]
            
            for suite_name, test_function in test_suites:
                logger.info(f"\n📊 Running {suite_name}...")
                start_time = time.time()
                
                try:
                    result = test_function()
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    self.test_results.append({
                        "suite": suite_name,
                        "status": "PASSED" if result else "FAILED",
                        "duration": duration,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    if result:
                        logger.info(f"✅ {suite_name} completed successfully in {duration:.2f}s")
                    else:
                        logger.error(f"❌ {suite_name} failed")
                        
                except Exception as e:
                    logger.error(f"❌ {suite_name} failed with error: {e}")
                    self.test_results.append({
                        "suite": suite_name,
                        "status": "FAILED",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Generate comprehensive report
            self.generate_comprehensive_report()
            
            logger.info("\n✅ Comprehensive test suite completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Comprehensive test suite failed: {e}")
            return False
    
    def check_services(self):
        """Check if services are running"""
        try:
            response = requests.get(f"{self.base_url}/health/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_unit_tests(self):
        """Run unit tests"""
        try:
            # Run Django unit tests
            result = subprocess.run([
                "python", "manage.py", "test", "--verbosity=2"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Django unit tests passed")
                return True
            else:
                logger.error(f"❌ Django unit tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Django unit tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Django unit tests failed: {e}")
            return False
    
    def run_integration_tests(self):
        """Run integration tests"""
        try:
            # Run integration tests
            result = subprocess.run([
                "python", "manage.py", "test", "core.tests.test_integration", "--verbosity=2"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info("✅ Integration tests passed")
                return True
            else:
                logger.error(f"❌ Integration tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Integration tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Integration tests failed: {e}")
            return False
    
    def run_api_tests(self):
        """Run API tests"""
        try:
            # Run API tests
            result = subprocess.run([
                "python", "manage.py", "test", "core.tests.test_apis", "--verbosity=2"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info("✅ API tests passed")
                return True
            else:
                logger.error(f"❌ API tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ API tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ API tests failed: {e}")
            return False
    
    def run_security_tests(self):
        """Run security tests"""
        try:
            # Run automated security tests
            result = subprocess.run([
                "python", "core/tests/test_security_automated.py"
            ], capture_output=True, text=True, timeout=1200)
            
            if result.returncode == 0:
                logger.info("✅ Security tests passed")
                return True
            else:
                logger.error(f"❌ Security tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Security tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Security tests failed: {e}")
            return False
    
    def run_load_tests(self):
        """Run load tests"""
        try:
            # Run load tests with Locust
            result = subprocess.run([
                "python", "load_testing/run_load_tests.py"
            ], capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                logger.info("✅ Load tests passed")
                return True
            else:
                logger.error(f"❌ Load tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Load tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Load tests failed: {e}")
            return False
    
    def run_penetration_tests(self):
        """Run penetration tests"""
        try:
            # Run penetration tests
            result = subprocess.run([
                "python", "core/tests/test_penetration_testing.py"
            ], capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                logger.info("✅ Penetration tests passed")
                return True
            else:
                logger.error(f"❌ Penetration tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Penetration tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Penetration tests failed: {e}")
            return False
    
    def run_third_party_tests(self):
        """Run third-party integration tests"""
        try:
            # Run third-party integration tests
            result = subprocess.run([
                "python", "core/tests/test_third_party_integrations.py"
            ], capture_output=True, text=True, timeout=1200)
            
            if result.returncode == 0:
                logger.info("✅ Third-party integration tests passed")
                return True
            else:
                logger.error(f"❌ Third-party integration tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Third-party integration tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Third-party integration tests failed: {e}")
            return False
    
    def run_accessibility_tests(self):
        """Run accessibility tests"""
        try:
            # Run frontend accessibility tests
            result = subprocess.run([
                "npm", "test", "--", "--testPathPattern=accessibility-testing"
            ], capture_output=True, text=True, timeout=600, cwd="customer-portal")
            
            if result.returncode == 0:
                logger.info("✅ Accessibility tests passed")
                return True
            else:
                logger.error(f"❌ Accessibility tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Accessibility tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Accessibility tests failed: {e}")
            return False
    
    def run_mobile_tests(self):
        """Run mobile device tests"""
        try:
            # Run mobile device tests
            result = subprocess.run([
                "npm", "test", "--", "--testPathPattern=mobile-device-testing"
            ], capture_output=True, text=True, timeout=600, cwd="customer-portal")
            
            if result.returncode == 0:
                logger.info("✅ Mobile device tests passed")
                return True
            else:
                logger.error(f"❌ Mobile device tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Mobile device tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Mobile device tests failed: {e}")
            return False
    
    def run_performance_tests(self):
        """Run performance tests"""
        try:
            # Run performance tests
            result = subprocess.run([
                "python", "manage.py", "test", "core.tests.test_performance", "--verbosity=2"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info("✅ Performance tests passed")
                return True
            else:
                logger.error(f"❌ Performance tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Performance tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Performance tests failed: {e}")
            return False
    
    def run_coverage_analysis(self):
        """Run coverage analysis"""
        try:
            # Run coverage analysis
            result = subprocess.run([
                "coverage", "run", "--source=.", "manage.py", "test"
            ], capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                # Generate coverage report
                coverage_result = subprocess.run([
                    "coverage", "report", "--show-missing"
                ], capture_output=True, text=True)
                
                if coverage_result.returncode == 0:
                    # Parse coverage percentage
                    coverage_output = coverage_result.stdout
                    lines = coverage_output.split('\n')
                    for line in lines:
                        if 'TOTAL' in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                self.coverage_score = int(parts[3].replace('%', ''))
                                break
                    
                    logger.info(f"✅ Coverage analysis completed: {self.coverage_score}%")
                    return True
                else:
                    logger.error(f"❌ Coverage report generation failed: {coverage_result.stderr}")
                    return False
            else:
                logger.error(f"❌ Coverage analysis failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Coverage analysis timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Coverage analysis failed: {e}")
            return False
    
    def run_frontend_tests(self):
        """Run frontend tests"""
        try:
            # Run frontend tests
            result = subprocess.run([
                "npm", "test", "--", "--coverage", "--watchAll=false"
            ], capture_output=True, text=True, timeout=600, cwd="customer-portal")
            
            if result.returncode == 0:
                logger.info("✅ Frontend tests passed")
                return True
            else:
                logger.error(f"❌ Frontend tests failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Frontend tests timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Frontend tests failed: {e}")
            return False
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        logger.info("\n📊 Generating Comprehensive Test Report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAILED'])
        
        # Calculate total duration
        total_duration = sum(r.get('duration', 0) for r in self.test_results)
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            "test_suite": "Comprehensive Test Suite",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "total_duration": total_duration,
                "coverage_score": self.coverage_score,
                "security_score": self.security_score
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        # Save report to file
        report_file = f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("🚀 COMPREHENSIVE TEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"Total Test Suites: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📊 Success Rate: {success_rate:.2f}%")
        logger.info(f"⏱️ Total Duration: {total_duration:.2f}s")
        logger.info(f"📈 Coverage Score: {self.coverage_score}%")
        logger.info(f"🛡️ Security Score: {self.security_score}%")
        logger.info(f"📄 Report saved to: {report_file}")
        
        # Print detailed results
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            duration = result.get('duration', 0)
            logger.info(f"{status_icon} {result['suite']}: {result['status']} ({duration:.2f}s)")
        
        # Print recommendations
        if report['recommendations']:
            logger.info("\n📋 RECOMMENDATIONS:")
            for recommendation in report['recommendations']:
                logger.info(f"  • {recommendation}")
        
        if success_rate >= 90:
            logger.info("🎉 Excellent! All tests are passing.")
        elif success_rate >= 75:
            logger.info("✅ Good! Most tests are passing.")
        elif success_rate >= 50:
            logger.info("⚠️ Fair! Some tests need attention.")
        else:
            logger.info("❌ Poor! Many tests need attention.")
        
        return report
    
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze test results
        failed_tests = [r for r in self.test_results if r['status'] == 'FAILED']
        
        if failed_tests:
            recommendations.append(f"Fix {len(failed_tests)} failing test suites")
        
        if self.coverage_score < 80:
            recommendations.append(f"Improve test coverage from {self.coverage_score}% to 80%+")
        
        if self.security_score < 90:
            recommendations.append(f"Improve security score from {self.security_score}% to 90%+")
        
        # Performance recommendations
        slow_tests = [r for r in self.test_results if r.get('duration', 0) > 300]
        if slow_tests:
            recommendations.append(f"Optimize {len(slow_tests)} slow test suites")
        
        return recommendations


def main():
    """Main function to run comprehensive tests"""
    print("🚀 Comprehensive Test Suite")
    print("=" * 50)
    
    # Run comprehensive test suite
    test_runner = ComprehensiveTestRunner()
    success = test_runner.run_all_tests()
    
    if success:
        print("\n✅ Comprehensive test suite completed successfully!")
    else:
        print("\n❌ Comprehensive test suite encountered errors!")
    
    return success


if __name__ == "__main__":
    main()
