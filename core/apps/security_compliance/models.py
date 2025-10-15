"""
Security and compliance suite models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class ZeroTrustPolicy(models.Model):
    """Zero Trust security policies."""

    POLICY_TYPES = [
        ("access_control", "Access Control"),
        ("device_trust", "Device Trust"),
        ("network_segmentation", "Network Segmentation"),
        ("data_protection", "Data Protection"),
        ("identity_verification", "Identity Verification"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES)
    description = models.TextField(blank=True)

    # Policy configuration
    rules = models.JSONField(default=list)
    conditions = models.JSONField(default=list)
    actions = models.JSONField(default=list)

    # Trust factors
    trust_factors = models.JSONField(default=list)
    risk_threshold = models.FloatField(default=0.5)
    verification_required = models.BooleanField(default=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_enforced = models.BooleanField(default=True)

    # Statistics
    evaluation_count = models.IntegerField(default=0)
    violation_count = models.IntegerField(default=0)
    last_evaluated = models.DateTimeField(blank=True, null=True)

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


class ThreatDetection(models.Model):
    """Threat detection and monitoring."""

    THREAT_TYPES = [
        ("malware", "Malware"),
        ("phishing", "Phishing"),
        ("brute_force", "Brute Force"),
        ("ddos", "DDoS"),
        ("insider_threat", "Insider Threat"),
        ("data_exfiltration", "Data Exfiltration"),
        ("privilege_escalation", "Privilege Escalation"),
        ("anomalous_behavior", "Anomalous Behavior"),
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
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)

    # Threat details
    title = models.CharField(max_length=255)
    description = models.TextField()
    source_ip = models.GenericIPAddressField(blank=True, null=True)
    target_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    # Detection data
    detection_rules = models.JSONField(default=list)
    indicators = models.JSONField(default=list)
    evidence = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)

    # Context
    affected_users = models.JSONField(default=list)
    affected_systems = models.JSONField(default=list)
    related_incidents = models.JSONField(default=list)

    # Status
    is_acknowledged = models.BooleanField(default=False)
    is_investigating = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    is_false_positive = models.BooleanField(default=False)

    # Response
    response_actions = models.JSONField(default=list)
    mitigation_steps = models.JSONField(default=list)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Timestamps
    detected_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["organization", "threat_type"]),
            models.Index(fields=["severity", "is_resolved"]),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.title}"


class ComplianceStandard(models.Model):
    """Compliance standards and frameworks."""

    STANDARD_TYPES = [
        ("gdpr", "GDPR"),
        ("hipaa", "HIPAA"),
        ("sox", "SOX"),
        ("pci_dss", "PCI DSS"),
        ("iso27001", "ISO 27001"),
        ("soc2", "SOC 2"),
        ("nist", "NIST"),
        ("fedramp", "FedRAMP"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    standard_type = models.CharField(max_length=50, choices=STANDARD_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Standard details
    version = models.CharField(max_length=20, default="1.0")
    effective_date = models.DateField()
    requirements = models.JSONField(default=list)
    controls = models.JSONField(default=list)

    # Compliance status
    compliance_score = models.FloatField(default=0.0)
    requirements_met = models.IntegerField(default=0)
    requirements_total = models.IntegerField(default=0)
    last_assessment = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_certified = models.BooleanField(default=False)
    certification_date = models.DateTimeField(blank=True, null=True)
    certification_expiry = models.DateTimeField(blank=True, null=True)

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


class ComplianceAssessment(models.Model):
    """Compliance assessments and audits."""

    ASSESSMENT_TYPES = [
        ("self_assessment", "Self Assessment"),
        ("internal_audit", "Internal Audit"),
        ("external_audit", "External Audit"),
        ("penetration_test", "Penetration Test"),
        ("vulnerability_assessment", "Vulnerability Assessment"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    standard = models.ForeignKey(ComplianceStandard, on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPES)

    # Assessment details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scope = models.TextField()
    methodology = models.TextField()

    # Results
    overall_score = models.FloatField(default=0.0)
    findings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    action_plan = models.JSONField(default=list)

    # Status
    status = models.CharField(max_length=50, default="planned")
    is_completed = models.BooleanField(default=False)
    requires_follow_up = models.BooleanField(default=False)

    # Timestamps
    planned_start = models.DateTimeField(blank=True, null=True)
    planned_end = models.DateTimeField(blank=True, null=True)
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)

    # Personnel
    assessor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_assessments",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assessments",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class DataGovernance(models.Model):
    """Data governance and classification."""

    DATA_CLASSIFICATIONS = [
        ("public", "Public"),
        ("internal", "Internal"),
        ("confidential", "Confidential"),
        ("restricted", "Restricted"),
        ("top_secret", "Top Secret"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    data_classification = models.CharField(max_length=50, choices=DATA_CLASSIFICATIONS)
    description = models.TextField(blank=True)

    # Data details
    data_type = models.CharField(max_length=100)
    data_source = models.CharField(max_length=255)
    data_owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Governance rules
    retention_period = models.IntegerField(default=0)  # days
    access_controls = models.JSONField(default=list)
    sharing_restrictions = models.JSONField(default=list)
    encryption_required = models.BooleanField(default=False)

    # Compliance
    applicable_standards = models.JSONField(default=list)
    privacy_requirements = models.JSONField(default=list)
    legal_requirements = models.JSONField(default=list)

    # Status
    is_active = models.BooleanField(default=True)
    is_encrypted = models.BooleanField(default=False)
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


class SecurityOrchestration(models.Model):
    """Security orchestration and automation."""

    ORCHESTRATION_TYPES = [
        ("incident_response", "Incident Response"),
        ("threat_hunting", "Threat Hunting"),
        ("vulnerability_management", "Vulnerability Management"),
        ("compliance_monitoring", "Compliance Monitoring"),
        ("security_awareness", "Security Awareness"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    orchestration_type = models.CharField(max_length=50, choices=ORCHESTRATION_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Orchestration configuration
    workflow = models.JSONField(default=dict)
    triggers = models.JSONField(default=list)
    conditions = models.JSONField(default=list)
    actions = models.JSONField(default=list)

    # Automation
    is_automated = models.BooleanField(default=True)
    automation_level = models.CharField(max_length=50, default="semi_automated")
    human_approval_required = models.BooleanField(default=False)

    # Performance
    execution_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    average_execution_time = models.FloatField(default=0.0)

    # Status
    is_active = models.BooleanField(default=True)
    last_executed = models.DateTimeField(blank=True, null=True)
    next_execution = models.DateTimeField(blank=True, null=True)

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


class IncidentResponse(models.Model):
    """Security incident response management."""

    INCIDENT_TYPES = [
        ("data_breach", "Data Breach"),
        ("malware", "Malware"),
        ("phishing", "Phishing"),
        ("ddos", "DDoS"),
        ("insider_threat", "Insider Threat"),
        ("system_compromise", "System Compromise"),
        ("unauthorized_access", "Unauthorized Access"),
        ("data_loss", "Data Loss"),
    ]

    SEVERITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("reported", "Reported"),
        ("investigating", "Investigating"),
        ("contained", "Contained"),
        ("eradicated", "Eradicated"),
        ("recovered", "Recovered"),
        ("closed", "Closed"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="reported")

    # Incident details
    title = models.CharField(max_length=255)
    description = models.TextField()
    impact_assessment = models.TextField(blank=True)

    # Response team
    incident_commander = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commanded_incidents",
    )
    response_team = models.ManyToManyField(
        User, blank=True, related_name="incident_team"
    )

    # Timeline
    detected_at = models.DateTimeField(auto_now_add=True)
    reported_at = models.DateTimeField(blank=True, null=True)
    contained_at = models.DateTimeField(blank=True, null=True)
    eradicated_at = models.DateTimeField(blank=True, null=True)
    recovered_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    # Response actions
    containment_actions = models.JSONField(default=list)
    eradication_actions = models.JSONField(default=list)
    recovery_actions = models.JSONField(default=list)
    lessons_learned = models.TextField(blank=True)

    # Documentation
    evidence = models.JSONField(default=list)
    communications = models.JSONField(default=list)
    reports = models.JSONField(default=list)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["organization", "incident_type"]),
            models.Index(fields=["severity", "status"]),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.title}"


class PenetrationTest(models.Model):
    """Penetration testing and vulnerability assessments."""

    TEST_TYPES = [
        ("black_box", "Black Box"),
        ("white_box", "White Box"),
        ("gray_box", "Gray Box"),
        ("web_application", "Web Application"),
        ("network", "Network"),
        ("wireless", "Wireless"),
        ("social_engineering", "Social Engineering"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    test_type = models.CharField(max_length=50, choices=TEST_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Test details
    scope = models.TextField()
    methodology = models.TextField()
    tools_used = models.JSONField(default=list)

    # Results
    vulnerabilities_found = models.IntegerField(default=0)
    critical_vulnerabilities = models.IntegerField(default=0)
    high_vulnerabilities = models.IntegerField(default=0)
    medium_vulnerabilities = models.IntegerField(default=0)
    low_vulnerabilities = models.IntegerField(default=0)

    # Risk assessment
    overall_risk_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=20, default="low")
    recommendations = models.JSONField(default=list)

    # Status
    status = models.CharField(max_length=50, default="planned")
    is_completed = models.BooleanField(default=False)
    requires_remediation = models.BooleanField(default=False)

    # Timestamps
    planned_start = models.DateTimeField(blank=True, null=True)
    planned_end = models.DateTimeField(blank=True, null=True)
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)

    # Personnel
    tester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_tests",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tests",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"
