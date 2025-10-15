"""
Load Testing Runner
Execute comprehensive load tests with Locust
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


class LoadTestRunner:
    """Comprehensive load testing runner"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.locust_host = "localhost:8000"
        self.test_results = []
        self.performance_metrics = {}
        
    def run_all_load_tests(self):
        """Run all load tests"""
        logger.info("🚀 Starting Load Test Suite")
        logger.info("=" * 60)
        
        try:
            # Check if services are running
            if not self.check_services():
                logger.error("❌ Services are not running. Please start the application first.")
                return False
            
            # Run different load test scenarios
            test_scenarios = [
                ("light_load", "Light Load Test"),
                ("medium_load", "Medium Load Test"),
                ("heavy_load", "Heavy Load Test"),
                ("stress_test", "Stress Test"),
                ("spike_test", "Spike Test")
            ]
            
            for scenario, description in test_scenarios:
                logger.info(f"\n📊 Running {description}...")
                result = self.run_load_test_scenario(scenario)
                self.test_results.append({
                    "scenario": scenario,
                    "description": description,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Generate comprehensive report
            self.generate_load_test_report()
            
            logger.info("\n✅ Load test suite completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Load test suite failed: {e}")
            return False
    
    def check_services(self):
        """Check if services are running"""
        try:
            response = requests.get(f"{self.base_url}/health/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_load_test_scenario(self, scenario: str):
        """Run a specific load test scenario"""
        try:
            # Get scenario configuration
            scenario_config = self.get_scenario_config(scenario)
            
            # Start system monitoring
            self.start_system_monitoring()
            
            # Run Locust test
            result = self.run_locust_test(scenario_config)
            
            # Stop system monitoring
            self.stop_system_monitoring()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Load test scenario {scenario} failed: {e}")
            return None
    
    def get_scenario_config(self, scenario: str):
        """Get configuration for a test scenario"""
        scenarios = {
            "light_load": {
                "users": 10,
                "spawn_rate": 2,
                "duration": "5m",
                "description": "Light load test with 10 users"
            },
            "medium_load": {
                "users": 50,
                "spawn_rate": 5,
                "duration": "10m",
                "description": "Medium load test with 50 users"
            },
            "heavy_load": {
                "users": 100,
                "spawn_rate": 10,
                "duration": "15m",
                "description": "Heavy load test with 100 users"
            },
            "stress_test": {
                "users": 200,
                "spawn_rate": 20,
                "duration": "10m",
                "description": "Stress test with 200 users"
            },
            "spike_test": {
                "users": 500,
                "spawn_rate": 50,
                "duration": "5m",
                "description": "Spike test with 500 users"
            }
        }
        
        return scenarios.get(scenario, scenarios["light_load"])
    
    def run_locust_test(self, config: Dict[str, Any]):
        """Run Locust test with given configuration"""
        try:
            # Prepare Locust command
            cmd = [
                "locust",
                "-f", "load_testing/locustfile.py",
                "--host", f"http://{self.locust_host}",
                "--users", str(config["users"]),
                "--spawn-rate", str(config["spawn_rate"]),
                "--run-time", config["duration"],
                "--headless",
                "--csv", f"load_testing/results/{config['users']}_users",
                "--html", f"load_testing/results/{config['users']}_users_report.html"
            ]
            
            # Create results directory
            os.makedirs("load_testing/results", exist_ok=True)
            
            # Run Locust
            logger.info(f"Running Locust with {config['users']} users for {config['duration']}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
            
            if result.returncode == 0:
                logger.info("✅ Locust test completed successfully")
                return self.parse_locust_results(config)
            else:
                logger.error(f"❌ Locust test failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Locust test timed out")
            return None
        except Exception as e:
            logger.error(f"❌ Locust test failed: {e}")
            return None
    
    def parse_locust_results(self, config: Dict[str, Any]):
        """Parse Locust results"""
        try:
            # Read CSV results
            csv_file = f"load_testing/results/{config['users']}_users_stats.csv"
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                
                # Parse results
                results = {
                    "scenario": config["description"],
                    "users": config["users"],
                    "duration": config["duration"],
                    "metrics": {}
                }
                
                # Parse CSV data
                for line in lines[1:]:  # Skip header
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        endpoint = parts[0]
                        requests = int(parts[1])
                        failures = int(parts[2])
                        avg_response_time = float(parts[3])
                        
                        results["metrics"][endpoint] = {
                            "requests": requests,
                            "failures": failures,
                            "avg_response_time": avg_response_time,
                            "success_rate": (requests - failures) / requests * 100 if requests > 0 else 0
                        }
                
                return results
            
        except Exception as e:
            logger.error(f"❌ Failed to parse Locust results: {e}")
            return None
    
    def start_system_monitoring(self):
        """Start system monitoring"""
        self.monitoring_data = {
            "cpu_usage": [],
            "memory_usage": [],
            "disk_usage": [],
            "network_usage": [],
            "timestamps": []
        }
        
        # Start monitoring in background
        self.monitoring = True
        self.monitor_system()
    
    def stop_system_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
    
    def monitor_system(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                
                # Network usage
                network = psutil.net_io_counters()
                network_bytes = network.bytes_sent + network.bytes_recv
                
                # Record metrics
                self.monitoring_data["cpu_usage"].append(cpu_percent)
                self.monitoring_data["memory_usage"].append(memory_percent)
                self.monitoring_data["disk_usage"].append(disk_percent)
                self.monitoring_data["network_usage"].append(network_bytes)
                self.monitoring_data["timestamps"].append(datetime.now().isoformat())
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ System monitoring error: {e}")
                break
    
    def generate_load_test_report(self):
        """Generate comprehensive load test report"""
        logger.info("\n📊 Generating Load Test Report...")
        
        # Calculate overall statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["result"] is not None])
        
        # Generate report
        report = {
            "test_suite": "Load Testing Suite",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests
            },
            "test_results": self.test_results,
            "system_monitoring": self.monitoring_data,
            "recommendations": self.generate_recommendations()
        }
        
        # Save report to file
        report_file = f"load_testing/results/load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("🚀 LOAD TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Successful: {successful_tests}")
        logger.info(f"❌ Failed: {total_tests - successful_tests}")
        logger.info(f"📄 Report saved to: {report_file}")
        
        # Print detailed results
        for result in self.test_results:
            if result["result"]:
                logger.info(f"\n📊 {result['description']}:")
                logger.info(f"  Users: {result['result']['users']}")
                logger.info(f"  Duration: {result['result']['duration']}")
                
                # Print endpoint metrics
                for endpoint, metrics in result["result"]["metrics"].items():
                    logger.info(f"  {endpoint}:")
                    logger.info(f"    Requests: {metrics['requests']}")
                    logger.info(f"    Failures: {metrics['failures']}")
                    logger.info(f"    Avg Response Time: {metrics['avg_response_time']:.2f}ms")
                    logger.info(f"    Success Rate: {metrics['success_rate']:.2f}%")
        
        return report
    
    def generate_recommendations(self):
        """Generate performance recommendations"""
        recommendations = []
        
        # Analyze results and generate recommendations
        for result in self.test_results:
            if result["result"]:
                for endpoint, metrics in result["result"]["metrics"].items():
                    # Check response times
                    if metrics["avg_response_time"] > 1000:  # > 1 second
                        recommendations.append({
                            "type": "performance",
                            "endpoint": endpoint,
                            "issue": "High response time",
                            "recommendation": "Optimize database queries and add caching"
                        })
                    
                    # Check success rates
                    if metrics["success_rate"] < 95:  # < 95% success rate
                        recommendations.append({
                            "type": "reliability",
                            "endpoint": endpoint,
                            "issue": "Low success rate",
                            "recommendation": "Check error handling and increase server capacity"
                        })
        
        return recommendations


def main():
    """Main function to run load tests"""
    print("🚀 Load Testing Suite")
    print("=" * 40)
    
    # Run load test suite
    test_runner = LoadTestRunner()
    success = test_runner.run_all_load_tests()
    
    if success:
        print("\n✅ Load test suite completed successfully!")
    else:
        print("\n❌ Load test suite encountered errors!")
    
    return success


if __name__ == "__main__":
    main()
