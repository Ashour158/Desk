"""
Optimized database indexes for improved performance.
"""

from django.db import migrations, models
from django.contrib.postgres.operations import AddIndex, CreateExtension
from django.contrib.postgres.indexes import GinIndex, BTreeIndex, HashIndex
from django.contrib.postgres.search import SearchVector
from django.db.models import Q


class OptimizedIndexes:
    """
    Comprehensive database index optimization utilities.
    """
    
    @staticmethod
    def get_ticket_indexes():
        """Get optimized indexes for Ticket model."""
        return [
            # Primary performance indexes
            models.Index(fields=['organization', 'status'], name='idx_ticket_org_status'),
            models.Index(fields=['organization', 'assigned_agent'], name='idx_ticket_org_agent'),
            models.Index(fields=['organization', 'customer'], name='idx_ticket_org_customer'),
            models.Index(fields=['organization', 'priority', 'status'], name='idx_ticket_org_priority_status'),
            models.Index(fields=['organization', 'created_at'], name='idx_ticket_org_created'),
            models.Index(fields=['organization', 'updated_at'], name='idx_ticket_org_updated'),
            
            # SLA and performance indexes
            models.Index(fields=['first_response_due'], name='idx_ticket_first_response_due'),
            models.Index(fields=['resolution_due'], name='idx_ticket_resolution_due'),
            models.Index(fields=['sla_breach'], name='idx_ticket_sla_breach'),
            models.Index(fields=['status', 'priority'], name='idx_ticket_status_priority'),
            
            # Channel and source indexes
            models.Index(fields=['channel'], name='idx_ticket_channel'),
            models.Index(fields=['source'], name='idx_ticket_source'),
            
            # Category and tag indexes
            models.Index(fields=['category'], name='idx_ticket_category'),
            models.Index(fields=['subcategory'], name='idx_ticket_subcategory'),
            
            # Analytics indexes
            models.Index(fields=['customer_satisfaction_score'], name='idx_ticket_satisfaction'),
            models.Index(fields=['time_to_first_response'], name='idx_ticket_first_response_time'),
            models.Index(fields=['time_to_resolution'], name='idx_ticket_resolution_time'),
            
            # Composite indexes for common queries
            models.Index(fields=['organization', 'status', 'priority'], name='idx_ticket_org_status_priority'),
            models.Index(fields=['organization', 'assigned_agent', 'status'], name='idx_ticket_org_agent_status'),
            models.Index(fields=['organization', 'customer', 'status'], name='idx_ticket_org_customer_status'),
            models.Index(fields=['organization', 'created_at', 'status'], name='idx_ticket_org_created_status'),
            
            # Partial indexes for performance
            models.Index(
                fields=['organization', 'assigned_agent'],
                condition=Q(status__in=['new', 'open', 'pending']),
                name='idx_ticket_active_org_agent'
            ),
            models.Index(
                fields=['organization', 'customer'],
                condition=Q(status__in=['new', 'open', 'pending', 'resolved']),
                name='idx_ticket_customer_org_status'
            ),
            models.Index(
                fields=['sla_breach'],
                condition=Q(sla_breach=True),
                name='idx_ticket_sla_breach_true'
            ),
        ]
    
    @staticmethod
    def get_user_indexes():
        """Get optimized indexes for User model."""
        return [
            # Primary performance indexes
            models.Index(fields=['organization', 'role'], name='idx_user_org_role'),
            models.Index(fields=['organization', 'is_active'], name='idx_user_org_active'),
            models.Index(fields=['role', 'is_active'], name='idx_user_role_active'),
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['username'], name='idx_user_username'),
            
            # Activity and performance indexes
            models.Index(fields=['last_active_at'], name='idx_user_last_active'),
            models.Index(fields=['created_at'], name='idx_user_created'),
            models.Index(fields=['updated_at'], name='idx_user_updated'),
            
            # Customer tier and availability indexes
            models.Index(fields=['customer_tier'], name='idx_user_customer_tier'),
            models.Index(fields=['availability_status'], name='idx_user_availability'),
            models.Index(fields=['max_concurrent_tickets'], name='idx_user_max_tickets'),
            
            # Notification preferences indexes
            models.Index(fields=['email_notifications'], name='idx_user_email_notifications'),
            models.Index(fields=['sms_notifications'], name='idx_user_sms_notifications'),
            models.Index(fields=['push_notifications'], name='idx_user_push_notifications'),
            
            # Composite indexes for common queries
            models.Index(fields=['organization', 'role', 'is_active'], name='idx_user_org_role_active'),
            models.Index(fields=['role', 'availability_status'], name='idx_user_role_availability'),
            models.Index(fields=['organization', 'customer_tier'], name='idx_user_org_tier'),
            
            # Partial indexes for performance
            models.Index(
                fields=['organization', 'role'],
                condition=Q(role__in=['admin', 'manager', 'agent']),
                name='idx_user_org_agents'
            ),
            models.Index(
                fields=['organization', 'customer_tier'],
                condition=Q(role='customer'),
                name='idx_user_org_customer_tier'
            ),
            models.Index(
                fields=['availability_status'],
                condition=Q(role__in=['admin', 'manager', 'agent']),
                name='idx_user_agent_availability'
            ),
        ]
    
    @staticmethod
    def get_organization_indexes():
        """Get optimized indexes for Organization model."""
        return [
            # Primary performance indexes
            models.Index(fields=['slug'], name='idx_org_slug'),
            models.Index(fields=['domain'], name='idx_org_domain'),
            models.Index(fields=['is_active'], name='idx_org_active'),
            models.Index(fields=['subscription_tier'], name='idx_org_subscription'),
            models.Index(fields=['created_at'], name='idx_org_created'),
            models.Index(fields=['updated_at'], name='idx_org_updated'),
            
            # Composite indexes for common queries
            models.Index(fields=['is_active', 'subscription_tier'], name='idx_org_active_subscription'),
            models.Index(fields=['created_at', 'is_active'], name='idx_org_created_active'),
        ]
    
    @staticmethod
    def get_ticket_comment_indexes():
        """Get optimized indexes for TicketComment model."""
        return [
            # Primary performance indexes
            models.Index(fields=['ticket', 'created_at'], name='idx_comment_ticket_created'),
            models.Index(fields=['author', 'created_at'], name='idx_comment_author_created'),
            models.Index(fields=['comment_type'], name='idx_comment_type'),
            models.Index(fields=['has_attachments'], name='idx_comment_attachments'),
            
            # Composite indexes for common queries
            models.Index(fields=['ticket', 'comment_type'], name='idx_comment_ticket_type'),
            models.Index(fields=['author', 'comment_type'], name='idx_comment_author_type'),
            models.Index(fields=['ticket', 'author'], name='idx_comment_ticket_author'),
        ]
    
    @staticmethod
    def get_ticket_attachment_indexes():
        """Get optimized indexes for TicketAttachment model."""
        return [
            # Primary performance indexes
            models.Index(fields=['ticket', 'uploaded_at'], name='idx_attachment_ticket_uploaded'),
            models.Index(fields=['uploaded_by', 'uploaded_at'], name='idx_attachment_uploader_uploaded'),
            models.Index(fields=['file_type'], name='idx_attachment_file_type'),
            models.Index(fields=['is_public'], name='idx_attachment_public'),
            models.Index(fields=['download_count'], name='idx_attachment_downloads'),
            
            # Composite indexes for common queries
            models.Index(fields=['ticket', 'is_public'], name='idx_attachment_ticket_public'),
            models.Index(fields=['uploaded_by', 'file_type'], name='idx_attachment_uploader_type'),
            models.Index(fields=['ticket', 'file_type'], name='idx_attachment_ticket_type'),
        ]
    
    @staticmethod
    def get_ticket_history_indexes():
        """Get optimized indexes for TicketHistory model."""
        return [
            # Primary performance indexes
            models.Index(fields=['ticket', 'created_at'], name='idx_history_ticket_created'),
            models.Index(fields=['user', 'created_at'], name='idx_history_user_created'),
            models.Index(fields=['change_type'], name='idx_history_change_type'),
            models.Index(fields=['field_name'], name='idx_history_field_name'),
            
            # Composite indexes for common queries
            models.Index(fields=['ticket', 'change_type'], name='idx_history_ticket_type'),
            models.Index(fields=['user', 'change_type'], name='idx_history_user_type'),
            models.Index(fields=['ticket', 'field_name'], name='idx_history_ticket_field'),
        ]
    
    @staticmethod
    def get_work_order_indexes():
        """Get optimized indexes for WorkOrder model."""
        return [
            # Primary performance indexes
            models.Index(fields=['organization', 'status'], name='idx_workorder_org_status'),
            models.Index(fields=['organization', 'technician'], name='idx_workorder_org_technician'),
            models.Index(fields=['organization', 'customer'], name='idx_workorder_org_customer'),
            models.Index(fields=['organization', 'priority'], name='idx_workorder_org_priority'),
            models.Index(fields=['organization', 'created_at'], name='idx_workorder_org_created'),
            models.Index(fields=['organization', 'scheduled_at'], name='idx_workorder_org_scheduled'),
            models.Index(fields=['organization', 'completed_at'], name='idx_workorder_org_completed'),
            
            # Composite indexes for common queries
            models.Index(fields=['organization', 'status', 'priority'], name='idx_workorder_org_status_priority'),
            models.Index(fields=['organization', 'technician', 'status'], name='idx_workorder_org_technician_status'),
            models.Index(fields=['organization', 'customer', 'status'], name='idx_workorder_org_customer_status'),
        ]
    
    @staticmethod
    def get_kb_article_indexes():
        """Get optimized indexes for KBArticle model."""
        return [
            # Primary performance indexes
            models.Index(fields=['organization', 'category'], name='idx_kb_org_category'),
            models.Index(fields=['organization', 'status'], name='idx_kb_org_status'),
            models.Index(fields=['organization', 'is_published'], name='idx_kb_org_published'),
            models.Index(fields=['organization', 'view_count'], name='idx_kb_org_views'),
            models.Index(fields=['organization', 'created_at'], name='idx_kb_org_created'),
            models.Index(fields=['organization', 'updated_at'], name='idx_kb_org_updated'),
            
            # Composite indexes for common queries
            models.Index(fields=['organization', 'category', 'is_published'], name='idx_kb_org_category_published'),
            models.Index(fields=['organization', 'status', 'is_published'], name='idx_kb_org_status_published'),
            models.Index(fields=['category', 'is_published'], name='idx_kb_category_published'),
        ]
    
    @staticmethod
    def get_full_text_search_indexes():
        """Get full-text search indexes for search functionality."""
        return [
            # Full-text search indexes using GIN
            GinIndex(
                fields=['subject', 'description'],
                name='idx_ticket_search_gin',
                opclasses=['gin_trgm_ops', 'gin_trgm_ops']
            ),
            GinIndex(
                fields=['content'],
                name='idx_comment_search_gin',
                opclasses=['gin_trgm_ops']
            ),
            GinIndex(
                fields=['title', 'content'],
                name='idx_kb_search_gin',
                opclasses=['gin_trgm_ops', 'gin_trgm_ops']
            ),
            GinIndex(
                fields=['first_name', 'last_name', 'email'],
                name='idx_user_search_gin',
                opclasses=['gin_trgm_ops', 'gin_trgm_ops', 'gin_trgm_ops']
            ),
        ]
    
    @staticmethod
    def get_json_field_indexes():
        """Get indexes for JSON fields."""
        return [
            # JSON field indexes using GIN
            GinIndex(
                fields=['tags'],
                name='idx_ticket_tags_gin'
            ),
            GinIndex(
                fields=['custom_fields'],
                name='idx_ticket_custom_fields_gin'
            ),
            GinIndex(
                fields=['skills'],
                name='idx_user_skills_gin'
            ),
            GinIndex(
                fields=['certifications'],
                name='idx_user_certifications_gin'
            ),
            GinIndex(
                fields=['settings'],
                name='idx_org_settings_gin'
            ),
        ]
    
    @staticmethod
    def get_partial_indexes():
        """Get partial indexes for specific conditions."""
        return [
            # Partial indexes for active records
            models.Index(
                fields=['organization', 'status'],
                condition=Q(is_active=True),
                name='idx_ticket_active_org_status'
            ),
            models.Index(
                fields=['organization', 'role'],
                condition=Q(is_active=True),
                name='idx_user_active_org_role'
            ),
            models.Index(
                fields=['organization', 'is_published'],
                condition=Q(is_published=True),
                name='idx_kb_published_org'
            ),
            
            # Partial indexes for specific statuses
            models.Index(
                fields=['organization', 'assigned_agent'],
                condition=Q(status__in=['new', 'open', 'pending']),
                name='idx_ticket_active_org_agent'
            ),
            models.Index(
                fields=['organization', 'customer'],
                condition=Q(role__in=['admin', 'manager', 'agent']),
                name='idx_user_org_agents'
            ),
        ]


