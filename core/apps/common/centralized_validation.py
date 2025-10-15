"""
Centralized validation system for all models.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from apps.tickets.models import Ticket, TicketComment, TicketAttachment
from apps.accounts.models import User
import re
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

User = get_user_model()


class ValidationRule:
    """
    Base class for validation rules.
    """
    
    def __init__(self, field_name: str, error_message: str = None):
        self.field_name = field_name
        self.error_message = error_message or f"Invalid value for {field_name}"
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        """Validate a field value."""
        raise NotImplementedError("Subclasses must implement validate method")
    
    def get_error_message(self, value: Any, model_instance: models.Model) -> str:
        """Get error message for validation failure."""
        return self.error_message


class RequiredValidationRule(ValidationRule):
    """Validation rule for required fields."""
    
    def __init__(self, field_name: str, error_message: str = None):
        super().__init__(field_name, error_message or f"{field_name} is required")
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        return value is not None and str(value).strip() != ''


class EmailValidationRule(ValidationRule):
    """Validation rule for email fields."""
    
    def __init__(self, field_name: str, error_message: str = None):
        super().__init__(field_name, error_message or f"Invalid email format for {field_name}")
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, str(value)))


class ChoiceValidationRule(ValidationRule):
    """Validation rule for choice fields."""
    
    def __init__(self, field_name: str, valid_choices: List[str], error_message: str = None):
        super().__init__(field_name, error_message or f"Invalid choice for {field_name}")
        self.valid_choices = valid_choices
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        return str(value) in self.valid_choices


class RangeValidationRule(ValidationRule):
    """Validation rule for numeric ranges."""
    
    def __init__(self, field_name: str, min_value: Union[int, float] = None, max_value: Union[int, float] = None, error_message: str = None):
        super().__init__(field_name, error_message or f"Value for {field_name} must be between {min_value} and {max_value}")
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        if value is None:
            return True  # Let required validation handle empty values
        
        try:
            numeric_value = float(value)
            if self.min_value is not None and numeric_value < self.min_value:
                return False
            if self.max_value is not None and numeric_value > self.max_value:
                return False
            return True
        except (ValueError, TypeError):
            return False


class ForeignKeyValidationRule(ValidationRule):
    """Validation rule for foreign key relationships."""
    
    def __init__(self, field_name: str, target_model: models.Model, error_message: str = None):
        super().__init__(field_name, error_message or f"Invalid {field_name} reference")
        self.target_model = target_model
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        try:
            if hasattr(value, 'pk'):
                return self.target_model.objects.filter(pk=value.pk).exists()
            else:
                return self.target_model.objects.filter(pk=value).exists()
        except (ValueError, TypeError):
            return False


class RoleBasedValidationRule(ValidationRule):
    """Validation rule for role-based access control."""
    
    def __init__(self, field_name: str, allowed_roles: List[str], error_message: str = None):
        super().__init__(field_name, error_message or f"User must have one of these roles: {allowed_roles}")
        self.allowed_roles = allowed_roles
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        try:
            if hasattr(value, 'role'):
                return value.role in self.allowed_roles
            else:
                user = User.objects.get(pk=value)
                return user.role in self.allowed_roles
        except (User.DoesNotExist, AttributeError):
            return False


class TimestampValidationRule(ValidationRule):
    """Validation rule for timestamp consistency."""
    
    def __init__(self, field_name: str, reference_field: str, error_message: str = None):
        super().__init__(field_name, error_message or f"{field_name} must be after {reference_field}")
        self.reference_field = reference_field
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        try:
            reference_value = getattr(model_instance, self.reference_field)
            if not reference_value:
                return True  # No reference to compare against
            
            return value >= reference_value
        except AttributeError:
            return False


class CentralizedValidator:
    """
    Centralized validation system for all models.
    """
    
    def __init__(self):
        self.validation_rules = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules for common models."""
        
        # User model validation rules
        self.add_model_rules('User', [
            RequiredValidationRule('email'),
            EmailValidationRule('email'),
            RequiredValidationRule('first_name'),
            RequiredValidationRule('last_name'),
            ChoiceValidationRule('role', ['admin', 'manager', 'agent', 'customer']),
            ChoiceValidationRule('customer_tier', ['basic', 'premium', 'enterprise']),
            ChoiceValidationRule('availability_status', ['available', 'busy', 'away', 'offline']),
            RangeValidationRule('max_concurrent_tickets', min_value=1, max_value=100),
            ForeignKeyValidationRule('organization', Organization),
        ])
        
        # Ticket model validation rules
        self.add_model_rules('Ticket', [
            RequiredValidationRule('subject'),
            RequiredValidationRule('description'),
            ChoiceValidationRule('status', ['new', 'open', 'pending', 'resolved', 'closed', 'cancelled']),
            ChoiceValidationRule('priority', ['low', 'medium', 'high', 'urgent']),
            ChoiceValidationRule('channel', ['email', 'web', 'phone', 'chat', 'social', 'api']),
            RangeValidationRule('customer_satisfaction_score', min_value=1, max_value=5),
            ForeignKeyValidationRule('organization', Organization),
            RoleBasedValidationRule('customer', ['customer']),
            RoleBasedValidationRule('assigned_agent', ['admin', 'manager', 'agent']),
            TimestampValidationRule('updated_at', 'created_at'),
            TimestampValidationRule('resolved_at', 'created_at'),
            TimestampValidationRule('first_response_at', 'created_at'),
            TimestampValidationRule('closed_at', 'created_at'),
        ])
        
        # TicketComment model validation rules
        self.add_model_rules('TicketComment', [
            RequiredValidationRule('content'),
            ChoiceValidationRule('comment_type', ['public', 'internal', 'system']),
            ForeignKeyValidationRule('ticket', Ticket),
            ForeignKeyValidationRule('author', User),
            TimestampValidationRule('updated_at', 'created_at'),
        ])
        
        # TicketAttachment model validation rules
        self.add_model_rules('TicketAttachment', [
            RequiredValidationRule('file_name'),
            RequiredValidationRule('file_path'),
            RangeValidationRule('file_size', min_value=1),
            RangeValidationRule('download_count', min_value=0),
            ForeignKeyValidationRule('ticket', Ticket),
            ForeignKeyValidationRule('uploaded_by', User),
        ])
        
        # Organization model validation rules
        self.add_model_rules('Organization', [
            RequiredValidationRule('name'),
            RequiredValidationRule('slug'),
            ChoiceValidationRule('subscription_tier', ['basic', 'premium', 'enterprise']),
            TimestampValidationRule('updated_at', 'created_at'),
        ])
    
    def add_model_rules(self, model_name: str, rules: List[ValidationRule]):
        """Add validation rules for a specific model."""
        if model_name not in self.validation_rules:
            self.validation_rules[model_name] = []
        self.validation_rules[model_name].extend(rules)
    
    def add_rule(self, model_name: str, rule: ValidationRule):
        """Add a single validation rule for a model."""
        if model_name not in self.validation_rules:
            self.validation_rules[model_name] = []
        self.validation_rules[model_name].append(rule)
    
    def validate_model(self, model_instance: models.Model) -> List[str]:
        """
        Validate a model instance using centralized rules.
        
        Args:
            model_instance: The model instance to validate
            
        Returns:
            List of error messages (empty if validation passes)
        """
        model_name = model_instance.__class__.__name__
        errors = []
        
        if model_name not in self.validation_rules:
            logger.warning(f"No validation rules found for model {model_name}")
            return errors
        
        for rule in self.validation_rules[model_name]:
            try:
                field_value = getattr(model_instance, rule.field_name, None)
                if not rule.validate(field_value, model_instance):
                    errors.append(rule.get_error_message(field_value, model_instance))
            except Exception as e:
                logger.error(f"Validation error for {model_name}.{rule.field_name}: {e}")
                errors.append(f"Validation error for {rule.field_name}: {str(e)}")
        
        return errors
    
    def validate_field(self, model_instance: models.Model, field_name: str) -> List[str]:
        """
        Validate a specific field of a model instance.
        
        Args:
            model_instance: The model instance to validate
            field_name: The field name to validate
            
        Returns:
            List of error messages (empty if validation passes)
        """
        model_name = model_instance.__class__.__name__
        errors = []
        
        if model_name not in self.validation_rules:
            return errors
        
        for rule in self.validation_rules[model_name]:
            if rule.field_name == field_name:
                try:
                    field_value = getattr(model_instance, field_name, None)
                    if not rule.validate(field_value, model_instance):
                        errors.append(rule.get_error_message(field_value, model_instance))
                except Exception as e:
                    logger.error(f"Validation error for {model_name}.{field_name}: {e}")
                    errors.append(f"Validation error for {field_name}: {str(e)}")
        
        return errors
    
    def get_model_rules(self, model_name: str) -> List[ValidationRule]:
        """Get validation rules for a specific model."""
        return self.validation_rules.get(model_name, [])
    
    def get_field_rules(self, model_name: str, field_name: str) -> List[ValidationRule]:
        """Get validation rules for a specific field of a model."""
        rules = self.get_model_rules(model_name)
        return [rule for rule in rules if rule.field_name == field_name]


