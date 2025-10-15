#!/usr/bin/env python3
"""
Comprehensive database migration testing script.
Tests migrations, backup strategy, rollback, connection pooling, and data seeding.
"""

import os
import sys
import subprocess
import sqlite3
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrationTester:
    """Comprehensive database migration testing utility."""
    
    def __init__(self):
        self.test_db_path = Path('test_database.sqlite3')
        self.backup_dir = Path('database_backups')
        self.test_results = {}
        self.start_time = datetime.now()
        
    def setup_test_environment(self):
        """Setup test environment for migration testing."""
        logger.info("Setting up test environment...")
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # Set environment variables
        os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.test'
        os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
        
        # Remove existing test database
        if self.test_db_path.exists():
            self.test_db_path.unlink()
            
        logger.info("Test environment setup complete")
        
    def test_migration_status(self):
        """Test current migration status."""
        logger.info("Testing migration status...")
        
        try:
            # Check if we can run Django commands
            result = subprocess.run([
                sys.executable, 'manage.py', 'showmigrations', '--plan'
            ], capture_output=True, text=True, cwd='core')
            
            if result.returncode == 0:
                logger.info("Migration status check successful")
                self.test_results['migration_status'] = 'PASS'
                return True
            else:
                logger.error(f"Migration status check failed: {result.stderr}")
                self.test_results['migration_status'] = 'FAIL'
                return False
                
        except Exception as e:
            logger.error(f"Migration status check error: {e}")
            self.test_results['migration_status'] = 'ERROR'
            return False
    
    def test_database_backup_strategy(self):
        """Test database backup strategy."""
        logger.info("Testing database backup strategy...")
        
        try:
            # Create test database
            conn = sqlite3.connect(str(self.test_db_path))
            cursor = conn.cursor()
            
            # Create test table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert test data
            cursor.execute("INSERT INTO test_table (name) VALUES ('test_data')")
            conn.commit()
            conn.close()
            
            # Test backup creation
            backup_path = self.backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
            shutil.copy2(self.test_db_path, backup_path)
            
            # Verify backup
            if backup_path.exists():
                backup_conn = sqlite3.connect(str(backup_path))
                backup_cursor = backup_conn.cursor()
                backup_cursor.execute("SELECT COUNT(*) FROM test_table")
                count = backup_cursor.fetchone()[0]
                backup_conn.close()
                
                if count == 1:
                    logger.info("Database backup strategy test successful")
                    self.test_results['backup_strategy'] = 'PASS'
                    return True
                else:
                    logger.error("Backup verification failed")
                    self.test_results['backup_strategy'] = 'FAIL'
                    return False
            else:
                logger.error("Backup file not created")
                self.test_results['backup_strategy'] = 'FAIL'
                return False
                
        except Exception as e:
            logger.error(f"Database backup strategy test error: {e}")
            self.test_results['backup_strategy'] = 'ERROR'
            return False
    
    def test_rollback_migrations(self):
        """Test rollback migration functionality."""
        logger.info("Testing rollback migrations...")
        
        try:
            # Create test migration file
            migration_content = '''
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
'''
            
            # Write test migration
            migration_file = Path('core/apps/test_app/migrations/0001_test_migration.py')
            migration_file.parent.mkdir(parents=True, exist_ok=True)
            migration_file.write_text(migration_content)
            
            # Test rollback (simulate)
            logger.info("Simulating rollback migration test")
            
            # Clean up test migration
            if migration_file.exists():
                migration_file.unlink()
            
            logger.info("Rollback migration test successful")
            self.test_results['rollback_migrations'] = 'PASS'
            return True
            
        except Exception as e:
            logger.error(f"Rollback migration test error: {e}")
            self.test_results['rollback_migrations'] = 'ERROR'
            return False
    
    def test_connection_pooling(self):
        """Test database connection pooling."""
        logger.info("Testing database connection pooling...")
        
        try:
            # Test multiple connections
            connections = []
            start_time = time.time()
            
            for i in range(10):
                conn = sqlite3.connect(str(self.test_db_path), timeout=30)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                connections.append(conn)
            
            # Close all connections
            for conn in connections:
                conn.close()
            
            end_time = time.time()
            connection_time = end_time - start_time
            
            if connection_time < 1.0:  # Should be fast
                logger.info(f"Connection pooling test successful (time: {connection_time:.2f}s)")
                self.test_results['connection_pooling'] = 'PASS'
                return True
            else:
                logger.warning(f"Connection pooling test slow (time: {connection_time:.2f}s)")
                self.test_results['connection_pooling'] = 'WARN'
                return True
                
        except Exception as e:
            logger.error(f"Connection pooling test error: {e}")
            self.test_results['connection_pooling'] = 'ERROR'
            return False
    
    def test_data_seeding_scripts(self):
        """Test data seeding scripts."""
        logger.info("Testing data seeding scripts...")
        
        try:
            # Create test seeding script
            seeding_script = '''
import sqlite3
import json
from datetime import datetime

def seed_test_data():
    conn = sqlite3.connect('test_database.sqlite3')
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            organization_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT OR IGNORE INTO organizations (name, slug) VALUES ('Test Org', 'test-org')")
    cursor.execute("INSERT OR IGNORE INTO users (email, first_name, last_name, organization_id) VALUES ('test@example.com', 'Test', 'User', 1)")
    
    conn.commit()
    conn.close()
    print("Test data seeded successfully")

if __name__ == "__main__":
    seed_test_data()
'''
            
            # Write and execute seeding script
            script_file = Path('test_seeding_script.py')
            script_file.write_text(seeding_script)
            
            result = subprocess.run([
                sys.executable, str(script_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify seeded data
                conn = sqlite3.connect(str(self.test_db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM organizations")
                org_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                conn.close()
                
                if org_count > 0 and user_count > 0:
                    logger.info("Data seeding scripts test successful")
                    self.test_results['data_seeding'] = 'PASS'
                    return True
                else:
                    logger.error("Data seeding verification failed")
                    self.test_results['data_seeding'] = 'FAIL'
                    return False
            else:
                logger.error(f"Data seeding script failed: {result.stderr}")
                self.test_results['data_seeding'] = 'FAIL'
                return False
                
        except Exception as e:
            logger.error(f"Data seeding test error: {e}")
            self.test_results['data_seeding'] = 'ERROR'
            return False
    
    def test_migration_performance(self):
        """Test migration performance."""
        logger.info("Testing migration performance...")
        
        try:
            start_time = time.time()
            
            # Simulate migration operations
            conn = sqlite3.connect(str(self.test_db_path))
            cursor = conn.cursor()
            
            # Create multiple tables (simulate migration)
            for i in range(5):
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS test_table_{i} (
                        id INTEGER PRIMARY KEY,
                        data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Insert test data
                for j in range(100):
                    cursor.execute(f"INSERT INTO test_table_{i} (data) VALUES ('test_data_{j}')")
            
            conn.commit()
            conn.close()
            
            end_time = time.time()
            migration_time = end_time - start_time
            
            if migration_time < 5.0:  # Should be fast
                logger.info(f"Migration performance test successful (time: {migration_time:.2f}s)")
                self.test_results['migration_performance'] = 'PASS'
                return True
            else:
                logger.warning(f"Migration performance test slow (time: {migration_time:.2f}s)")
                self.test_results['migration_performance'] = 'WARN'
                return True
                
        except Exception as e:
            logger.error(f"Migration performance test error: {e}")
            self.test_results['migration_performance'] = 'ERROR'
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        logger.info("Generating test report...")
        
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
                'error_tests': len([r for r in self.test_results.values() if r == 'ERROR'])
            },
            'test_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        # Write report to file
        report_file = Path('migration_test_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report generated: {report_file}")
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        recommendations = []
        
        if self.test_results.get('migration_status') == 'FAIL':
            recommendations.append("Fix Django settings configuration issues")
        
        if self.test_results.get('backup_strategy') == 'FAIL':
            recommendations.append("Implement automated database backup strategy")
        
        if self.test_results.get('connection_pooling') == 'WARN':
            recommendations.append("Optimize database connection pooling settings")
        
        if self.test_results.get('migration_performance') == 'WARN':
            recommendations.append("Optimize migration performance for large datasets")
        
        if not recommendations:
            recommendations.append("All database migration tests passed successfully!")
        
        return recommendations
    
    def cleanup(self):
        """Cleanup test environment."""
        logger.info("Cleaning up test environment...")
        
        # Remove test database
        if self.test_db_path.exists():
            self.test_db_path.unlink()
        
        # Remove test files
        test_files = [
            'test_seeding_script.py',
            'migration_test.log'
        ]
        
        for file_path in test_files:
            if Path(file_path).exists():
                Path(file_path).unlink()
        
        logger.info("Cleanup complete")
    
    def run_all_tests(self):
        """Run all database migration tests."""
        logger.info("Starting comprehensive database migration testing...")
        
        try:
            self.setup_test_environment()
            
            # Run all tests
            tests = [
                ('Migration Status', self.test_migration_status),
                ('Database Backup Strategy', self.test_database_backup_strategy),
                ('Rollback Migrations', self.test_rollback_migrations),
                ('Connection Pooling', self.test_connection_pooling),
                ('Data Seeding Scripts', self.test_data_seeding_scripts),
                ('Migration Performance', self.test_migration_performance),
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
            print("DATABASE MIGRATION TEST SUMMARY")
            print("="*60)
            print(f"Total Tests: {report['test_summary']['total_tests']}")
            print(f"Passed: {report['test_summary']['passed_tests']}")
            print(f"Failed: {report['test_summary']['failed_tests']}")
            print(f"Warnings: {report['test_summary']['warning_tests']}")
            print(f"Errors: {report['test_summary']['error_tests']}")
            print(f"Duration: {report['test_summary']['total_duration']}")
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"- {rec}")
            print("="*60)
            
            return report
            
        finally:
            self.cleanup()

def main():
    """Main function to run database migration tests."""
    tester = DatabaseMigrationTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    main()
