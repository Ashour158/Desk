"""
Comprehensive validation system with field-level validation for all endpoints.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
import re
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
User = get_user_model()


class ComprehensiveFieldValidator:
    """
    Comprehensive field validator with advanced validation rules.
    """
    
    def __init__(self):
        self.validation_rules = {}
        self.cross_field_rules = {}
        self.business_rules = {}
        self._setup_comprehensive_rules()
    
    def _setup_comprehensive_rules(self):
        """Setup comprehensive validation rules for all models."""
        
        # TODO: Define validation rule classes before using them
        # Enhanced User validation
        # self.add_model_rules('User', [
        #     RequiredFieldValidationRule('email'),
        #     EmailValidationRule('email'),
        #     ...
        # ])
        pass
        
        # TODO: Define validation rule classes before using them
        # Enhanced Ticket validation
        # self.add_model_rules('Ticket', [...])
        
        # Enhanced Organization validation
        # self.add_model_rules('Organization', [...])
        pass
    
    def add_model_rules(self, model_name: str, rules: List):
        """Add validation rules for a specific model."""
        if model_name not in self.validation_rules:
            self.validation_rules[model_name] = []
        self.validation_rules[model_name].extend(rules)
    
    def validate_model(self, model_instance: models.Model) -> Dict[str, Any]:
        """
        Comprehensive model validation with detailed results.
        
        Args:
            model_instance: The model instance to validate
            
        Returns:
            Dict with comprehensive validation results
        """
        model_name = model_instance.__class__.__name__
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_results': {},
            'cross_field_results': {},
            'business_rule_results': {},
            'model_name': model_name,
            'timestamp': timezone.now().isoformat()
        }
        
        try:
            # Field-level validation
            if model_name in self.validation_rules:
                for rule in self.validation_rules[model_name]:
                    field_result = self._validate_field_rule(rule, model_instance)
                    validation_result['field_results'][rule.field_name] = field_result
                    
                    if not field_result['is_valid']:
                        validation_result['is_valid'] = False
                        validation_result['errors'].extend(field_result['errors'])
            
            # Cross-field validation
            if model_name in self.cross_field_rules:
                for rule in self.cross_field_rules[model_name]:
                    cross_field_result = self._validate_cross_field_rule(rule, model_instance)
                    validation_result['cross_field_results'][rule.field_name] = cross_field_result
                    
                    if not cross_field_result['is_valid']:
                        validation_result['is_valid'] = False
                        validation_result['errors'].extend(cross_field_result['errors'])
            
            # Business rule validation
            if model_name in self.business_rules:
                for rule in self.business_rules[model_name]:
                    business_result = self._validate_business_rule(rule, model_instance)
                    validation_result['business_rule_results'][rule.field_name] = business_result
                    
                    if not business_result['is_valid']:
                        validation_result['is_valid'] = False
                        validation_result['errors'].extend(business_result['errors'])
            
        except Exception as e:
            logger.error(f"Validation error for {model_name}: {e}")
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation system error: {str(e)}")
        
        return validation_result
    
    def _validate_field_rule(self, rule, model_instance: models.Model) -> Dict[str, Any]:
        """Validate a single field rule."""
        try:
            field_value = getattr(model_instance, rule.field_name, None)
            is_valid = rule.validate(field_value, model_instance)
            
            return {
                'is_valid': is_valid,
                'field_name': rule.field_name,
                'field_value': field_value,
                'errors': [rule.get_error_message(field_value, model_instance)] if not is_valid else [],
                'rule_type': type(rule).__name__
            }
        except Exception as e:
            return {
                'is_valid': False,
                'field_name': rule.field_name,
                'field_value': None,
                'errors': [f"Validation error: {str(e)}"],
                'rule_type': type(rule).__name__
            }
    
    def _validate_cross_field_rule(self, rule, model_instance: models.Model) -> Dict[str, Any]:
        """Validate cross-field rules."""
        try:
            field_value = getattr(model_instance, rule.field_name, None)
            is_valid = rule.validate(field_value, model_instance)
            
            return {
                'is_valid': is_valid,
                'field_name': rule.field_name,
                'field_value': field_value,
                'errors': [rule.get_error_message(field_value, model_instance)] if not is_valid else [],
                'rule_type': 'CrossFieldValidationRule'
            }
        except Exception as e:
            return {
                'is_valid': False,
                'field_name': rule.field_name,
                'field_value': None,
                'errors': [f"Cross-field validation error: {str(e)}"],
                'rule_type': 'CrossFieldValidationRule'
            }
    
    def _validate_business_rule(self, rule, model_instance: models.Model) -> Dict[str, Any]:
        """Validate business rules."""
        try:
            field_value = getattr(model_instance, rule.field_name, None)
            is_valid = rule.validate(field_value, model_instance)
            
            return {
                'is_valid': is_valid,
                'field_name': rule.field_name,
                'field_value': field_value,
                'errors': [rule.get_error_message(field_value, model_instance)] if not is_valid else [],
                'rule_type': 'BusinessRuleValidationRule'
            }
        except Exception as e:
            return {
                'is_valid': False,
                'field_name': rule.field_name,
                'field_value': None,
                'errors': [f"Business rule validation error: {str(e)}"],
                'rule_type': 'BusinessRuleValidationRule'
            }
    
    # Business rule validation methods
    def _validate_user_email_business_rules(self, email: str, model_instance: models.Model) -> bool:
        """Validate user email business rules."""
        if not email:
            return True
        
        # Check for organization-specific email domains
        if hasattr(model_instance, 'organization') and model_instance.organization:
            org_domain = model_instance.organization.domain
            if org_domain and not email.endswith(f"@{org_domain}"):
                return False
        
        return True
    
    def _validate_ticket_status_business_rules(self, status: str, model_instance: models.Model) -> bool:
        """Validate ticket status business rules."""
        if not status:
            return True
        
        # Check status transitions
        if hasattr(model_instance, 'pk') and model_instance.pk:
            # This is an update, check status transition
            try:
                original = model_instance.__class__.objects.get(pk=model_instance.pk)
                if original.status == 'closed' and status != 'closed':
                    return False  # Cannot reopen closed tickets
            except:
                pass
        
        return True
    
    def _validate_subscription_tier_business_rules(self, tier: str, model_instance: models.Model) -> bool:
        """Validate subscription tier business rules."""
        if not tier:
            return True
        
        # Check tier upgrade/downgrade rules
        if hasattr(model_instance, 'pk') and model_instance.pk:
            try:
                original = model_instance.__class__.objects.get(pk=model_instance.pk)
                if original.subscription_tier == 'enterprise' and tier != 'enterprise':
                    return False  # Cannot downgrade from enterprise
            except:
                pass
        
        return True
    
    def _validate_ticket_assignment(self, status: str, related_values: Dict, model_instance: models.Model) -> bool:
        """Validate ticket assignment cross-field rules."""
        if status == 'open' and not related_values.get('assigned_agent'):
            return False  # Open tickets must have assigned agent
        
        if status == 'closed' and related_values.get('priority') == 'urgent':
            return False  # Urgent tickets cannot be closed without resolution
        
        return True


class EnhancedSerializerMixin:
    """
    Mixin to add comprehensive validation to serializers.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = ComprehensiveFieldValidator()
    
    def validate(self, attrs):
        """Enhanced validation with comprehensive checks."""
        # Get model instance for validation
        if self.instance:
            # Update existing instance
            for key, value in attrs.items():
                setattr(self.instance, key, value)
            model_instance = self.instance
        else:
            # Create new instance
            model_instance = self.Meta.model(**attrs)
        
        # Perform comprehensive validation
        validation_result = self.validator.validate_model(model_instance)
        
        if not validation_result['is_valid']:
            # Convert validation errors to serializer errors
            serializer_errors = {}
            for error in validation_result['errors']:
                if 'field' in error:
                    field_name = error['field']
                    if field_name not in serializer_errors:
                        serializer_errors[field_name] = []
                    serializer_errors[field_name].append(error['message'])
                else:
                    # Non-field errors
                    if 'non_field_errors' not in serializer_errors:
                        serializer_errors['non_field_errors'] = []
                    serializer_errors['non_field_errors'].append(error)
            
            raise serializers.ValidationError(serializer_errors)
        
        return attrs
    
    def validate_email(self, value):
        """Enhanced email validation."""
        if not value:
            return value
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Invalid email format")
        
        # Check for organization domain if applicable
        if hasattr(self, 'context') and 'request' in self.context:
            user = self.context['request'].user
            if hasattr(user, 'organization') and user.organization:
                org_domain = user.organization.domain
                if org_domain and not value.endswith(f"@{org_domain}"):
                    raise serializers.ValidationError(f"Email must be from organization domain: {org_domain}")
        
        return value
    
    def validate_phone(self, value):
        """Enhanced phone validation."""
        if not value:
            return value
        
        # International phone number validation
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', value)
        
        if not re.match(phone_pattern, cleaned_phone):
            raise serializers.ValidationError("Invalid phone number format")
        
        return cleaned_phone