class CentralizedValidationMixin:
    """
    Mixin to add centralized validation to Django models.
    """
    
    def clean(self):
        """Override clean method to use centralized validation."""
        super().clean()
        
        validator = CentralizedValidator()
        errors = validator.validate_model(self)
        
        if errors:
            raise ValidationError(errors)
    
    def validate_field(self, field_name: str):
        """Validate a specific field."""
        validator = CentralizedValidator()
        errors = validator.validate_field(self, field_name)
        
        if errors:
            raise ValidationError(errors)
    
    def get_validation_errors(self):
        """Get all validation errors for this instance."""
        validator = CentralizedValidator()
        return validator.validate_model(self)
    
    def is_valid(self):
        """Check if the model instance is valid."""
        return len(self.get_validation_errors()) == 0


class ValidationManager:
    """
    Manager for validation operations.
    """
    
    def __init__(self):
        self.validator = CentralizedValidator()
    
    def validate_bulk(self, model_instances: List[models.Model]) -> Dict[str, List[str]]:
        """
        Validate multiple model instances.
        
        Args:
            model_instances: List of model instances to validate
            
        Returns:
            Dictionary mapping instance IDs to error lists
        """
        results = {}
        
        for instance in model_instances:
            errors = self.validator.validate_model(instance)
            results[f"{instance.__class__.__name__}_{instance.pk}"] = errors
        
        return results
    
    def validate_model_class(self, model_class: models.Model, data: Dict[str, Any]) -> List[str]:
        """
        Validate data against a model class without creating an instance.
        
        Args:
            model_class: The model class to validate against
            data: Dictionary of field values
            
        Returns:
            List of error messages
        """
        # Create a temporary instance for validation
        instance = model_class(**data)
        return self.validator.validate_model(instance)
    
    def get_validation_summary(self, model_instances: List[models.Model]) -> Dict[str, Any]:
        """
        Get validation summary for multiple instances.
        
        Args:
            model_instances: List of model instances to validate
            
        Returns:
            Validation summary dictionary
        """
        results = self.validate_bulk(model_instances)
        
        total_instances = len(model_instances)
        valid_instances = sum(1 for errors in results.values() if not errors)
        invalid_instances = total_instances - valid_instances
        
        return {
            'total_instances': total_instances,
            'valid_instances': valid_instances,
            'invalid_instances': invalid_instances,
            'validation_rate': (valid_instances / total_instances) * 100 if total_instances > 0 else 0,
            'errors': results
        }


# Global validator instance
centralized_validator = CentralizedValidator()

# Export utilities
__all__ = [
    'ValidationRule',
    'RequiredValidationRule',
    'EmailValidationRule',
    'ChoiceValidationRule',
    'RangeValidationRule',
    'ForeignKeyValidationRule',
    'RoleBasedValidationRule',
    'TimestampValidationRule',
    'CentralizedValidator',
    'CentralizedValidationMixin',
    'ValidationManager',
    'centralized_validator'
]
