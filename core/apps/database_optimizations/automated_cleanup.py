"""
Automated data cleanup processes for maintaining data integrity.
"""

from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AutomatedDataCleanup:
    """
    Automated data cleanup utilities for maintaining data integrity.
    """
    
    def __init__(self):
        self.cleanup_stats = {
            'orphaned_records_removed': 0,
            'duplicate_records_removed': 0,
            'null_values_fixed': 0,
            'invalid_enums_fixed': 0,
            'timestamp_issues_fixed': 0,
            'data_inconsistencies_fixed': 0
        }
    
    def cleanup_orphaned_records(self, dry_run=False):
        """
        Clean up orphaned records across all tables.
        """
        logger.info("Starting orphaned records cleanup...")
        
        with connection.cursor() as cursor:
            # Clean up orphaned tickets
            if not dry_run:
                cursor.execute("""
                    DELETE FROM tickets_ticket 
                    WHERE organization_id NOT IN (SELECT id FROM organizations_organization);
                """)
                orphaned_tickets = cursor.rowcount
                self.cleanup_stats['orphaned_records_removed'] += orphaned_tickets
                logger.info(f"Removed {orphaned_tickets} orphaned tickets")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticket 
                    WHERE organization_id NOT IN (SELECT id FROM organizations_organization);
                """)
                orphaned_tickets = cursor.fetchone()[0]
                logger.info(f"Would remove {orphaned_tickets} orphaned tickets")
            
            # Clean up orphaned comments
            if not dry_run:
                cursor.execute("""
                    DELETE FROM tickets_ticketcomment 
                    WHERE ticket_id NOT IN (SELECT id FROM tickets_ticket);
                """)
                orphaned_comments = cursor.rowcount
                self.cleanup_stats['orphaned_records_removed'] += orphaned_comments
                logger.info(f"Removed {orphaned_comments} orphaned comments")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticketcomment 
                    WHERE ticket_id NOT IN (SELECT id FROM tickets_ticket);
                """)
                orphaned_comments = cursor.fetchone()[0]
                logger.info(f"Would remove {orphaned_comments} orphaned comments")
            
            # Clean up orphaned attachments
            if not dry_run:
                cursor.execute("""
                    DELETE FROM tickets_ticketattachment 
                    WHERE ticket_id NOT IN (SELECT id FROM tickets_ticket);
                """)
                orphaned_attachments = cursor.rowcount
                self.cleanup_stats['orphaned_records_removed'] += orphaned_attachments
                logger.info(f"Removed {orphaned_attachments} orphaned attachments")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticketattachment 
                    WHERE ticket_id NOT IN (SELECT id FROM tickets_ticket);
                """)
                orphaned_attachments = cursor.fetchone()[0]
                logger.info(f"Would remove {orphaned_attachments} orphaned attachments")
            
            # Clean up orphaned sessions
            if not dry_run:
                cursor.execute("""
                    DELETE FROM accounts_usersession 
                    WHERE user_id NOT IN (SELECT id FROM accounts_user);
                """)
                orphaned_sessions = cursor.rowcount
                self.cleanup_stats['orphaned_records_removed'] += orphaned_sessions
                logger.info(f"Removed {orphaned_sessions} orphaned sessions")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM accounts_usersession 
                    WHERE user_id NOT IN (SELECT id FROM accounts_user);
                """)
                orphaned_sessions = cursor.fetchone()[0]
                logger.info(f"Would remove {orphaned_sessions} orphaned sessions")
    
    def cleanup_duplicate_records(self, dry_run=False):
        """
        Clean up duplicate records across all tables.
        """
        logger.info("Starting duplicate records cleanup...")
        
        with connection.cursor() as cursor:
            # Clean up duplicate ticket numbers
            if not dry_run:
                cursor.execute("""
                    DELETE FROM tickets_ticket 
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM tickets_ticket 
                        GROUP BY ticket_number
                    );
                """)
                duplicate_tickets = cursor.rowcount
                self.cleanup_stats['duplicate_records_removed'] += duplicate_tickets
                logger.info(f"Removed {duplicate_tickets} duplicate tickets")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticket 
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM tickets_ticket 
                        GROUP BY ticket_number
                    );
                """)
                duplicate_tickets = cursor.fetchone()[0]
                logger.info(f"Would remove {duplicate_tickets} duplicate tickets")
            
            # Clean up duplicate session keys
            if not dry_run:
                cursor.execute("""
                    DELETE FROM accounts_usersession 
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM accounts_usersession 
                        GROUP BY session_key
                    );
                """)
                duplicate_sessions = cursor.rowcount
                self.cleanup_stats['duplicate_records_removed'] += duplicate_sessions
                logger.info(f"Removed {duplicate_sessions} duplicate sessions")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM accounts_usersession 
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM accounts_usersession 
                        GROUP BY session_key
                    );
                """)
                duplicate_sessions = cursor.fetchone()[0]
                logger.info(f"Would remove {duplicate_sessions} duplicate sessions")
    
    def fix_null_values(self, dry_run=False):
        """
        Fix NULL values in required fields.
        """
        logger.info("Starting NULL values fix...")
        
        with connection.cursor() as cursor:
            # Fix NULL ticket subjects
            if not dry_run:
                cursor.execute("""
                    UPDATE tickets_ticket 
                    SET subject = 'No Subject' 
                    WHERE subject IS NULL OR subject = '';
                """)
                null_subjects = cursor.rowcount
                self.cleanup_stats['null_values_fixed'] += null_subjects
                logger.info(f"Fixed {null_subjects} NULL ticket subjects")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticket 
                    WHERE subject IS NULL OR subject = '';
                """)
                null_subjects = cursor.fetchone()[0]
                logger.info(f"Would fix {null_subjects} NULL ticket subjects")
            
            # Fix NULL ticket descriptions
            if not dry_run:
                cursor.execute("""
                    UPDATE tickets_ticket 
                    SET description = 'No Description' 
                    WHERE description IS NULL OR description = '';
                """)
                null_descriptions = cursor.rowcount
                self.cleanup_stats['null_values_fixed'] += null_descriptions
                logger.info(f"Fixed {null_descriptions} NULL ticket descriptions")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticket 
                    WHERE description IS NULL OR description = '';
                """)
                null_descriptions = cursor.fetchone()[0]
                logger.info(f"Would fix {null_descriptions} NULL ticket descriptions")
            
            # Fix NULL user emails
            if not dry_run:
                cursor.execute("""
                    UPDATE accounts_user 
                    SET email = CONCAT('user_', id, '@example.com') 
                    WHERE email IS NULL OR email = '';
                """)
                null_emails = cursor.rowcount
                self.cleanup_stats['null_values_fixed'] += null_emails
                logger.info(f"Fixed {null_emails} NULL user emails")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM accounts_user 
                    WHERE email IS NULL OR email = '';
                """)
                null_emails = cursor.fetchone()[0]
                logger.info(f"Would fix {null_emails} NULL user emails")
    
    def fix_invalid_enum_values(self, dry_run=False):
        """
        Fix invalid enum values.
        """
        logger.info("Starting invalid enum values fix...")
        
        with connection.cursor() as cursor:
            # Fix invalid ticket statuses
            if not dry_run:
                cursor.execute("""
                    UPDATE tickets_ticket 
                    SET status = 'new' 
                    WHERE status NOT IN ('new', 'open', 'pending', 'resolved', 'closed', 'cancelled');
                """)
                invalid_statuses = cursor.rowcount
                self.cleanup_stats['invalid_enums_fixed'] += invalid_statuses
                logger.info(f"Fixed {invalid_statuses} invalid ticket statuses")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticket 
                    WHERE status NOT IN ('new', 'open', 'pending', 'resolved', 'closed', 'cancelled');
                """)
                invalid_statuses = cursor.fetchone()[0]
                logger.info(f"Would fix {invalid_statuses} invalid ticket statuses")
            
            # Fix invalid user roles
            if not dry_run:
                cursor.execute("""
                    UPDATE accounts_user 
                    SET role = 'customer' 
                    WHERE role NOT IN ('admin', 'manager', 'agent', 'customer');
                """)
                invalid_roles = cursor.rowcount
                self.cleanup_stats['invalid_enums_fixed'] += invalid_roles
                logger.info(f"Fixed {invalid_roles} invalid user roles")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM accounts_user 
                    WHERE role NOT IN ('admin', 'manager', 'agent', 'customer');
                """)
                invalid_roles = cursor.fetchone()[0]
                logger.info(f"Would fix {invalid_roles} invalid user roles")
    
    def fix_timestamp_issues(self, dry_run=False):
        """
        Fix timestamp consistency issues.
        """
        logger.info("Starting timestamp issues fix...")
        
        with connection.cursor() as cursor:
            # Fix tickets where updated_at is before created_at
            if not dry_run:
                cursor.execute("""
                    UPDATE tickets_ticket 
                    SET updated_at = created_at 
                    WHERE updated_at < created_at;
                """)
                timestamp_issues = cursor.rowcount
                self.cleanup_stats['timestamp_issues_fixed'] += timestamp_issues
                logger.info(f"Fixed {timestamp_issues} timestamp issues")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticket 
                    WHERE updated_at < created_at;
                """)
                timestamp_issues = cursor.fetchone()[0]
                logger.info(f"Would fix {timestamp_issues} timestamp issues")
    
    def fix_data_inconsistencies(self, dry_run=False):
        """
        Fix data inconsistencies.
        """
        logger.info("Starting data inconsistencies fix...")
        
        with connection.cursor() as cursor:
            # Fix invalid satisfaction scores
            if not dry_run:
                cursor.execute("""
                    UPDATE tickets_ticket 
                    SET customer_satisfaction_score = 3 
                    WHERE customer_satisfaction_score IS NOT NULL 
                    AND (customer_satisfaction_score < 1 OR customer_satisfaction_score > 5);
                """)
                invalid_scores = cursor.rowcount
                self.cleanup_stats['data_inconsistencies_fixed'] += invalid_scores
                logger.info(f"Fixed {invalid_scores} invalid satisfaction scores")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticket 
                    WHERE customer_satisfaction_score IS NOT NULL 
                    AND (customer_satisfaction_score < 1 OR customer_satisfaction_score > 5);
                """)
                invalid_scores = cursor.fetchone()[0]
                logger.info(f"Would fix {invalid_scores} invalid satisfaction scores")
            
            # Fix invalid file sizes
            if not dry_run:
                cursor.execute("""
                    UPDATE tickets_ticketattachment 
                    SET file_size = 1024 
                    WHERE file_size <= 0;
                """)
                invalid_sizes = cursor.rowcount
                self.cleanup_stats['data_inconsistencies_fixed'] += invalid_sizes
                logger.info(f"Fixed {invalid_sizes} invalid file sizes")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM tickets_ticketattachment 
                    WHERE file_size <= 0;
                """)
                invalid_sizes = cursor.fetchone()[0]
                logger.info(f"Would fix {invalid_sizes} invalid file sizes")
    
    def run_comprehensive_cleanup(self, dry_run=False):
        """
        Run comprehensive data cleanup.
        """
        logger.info(f"Starting comprehensive data cleanup (dry_run={dry_run})...")
        
        with transaction.atomic():
            self.cleanup_orphaned_records(dry_run)
            self.cleanup_duplicate_records(dry_run)
            self.fix_null_values(dry_run)
            self.fix_invalid_enum_values(dry_run)
            self.fix_timestamp_issues(dry_run)
            self.fix_data_inconsistencies(dry_run)
        
        logger.info("Comprehensive data cleanup completed")
        logger.info(f"Cleanup statistics: {self.cleanup_stats}")
        
        return self.cleanup_stats


