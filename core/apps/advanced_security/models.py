"""
Advanced Security models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class SecurityPolicy(models.Model):
    """Security policy management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=100)
    rules = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    """Security audit logging."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    resource = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)


class ThreatDetection(models.Model):
    """Threat detection alerts."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    threat_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=50)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ComplianceReport(models.Model):
    """Compliance reporting."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100)
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class SecurityIncident(models.Model):
    """Security incident management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    incident_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
