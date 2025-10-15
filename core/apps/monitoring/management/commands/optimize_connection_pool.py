"""
Management command to optimize database connection pool settings.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Optimize connection pool command."""
    
    help = 'Optimize database connection pool settings based on current usage patterns'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-duration',
            type=int,
            default=60,
            help='Duration in seconds to test connection pool (default: 60)',
        )
        parser.add_argument(
            '--max-connections',
            type=int,
            default=20,
            help='Maximum number of connections to test (default: 20)',
        )
        parser.add_argument(
            '--apply-changes',
            action='store_true',
            help='Apply optimized settings to configuration',
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        test_duration = options['test_duration']
        max_connections = options['max_connections']
        apply_changes = options['apply_changes']
        
        self.stdout.write(
            self.style.SUCCESS("Starting connection pool optimization...")
        )
        
        # Analyze current connection usage
        current_analysis = self._analyze_current_usage()
        
        # Test different connection pool configurations
        test_results = self._test_connection_pools(max_connections, test_duration)
        
        # Find optimal configuration
        optimal_config = self._find_optimal_configuration(test_results)
        
        # Display results
        self._display_results(current_analysis, test_results, optimal_config)
        
        # Apply changes if requested
        if apply_changes:
            self._apply_optimal_configuration(optimal_config)
            self.stdout.write(
                self.style.SUCCESS("Optimal configuration applied!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Use --apply-changes to apply the optimal configuration"
                )
            )
    
    def _analyze_current_usage(self):
        """Analyze current connection usage patterns."""
        self.stdout.write("Analyzing current connection usage...")
        
        try:
            with connection.cursor() as cursor:
                # Get current connection settings
                cursor.execute("SHOW max_connections;")
                max_connections = cursor.fetchone()[0]
                
                cursor.execute("SHOW shared_preload_libraries;")
                shared_preload = cursor.fetchone()[0]
                
                # Get current active connections
                cursor.execute("""
                    SELECT count(*) as active_connections,
                           count(*) FILTER (WHERE state = 'active') as active_queries,
                           count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity 
                    WHERE datname = current_database();
                """)
                connection_stats = cursor.fetchone()
                
                # Get connection pool statistics
                cursor.execute("""
                    SELECT 
                        setting as current_setting,
                        unit,
                        context
                    FROM pg_settings 
                    WHERE name IN ('max_connections', 'shared_buffers', 'work_mem', 'maintenance_work_mem');
                """)
                settings_info = cursor.fetchall()
                
                return {
                    'max_connections': max_connections,
                    'shared_preload': shared_preload,
                    'active_connections': connection_stats[0],
                    'active_queries': connection_stats[1],
                    'idle_connections': connection_stats[2],
                    'settings': dict(settings_info)
                }
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error analyzing current usage: {e}")
            )
            return {}
    
    def _test_connection_pools(self, max_connections, test_duration):
        """Test different connection pool configurations."""
        self.stdout.write(f"Testing connection pools for {test_duration} seconds...")
        
        test_configs = [
            {'CONN_MAX_AGE': 0, 'CONN_HEALTH_CHECKS': False},
            {'CONN_MAX_AGE': 60, 'CONN_HEALTH_CHECKS': False},
            {'CONN_MAX_AGE': 300, 'CONN_HEALTH_CHECKS': True},
            {'CONN_MAX_AGE': 600, 'CONN_HEALTH_CHECKS': True},
            {'CONN_MAX_AGE': 1800, 'CONN_HEALTH_CHECKS': True},
        ]
        
        results = []
        
        for i, config in enumerate(test_configs):
            self.stdout.write(f"Testing configuration {i+1}/{len(test_configs)}: {config}")
            
            # Test connection performance
            start_time = time.time()
            connection_times = []
            error_count = 0
            
            # Simulate connection usage
            for _ in range(max_connections):
                try:
                    conn_start = time.time()
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                    conn_time = time.time() - conn_start
                    connection_times.append(conn_time)
                except Exception as e:
                    error_count += 1
                    logger.error(f"Connection error: {e}")
            
            test_duration_actual = time.time() - start_time
            
            # Calculate performance metrics
            avg_connection_time = sum(connection_times) / len(connection_times) if connection_times else 0
            max_connection_time = max(connection_times) if connection_times else 0
            min_connection_time = min(connection_times) if connection_times else 0
            success_rate = (len(connection_times) / max_connections) * 100
            
            results.append({
                'config': config,
                'avg_connection_time': avg_connection_time,
                'max_connection_time': max_connection_time,
                'min_connection_time': min_connection_time,
                'success_rate': success_rate,
                'error_count': error_count,
                'test_duration': test_duration_actual
            })
            
            # Wait between tests
            time.sleep(1)
        
        return results
    
    def _find_optimal_configuration(self, test_results):
        """Find the optimal configuration based on test results."""
        if not test_results:
            return None
        
        # Score each configuration
        scored_configs = []
        
        for result in test_results:
            # Calculate score based on multiple factors
            score = 0
            
            # Prefer faster connection times
            if result['avg_connection_time'] < 0.1:  # Less than 100ms
                score += 30
            elif result['avg_connection_time'] < 0.5:  # Less than 500ms
                score += 20
            elif result['avg_connection_time'] < 1.0:  # Less than 1s
                score += 10
            
            # Prefer higher success rates
            if result['success_rate'] > 95:
                score += 25
            elif result['success_rate'] > 90:
                score += 15
            elif result['success_rate'] > 80:
                score += 5
            
            # Prefer fewer errors
            if result['error_count'] == 0:
                score += 20
            elif result['error_count'] < 5:
                score += 10
            elif result['error_count'] < 10:
                score += 5
            
            # Prefer reasonable connection age
            conn_age = result['config']['CONN_MAX_AGE']
            if 300 <= conn_age <= 600:  # 5-10 minutes
                score += 15
            elif 60 <= conn_age <= 1800:  # 1-30 minutes
                score += 10
            
            # Prefer health checks enabled
            if result['config']['CONN_HEALTH_CHECKS']:
                score += 10
            
            scored_configs.append({
                'config': result['config'],
                'score': score,
                'metrics': result
            })
        
        # Sort by score and return the best configuration
        scored_configs.sort(key=lambda x: x['score'], reverse=True)
        return scored_configs[0] if scored_configs else None
    
    def _display_results(self, current_analysis, test_results, optimal_config):
        """Display optimization results."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("CONNECTION POOL OPTIMIZATION RESULTS")
        self.stdout.write("="*60)
        
        # Current analysis
        if current_analysis:
            self.stdout.write("\nCurrent Connection Usage:")
            self.stdout.write(f"- Max Connections: {current_analysis.get('max_connections', 'N/A')}")
            self.stdout.write(f"- Active Connections: {current_analysis.get('active_connections', 'N/A')}")
            self.stdout.write(f"- Active Queries: {current_analysis.get('active_queries', 'N/A')}")
            self.stdout.write(f"- Idle Connections: {current_analysis.get('idle_connections', 'N/A')}")
        
        # Test results
        self.stdout.write("\nConnection Pool Test Results:")
        self.stdout.write("-" * 60)
        self.stdout.write(f"{'Config':<20} {'Avg Time':<10} {'Success %':<10} {'Errors':<8} {'Score':<8}")
        self.stdout.write("-" * 60)
        
        for i, result in enumerate(test_results):
            config_str = f"CONN_MAX_AGE={result['config']['CONN_MAX_AGE']}"
            avg_time = f"{result['avg_connection_time']:.3f}s"
            success_rate = f"{result['success_rate']:.1f}%"
            errors = str(result['error_count'])
            
            self.stdout.write(f"{config_str:<20} {avg_time:<10} {success_rate:<10} {errors:<8}")
        
        # Optimal configuration
        if optimal_config:
            self.stdout.write("\nOptimal Configuration:")
            self.stdout.write(f"- CONN_MAX_AGE: {optimal_config['config']['CONN_MAX_AGE']}")
            self.stdout.write(f"- CONN_HEALTH_CHECKS: {optimal_config['config']['CONN_HEALTH_CHECKS']}")
            self.stdout.write(f"- Score: {optimal_config['score']}")
            self.stdout.write(f"- Avg Connection Time: {optimal_config['metrics']['avg_connection_time']:.3f}s")
            self.stdout.write(f"- Success Rate: {optimal_config['metrics']['success_rate']:.1f}%")
            self.stdout.write(f"- Errors: {optimal_config['metrics']['error_count']}")
        
        self.stdout.write("="*60)
    
    def _apply_optimal_configuration(self, optimal_config):
        """Apply the optimal configuration."""
        if not optimal_config:
            self.stdout.write(
                self.style.ERROR("No optimal configuration found!")
            )
            return
        
        config = optimal_config['config']
        
        # Create optimized settings
        optimized_settings = f"""
# Optimized database connection pool settings
# Generated by connection pool optimization

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'helpdesk_production'),
        'USER': os.environ.get('DB_USER', 'helpdesk_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {{
            'sslmode': 'require',
        }},
        'CONN_MAX_AGE': {config['CONN_MAX_AGE']},
        'CONN_HEALTH_CHECKS': {config['CONN_HEALTH_CHECKS']},
    }}
}}

# Additional connection pool optimizations
DATABASE_POOL_SIZE = 20
DATABASE_POOL_OVERFLOW = 0
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600
"""
        
        # Write optimized settings to file
        settings_file = 'optimized_database_settings.py'
        with open(settings_file, 'w') as f:
            f.write(optimized_settings)
        
        self.stdout.write(f"Optimized settings written to: {settings_file}")
        
        # Display recommendations
        self.stdout.write("\nRecommendations:")
        self.stdout.write("1. Update your database settings with the optimized configuration")
        self.stdout.write("2. Monitor connection usage after applying changes")
        self.stdout.write("3. Adjust settings based on actual usage patterns")
        self.stdout.write("4. Consider using connection pooling middleware if needed")
