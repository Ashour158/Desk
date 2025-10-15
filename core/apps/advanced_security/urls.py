"""
Advanced Security URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SecurityPolicyViewSet,
    AuditLogViewSet,
    ThreatDetectionViewSet,
    ComplianceReportViewSet,
    SecurityIncidentViewSet,
    advanced_security_dashboard,
    advanced_security_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"security-policies", SecurityPolicyViewSet)
router.register(r"audit-logs", AuditLogViewSet)
router.register(r"threat-detection", ThreatDetectionViewSet)
router.register(r"compliance-reports", ComplianceReportViewSet)
router.register(r"security-incidents", SecurityIncidentViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path("dashboard/", advanced_security_dashboard, name="advanced_security_dashboard"),
    path("analytics/", advanced_security_analytics, name="advanced_security_analytics"),
]
