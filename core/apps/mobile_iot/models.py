"""
Mobile & IoT Platform models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class MobileApp(models.Model):
    """Mobile application management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=50)
    version = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class IoTDevice(models.Model):
    """IoT device management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=200)
    device_type = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class LocationTracking(models.Model):
    """Location tracking data."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class OfflineSync(models.Model):
    """Offline synchronization."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=200)
    sync_status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
