"""
Enhanced Advanced Analytics & Business Intelligence URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    DataSciencePlatformViewSet,
    RealTimeAnalyticsEngineViewSet,
    AdvancedReportingSuiteViewSet,
    BusinessIntelligenceToolsViewSet,
    DataGovernanceViewSet,
    AnalyticsModelViewSet,
    AnalyticsDashboardViewSet,
    AnalyticsReportViewSet,
    AnalyticsAlertViewSet,
)

# Create router for enhanced Advanced Analytics endpoints
router = DefaultRouter()
router.register(r"data-science-platforms", DataSciencePlatformViewSet)
router.register(r"real-time-analytics", RealTimeAnalyticsEngineViewSet)
router.register(r"reporting-suites", AdvancedReportingSuiteViewSet)
router.register(r"bi-tools", BusinessIntelligenceToolsViewSet)
router.register(r"data-governance", DataGovernanceViewSet)
router.register(r"analytics-models", AnalyticsModelViewSet)
router.register(r"analytics-dashboards", AnalyticsDashboardViewSet)
router.register(r"analytics-reports", AnalyticsReportViewSet)
router.register(r"analytics-alerts", AnalyticsAlertViewSet)

urlpatterns = [
    path("enhanced/", include(router.urls)),
]
