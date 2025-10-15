"""
Data integrity monitoring dashboard and alerting system.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class DataIntegrityMonitor:
    """
    Comprehensive data integrity monitoring system.
    """
    
    def __init__(self):
        self.monitoring_stats = {
            'total_checks': 0,
            'critical_issues': 0,
            'warning_issues': 0,
            'info_issues': 0,
            'last_check': None,
            'check_duration': 0
        }
    
    def check_orphaned_records(self):
        """
        Check for orphaned records across all tables.
        """
        issues = []
        
        with connection.cursor() as cursor:
            # Check for orphaned tickets
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket t
                LEFT JOIN organizations_organization o ON t.organization_id = o.id
                WHERE o.id IS NULL;
            """)
            orphaned_tickets = cursor.fetchone()[0]
            if orphaned_tickets > 0:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticket',
                    'field': 'organization_id',
                    'count': orphaned_tickets,
                    'description': f'{orphaned_tickets} tickets have invalid organization references'
                })
            
            # Check for orphaned comments
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketcomment tc
                LEFT JOIN tickets_ticket t ON tc.ticket_id = t.id
                WHERE t.id IS NULL;
            """)
            orphaned_comments = cursor.fetchone()[0]
            if orphaned_comments > 0:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticketcomment',
                    'field': 'ticket_id',
                    'count': orphaned_comments,
                    'description': f'{orphaned_comments} ticket comments have invalid ticket references'
                })
            
            # Check for orphaned attachments
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketattachment ta
                LEFT JOIN tickets_ticket t ON ta.ticket_id = t.id
                WHERE t.id IS NULL;
            """)
            orphaned_attachments = cursor.fetchone()[0]
            if orphaned_attachments > 0:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticketattachment',
                    'field': 'ticket_id',
                    'count': orphaned_attachments,
                    'description': f'{orphaned_attachments} ticket attachments have invalid ticket references'
                })
        
        return issues
    
    def check_duplicate_records(self):
        """
        Check for duplicate records across all tables.
        """
        issues = []
        
        with connection.cursor() as cursor:
            # Check for duplicate ticket numbers
            cursor.execute("""
                SELECT ticket_number, COUNT(*) as count
                FROM tickets_ticket
                GROUP BY ticket_number
                HAVING COUNT(*) > 1;
            """)
            duplicate_tickets = cursor.fetchall()
            for ticket_number, count in duplicate_tickets:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticket',
                    'field': 'ticket_number',
                    'value': ticket_number,
                    'count': count,
                    'description': f'Duplicate ticket number: {ticket_number} ({count} occurrences)'
                })
            
            # Check for duplicate session keys
            cursor.execute("""
                SELECT session_key, COUNT(*) as count
                FROM accounts_usersession
                GROUP BY session_key
                HAVING COUNT(*) > 1;
            """)
            duplicate_sessions = cursor.fetchall()
            for session_key, count in duplicate_sessions:
                issues.append({
                    'type': 'critical',
                    'table': 'accounts_usersession',
                    'field': 'session_key',
                    'value': session_key,
                    'count': count,
                    'description': f'Duplicate session key: {session_key} ({count} occurrences)'
                })
        
        return issues
    
    def check_null_values(self):
        """
        Check for NULL values in required fields.
        """
        issues = []
        
        with connection.cursor() as cursor:
            # Check for NULL ticket subjects
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket 
                WHERE subject IS NULL OR subject = '';
            """)
            null_subjects = cursor.fetchone()[0]
            if null_subjects > 0:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticket',
                    'field': 'subject',
                    'count': null_subjects,
                    'description': f'{null_subjects} tickets have NULL or empty subject'
                })
            
            # Check for NULL user emails
            cursor.execute("""
                SELECT COUNT(*) FROM accounts_user 
                WHERE email IS NULL OR email = '';
            """)
            null_emails = cursor.fetchone()[0]
            if null_emails > 0:
                issues.append({
                    'type': 'critical',
                    'table': 'accounts_user',
                    'field': 'email',
                    'count': null_emails,
                    'description': f'{null_emails} users have NULL or empty email'
                })
        
        return issues
    
    def check_invalid_enum_values(self):
        """
        Check for invalid enum values.
        """
        issues = []
        
        with connection.cursor() as cursor:
            # Check for invalid ticket statuses
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM tickets_ticket
                WHERE status NOT IN ('new', 'open', 'pending', 'resolved', 'closed', 'cancelled')
                GROUP BY status;
            """)
            invalid_statuses = cursor.fetchall()
            for status, count in invalid_statuses:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticket',
                    'field': 'status',
                    'value': status,
                    'count': count,
                    'description': f'{count} tickets have invalid status: {status}'
                })
            
            # Check for invalid user roles
            cursor.execute("""
                SELECT role, COUNT(*) as count
                FROM accounts_user
                WHERE role NOT IN ('admin', 'manager', 'agent', 'customer')
                GROUP BY role;
            """)
            invalid_roles = cursor.fetchall()
            for role, count in invalid_roles:
                issues.append({
                    'type': 'critical',
                    'table': 'accounts_user',
                    'field': 'role',
                    'value': role,
                    'count': count,
                    'description': f'{count} users have invalid role: {role}'
                })
        
        return issues
    
    def check_timestamp_consistency(self):
        """
        Check for timestamp consistency issues.
        """
        issues = []
        
        with connection.cursor() as cursor:
            # Check for tickets where updated_at is before created_at
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE updated_at < created_at;
            """)
            inconsistent_timestamps = cursor.fetchone()[0]
            if inconsistent_timestamps > 0:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticket',
                    'field': 'updated_at < created_at',
                    'count': inconsistent_timestamps,
                    'description': f'{inconsistent_timestamps} tickets have updated_at before created_at'
                })
        
        return issues
    
    def check_data_inconsistencies(self):
        """
        Check for data inconsistencies.
        """
        issues = []
        
        with connection.cursor() as cursor:
            # Check for invalid satisfaction scores
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE customer_satisfaction_score IS NOT NULL 
                AND (customer_satisfaction_score < 1 OR customer_satisfaction_score > 5);
            """)
            invalid_scores = cursor.fetchone()[0]
            if invalid_scores > 0:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticket',
                    'field': 'customer_satisfaction_score',
                    'count': invalid_scores,
                    'description': f'{invalid_scores} tickets have invalid satisfaction scores (not 1-5)'
                })
            
            # Check for invalid file sizes
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketattachment
                WHERE file_size <= 0;
            """)
            invalid_sizes = cursor.fetchone()[0]
            if invalid_sizes > 0:
                issues.append({
                    'type': 'critical',
                    'table': 'tickets_ticketattachment',
                    'field': 'file_size',
                    'count': invalid_sizes,
                    'description': f'{invalid_sizes} ticket attachments have invalid file sizes (<= 0)'
                })
        
        return issues
    
    def run_comprehensive_check(self):
        """
        Run comprehensive data integrity check.
        """
        start_time = timezone.now()
        
        logger.info("Starting comprehensive data integrity check...")
        
        all_issues = []
        
        # Run all checks
        all_issues.extend(self.check_orphaned_records())
        all_issues.extend(self.check_duplicate_records())
        all_issues.extend(self.check_null_values())
        all_issues.extend(self.check_invalid_enum_values())
        all_issues.extend(self.check_timestamp_consistency())
        all_issues.extend(self.check_data_inconsistencies())
        
        # Categorize issues
        critical_issues = [issue for issue in all_issues if issue['type'] == 'critical']
        warning_issues = [issue for issue in all_issues if issue['type'] == 'warning']
        info_issues = [issue for issue in all_issues if issue['type'] == 'info']
        
        # Update monitoring stats
        end_time = timezone.now()
        self.monitoring_stats.update({
            'total_checks': len(all_issues),
            'critical_issues': len(critical_issues),
            'warning_issues': len(warning_issues),
            'info_issues': len(info_issues),
            'last_check': end_time,
            'check_duration': (end_time - start_time).total_seconds()
        })
        
        logger.info(f"Data integrity check completed in {self.monitoring_stats['check_duration']:.2f} seconds")
        logger.info(f"Found {len(critical_issues)} critical issues, {len(warning_issues)} warning issues, {len(info_issues)} info issues")
        
        return {
            'critical_issues': critical_issues,
            'warning_issues': warning_issues,
            'info_issues': info_issues,
            'total_issues': len(all_issues),
            'monitoring_stats': self.monitoring_stats
        }
    
    def generate_dashboard_data(self):
        """
        Generate data for the monitoring dashboard.
        """
        results = self.run_comprehensive_check()
        
        dashboard_data = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': 'healthy' if results['critical_issues'] == 0 else 'unhealthy',
            'total_issues': results['total_issues'],
            'critical_issues': len(results['critical_issues']),
            'warning_issues': len(results['warning_issues']),
            'info_issues': len(results['info_issues']),
            'issues_by_type': self._categorize_issues_by_type(results),
            'issues_by_table': self._categorize_issues_by_table(results),
            'monitoring_stats': self.monitoring_stats
        }
        
        return dashboard_data
    
    def _categorize_issues_by_type(self, results):
        """
        Categorize issues by type for dashboard visualization.
        """
        type_counts = {}
        
        for issue in results['critical_issues'] + results['warning_issues'] + results['info_issues']:
            issue_type = issue.get('type', 'unknown')
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
        
        return type_counts
    
    def _categorize_issues_by_table(self, results):
        """
        Categorize issues by table for dashboard visualization.
        """
        table_counts = {}
        
        for issue in results['critical_issues'] + results['warning_issues'] + results['info_issues']:
            table = issue.get('table', 'unknown')
            table_counts[table] = table_counts.get(table, 0) + 1
        
        return table_counts
    
    def send_alert_if_needed(self, results):
        """
        Send alert if critical issues are found.
        """
        if results['critical_issues'] > 0:
            logger.critical(f"CRITICAL: {results['critical_issues']} data integrity issues found!")
            # Here you would implement actual alerting (email, Slack, etc.)
            return True
        
        return False


class MonitoringDashboardCommand(BaseCommand):
    """
    Django management command for data integrity monitoring dashboard.
    """
    
    help = 'Run data integrity monitoring dashboard'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--export-dashboard',
            action='store_true',
            help='Export dashboard data to JSON file'
        )
        parser.add_argument(
            '--send-alerts',
            action='store_true',
            help='Send alerts for critical issues'
        )
        parser.add_argument(
            '--format',
            choices=['json', 'table', 'summary'],
            default='summary',
            help='Output format for the dashboard'
        )
    
    def handle(self, *args, **options):
        """Handle the monitoring dashboard command."""
        monitor = DataIntegrityMonitor()
        
        self.stdout.write(self.style.SUCCESS('Starting data integrity monitoring...'))
        
        # Run comprehensive check
        results = monitor.run_comprehensive_check()
        
        # Generate dashboard data
        dashboard_data = monitor.generate_dashboard_data()
        
        # Display results based on format
        if options['format'] == 'json':
            self.stdout.write(json.dumps(dashboard_data, indent=2))
        elif options['format'] == 'table':
            self._display_table_format(results)
        else:  # summary
            self._display_summary_format(results)
        
        # Export dashboard if requested
        if options['export_dashboard']:
            self._export_dashboard(dashboard_data)
        
        # Send alerts if requested
        if options['send_alerts']:
            monitor.send_alert_if_needed(results)
    
    def _display_summary_format(self, results):
        """Display results in summary format."""
        self.stdout.write(self.style.SUCCESS('\n=== Data Integrity Monitoring Summary ==='))
        self.stdout.write(f'Total Issues: {results["total_issues"]}')
        self.stdout.write(f'Critical Issues: {len(results["critical_issues"])}')
        self.stdout.write(f'Warning Issues: {len(results["warning_issues"])}')
        self.stdout.write(f'Info Issues: {len(results["info_issues"])}')
        
        if results['critical_issues']:
            self.stdout.write(self.style.ERROR('\n=== CRITICAL ISSUES ==='))
            for issue in results['critical_issues']:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ {issue['type'].upper()}: {issue['description']} "
                        f"(Table: {issue['table']}, Field: {issue['field']}, Count: {issue['count']})"
                    )
                )
        
        if results['warning_issues']:
            self.stdout.write(self.style.WARNING('\n=== WARNING ISSUES ==='))
            for issue in results['warning_issues']:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  {issue['type'].upper()}: {issue['description']} "
                        f"(Table: {issue['table']}, Field: {issue['field']}, Count: {issue['count']})"
                    )
                )
    
    def _display_table_format(self, results):
        """Display results in table format."""
        from django.utils import timezone
        
        self.stdout.write('\n=== Data Integrity Issues Table ===')
        self.stdout.write('Type\t\tTable\t\t\tField\t\t\tCount\tDescription')
        self.stdout.write('-' * 80)
        
        for issue in results['critical_issues'] + results['warning_issues'] + results['info_issues']:
            self.stdout.write(
                f"{issue['type']}\t\t{issue['table']}\t\t{issue['field']}\t\t{issue['count']}\t{issue['description']}"
            )
    
    def _export_dashboard(self, dashboard_data):
        """Export dashboard data to JSON file."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data_integrity_dashboard_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        self.stdout.write(self.style.SUCCESS(f'Dashboard data exported to: {filename}'))


# Export utilities
__all__ = [
    'DataIntegrityMonitor',
    'MonitoringDashboardCommand'
]
