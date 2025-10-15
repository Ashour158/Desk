"""
Comprehensive data integrity analysis for the database.
"""

from django.db import connection
from django.core.management.base import BaseCommand
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataIntegrityAnalyzer:
    """
    Comprehensive data integrity analysis utilities.
    """
    
    def __init__(self):
        self.integrity_issues = []
        self.critical_issues = []
        self.warning_issues = []
        self.info_issues = []
    
    def analyze_all_integrity_issues(self):
        """
        Run comprehensive data integrity analysis.
        """
        logger.info("Starting comprehensive data integrity analysis...")
        
        # 1. Check for orphaned records
        self.check_orphaned_records()
        
        # 2. Check for duplicate entries
        self.check_duplicate_entries()
        
        # 3. Check for NULL values in required fields
        self.check_null_values()
        
        # 4. Check for invalid enum values
        self.check_invalid_enum_values()
        
        # 5. Check timestamp consistency
        self.check_timestamp_consistency()
        
        # 6. Check for data inconsistencies
        self.check_data_inconsistencies()
        
        # 7. Check for referential integrity issues
        self.check_referential_integrity()
        
        return {
            'critical_issues': self.critical_issues,
            'warning_issues': self.warning_issues,
            'info_issues': self.info_issues,
            'total_issues': len(self.critical_issues) + len(self.warning_issues) + len(self.info_issues)
        }
    
    def check_orphaned_records(self):
        """
        Check for orphaned records (foreign key violations).
        """
        logger.info("Checking for orphaned records...")
        
        with connection.cursor() as cursor:
            # Check for tickets with invalid organization references
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket t
                LEFT JOIN organizations_organization o ON t.organization_id = o.id
                WHERE o.id IS NULL;
            """)
            orphaned_tickets = cursor.fetchone()[0]
            if orphaned_tickets > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'tickets_ticket',
                    'field': 'organization_id',
                    'count': orphaned_tickets,
                    'description': f'{orphaned_tickets} tickets have invalid organization references'
                })
            
            # Check for tickets with invalid customer references
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket t
                LEFT JOIN accounts_user u ON t.customer_id = u.id
                WHERE u.id IS NULL;
            """)
            orphaned_customer_tickets = cursor.fetchone()[0]
            if orphaned_customer_tickets > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'tickets_ticket',
                    'field': 'customer_id',
                    'count': orphaned_customer_tickets,
                    'description': f'{orphaned_customer_tickets} tickets have invalid customer references'
                })
            
            # Check for tickets with invalid assigned_agent references
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket t
                LEFT JOIN accounts_user u ON t.assigned_agent_id = u.id
                WHERE t.assigned_agent_id IS NOT NULL AND u.id IS NULL;
            """)
            orphaned_agent_tickets = cursor.fetchone()[0]
            if orphaned_agent_tickets > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'tickets_ticket',
                    'field': 'assigned_agent_id',
                    'count': orphaned_agent_tickets,
                    'description': f'{orphaned_agent_tickets} tickets have invalid assigned agent references'
                })
            
            # Check for ticket comments with invalid ticket references
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketcomment tc
                LEFT JOIN tickets_ticket t ON tc.ticket_id = t.id
                WHERE t.id IS NULL;
            """)
            orphaned_comments = cursor.fetchone()[0]
            if orphaned_comments > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'tickets_ticketcomment',
                    'field': 'ticket_id',
                    'count': orphaned_comments,
                    'description': f'{orphaned_comments} ticket comments have invalid ticket references'
                })
            
            # Check for ticket comments with invalid author references
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketcomment tc
                LEFT JOIN accounts_user u ON tc.author_id = u.id
                WHERE u.id IS NULL;
            """)
            orphaned_comment_authors = cursor.fetchone()[0]
            if orphaned_comment_authors > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'tickets_ticketcomment',
                    'field': 'author_id',
                    'count': orphaned_comment_authors,
                    'description': f'{orphaned_comment_authors} ticket comments have invalid author references'
                })
            
            # Check for ticket attachments with invalid ticket references
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketattachment ta
                LEFT JOIN tickets_ticket t ON ta.ticket_id = t.id
                WHERE t.id IS NULL;
            """)
            orphaned_attachments = cursor.fetchone()[0]
            if orphaned_attachments > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'tickets_ticketattachment',
                    'field': 'ticket_id',
                    'count': orphaned_attachments,
                    'description': f'{orphaned_attachments} ticket attachments have invalid ticket references'
                })
            
            # Check for ticket attachments with invalid comment references
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketattachment ta
                LEFT JOIN tickets_ticketcomment tc ON ta.comment_id = tc.id
                WHERE ta.comment_id IS NOT NULL AND tc.id IS NULL;
            """)
            orphaned_comment_attachments = cursor.fetchone()[0]
            if orphaned_comment_attachments > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'tickets_ticketattachment',
                    'field': 'comment_id',
                    'count': orphaned_comment_attachments,
                    'description': f'{orphaned_comment_attachments} ticket attachments have invalid comment references'
                })
            
            # Check for user sessions with invalid user references
            cursor.execute("""
                SELECT COUNT(*) FROM accounts_usersession us
                LEFT JOIN accounts_user u ON us.user_id = u.id
                WHERE u.id IS NULL;
            """)
            orphaned_sessions = cursor.fetchone()[0]
            if orphaned_sessions > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'accounts_usersession',
                    'field': 'user_id',
                    'count': orphaned_sessions,
                    'description': f'{orphaned_sessions} user sessions have invalid user references'
                })
            
            # Check for user permissions with invalid user references
            cursor.execute("""
                SELECT COUNT(*) FROM accounts_userpermission up
                LEFT JOIN accounts_user u ON up.user_id = u.id
                WHERE u.id IS NULL;
            """)
            orphaned_permissions = cursor.fetchone()[0]
            if orphaned_permissions > 0:
                self.critical_issues.append({
                    'type': 'orphaned_records',
                    'table': 'accounts_userpermission',
                    'field': 'user_id',
                    'count': orphaned_permissions,
                    'description': f'{orphaned_permissions} user permissions have invalid user references'
                })
    
    def check_duplicate_entries(self):
        """
        Check for duplicate entries where uniqueness is expected.
        """
        logger.info("Checking for duplicate entries...")
        
        with connection.cursor() as cursor:
            # Check for duplicate ticket numbers
            cursor.execute("""
                SELECT ticket_number, COUNT(*) as count
                FROM tickets_ticket
                GROUP BY ticket_number
                HAVING COUNT(*) > 1;
            """)
            duplicate_ticket_numbers = cursor.fetchall()
            for ticket_number, count in duplicate_ticket_numbers:
                self.critical_issues.append({
                    'type': 'duplicate_entries',
                    'table': 'tickets_ticket',
                    'field': 'ticket_number',
                    'value': ticket_number,
                    'count': count,
                    'description': f'Duplicate ticket number: {ticket_number} ({count} occurrences)'
                })
            
            # Check for duplicate user sessions
            cursor.execute("""
                SELECT session_key, COUNT(*) as count
                FROM accounts_usersession
                GROUP BY session_key
                HAVING COUNT(*) > 1;
            """)
            duplicate_sessions = cursor.fetchall()
            for session_key, count in duplicate_sessions:
                self.critical_issues.append({
                    'type': 'duplicate_entries',
                    'table': 'accounts_usersession',
                    'field': 'session_key',
                    'value': session_key,
                    'count': count,
                    'description': f'Duplicate session key: {session_key} ({count} occurrences)'
                })
            
            # Check for duplicate user permissions
            cursor.execute("""
                SELECT user_id, permission, COUNT(*) as count
                FROM accounts_userpermission
                GROUP BY user_id, permission
                HAVING COUNT(*) > 1;
            """)
            duplicate_permissions = cursor.fetchall()
            for user_id, permission, count in duplicate_permissions:
                self.critical_issues.append({
                    'type': 'duplicate_entries',
                    'table': 'accounts_userpermission',
                    'field': 'user_id, permission',
                    'value': f'{user_id}, {permission}',
                    'count': count,
                    'description': f'Duplicate user permission: user {user_id}, permission {permission} ({count} occurrences)'
                })
            
            # Check for duplicate organization slugs
            cursor.execute("""
                SELECT slug, COUNT(*) as count
                FROM organizations_organization
                GROUP BY slug
                HAVING COUNT(*) > 1;
            """)
            duplicate_slugs = cursor.fetchall()
            for slug, count in duplicate_slugs:
                self.critical_issues.append({
                    'type': 'duplicate_entries',
                    'table': 'organizations_organization',
                    'field': 'slug',
                    'value': slug,
                    'count': count,
                    'description': f'Duplicate organization slug: {slug} ({count} occurrences)'
                })
    
    def check_null_values(self):
        """
        Check for NULL values in required fields.
        """
        logger.info("Checking for NULL values in required fields...")
        
        with connection.cursor() as cursor:
            # Check for tickets with NULL subject
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket WHERE subject IS NULL OR subject = '';
            """)
            null_subjects = cursor.fetchone()[0]
            if null_subjects > 0:
                self.critical_issues.append({
                    'type': 'null_values',
                    'table': 'tickets_ticket',
                    'field': 'subject',
                    'count': null_subjects,
                    'description': f'{null_subjects} tickets have NULL or empty subject'
                })
            
            # Check for tickets with NULL description
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket WHERE description IS NULL OR description = '';
            """)
            null_descriptions = cursor.fetchone()[0]
            if null_descriptions > 0:
                self.critical_issues.append({
                    'type': 'null_values',
                    'table': 'tickets_ticket',
                    'field': 'description',
                    'count': null_descriptions,
                    'description': f'{null_descriptions} tickets have NULL or empty description'
                })
            
            # Check for ticket comments with NULL content
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketcomment WHERE content IS NULL OR content = '';
            """)
            null_comment_content = cursor.fetchone()[0]
            if null_comment_content > 0:
                self.critical_issues.append({
                    'type': 'null_values',
                    'table': 'tickets_ticketcomment',
                    'field': 'content',
                    'count': null_comment_content,
                    'description': f'{null_comment_content} ticket comments have NULL or empty content'
                })
            
            # Check for ticket attachments with NULL file_name
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketattachment WHERE file_name IS NULL OR file_name = '';
            """)
            null_file_names = cursor.fetchone()[0]
            if null_file_names > 0:
                self.critical_issues.append({
                    'type': 'null_values',
                    'table': 'tickets_ticketattachment',
                    'field': 'file_name',
                    'count': null_file_names,
                    'description': f'{null_file_names} ticket attachments have NULL or empty file_name'
                })
            
            # Check for ticket attachments with NULL file_path
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketattachment WHERE file_path IS NULL OR file_path = '';
            """)
            null_file_paths = cursor.fetchone()[0]
            if null_file_paths > 0:
                self.critical_issues.append({
                    'type': 'null_values',
                    'table': 'tickets_ticketattachment',
                    'field': 'file_path',
                    'count': null_file_paths,
                    'description': f'{null_file_paths} ticket attachments have NULL or empty file_path'
                })
            
            # Check for users with NULL email
            cursor.execute("""
                SELECT COUNT(*) FROM accounts_user WHERE email IS NULL OR email = '';
            """)
            null_emails = cursor.fetchone()[0]
            if null_emails > 0:
                self.critical_issues.append({
                    'type': 'null_values',
                    'table': 'accounts_user',
                    'field': 'email',
                    'count': null_emails,
                    'description': f'{null_emails} users have NULL or empty email'
                })
            
            # Check for organizations with NULL name
            cursor.execute("""
                SELECT COUNT(*) FROM organizations_organization WHERE name IS NULL OR name = '';
            """)
            null_org_names = cursor.fetchone()[0]
            if null_org_names > 0:
                self.critical_issues.append({
                    'type': 'null_values',
                    'table': 'organizations_organization',
                    'field': 'name',
                    'count': null_org_names,
                    'description': f'{null_org_names} organizations have NULL or empty name'
                })
    
    def check_invalid_enum_values(self):
        """
        Check for invalid enum values.
        """
        logger.info("Checking for invalid enum values...")
        
        with connection.cursor() as cursor:
            # Check for invalid ticket status values
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM tickets_ticket
                WHERE status NOT IN ('new', 'open', 'pending', 'resolved', 'closed', 'cancelled')
                GROUP BY status;
            """)
            invalid_statuses = cursor.fetchall()
            for status, count in invalid_statuses:
                self.critical_issues.append({
                    'type': 'invalid_enum_values',
                    'table': 'tickets_ticket',
                    'field': 'status',
                    'value': status,
                    'count': count,
                    'description': f'{count} tickets have invalid status: {status}'
                })
            
            # Check for invalid ticket priority values
            cursor.execute("""
                SELECT priority, COUNT(*) as count
                FROM tickets_ticket
                WHERE priority NOT IN ('low', 'medium', 'high', 'urgent')
                GROUP BY priority;
            """)
            invalid_priorities = cursor.fetchall()
            for priority, count in invalid_priorities:
                self.critical_issues.append({
                    'type': 'invalid_enum_values',
                    'table': 'tickets_ticket',
                    'field': 'priority',
                    'value': priority,
                    'count': count,
                    'description': f'{count} tickets have invalid priority: {priority}'
                })
            
            # Check for invalid ticket channel values
            cursor.execute("""
                SELECT channel, COUNT(*) as count
                FROM tickets_ticket
                WHERE channel NOT IN ('email', 'web', 'phone', 'chat', 'social', 'api')
                GROUP BY channel;
            """)
            invalid_channels = cursor.fetchall()
            for channel, count in invalid_channels:
                self.critical_issues.append({
                    'type': 'invalid_enum_values',
                    'table': 'tickets_ticket',
                    'field': 'channel',
                    'value': channel,
                    'count': count,
                    'description': f'{count} tickets have invalid channel: {channel}'
                })
            
            # Check for invalid user role values
            cursor.execute("""
                SELECT role, COUNT(*) as count
                FROM accounts_user
                WHERE role NOT IN ('admin', 'manager', 'agent', 'customer')
                GROUP BY role;
            """)
            invalid_roles = cursor.fetchall()
            for role, count in invalid_roles:
                self.critical_issues.append({
                    'type': 'invalid_enum_values',
                    'table': 'accounts_user',
                    'field': 'role',
                    'value': role,
                    'count': count,
                    'description': f'{count} users have invalid role: {role}'
                })
            
            # Check for invalid customer tier values
            cursor.execute("""
                SELECT customer_tier, COUNT(*) as count
                FROM accounts_user
                WHERE customer_tier NOT IN ('basic', 'premium', 'enterprise')
                GROUP BY customer_tier;
            """)
            invalid_tiers = cursor.fetchall()
            for tier, count in invalid_tiers:
                self.critical_issues.append({
                    'type': 'invalid_enum_values',
                    'table': 'accounts_user',
                    'field': 'customer_tier',
                    'value': tier,
                    'count': count,
                    'description': f'{count} users have invalid customer tier: {tier}'
                })
            
            # Check for invalid comment type values
            cursor.execute("""
                SELECT comment_type, COUNT(*) as count
                FROM tickets_ticketcomment
                WHERE comment_type NOT IN ('public', 'internal', 'system')
                GROUP BY comment_type;
            """)
            invalid_comment_types = cursor.fetchall()
            for comment_type, count in invalid_comment_types:
                self.critical_issues.append({
                    'type': 'invalid_enum_values',
                    'table': 'tickets_ticketcomment',
                    'field': 'comment_type',
                    'value': comment_type,
                    'count': count,
                    'description': f'{count} ticket comments have invalid comment_type: {comment_type}'
                })
            
            # Check for invalid change type values
            cursor.execute("""
                SELECT change_type, COUNT(*) as count
                FROM tickets_tickethistory
                WHERE change_type NOT IN ('created', 'updated', 'assigned', 'status_changed', 'priority_changed', 'resolved', 'closed')
                GROUP BY change_type;
            """)
            invalid_change_types = cursor.fetchall()
            for change_type, count in invalid_change_types:
                self.critical_issues.append({
                    'type': 'invalid_enum_values',
                    'table': 'tickets_tickethistory',
                    'field': 'change_type',
                    'value': change_type,
                    'count': count,
                    'description': f'{count} ticket history records have invalid change_type: {change_type}'
                })
    
    def check_timestamp_consistency(self):
        """
        Check timestamp consistency (created_at, updated_at).
        """
        logger.info("Checking timestamp consistency...")
        
        with connection.cursor() as cursor:
            # Check for tickets where updated_at is before created_at
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE updated_at < created_at;
            """)
            inconsistent_ticket_timestamps = cursor.fetchone()[0]
            if inconsistent_ticket_timestamps > 0:
                self.critical_issues.append({
                    'type': 'timestamp_inconsistency',
                    'table': 'tickets_ticket',
                    'field': 'updated_at < created_at',
                    'count': inconsistent_ticket_timestamps,
                    'description': f'{inconsistent_ticket_timestamps} tickets have updated_at before created_at'
                })
            
            # Check for ticket comments where updated_at is before created_at
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketcomment
                WHERE updated_at < created_at;
            """)
            inconsistent_comment_timestamps = cursor.fetchone()[0]
            if inconsistent_comment_timestamps > 0:
                self.critical_issues.append({
                    'type': 'timestamp_inconsistency',
                    'table': 'tickets_ticketcomment',
                    'field': 'updated_at < created_at',
                    'count': inconsistent_comment_timestamps,
                    'description': f'{inconsistent_comment_timestamps} ticket comments have updated_at before created_at'
                })
            
            # Check for tickets where resolved_at is before created_at
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE resolved_at IS NOT NULL AND resolved_at < created_at;
            """)
            inconsistent_resolution_timestamps = cursor.fetchone()[0]
            if inconsistent_resolution_timestamps > 0:
                self.critical_issues.append({
                    'type': 'timestamp_inconsistency',
                    'table': 'tickets_ticket',
                    'field': 'resolved_at < created_at',
                    'count': inconsistent_resolution_timestamps,
                    'description': f'{inconsistent_resolution_timestamps} tickets have resolved_at before created_at'
                })
            
            # Check for tickets where first_response_at is before created_at
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE first_response_at IS NOT NULL AND first_response_at < created_at;
            """)
            inconsistent_first_response_timestamps = cursor.fetchone()[0]
            if inconsistent_first_response_timestamps > 0:
                self.critical_issues.append({
                    'type': 'timestamp_inconsistency',
                    'table': 'tickets_ticket',
                    'field': 'first_response_at < created_at',
                    'count': inconsistent_first_response_timestamps,
                    'description': f'{inconsistent_first_response_timestamps} tickets have first_response_at before created_at'
                })
            
            # Check for tickets where closed_at is before created_at
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE closed_at IS NOT NULL AND closed_at < created_at;
            """)
            inconsistent_closed_timestamps = cursor.fetchone()[0]
            if inconsistent_closed_timestamps > 0:
                self.critical_issues.append({
                    'type': 'timestamp_inconsistency',
                    'table': 'tickets_ticket',
                    'field': 'closed_at < created_at',
                    'count': inconsistent_closed_timestamps,
                    'description': f'{inconsistent_closed_timestamps} tickets have closed_at before created_at'
                })
            
            # Check for user sessions where last_activity is before created_at
            cursor.execute("""
                SELECT COUNT(*) FROM accounts_usersession
                WHERE last_activity < created_at;
            """)
            inconsistent_session_timestamps = cursor.fetchone()[0]
            if inconsistent_session_timestamps > 0:
                self.critical_issues.append({
                    'type': 'timestamp_inconsistency',
                    'table': 'accounts_usersession',
                    'field': 'last_activity < created_at',
                    'count': inconsistent_session_timestamps,
                    'description': f'{inconsistent_session_timestamps} user sessions have last_activity before created_at'
                })
    
    def check_data_inconsistencies(self):
        """
        Check for data inconsistencies.
        """
        logger.info("Checking for data inconsistencies...")
        
        with connection.cursor() as cursor:
            # Check for tickets with invalid satisfaction scores
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE customer_satisfaction_score IS NOT NULL 
                AND (customer_satisfaction_score < 1 OR customer_satisfaction_score > 5);
            """)
            invalid_satisfaction_scores = cursor.fetchone()[0]
            if invalid_satisfaction_scores > 0:
                self.critical_issues.append({
                    'type': 'data_inconsistency',
                    'table': 'tickets_ticket',
                    'field': 'customer_satisfaction_score',
                    'count': invalid_satisfaction_scores,
                    'description': f'{invalid_satisfaction_scores} tickets have invalid satisfaction scores (not 1-5)'
                })
            
            # Check for ticket attachments with invalid file sizes
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketattachment
                WHERE file_size <= 0;
            """)
            invalid_file_sizes = cursor.fetchone()[0]
            if invalid_file_sizes > 0:
                self.critical_issues.append({
                    'type': 'data_inconsistency',
                    'table': 'tickets_ticketattachment',
                    'field': 'file_size',
                    'count': invalid_file_sizes,
                    'description': f'{invalid_file_sizes} ticket attachments have invalid file sizes (<= 0)'
                })
            
            # Check for users with invalid max_concurrent_tickets
            cursor.execute("""
                SELECT COUNT(*) FROM accounts_user
                WHERE max_concurrent_tickets <= 0;
            """)
            invalid_max_tickets = cursor.fetchone()[0]
            if invalid_max_tickets > 0:
                self.critical_issues.append({
                    'type': 'data_inconsistency',
                    'table': 'accounts_user',
                    'field': 'max_concurrent_tickets',
                    'count': invalid_max_tickets,
                    'description': f'{invalid_max_tickets} users have invalid max_concurrent_tickets (<= 0)'
                })
            
            # Check for canned responses with invalid usage_count
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_cannedresponse
                WHERE usage_count < 0;
            """)
            invalid_usage_counts = cursor.fetchone()[0]
            if invalid_usage_counts > 0:
                self.critical_issues.append({
                    'type': 'data_inconsistency',
                    'table': 'tickets_cannedresponse',
                    'field': 'usage_count',
                    'count': invalid_usage_counts,
                    'description': f'{invalid_usage_counts} canned responses have invalid usage_count (< 0)'
                })
            
            # Check for ticket attachments with invalid download_count
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticketattachment
                WHERE download_count < 0;
            """)
            invalid_download_counts = cursor.fetchone()[0]
            if invalid_download_counts > 0:
                self.critical_issues.append({
                    'type': 'data_inconsistency',
                    'table': 'tickets_ticketattachment',
                    'field': 'download_count',
                    'count': invalid_download_counts,
                    'description': f'{invalid_download_counts} ticket attachments have invalid download_count (< 0)'
                })
    
    def check_referential_integrity(self):
        """
        Check for referential integrity issues.
        """
        logger.info("Checking referential integrity...")
        
        with connection.cursor() as cursor:
            # Check for tickets where customer is not actually a customer
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket t
                JOIN accounts_user u ON t.customer_id = u.id
                WHERE u.role != 'customer';
            """)
            non_customer_tickets = cursor.fetchone()[0]
            if non_customer_tickets > 0:
                self.critical_issues.append({
                    'type': 'referential_integrity',
                    'table': 'tickets_ticket',
                    'field': 'customer_id',
                    'count': non_customer_tickets,
                    'description': f'{non_customer_tickets} tickets have customer_id pointing to non-customer users'
                })
            
            # Check for tickets where assigned_agent is not actually an agent
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket t
                JOIN accounts_user u ON t.assigned_agent_id = u.id
                WHERE u.role NOT IN ('admin', 'manager', 'agent');
            """)
            non_agent_tickets = cursor.fetchone()[0]
            if non_agent_tickets > 0:
                self.critical_issues.append({
                    'type': 'referential_integrity',
                    'table': 'tickets_ticket',
                    'field': 'assigned_agent_id',
                    'count': non_agent_tickets,
                    'description': f'{non_agent_tickets} tickets have assigned_agent_id pointing to non-agent users'
                })
            
            # Check for tickets where SLA fields are inconsistent
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE first_response_at IS NOT NULL 
                AND first_response_due IS NOT NULL 
                AND first_response_at > first_response_due;
            """)
            sla_breach_first_response = cursor.fetchone()[0]
            if sla_breach_first_response > 0:
                self.warning_issues.append({
                    'type': 'referential_integrity',
                    'table': 'tickets_ticket',
                    'field': 'first_response_at > first_response_due',
                    'count': sla_breach_first_response,
                    'description': f'{sla_breach_first_response} tickets have first_response_at after first_response_due (SLA breach)'
                })
            
            # Check for tickets where resolution fields are inconsistent
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_ticket
                WHERE resolved_at IS NOT NULL 
                AND resolution_due IS NOT NULL 
                AND resolved_at > resolution_due;
            """)
            sla_breach_resolution = cursor.fetchone()[0]
            if sla_breach_resolution > 0:
                self.warning_issues.append({
                    'type': 'referential_integrity',
                    'table': 'tickets_ticket',
                    'field': 'resolved_at > resolution_due',
                    'count': sla_breach_resolution,
                    'description': f'{sla_breach_resolution} tickets have resolved_at after resolution_due (SLA breach)'
                })


