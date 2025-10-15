"""
Integration Platform URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WebhookViewSet,
    APIIntegrationViewSet,
    ThirdPartyServiceViewSet,
    IntegrationLogViewSet,
    ConnectorViewSet,
    integration_platform_dashboard,
    integration_platform_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"webhooks", WebhookViewSet)
router.register(r"api-integrations", APIIntegrationViewSet)
router.register(r"third-party-services", ThirdPartyServiceViewSet)
router.register(r"integration-logs", IntegrationLogViewSet)
router.register(r"connectors", ConnectorViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path(
        "dashboard/",
        integration_platform_dashboard,
        name="integration_platform_dashboard",
    ),
    path(
        "analytics/",
        integration_platform_analytics,
        name="integration_platform_analytics",
    ),
]
