"""
Enhanced Advanced Security & Compliance Suite serializers for advanced capabilities.
"""

from rest_framework import serializers
from .enhanced_models import (
    ThreatProtection,
    SecurityManagement,
    AuthenticationAuthorization,
    DataProtection,
    ComplianceGovernance,
    SecurityIncident,
    SecurityAudit,
    SecurityPolicy,
    SecurityMetric,
)


class ThreatProtectionSerializer(serializers.ModelSerializer):
    """Serializer for Threat Protection."""

    class Meta:
        model = ThreatProtection
        fields = [
            "id",
            "name",
            "threat_type",
            "protection_config",
            "ai_detection_rules",
            "behavioral_analytics",
            "threat_intelligence",
            "incident_response",
            "total_threats_detected",
            "threats_blocked",
            "false_positives",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_protection_config(self, value):
        """Validate protection config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Protection config must be a dictionary.")
        return value

    def validate_ai_detection_rules(self, value):
        """Validate AI detection rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("AI detection rules must be a list.")
        return value

    def validate_behavioral_analytics(self, value):
        """Validate behavioral analytics."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Behavioral analytics must be a dictionary."
            )
        return value

    def validate_threat_intelligence(self, value):
        """Validate threat intelligence."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Threat intelligence must be a dictionary."
            )
        return value

    def validate_incident_response(self, value):
        """Validate incident response."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Incident response must be a dictionary.")
        return value


class SecurityManagementSerializer(serializers.ModelSerializer):
    """Serializer for Security Management."""

    class Meta:
        model = SecurityManagement
        fields = [
            "id",
            "name",
            "management_type",
            "siem_config",
            "soar_config",
            "vulnerability_scanning",
            "security_policies",
            "incident_workflows",
            "total_incidents",
            "resolved_incidents",
            "average_resolution_time",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_siem_config(self, value):
        """Validate SIEM config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("SIEM config must be a dictionary.")
        return value

    def validate_soar_config(self, value):
        """Validate SOAR config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("SOAR config must be a dictionary.")
        return value

    def validate_vulnerability_scanning(self, value):
        """Validate vulnerability scanning."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Vulnerability scanning must be a dictionary."
            )
        return value

    def validate_security_policies(self, value):
        """Validate security policies."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Security policies must be a list.")
        return value

    def validate_incident_workflows(self, value):
        """Validate incident workflows."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Incident workflows must be a list.")
        return value


class AuthenticationAuthorizationSerializer(serializers.ModelSerializer):
    """Serializer for Authentication & Authorization."""

    class Meta:
        model = AuthenticationAuthorization
        fields = [
            "id",
            "name",
            "auth_type",
            "authentication_methods",
            "authorization_rules",
            "biometric_config",
            "pam_config",
            "zero_trust_config",
            "total_authentications",
            "successful_authentications",
            "failed_authentications",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_authentication_methods(self, value):
        """Validate authentication methods."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Authentication methods must be a list.")
        return value

    def validate_authorization_rules(self, value):
        """Validate authorization rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Authorization rules must be a list.")
        return value

    def validate_biometric_config(self, value):
        """Validate biometric config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Biometric config must be a dictionary.")
        return value

    def validate_pam_config(self, value):
        """Validate PAM config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("PAM config must be a dictionary.")
        return value

    def validate_zero_trust_config(self, value):
        """Validate zero trust config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Zero trust config must be a dictionary.")
        return value


class DataProtectionSerializer(serializers.ModelSerializer):
    """Serializer for Data Protection."""

    class Meta:
        model = DataProtection
        fields = [
            "id",
            "name",
            "protection_type",
            "dlp_config",
            "consent_management",
            "anonymization_rules",
            "encryption_settings",
            "data_classification",
            "total_data_protected",
            "data_breaches_prevented",
            "compliance_score",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_dlp_config(self, value):
        """Validate DLP config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("DLP config must be a dictionary.")
        return value

    def validate_consent_management(self, value):
        """Validate consent management."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Consent management must be a dictionary."
            )
        return value

    def validate_anonymization_rules(self, value):
        """Validate anonymization rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Anonymization rules must be a list.")
        return value

    def validate_encryption_settings(self, value):
        """Validate encryption settings."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Encryption settings must be a dictionary."
            )
        return value

    def validate_data_classification(self, value):
        """Validate data classification."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Data classification must be a dictionary."
            )
        return value


