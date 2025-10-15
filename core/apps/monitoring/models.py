"""
Monitoring models for system metrics and alerts.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class SystemMetric(models.Model):
    """Model for storing system metrics."""
    
    METRIC_TYPES = [
        ('cpu', 'CPU Usage'),
        ('memory', 'Memory Usage'),
        ('disk', 'Disk Usage'),
        ('network', 'Network Usage'),
        ('database', 'Database Performance'),
        ('response_time', 'Response Time'),
        ('error_rate', 'Error Rate'),
        ('throughput', 'Throughput'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    name = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='percent')
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['name', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value}{self.unit} at {self.timestamp}"


class Alert(models.Model):
    """Model for storing system alerts."""
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('suppressed', 'Suppressed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    metric_type = models.CharField(max_length=20, choices=SystemMetric.METRIC_TYPES)
    threshold_value = models.FloatField()
    actual_value = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['metric_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.severity}) - {self.status}"
    
    def acknowledge(self, user):
        """Acknowledge the alert."""
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.save()
    
    def resolve(self):
        """Resolve the alert."""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()


class PerformanceReport(models.Model):
    """Model for storing performance reports."""
    
    REPORT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]
    
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    metrics_data = models.JSONField(default=dict)
    generated_at = models.DateTimeField(default=timezone.now)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_type', 'generated_at']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.report_type}) - {self.generated_at}"


class HealthCheck(models.Model):
    """Model for storing health check results."""
    
    SERVICE_TYPES = [
        ('database', 'Database'),
        ('redis', 'Redis'),
        ('email', 'Email'),
        ('storage', 'Storage'),
        ('api', 'API'),
        ('frontend', 'Frontend'),
    ]
    
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
    ]
    
    service_name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    response_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    checked_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['service_type', 'status']),
            models.Index(fields=['checked_at']),
        ]
    
    def __str__(self):
        return f"{self.service_name} - {self.status}"


class MonitoringConfiguration(models.Model):
    """Model for storing monitoring configuration."""
    
    metric_type = models.CharField(max_length=20, choices=SystemMetric.METRIC_TYPES, unique=True)
    enabled = models.BooleanField(default=True)
    threshold_warning = models.FloatField()
    threshold_critical = models.FloatField()
    check_interval = models.IntegerField(default=60)  # seconds
    alert_enabled = models.BooleanField(default=True)
    notification_channels = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['metric_type']
    
    def __str__(self):
        return f"{self.metric_type} monitoring configuration"