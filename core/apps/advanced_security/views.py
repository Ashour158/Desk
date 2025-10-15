"""
Advanced Security views.
"""

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    SecurityPolicy,
    AuditLog,
    ThreatDetection,
    ComplianceReport,
    SecurityIncident,
)
from .serializers import (
    SecurityPolicySerializer,
    AuditLogSerializer,
    ThreatDetectionSerializer,
    ComplianceReportSerializer,
    SecurityIncidentSerializer,
)


class SecurityPolicyViewSet(viewsets.ModelViewSet):
    """ViewSet for security policy management."""

    queryset = SecurityPolicy.objects.all()
    serializer_class = SecurityPolicySerializer


class AuditLogViewSet(viewsets.ModelViewSet):
    """ViewSet for audit log management."""

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer


class ThreatDetectionViewSet(viewsets.ModelViewSet):
    """ViewSet for threat detection management."""

    queryset = ThreatDetection.objects.all()
    serializer_class = ThreatDetectionSerializer


class ComplianceReportViewSet(viewsets.ModelViewSet):
    """ViewSet for compliance report management."""

    queryset = ComplianceReport.objects.all()
    serializer_class = ComplianceReportSerializer


class SecurityIncidentViewSet(viewsets.ModelViewSet):
    """ViewSet for security incident management."""

    queryset = SecurityIncident.objects.all()
    serializer_class = SecurityIncidentSerializer


def advanced_security_dashboard(request):
    """Advanced Security Dashboard view."""
    context = {
        "total_policies": SecurityPolicy.objects.count(),
        "audit_logs": AuditLog.objects.count(),
        "threat_detections": ThreatDetection.objects.count(),
        "compliance_reports": ComplianceReport.objects.count(),
        "security_incidents": SecurityIncident.objects.count(),
    }
    return render(request, "advanced_security/dashboard.html", context)


def advanced_security_analytics(request):
    """Advanced Security Analytics view."""
    return render(request, "advanced_security/analytics.html")
