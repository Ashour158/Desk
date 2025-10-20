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
            models.Index(fields=["assigned_agent", "status"]),  # For agent workload queries
            models.Index(fields=["sla_policy"]),  # For SLA queries
            models.Index(fields=["first_response_due"]),  # For SLA tracking
            models.Index(fields=["resolution_due"]),  # For SLA tracking
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)

    def generate_ticket_number(self):
        """Generate unique sequential ticket number."""
        # Get or create sequence for organization
        sequence, created = TicketNumberSequence.objects.get_or_create(
            organization=self.organization,
            defaults={
                "prefix": "TK",
                "current_number": 0,
                "padding_length": 5,
                "include_year": True,
                "include_month": False,
                "year_reset": True,
            },
        )

        return sequence.get_next_number()

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
    """Enhanced file attachments for tickets."""

    FILE_CATEGORIES = [
        ("image", "Image"),
        ("document", "Document"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("archive", "Archive"),
        ("other", "Other"),
    ]

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
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=100)  # MIME type
    file_category = models.CharField(
        max_length=20, choices=FILE_CATEGORIES, default="other"
    )
    file_path = models.CharField(max_length=500)
    file_url = models.URLField(blank=True)

    # Thumbnail for images
    thumbnail_path = models.CharField(max_length=500, blank=True)
    thumbnail_url = models.URLField(blank=True)

    # Security
    virus_scanned = models.BooleanField(default=False)
    virus_scan_result = models.CharField(max_length=50, blank=True)
    is_safe = models.BooleanField(default=False)

    # Metadata
    is_public = models.BooleanField(
        default=False, help_text="Visible to customers in portal"
    )
    download_count = models.IntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tickets_ticket_attachment"
        indexes = [
            models.Index(fields=["ticket", "uploaded_at"]),
            models.Index(fields=["uploaded_by", "uploaded_at"]),
            models.Index(fields=["file_category"]),
            models.Index(fields=["is_public"]),
        ]

    def __str__(self):
        return f"{self.file_name} - {self.ticket.ticket_number}"

    def record_download(self):
        """Record file download."""
        self.download_count += 1
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=["download_count", "last_downloaded_at"])

    def determine_file_category(self):
        """Determine file category from MIME type."""
        if self.file_type.startswith("image/"):
            return "image"
        elif self.file_type.startswith("video/"):
            return "video"
        elif self.file_type.startswith("audio/"):
            return "audio"
        elif self.file_type in [
            "application/pdf",
            "application/msword",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
        ]:
            return "document"
        elif self.file_type in [
            "application/zip",
            "application/x-rar-compressed",
            "application/x-7z-compressed",
        ]:
            return "archive"
        else:
            return "other"


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




class TicketNumberSequence(models.Model):
    """Database sequence for ticket numbering per organization."""

    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="ticket_sequence"
    )
    current_number = models.IntegerField(default=0)
    prefix = models.CharField(max_length=10, default="TK")
    year_reset = models.BooleanField(
        default=True, help_text="Reset counter at start of each year"
    )
    month_reset = models.BooleanField(
        default=False, help_text="Reset counter at start of each month"
    )
    padding_length = models.IntegerField(
        default=5, help_text="Number of digits (e.g., 5 = 00001)"
    )

    # Format options
    include_year = models.BooleanField(default=True)
    include_month = models.BooleanField(default=False)
    separator = models.CharField(max_length=5, default="-")

    last_reset_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "ticket_number_sequences"
        verbose_name = "Ticket Number Sequence"
        verbose_name_plural = "Ticket Number Sequences"

    def __str__(self):
        return f"{self.organization.name} - {self.prefix}"

    def get_next_number(self):
        """
        Get next ticket number with atomic increment.

        Returns:
            str: Formatted ticket number (e.g., "TK-2025-00001")
        """
        from django.db import transaction

        with transaction.atomic():
            # Lock the row for update
            sequence = TicketNumberSequence.objects.select_for_update().get(id=self.id)

            # Check if reset is needed
            current_date = timezone.now().date()
            should_reset = False

            if sequence.year_reset and current_date.year > sequence.last_reset_date.year:
                should_reset = True
            elif sequence.month_reset and (
                current_date.year > sequence.last_reset_date.year
                or current_date.month > sequence.last_reset_date.month
            ):
                should_reset = True

            if should_reset:
                sequence.current_number = 0
                sequence.last_reset_date = current_date

            # Increment counter
            sequence.current_number += 1
            sequence.save()

            # Format the number
            return sequence.format_ticket_number(sequence.current_number)

    def format_ticket_number(self, number):
        """
        Format ticket number according to configuration.

        Args:
            number: Sequential number

        Returns:
            str: Formatted ticket number

        Examples:
            - TK-2025-00001 (with year)
            - TK-2025-10-00001 (with year and month)
            - TK-00001 (no year/month)
        """
        parts = [self.prefix]

        current_date = timezone.now().date()

        if self.include_year:
            parts.append(str(current_date.year))

        if self.include_month:
            parts.append(str(current_date.month).zfill(2))

        # Add padded number
        padded_number = str(number).zfill(self.padding_length)
        parts.append(padded_number)

        return self.separator.join(parts)