class IndexOptimizationMigration(migrations.Migration):
    """
    Migration to add optimized indexes.
    """
    
    dependencies = [
        ('tickets', '0006_add_materialized_views'),
        ('accounts', '0001_initial'),
        ('organizations', '0001_initial'),
    ]
    
    operations = [
        # Add optimized indexes for Ticket model
        *[AddIndex(
            model_name='ticket',
            index=index
        ) for index in OptimizedIndexes.get_ticket_indexes()],
        
        # Add optimized indexes for User model
        *[AddIndex(
            model_name='user',
            index=index
        ) for index in OptimizedIndexes.get_user_indexes()],
        
        # Add optimized indexes for Organization model
        *[AddIndex(
            model_name='organization',
            index=index
        ) for index in OptimizedIndexes.get_organization_indexes()],
        
        # Add optimized indexes for TicketComment model
        *[AddIndex(
            model_name='ticketcomment',
            index=index
        ) for index in OptimizedIndexes.get_ticket_comment_indexes()],
        
        # Add optimized indexes for TicketAttachment model
        *[AddIndex(
            model_name='ticketattachment',
            index=index
        ) for index in OptimizedIndexes.get_ticket_attachment_indexes()],
        
        # Add optimized indexes for TicketHistory model
        *[AddIndex(
            model_name='tickethistory',
            index=index
        ) for index in OptimizedIndexes.get_ticket_history_indexes()],
        
        # Add full-text search indexes
        *[AddIndex(
            model_name='ticket',
            index=index
        ) for index in OptimizedIndexes.get_full_text_search_indexes()],
        
        # Add JSON field indexes
        *[AddIndex(
            model_name='ticket',
            index=index
        ) for index in OptimizedIndexes.get_json_field_indexes()],
        
        # Add partial indexes
        *[AddIndex(
            model_name='ticket',
            index=index
        ) for index in OptimizedIndexes.get_partial_indexes()],
    ]


class IndexPerformanceAnalyzer:
    """
    Utility for analyzing index performance.
    """
    
    @staticmethod
    def analyze_index_usage():
        """
        Analyze index usage statistics.
        """
        from django.db import connection
        
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
    def find_unused_indexes():
        """
        Find unused indexes that can be removed.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan
                FROM pg_stat_user_indexes
                WHERE idx_scan = 0
                AND indexname NOT LIKE '%_pkey'
                ORDER BY tablename, indexname;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def find_duplicate_indexes():
        """
        Find duplicate indexes.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexdef;
            """)
            return cursor.fetchall()
    
    @staticmethod
    def get_index_size():
        """
        Get index size information.
        """
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    pg_size_pretty(pg_relation_size(indexrelid)) as size
                FROM pg_stat_user_indexes
                ORDER BY pg_relation_size(indexrelid) DESC;
            """)
            return cursor.fetchall()


# Export utilities
__all__ = [
    'OptimizedIndexes',
    'IndexOptimizationMigration',
    'IndexPerformanceAnalyzer'
]
