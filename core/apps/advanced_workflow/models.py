"""
Advanced Workflow models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class WorkflowTemplate(models.Model):
    """Workflow template management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    workflow_definition = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProcessAutomation(models.Model):
    """Process automation rules."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    trigger_conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkflowExecution(models.Model):
    """Workflow execution tracking."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    workflow = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class WorkflowRule(models.Model):
    """Workflow rule management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
