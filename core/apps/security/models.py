"""
Enterprise security models for helpdesk platform.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils import timezone
from django_cryptography.fields import encrypt
import uuid

User = get_user_model()


class SecurityPolicy(models.Model):
    """Organization security policies."""

    POLICY_TYPES = [
        ("password", "Password Policy"),
        ("session", "Session Policy"),
        ("ip_whitelist", "IP Whitelist"),
        ("device_trust", "Device Trust"),
        ("data_retention", "Data Retention"),
        ("audit", "Audit Policy"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Policy configuration
    config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ["organization", "policy_type", "name"]
        ordering = ["policy_type", "name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class SSOConfiguration(models.Model):
    """Single Sign-On configuration."""

    SSO_TYPES = [
        ("saml", "SAML 2.0"),
        ("oauth2", "OAuth 2.0"),
        ("ldap", "LDAP"),
        ("azure_ad", "Azure Active Directory"),
        ("google_workspace", "Google Workspace"),
        ("okta", "Okta"),
    ]

    organization = models.OneToOneField(
        "organizations.Organization", on_delete=models.CASCADE
    )
    sso_type = models.CharField(max_length=50, choices=SSO_TYPES)
    name = models.CharField(max_length=255)

    # Configuration (encrypted)
    client_id = encrypt(models.CharField(max_length=255, blank=True))
    client_secret = encrypt(models.CharField(max_length=255, blank=True))
    issuer_url = models.URLField(blank=True)
    metadata_url = models.URLField(blank=True)
    certificate = encrypt(models.TextField(blank=True))

    # Advanced settings
    attribute_mapping = models.JSONField(default=dict)
    auto_provision = models.BooleanField(default=True)
    sync_groups = models.BooleanField(default=True)
    logout_url = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class DeviceTrust(models.Model):
    """Device trust management."""

    TRUST_LEVELS = [
        ("trusted", "Trusted"),
        ("suspicious", "Suspicious"),
        ("blocked", "Blocked"),
        ("unknown", "Unknown"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.UUIDField(default=uuid.uuid4, unique=True)
    device_name = models.CharField(max_length=255)
    device_type = models.CharField(max_length=50)  # desktop, mobile, tablet
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()

    # Trust information
    trust_level = models.CharField(
        max_length=20, choices=TRUST_LEVELS, default="unknown"
    )
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=50, blank=True)

    # Location data
    country = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)

    # Security features
    has_2fa = models.BooleanField(default=False)
    biometric_enabled = models.BooleanField(default=False)
    encryption_enabled = models.BooleanField(default=False)

    # Timestamps
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ["organization", "user", "device_id"]
        ordering = ["-last_seen"]

    def __str__(self):
        return f"{self.user.full_name} - {self.device_name}"


class SecurityEvent(models.Model):
    """Security events and alerts."""

    EVENT_TYPES = [
        ("login_success", "Successful Login"),
        ("login_failed", "Failed Login"),
        ("logout", "Logout"),
        ("password_change", "Password Changed"),
        ("2fa_enabled", "2FA Enabled"),
        ("2fa_disabled", "2FA Disabled"),
        ("suspicious_activity", "Suspicious Activity"),
        ("data_export", "Data Export"),
        ("admin_action", "Admin Action"),
        ("api_access", "API Access"),
        ("file_upload", "File Upload"),
        ("permission_change", "Permission Changed"),
    ]

    SEVERITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(
        max_length=20, choices=SEVERITY_LEVELS, default="medium"
    )

    # Event details
    title = models.CharField(max_length=255)
    description = models.TextField()
    details = models.JSONField(default=dict)

    # Context
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_id = models.UUIDField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)

    # Related entities
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.UUIDField(blank=True, null=True)

    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_events",
    )
    resolution_notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "event_type"]),
            models.Index(fields=["organization", "severity"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.organization.name}"


class ComplianceAudit(models.Model):
    """Compliance audit records."""

    COMPLIANCE_FRAMEWORKS = [
        ("gdpr", "GDPR"),
        ("hipaa", "HIPAA"),
        ("sox", "SOX"),
        ("pci_dss", "PCI DSS"),
        ("iso27001", "ISO 27001"),
        ("ccpa", "CCPA"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    framework = models.CharField(max_length=20, choices=COMPLIANCE_FRAMEWORKS)
    audit_type = models.CharField(max_length=100)

    # Audit details
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.JSONField(default=list)
    findings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)

    # Status
    status = models.CharField(max_length=20, default="pending")
    score = models.IntegerField(blank=True, null=True)
    max_score = models.IntegerField(default=100)

    # Dates
    audit_date = models.DateTimeField()
    due_date = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Auditors
    auditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_audits",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-audit_date"]

    def __str__(self):
        return f"{self.framework} - {self.title}"


class DataRetentionPolicy(models.Model):
    """Data retention policies."""

    RETENTION_TYPES = [
        ("tickets", "Tickets"),
        ("comments", "Comments"),
        ("attachments", "Attachments"),
        ("logs", "Logs"),
        ("notifications", "Notifications"),
        ("reports", "Reports"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    retention_type = models.CharField(max_length=50, choices=RETENTION_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Retention rules
    retention_period_days = models.IntegerField()
    archive_before_delete = models.BooleanField(default=True)
    anonymize_personal_data = models.BooleanField(default=True)

    # Legal requirements
    legal_basis = models.CharField(max_length=100, blank=True)
    compliance_framework = models.CharField(max_length=20, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["organization", "retention_type"]
        ordering = ["retention_type"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class APIAccessLog(models.Model):
    """API access logging."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Request details
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=255)
    status_code = models.IntegerField()
    response_time_ms = models.IntegerField()

    # Request data
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    request_size = models.IntegerField(default=0)
    response_size = models.IntegerField(default=0)

    # API key information
    api_key_id = models.CharField(max_length=100, blank=True)
    rate_limit_remaining = models.IntegerField(blank=True, null=True)

    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["organization", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["endpoint", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"


class SecurityScan(models.Model):
    """Security vulnerability scans."""

    SCAN_TYPES = [
        ("vulnerability", "Vulnerability Scan"),
        ("dependency", "Dependency Scan"),
        ("code_quality", "Code Quality Scan"),
        ("secrets", "Secrets Scan"),
        ("compliance", "Compliance Scan"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    scan_type = models.CharField(max_length=50, choices=SCAN_TYPES)
    name = models.CharField(max_length=255)

    # Scan results
    total_issues = models.IntegerField(default=0)
    critical_issues = models.IntegerField(default=0)
    high_issues = models.IntegerField(default=0)
    medium_issues = models.IntegerField(default=0)
    low_issues = models.IntegerField(default=0)

    # Scan data
    scan_data = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)

    # Status
    status = models.CharField(max_length=20, default="pending")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.name} - {self.scan_type}"
