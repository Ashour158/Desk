"""
Database management utilities for advanced features.
"""

from django.db import connection
from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Advanced database management utilities.
    """
    
    @staticmethod
    def refresh_materialized_views():
        """Refresh all materialized views."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT refresh_dashboard_views();")
            logger.info("Materialized views refreshed successfully")
    
    @staticmethod
    def refresh_organization_views(organization_id):
        """Refresh materialized views for specific organization."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT refresh_organization_views(%s);", [organization_id])
            logger.info(f"Materialized views refreshed for organization {organization_id}")
    
    @staticmethod
    def create_monthly_partition(table_name, partition_date):
        """Create new monthly partition for partitioned tables."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT create_monthly_partition(%s, %s);", [table_name, partition_date])
            logger.info(f"Monthly partition created for {table_name} on {partition_date}")
    
    @staticmethod
    def create_hash_partition(table_name, partition_count):
        """Create new hash partitions for partitioned tables."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT create_hash_partition(%s, %s);", [table_name, partition_count])
            logger.info(f"Hash partitions created for {table_name} with {partition_count} partitions")
    
    @staticmethod
    def drop_old_partitions(table_name, retention_months=12):
        """Drop old partitions beyond retention period."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT drop_old_partitions(%s, %s);", [table_name, retention_months])
            logger.info(f"Old partitions dropped for {table_name} (retention: {retention_months} months)")
    
    @staticmethod
    def get_partition_info(table_name):
        """Get information about table partitions."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE tablename LIKE %s || '_%'
                ORDER BY tablename;
            """, [table_name])
            return cursor.fetchall()
    
    @staticmethod
    def get_materialized_view_info():
        """Get information about materialized views."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    matviewname,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size,
                    definition
                FROM pg_matviews 
                WHERE schemaname = 'public'
                ORDER BY matviewname;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def get_index_usage_stats():
        """Get index usage statistics."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def get_table_size_info():
        """Get table size information."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def get_fulltext_search_stats():
        """Get full-text search index statistics."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) as size
                FROM pg_indexes 
                WHERE indexname LIKE '%fulltext%'
                ORDER BY pg_relation_size(schemaname||'.'||indexname) DESC;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def analyze_tables():
        """Run ANALYZE on all tables for updated statistics."""
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE;")
            logger.info("Table statistics updated")
    
    @staticmethod
    def vacuum_tables():
        """Run VACUUM on all tables for maintenance."""
        with connection.cursor() as cursor:
            cursor.execute("VACUUM ANALYZE;")
            logger.info("Table vacuum completed")
    
    @staticmethod
    def get_database_performance_stats():
        """Get comprehensive database performance statistics."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    'Database Size' as metric,
                    pg_size_pretty(pg_database_size(current_database())) as value
                UNION ALL
                SELECT 
                    'Total Tables' as metric,
                    count(*)::text as value
                FROM pg_tables WHERE schemaname = 'public'
                UNION ALL
                SELECT 
                    'Total Indexes' as metric,
                    count(*)::text as value
                FROM pg_indexes WHERE schemaname = 'public'
                UNION ALL
                SELECT 
                    'Total Materialized Views' as metric,
                    count(*)::text as value
                FROM pg_matviews WHERE schemaname = 'public'
                UNION ALL
                SELECT 
                    'Active Connections' as metric,
                    count(*)::text as value
                FROM pg_stat_activity WHERE state = 'active'
                ORDER BY metric;
            """)
            return cursor.fetchall()


