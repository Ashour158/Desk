"""
Feature management models for comprehensive system organization.
"""

from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization


class FeatureCategory(models.Model):
    """Logical grouping of features by function."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="fas fa-cog")
    color = models.CharField(max_length=7, default="#2E86AB")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Feature Categories"

    def __str__(self):
        return self.name


class Feature(models.Model):
    """Individual system features."""

    FEATURE_TYPES = [
        ("core", "Core Feature"),
        ("advanced", "Advanced Feature"),
        ("integration", "Integration"),
        ("automation", "Automation"),
        ("analytics", "Analytics"),
        ("communication", "Communication"),
        ("security", "Security"),
        ("mobile", "Mobile"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("maintenance", "Maintenance"),
        ("beta", "Beta"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPES)
    category = models.ForeignKey(
        FeatureCategory, on_delete=models.CASCADE, related_name="features"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Feature configuration
    endpoint = models.CharField(max_length=200, blank=True, null=True)
    api_version = models.CharField(max_length=10, default="v1")
    requires_auth = models.BooleanField(default=True)
    requires_permission = models.CharField(max_length=100, blank=True, null=True)

    # Real-time capabilities
    supports_realtime = models.BooleanField(default=False)
    websocket_channel = models.CharField(max_length=100, blank=True, null=True)

    # Integration settings
    microservice = models.CharField(max_length=100, blank=True, null=True)
    external_service = models.CharField(max_length=100, blank=True, null=True)

    # UI settings
    icon = models.CharField(max_length=50, default="fas fa-cog")
    color = models.CharField(max_length=7, default="#2E86AB")
    order = models.PositiveIntegerField(default=0)

    # Feature metadata
    version = models.CharField(max_length=20, default="1.0.0")
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Organization-specific settings
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    is_global = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        unique_together = ["name", "organization"]

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        """Check if feature is available for use."""
        return self.status == "active" and self.is_global

    @property
    def full_endpoint(self):
        """Get full API endpoint URL."""
        if self.endpoint:
            return f"/api/{self.api_version}/{self.endpoint}/"
        return None

    def get_websocket_channel(self):
        """Get WebSocket channel for real-time updates."""
        if self.supports_realtime and self.websocket_channel:
            return self.websocket_channel
        return None


class FeaturePermission(models.Model):
    """Feature-specific permissions."""

    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="permissions"
    )
    permission_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["feature", "permission_name"]

    def __str__(self):
        return f"{self.feature.name} - {self.permission_name}"


class FeatureConnection(models.Model):
    """Connections between features."""

    CONNECTION_TYPES = [
        ("data_flow", "Data Flow"),
        ("workflow", "Workflow"),
        ("integration", "Integration"),
        ("dependency", "Dependency"),
        ("notification", "Notification"),
    ]

    source_feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="outgoing_connections"
    )
    target_feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="incoming_connections"
    )
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["source_feature", "target_feature", "connection_type"]

    def __str__(self):
        return f"{self.source_feature.name} -> {self.target_feature.name}"


class FeatureUsage(models.Model):
    """Track feature usage statistics."""

    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="usage_stats"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    # Usage metrics
    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    session_duration = models.DurationField(null=True, blank=True)

    # Performance metrics
    response_time = models.FloatField(null=True, blank=True)  # in milliseconds
    error_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["feature", "user", "organization"]

    def __str__(self):
        return f"{self.feature.name} - {self.organization.name}"


class FeatureHealth(models.Model):
    """Feature health monitoring."""

    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="health_checks"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("healthy", "Healthy"),
            ("degraded", "Degraded"),
            ("unhealthy", "Unhealthy"),
            ("unknown", "Unknown"),
        ],
    )
    response_time = models.FloatField(null=True, blank=True)
    error_rate = models.FloatField(default=0.0)
    last_check = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-last_check"]

    def __str__(self):
        return f"{self.feature.name} - {self.status}"


class FeatureConfiguration(models.Model):
    """Feature-specific configuration."""

    feature = models.ForeignKey(
        Feature, on_delete=models.CASCADE, related_name="configurations"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )

    # Configuration data
    config_key = models.CharField(max_length=100)
    config_value = models.TextField()
    config_type = models.CharField(
        max_length=20,
        choices=[
            ("string", "String"),
            ("integer", "Integer"),
            ("boolean", "Boolean"),
            ("json", "JSON"),
            ("url", "URL"),
        ],
        default="string",
    )

    is_encrypted = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["feature", "organization", "config_key"]

    def __str__(self):
        return f"{self.feature.name} - {self.config_key}"
