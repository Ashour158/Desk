#!/usr/bin/env python3
"""
Environment Configuration Validation Script
Validates all required environment variables and configuration settings
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple

class EnvironmentValidator:
    def __init__(self):
        self.required_vars = {
            'django_core': [
                'SECRET_KEY',
                'DEBUG',
                'ALLOWED_HOSTS',
                'DJANGO_SETTINGS_MODULE'
            ],
            'database': [
                'DATABASE_URL',
                'DB_HOST',
                'DB_NAME',
                'DB_USER',
                'DB_PASSWORD',
                'DB_PORT'
            ],
            'redis': [
                'REDIS_URL',
                'CELERY_BROKER_URL',
                'CELERY_RESULT_BACKEND'
            ],
            'email': [
                'EMAIL_HOST',
                'EMAIL_PORT',
                'EMAIL_HOST_USER',
                'EMAIL_HOST_PASSWORD',
                'DEFAULT_FROM_EMAIL'
            ],
            'security': [
                'CORS_ALLOWED_ORIGINS',
                'SECURE_SSL_REDIRECT',
                'SESSION_COOKIE_SECURE',
                'CSRF_COOKIE_SECURE'
            ],
            'external_services': [
                'OPENAI_API_KEY',
                'TWILIO_ACCOUNT_SID',
                'TWILIO_AUTH_TOKEN'
            ],
            'file_storage': [
                'AWS_ACCESS_KEY_ID',
                'AWS_SECRET_ACCESS_KEY',
                'AWS_STORAGE_BUCKET_NAME',
                'AWS_S3_REGION_NAME'
            ],
            'monitoring': [
                'SENTRY_DSN',
                'LOG_LEVEL'
            ]
        }
        
        self.optional_vars = [
            'ANTHROPIC_API_KEY',
            'GOOGLE_MAPS_API_KEY',
            'SENDGRID_API_KEY',
            'JWT_SECRET_KEY',
            'RATE_LIMIT_ENABLED',
            'METRICS_ENABLED'
        ]
        
        self.validation_results = {
            'required_vars': {},
            'optional_vars': {},
            'connections': {},
            'security': {},
            'overall_status': 'UNKNOWN'
        }
    
    def log(self, message: str, level: str = 'INFO'):
        """Log message with timestamp"""
        timestamp = __import__('datetime').datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def validate_required_variables(self) -> Dict[str, bool]:
        """Validate all required environment variables"""
        self.log("Validating required environment variables...")
        
        results = {}
        missing_vars = []
        
        for category, vars_list in self.required_vars.items():
            category_results = {}
            for var in vars_list:
                value = os.environ.get(var)
                if value:
                    category_results[var] = True
                    self.log(f"✅ {var}: Set")
                else:
                    category_results[var] = False
                    missing_vars.append(var)
                    self.log(f"❌ {var}: Missing", 'ERROR')
            
            results[category] = category_results
        
        if missing_vars:
            self.log(f"Missing required variables: {', '.join(missing_vars)}", 'ERROR')
            return False
        
        self.log("All required environment variables are set")
        return True
    
    def validate_optional_variables(self) -> Dict[str, bool]:
        """Validate optional environment variables"""
        self.log("Checking optional environment variables...")
        
        results = {}
        for var in self.optional_vars:
            value = os.environ.get(var)
            if value:
                results[var] = True
                self.log(f"✅ {var}: Set")
            else:
                results[var] = False
                self.log(f"⚠️ {var}: Not set (optional)")
        
        return results
    
    def validate_database_connection(self) -> bool:
        """Validate database connection"""
        self.log("Testing database connection...")
        
        try:
            import django
            from django.conf import settings
            from django.db import connection
            
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            if result:
                self.log("✅ Database connection successful")
                return True
            else:
                self.log("❌ Database connection failed", 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"❌ Database connection error: {str(e)}", 'ERROR')
            return False
    
    def validate_redis_connection(self) -> bool:
        """Validate Redis connection"""
        self.log("Testing Redis connection...")
        
        try:
            import redis
            from urllib.parse import urlparse
            
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                self.log("❌ REDIS_URL not set", 'ERROR')
                return False
            
            # Parse Redis URL
            parsed = urlparse(redis_url)
            r = redis.Redis(
                host=parsed.hostname,
                port=parsed.port or 6379,
                db=int(parsed.path.lstrip('/')) if parsed.path else 0,
                password=parsed.password
            )
            
            # Test connection
            r.ping()
            self.log("✅ Redis connection successful")
            return True
            
        except Exception as e:
            self.log(f"❌ Redis connection error: {str(e)}", 'ERROR')
            return False
    
    def validate_email_configuration(self) -> bool:
        """Validate email configuration"""
        self.log("Testing email configuration...")
        
        try:
            from django.core.mail import get_connection
            from django.conf import settings
            
            # Test email backend
            connection = get_connection()
            connection.open()
            connection.close()
            
            self.log("✅ Email configuration valid")
            return True
            
        except Exception as e:
            self.log(f"❌ Email configuration error: {str(e)}", 'ERROR')
            return False
    
    def validate_security_settings(self) -> Dict[str, bool]:
        """Validate security settings"""
        self.log("Validating security settings...")
        
        security_checks = {
            'ssl_redirect': os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true',
            'hsts_enabled': os.environ.get('SECURE_HSTS_SECONDS', '0') != '0',
            'session_secure': os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true',
            'csrf_secure': os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true',
            'cors_configured': bool(os.environ.get('CORS_ALLOWED_ORIGINS')),
            'secret_key_set': bool(os.environ.get('SECRET_KEY')),
            'debug_disabled': os.environ.get('DEBUG', 'True').lower() == 'false'
        }
        
        for check, result in security_checks.items():
            if result:
                self.log(f"✅ {check}: Secure")
            else:
                self.log(f"⚠️ {check}: Needs attention", 'WARNING')
        
        return security_checks
    
    def validate_external_services(self) -> Dict[str, bool]:
        """Validate external service configurations"""
        self.log("Validating external service configurations...")
        
        services = {
            'openai': bool(os.environ.get('OPENAI_API_KEY')),
            'twilio': bool(os.environ.get('TWILIO_ACCOUNT_SID') and os.environ.get('TWILIO_AUTH_TOKEN')),
            'aws': bool(os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')),
            'sentry': bool(os.environ.get('SENTRY_DSN'))
        }
        
        for service, configured in services.items():
            if configured:
                self.log(f"✅ {service}: Configured")
            else:
                self.log(f"⚠️ {service}: Not configured", 'WARNING')
        
        return services
    
    def validate_application_health(self) -> bool:
        """Validate application health endpoints"""
        self.log("Testing application health endpoints...")
        
        health_endpoints = [
            ('Django API', os.environ.get('DJANGO_API_URL', 'http://localhost:8000') + '/health/'),
            ('AI Service', os.environ.get('AI_SERVICE_URL', 'http://localhost:8001') + '/health/'),
            ('Realtime Service', os.environ.get('REALTIME_SERVICE_URL', 'http://localhost:3000') + '/health/')
        ]
        
        all_healthy = True
        
        for service_name, url in health_endpoints:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log(f"✅ {service_name}: Healthy")
                else:
                    self.log(f"❌ {service_name}: Unhealthy (Status: {response.status_code})", 'ERROR')
                    all_healthy = False
            except Exception as e:
                self.log(f"❌ {service_name}: Error - {str(e)}", 'ERROR')
                all_healthy = False
        
        return all_healthy
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        self.log("Generating validation report...")
        
        # Run all validations
        required_vars_valid = self.validate_required_variables()
        optional_vars_status = self.validate_optional_variables()
        db_connection = self.validate_database_connection()
        redis_connection = self.validate_redis_connection()
        email_config = self.validate_email_configuration()
        security_settings = self.validate_security_settings()
        external_services = self.validate_external_services()
        app_health = self.validate_application_health()
        
        # Calculate overall status
        critical_checks = [
            required_vars_valid,
            db_connection,
            redis_connection,
            email_config
        ]
        
        if all(critical_checks):
            overall_status = 'HEALTHY'
        elif any(critical_checks):
            overall_status = 'DEGRADED'
        else:
            overall_status = 'UNHEALTHY'
        
        # Generate report
        report = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'overall_status': overall_status,
            'required_variables': required_vars_valid,
            'optional_variables': optional_vars_status,
            'database_connection': db_connection,
            'redis_connection': redis_connection,
            'email_configuration': email_config,
            'security_settings': security_settings,
            'external_services': external_services,
            'application_health': app_health,
            'summary': {
                'total_checks': 8,
                'passed_checks': sum([
                    required_vars_valid,
                    db_connection,
                    redis_connection,
                    email_config,
                    app_health
                ]),
                'security_score': sum(security_settings.values()) / len(security_settings),
                'service_coverage': sum(external_services.values()) / len(external_services)
            }
        }
        
        return report
    
    def print_summary(self, report: Dict):
        """Print validation summary"""
        self.log("=" * 60)
        self.log("ENVIRONMENT VALIDATION SUMMARY")
        self.log("=" * 60)
        self.log(f"Overall Status: {report['overall_status']}")
        self.log(f"Required Variables: {'✅ PASS' if report['required_variables'] else '❌ FAIL'}")
        self.log(f"Database Connection: {'✅ PASS' if report['database_connection'] else '❌ FAIL'}")
        self.log(f"Redis Connection: {'✅ PASS' if report['redis_connection'] else '❌ FAIL'}")
        self.log(f"Email Configuration: {'✅ PASS' if report['email_configuration'] else '❌ FAIL'}")
        self.log(f"Application Health: {'✅ PASS' if report['application_health'] else '❌ FAIL'}")
        self.log(f"Security Score: {report['summary']['security_score']:.1%}")
        self.log(f"Service Coverage: {report['summary']['service_coverage']:.1%}")
        self.log(f"Checks Passed: {report['summary']['passed_checks']}/{report['summary']['total_checks']}")
        self.log("=" * 60)
    
    def save_report(self, report: Dict):
        """Save validation report to file"""
        report_file = f"validation_report_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        self.log(f"Report saved to {report_file}")

def main():
    """Main function"""
    print("🔍 Environment Configuration Validation")
    print("=" * 60)
    
    validator = EnvironmentValidator()
    
    try:
        # Generate report
        report = validator.generate_report()
        
        # Print summary
        validator.print_summary(report)
        
        # Save report
        validator.save_report(report)
        
        # Exit with appropriate code
        if report['overall_status'] == 'HEALTHY':
            sys.exit(0)
        elif report['overall_status'] == 'DEGRADED':
            sys.exit(1)
        else:
            sys.exit(2)
            
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    main()
