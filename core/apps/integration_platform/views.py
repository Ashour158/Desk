"""
Integration Platform views.
"""

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Webhook,
    APIIntegration,
    ThirdPartyService,
    IntegrationLog,
    Connector,
)
from .serializers import (
    WebhookSerializer,
    APIIntegrationSerializer,
    ThirdPartyServiceSerializer,
    IntegrationLogSerializer,
    ConnectorSerializer,
)


class WebhookViewSet(viewsets.ModelViewSet):
    """ViewSet for webhook management."""

    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer


class APIIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for API integration management."""

    queryset = APIIntegration.objects.all()
    serializer_class = APIIntegrationSerializer


class ThirdPartyServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for third-party service management."""

    queryset = ThirdPartyService.objects.all()
    serializer_class = ThirdPartyServiceSerializer


class IntegrationLogViewSet(viewsets.ModelViewSet):
    """ViewSet for integration log management."""

    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer


class ConnectorViewSet(viewsets.ModelViewSet):
    """ViewSet for connector management."""

    queryset = Connector.objects.all()
    serializer_class = ConnectorSerializer


def integration_platform_dashboard(request):
    """Integration Platform Dashboard view."""
    context = {
        "total_webhooks": Webhook.objects.count(),
        "active_integrations": APIIntegration.objects.filter(is_active=True).count(),
        "third_party_services": ThirdPartyService.objects.count(),
        "integration_logs": IntegrationLog.objects.count(),
    }
    return render(request, "integration_platform/dashboard.html", context)


def integration_platform_analytics(request):
    """Integration Platform Analytics view."""
    return render(request, "integration_platform/analytics.html")
