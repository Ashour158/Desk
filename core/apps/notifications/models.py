"""
Notification models for helpdesk platform.
"""

import logging
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.organizations.models import Organization

User = get_user_model()
logger = logging.getLogger(__name__)


class Notification(models.Model):
    """In-app notification model."""

    NOTIFICATION_TYPES = [
        ("ticket_created", "Ticket Created"),
        ("ticket_updated", "Ticket Updated"),
        ("ticket_assigned", "Ticket Assigned"),
        ("ticket_resolved", "Ticket Resolved"),
        ("ticket_comment", "Ticket Comment"),
        ("work_order_created", "Work Order Created"),
        ("work_order_assigned", "Work Order Assigned"),
        ("work_order_completed", "Work Order Completed"),
        ("sla_breach", "SLA Breach"),
        ("system_alert", "System Alert"),
        ("announcement", "Announcement"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )

    # Related entity
    entity_type = models.CharField(max_length=50, blank=True, null=True)
    entity_id = models.UUIDField(blank=True, null=True)

    # Notification state
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    # Delivery channels
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["organization", "notification_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.full_name}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    def mark_as_sent(self, channel=None):
        """Mark notification as sent via specific channel."""
        if channel == "email":
            self.email_sent = True
        elif channel == "sms":
            self.sms_sent = True
        elif channel == "push":
            self.push_sent = True

        self.is_sent = self.email_sent or self.sms_sent or self.push_sent
        self.save(update_fields=["email_sent", "sms_sent", "push_sent", "is_sent"])


class NotificationTemplate(models.Model):
    """Notification template model."""

    TEMPLATE_TYPES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push Notification"),
        ("in_app", "In-App Notification"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    notification_type = models.CharField(
        max_length=50, choices=Notification.NOTIFICATION_TYPES
    )

    # Template content
    subject = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    message = models.TextField()

    # Template variables
    variables = models.JSONField(default=list, blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["organization", "name", "template_type"]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.template_type})"

    def render(self, context):
        """Render template with context."""
        try:
            from django.template import Template, Context

            template = Template(self.message)
            return template.render(Context(context))
        except Exception as e:
            logger.error(f"Error rendering template {self.id}: {str(e)}")
            return self.message


class NotificationPreference(models.Model):
    """User notification preferences."""

    DELIVERY_CHOICES = [
        ("immediate", "Immediate"),
        ("daily", "Daily Digest"),
        ("weekly", "Weekly Digest"),
        ("never", "Never"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )

    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_tickets = models.BooleanField(default=True)
    email_work_orders = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)
    email_digest = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES, default="daily"
    )

    # SMS preferences
    sms_enabled = models.BooleanField(default=False)
    sms_phone_number = models.CharField(max_length=20, blank=True)
    sms_tickets = models.BooleanField(default=False)
    sms_work_orders = models.BooleanField(default=False)
    sms_system = models.BooleanField(default=False)

    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_tickets = models.BooleanField(default=True)
    push_work_orders = models.BooleanField(default=True)
    push_system = models.BooleanField(default=True)

    # In-app preferences
    in_app_enabled = models.BooleanField(default=True)
    in_app_tickets = models.BooleanField(default=True)
    in_app_work_orders = models.BooleanField(default=True)
    in_app_system = models.BooleanField(default=True)

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(blank=True, null=True)
    quiet_hours_end = models.TimeField(blank=True, null=True)
    quiet_hours_timezone = models.CharField(max_length=50, default="UTC")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification Preferences - {self.user.full_name}"

    def should_send_notification(self, notification_type, channel):
        """Check if notification should be sent based on preferences."""
        if not getattr(self, f"{channel}_enabled", False):
            return False

        # Check specific notification type preferences
        if notification_type.startswith("ticket_"):
            return getattr(self, f"{channel}_tickets", False)
        elif notification_type.startswith("work_order_"):
            return getattr(self, f"{channel}_work_orders", False)
        elif notification_type in ["system_alert", "announcement"]:
            return getattr(self, f"{channel}_system", False)

        return True

    def is_quiet_hours(self):
        """Check if current time is within quiet hours."""
        if not self.quiet_hours_enabled:
            return False

        from django.utils import timezone

        now = timezone.now()

        # Convert to user's timezone
        if self.quiet_hours_timezone:
            try:
                import pytz

                user_tz = pytz.timezone(self.quiet_hours_timezone)
                now = now.astimezone(user_tz)
            except:
                pass

        current_time = now.time()

        if self.quiet_hours_start and self.quiet_hours_end:
            if self.quiet_hours_start <= self.quiet_hours_end:
                return self.quiet_hours_start <= current_time <= self.quiet_hours_end
            else:
                # Quiet hours span midnight
                return (
                    current_time >= self.quiet_hours_start
                    or current_time <= self.quiet_hours_end
                )

        return False


class NotificationLog(models.Model):
    """Log of notification delivery attempts."""

    DELIVERY_STATUS = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
        ("bounced", "Bounced"),
        ("complained", "Complained"),
    ]

    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="delivery_logs"
    )
    channel = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default="pending")

    # Delivery details
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)

    # Response data
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Timestamps
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["notification", "channel"]),
            models.Index(fields=["status", "sent_at"]),
        ]

    def __str__(self):
        return f"{self.notification.title} - {self.channel} - {self.status}"
