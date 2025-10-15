"""
API URL configuration for the helpdesk platform.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    APIServiceViewSet,
    WebhookViewSet,
    IntegrationLogViewSet,
    realtime_webhook,
    microservice_status,
    api_documentation,
    system_status,
    feature_status,
    feature_connections,
    realtime_capabilities,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"services", APIServiceViewSet)
router.register(r"webhooks", WebhookViewSet)
router.register(r"integration-logs", IntegrationLogViewSet)

urlpatterns = [
    # API Router
    path("", include(router.urls)),
    # Health Check
    path("health/", microservice_status, name="health_check"),
    # Real-time Webhooks
    path("realtime/webhook/", realtime_webhook, name="realtime_webhook"),
    # API Documentation
    path("docs/", api_documentation, name="api_documentation"),
    # Microservice Status
    path("status/", microservice_status, name="microservice_status"),
    # System Status
    path("system/status/", system_status, name="system_status"),
    path("features/status/", feature_status, name="feature_status"),
    path("features/connections/", feature_connections, name="feature_connections"),
    path("realtime/capabilities/", realtime_capabilities, name="realtime_capabilities"),
]
