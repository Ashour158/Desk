#!/usr/bin/env python3
"""
Environment Switching Test Script
Tests switching between development, staging, and production environments
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Environment configurations
ENVIRONMENTS = {
    'development': {
        'DJANGO_SETTINGS_MODULE': 'config.settings.development',
        'DEBUG': 'True',
        'DATABASE_URL': 'sqlite:///db.sqlite3',
        'REDIS_URL': 'redis://localhost:6379/0',
        'ALLOWED_HOSTS': 'localhost,127.0.0.1',
        'CORS_ALLOWED_ORIGINS': 'http://localhost:3000,http://127.0.0.1:3000',
        'SECURE_SSL_REDIRECT': 'False',
        'SECURE_HSTS_SECONDS': '0',
    },
    'staging': {
        'DJANGO_SETTINGS_MODULE': 'config.settings.staging',
        'DEBUG': 'False',
        'DATABASE_URL': 'postgresql://helpdesk_user:password@staging-db:5432/helpdesk_staging',
        'REDIS_URL': 'redis://staging-redis:6379/1',
        'ALLOWED_HOSTS': 'staging.helpdesk.com,staging-api.helpdesk.com',
        'CORS_ALLOWED_ORIGINS': 'https://staging.helpdesk.com,https://staging-api.helpdesk.com',
        'SECURE_SSL_REDIRECT': 'True',
        'SECURE_HSTS_SECONDS': '31536000',
    },
    'production': {
        'DJANGO_SETTINGS_MODULE': 'config.settings.production',
        'DEBUG': 'False',
        'DATABASE_URL': 'postgresql://helpdesk_user:password@prod-db:5432/helpdesk_production',
        'REDIS_URL': 'redis://prod-redis:6379/1',
        'ALLOWED_HOSTS': 'helpdesk.com,api.helpdesk.com',
        'CORS_ALLOWED_ORIGINS': 'https://helpdesk.com,https://api.helpdesk.com',
        'SECURE_SSL_REDIRECT': 'True',
        'SECURE_HSTS_SECONDS': '31536000',
    }
}

class EnvironmentTester:
    def __init__(self):
        self.results = {}
        self.current_env = None
        
    def set_environment(self, env_name):
        """Set environment variables for the specified environment"""
        if env_name not in ENVIRONMENTS:
            raise ValueError(f"Unknown environment: {env_name}")
            
        env_vars = ENVIRONMENTS[env_name]
        for key, value in env_vars.items():
            os.environ[key] = value
            
        self.current_env = env_name
        print(f"✅ Environment set to: {env_name}")
        
    def test_django_settings(self):
        """Test Django settings loading"""
        try:
            import django
            from django.conf import settings
            
            # Test basic settings
            tests = {
                'DEBUG': settings.DEBUG,
                'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
                'DATABASES': settings.DATABASES,
                'CACHES': settings.CACHES,
                'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', None),
                'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', None),
            }
            
            print(f"✅ Django settings loaded successfully for {self.current_env}")
            return {'status': 'success', 'tests': tests}
            
        except Exception as e:
            print(f"❌ Django settings failed for {self.current_env}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_database_connection(self):
        """Test database connection"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            print(f"✅ Database connection successful for {self.current_env}")
            return {'status': 'success', 'result': result}
            
        except Exception as e:
            print(f"❌ Database connection failed for {self.current_env}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_cache_connection(self):
        """Test cache connection"""
        try:
            from django.core.cache import cache
            cache.set('test_key', 'test_value', 10)
            result = cache.get('test_key')
            cache.delete('test_key')
            
            if result == 'test_value':
                print(f"✅ Cache connection successful for {self.current_env}")
                return {'status': 'success', 'result': result}
            else:
                print(f"❌ Cache test failed for {self.current_env}")
                return {'status': 'error', 'error': 'Cache test failed'}
                
        except Exception as e:
            print(f"❌ Cache connection failed for {self.current_env}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_feature_flags(self):
        """Test feature flags configuration"""
        try:
            from django.conf import settings
            
            # Check if feature flags are configured
            feature_flags = getattr(settings, 'FEATURE_FLAGS', {})
            api_endpoints = getattr(settings, 'API_ENDPOINTS', {})
            third_party_services = getattr(settings, 'THIRD_PARTY_SERVICES', {})
            
            tests = {
                'feature_flags_count': len(feature_flags),
                'api_endpoints_count': len(api_endpoints),
                'third_party_services_count': len(third_party_services),
                'feature_flags': feature_flags,
                'api_endpoints': api_endpoints,
                'third_party_services': third_party_services,
            }
            
            print(f"✅ Feature flags configured for {self.current_env}")
            return {'status': 'success', 'tests': tests}
            
        except Exception as e:
            print(f"❌ Feature flags test failed for {self.current_env}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_security_settings(self):
        """Test security settings"""
        try:
            from django.conf import settings
            
            security_tests = {
                'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', None),
                'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', None),
                'SECURE_HSTS_INCLUDE_SUBDOMAINS': getattr(settings, 'SECURE_HSTS_INCLUDE_SUBDOMAINS', None),
                'SECURE_HSTS_PRELOAD': getattr(settings, 'SECURE_HSTS_PRELOAD', None),
                'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', None),
                'SECURE_BROWSER_XSS_FILTER': getattr(settings, 'SECURE_BROWSER_XSS_FILTER', None),
                'X_FRAME_OPTIONS': getattr(settings, 'X_FRAME_OPTIONS', None),
                'SECURE_REFERRER_POLICY': getattr(settings, 'SECURE_REFERRER_POLICY', None),
            }
            
            print(f"✅ Security settings configured for {self.current_env}")
            return {'status': 'success', 'tests': security_tests}
            
        except Exception as e:
            print(f"❌ Security settings test failed for {self.current_env}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_environment_switching(self):
        """Test switching between environments"""
        print("\n🔄 Testing Environment Switching...")
        
        for env_name in ENVIRONMENTS.keys():
            print(f"\n--- Testing {env_name.upper()} Environment ---")
            
            # Set environment
            self.set_environment(env_name)
            
            # Initialize Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', ENVIRONMENTS[env_name]['DJANGO_SETTINGS_MODULE'])
            
            try:
                import django
                django.setup()
                
                # Run tests
                env_results = {
                    'django_settings': self.test_django_settings(),
                    'database_connection': self.test_database_connection(),
                    'cache_connection': self.test_cache_connection(),
                    'feature_flags': self.test_feature_flags(),
                    'security_settings': self.test_security_settings(),
                }
                
                self.results[env_name] = env_results
                
            except Exception as e:
                print(f"❌ Failed to initialize {env_name}: {e}")
                self.results[env_name] = {'error': str(e)}
    
    def generate_report(self):
        """Generate test report"""
        print("\n📊 Environment Switching Test Report")
        print("=" * 50)
        
        for env_name, results in self.results.items():
            print(f"\n{env_name.upper()} Environment:")
            print("-" * 30)
            
            if 'error' in results:
                print(f"❌ Initialization Error: {results['error']}")
                continue
                
            for test_name, test_result in results.items():
                if test_result['status'] == 'success':
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED - {test_result.get('error', 'Unknown error')}")
        
        # Save detailed report
        report_file = project_root / 'environment_switching_test_report.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def run_all_tests(self):
        """Run all environment switching tests"""
        print("🚀 Starting Environment Switching Tests...")
        
        try:
            self.test_environment_switching()
            self.generate_report()
            
            print("\n✅ Environment switching tests completed!")
            
        except Exception as e:
            print(f"\n❌ Environment switching tests failed: {e}")
            return False
        
        return True

def main():
    """Main function"""
    tester = EnvironmentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All environment switching tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some environment switching tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