class DatabaseMaintenanceCommand(BaseCommand):
    """
    Django management command for database maintenance.
    """
    
    help = 'Perform database maintenance tasks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--refresh-views',
            action='store_true',
            help='Refresh materialized views'
        )
        parser.add_argument(
            '--create-partitions',
            action='store_true',
            help='Create new partitions for partitioned tables'
        )
        parser.add_argument(
            '--drop-old-partitions',
            action='store_true',
            help='Drop old partitions beyond retention period'
        )
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Run ANALYZE on all tables'
        )
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Run VACUUM on all tables'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show database statistics'
        )
        parser.add_argument(
            '--organization-id',
            type=int,
            help='Organization ID for organization-specific operations'
        )
        parser.add_argument(
            '--retention-months',
            type=int,
            default=12,
            help='Retention period in months for partition cleanup'
        )
    
    def handle(self, *args, **options):
        """Handle the maintenance command."""
        db_manager = DatabaseManager()
        
        if options['refresh_views']:
            if options['organization_id']:
                db_manager.refresh_organization_views(options['organization_id'])
                self.stdout.write(
                    self.style.SUCCESS(f'Materialized views refreshed for organization {options["organization_id"]}')
                )
            else:
                db_manager.refresh_materialized_views()
                self.stdout.write(
                    self.style.SUCCESS('All materialized views refreshed')
                )
        
        if options['create_partitions']:
            # Create partitions for the next month
            from datetime import date, timedelta
            next_month = date.today() + timedelta(days=30)
            
            db_manager.create_monthly_partition('tickets_tickethistory_partitioned', next_month)
            db_manager.create_monthly_partition('tickets_ticketcomment_partitioned', next_month)
            db_manager.create_monthly_partition('accounts_usersession_partitioned', next_month)
            
            self.stdout.write(
                self.style.SUCCESS('New partitions created for next month')
            )
        
        if options['drop_old_partitions']:
            retention_months = options['retention_months']
            
            db_manager.drop_old_partitions('tickets_tickethistory_partitioned', retention_months)
            db_manager.drop_old_partitions('tickets_ticketcomment_partitioned', retention_months)
            db_manager.drop_old_partitions('accounts_usersession_partitioned', retention_months)
            
            self.stdout.write(
                self.style.SUCCESS(f'Old partitions dropped (retention: {retention_months} months)')
            )
        
        if options['analyze']:
            db_manager.analyze_tables()
            self.stdout.write(
                self.style.SUCCESS('Table statistics updated')
            )
        
        if options['vacuum']:
            db_manager.vacuum_tables()
            self.stdout.write(
                self.style.SUCCESS('Table vacuum completed')
            )
        
        if options['stats']:
            self.show_database_stats(db_manager)
    
    def show_database_stats(self, db_manager):
        """Show comprehensive database statistics."""
        self.stdout.write(self.style.SUCCESS('\n=== Database Performance Statistics ==='))
        
        # General performance stats
        perf_stats = db_manager.get_database_performance_stats()
        for metric, value in perf_stats:
            self.stdout.write(f'{metric}: {value}')
        
        # Table size information
        self.stdout.write(self.style.SUCCESS('\n=== Table Size Information ==='))
        table_sizes = db_manager.get_table_size_info()
        for schema, table, size, table_size, index_size in table_sizes[:10]:  # Top 10
            self.stdout.write(f'{table}: {size} (table: {table_size}, indexes: {index_size})')
        
        # Index usage statistics
        self.stdout.write(self.style.SUCCESS('\n=== Index Usage Statistics ==='))
        index_stats = db_manager.get_index_usage_stats()
        for schema, table, index, scans, reads, fetches in index_stats[:10]:  # Top 10
            self.stdout.write(f'{index}: {scans} scans, {reads} reads, {fetches} fetches')
        
        # Materialized view information
        self.stdout.write(self.style.SUCCESS('\n=== Materialized Views ==='))
        mv_info = db_manager.get_materialized_view_info()
        for schema, view, size, definition in mv_info:
            self.stdout.write(f'{view}: {size}')
        
        # Full-text search statistics
        self.stdout.write(self.style.SUCCESS('\n=== Full-Text Search Indexes ==='))
        ft_stats = db_manager.get_fulltext_search_stats()
        for schema, table, index, size in ft_stats:
            self.stdout.write(f'{index}: {size}')


# Export utilities
__all__ = [
    'DatabaseManager',
    'DatabaseMaintenanceCommand'
]
