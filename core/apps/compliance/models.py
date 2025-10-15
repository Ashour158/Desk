"""
Compliance models for helpdesk platform.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class ComplianceFramework(models.Model):
    """Compliance frameworks (GDPR, HIPAA, SOX, etc.)."""

    FRAMEWORK_TYPES = [
        ("gdpr", "GDPR"),
        ("hipaa", "HIPAA"),
        ("sox", "SOX"),
        ("pci_dss", "PCI DSS"),
        ("iso27001", "ISO 27001"),
        ("ccpa", "CCPA"),
        ("ferpa", "FERPA"),
        ("coppa", "COPPA"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    framework_type = models.CharField(max_length=20, choices=FRAMEWORK_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Framework configuration
    requirements = models.JSONField(default=list)
    controls = models.JSONField(default=list)
    policies = models.JSONField(default=list)

    # Status
    is_active = models.BooleanField(default=True)
    compliance_level = models.IntegerField(default=0)  # 0-100%

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ["organization", "framework_type"]
        ordering = ["framework_type"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class ComplianceRequirement(models.Model):
    """Individual compliance requirements."""

    PRIORITY_LEVELS = [
        ("critical", "Critical"),
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("non_applicable", "Non-Applicable"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE)

    # Requirement details
    requirement_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)

    # Compliance details
    priority = models.CharField(
        max_length=20, choices=PRIORITY_LEVELS, default="medium"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )
    compliance_level = models.IntegerField(default=0)  # 0-100%

    # Implementation details
    implementation_notes = models.TextField(blank=True)
    evidence = models.JSONField(default=list)
    responsible_person = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Dates
    due_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["organization", "framework", "requirement_id"]
        ordering = ["priority", "requirement_id"]

    def __str__(self):
        return f"{self.framework.name} - {self.title}"


class DataProcessingActivity(models.Model):
    """Data processing activities for GDPR compliance."""

    PROCESSING_PURPOSES = [
        ("support", "Customer Support"),
        ("marketing", "Marketing"),
        ("analytics", "Analytics"),
        ("security", "Security"),
        ("legal", "Legal Compliance"),
        ("contract", "Contract Performance"),
    ]

    LEGAL_BASIS = [
        ("consent", "Consent"),
        ("contract", "Contract"),
        ("legal_obligation", "Legal Obligation"),
        ("vital_interests", "Vital Interests"),
        ("public_task", "Public Task"),
        ("legitimate_interests", "Legitimate Interests"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    purpose = models.CharField(max_length=50, choices=PROCESSING_PURPOSES)
    legal_basis = models.CharField(max_length=50, choices=LEGAL_BASIS)

    # Data categories
    personal_data_categories = models.JSONField(default=list)
    special_categories = models.JSONField(default=list)

    # Data subjects
    data_subjects = models.JSONField(default=list)
    data_retention_period = models.IntegerField(default=365)  # days

    # Third parties
    third_parties = models.JSONField(default=list)
    international_transfers = models.JSONField(default=list)

    # Security measures
    technical_measures = models.JSONField(default=list)
    organizational_measures = models.JSONField(default=list)

    # Status
    is_active = models.BooleanField(default=True)
    last_reviewed = models.DateTimeField(blank=True, null=True)

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


class DataSubjectRequest(models.Model):
    """Data subject requests (GDPR Article 15-22)."""

    REQUEST_TYPES = [
        ("access", "Access Request (Article 15)"),
        ("rectification", "Rectification Request (Article 16)"),
        ("erasure", "Erasure Request (Article 17)"),
        ("restriction", "Restriction Request (Article 18)"),
        ("portability", "Data Portability (Article 20)"),
        ("objection", "Objection Request (Article 21)"),
    ]

    STATUS_CHOICES = [
        ("received", "Received"),
        ("under_review", "Under Review"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received")

    # Data subject information
    data_subject_name = models.CharField(max_length=255)
    data_subject_email = models.EmailField()
    data_subject_phone = models.CharField(max_length=20, blank=True)
    data_subject_address = models.TextField(blank=True)

    # Request details
    description = models.TextField()
    requested_data = models.JSONField(default=list)
    verification_method = models.CharField(max_length=50, default="email")
    verification_status = models.BooleanField(default=False)

    # Processing
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    processing_notes = models.TextField(blank=True)
    response_data = models.JSONField(default=dict)

    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-received_at"]

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.data_subject_name}"


class PrivacyPolicy(models.Model):
    """Privacy policies for organizations."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    version = models.CharField(max_length=20, default="1.0")

    # Policy details
    effective_date = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)
    language = models.CharField(max_length=10, default="en")

    # Status
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-effective_date"]

    def __str__(self):
        return f"{self.organization.name} - {self.title} v{self.version}"