class DataIntegrityCommand(BaseCommand):
    """
    Django management command for data integrity analysis.
    """
    
    help = 'Analyze database for data integrity issues'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Attempt to fix identified issues (use with caution)'
        )
        parser.add_argument(
            '--export-report',
            action='store_true',
            help='Export detailed report to file'
        )
        parser.add_argument(
            '--severity',
            choices=['critical', 'warning', 'info', 'all'],
            default='all',
            help='Filter issues by severity level'
        )
    
    def handle(self, *args, **options):
        """Handle the data integrity analysis command."""
        analyzer = DataIntegrityAnalyzer()
        
        self.stdout.write(self.style.SUCCESS('Starting data integrity analysis...'))
        
        # Run comprehensive analysis
        results = analyzer.analyze_all_integrity_issues()
        
        # Display results
        self.display_results(results, options['severity'])
        
        # Export report if requested
        if options['export_report']:
            self.export_report(results)
        
        # Fix issues if requested
        if options['fix_issues']:
            self.fix_issues(results)
    
    def display_results(self, results, severity_filter):
        """Display analysis results."""
        total_issues = results['total_issues']
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Data Integrity Analysis Results ==='))
        self.stdout.write(f'Total Issues Found: {total_issues}')
        self.stdout.write(f'Critical Issues: {len(results["critical_issues"])}')
        self.stdout.write(f'Warning Issues: {len(results["warning_issues"])}')
        self.stdout.write(f'Info Issues: {len(results["info_issues"])}')
        
        # Display critical issues
        if severity_filter in ['critical', 'all'] and results['critical_issues']:
            self.stdout.write(self.style.ERROR('\n=== CRITICAL ISSUES ==='))
            for issue in results['critical_issues']:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ {issue['type'].upper()}: {issue['description']} "
                        f"(Table: {issue['table']}, Field: {issue['field']}, Count: {issue['count']})"
                    )
                )
        
        # Display warning issues
        if severity_filter in ['warning', 'all'] and results['warning_issues']:
            self.stdout.write(self.style.WARNING('\n=== WARNING ISSUES ==='))
            for issue in results['warning_issues']:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  {issue['type'].upper()}: {issue['description']} "
                        f"(Table: {issue['table']}, Field: {issue['field']}, Count: {issue['count']})"
                    )
                )
        
        # Display info issues
        if severity_filter in ['info', 'all'] and results['info_issues']:
            self.stdout.write(self.style.SUCCESS('\n=== INFO ISSUES ==='))
            for issue in results['info_issues']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"ℹ️  {issue['type'].upper()}: {issue['description']} "
                        f"(Table: {issue['table']}, Field: {issue['field']}, Count: {issue['count']})"
                    )
                )
    
    def export_report(self, results):
        """Export detailed report to file."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data_integrity_report_{timestamp}.md'
        
        with open(filename, 'w') as f:
            f.write(f"# Data Integrity Analysis Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## Summary\n")
            f.write(f"- Total Issues: {results['total_issues']}\n")
            f.write(f"- Critical Issues: {len(results['critical_issues'])}\n")
            f.write(f"- Warning Issues: {len(results['warning_issues'])}\n")
            f.write(f"- Info Issues: {len(results['info_issues'])}\n\n")
            
            if results['critical_issues']:
                f.write(f"## Critical Issues\n\n")
                for issue in results['critical_issues']:
                    f.write(f"### {issue['type'].upper()}\n")
                    f.write(f"- **Table**: {issue['table']}\n")
                    f.write(f"- **Field**: {issue['field']}\n")
                    f.write(f"- **Count**: {issue['count']}\n")
                    f.write(f"- **Description**: {issue['description']}\n\n")
            
            if results['warning_issues']:
                f.write(f"## Warning Issues\n\n")
                for issue in results['warning_issues']:
                    f.write(f"### {issue['type'].upper()}\n")
                    f.write(f"- **Table**: {issue['table']}\n")
                    f.write(f"- **Field**: {issue['field']}\n")
                    f.write(f"- **Count**: {issue['count']}\n")
                    f.write(f"- **Description**: {issue['description']}\n\n")
        
        self.stdout.write(self.style.SUCCESS(f'Report exported to: {filename}'))
    
    def fix_issues(self, results):
        """Attempt to fix identified issues."""
        self.stdout.write(self.style.WARNING('Fixing issues is not implemented yet.'))
        self.stdout.write(self.style.WARNING('Please review issues manually and implement fixes as needed.'))


# Export utilities
__all__ = [
    'DataIntegrityAnalyzer',
    'DataIntegrityCommand'
]
