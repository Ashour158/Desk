"""
Enhanced centralized validation with field-level validation and custom validation rules.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from apps.tickets.models import Ticket, TicketComment
from apps.accounts.models import User
import re
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

User = get_user_model()


class FieldValidationRule:
    """
    Base class for field-level validation rules.
    """
    
    def __init__(self, field_name: str, error_message: str = None, custom_validator: Callable = None):
        self.field_name = field_name
        self.error_message = error_message or f"Invalid value for {field_name}"
        self.custom_validator = custom_validator
    
    def validate(self, value: Any, model_instance: models.Model) -> bool:
        """Validate a field value."""
        if self.custom_validator:
            return self.custom_validator(value, model_instance)
        return self._validate(value, model_instance)
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        """Override in subclasses for specific validation logic."""
        raise NotImplementedError("Subclasses must implement _validate method")
    
    def get_error_message(self, value: Any, model_instance: models.Model) -> str:
        """Get error message for validation failure."""
        return self.error_message


class RequiredFieldValidationRule(FieldValidationRule):
    """Validation rule for required fields."""
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        return value is not None and value != ''


class EmailValidationRule(FieldValidationRule):
    """Validation rule for email fields."""
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, value))


class PhoneValidationRule(FieldValidationRule):
    """Validation rule for phone number fields."""
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        # International phone number pattern
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(phone_pattern, value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')))


class ChoiceValidationRule(FieldValidationRule):
    """Validation rule for choice fields."""
    
    def __init__(self, field_name: str, choices: List[str], error_message: str = None):
        super().__init__(field_name, error_message)
        self.choices = choices
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        return value in self.choices


class RangeValidationRule(FieldValidationRule):
    """Validation rule for numeric range fields."""
    
    def __init__(self, field_name: str, min_value: float = None, max_value: float = None, error_message: str = None):
        super().__init__(field_name, error_message)
        self.min_value = min_value
        self.max_value = max_value
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
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


class LengthValidationRule(FieldValidationRule):
    """Validation rule for string length fields."""
    
    def __init__(self, field_name: str, min_length: int = None, max_length: int = None, error_message: str = None):
        super().__init__(field_name, error_message)
        self.min_length = min_length
        self.max_length = max_length
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        string_value = str(value)
        if self.min_length is not None and len(string_value) < self.min_length:
            return False
        if self.max_length is not None and len(string_value) > self.max_length:
            return False
        return True


class ForeignKeyValidationRule(FieldValidationRule):
    """Validation rule for foreign key fields."""
    
    def __init__(self, field_name: str, model_class: models.Model, error_message: str = None):
        super().__init__(field_name, error_message)
        self.model_class = model_class
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        try:
            if isinstance(value, self.model_class):
                return True
            elif isinstance(value, (int, str)):
                return self.model_class.objects.filter(pk=value).exists()
            return False
        except Exception:
            return False


class UniqueValidationRule(FieldValidationRule):
    """Validation rule for unique fields."""
    
    def __init__(self, field_name: str, model_class: models.Model, exclude_instance: bool = True, error_message: str = None):
        super().__init__(field_name, error_message)
        self.model_class = model_class
        self.exclude_instance = exclude_instance
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        try:
            queryset = self.model_class.objects.filter(**{self.field_name: value})
            if self.exclude_instance and hasattr(model_instance, 'pk') and model_instance.pk:
                queryset = queryset.exclude(pk=model_instance.pk)
            return not queryset.exists()
        except Exception:
            return False


class DateRangeValidationRule(FieldValidationRule):
    """Validation rule for date range fields."""
    
    def __init__(self, field_name: str, min_date: datetime = None, max_date: datetime = None, error_message: str = None):
        super().__init__(field_name, error_message)
        self.min_date = min_date
        self.max_date = max_date
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        if not value:
            return True  # Let required validation handle empty values
        
        try:
            if isinstance(value, str):
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            
            if self.min_date and value < self.min_date:
                return False
            if self.max_date and value > self.max_date:
                return False
            return True
        except (ValueError, TypeError):
            return False


class CrossFieldValidationRule(FieldValidationRule):
    """Validation rule for cross-field validation."""
    
    def __init__(self, field_name: str, related_fields: List[str], validator_func: Callable, error_message: str = None):
        super().__init__(field_name, error_message)
        self.related_fields = related_fields
        self.validator_func = validator_func
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        try:
            # Get related field values
            related_values = {}
            for field in self.related_fields:
                related_values[field] = getattr(model_instance, field, None)
            
            # Call validator function with all values
            return self.validator_func(value, related_values, model_instance)
        except Exception:
            return False


class BusinessRuleValidationRule(FieldValidationRule):
    """Validation rule for business logic validation."""
    
    def __init__(self, field_name: str, business_rule_func: Callable, error_message: str = None):
        super().__init__(field_name, error_message)
        self.business_rule_func = business_rule_func
    
    def _validate(self, value: Any, model_instance: models.Model) -> bool:
        try:
            return self.business_rule_func(value, model_instance)
        except Exception:
            return False


class EnhancedCentralizedValidator:
    """
    Enhanced centralized validation system with field-level validation.
    """
    
    def __init__(self):
        self.validation_rules = {}
        self.field_rules = {}
        self.cross_field_rules = {}
        self.business_rules = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules for common models."""
        
        # User model validation rules
        self.add_model_rules('User', [
            RequiredFieldValidationRule('email'),
            EmailValidationRule('email'),
            RequiredFieldValidationRule('first_name'),
            RequiredFieldValidationRule('last_name'),
            ChoiceValidationRule('role', ['admin', 'manager', 'agent', 'customer']),
            ChoiceValidationRule('customer_tier', ['basic', 'premium', 'enterprise']),
            ChoiceValidationRule('availability_status', ['available', 'busy', 'away', 'offline']),
            RangeValidationRule('max_concurrent_tickets', min_value=1, max_value=100),
            ForeignKeyValidationRule('organization', Organization),
            LengthValidationRule('first_name', min_length=1, max_length=50),
            LengthValidationRule('last_name', min_length=1, max_length=50),
            LengthValidationRule('phone', max_length=20),
            PhoneValidationRule('phone'),
        ])
        
        # Ticket model validation rules
        self.add_model_rules('Ticket', [
            RequiredFieldValidationRule('subject'),
            RequiredFieldValidationRule('description'),
            ChoiceValidationRule('status', ['new', 'open', 'pending', 'resolved', 'closed']),
            ChoiceValidationRule('priority', ['low', 'medium', 'high', 'urgent']),
            ForeignKeyValidationRule('customer', User),
            ForeignKeyValidationRule('organization', Organization),
            LengthValidationRule('subject', min_length=1, max_length=200),
            LengthValidationRule('description', min_length=1, max_length=5000),
            UniqueValidationRule('ticket_number', Ticket),
        ])
        
        # TicketComment model validation rules
        self.add_model_rules('TicketComment', [
            RequiredFieldValidationRule('content'),
            ForeignKeyValidationRule('ticket', Ticket),
            ForeignKeyValidationRule('author', User),
            LengthValidationRule('content', min_length=1, max_length=2000),
        ])
        
        # Organization model validation rules
        self.add_model_rules('Organization', [
            RequiredFieldValidationRule('name'),
            RequiredFieldValidationRule('slug'),
            ChoiceValidationRule('subscription_tier', ['basic', 'premium', 'enterprise']),
            LengthValidationRule('name', min_length=1, max_length=100),
            LengthValidationRule('slug', min_length=1, max_length=50),
            UniqueValidationRule('slug', Organization),
        ])
    
    def add_model_rules(self, model_name: str, rules: List[FieldValidationRule]):
        """Add validation rules for a specific model."""
        if model_name not in self.validation_rules:
            self.validation_rules[model_name] = []
        
        self.validation_rules[model_name].extend(rules)
    
    def add_field_rule(self, model_name: str, field_name: str, rule: FieldValidationRule):
        """Add a specific field validation rule."""
        if model_name not in self.field_rules:
            self.field_rules[model_name] = {}
        
        if field_name not in self.field_rules[model_name]:
            self.field_rules[model_name][field_name] = []
        
        self.field_rules[model_name][field_name].append(rule)
    
    def add_cross_field_rule(self, model_name: str, rule: CrossFieldValidationRule):
        """Add cross-field validation rule."""
        if model_name not in self.cross_field_rules:
            self.cross_field_rules[model_name] = []
        
        self.cross_field_rules[model_name].append(rule)
    
    def add_business_rule(self, model_name: str, rule: BusinessRuleValidationRule):
        """Add business rule validation."""
        if model_name not in self.business_rules:
            self.business_rules[model_name] = []
        
        self.business_rules[model_name].append(rule)
    
    def validate_model(self, model_instance: models.Model) -> List[str]:
        """
        Validate a model instance using all validation rules.
        
        Args:
            model_instance: The model instance to validate
            
        Returns:
            List of error messages (empty if validation passes)
        """
        model_name = model_instance.__class__.__name__
        errors = []
        
        # Validate standard field rules
        if model_name in self.validation_rules:
            for rule in self.validation_rules[model_name]:
                try:
                    field_value = getattr(model_instance, rule.field_name, None)
                    if not rule.validate(field_value, model_instance):
                        errors.append(rule.get_error_message(field_value, model_instance))
                except Exception as e:
                    logger.error(f"Validation error for {model_name}.{rule.field_name}: {e}")
                    errors.append(f"Validation error for {rule.field_name}: {str(e)}")
        
        # Validate field-specific rules
        if model_name in self.field_rules:
            for field_name, rules in self.field_rules[model_name].items():
                for rule in rules:
                    try:
                        field_value = getattr(model_instance, field_name, None)
                        if not rule.validate(field_value, model_instance):
                            errors.append(rule.get_error_message(field_value, model_instance))
                    except Exception as e:
                        logger.error(f"Field validation error for {model_name}.{field_name}: {e}")
                        errors.append(f"Field validation error for {field_name}: {str(e)}")
        
        # Validate cross-field rules
        if model_name in self.cross_field_rules:
            for rule in self.cross_field_rules[model_name]:
                try:
                    field_value = getattr(model_instance, rule.field_name, None)
                    if not rule.validate(field_value, model_instance):
                        errors.append(rule.get_error_message(field_value, model_instance))
                except Exception as e:
                    logger.error(f"Cross-field validation error for {model_name}.{rule.field_name}: {e}")
                    errors.append(f"Cross-field validation error for {rule.field_name}: {str(e)}")
        
        # Validate business rules
        if model_name in self.business_rules:
            for rule in self.business_rules[model_name]:
                try:
                    field_value = getattr(model_instance, rule.field_name, None)
                    if not rule.validate(field_value, model_instance):
                        errors.append(rule.get_error_message(field_value, model_instance))
                except Exception as e:
                    logger.error(f"Business rule validation error for {model_name}.{rule.field_name}: {e}")
                    errors.append(f"Business rule validation error for {rule.field_name}: {str(e)}")
        
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
        
        # Validate standard field rules
        if model_name in self.validation_rules:
            for rule in self.validation_rules[model_name]:
                if rule.field_name == field_name:
                    try:
                        field_value = getattr(model_instance, field_name, None)
                        if not rule.validate(field_value, model_instance):
                            errors.append(rule.get_error_message(field_value, model_instance))
                    except Exception as e:
                        logger.error(f"Validation error for {model_name}.{field_name}: {e}")
                        errors.append(f"Validation error for {field_name}: {str(e)}")
        
        # Validate field-specific rules
        if model_name in self.field_rules and field_name in self.field_rules[model_name]:
            for rule in self.field_rules[model_name][field_name]:
                try:
                    field_value = getattr(model_instance, field_name, None)
                    if not rule.validate(field_value, model_instance):
                        errors.append(rule.get_error_message(field_value, model_instance))
                except Exception as e:
                    logger.error(f"Field validation error for {model_name}.{field_name}: {e}")
                    errors.append(f"Field validation error for {field_name}: {str(e)}")
        
        return errors
    
    def get_model_rules(self, model_name: str) -> List[FieldValidationRule]:
        """Get validation rules for a specific model."""
        return self.validation_rules.get(model_name, [])
    
    def get_field_rules(self, model_name: str, field_name: str) -> List[FieldValidationRule]:
        """Get validation rules for a specific field of a model."""
        if model_name in self.field_rules and field_name in self.field_rules[model_name]:
            return self.field_rules[model_name][field_name]
        return []


