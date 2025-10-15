"""
Migration to implement all model improvements:
- Standardized soft delete
- Centralized validation
- Enhanced constraints
- Optimized indexes
"""

from django.db import migrations, models
from django.contrib.postgres.operations import AddIndex, CreateExtension
from django.contrib.postgres.indexes import GinIndex, BTreeIndex, HashIndex
from django.contrib.postgres.constraints import ExclusionConstraint
from django.db.models import Q
from .optimized_indexes import OptimizedIndexes
from .enhanced_constraints import EnhancedConstraints


class Migration(migrations.Migration):
    """
    Comprehensive migration for model improvements.
    """
    
    dependencies = [
        ('database_optimizations', '0006_add_materialized_views'),
        ('tickets', '0006_add_materialized_views'),
        ('accounts', '0001_initial'),
        ('organizations', '0001_initial'),
    ]
    
    operations = [
        # Enable required extensions
        CreateExtension('pg_trgm'),
        CreateExtension('btree_gin'),
        
        # Add soft delete fields to existing models
        migrations.AddField(
            model_name='ticket',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Whether this record is active (not soft deleted)'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, help_text='When this record was soft deleted'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='deleted_by',
            field=models.ForeignKey(
                'accounts.User',
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name='ticket_deleted',
                help_text='User who soft deleted this record'
            ),
        ),
        migrations.AddField(
            model_name='ticket',
            name='delete_reason',
            field=models.CharField(max_length=255, blank=True, help_text='Reason for soft deletion'),
        ),
        
        # Add soft delete fields to User model
        migrations.AddField(
            model_name='user',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, help_text='When this record was soft deleted'),
        ),
        migrations.AddField(
            model_name='user',
            name='deleted_by',
            field=models.ForeignKey(
                'accounts.User',
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name='user_deleted',
                help_text='User who soft deleted this record'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='delete_reason',
            field=models.CharField(max_length=255, blank=True, help_text='Reason for soft deletion'),
        ),
        
        # Add soft delete fields to Organization model
        migrations.AddField(
            model_name='organization',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, help_text='When this record was soft deleted'),
        ),
        migrations.AddField(
            model_name='organization',
            name='deleted_by',
            field=models.ForeignKey(
                'accounts.User',
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name='organization_deleted',
                help_text='User who soft deleted this record'
            ),
        ),
        migrations.AddField(
            model_name='organization',
            name='delete_reason',
            field=models.CharField(max_length=255, blank=True, help_text='Reason for soft deletion'),
        ),
        
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
        
        # Add unique constraints
        *[migrations.AddConstraint(
            model_name='ticket',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_unique_constraints()],
        
        # Add exclusion constraints
        *[migrations.AddConstraint(
            model_name='slapolicy',
            constraint=constraint
        ) for constraint in EnhancedConstraints.get_exclusion_constraints()],
    ]
