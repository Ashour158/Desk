"""
Enhanced Advanced Security & Compliance Suite models for advanced capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class ThreatProtection(models.Model):
    """Advanced Threat Protection with AI-powered threat detection and behavioral analytics."""

    THREAT_TYPE_CHOICES = [
        ("malware", "Malware"),
        ("phishing", "Phishing"),
        ("ddos", "DDoS"),
        ("insider_threat", "Insider Threat"),
        ("advanced_persistent_threat", "Advanced Persistent Threat"),
        ("zero_day", "Zero Day"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPE_CHOICES)
    protection_config = models.JSONField(default=dict)
    ai_detection_rules = models.JSONField(default=list)
    behavioral_analytics = models.JSONField(default=dict)
    threat_intelligence = models.JSONField(default=dict)
    incident_response = models.JSONField(default=dict)
    total_threats_detected = models.PositiveIntegerField(default=0)
    threats_blocked = models.PositiveIntegerField(default=0)
    false_positives = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Threat Protection"
        verbose_name_plural = "Threat Protections"

    def __str__(self):
        return self.name


class SecurityManagement(models.Model):
    """Enterprise Security Management with SIEM, SOAR, and vulnerability management."""

    MANAGEMENT_TYPE_CHOICES = [
        ("siem", "SIEM"),
        ("soar", "SOAR"),
        ("vulnerability_management", "Vulnerability Management"),
        ("security_orchestration", "Security Orchestration"),
        ("incident_management", "Incident Management"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    management_type = models.CharField(max_length=50, choices=MANAGEMENT_TYPE_CHOICES)
    siem_config = models.JSONField(default=dict)
    soar_config = models.JSONField(default=dict)
    vulnerability_scanning = models.JSONField(default=dict)
    security_policies = models.JSONField(default=list)
    incident_workflows = models.JSONField(default=list)
    total_incidents = models.PositiveIntegerField(default=0)
    resolved_incidents = models.PositiveIntegerField(default=0)
    average_resolution_time = models.DurationField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Security Management"
        verbose_name_plural = "Security Managements"

    def __str__(self):
        return self.name


class AuthenticationAuthorization(models.Model):
    """Advanced Authentication & Authorization with biometric authentication and PAM."""

    AUTH_TYPE_CHOICES = [
        ("multi_factor", "Multi-Factor Authentication"),
        ("biometric", "Biometric Authentication"),
        ("privileged_access", "Privileged Access Management"),
        ("single_sign_on", "Single Sign-On"),
        ("zero_trust", "Zero Trust Authentication"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    auth_type = models.CharField(max_length=50, choices=AUTH_TYPE_CHOICES)
    authentication_methods = models.JSONField(default=list)
    authorization_rules = models.JSONField(default=list)
    biometric_config = models.JSONField(default=dict)
    pam_config = models.JSONField(default=dict)
    zero_trust_config = models.JSONField(default=dict)
    total_authentications = models.PositiveIntegerField(default=0)
    successful_authentications = models.PositiveIntegerField(default=0)
    failed_authentications = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Authentication & Authorization"
        verbose_name_plural = "Authentication & Authorizations"

    def __str__(self):
        return self.name


class DataProtection(models.Model):
    """Data Protection & Privacy with DLP, consent management, and data anonymization."""

    PROTECTION_TYPE_CHOICES = [
        ("data_loss_prevention", "Data Loss Prevention"),
        ("consent_management", "Consent Management"),
        ("data_anonymization", "Data Anonymization"),
        ("encryption", "Encryption"),
        ("data_classification", "Data Classification"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    protection_type = models.CharField(max_length=50, choices=PROTECTION_TYPE_CHOICES)
    dlp_config = models.JSONField(default=dict)
    consent_management = models.JSONField(default=dict)
    anonymization_rules = models.JSONField(default=list)
    encryption_settings = models.JSONField(default=dict)
    data_classification = models.JSONField(default=dict)
    total_data_protected = models.PositiveIntegerField(default=0)
    data_breaches_prevented = models.PositiveIntegerField(default=0)
    compliance_score = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Data Protection"
        verbose_name_plural = "Data Protections"

    def __str__(self):
        return self.name


class ComplianceGovernance(models.Model):
    """Compliance & Governance with regulatory compliance automation and audit trail management."""

    COMPLIANCE_TYPE_CHOICES = [
        ("gdpr", "GDPR"),
        ("hipaa", "HIPAA"),
        ("sox", "SOX"),
        ("pci_dss", "PCI DSS"),
        ("iso_27001", "ISO 27001"),
        ("custom", "Custom Compliance"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    compliance_type = models.CharField(max_length=50, choices=COMPLIANCE_TYPE_CHOICES)
    compliance_framework = models.JSONField(default=dict)
    audit_trail_config = models.JSONField(default=dict)
    regulatory_requirements = models.JSONField(default=list)
    compliance_monitoring = models.JSONField(default=dict)
    reporting_automation = models.JSONField(default=dict)
    total_audits = models.PositiveIntegerField(default=0)
    compliance_score = models.FloatField(default=0.0)
    last_audit = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compliance & Governance"
        verbose_name_plural = "Compliance & Governances"

    def __str__(self):
        return self.name


class SecurityIncident(models.Model):
    """Security Incident for tracking and managing security events."""

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("investigating", "Investigating"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    incident_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    threat_type = models.CharField(max_length=100, null=True, blank=True)
    affected_systems = models.JSONField(default=list)
    incident_data = models.JSONField(default=dict)
    resolution_notes = models.TextField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Security Incident"
        verbose_name_plural = "Security Incidents"

    def __str__(self):
        return f"{self.incident_id} - {self.title}"


class SecurityAudit(models.Model):
    """Security Audit for compliance and security assessments."""

    AUDIT_TYPE_CHOICES = [
        ("compliance", "Compliance Audit"),
        ("security", "Security Audit"),
        ("penetration_test", "Penetration Test"),
        ("vulnerability_assessment", "Vulnerability Assessment"),
        ("risk_assessment", "Risk Assessment"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    audit_id = models.CharField(max_length=100, unique=True)
    audit_type = models.CharField(max_length=50, choices=AUDIT_TYPE_CHOICES)
    audit_scope = models.JSONField(default=dict)
    audit_findings = models.JSONField(default=list)
    compliance_requirements = models.JSONField(default=list)
    audit_results = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    audit_score = models.FloatField(default=0.0)
    audit_date = models.DateTimeField()
    auditor = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Security Audit"
        verbose_name_plural = "Security Audits"

    def __str__(self):
        return f"{self.audit_id} - {self.audit_type}"


class SecurityPolicy(models.Model):
    """Security Policy for defining security rules and procedures."""

    POLICY_TYPE_CHOICES = [
        ("access_control", "Access Control"),
        ("data_protection", "Data Protection"),
        ("incident_response", "Incident Response"),
        ("password_policy", "Password Policy"),
        ("network_security", "Network Security"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPE_CHOICES)
    policy_content = models.TextField()
    policy_rules = models.JSONField(default=list)
    enforcement_config = models.JSONField(default=dict)
    compliance_requirements = models.JSONField(default=list)
    approval_workflow = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Security Policy"
        verbose_name_plural = "Security Policies"

    def __str__(self):
        return self.name


class SecurityMetric(models.Model):
    """Security Metric for tracking security performance and compliance."""

    METRIC_TYPE_CHOICES = [
        ("threat_detection", "Threat Detection"),
        ("incident_response", "Incident Response"),
        ("compliance", "Compliance"),
        ("vulnerability", "Vulnerability"),
        ("access_control", "Access Control"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    metric_name = models.CharField(max_length=200)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPE_CHOICES)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=50)
    target_value = models.FloatField(null=True, blank=True)
    metric_data = models.JSONField(default=dict)
    measurement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Security Metric"
        verbose_name_plural = "Security Metrics"

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.metric_unit}"
