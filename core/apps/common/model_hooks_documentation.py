"""
Comprehensive documentation for model hooks and lifecycle methods.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
from typing import Dict, List, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class ModelHookRegistry:
    """
    Registry for model hooks and lifecycle methods.
    """
    
    def __init__(self):
        self.hooks = {
            'before_save': [],
            'after_save': [],
            'before_create': [],
            'after_create': [],
            'before_update': [],
            'after_update': [],
            'before_delete': [],
            'after_delete': [],
            'before_restore': [],
            'after_restore': [],
            'before_soft_delete': [],
            'after_soft_delete': [],
        }
    
    def register_hook(self, hook_type: str, model_class: str, hook_function: Callable):
        """Register a hook for a specific model."""
        if hook_type not in self.hooks:
            raise ValueError(f"Invalid hook type: {hook_type}")
        
        if model_class not in self.hooks[hook_type]:
            self.hooks[hook_type][model_class] = []
        
        self.hooks[hook_type][model_class].append(hook_function)
        logger.info(f"Registered {hook_type} hook for {model_class}")
    
    def get_hooks(self, hook_type: str, model_class: str) -> List[Callable]:
        """Get hooks for a specific model and hook type."""
        return self.hooks.get(hook_type, {}).get(model_class, [])
    
    def execute_hooks(self, hook_type: str, model_class: str, instance: models.Model, **kwargs):
        """Execute hooks for a specific model and hook type."""
        hooks = self.get_hooks(hook_type, model_class)
        
        for hook in hooks:
            try:
                hook(instance, **kwargs)
            except Exception as e:
                logger.error(f"Error executing {hook_type} hook for {model_class}: {e}")


# Global hook registry
hook_registry = ModelHookRegistry()


def model_hook(hook_type: str, model_class: str):
    """
    Decorator for registering model hooks.
    
    Args:
        hook_type: Type of hook (before_save, after_save, etc.)
        model_class: Name of the model class
    """
    def decorator(func):
        hook_registry.register_hook(hook_type, model_class, func)
        return func
    return decorator


class ModelHooksMixin:
    """
    Mixin to add comprehensive hook functionality to Django models.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_values = {}
        self._is_new = True
    
    def save(self, *args, **kwargs):
        """
        Enhanced save method with comprehensive hooks.
        """
        model_class = self.__class__.__name__
        is_new = self.pk is None
        
        # Store original values for comparison
        if not is_new:
            self._original_values = {field.name: getattr(self, field.name) for field in self._meta.fields}
        
        # Execute before hooks
        if is_new:
            hook_registry.execute_hooks('before_create', model_class, self, **kwargs)
        else:
            hook_registry.execute_hooks('before_update', model_class, self, **kwargs)
        
        hook_registry.execute_hooks('before_save', model_class, self, **kwargs)
        
        # Perform the actual save
        try:
            result = super().save(*args, **kwargs)
            
            # Execute after hooks
            hook_registry.execute_hooks('after_save', model_class, self, **kwargs)
            
            if is_new:
                hook_registry.execute_hooks('after_create', model_class, self, **kwargs)
            else:
                hook_registry.execute_hooks('after_update', model_class, self, **kwargs)
            
            return result
            
        except Exception as e:
            logger.error(f"Error saving {model_class} {self.pk}: {e}")
            raise
    
    def delete(self, *args, **kwargs):
        """
        Enhanced delete method with hooks.
        """
        model_class = self.__class__.__name__
        
        # Execute before hooks
        hook_registry.execute_hooks('before_delete', model_class, self, **kwargs)
        
        # Perform the actual delete
        try:
            result = super().delete(*args, **kwargs)
            
            # Execute after hooks
            hook_registry.execute_hooks('after_delete', model_class, self, **kwargs)
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting {model_class} {self.pk}: {e}")
            raise
    
    def soft_delete(self, user=None, reason=''):
        """
        Soft delete with hooks.
        """
        model_class = self.__class__.__name__
        
        # Execute before hooks
        hook_registry.execute_hooks('before_soft_delete', model_class, self, user=user, reason=reason)
        
        # Perform soft delete
        if hasattr(self, 'is_active'):
            self.is_active = False
            self.deleted_at = timezone.now()
            if hasattr(self, 'deleted_by'):
                self.deleted_by = user
            if hasattr(self, 'delete_reason'):
                self.delete_reason = reason
            self.save()
        
        # Execute after hooks
        hook_registry.execute_hooks('after_soft_delete', model_class, self, user=user, reason=reason)
    
    def restore(self, user=None):
        """
        Restore with hooks.
        """
        model_class = self.__class__.__name__
        
        # Execute before hooks
        hook_registry.execute_hooks('before_restore', model_class, self, user=user)
        
        # Perform restore
        if hasattr(self, 'is_active'):
            self.is_active = True
            if hasattr(self, 'deleted_at'):
                self.deleted_at = None
            if hasattr(self, 'deleted_by'):
                self.deleted_by = None
            if hasattr(self, 'delete_reason'):
                self.delete_reason = ''
            self.save()
        
        # Execute after hooks
        hook_registry.execute_hooks('after_restore', model_class, self, user=user)
    
    def get_changed_fields(self):
        """Get fields that have changed since last save."""
        if not self._original_values:
            return []
        
        changed_fields = []
        for field in self._meta.fields:
            current_value = getattr(self, field.name)
            original_value = self._original_values.get(field.name)
            if current_value != original_value:
                changed_fields.append(field.name)
        
        return changed_fields
    
    def has_field_changed(self, field_name: str):
        """Check if a specific field has changed."""
        if not self._original_values:
            return False
        
        current_value = getattr(self, field_name, None)
        original_value = self._original_values.get(field_name)
        return current_value != original_value


