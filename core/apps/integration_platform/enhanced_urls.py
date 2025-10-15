"""
Enhanced Integration & API Platform URLs for advanced capabilities.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    EnterpriseIntegrationHubViewSet,
    APIManagementViewSet,
    WorkflowAutomationViewSet,
    DataIntegrationViewSet,
    IntegrationMarketplaceViewSet,
    IntegrationConnectorViewSet,
    IntegrationTemplateViewSet,
    IntegrationLogViewSet,
    IntegrationMetricViewSet,
    integration_dashboard,
    integration_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"integration-hubs", EnterpriseIntegrationHubViewSet)
router.register(r"api-management", APIManagementViewSet)
router.register(r"workflow-automation", WorkflowAutomationViewSet)
router.register(r"data-integration", DataIntegrationViewSet)
router.register(r"integration-marketplace", IntegrationMarketplaceViewSet)
router.register(r"integration-connectors", IntegrationConnectorViewSet)
router.register(r"integration-templates", IntegrationTemplateViewSet)
router.register(r"integration-logs", IntegrationLogViewSet)
router.register(r"integration-metrics", IntegrationMetricViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path("dashboard/", integration_dashboard, name="integration_dashboard"),
    path("analytics/", integration_analytics, name="integration_analytics"),
]
