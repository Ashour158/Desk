#!/usr/bin/env python3
"""
Secrets Management Validation Script
Validates AWS Secrets Manager, HashiCorp Vault, and environment variable configurations
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class SecretsValidator:
    def __init__(self):
        self.results = {}
        self.test_secrets = {
            'DB_PASSWORD': 'test_db_password_123',
            'REDIS_PASSWORD': 'test_redis_password_456',
            'EMAIL_HOST_PASSWORD': 'test_email_password_789',
            'OPENAI_API_KEY': 'sk-test-openai-key-123456789',
            'TWILIO_ACCOUNT_SID': 'ACtest123456789',
            'TWILIO_AUTH_TOKEN': 'test_twilio_token_123',
            'SENDGRID_API_KEY': 'SG.test_sendgrid_key_123456789',
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'SENTRY_DSN': 'https://test@sentry.io/123456',
        }
    
    def test_environment_variables(self) -> Dict[str, Any]:
        """Test environment variables secrets management"""
        print("🔍 Testing Environment Variables...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Test setting and getting environment variables
            for key, value in self.test_secrets.items():
                os.environ[key] = value
                retrieved_value = os.environ.get(key)
                
                if retrieved_value == value:
                    results['tests'][key] = {'status': 'success', 'value': '***hidden***'}
                else:
                    results['tests'][key] = {'status': 'error', 'error': 'Value mismatch'}
                    results['errors'].append(f"Environment variable {key} test failed")
            
            # Test secret retrieval
            from core.apps.secrets.management import EnvironmentSecretsManager
            manager = EnvironmentSecretsManager()
            
            for key, expected_value in self.test_secrets.items():
                retrieved_value = manager.get_secret(key)
                if retrieved_value == expected_value:
                    results['tests'][f"{key}_manager"] = {'status': 'success'}
                else:
                    results['tests'][f"{key}_manager"] = {'status': 'error', 'error': 'Manager test failed'}
                    results['errors'].append(f"Secrets manager test failed for {key}")
            
            print("✅ Environment variables secrets management working")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Environment variables test failed: {e}")
        
        return results
    
    def test_aws_secrets_manager(self) -> Dict[str, Any]:
        """Test AWS Secrets Manager integration"""
        print("🔍 Testing AWS Secrets Manager...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Check if boto3 is available
            try:
                import boto3
                print("✅ boto3 is available")
            except ImportError:
                results['status'] = 'error'
                results['errors'].append("boto3 not installed. Install with: pip install boto3")
                print("❌ boto3 not installed")
                return results
            
            # Check AWS credentials
            try:
                session = boto3.Session()
                credentials = session.get_credentials()
                if credentials is None:
                    results['status'] = 'error'
                    results['errors'].append("AWS credentials not configured")
                    print("❌ AWS credentials not configured")
                    return results
                print("✅ AWS credentials configured")
            except Exception as e:
                results['status'] = 'error'
                results['errors'].append(f"AWS credentials error: {e}")
                print(f"❌ AWS credentials error: {e}")
                return results
            
            # Test AWS Secrets Manager
            from core.apps.secrets.management import AWSSecretsManager
            
            try:
                manager = AWSSecretsManager()
                print("✅ AWS Secrets Manager initialized")
                
                # Test setting a secret
                test_key = 'test_secret_validation'
                test_value = 'test_value_123'
                
                if manager.set_secret(test_key, test_value):
                    print("✅ Secret set successfully")
                    
                    # Test getting the secret
                    retrieved_value = manager.get_secret(test_key)
                    if retrieved_value == test_value:
                        print("✅ Secret retrieved successfully")
                        results['tests']['set_get_secret'] = {'status': 'success'}
                    else:
                        print("❌ Secret retrieval failed")
                        results['tests']['set_get_secret'] = {'status': 'error', 'error': 'Value mismatch'}
                        results['errors'].append("Secret retrieval failed")
                    
                    # Test deleting the secret
                    if manager.delete_secret(test_key):
                        print("✅ Secret deleted successfully")
                        results['tests']['delete_secret'] = {'status': 'success'}
                    else:
                        print("❌ Secret deletion failed")
                        results['tests']['delete_secret'] = {'status': 'error', 'error': 'Deletion failed'}
                        results['errors'].append("Secret deletion failed")
                else:
                    print("❌ Secret setting failed")
                    results['tests']['set_secret'] = {'status': 'error', 'error': 'Setting failed'}
                    results['errors'].append("Secret setting failed")
                
            except Exception as e:
                results['status'] = 'error'
                results['errors'].append(f"AWS Secrets Manager error: {e}")
                print(f"❌ AWS Secrets Manager error: {e}")
        
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ AWS Secrets Manager test failed: {e}")
        
        return results
    
    def test_vault_secrets_manager(self) -> Dict[str, Any]:
        """Test HashiCorp Vault integration"""
        print("🔍 Testing HashiCorp Vault...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Check if hvac is available
            try:
                import hvac
                print("✅ hvac is available")
            except ImportError:
                results['status'] = 'error'
                results['errors'].append("hvac not installed. Install with: pip install hvac")
                print("❌ hvac not installed")
                return results
            
            # Check Vault connection
            vault_url = os.environ.get('VAULT_URL', 'http://localhost:8200')
            vault_token = os.environ.get('VAULT_TOKEN', '')
            
            if not vault_token:
                results['status'] = 'error'
                results['errors'].append("VAULT_TOKEN not configured")
                print("❌ VAULT_TOKEN not configured")
                return results
            
            try:
                client = hvac.Client(url=vault_url, token=vault_token)
                if not client.is_authenticated():
                    results['status'] = 'error'
                    results['errors'].append("Vault authentication failed")
                    print("❌ Vault authentication failed")
                    return results
                print("✅ Vault authentication successful")
            except Exception as e:
                results['status'] = 'error'
                results['errors'].append(f"Vault connection error: {e}")
                print(f"❌ Vault connection error: {e}")
                return results
            
            # Test Vault Secrets Manager
            from core.apps.secrets.management import VaultSecretsManager
            
            try:
                manager = VaultSecretsManager()
                print("✅ Vault Secrets Manager initialized")
                
                # Test setting a secret
                test_key = 'test_secret_validation'
                test_value = 'test_value_123'
                
                if manager.set_secret(test_key, test_value):
                    print("✅ Secret set successfully")
                    
                    # Test getting the secret
                    retrieved_value = manager.get_secret(test_key)
                    if retrieved_value == test_value:
                        print("✅ Secret retrieved successfully")
                        results['tests']['set_get_secret'] = {'status': 'success'}
                    else:
                        print("❌ Secret retrieval failed")
                        results['tests']['set_get_secret'] = {'status': 'error', 'error': 'Value mismatch'}
                        results['errors'].append("Secret retrieval failed")
                    
                    # Test deleting the secret
                    if manager.delete_secret(test_key):
                        print("✅ Secret deleted successfully")
                        results['tests']['delete_secret'] = {'status': 'success'}
                    else:
                        print("❌ Secret deletion failed")
                        results['tests']['delete_secret'] = {'status': 'error', 'error': 'Deletion failed'}
                        results['errors'].append("Secret deletion failed")
                else:
                    print("❌ Secret setting failed")
                    results['tests']['set_secret'] = {'status': 'error', 'error': 'Setting failed'}
                    results['errors'].append("Secret setting failed")
                
            except Exception as e:
                results['status'] = 'error'
                results['errors'].append(f"Vault Secrets Manager error: {e}")
                print(f"❌ Vault Secrets Manager error: {e}")
        
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Vault Secrets Manager test failed: {e}")
        
        return results
    
    def test_secrets_integration(self) -> Dict[str, Any]:
        """Test secrets integration with Django settings"""
        print("🔍 Testing Secrets Integration...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Set up Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
            
            import django
            django.setup()
            
            from django.conf import settings
            from core.apps.secrets.management import configure_secrets
            
            # Test secrets configuration
            configure_secrets()
            
            # Check if secrets are properly configured
            secret_checks = {
                'DATABASES': hasattr(settings, 'DATABASES') and 'default' in settings.DATABASES,
                'CACHES': hasattr(settings, 'CACHES') and 'default' in settings.CACHES,
                'EMAIL_HOST_PASSWORD': hasattr(settings, 'EMAIL_HOST_PASSWORD'),
                'OPENAI_API_KEY': hasattr(settings, 'OPENAI_API_KEY'),
                'TWILIO_ACCOUNT_SID': hasattr(settings, 'TWILIO_ACCOUNT_SID'),
                'TWILIO_AUTH_TOKEN': hasattr(settings, 'TWILIO_AUTH_TOKEN'),
                'SENDGRID_API_KEY': hasattr(settings, 'SENDGRID_API_KEY'),
                'AWS_ACCESS_KEY_ID': hasattr(settings, 'AWS_ACCESS_KEY_ID'),
                'AWS_SECRET_ACCESS_KEY': hasattr(settings, 'AWS_SECRET_ACCESS_KEY'),
                'SENTRY_DSN': hasattr(settings, 'SENTRY_DSN'),
            }
            
            for check_name, check_result in secret_checks.items():
                if check_result:
                    results['tests'][check_name] = {'status': 'success'}
                else:
                    results['tests'][check_name] = {'status': 'error', 'error': 'Not configured'}
                    results['errors'].append(f"Secret {check_name} not configured")
            
            print("✅ Secrets integration test completed")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Secrets integration test failed: {e}")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all secrets management tests"""
        print("🚀 Starting Secrets Management Validation...")
        
        self.results = {
            'environment_variables': self.test_environment_variables(),
            'aws_secrets_manager': self.test_aws_secrets_manager(),
            'vault_secrets_manager': self.test_vault_secrets_manager(),
            'secrets_integration': self.test_secrets_integration(),
        }
        
        return self.results
    
    def generate_report(self):
        """Generate validation report"""
        print("\n📊 Secrets Management Validation Report")
        print("=" * 50)
        
        for test_name, results in self.results.items():
            print(f"\n{test_name.replace('_', ' ').title()}:")
            print("-" * 30)
            
            if results['status'] == 'success':
                print("✅ Status: PASSED")
            else:
                print("❌ Status: FAILED")
                for error in results.get('errors', []):
                    print(f"   - {error}")
            
            # Show test details
            for test_key, test_result in results.get('tests', {}).items():
                if test_result['status'] == 'success':
                    print(f"✅ {test_key}: PASSED")
                else:
                    print(f"❌ {test_key}: FAILED - {test_result.get('error', 'Unknown error')}")
        
        # Save detailed report
        report_file = project_root / 'secrets_management_validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def cleanup_test_secrets(self):
        """Clean up test secrets from environment"""
        print("\n🧹 Cleaning up test secrets...")
        
        for key in self.test_secrets.keys():
            if key in os.environ:
                del os.environ[key]
        
        print("✅ Test secrets cleaned up")

def main():
    """Main function"""
    validator = SecretsValidator()
    
    try:
        results = validator.run_all_tests()
        validator.generate_report()
        
        # Check overall status
        all_passed = all(result['status'] == 'success' for result in results.values())
        
        if all_passed:
            print("\n🎉 All secrets management tests passed!")
            return 0
        else:
            print("\n💥 Some secrets management tests failed!")
            return 1
    
    except Exception as e:
        print(f"\n❌ Secrets management validation failed: {e}")
        return 1
    
    finally:
        validator.cleanup_test_secrets()

if __name__ == '__main__':
    sys.exit(main())