class EnhancedValidationMixin:
    """
    Enhanced mixin to add comprehensive validation to Django models.
    """
    
    def clean(self):
        """Override clean method to use enhanced validation."""
        super().clean()
        
        validator = EnhancedCentralizedValidator()
        errors = validator.validate_model(self)
        
        if errors:
            raise ValidationError(errors)
    
    def validate_field(self, field_name: str):
        """Validate a specific field."""
        validator = EnhancedCentralizedValidator()
        errors = validator.validate_field(self, field_name)
        
        if errors:
            raise ValidationError(errors)
    
    def get_validation_errors(self):
        """Get all validation errors for this instance."""
        validator = EnhancedCentralizedValidator()
        return validator.validate_model(self)
    
    def is_valid(self):
        """Check if the model instance is valid."""
        return len(self.get_validation_errors()) == 0
    
    def get_field_validation_errors(self, field_name: str):
        """Get validation errors for a specific field."""
        validator = EnhancedCentralizedValidator()
        return validator.validate_field(self, field_name)


class ValidationManager:
    """
    Manager for validation operations with enhanced features.
    """
    
    def __init__(self):
        self.validator = EnhancedCentralizedValidator()
    
    def validate_model_instance(self, model_instance: models.Model) -> Dict[str, Any]:
        """
        Validate a model instance and return detailed results.
        
        Args:
            model_instance: The model instance to validate
            
        Returns:
            Dict with validation results
        """
        errors = self.validator.validate_model(model_instance)
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'error_count': len(errors),
            'model_name': model_instance.__class__.__name__,
            'timestamp': timezone.now().isoformat(),
        }
    
    def validate_field(self, model_instance: models.Model, field_name: str) -> Dict[str, Any]:
        """
        Validate a specific field and return detailed results.
        
        Args:
            model_instance: The model instance to validate
            field_name: The field name to validate
            
        Returns:
            Dict with field validation results
        """
        errors = self.validator.validate_field(model_instance, field_name)
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'error_count': len(errors),
            'field_name': field_name,
            'model_name': model_instance.__class__.__name__,
            'timestamp': timezone.now().isoformat(),
        }
    
    def get_validation_summary(self, model_class: models.Model) -> Dict[str, Any]:
        """
        Get validation summary for a model class.
        
        Args:
            model_class: The model class to analyze
            
        Returns:
            Dict with validation summary
        """
        model_name = model_class.__name__
        rules = self.validator.get_model_rules(model_name)
        
        return {
            'model_name': model_name,
            'total_rules': len(rules),
            'rule_types': [type(rule).__name__ for rule in rules],
            'fields_with_rules': list(set(rule.field_name for rule in rules)),
            'timestamp': timezone.now().isoformat(),
        }


# Global enhanced validator instance
enhanced_validator = EnhancedCentralizedValidator()

# Global validation manager instance
validation_manager = ValidationManager()