class DataCleanupCommand(BaseCommand):
    """
    Django management command for automated data cleanup.
    """
    
    help = 'Run automated data cleanup processes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without making changes'
        )
        parser.add_argument(
            '--orphaned-only',
            action='store_true',
            help='Only clean up orphaned records'
        )
        parser.add_argument(
            '--duplicates-only',
            action='store_true',
            help='Only clean up duplicate records'
        )
        parser.add_argument(
            '--nulls-only',
            action='store_true',
            help='Only fix NULL values'
        )
        parser.add_argument(
            '--enums-only',
            action='store_true',
            help='Only fix invalid enum values'
        )
        parser.add_argument(
            '--timestamps-only',
            action='store_true',
            help='Only fix timestamp issues'
        )
        parser.add_argument(
            '--inconsistencies-only',
            action='store_true',
            help='Only fix data inconsistencies'
        )
    
    def handle(self, *args, **options):
        """Handle the data cleanup command."""
        cleanup = AutomatedDataCleanup()
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN: No changes will be made"))
        
        if options['orphaned_only']:
            cleanup.cleanup_orphaned_records(dry_run)
        elif options['duplicates_only']:
            cleanup.cleanup_duplicate_records(dry_run)
        elif options['nulls_only']:
            cleanup.fix_null_values(dry_run)
        elif options['enums_only']:
            cleanup.fix_invalid_enum_values(dry_run)
        elif options['timestamps_only']:
            cleanup.fix_timestamp_issues(dry_run)
        elif options['inconsistencies_only']:
            cleanup.fix_data_inconsistencies(dry_run)
        else:
            # Run comprehensive cleanup
            stats = cleanup.run_comprehensive_cleanup(dry_run)
            
            self.stdout.write(self.style.SUCCESS("Data cleanup completed"))
            self.stdout.write(f"Orphaned records removed: {stats['orphaned_records_removed']}")
            self.stdout.write(f"Duplicate records removed: {stats['duplicate_records_removed']}")
            self.stdout.write(f"NULL values fixed: {stats['null_values_fixed']}")
            self.stdout.write(f"Invalid enums fixed: {stats['invalid_enums_fixed']}")
            self.stdout.write(f"Timestamp issues fixed: {stats['timestamp_issues_fixed']}")
            self.stdout.write(f"Data inconsistencies fixed: {stats['data_inconsistencies_fixed']}")


# Export utilities
__all__ = [
    'AutomatedDataCleanup',
    'DataCleanupCommand'
]
