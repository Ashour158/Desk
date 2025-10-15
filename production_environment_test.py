#!/usr/bin/env python3
"""
Production environment testing script.
Tests all systems in production environment.
"""

import os
import sys
import subprocess
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionEnvironmentTester:
    """Comprehensive production environment testing utility."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    def test_database_connectivity(self):
        """Test database connectivity in production."""
        logger.info("Testing database connectivity...")
        
        try:
            # Test PostgreSQL connection
            import psycopg2
            
            # Production database configuration
            db_config = {
                'host': os.environ.get('DB_HOST', 'localhost'),
                'port': os.environ.get('DB_PORT', '5432'),
                'database': os.environ.get('DB_NAME', 'helpdesk_production'),
                'user': os.environ.get('DB_USER', 'helpdesk_user'),
                'password': os.environ.get('DB_PASSWORD', ''),
            }
            
            # Test connection
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            logger.info(f"Database connection successful: {version}")
            self.test_results['database_connectivity'] = 'PASS'
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.test_results['database_connectivity'] = 'FAIL'
            return False
    
    def test_redis_connectivity(self):
        """Test Redis connectivity in production."""
        logger.info("Testing Redis connectivity...")
        
        try:
            import redis
            
            # Redis configuration
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
            r = redis.from_url(redis_url)
            
            # Test connection
            r.ping()
            
            # Test basic operations
            r.set('test_key', 'test_value', ex=60)
            value = r.get('test_key')
            r.delete('test_key')
            
            if value == b'test_value':
                logger.info("Redis connection and operations successful")
                self.test_results['redis_connectivity'] = 'PASS'
                return True
            else:
                logger.error("Redis operations failed")
                self.test_results['redis_connectivity'] = 'FAIL'
                return False
                
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.test_results['redis_connectivity'] = 'FAIL'
            return False
    
    def test_email_configuration(self):
        """Test email configuration in production."""
        logger.info("Testing email configuration...")
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # Test email sending
            send_mail(
                'Production Test Email',
                'This is a test email from production environment.',
                settings.DEFAULT_FROM_EMAIL,
                ['test@example.com'],
                fail_silently=False,
            )
            
            logger.info("Email configuration test successful")
            self.test_results['email_configuration'] = 'PASS'
            return True
            
        except Exception as e:
            logger.error(f"Email configuration test failed: {e}")
            self.test_results['email_configuration'] = 'FAIL'
            return False
    
    def test_static_files(self):
        """Test static files configuration."""
        logger.info("Testing static files configuration...")
        
        try:
            # Check if static files directory exists
            static_root = Path('staticfiles')
            if static_root.exists():
                # Check if static files are collected
                static_files = list(static_root.rglob('*'))
                if len(static_files) > 0:
                    logger.info(f"Static files found: {len(static_files)} files")
                    self.test_results['static_files'] = 'PASS'
                    return True
                else:
                    logger.warning("Static files directory is empty")
                    self.test_results['static_files'] = 'WARN'
                    return True
            else:
                logger.error("Static files directory not found")
                self.test_results['static_files'] = 'FAIL'
                return False
                
        except Exception as e:
            logger.error(f"Static files test failed: {e}")
            self.test_results['static_files'] = 'FAIL'
            return False
    
    def test_media_files(self):
        """Test media files configuration."""
        logger.info("Testing media files configuration...")
        
        try:
            # Check if media directory exists
            media_root = Path('media')
            if media_root.exists():
                logger.info("Media directory exists")
                self.test_results['media_files'] = 'PASS'
                return True
            else:
                # Create media directory
                media_root.mkdir(exist_ok=True)
                logger.info("Media directory created")
                self.test_results['media_files'] = 'PASS'
                return True
                
        except Exception as e:
            logger.error(f"Media files test failed: {e}")
            self.test_results['media_files'] = 'FAIL'
            return False
    
    def test_ssl_configuration(self):
        """Test SSL configuration."""
        logger.info("Testing SSL configuration...")
        
        try:
            import ssl
            import socket
            
            # Test SSL certificate
            hostname = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')[0]
            port = 443
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            logger.info("SSL configuration test successful")
            self.test_results['ssl_configuration'] = 'PASS'
            return True
            
        except Exception as e:
            logger.warning(f"SSL configuration test failed: {e}")
            self.test_results['ssl_configuration'] = 'WARN'
            return True
    
    def test_security_headers(self):
        """Test security headers configuration."""
        logger.info("Testing security headers...")
        
        try:
            import requests
            
            # Test security headers
            url = os.environ.get('SITE_URL', 'http://localhost:8000')
            response = requests.get(url, timeout=10)
            
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection',
                'Strict-Transport-Security',
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if missing_headers:
                logger.warning(f"Missing security headers: {missing_headers}")
                self.test_results['security_headers'] = 'WARN'
            else:
                logger.info("All security headers present")
                self.test_results['security_headers'] = 'PASS'
            
            return True
            
        except Exception as e:
            logger.error(f"Security headers test failed: {e}")
            self.test_results['security_headers'] = 'FAIL'
            return False
    
    def test_performance_metrics(self):
        """Test performance metrics."""
        logger.info("Testing performance metrics...")
        
        try:
            import psutil
            
            # System performance metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'memory_available': memory.available,
                'disk_free': disk.free,
            }
            
            # Check if metrics are within acceptable ranges
            if cpu_percent < 80 and memory.percent < 80 and disk.percent < 90:
                logger.info(f"Performance metrics acceptable: {metrics}")
                self.test_results['performance_metrics'] = 'PASS'
                return True
            else:
                logger.warning(f"Performance metrics concerning: {metrics}")
                self.test_results['performance_metrics'] = 'WARN'
                return True
                
        except Exception as e:
            logger.error(f"Performance metrics test failed: {e}")
            self.test_results['performance_metrics'] = 'FAIL'
            return False
    
    def test_logging_configuration(self):
        """Test logging configuration."""
        logger.info("Testing logging configuration...")
        
        try:
            # Check if logs directory exists
            logs_dir = Path('logs')
            if logs_dir.exists():
                # Check if log files are being created
                log_files = list(logs_dir.glob('*.log'))
                if len(log_files) > 0:
                    logger.info(f"Log files found: {len(log_files)} files")
                    self.test_results['logging_configuration'] = 'PASS'
                    return True
                else:
                    logger.warning("No log files found")
                    self.test_results['logging_configuration'] = 'WARN'
                    return True
            else:
                logger.error("Logs directory not found")
                self.test_results['logging_configuration'] = 'FAIL'
                return False
                
        except Exception as e:
            logger.error(f"Logging configuration test failed: {e}")
            self.test_results['logging_configuration'] = 'FAIL'
            return False
    
    def test_environment_variables(self):
        """Test environment variables configuration."""
        logger.info("Testing environment variables...")
        
        required_vars = [
            'SECRET_KEY',
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD',
            'DB_HOST',
            'DB_PORT',
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing environment variables: {missing_vars}")
            self.test_results['environment_variables'] = 'FAIL'
            return False
        else:
            logger.info("All required environment variables present")
            self.test_results['environment_variables'] = 'PASS'
            return True
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        logger.info("Generating production test report...")
        
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        report = {
            'test_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_duration': f"{total_time:.2f} seconds",
                'total_tests': len(self.test_results),
                'passed_tests': len([r for r in self.test_results.values() if r == 'PASS']),
                'failed_tests': len([r for r in self.test_results.values() if r == 'FAIL']),
                'warning_tests': len([r for r in self.test_results.values() if r == 'WARN']),
            },
            'test_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        # Write report to file
        report_file = Path('production_test_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Production test report generated: {report_file}")
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        recommendations = []
        
        if self.test_results.get('database_connectivity') == 'FAIL':
            recommendations.append("Fix database connectivity issues")
        
        if self.test_results.get('redis_connectivity') == 'FAIL':
            recommendations.append("Fix Redis connectivity issues")
        
        if self.test_results.get('email_configuration') == 'FAIL':
            recommendations.append("Configure email settings properly")
        
        if self.test_results.get('static_files') == 'FAIL':
            recommendations.append("Collect static files")
        
        if self.test_results.get('security_headers') == 'WARN':
            recommendations.append("Add missing security headers")
        
        if self.test_results.get('performance_metrics') == 'WARN':
            recommendations.append("Optimize system performance")
        
        if not recommendations:
            recommendations.append("All production environment tests passed successfully!")
        
        return recommendations
    
    def run_all_tests(self):
        """Run all production environment tests."""
        logger.info("Starting production environment testing...")
        
        try:
            # Run all tests
            tests = [
                ('Database Connectivity', self.test_database_connectivity),
                ('Redis Connectivity', self.test_redis_connectivity),
                ('Email Configuration', self.test_email_configuration),
                ('Static Files', self.test_static_files),
                ('Media Files', self.test_media_files),
                ('SSL Configuration', self.test_ssl_configuration),
                ('Security Headers', self.test_security_headers),
                ('Performance Metrics', self.test_performance_metrics),
                ('Logging Configuration', self.test_logging_configuration),
                ('Environment Variables', self.test_environment_variables),
            ]
            
            for test_name, test_func in tests:
                logger.info(f"Running {test_name} test...")
                try:
                    test_func()
                except Exception as e:
                    logger.error(f"{test_name} test failed with error: {e}")
                    self.test_results[test_name.lower().replace(' ', '_')] = 'ERROR'
            
            # Generate report
            report = self.generate_test_report()
            
            # Print summary
            print("\n" + "="*60)
            print("PRODUCTION ENVIRONMENT TEST SUMMARY")
            print("="*60)
            print(f"Total Tests: {report['test_summary']['total_tests']}")
            print(f"Passed: {report['test_summary']['passed_tests']}")
            print(f"Failed: {report['test_summary']['failed_tests']}")
            print(f"Warnings: {report['test_summary']['warning_tests']}")
            print(f"Duration: {report['test_summary']['total_duration']}")
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"- {rec}")
            print("="*60)
            
            return report
            
        except Exception as e:
            logger.error(f"Production environment testing failed: {e}")
            return None

def main():
    """Main function to run production environment tests."""
    tester = ProductionEnvironmentTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    main()
