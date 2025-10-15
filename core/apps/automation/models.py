"""
Automation and workflow models.
"""

import uuid
from django.db import models
from django.utils import timezone
from apps.organizations.managers import TenantAwareModel, TenantManager


class AutomationRule(TenantAwareModel):
    """
    Automation rules for tickets and work orders.
    """

    TRIGGER_TYPES = [
        ("ticket_created", "Ticket Created"),
        ("ticket_updated", "Ticket Updated"),
        ("ticket_assigned", "Ticket Assigned"),
        ("ticket_status_changed", "Ticket Status Changed"),
        ("work_order_created", "Work Order Created"),
        ("work_order_assigned", "Work Order Assigned"),
        ("time_based", "Time Based"),
        ("sla_breach", "SLA Breach"),
    ]

    ACTION_TYPES = [
        ("assign", "Assign"),
        ("change_status", "Change Status"),
        ("change_priority", "Change Priority"),
        ("send_email", "Send Email"),
        ("send_sms", "Send SMS"),
        ("create_task", "Create Task"),
        ("escalate", "Escalate"),
        ("webhook", "Webhook"),
        ("add_tag", "Add Tag"),
        ("remove_tag", "Remove Tag"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Rule name")
    description = models.TextField(blank=True, help_text="Rule description")

    # Trigger configuration
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    trigger_conditions = models.JSONField(default=dict, help_text="Trigger conditions")

    # Action configuration
    actions = models.JSONField(default=list, help_text="Actions to execute")

    # Execution settings
    execution_order = models.PositiveIntegerField(
        default=0, help_text="Execution order"
    )
    is_active = models.BooleanField(default=True, help_text="Rule is active")
    stop_on_match = models.BooleanField(
        default=False, help_text="Stop processing after match"
    )

    # Statistics
    execution_count = models.PositiveIntegerField(
        default=0, help_text="Number of executions"
    )
    last_executed = models.DateTimeField(
        null=True, blank=True, help_text="Last execution time"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "automation_rules"
        verbose_name = "Automation Rule"
        verbose_name_plural = "Automation Rules"
        ordering = ["execution_order", "name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class AutomationExecution(models.Model):
    """
    Track automation rule executions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(
        AutomationRule, on_delete=models.CASCADE, related_name="executions"
    )

    # Execution details
    entity_type = models.CharField(
        max_length=50, help_text="Entity type (ticket, work_order)"
    )
    entity_id = models.UUIDField(help_text="Entity ID")
    trigger_data = models.JSONField(default=dict, help_text="Trigger data")
    actions_executed = models.JSONField(default=list, help_text="Actions executed")

    # Results
    success = models.BooleanField(default=True, help_text="Execution successful")
    error_message = models.TextField(blank=True, help_text="Error message if failed")
    execution_time = models.DecimalField(
        max_digits=8, decimal_places=3, default=0, help_text="Execution time in seconds"
    )

    # Timestamps
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "automation_executions"
        verbose_name = "Automation Execution"
        verbose_name_plural = "Automation Executions"
        ordering = ["-executed_at"]

    def __str__(self):
        return f"Execution of {self.rule.name} on {self.entity_type} {self.entity_id}"


class EmailTemplate(TenantAwareModel):
    """
    Email templates for automated communications.
    """

    TEMPLATE_TYPES = [
        ("ticket_created", "Ticket Created"),
        ("ticket_assigned", "Ticket Assigned"),
        ("ticket_resolved", "Ticket Resolved"),
        ("ticket_closed", "Ticket Closed"),
        ("work_order_created", "Work Order Created"),
        ("work_order_scheduled", "Work Order Scheduled"),
        ("work_order_completed", "Work Order Completed"),
        ("sla_breach", "SLA Breach"),
        ("welcome", "Welcome"),
        ("password_reset", "Password Reset"),
        ("custom", "Custom"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Template name")
    template_type = models.CharField(
        max_length=30, choices=TEMPLATE_TYPES, default="custom"
    )

    # Email content
    subject = models.CharField(max_length=500, help_text="Email subject")
    body_html = models.TextField(help_text="HTML email body")
    body_text = models.TextField(blank=True, help_text="Plain text email body")

    # Template variables
    variables = models.JSONField(default=list, help_text="Available template variables")

    # Settings
    is_active = models.BooleanField(default=True, help_text="Template is active")
    is_system = models.BooleanField(
        default=False, help_text="System template (cannot be deleted)"
    )

    # Usage tracking
    usage_count = models.PositiveIntegerField(
        default=0, help_text="Number of times used"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "email_templates"
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
        ordering = ["name"]
        unique_together = ["organization", "template_type"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class Webhook(TenantAwareModel):
    """
    Webhooks for external integrations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Webhook name")
    url = models.URLField(help_text="Webhook URL")
    secret_key = models.CharField(
        max_length=255, blank=True, help_text="Webhook secret key"
    )

    # Events
    events = models.JSONField(default=list, help_text="Events to trigger webhook")

    # Settings
    is_active = models.BooleanField(default=True, help_text="Webhook is active")
    retry_count = models.PositiveIntegerField(default=3, help_text="Number of retries")
    timeout_seconds = models.PositiveIntegerField(
        default=30, help_text="Request timeout"
    )

    # Statistics
    success_count = models.PositiveIntegerField(
        default=0, help_text="Successful deliveries"
    )
    failure_count = models.PositiveIntegerField(
        default=0, help_text="Failed deliveries"
    )
    last_triggered = models.DateTimeField(
        null=True, blank=True, help_text="Last trigger time"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "webhooks"
        verbose_name = "Webhook"
        verbose_name_plural = "Webhooks"
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class WebhookDelivery(models.Model):
    """
    Track webhook delivery attempts.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("retrying", "Retrying"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(
        Webhook, on_delete=models.CASCADE, related_name="deliveries"
    )

    # Delivery details
    event_type = models.CharField(max_length=50, help_text="Event type")
    payload = models.JSONField(default=dict, help_text="Webhook payload")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Response details
    response_status = models.PositiveIntegerField(
        null=True, blank=True, help_text="HTTP response status"
    )
    response_body = models.TextField(blank=True, help_text="Response body")
    error_message = models.TextField(blank=True, help_text="Error message")

    # Retry information
    attempt_count = models.PositiveIntegerField(
        default=1, help_text="Number of attempts"
    )
    next_retry_at = models.DateTimeField(
        null=True, blank=True, help_text="Next retry time"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(
        null=True, blank=True, help_text="Delivery time"
    )

    class Meta:
        db_table = "webhook_deliveries"
        verbose_name = "Webhook Delivery"
        verbose_name_plural = "Webhook Deliveries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Delivery of {self.webhook.name} - {self.event_type}"


class ScheduledTask(TenantAwareModel):
    """
    Scheduled tasks for automation.
    """

    TASK_TYPES = [
        ("sla_check", "SLA Check"),
        ("cleanup", "Cleanup"),
        ("report", "Report Generation"),
        ("backup", "Backup"),
        ("custom", "Custom"),
    ]

    FREQUENCY_CHOICES = [
        ("minutely", "Every Minute"),
        ("hourly", "Hourly"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Task name")
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, default="custom")

    # Schedule configuration
    frequency = models.CharField(
        max_length=20, choices=FREQUENCY_CHOICES, default="daily"
    )
    cron_expression = models.CharField(
        max_length=100, blank=True, help_text="Custom cron expression"
    )
    timezone = models.CharField(max_length=50, default="UTC", help_text="Task timezone")

    # Task configuration
    task_function = models.CharField(
        max_length=255, help_text="Task function to execute"
    )
    task_parameters = models.JSONField(default=dict, help_text="Task parameters")

    # Settings
    is_active = models.BooleanField(default=True, help_text="Task is active")
    max_execution_time = models.PositiveIntegerField(
        default=300, help_text="Max execution time in seconds"
    )

    # Statistics
    execution_count = models.PositiveIntegerField(
        default=0, help_text="Number of executions"
    )
    success_count = models.PositiveIntegerField(
        default=0, help_text="Successful executions"
    )
    failure_count = models.PositiveIntegerField(
        default=0, help_text="Failed executions"
    )
    last_executed = models.DateTimeField(
        null=True, blank=True, help_text="Last execution time"
    )
    next_execution = models.DateTimeField(
        null=True, blank=True, help_text="Next execution time"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "scheduled_tasks"
        verbose_name = "Scheduled Task"
        verbose_name_plural = "Scheduled Tasks"
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class TaskExecution(models.Model):
    """
    Track scheduled task executions.
    """

    STATUS_CHOICES = [
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("timeout", "Timeout"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        ScheduledTask, on_delete=models.CASCADE, related_name="executions"
    )

    # Execution details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="running")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.DecimalField(
        max_digits=8, decimal_places=3, default=0, help_text="Execution time in seconds"
    )

    # Results
    success = models.BooleanField(default=False, help_text="Execution successful")
    result_data = models.JSONField(default=dict, help_text="Execution result data")
    error_message = models.TextField(blank=True, help_text="Error message if failed")

    class Meta:
        db_table = "task_executions"
        verbose_name = "Task Execution"
        verbose_name_plural = "Task Executions"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Execution of {self.task.name} at {self.started_at}"
