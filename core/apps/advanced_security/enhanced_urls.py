"""
Enhanced Advanced Security & Compliance Suite URLs for advanced capabilities.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    ThreatProtectionViewSet,
    SecurityManagementViewSet,
    AuthenticationAuthorizationViewSet,
    DataProtectionViewSet,
    ComplianceGovernanceViewSet,
    SecurityIncidentViewSet,
    SecurityAuditViewSet,
    SecurityPolicyViewSet,
    SecurityMetricViewSet,
    advanced_security_dashboard,
    advanced_security_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"threat-protections", ThreatProtectionViewSet)
router.register(r"security-managements", SecurityManagementViewSet)
router.register(r"authentication-authorizations", AuthenticationAuthorizationViewSet)
router.register(r"data-protections", DataProtectionViewSet)
router.register(r"compliance-governances", ComplianceGovernanceViewSet)
router.register(r"security-incidents", SecurityIncidentViewSet)
router.register(r"security-audits", SecurityAuditViewSet)
router.register(r"security-policies", SecurityPolicyViewSet)
router.register(r"security-metrics", SecurityMetricViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path("dashboard/", advanced_security_dashboard, name="advanced_security_dashboard"),
    path("analytics/", advanced_security_analytics, name="advanced_security_analytics"),
]
