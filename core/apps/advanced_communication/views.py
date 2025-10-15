"""
Advanced Communication views.
"""

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    CommunicationChannel,
    VideoConference,
    CommunicationTemplate,
    CommunicationLog,
)
from .serializers import (
    CommunicationChannelSerializer,
    VideoConferenceSerializer,
    CommunicationTemplateSerializer,
    CommunicationLogSerializer,
)


class CommunicationChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for communication channel management."""

    queryset = CommunicationChannel.objects.all()
    serializer_class = CommunicationChannelSerializer


class VideoConferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for video conference management."""

    queryset = VideoConference.objects.all()
    serializer_class = VideoConferenceSerializer


class CommunicationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for communication template management."""

    queryset = CommunicationTemplate.objects.all()
    serializer_class = CommunicationTemplateSerializer


class CommunicationLogViewSet(viewsets.ModelViewSet):
    """ViewSet for communication log management."""

    queryset = CommunicationLog.objects.all()
    serializer_class = CommunicationLogSerializer


def advanced_communication_dashboard(request):
    """Advanced Communication Dashboard view."""
    context = {
        "total_channels": CommunicationChannel.objects.count(),
        "active_conferences": VideoConference.objects.filter(is_active=True).count(),
        "communication_templates": CommunicationTemplate.objects.count(),
        "communication_logs": CommunicationLog.objects.count(),
    }
    return render(request, "advanced_communication/dashboard.html", context)


def advanced_communication_analytics(request):
    """Advanced Communication Analytics view."""
    return render(request, "advanced_communication/analytics.html")