class ModelHooksDocumentation:
    """
    Comprehensive documentation for model hooks.
    """
    
    @staticmethod
    def get_hook_documentation():
        """
        Get comprehensive documentation for all model hooks.
        """
        return {
            'hook_types': {
                'before_save': {
                    'description': 'Executed before any save operation (create or update)',
                    'parameters': ['instance', '**kwargs'],
                    'use_cases': [
                        'Data validation',
                        'Field auto-population',
                        'Business logic enforcement',
                        'Audit trail preparation'
                    ],
                    'examples': [
                        'Auto-generate ticket numbers',
                        'Set organization from context',
                        'Validate business rules',
                        'Prepare audit data'
                    ]
                },
                'after_save': {
                    'description': 'Executed after any save operation (create or update)',
                    'parameters': ['instance', '**kwargs'],
                    'use_cases': [
                        'Post-save processing',
                        'Cache invalidation',
                        'Notification sending',
                        'Integration updates'
                    ],
                    'examples': [
                        'Send email notifications',
                        'Update search indexes',
                        'Trigger webhooks',
                        'Update related records'
                    ]
                },
                'before_create': {
                    'description': 'Executed before creating a new record',
                    'parameters': ['instance', '**kwargs'],
                    'use_cases': [
                        'Initial data setup',
                        'Default value assignment',
                        'Pre-creation validation',
                        'Resource allocation'
                    ],
                    'examples': [
                        'Set default values',
                        'Generate unique identifiers',
                        'Allocate resources',
                        'Set initial status'
                    ]
                },
                'after_create': {
                    'description': 'Executed after creating a new record',
                    'parameters': ['instance', '**kwargs'],
                    'use_cases': [
                        'Welcome notifications',
                        'Initial setup tasks',
                        'Audit trail creation',
                        'Integration setup'
                    ],
                    'examples': [
                        'Send welcome emails',
                        'Create default settings',
                        'Log creation event',
                        'Setup integrations'
                    ]
                },
                'before_update': {
                    'description': 'Executed before updating an existing record',
                    'parameters': ['instance', '**kwargs'],
                    'use_cases': [
                        'Change validation',
                        'Business rule enforcement',
                        'Audit trail preparation',
                        'Conflict resolution'
                    ],
                    'examples': [
                        'Validate status changes',
                        'Check permissions',
                        'Prepare change log',
                        'Resolve conflicts'
                    ]
                },
                'after_update': {
                    'description': 'Executed after updating an existing record',
                    'parameters': ['instance', '**kwargs'],
                    'use_cases': [
                        'Change notifications',
                        'Cache updates',
                        'Integration updates',
                        'Audit trail completion'
                    ],
                    'examples': [
                        'Notify stakeholders',
                        'Update search indexes',
                        'Sync with external systems',
                        'Complete audit trail'
                    ]
                },
                'before_delete': {
                    'description': 'Executed before deleting a record',
                    'parameters': ['instance', '**kwargs'],
                    'use_cases': [
                        'Dependency checking',
                        'Permission validation',
                        'Cleanup preparation',
                        'Audit trail creation'
                    ],
                    'examples': [
                        'Check for dependencies',
                        'Validate delete permissions',
                        'Prepare cleanup tasks',
                        'Create deletion audit'
                    ]
                },
                'after_delete': {
                    'description': 'Executed after deleting a record',
                    'parameters': ['instance', '**kwargs'],
                    'use_cases': [
                        'Cleanup tasks',
                        'Cache invalidation',
                        'Notification sending',
                        'Integration updates'
                    ],
                    'examples': [
                        'Clean up related files',
                        'Invalidate caches',
                        'Notify stakeholders',
                        'Update external systems'
                    ]
                },
                'before_soft_delete': {
                    'description': 'Executed before soft deleting a record',
                    'parameters': ['instance', 'user', 'reason', '**kwargs'],
                    'use_cases': [
                        'Soft delete validation',
                        'Dependency checking',
                        'Permission validation',
                        'Audit preparation'
                    ],
                    'examples': [
                        'Validate soft delete rules',
                        'Check for active dependencies',
                        'Validate user permissions',
                        'Prepare soft delete audit'
                    ]
                },
                'after_soft_delete': {
                    'description': 'Executed after soft deleting a record',
                    'parameters': ['instance', 'user', 'reason', '**kwargs'],
                    'use_cases': [
                        'Post-soft-delete processing',
                        'Notification sending',
                        'Cache updates',
                        'Integration updates'
                    ],
                    'examples': [
                        'Send deletion notifications',
                        'Update search indexes',
                        'Sync with external systems',
                        'Complete soft delete audit'
                    ]
                },
                'before_restore': {
                    'description': 'Executed before restoring a soft deleted record',
                    'parameters': ['instance', 'user', '**kwargs'],
                    'use_cases': [
                        'Restore validation',
                        'Permission checking',
                        'Dependency validation',
                        'Audit preparation'
                    ],
                    'examples': [
                        'Validate restore rules',
                        'Check user permissions',
                        'Validate dependencies',
                        'Prepare restore audit'
                    ]
                },
                'after_restore': {
                    'description': 'Executed after restoring a soft deleted record',
                    'parameters': ['instance', 'user', '**kwargs'],
                    'use_cases': [
                        'Post-restore processing',
                        'Notification sending',
                        'Cache updates',
                        'Integration updates'
                    ],
                    'examples': [
                        'Send restoration notifications',
                        'Update search indexes',
                        'Sync with external systems',
                        'Complete restore audit'
                    ]
                }
            },
            'best_practices': [
                'Keep hooks lightweight and fast',
                'Use hooks for business logic, not data validation',
                'Handle exceptions gracefully in hooks',
                'Document hook dependencies and order',
                'Test hooks thoroughly',
                'Avoid infinite loops in hooks',
                'Use hooks for cross-cutting concerns',
                'Consider performance impact of hooks'
            ],
            'common_patterns': [
                'Audit trail creation',
                'Notification sending',
                'Cache invalidation',
                'Integration updates',
                'Business rule enforcement',
                'Data transformation',
                'Permission checking',
                'Resource management'
            ],
            'anti_patterns': [
                'Heavy computation in hooks',
                'Database queries in hooks',
                'Synchronous external API calls',
                'Complex business logic in hooks',
                'Hooks that modify the same record',
                'Hooks that trigger other hooks',
                'Hooks without error handling',
                'Hooks that block the main thread'
            ]
        }
    
    @staticmethod
    def get_model_hooks_examples():
        """
        Get practical examples of model hooks.
        """
        return {
            'ticket_hooks': {
                'before_save': '''
@model_hook('before_save', 'Ticket')
def auto_generate_ticket_number(instance, **kwargs):
    """Auto-generate ticket number if not provided."""
    if not instance.ticket_number:
        instance.ticket_number = f"TK-{uuid.uuid4().hex[:8].upper()}"
''',
                'after_save': '''
@model_hook('after_save', 'Ticket')
def send_ticket_notifications(instance, **kwargs):
    """Send notifications when ticket is created or updated."""
    if instance.pk:
        # Send notifications to relevant users
        send_ticket_notification.delay(instance.pk)
''',
                'before_update': '''
@model_hook('before_update', 'Ticket')
def validate_status_change(instance, **kwargs):
    """Validate status changes."""
    if instance.has_field_changed('status'):
        # Validate status transition
        validate_ticket_status_transition(instance)
''',
                'after_update': '''
@model_hook('after_update', 'Ticket')
def update_sla_metrics(instance, **kwargs):
    """Update SLA metrics when ticket is updated."""
    if instance.has_field_changed('status'):
        instance.calculate_sla_metrics()
'''
            },
            'user_hooks': {
                'before_save': '''
@model_hook('before_save', 'User')
def set_default_values(instance, **kwargs):
    """Set default values for new users."""
    if not instance.pk:
        instance.timezone = instance.timezone or 'UTC'
        instance.language = instance.language or 'en'
''',
                'after_create': '''
@model_hook('after_create', 'User')
def setup_user_account(instance, **kwargs):
    """Setup new user account."""
    # Create default settings
    create_user_defaults.delay(instance.pk)
    # Send welcome email
    send_welcome_email.delay(instance.pk)
''',
                'after_update': '''
@model_hook('after_update', 'User')
def update_user_activity(instance, **kwargs):
    """Update user activity tracking."""
    if instance.has_field_changed('last_active_at'):
        # Update activity metrics
        update_user_activity_metrics.delay(instance.pk)
'''
            },
            'organization_hooks': {
                'before_save': '''
@model_hook('before_save', 'Organization')
def generate_slug(instance, **kwargs):
    """Generate slug from name if not provided."""
    if not instance.slug and instance.name:
        instance.slug = slugify(instance.name)
''',
                'after_create': '''
@model_hook('after_create', 'Organization')
def setup_organization(instance, **kwargs):
    """Setup new organization."""
    # Create default settings
    create_organization_defaults.delay(instance.pk)
    # Create default departments
    create_default_departments.delay(instance.pk)
'''
            }
        }


# Export utilities
__all__ = [
    'ModelHookRegistry',
    'model_hook',
    'ModelHooksMixin',
    'ModelHooksDocumentation',
    'hook_registry'
]
