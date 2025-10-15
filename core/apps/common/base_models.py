"""
Base model classes to eliminate duplicate code across the application.
"""

from django.db import models
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from .constants import (
    SHORT_FIELD_LENGTH,
    MEDIUM_FIELD_LENGTH,
    LONG_FIELD_LENGTH,
    VERY_LONG_FIELD_LENGTH,
    COMMON_STATUS_CHOICES,
    STATUS_ACTIVE,
)

User = get_user_model()


class TenantAwareModel(models.Model):
    """Base model with organization-based multi-tenancy."""
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        help_text="Organization this record belongs to"
    )
    
    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """Base model with created_at and updated_at timestamps."""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class NamedModel(models.Model):
    """Base model with a name field."""
    
    name = models.CharField(
        max_length=LONG_FIELD_LENGTH,
        help_text="Name of the item"
    )
    
    class Meta:
        abstract = True


class StatusModel(models.Model):
    """Base model with status field."""
    
    status = models.CharField(
        max_length=SHORT_FIELD_LENGTH,
        choices=COMMON_STATUS_CHOICES,
        default=STATUS_ACTIVE,
        help_text="Current status"
    )
    
    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """Base model with is_active boolean field."""
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this item is active"
    )
    
    class Meta:
        abstract = True


class BaseModel(TenantAwareModel, TimestampedModel, NamedModel, StatusModel, ActiveModel):
    """Complete base model with all common fields."""
    
    class Meta:
        abstract = True


class ConfigurationModel(models.Model):
    """Base model for items with JSON configuration."""
    
    configuration = models.JSONField(
        default=dict,
        help_text="Configuration settings"
    )
    
    class Meta:
        abstract = True


class MetricsModel(models.Model):
    """Base model for items with usage metrics."""
    
    total_usage = models.PositiveIntegerField(
        default=0,
        help_text="Total usage count"
    )
    active_count = models.PositiveIntegerField(
        default=0,
        help_text="Currently active count"
    )
    
    class Meta:
        abstract = True


class DataPointModel(models.Model):
    """Base model for data points with value, unit, and metadata."""
    
    data_type = models.CharField(
        max_length=MEDIUM_FIELD_LENGTH,
        help_text="Type of data"
    )
    value = models.FloatField(help_text="Data value")
    unit = models.CharField(
        max_length=SHORT_FIELD_LENGTH,
        help_text="Unit of measurement"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata"
    )
    
    class Meta:
        abstract = True


class LocationModel(models.Model):
    """Base model for items with location data."""
    
    latitude = models.FloatField(help_text="Latitude coordinate")
    longitude = models.FloatField(help_text="Longitude coordinate")
    altitude = models.FloatField(
        null=True,
        blank=True,
        help_text="Altitude coordinate"
    )
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="Location accuracy in meters"
    )
    
    class Meta:
        abstract = True


class WorkflowNodeModel(models.Model):
    """Base model for workflow nodes."""
    
    node_id = models.CharField(
        max_length=MEDIUM_FIELD_LENGTH,
        help_text="Unique node identifier"
    )
    node_type = models.CharField(
        max_length=SHORT_FIELD_LENGTH,
        help_text="Type of workflow node"
    )
    width = models.FloatField(
        default=100.0,
        help_text="Node width in pixels"
    )
    height = models.FloatField(
        default=50.0,
        help_text="Node height in pixels"
    )
    position_x = models.FloatField(
        default=0.0,
        help_text="X position in pixels"
    )
    position_y = models.FloatField(
        default=0.0,
        help_text="Y position in pixels"
    )
    
    class Meta:
        abstract = True


class ProcessModel(models.Model):
    """Base model for process-related items."""
    
    process_name = models.CharField(
        max_length=VERY_LONG_FIELD_LENGTH,
        help_text="Name of the process"
    )
    process_type = models.CharField(
        max_length=MEDIUM_FIELD_LENGTH,
        help_text="Type of process"
    )
    data_source = models.CharField(
        max_length=VERY_LONG_FIELD_LENGTH,
        help_text="Data source for the process"
    )
    time_window = models.IntegerField(
        default=30,
        help_text="Time window in days"
    )
    
    class Meta:
        abstract = True


class AIModel(models.Model):
    """Base model for AI-related items."""
    
    ai_type = models.CharField(
        max_length=SHORT_FIELD_LENGTH,
        help_text="Type of AI model"
    )
    model_name = models.CharField(
        max_length=VERY_LONG_FIELD_LENGTH,
        help_text="Name of the AI model"
    )
    model_version = models.CharField(
        max_length=SHORT_FIELD_LENGTH,
        help_text="Version of the AI model"
    )
    confidence_threshold = models.FloatField(
        default=0.8,
        help_text="Confidence threshold for predictions"
    )
    
    class Meta:
        abstract = True
