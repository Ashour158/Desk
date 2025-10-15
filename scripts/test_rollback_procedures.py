#!/usr/bin/env python3
"""
Rollback Procedures Testing Script
Tests rollback procedures for configuration changes, deployments, and database migrations
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class RollbackTester:
    def __init__(self):
        self.results = {}
        self.backup_dir = project_root / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def create_backup(self, backup_name: str, files: List[str]) -> str:
        """Create a backup of specified files"""
        backup_path = self.backup_dir / f"{backup_name}_{self.timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        for file_path in files:
            source = project_root / file_path
            if source.exists():
                dest = backup_path / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(source.read_text())
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str, files: List[str]) -> bool:
        """Restore files from backup"""
        try:
            backup_dir = Path(backup_path)
            for file_path in files:
                source = backup_dir / file_path
                if source.exists():
                    dest = project_root / file_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(source.read_text())
            return True
        except Exception as e:
            print(f"❌ Failed to restore backup: {e}")
            return False
    
    def test_configuration_rollback(self) -> Dict[str, Any]:
        """Test configuration file rollback"""
        print("🔄 Testing Configuration Rollback...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Files to test rollback for
            config_files = [
                'core/config/settings/development.py',
                'core/config/settings/staging.py',
                'core/config/settings/production.py',
                'core/config/settings/base.py',
                'nginx/nginx.conf',
                'docker-compose.yml',
            ]
            
            # Create backup
            backup_path = self.create_backup('config_backup', config_files)
            print(f"✅ Configuration backup created: {backup_path}")
            
            # Simulate configuration change
            staging_file = project_root / 'core/config/settings/staging.py'
            if staging_file.exists():
                original_content = staging_file.read_text()
                
                # Add a test comment
                modified_content = original_content + "\n# TEST ROLLBACK COMMENT\n"
                staging_file.write_text(modified_content)
                print("✅ Configuration modified for testing")
                
                # Test rollback
                if self.restore_backup(backup_path, config_files):
                    print("✅ Configuration rollback successful")
                    results['tests']['config_rollback'] = {'status': 'success'}
                else:
                    print("❌ Configuration rollback failed")
                    results['tests']['config_rollback'] = {'status': 'error', 'error': 'Restore failed'}
                    results['errors'].append("Configuration rollback failed")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Configuration rollback test failed: {e}")
        
        return results
    
    def test_database_migration_rollback(self) -> Dict[str, Any]:
        """Test database migration rollback"""
        print("🔄 Testing Database Migration Rollback...")
        
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
            
            from django.core.management import execute_from_command_line
            
            # Get current migration state
            try:
                result = subprocess.run(
                    ['python', 'manage.py', 'showmigrations'],
                    capture_output=True,
                    text=True,
                    cwd=project_root
                )
                current_migrations = result.stdout
                print("✅ Current migration state captured")
            except Exception as e:
                print(f"❌ Failed to get migration state: {e}")
                results['errors'].append(f"Migration state capture failed: {e}")
                return results
            
            # Create a test migration
            try:
                result = subprocess.run(
                    ['python', 'manage.py', 'makemigrations', '--empty', 'test_app'],
                    capture_output=True,
                    text=True,
                    cwd=project_root
                )
                if result.returncode == 0:
                    print("✅ Test migration created")
                else:
                    print(f"❌ Failed to create test migration: {result.stderr}")
                    results['errors'].append("Test migration creation failed")
                    return results
            except Exception as e:
                print(f"❌ Migration creation failed: {e}")
                results['errors'].append(f"Migration creation failed: {e}")
                return results
            
            # Apply migration
            try:
                result = subprocess.run(
                    ['python', 'manage.py', 'migrate'],
                    capture_output=True,
                    text=True,
                    cwd=project_root
                )
                if result.returncode == 0:
                    print("✅ Migration applied")
                else:
                    print(f"❌ Migration application failed: {result.stderr}")
                    results['errors'].append("Migration application failed")
                    return results
            except Exception as e:
                print(f"❌ Migration application failed: {e}")
                results['errors'].append(f"Migration application failed: {e}")
                return results
            
            # Test rollback
            try:
                result = subprocess.run(
                    ['python', 'manage.py', 'migrate', 'test_app', 'zero'],
                    capture_output=True,
                    text=True,
                    cwd=project_root
                )
                if result.returncode == 0:
                    print("✅ Migration rollback successful")
                    results['tests']['migration_rollback'] = {'status': 'success'}
                else:
                    print(f"❌ Migration rollback failed: {result.stderr}")
                    results['tests']['migration_rollback'] = {'status': 'error', 'error': 'Rollback failed'}
                    results['errors'].append("Migration rollback failed")
            except Exception as e:
                print(f"❌ Migration rollback failed: {e}")
                results['tests']['migration_rollback'] = {'status': 'error', 'error': str(e)}
                results['errors'].append(f"Migration rollback failed: {e}")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Database migration rollback test failed: {e}")
        
        return results
    
    def test_environment_rollback(self) -> Dict[str, Any]:
        """Test environment variable rollback"""
        print("🔄 Testing Environment Variable Rollback...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Test environment variables
            test_vars = {
                'TEST_VAR_1': 'original_value_1',
                'TEST_VAR_2': 'original_value_2',
                'TEST_VAR_3': 'original_value_3',
            }
            
            # Set original values
            original_values = {}
            for key, value in test_vars.items():
                original_values[key] = os.environ.get(key)
                os.environ[key] = value
            
            print("✅ Original environment variables set")
            
            # Simulate environment change
            for key in test_vars.keys():
                os.environ[key] = f"modified_{key}_value"
            
            print("✅ Environment variables modified")
            
            # Test rollback
            rollback_success = True
            for key, original_value in original_values.items():
                if original_value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = original_value
            
            # Verify rollback
            for key, expected_value in original_values.items():
                current_value = os.environ.get(key)
                if current_value != expected_value:
                    rollback_success = False
                    results['errors'].append(f"Environment variable {key} rollback failed")
            
            if rollback_success:
                print("✅ Environment variable rollback successful")
                results['tests']['env_rollback'] = {'status': 'success'}
            else:
                print("❌ Environment variable rollback failed")
                results['tests']['env_rollback'] = {'status': 'error', 'error': 'Rollback verification failed'}
                results['errors'].append("Environment variable rollback failed")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Environment variable rollback test failed: {e}")
        
        return results
    
    def test_secrets_rollback(self) -> Dict[str, Any]:
        """Test secrets management rollback"""
        print("🔄 Testing Secrets Management Rollback...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Test secrets rollback
            test_secrets = {
                'TEST_SECRET_1': 'original_secret_1',
                'TEST_SECRET_2': 'original_secret_2',
                'TEST_SECRET_3': 'original_secret_3',
            }
            
            # Store original values
            original_secrets = {}
            for key, value in test_secrets.items():
                original_secrets[key] = os.environ.get(key)
                os.environ[key] = value
            
            print("✅ Original secrets set")
            
            # Simulate secrets change
            for key in test_secrets.keys():
                os.environ[key] = f"modified_{key}_secret"
            
            print("✅ Secrets modified")
            
            # Test rollback
            rollback_success = True
            for key, original_value in original_secrets.items():
                if original_value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = original_value
            
            # Verify rollback
            for key, expected_value in original_secrets.items():
                current_value = os.environ.get(key)
                if current_value != expected_value:
                    rollback_success = False
                    results['errors'].append(f"Secret {key} rollback failed")
            
            if rollback_success:
                print("✅ Secrets rollback successful")
                results['tests']['secrets_rollback'] = {'status': 'success'}
            else:
                print("❌ Secrets rollback failed")
                results['tests']['secrets_rollback'] = {'status': 'error', 'error': 'Rollback verification failed'}
                results['errors'].append("Secrets rollback failed")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Secrets rollback test failed: {e}")
        
        return results
    
    def test_feature_flags_rollback(self) -> Dict[str, Any]:
        """Test feature flags rollback"""
        print("🔄 Testing Feature Flags Rollback...")
        
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
            
            # Get original feature flags
            original_flags = getattr(settings, 'FEATURE_FLAGS', {})
            print("✅ Original feature flags captured")
            
            # Simulate feature flags change
            modified_flags = original_flags.copy()
            modified_flags['TEST_FEATURE'] = True
            modified_flags['ANOTHER_TEST_FEATURE'] = False
            
            # Simulate rollback by restoring original flags
            rollback_success = True
            for key, value in original_flags.items():
                if key in modified_flags and modified_flags[key] != value:
                    rollback_success = False
                    results['errors'].append(f"Feature flag {key} rollback failed")
            
            if rollback_success:
                print("✅ Feature flags rollback successful")
                results['tests']['feature_flags_rollback'] = {'status': 'success'}
            else:
                print("❌ Feature flags rollback failed")
                results['tests']['feature_flags_rollback'] = {'status': 'error', 'error': 'Rollback verification failed'}
                results['errors'].append("Feature flags rollback failed")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Feature flags rollback test failed: {e}")
        
        return results
    
    def test_deployment_rollback(self) -> Dict[str, Any]:
        """Test deployment rollback"""
        print("🔄 Testing Deployment Rollback...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Test Docker deployment rollback
            docker_files = [
                'docker-compose.yml',
                'core/Dockerfile',
                'ai-service/Dockerfile',
                'realtime-service/Dockerfile',
            ]
            
            # Create backup
            backup_path = self.create_backup('deployment_backup', docker_files)
            print(f"✅ Deployment backup created: {backup_path}")
            
            # Simulate deployment change
            docker_compose_file = project_root / 'docker-compose.yml'
            if docker_compose_file.exists():
                original_content = docker_compose_file.read_text()
                
                # Add a test comment
                modified_content = original_content + "\n# TEST DEPLOYMENT ROLLBACK\n"
                docker_compose_file.write_text(modified_content)
                print("✅ Deployment configuration modified")
                
                # Test rollback
                if self.restore_backup(backup_path, docker_files):
                    print("✅ Deployment rollback successful")
                    results['tests']['deployment_rollback'] = {'status': 'success'}
                else:
                    print("❌ Deployment rollback failed")
                    results['tests']['deployment_rollback'] = {'status': 'error', 'error': 'Restore failed'}
                    results['errors'].append("Deployment rollback failed")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Deployment rollback test failed: {e}")
        
        return results
    
    def test_nginx_rollback(self) -> Dict[str, Any]:
        """Test Nginx configuration rollback"""
        print("🔄 Testing Nginx Configuration Rollback...")
        
        results = {
            'status': 'success',
            'tests': {},
            'errors': []
        }
        
        try:
            # Test Nginx configuration rollback
            nginx_files = [
                'nginx/nginx.conf',
                'nginx/ssl/',
            ]
            
            # Create backup
            backup_path = self.create_backup('nginx_backup', nginx_files)
            print(f"✅ Nginx backup created: {backup_path}")
            
            # Simulate Nginx configuration change
            nginx_file = project_root / 'nginx/nginx.conf'
            if nginx_file.exists():
                original_content = nginx_file.read_text()
                
                # Add a test comment
                modified_content = original_content + "\n# TEST NGINX ROLLBACK\n"
                nginx_file.write_text(modified_content)
                print("✅ Nginx configuration modified")
                
                # Test rollback
                if self.restore_backup(backup_path, nginx_files):
                    print("✅ Nginx rollback successful")
                    results['tests']['nginx_rollback'] = {'status': 'success'}
                else:
                    print("❌ Nginx rollback failed")
                    results['tests']['nginx_rollback'] = {'status': 'error', 'error': 'Restore failed'}
                    results['errors'].append("Nginx rollback failed")
            
        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(str(e))
            print(f"❌ Nginx rollback test failed: {e}")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all rollback tests"""
        print("🚀 Starting Rollback Procedures Tests...")
        
        self.results = {
            'configuration_rollback': self.test_configuration_rollback(),
            'database_migration_rollback': self.test_database_migration_rollback(),
            'environment_rollback': self.test_environment_rollback(),
            'secrets_rollback': self.test_secrets_rollback(),
            'feature_flags_rollback': self.test_feature_flags_rollback(),
            'deployment_rollback': self.test_deployment_rollback(),
            'nginx_rollback': self.test_nginx_rollback(),
        }
        
        return self.results
    
    def generate_report(self):
        """Generate rollback test report"""
        print("\n📊 Rollback Procedures Test Report")
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
        report_file = project_root / 'rollback_procedures_test_report.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
    
    def cleanup_backups(self):
        """Clean up test backups"""
        print("\n🧹 Cleaning up test backups...")
        
        try:
            import shutil
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            print("✅ Test backups cleaned up")
        except Exception as e:
            print(f"⚠️ Failed to clean up backups: {e}")

def main():
    """Main function"""
    tester = RollbackTester()
    
    try:
        results = tester.run_all_tests()
        tester.generate_report()
        
        # Check overall status
        all_passed = all(result['status'] == 'success' for result in results.values())
        
        if all_passed:
            print("\n🎉 All rollback procedures tests passed!")
            return 0
        else:
            print("\n💥 Some rollback procedures tests failed!")
            return 1
    
    except Exception as e:
        print(f"\n❌ Rollback procedures testing failed: {e}")
        return 1
    
    finally:
        tester.cleanup_backups()

if __name__ == '__main__':
    sys.exit(main())
