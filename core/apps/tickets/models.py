"""
Ticket system models with multi-tenant support.
"""

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from apps.organizations.models import Organization
from apps.accounts.models import User


class Ticket(models.Model):
    """Main ticket model with comprehensive fields."""

    # Basic fields
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="tickets"
    )
    ticket_number = models.CharField(max_length=20, unique=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()

    # Status and priority
    status = models.CharField(
        max_length=20,
        choices=[
            ("new", "New"),
            ("open", "Open"),
            ("pending", "Pending"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        default="new",
    )

    priority = models.CharField(
        max_length=10,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("urgent", "Urgent"),
        ],
        default="medium",
    )

    # Channel and source
    channel = models.CharField(
        max_length=20,
        choices=[
            ("email", "Email"),
            ("web", "Web Form"),
            ("phone", "Phone"),
            ("chat", "Live Chat"),
            ("social", "Social Media"),
            ("api", "API"),
        ],
        default="web",
    )

    source = models.CharField(max_length=50, blank=True)  # e.g., 'support@company.com'

    # User relationships
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="customer_tickets",
        limit_choices_to={"role": "customer"},
    )
    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        limit_choices_to={"role__in": ["admin", "manager", "agent"]},
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_tickets"
    )

    # SLA fields
    sla_policy = models.ForeignKey(
        "automation.SLAPolicy", on_delete=models.SET_NULL, null=True, blank=True
    )
    first_response_due = models.DateTimeField(null=True, blank=True)
    resolution_due = models.DateTimeField(null=True, blank=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    sla_breach = models.BooleanField(default=False)

    # Categorization
    category = models.CharField(max_length=50, blank=True)
    subcategory = models.CharField(max_length=50, blank=True)
    tags = models.JSONField(default=list, blank=True)

    # Custom fields
    custom_fields = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Analytics
    time_to_first_response = models.DurationField(null=True, blank=True)
    time_to_resolution = models.DurationField(null=True, blank=True)
    customer_satisfaction_score = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "tickets_ticket"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "assigned_agent"]),
            models.Index(fields=["organization", "customer"]),
            models.Index(fields=["ticket_number"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["priority", "status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)

    def generate_ticket_number(self):
        """Generate unique ticket number."""
        import uuid

        return f"TK-{uuid.uuid4().hex[:8].upper()}"

    def is_overdue(self):
        """Check if ticket is overdue."""
        if self.status in ["resolved", "closed", "cancelled"]:
            return False
        if self.resolution_due and timezone.now() > self.resolution_due:
            return True
        return False

    def calculate_sla_metrics(self):
        """Calculate SLA metrics."""
        if self.first_response_at and self.created_at:
            self.time_to_first_response = self.first_response_at - self.created_at

        if self.resolved_at and self.created_at:
            self.time_to_resolution = self.resolved_at - self.created_at

        self.save(update_fields=["time_to_first_response", "time_to_resolution"])


class TicketComment(models.Model):
    """Comments and notes on tickets."""

    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ticket_comments"
    )
    content = models.TextField()

    # Comment type
    comment_type = models.CharField(
        max_length=20,
        choices=[
            ("public", "Public Comment"),
            ("internal", "Internal Note"),
            ("system", "System Message"),
        ],
        default="public",
    )

    # Attachments
    has_attachments = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tickets_ticket_comment"
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
            models.Index(fields=["author", "created_at"]),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.ticket.ticket_number} by {self.author.email}"


class TicketAttachment(models.Model):
    """File attachments for tickets."""

    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="attachments"
    )
    comment = models.ForeignKey(
        TicketComment,
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ticket_attachments"
    )

    # File information
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=100)
    file_path = models.CharField(max_length=500)
    file_url = models.URLField(blank=True)

    # Metadata
    is_public = models.BooleanField(default=True)
    download_count = models.IntegerField(default=0)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tickets_ticket_attachment"
        indexes = [
            models.Index(fields=["ticket", "uploaded_at"]),
            models.Index(fields=["uploaded_by", "uploaded_at"]),
        ]

    def __str__(self):
        return f"{self.file_name} - {self.ticket.ticket_number}"


class TicketHistory(models.Model):
    """Audit trail for ticket changes."""

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="history")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ticket_history"
    )

    # Change information
    field_name = models.CharField(max_length=50)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    change_type = models.CharField(
        max_length=20,
        choices=[
            ("created", "Created"),
            ("updated", "Updated"),
            ("assigned", "Assigned"),
            ("status_changed", "Status Changed"),
            ("priority_changed", "Priority Changed"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
    )

    # Additional data
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tickets_ticket_history"
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["change_type", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.change_type} by {self.user.email}"


class CannedResponse(models.Model):
    """Pre-written responses for common issues."""

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="canned_responses"
    )
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    content = models.TextField()

    # Categorization
    category = models.CharField(max_length=50, blank=True)
    tags = models.JSONField(default=list, blank=True)

    # Usage tracking
    usage_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_canned_responses"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tickets_canned_response"
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["category"]),
            models.Index(fields=["usage_count"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.organization.name}"

    def increment_usage(self):
        """Increment usage count."""
        self.usage_count += 1
        self.save(update_fields=["usage_count"])
