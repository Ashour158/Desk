"""
Standardized soft delete implementation for all models.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class SoftDeleteModel(models.Model):
    """
    Standardized soft delete base model with consistent behavior.
    """
    
    # Soft delete fields
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this record is active (not soft deleted)"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this record was soft deleted"
    )
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        help_text="User who soft deleted this record"
    )
    delete_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reason for soft deletion"
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None, reason=''):
        """
        Soft delete this record.
        
        Args:
            user: User performing the deletion
            reason: Reason for deletion
        """
        if not self.is_active:
            raise ValidationError("Record is already soft deleted")
        
        self.is_active = False
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.delete_reason = reason
        self.save(update_fields=['is_active', 'deleted_at', 'deleted_by', 'delete_reason'])
        
        logger.info(f"Soft deleted {self.__class__.__name__} {self.pk} by {user} - {reason}")
    
    def restore(self, user=None):
        """
        Restore this soft deleted record.
        
        Args:
            user: User performing the restoration
        """
        if self.is_active:
            raise ValidationError("Record is not soft deleted")
        
        self.is_active = True
        self.deleted_at = None
        self.deleted_by = None
        self.delete_reason = ''
        self.save(update_fields=['is_active', 'deleted_at', 'deleted_by', 'delete_reason'])
        
        logger.info(f"Restored {self.__class__.__name__} {self.pk} by {user}")
    
    def is_deleted(self):
        """Check if record is soft deleted."""
        return not self.is_active
    
    def get_deletion_info(self):
        """Get deletion information."""
        if self.is_active:
            return None
        
        return {
            'deleted_at': self.deleted_at,
            'deleted_by': self.deleted_by,
            'delete_reason': self.delete_reason
        }


class SoftDeleteManager(models.Manager):
    """
    Manager for soft delete functionality.
    """
    
    def active(self):
        """Return only active (non-deleted) records."""
        return self.filter(is_active=True)
    
    def deleted(self):
        """Return only soft deleted records."""
        return self.filter(is_active=False)
    
    def with_deleted(self):
        """Return all records including soft deleted."""
        return self.all()
    
    def delete(self):
        """Override delete to use soft delete."""
        for obj in self:
            obj.soft_delete()
    
    def hard_delete(self):
        """Perform actual database deletion."""
        return super().delete()


class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet for soft delete functionality.
    """
    
    def active(self):
        """Return only active (non-deleted) records."""
        return self.filter(is_active=True)
    
    def deleted(self):
        """Return only soft deleted records."""
        return self.filter(is_active=False)
    
    def with_deleted(self):
        """Return all records including soft deleted."""
        return self.all()
    
    def delete(self):
        """Override delete to use soft delete."""
        for obj in self:
            obj.soft_delete()
    
    def hard_delete(self):
        """Perform actual database deletion."""
        return super().delete()


class EnhancedSoftDeleteModel(SoftDeleteModel):
    """
    Enhanced soft delete model with additional features.
    """
    
    # Additional soft delete fields
    deletion_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the deletion"
    )
    can_be_restored = models.BooleanField(
        default=True,
        help_text="Whether this record can be restored"
    )
    auto_delete_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this record should be automatically hard deleted"
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None, reason='', metadata=None, auto_delete_at=None):
        """
        Enhanced soft delete with additional options.
        
        Args:
            user: User performing the deletion
            reason: Reason for deletion
            metadata: Additional deletion metadata
            auto_delete_at: When to auto-delete (hard delete)
        """
        if not self.is_active:
            raise ValidationError("Record is already soft deleted")
        
        self.is_active = False
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.delete_reason = reason
        self.deletion_metadata = metadata or {}
        self.auto_delete_at = auto_delete_at
        self.save(update_fields=[
            'is_active', 'deleted_at', 'deleted_by', 'delete_reason',
            'deletion_metadata', 'auto_delete_at'
        ])
        
        logger.info(f"Enhanced soft deleted {self.__class__.__name__} {self.pk} by {user} - {reason}")
    
    def can_restore(self):
        """Check if record can be restored."""
        return self.can_be_restored and not self.is_active
    
    def should_auto_delete(self):
        """Check if record should be auto-deleted."""
        if not self.auto_delete_at:
            return False
        return timezone.now() >= self.auto_delete_at
    
    def get_retention_info(self):
        """Get retention information."""
        if self.is_active:
            return None
        
        return {
            'deleted_at': self.deleted_at,
            'deleted_by': self.deleted_by,
            'delete_reason': self.delete_reason,
            'deletion_metadata': self.deletion_metadata,
            'can_be_restored': self.can_be_restored,
            'auto_delete_at': self.auto_delete_at,
            'should_auto_delete': self.should_auto_delete()
        }


class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality to existing models.
    """
    
    def soft_delete(self, user=None, reason=''):
        """Add soft delete functionality to existing models."""
        if hasattr(self, 'is_active') and not self.is_active:
            raise ValidationError("Record is already soft deleted")
        
        # Add soft delete fields if they don't exist
        if not hasattr(self, 'is_active'):
            self.is_active = True
        if not hasattr(self, 'deleted_at'):
            self.deleted_at = None
        if not hasattr(self, 'deleted_by'):
            self.deleted_by = None
        if not hasattr(self, 'delete_reason'):
            self.delete_reason = ''
        
        self.is_active = False
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.delete_reason = reason
        self.save()
        
        logger.info(f"Soft deleted {self.__class__.__name__} {self.pk} by {user} - {reason}")
    
    def restore(self, user=None):
        """Add restore functionality to existing models."""
        if hasattr(self, 'is_active') and self.is_active:
            raise ValidationError("Record is not soft deleted")
        
        self.is_active = True
        self.deleted_at = None
        self.deleted_by = None
        self.delete_reason = ''
        self.save()
        
        logger.info(f"Restored {self.__class__.__name__} {self.pk} by {user}")
    
    def is_deleted(self):
        """Check if record is soft deleted."""
        return hasattr(self, 'is_active') and not self.is_active


# Export utilities
__all__ = [
    'SoftDeleteModel',
    'SoftDeleteManager',
    'SoftDeleteQuerySet',
    'EnhancedSoftDeleteModel',
    'SoftDeleteMixin'
]
