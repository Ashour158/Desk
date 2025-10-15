#!/usr/bin/env python3
"""
Comprehensive Testing Script for Updated Dependencies
Tests all updated Python and Node.js dependencies for compatibility and functionality.
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path

class DependencyTester:
    def __init__(self):
        self.results = {
            'python_tests': {},
            'nodejs_tests': {},
            'security_tests': {},
            'overall_status': 'PENDING'
        }
        self.start_time = time.time()
    
    def log(self, message, level='INFO'):
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def run_command(self, command, cwd=None, timeout=300):
        """Run a command and return success status and output"""
        try:
            self.log(f"Running: {command}")
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {command}", 'ERROR')
            return False, "", "Command timed out"
        except Exception as e:
            self.log(f"Command failed: {command} - {str(e)}", 'ERROR')
            return False, "", str(e)
    
    def test_python_dependencies(self):
        """Test Python dependencies and security"""
        self.log("Testing Python Dependencies...")
        
        # Test main requirements
        success, stdout, stderr = self.run_command("safety check -r requirements.txt")
        self.results['python_tests']['main_requirements'] = {
            'status': 'PASS' if success else 'FAIL',
            'output': stdout,
            'error': stderr
        }
        
        # Test AI service requirements
        success, stdout, stderr = self.run_command("safety check -r ai-service/requirements.txt")
        self.results['python_tests']['ai_service'] = {
            'status': 'PASS' if success else 'FAIL',
            'output': stdout,
            'error': stderr
        }
        
        # Test Django functionality
        success, stdout, stderr = self.run_command("python -c \"import django; print(f'Django {django.get_version()} OK')\"")
        self.results['python_tests']['django_import'] = {
            'status': 'PASS' if success else 'FAIL',
            'output': stdout,
            'error': stderr
        }
        
        # Test AI libraries
        success, stdout, stderr = self.run_command("python -c \"import transformers; print(f'Transformers {transformers.__version__} OK')\"")
        self.results['python_tests']['transformers'] = {
            'status': 'PASS' if success else 'FAIL',
            'output': stdout,
            'error': stderr
        }
        
        success, stdout, stderr = self.run_command("python -c \"import torch; print(f'PyTorch {torch.__version__} OK')\"")
        self.results['python_tests']['pytorch'] = {
            'status': 'PASS' if success else 'FAIL',
            'output': stdout,
            'error': stderr
        }
        
        # Test other critical packages
        packages_to_test = [
            'pillow', 'twilio', 'gunicorn', 'requests', 'sentry_sdk'
        ]
        
        for package in packages_to_test:
            success, stdout, stderr = self.run_command(f"python -c \"import {package}; print(f'{package.title()} OK')\"")
            self.results['python_tests'][package] = {
                'status': 'PASS' if success else 'FAIL',
                'output': stdout,
                'error': stderr
            }
    
    def test_nodejs_dependencies(self):
        """Test Node.js dependencies"""
        self.log("Testing Node.js Dependencies...")
        
        # Test customer portal
        success, stdout, stderr = self.run_command("npm audit --audit-level=moderate", cwd="customer-portal")
        self.results['nodejs_tests']['customer_portal_audit'] = {
            'status': 'PASS' if success else 'FAIL',
            'output': stdout,
            'error': stderr
        }
        
        # Test realtime service
        success, stdout, stderr = self.run_command("npm audit --audit-level=moderate", cwd="realtime-service")
        self.results['nodejs_tests']['realtime_service_audit'] = {
            'status': 'PASS' if success else 'FAIL',
            'output': stdout,
            'error': stderr
        }
        
        # Test outdated packages
        success, stdout, stderr = self.run_command("npm outdated", cwd="customer-portal")
        self.results['nodejs_tests']['customer_portal_outdated'] = {
            'status': 'INFO',
            'output': stdout,
            'error': stderr
        }
        
        success, stdout, stderr = self.run_command("npm outdated", cwd="realtime-service")
        self.results['nodejs_tests']['realtime_service_outdated'] = {
            'status': 'INFO',
            'output': stdout,
            'error': stderr
        }
    
    def test_security_scanning(self):
        """Run comprehensive security scans"""
        self.log("Running Security Scans...")
        
        # Python security scans
        success, stdout, stderr = self.run_command("safety check -r requirements.txt")
        self.results['security_tests']['python_main'] = {
            'status': 'PASS' if success else 'FAIL',
            'vulnerabilities': 0 if success else len([line for line in stderr.split('\n') if 'vulnerability' in line.lower()]),
            'output': stdout,
            'error': stderr
        }
        
        success, stdout, stderr = self.run_command("safety check -r ai-service/requirements.txt")
        self.results['security_tests']['python_ai'] = {
            'status': 'PASS' if success else 'FAIL',
            'vulnerabilities': 0 if success else len([line for line in stderr.split('\n') if 'vulnerability' in line.lower()]),
            'output': stdout,
            'error': stderr
        }
        
        # Node.js security scans
        success, stdout, stderr = self.run_command("npm audit --audit-level=moderate", cwd="customer-portal")
        self.results['security_tests']['nodejs_customer_portal'] = {
            'status': 'PASS' if success else 'FAIL',
            'vulnerabilities': 0 if success else len([line for line in stderr.split('\n') if 'vulnerability' in line.lower()]),
            'output': stdout,
            'error': stderr
        }
        
        success, stdout, stderr = self.run_command("npm audit --audit-level=moderate", cwd="realtime-service")
        self.results['security_tests']['nodejs_realtime'] = {
            'status': 'PASS' if success else 'FAIL',
            'vulnerabilities': 0 if success else len([line for line in stderr.split('\n') if 'vulnerability' in line.lower()]),
            'output': stdout,
            'error': stderr
        }
    
    def generate_report(self):
        """Generate comprehensive test report"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Calculate overall status
        all_tests = []
        for category in self.results.values():
            if isinstance(category, dict):
                for test_name, test_result in category.items():
                    if isinstance(test_result, dict) and 'status' in test_result:
                        all_tests.append(test_result['status'])
        
        pass_count = all_tests.count('PASS')
        fail_count = all_tests.count('FAIL')
        total_tests = len(all_tests)
        
        if fail_count == 0:
            self.results['overall_status'] = 'PASS'
        elif pass_count > fail_count:
            self.results['overall_status'] = 'PARTIAL'
        else:
            self.results['overall_status'] = 'FAIL'
        
        # Generate report
        report = {
            'summary': {
                'overall_status': self.results['overall_status'],
                'total_tests': total_tests,
                'passed': pass_count,
                'failed': fail_count,
                'duration_seconds': round(duration, 2)
            },
            'results': self.results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save report
        with open('dependency_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self.log("=" * 60)
        self.log("DEPENDENCY TEST SUMMARY")
        self.log("=" * 60)
        self.log(f"Overall Status: {self.results['overall_status']}")
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {pass_count}")
        self.log(f"Failed: {fail_count}")
        self.log(f"Duration: {duration:.2f} seconds")
        self.log("=" * 60)
        
        # Print detailed results
        for category, tests in self.results.items():
            if isinstance(tests, dict) and category != 'overall_status':
                self.log(f"\n{category.upper().replace('_', ' ')}:")
                for test_name, test_result in tests.items():
                    if isinstance(test_result, dict) and 'status' in test_result:
                        status_icon = "[PASS]" if test_result['status'] == 'PASS' else "[FAIL]" if test_result['status'] == 'FAIL' else "[INFO]"
                        self.log(f"  {status_icon} {test_name}: {test_result['status']}")
        
        return report
    
    def run_all_tests(self):
        """Run all dependency tests"""
        self.log("Starting Comprehensive Dependency Testing...")
        self.log("=" * 60)
        
        try:
            self.test_python_dependencies()
            self.test_nodejs_dependencies()
            self.test_security_scanning()
            
            report = self.generate_report()
            return report
            
        except Exception as e:
            self.log(f"Testing failed with error: {str(e)}", 'ERROR')
            self.results['overall_status'] = 'ERROR'
            return self.results

def main():
    """Main function to run dependency tests"""
    print("Comprehensive Dependency Testing Script")
    print("=" * 60)
    
    tester = DependencyTester()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    if report['summary']['overall_status'] == 'PASS':
        sys.exit(0)
    elif report['summary']['overall_status'] == 'PARTIAL':
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
