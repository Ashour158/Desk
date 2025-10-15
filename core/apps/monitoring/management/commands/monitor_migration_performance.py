"""
Management command to monitor migration performance.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection, transaction
from django.utils import timezone
import time
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Monitor migration performance command."""
    
    help = 'Monitor and analyze migration performance metrics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            type=int,
            default=300,
            help='Duration in seconds to monitor (default: 300)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Monitoring interval in seconds (default: 30)',
        )
        parser.add_argument(
            '--output-file',
            type=str,
            default='migration_performance_report.json',
            help='Output file for performance report',
        )
        parser.add_argument(
            '--test-migration',
            action='store_true',
            help='Test migration performance with sample data',
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        duration = options['duration']
        interval = options['interval']
        output_file = options['output_file']
        test_migration = options['test_migration']
        
        self.stdout.write(
            self.style.SUCCESS("Starting migration performance monitoring...")
        )
        
        # Initialize monitoring
        monitoring_data = {
            'start_time': timezone.now().isoformat(),
            'duration': duration,
            'interval': interval,
            'metrics': [],
            'migrations_tested': [],
            'performance_summary': {}
        }
        
        # Test migration if requested
        if test_migration:
            self._test_migration_performance(monitoring_data)
        
        # Monitor for specified duration
        self._monitor_migration_performance(monitoring_data, duration, interval)
        
        # Generate performance report
        self._generate_performance_report(monitoring_data, output_file)
        
        self.stdout.write(
            self.style.SUCCESS(f"Migration performance monitoring completed!")
        )
        self.stdout.write(f"Report saved to: {output_file}")
    
    def _test_migration_performance(self, monitoring_data):
        """Test migration performance with sample data."""
        self.stdout.write("Testing migration performance...")
        
        test_migrations = [
            {
                'name': 'create_test_table',
                'sql': '''
                    CREATE TABLE IF NOT EXISTS test_migration_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''',
                'rollback_sql': 'DROP TABLE IF EXISTS test_migration_table;'
            },
            {
                'name': 'add_test_index',
                'sql': 'CREATE INDEX IF NOT EXISTS test_migration_table_name_idx ON test_migration_table (name);',
                'rollback_sql': 'DROP INDEX IF EXISTS test_migration_table_name_idx;'
            },
            {
                'name': 'insert_test_data',
                'sql': '''
                    INSERT INTO test_migration_table (name) 
                    SELECT 'test_' || generate_series(1, 1000);
                ''',
                'rollback_sql': 'DELETE FROM test_migration_table WHERE name LIKE 'test_%';'
            }
        ]
        
        for migration in test_migrations:
            start_time = time.time()
            
            try:
                with connection.cursor() as cursor:
                    cursor.execute(migration['sql'])
                
                execution_time = time.time() - start_time
                
                # Get database statistics
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
                    db_size = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT count(*) FROM test_migration_table;")
                    record_count = cursor.fetchone()[0]
                
                migration_result = {
                    'name': migration['name'],
                    'execution_time': execution_time,
                    'database_size': db_size,
                    'record_count': record_count,
                    'status': 'success',
                    'timestamp': timezone.now().isoformat()
                }
                
                # Rollback the migration
                with connection.cursor() as cursor:
                    cursor.execute(migration['rollback_sql'])
                
                monitoring_data['migrations_tested'].append(migration_result)
                
                self.stdout.write(
                    f"✓ {migration['name']}: {execution_time:.3f}s"
                )
                
            except Exception as e:
                migration_result = {
                    'name': migration['name'],
                    'execution_time': 0,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                }
                
                monitoring_data['migrations_tested'].append(migration_result)
                
                self.stdout.write(
                    self.style.ERROR(f"✗ {migration['name']}: {e}")
                )
    
    def _monitor_migration_performance(self, monitoring_data, duration, interval):
        """Monitor migration performance for specified duration."""
        self.stdout.write(f"Monitoring migration performance for {duration} seconds...")
        
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time:
            current_time = timezone.now()
            
            # Collect current metrics
            metrics = self._collect_migration_metrics()
            metrics['timestamp'] = current_time.isoformat()
            metrics['elapsed_time'] = time.time() - start_time
            
            monitoring_data['metrics'].append(metrics)
            
            # Display current status
            self.stdout.write(
                f"Time: {metrics['elapsed_time']:.1f}s | "
                f"Active Migrations: {metrics['active_migrations']} | "
                f"DB Connections: {metrics['db_connections']} | "
                f"DB Size: {metrics['db_size']}"
            )
            
            # Wait for next interval
            time.sleep(interval)
        
        # Calculate performance summary
        self._calculate_performance_summary(monitoring_data)
    
    def _collect_migration_metrics(self):
        """Collect current migration performance metrics."""
        try:
            with connection.cursor() as cursor:
                # Get active migrations
                cursor.execute("""
                    SELECT count(*) FROM django_migrations 
                    WHERE applied IS NOT NULL;
                """)
                applied_migrations = cursor.fetchone()[0]
                
                # Get database connections
                cursor.execute("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE datname = current_database();
                """)
                db_connections = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
                db_size = cursor.fetchone()[0]
                
                # Get table count
                cursor.execute("""
                    SELECT count(*) FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                table_count = cursor.fetchone()[0]
                
                # Get index count
                cursor.execute("""
                    SELECT count(*) FROM pg_indexes 
                    WHERE schemaname = 'public';
                """)
                index_count = cursor.fetchone()[0]
                
                # Get recent migration activity
                cursor.execute("""
                    SELECT count(*) FROM django_migrations 
                    WHERE applied > NOW() - INTERVAL '1 hour';
                """)
                recent_migrations = cursor.fetchone()[0]
                
                return {
                    'active_migrations': applied_migrations,
                    'db_connections': db_connections,
                    'db_size': db_size,
                    'table_count': table_count,
                    'index_count': index_count,
                    'recent_migrations': recent_migrations,
                    'timestamp': timezone.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error collecting migration metrics: {e}")
            return {
                'active_migrations': 0,
                'db_connections': 0,
                'db_size': 'Unknown',
                'table_count': 0,
                'index_count': 0,
                'recent_migrations': 0,
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    def _calculate_performance_summary(self, monitoring_data):
        """Calculate performance summary from collected metrics."""
        if not monitoring_data['metrics']:
            return
        
        metrics = monitoring_data['metrics']
        
        # Calculate averages and trends
        db_connections = [m.get('db_connections', 0) for m in metrics]
        table_counts = [m.get('table_count', 0) for m in metrics]
        index_counts = [m.get('index_count', 0) for m in metrics]
        
        summary = {
            'monitoring_duration': monitoring_data['duration'],
            'total_measurements': len(metrics),
            'average_db_connections': sum(db_connections) / len(db_connections) if db_connections else 0,
            'max_db_connections': max(db_connections) if db_connections else 0,
            'min_db_connections': min(db_connections) if db_connections else 0,
            'average_table_count': sum(table_counts) / len(table_counts) if table_counts else 0,
            'average_index_count': sum(index_counts) / len(index_counts) if index_counts else 0,
            'migration_tests_performed': len(monitoring_data['migrations_tested']),
            'successful_migration_tests': len([m for m in monitoring_data['migrations_tested'] if m.get('status') == 'success']),
            'failed_migration_tests': len([m for m in monitoring_data['migrations_tested'] if m.get('status') == 'failed']),
        }
        
        # Calculate migration test performance
        successful_tests = [m for m in monitoring_data['migrations_tested'] if m.get('status') == 'success']
        if successful_tests:
            execution_times = [m.get('execution_time', 0) for m in successful_tests]
            summary.update({
                'average_migration_time': sum(execution_times) / len(execution_times),
                'fastest_migration_time': min(execution_times),
                'slowest_migration_time': max(execution_times),
            })
        
        monitoring_data['performance_summary'] = summary
    
    def _generate_performance_report(self, monitoring_data, output_file):
        """Generate comprehensive performance report."""
        self.stdout.write("Generating performance report...")
        
        # Add end time
        monitoring_data['end_time'] = timezone.now().isoformat()
        
        # Write report to file
        with open(output_file, 'w') as f:
            json.dump(monitoring_data, f, indent=2)
        
        # Display summary
        summary = monitoring_data['performance_summary']
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("MIGRATION PERFORMANCE REPORT")
        self.stdout.write("="*60)
        
        self.stdout.write(f"\nMonitoring Duration: {summary['monitoring_duration']} seconds")
        self.stdout.write(f"Total Measurements: {summary['total_measurements']}")
        
        self.stdout.write(f"\nDatabase Performance:")
        self.stdout.write(f"- Average Connections: {summary['average_db_connections']:.1f}")
        self.stdout.write(f"- Max Connections: {summary['max_db_connections']}")
        self.stdout.write(f"- Min Connections: {summary['min_db_connections']}")
        
        self.stdout.write(f"\nDatabase Structure:")
        self.stdout.write(f"- Average Tables: {summary['average_table_count']:.1f}")
        self.stdout.write(f"- Average Indexes: {summary['average_index_count']:.1f}")
        
        if summary['migration_tests_performed'] > 0:
            self.stdout.write(f"\nMigration Test Results:")
            self.stdout.write(f"- Tests Performed: {summary['migration_tests_performed']}")
            self.stdout.write(f"- Successful: {summary['successful_migration_tests']}")
            self.stdout.write(f"- Failed: {summary['failed_migration_tests']}")
            
            if 'average_migration_time' in summary:
                self.stdout.write(f"- Average Time: {summary['average_migration_time']:.3f}s")
                self.stdout.write(f"- Fastest: {summary['fastest_migration_time']:.3f}s")
                self.stdout.write(f"- Slowest: {summary['slowest_migration_time']:.3f}s")
        
        self.stdout.write("="*60)
        
        # Generate recommendations
        self._generate_recommendations(summary)
    
    def _generate_recommendations(self, summary):
        """Generate performance recommendations."""
        recommendations = []
        
        # Database connection recommendations
        if summary['average_db_connections'] > 50:
            recommendations.append("Consider optimizing database connection pooling - high connection usage detected")
        
        if summary['max_db_connections'] > 80:
            recommendations.append("Monitor for connection leaks - maximum connections exceeded 80")
        
        # Migration performance recommendations
        if 'average_migration_time' in summary:
            if summary['average_migration_time'] > 5.0:
                recommendations.append("Consider optimizing migration performance - average time exceeds 5 seconds")
            
            if summary['slowest_migration_time'] > 10.0:
                recommendations.append("Review slowest migrations for optimization opportunities")
        
        # Test results recommendations
        if summary['failed_migration_tests'] > 0:
            recommendations.append("Address failed migration tests to ensure system stability")
        
        if summary['successful_migration_tests'] == 0 and summary['migration_tests_performed'] > 0:
            recommendations.append("Investigate migration test failures - no successful tests")
        
        # Display recommendations
        if recommendations:
            self.stdout.write("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                self.stdout.write(f"{i}. {rec}")
        else:
            self.stdout.write("\nNo specific recommendations at this time.")
        
        self.stdout.write("="*60)
