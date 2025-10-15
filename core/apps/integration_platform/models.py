"""
Integration Platform models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class Webhook(models.Model):
    """Webhook configuration."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    url = models.URLField()
    events = models.JSONField(default=list)
    secret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class APIIntegration(models.Model):
    """API integration management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    api_type = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ThirdPartyService(models.Model):
    """Third-party service integration."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class IntegrationLog(models.Model):
    """Integration activity logging."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    integration = models.ForeignKey(APIIntegration, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Connector(models.Model):
    """Integration connector."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    connector_type = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
