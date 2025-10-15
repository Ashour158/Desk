"""
Advanced Analytics models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class CustomReport(models.Model):
    """Custom report builder."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    query = models.TextField()
    parameters = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Dashboard(models.Model):
    """Analytics dashboard."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class KPIBuilder(models.Model):
    """KPI builder."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    kpi_definition = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DataExport(models.Model):
    """Data export management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    export_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class ReportSchedule(models.Model):
    """Report scheduling."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    report = models.ForeignKey(CustomReport, on_delete=models.CASCADE)
    schedule = models.CharField(max_length=100)
    recipients = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
