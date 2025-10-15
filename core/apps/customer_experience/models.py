"""
Customer Experience models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class CustomerJourney(models.Model):
    """Customer journey mapping."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    customer = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    touchpoint = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    sentiment = models.CharField(max_length=20, null=True, blank=True)


class CustomerPersona(models.Model):
    """Customer persona management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProactiveSupport(models.Model):
    """Proactive support triggers."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    trigger_type = models.CharField(max_length=100)
    conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)


class CustomerHealthScore(models.Model):
    """Customer health scoring."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    customer = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    score = models.FloatField()
    factors = models.JSONField(default=dict)
    calculated_at = models.DateTimeField(auto_now_add=True)


class PersonalizationRule(models.Model):
    """Personalization rules."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
