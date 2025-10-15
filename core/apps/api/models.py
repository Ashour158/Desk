"""
API models for the helpdesk platform.
"""

from django.db import models
from apps.organizations.models import Organization


class APIService(models.Model):
    """API service configuration."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=100)
    endpoint = models.URLField()
    api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Webhook(models.Model):
    """Webhook configuration."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField()
    events = models.JSONField(default=list)
    secret_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class IntegrationLog(models.Model):
    """Integration activity log."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    service = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    request_data = models.JSONField(blank=True, null=True)
    response_data = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service} - {self.action} ({self.status})"