class ConsentRecord(models.Model):
    """Consent records for data processing."""

    CONSENT_TYPES = [
        ("explicit", "Explicit Consent"),
        ("implied", "Implied Consent"),
        ("opt_in", "Opt-in"),
        ("opt_out", "Opt-out"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    data_subject_email = models.EmailField()
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)

    # Consent details
    purpose = models.CharField(max_length=255)
    legal_basis = models.CharField(max_length=50)
    consent_given = models.BooleanField(default=True)
    consent_withdrawn = models.BooleanField(default=False)

    # Consent evidence
    consent_method = models.CharField(max_length=50)  # email, form, checkbox, etc.
    consent_text = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    # Timestamps
    given_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-given_at"]
        indexes = [
            models.Index(fields=["organization", "data_subject_email"]),
            models.Index(fields=["consent_given", "consent_withdrawn"]),
        ]

    def __str__(self):
        return f"{self.data_subject_email} - {self.purpose}"


class DataBreach(models.Model):
    """Data breach records for compliance reporting."""

    SEVERITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("detected", "Detected"),
        ("investigating", "Investigating"),
        ("contained", "Contained"),
        ("resolved", "Resolved"),
        ("reported", "Reported to Authorities"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    breach_id = models.UUIDField(default=uuid.uuid4, unique=True)

    # Breach details
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="detected")

    # Impact assessment
    affected_records = models.IntegerField(default=0)
    affected_data_subjects = models.IntegerField(default=0)
    data_categories = models.JSONField(default=list)
    special_categories = models.JSONField(default=list)

    # Timeline
    detected_at = models.DateTimeField(auto_now_add=True)
    occurred_at = models.DateTimeField(blank=True, null=True)
    contained_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    # Reporting
    reported_to_authorities = models.BooleanField(default=False)
    reported_to_data_subjects = models.BooleanField(default=False)
    authority_notification_date = models.DateTimeField(blank=True, null=True)
    data_subject_notification_date = models.DateTimeField(blank=True, null=True)

    # Investigation
    root_cause = models.TextField(blank=True)
    corrective_actions = models.JSONField(default=list)
    preventive_measures = models.JSONField(default=list)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-detected_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.title}"


class ComplianceAudit(models.Model):
    """Compliance audits and assessments."""

    AUDIT_TYPES = [
        ("internal", "Internal Audit"),
        ("external", "External Audit"),
        ("self_assessment", "Self Assessment"),
        ("certification", "Certification Audit"),
    ]

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE)

    # Audit details
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")

    # Scope
    scope = models.JSONField(default=list)
    excluded_areas = models.JSONField(default=list)

    # Results
    total_requirements = models.IntegerField(default=0)
    compliant_requirements = models.IntegerField(default=0)
    non_compliant_requirements = models.IntegerField(default=0)
    partially_compliant_requirements = models.IntegerField(default=0)

    # Findings
    findings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    action_plan = models.JSONField(default=list)

    # Dates
    planned_start = models.DateTimeField()
    planned_end = models.DateTimeField()
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)

    # Auditors
    lead_auditor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_audits",
    )
    audit_team = models.ManyToManyField(User, blank=True, related_name="audit_team")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-planned_start"]

    def __str__(self):
        return f"{self.organization.name} - {self.title}"
