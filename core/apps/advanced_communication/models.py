"""
Advanced Communication models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class CommunicationChannel(models.Model):
    """Communication channel management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    channel_type = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class VideoConference(models.Model):
    """Video conference management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    participants = models.JSONField(default=list)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class CommunicationTemplate(models.Model):
    """Communication template management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=100)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CommunicationLog(models.Model):
    """Communication activity logging."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    channel = models.ForeignKey(CommunicationChannel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