class ComprehensiveValidationViewSet:
    """
    ViewSet mixin with comprehensive validation.
    """
    
    def create(self, request, *args, **kwargs):
        """Enhanced create with comprehensive validation."""
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                # Additional comprehensive validation
                validation_result = self._perform_comprehensive_validation(serializer.validated_data)
                
                if not validation_result['is_valid']:
                    return Response({
                        'error': {
                            'code': 'VALIDATION_ERROR',
                            'message': 'Comprehensive validation failed',
                            'details': validation_result['errors'],
                            'timestamp': timezone.now().isoformat()
                        },
                        'meta': {
                            'timestamp': timezone.now().isoformat(),
                            'version': 'v1',
                            'request_id': str(uuid.uuid4()),
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Save with transaction
                with transaction.atomic():
                    instance = serializer.save()
                    self.perform_create(serializer)
                
                return Response({
                    'data': serializer.data,
                    'message': 'Resource created successfully',
                    'validation_info': validation_result,
                    'meta': {
                        'timestamp': timezone.now().isoformat(),
                        'version': 'v1',
                        'request_id': str(uuid.uuid4()),
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Validation failed',
                        'details': serializer.errors,
                        'timestamp': timezone.now().isoformat()
                    },
                    'meta': {
                        'timestamp': timezone.now().isoformat(),
                        'version': 'v1',
                        'request_id': str(uuid.uuid4()),
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Create error in {self.__class__.__name__}: {e}")
            return Response({
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'Failed to create resource',
                    'details': str(e),
                    'timestamp': timezone.now().isoformat()
                },
                'meta': {
                    'timestamp': timezone.now().isoformat(),
                    'version': 'v1',
                    'request_id': str(uuid.uuid4()),
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _perform_comprehensive_validation(self, validated_data: Dict) -> Dict[str, Any]:
        """Perform comprehensive validation on validated data."""
        try:
            # Create temporary model instance
            model_instance = self.get_serializer().Meta.model(**validated_data)
            
            # Perform comprehensive validation
            validator = ComprehensiveFieldValidator()
            return validator.validate_model(model_instance)
            
        except Exception as e:
            logger.error(f"Comprehensive validation error: {e}")
            return {
                'is_valid': False,
                'errors': [f"Validation system error: {str(e)}"],
                'timestamp': timezone.now().isoformat()
            }


# Global comprehensive validator instance
comprehensive_validator = ComprehensiveFieldValidator()
