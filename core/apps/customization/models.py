"""
Advanced customization models for helpdesk platform.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import uuid

User = get_user_model()


class CustomObject(models.Model):
    """Custom objects for organizations."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Object configuration
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)

    # Permissions
    can_create = models.BooleanField(default=True)
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=True)

    # UI configuration
    icon = models.CharField(max_length=50, default="fas fa-cube")
    color = models.CharField(max_length=7, default="#007bff")
    sort_order = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ["organization", "name"]
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.organization.name} - {self.display_name}"


class CustomField(models.Model):
    """Custom fields for objects."""

    FIELD_TYPES = [
        ("text", "Text"),
        ("textarea", "Text Area"),
        ("number", "Number"),
        ("email", "Email"),
        ("url", "URL"),
        ("date", "Date"),
        ("datetime", "Date Time"),
        ("boolean", "Boolean"),
        ("choice", "Choice"),
        ("multi_choice", "Multiple Choice"),
        ("file", "File"),
        ("image", "Image"),
        ("json", "JSON"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    custom_object = models.ForeignKey(
        CustomObject, on_delete=models.CASCADE, related_name="fields"
    )

    # Field configuration
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    description = models.TextField(blank=True)

    # Field properties
    is_required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=True)
    is_filterable = models.BooleanField(default=True)

    # Field options
    default_value = models.TextField(blank=True)
    choices = models.JSONField(default=list, blank=True)  # For choice fields
    validation_rules = models.JSONField(default=dict, blank=True)

    # UI configuration
    placeholder = models.CharField(max_length=255, blank=True)
    help_text = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ["custom_object", "name"]
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.custom_object.display_name} - {self.display_name}"


class CustomObjectInstance(models.Model):
    """Instances of custom objects."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    custom_object = models.ForeignKey(CustomObject, on_delete=models.CASCADE)

    # Instance data
    data = models.JSONField(default=dict)

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "custom_object"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.custom_object.display_name} Instance"


class WorkflowTemplate(models.Model):
    """Workflow templates for automation."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Workflow configuration
    trigger_type = models.CharField(
        max_length=50
    )  # ticket_created, work_order_assigned, etc.
    conditions = models.JSONField(default=list)
    actions = models.JSONField(default=list)

    # Status
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class DashboardTemplate(models.Model):
    """Dashboard templates for customization."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Dashboard configuration
    layout = models.JSONField(default=dict)
    widgets = models.JSONField(default=list)
    permissions = models.JSONField(default=dict)

    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class CustomTheme(models.Model):
    """Custom themes for organizations."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Theme configuration
    primary_color = models.CharField(max_length=7, default="#007bff")
    secondary_color = models.CharField(max_length=7, default="#6c757d")
    success_color = models.CharField(max_length=7, default="#28a745")
    warning_color = models.CharField(max_length=7, default="#ffc107")
    danger_color = models.CharField(max_length=7, default="#dc3545")
    info_color = models.CharField(max_length=7, default="#17a2b8")

    # Typography
    font_family = models.CharField(max_length=100, default="Inter, sans-serif")
    font_size = models.CharField(max_length=10, default="14px")

    # Layout
    sidebar_width = models.CharField(max_length=10, default="250px")
    header_height = models.CharField(max_length=10, default="60px")

    # Custom CSS
    custom_css = models.TextField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class CustomPermission(models.Model):
    """Custom permissions for organizations."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Permission configuration
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    custom_object = models.ForeignKey(
        CustomObject, on_delete=models.CASCADE, null=True, blank=True
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ["organization", "codename"]
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class CustomRole(models.Model):
    """Custom roles for organizations."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Role configuration
    permissions = models.ManyToManyField(CustomPermission, blank=True)
    is_system = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class CustomReport(models.Model):
    """Custom reports for organizations."""

    REPORT_TYPES = [
        ("table", "Table"),
        ("chart", "Chart"),
        ("dashboard", "Dashboard"),
        ("export", "Export"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)

    # Report configuration
    query = models.TextField()
    parameters = models.JSONField(default=dict)
    filters = models.JSONField(default=list)
    columns = models.JSONField(default=list)

    # UI configuration
    chart_config = models.JSONField(default=dict, blank=True)
    layout_config = models.JSONField(default=dict, blank=True)

    # Permissions
    is_public = models.BooleanField(default=False)
    allowed_roles = models.ManyToManyField(CustomRole, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class CustomIntegration(models.Model):
    """Custom integrations for organizations."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Integration configuration
    integration_type = models.CharField(max_length=50)  # webhook, api, oauth, etc.
    config = models.JSONField(default=dict)
    credentials = models.JSONField(default=dict)

    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class CustomNotificationTemplate(models.Model):
    """Custom notification templates."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Template configuration
    template_type = models.CharField(max_length=50)  # email, sms, push, etc.
    subject = models.CharField(max_length=255, blank=True)
    body_html = models.TextField(blank=True)
    body_text = models.TextField(blank=True)

    # Template variables
    variables = models.JSONField(default=list)

    # Status
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"