class ComplianceGovernanceSerializer(serializers.ModelSerializer):
    """Serializer for Compliance & Governance."""

    class Meta:
        model = ComplianceGovernance
        fields = [
            "id",
            "name",
            "compliance_type",
            "compliance_framework",
            "audit_trail_config",
            "regulatory_requirements",
            "compliance_monitoring",
            "reporting_automation",
            "total_audits",
            "compliance_score",
            "last_audit",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_compliance_framework(self, value):
        """Validate compliance framework."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Compliance framework must be a dictionary."
            )
        return value

    def validate_audit_trail_config(self, value):
        """Validate audit trail config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Audit trail config must be a dictionary."
            )
        return value

    def validate_regulatory_requirements(self, value):
        """Validate regulatory requirements."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Regulatory requirements must be a list.")
        return value

    def validate_compliance_monitoring(self, value):
        """Validate compliance monitoring."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Compliance monitoring must be a dictionary."
            )
        return value

    def validate_reporting_automation(self, value):
        """Validate reporting automation."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Reporting automation must be a dictionary."
            )
        return value


class SecurityIncidentSerializer(serializers.ModelSerializer):
    """Serializer for Security Incidents."""

    class Meta:
        model = SecurityIncident
        fields = [
            "id",
            "incident_id",
            "title",
            "description",
            "severity",
            "status",
            "threat_type",
            "affected_systems",
            "incident_data",
            "resolution_notes",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_affected_systems(self, value):
        """Validate affected systems."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Affected systems must be a list.")
        return value

    def validate_incident_data(self, value):
        """Validate incident data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Incident data must be a dictionary.")
        return value


class SecurityAuditSerializer(serializers.ModelSerializer):
    """Serializer for Security Audits."""

    class Meta:
        model = SecurityAudit
        fields = [
            "id",
            "audit_id",
            "audit_type",
            "audit_scope",
            "audit_findings",
            "compliance_requirements",
            "audit_results",
            "recommendations",
            "audit_score",
            "audit_date",
            "auditor",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_audit_scope(self, value):
        """Validate audit scope."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Audit scope must be a dictionary.")
        return value

    def validate_audit_findings(self, value):
        """Validate audit findings."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Audit findings must be a list.")
        return value

    def validate_compliance_requirements(self, value):
        """Validate compliance requirements."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Compliance requirements must be a list.")
        return value

    def validate_audit_results(self, value):
        """Validate audit results."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Audit results must be a dictionary.")
        return value

    def validate_recommendations(self, value):
        """Validate recommendations."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Recommendations must be a list.")
        return value


class SecurityPolicySerializer(serializers.ModelSerializer):
    """Serializer for Security Policies."""

    class Meta:
        model = SecurityPolicy
        fields = [
            "id",
            "name",
            "policy_type",
            "policy_content",
            "policy_rules",
            "enforcement_config",
            "compliance_requirements",
            "approval_workflow",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_policy_rules(self, value):
        """Validate policy rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Policy rules must be a list.")
        return value

    def validate_enforcement_config(self, value):
        """Validate enforcement config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Enforcement config must be a dictionary."
            )
        return value

    def validate_compliance_requirements(self, value):
        """Validate compliance requirements."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Compliance requirements must be a list.")
        return value

    def validate_approval_workflow(self, value):
        """Validate approval workflow."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Approval workflow must be a dictionary.")
        return value


class SecurityMetricSerializer(serializers.ModelSerializer):
    """Serializer for Security Metrics."""

    class Meta:
        model = SecurityMetric
        fields = [
            "id",
            "metric_name",
            "metric_type",
            "metric_value",
            "metric_unit",
            "target_value",
            "metric_data",
            "measurement_date",
        ]
        read_only_fields = ["id", "measurement_date"]

    def validate_metric_data(self, value):
        """Validate metric data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metric data must be a dictionary.")
        return value
