"""
Advanced Security serializers.
"""

from rest_framework import serializers
from .models import (
    SecurityPolicy,
    AuditLog,
    ThreatDetection,
    ComplianceReport,
    SecurityIncident,
)


class SecurityPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityPolicy
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"


class ThreatDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatDetection
        fields = "__all__"


class ComplianceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceReport
        fields = "__all__"


class SecurityIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityIncident
        fields = "__all__"
