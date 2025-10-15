"""
Enhanced database constraints for improved data integrity.
"""

from django.db import migrations, models
from django.db.models import Q
from django.contrib.postgres.operations import AddIndex, CreateExtension
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.indexes import GinIndex, BTreeIndex, HashIndex


class EnhancedConstraints:
    """
    Comprehensive database constraint utilities.
    """
    
    @staticmethod
    def get_ticket_constraints():
        """Get enhanced constraints for Ticket model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(customer_satisfaction_score__isnull=True) | Q(customer_satisfaction_score__gte=1, customer_satisfaction_score__lte=5),
                name='check_ticket_satisfaction_score_range'
            ),
            models.CheckConstraint(
                check=Q(time_to_first_response__isnull=True) | Q(time_to_first_response__gte=0),
                name='check_ticket_first_response_time_positive'
            ),
            models.CheckConstraint(
                check=Q(time_to_resolution__isnull=True) | Q(time_to_resolution__gte=0),
                name='check_ticket_resolution_time_positive'
            ),
            
            # Status transition constraints
            models.CheckConstraint(
                check=Q(status__in=['new', 'open', 'pending', 'resolved', 'closed', 'cancelled']),
                name='check_ticket_status_valid'
            ),
            models.CheckConstraint(
                check=Q(priority__in=['low', 'medium', 'high', 'urgent']),
                name='check_ticket_priority_valid'
            ),
            models.CheckConstraint(
                check=Q(channel__in=['email', 'web', 'phone', 'chat', 'social', 'api']),
                name='check_ticket_channel_valid'
            ),
            
            # Timestamp consistency constraints
            models.CheckConstraint(
                check=Q(updated_at__gte=models.F('created_at')),
                name='check_ticket_updated_after_created'
            ),
            models.CheckConstraint(
                check=Q(resolved_at__isnull=True) | Q(resolved_at__gte=models.F('created_at'))),
                name='check_ticket_resolved_after_created'
            ),
            models.CheckConstraint(
                check=Q(first_response_at__isnull=True) | Q(first_response_at__gte=models.F('created_at'))),
                name='check_ticket_first_response_after_created'
            ),
            models.CheckConstraint(
                check=Q(closed_at__isnull=True) | Q(closed_at__gte=models.F('created_at'))),
                name='check_ticket_closed_after_created'
            ),
            
            # SLA constraints
            models.CheckConstraint(
                check=Q(first_response_due__isnull=True) | Q(first_response_due__gte=models.F('created_at'))),
                name='check_ticket_first_response_due_after_created'
            ),
            models.CheckConstraint(
                check=Q(resolution_due__isnull=True) | Q(resolution_due__gte=models.F('created_at'))),
                name='check_ticket_resolution_due_after_created'
            ),
            models.CheckConstraint(
                check=Q(first_response_at__isnull=True) | Q(first_response_due__isnull=True) | Q(first_response_at__lte=models.F('first_response_due'))),
                name='check_ticket_first_response_within_sla'
            ),
            models.CheckConstraint(
                check=Q(resolved_at__isnull=True) | Q(resolution_due__isnull=True) | Q(resolved_at__lte=models.F('resolution_due'))),
                name='check_ticket_resolution_within_sla'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(status='closed') | Q(closed_at__isnull=True),
                name='check_ticket_closed_at_only_when_closed'
            ),
            models.CheckConstraint(
                check=Q(status='resolved') | Q(resolved_at__isnull=True),
                name='check_ticket_resolved_at_only_when_resolved'
            ),
            models.CheckConstraint(
                check=Q(status__in=['resolved', 'closed']) | Q(sla_breach=False),
                name='check_ticket_sla_breach_only_for_active_tickets'
            ),
        ]
    
    @staticmethod
    def get_user_constraints():
        """Get enhanced constraints for User model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(max_concurrent_tickets__gte=1, max_concurrent_tickets__lte=100),
                name='check_user_max_tickets_range'
            ),
            models.CheckConstraint(
                check=Q(role__in=['admin', 'manager', 'agent', 'customer']),
                name='check_user_role_valid'
            ),
            models.CheckConstraint(
                check=Q(customer_tier__in=['basic', 'premium', 'enterprise']),
                name='check_user_customer_tier_valid'
            ),
            models.CheckConstraint(
                check=Q(availability_status__in=['available', 'busy', 'away', 'offline']),
                name='check_user_availability_status_valid'
            ),
            
            # Timestamp consistency constraints
            models.CheckConstraint(
                check=Q(updated_at__gte=models.F('created_at')),
                name='check_user_updated_after_created'
            ),
            models.CheckConstraint(
                check=Q(last_active_at__isnull=True) | Q(last_active_at__gte=models.F('created_at'))),
                name='check_user_last_active_after_created'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(role='customer') | Q(customer_tier='basic'),
                name='check_user_customer_tier_only_for_customers'
            ),
            models.CheckConstraint(
                check=Q(role__in=['admin', 'manager', 'agent']) | Q(availability_status='offline'),
                name='check_user_availability_only_for_agents'
            ),
            models.CheckConstraint(
                check=Q(role__in=['admin', 'manager', 'agent']) | Q(max_concurrent_tickets=0),
                name='check_user_max_tickets_only_for_agents'
            ),
        ]
    
    @staticmethod
    def get_organization_constraints():
        """Get enhanced constraints for Organization model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(subscription_tier__in=['basic', 'premium', 'enterprise']),
                name='check_org_subscription_tier_valid'
            ),
            models.CheckConstraint(
                check=Q(updated_at__gte=models.F('created_at')),
                name='check_org_updated_after_created'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(is_active=True) | Q(domain__isnull=True),
                name='check_org_domain_only_when_active'
            ),
        ]
    
    @staticmethod
    def get_ticket_comment_constraints():
        """Get enhanced constraints for TicketComment model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(comment_type__in=['public', 'internal', 'system']),
                name='check_comment_type_valid'
            ),
            models.CheckConstraint(
                check=Q(updated_at__gte=models.F('created_at')),
                name='check_comment_updated_after_created'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(comment_type='system') | Q(author__isnull=False),
                name='check_comment_author_required_for_non_system'
            ),
        ]
    
    @staticmethod
    def get_ticket_attachment_constraints():
        """Get enhanced constraints for TicketAttachment model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(file_size__gte=1),
                name='check_attachment_file_size_positive'
            ),
            models.CheckConstraint(
                check=Q(download_count__gte=0),
                name='check_attachment_download_count_non_negative'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(comment__isnull=True) | Q(ticket=comment__ticket),
                name='check_attachment_comment_belongs_to_same_ticket'
            ),
        ]
    
    @staticmethod
    def get_ticket_history_constraints():
        """Get enhanced constraints for TicketHistory model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(change_type__in=['created', 'updated', 'assigned', 'status_changed', 'priority_changed', 'resolved', 'closed']),
                name='check_history_change_type_valid'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(change_type='created') | Q(user__isnull=False),
                name='check_history_user_required_for_non_created'
            ),
        ]
    
    @staticmethod
    def get_work_order_constraints():
        """Get enhanced constraints for WorkOrder model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(status__in=['pending', 'assigned', 'in_progress', 'completed', 'cancelled']),
                name='check_workorder_status_valid'
            ),
            models.CheckConstraint(
                check=Q(priority__in=['low', 'medium', 'high', 'urgent']),
                name='check_workorder_priority_valid'
            ),
            
            # Timestamp consistency constraints
            models.CheckConstraint(
                check=Q(updated_at__gte=models.F('created_at')),
                name='check_workorder_updated_after_created'
            ),
            models.CheckConstraint(
                check=Q(completed_at__isnull=True) | Q(completed_at__gte=models.F('created_at'))),
                name='check_workorder_completed_after_created'
            ),
            models.CheckConstraint(
                check=Q(scheduled_at__isnull=True) | Q(scheduled_at__gte=models.F('created_at'))),
                name='check_workorder_scheduled_after_created'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(status='completed') | Q(completed_at__isnull=True),
                name='check_workorder_completed_at_only_when_completed'
            ),
            models.CheckConstraint(
                check=Q(status='assigned') | Q(technician__isnull=True),
                name='check_workorder_technician_required_when_assigned'
            ),
        ]
    
    @staticmethod
    def get_kb_article_constraints():
        """Get enhanced constraints for KBArticle model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(status__in=['draft', 'published', 'archived']),
                name='check_kb_article_status_valid'
            ),
            models.CheckConstraint(
                check=Q(view_count__gte=0),
                name='check_kb_article_view_count_non_negative'
            ),
            models.CheckConstraint(
                check=Q(helpful_count__gte=0),
                name='check_kb_article_helpful_count_non_negative'
            ),
            models.CheckConstraint(
                check=Q(not_helpful_count__gte=0),
                name='check_kb_article_not_helpful_count_non_negative'
            ),
            
            # Timestamp consistency constraints
            models.CheckConstraint(
                check=Q(updated_at__gte=models.F('created_at')),
                name='check_kb_article_updated_after_created'
            ),
            models.CheckConstraint(
                check=Q(published_at__isnull=True) | Q(published_at__gte=models.F('created_at'))),
                name='check_kb_article_published_after_created'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(status='published') | Q(is_published=False),
                name='check_kb_article_published_only_when_published'
            ),
            models.CheckConstraint(
                check=Q(status='published') | Q(published_at__isnull=True),
                name='check_kb_article_published_at_only_when_published'
            ),
        ]
    
    @staticmethod
    def get_user_session_constraints():
        """Get enhanced constraints for UserSession model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(last_activity__gte=models.F('created_at')),
                name='check_session_last_activity_after_created'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(is_active=True) | Q(last_activity__lt=models.F('created_at') + models.F('created_at'))),
                name='check_session_inactive_when_expired'
            ),
        ]
    
    @staticmethod
    def get_user_permission_constraints():
        """Get enhanced constraints for UserPermission model."""
        return [
            # Data validation constraints
            models.CheckConstraint(
                check=Q(expires_at__isnull=True) | Q(expires_at__gte=models.F('granted_at'))),
                name='check_permission_expires_after_granted'
            ),
            
            # Business logic constraints
            models.CheckConstraint(
                check=Q(is_active=True) | Q(expires_at__lt=models.F('granted_at'))),
                name='check_permission_inactive_when_expired'
            ),
        ]
    
    @staticmethod
    def get_exclusion_constraints():
        """Get exclusion constraints for preventing conflicts."""
        return [
            # Prevent overlapping SLA policies
            ExclusionConstraint(
                name='exclude_overlapping_sla_policies',
                expressions=[
                    ('organization', '='),
                    ('name', '='),
                ],
                condition=Q(is_active=True)
            ),
            
            # Prevent duplicate active sessions
            ExclusionConstraint(
                name='exclude_duplicate_active_sessions',
                expressions=[
                    ('user', '='),
                    ('session_key', '='),
                ],
                condition=Q(is_active=True)
            ),
        ]
    
    @staticmethod
    def get_unique_constraints():
        """Get unique constraints for data integrity."""
        return [
            # Unique constraints
            models.UniqueConstraint(
                fields=['organization', 'ticket_number'],
                name='unique_org_ticket_number'
            ),
            models.UniqueConstraint(
                fields=['organization', 'slug'],
                name='unique_org_slug'
            ),
            models.UniqueConstraint(
                fields=['organization', 'domain'],
                name='unique_org_domain',
                condition=Q(domain__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'permission'],
                name='unique_user_permission'
            ),
            models.UniqueConstraint(
                fields=['session_key'],
                name='unique_session_key'
            ),
        ]


class EnhancedConstraintsMigration(migrations.Migration):
    """
    Migration to add enhanced database constraints.
    """
    
    dependencies = [
        ('database_optimizations', '0002_add_enhanced_data_integrity_constraints'),
    ]
    
    operations = [
        # Add enhanced constraints for Ticket model
        *[migrations.AddConstraint(
            model_name='ticket',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_ticket_constraints()],
        
        # Add enhanced constraints for User model
        *[migrations.AddConstraint(
            model_name='user',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_user_constraints()],
        
        # Add enhanced constraints for Organization model
        *[migrations.AddConstraint(
            model_name='organization',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_organization_constraints()],
        
        # Add enhanced constraints for TicketComment model
        *[migrations.AddConstraint(
            model_name='ticketcomment',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_ticket_comment_constraints()],
        
        # Add enhanced constraints for TicketAttachment model
        *[migrations.AddConstraint(
            model_name='ticketattachment',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_ticket_attachment_constraints()],
        
        # Add enhanced constraints for TicketHistory model
        *[migrations.AddConstraint(
            model_name='tickethistory',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_ticket_history_constraints()],
        
        # Add enhanced constraints for WorkOrder model
        *[migrations.AddConstraint(
            model_name='workorder',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_work_order_constraints()],
        
        # Add enhanced constraints for KBArticle model
        *[migrations.AddConstraint(
            model_name='kbarticle',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_kb_article_constraints()],
        
        # Add enhanced constraints for UserSession model
        *[migrations.AddConstraint(
            model_name='usersession',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_user_session_constraints()],
        
        # Add enhanced constraints for UserPermission model
        *[migrations.AddConstraint(
            model_name='userpermission',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_user_permission_constraints()],
        
        # Add exclusion constraints
        *[migrations.AddConstraint(
            model_name='slapolicy',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_exclusion_constraints()],
        
        # Add unique constraints
        *[migrations.AddConstraint(
            model_name='ticket',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_unique_constraints()],
    ]


class ConstraintValidator:
    """
    Utility for validating database constraints.
    """
    
    @staticmethod
    def validate_constraints():
        """
        Validate all database constraints.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    conname,
                    contype,
                    confrelid::regclass,
                    conrelid::regclass
                FROM pg_constraint
                WHERE contype IN ('c', 'f', 'u', 'x')
                ORDER BY conname;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def find_constraint_violations():
        """
        Find records that violate constraints.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    constraint_name,
                    constraint_type
                FROM information_schema.table_constraints
                WHERE constraint_type IN ('CHECK', 'UNIQUE', 'FOREIGN KEY', 'EXCLUDE')
                ORDER BY tablename, constraint_name;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def get_constraint_dependencies():
        """
        Get constraint dependencies.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_name, tc.constraint_name;
            """)
            return cursor.fetchall()


# Export utilities
__all__ = [
    'EnhancedConstraints',
    'EnhancedConstraintsMigration',
    'ConstraintValidator'
]
