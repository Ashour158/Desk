"""
Mobile & IoT Platform views.
"""

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MobileApp, IoTDevice, LocationTracking, OfflineSync
from .serializers import (
    MobileAppSerializer,
    IoTDeviceSerializer,
    LocationTrackingSerializer,
    OfflineSyncSerializer,
)


class MobileAppViewSet(viewsets.ModelViewSet):
    """ViewSet for mobile app management."""

    queryset = MobileApp.objects.all()
    serializer_class = MobileAppSerializer


class IoTDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for IoT device management."""

    queryset = IoTDevice.objects.all()
    serializer_class = IoTDeviceSerializer


class LocationTrackingViewSet(viewsets.ModelViewSet):
    """ViewSet for location tracking management."""

    queryset = LocationTracking.objects.all()
    serializer_class = LocationTrackingSerializer


class OfflineSyncViewSet(viewsets.ModelViewSet):
    """ViewSet for offline sync management."""

    queryset = OfflineSync.objects.all()
    serializer_class = OfflineSyncSerializer


def mobile_iot_dashboard(request):
    """Mobile & IoT Dashboard view."""
    context = {
        "total_mobile_apps": MobileApp.objects.count(),
        "active_iot_devices": IoTDevice.objects.filter(is_active=True).count(),
        "location_trackings": LocationTracking.objects.count(),
        "offline_syncs": OfflineSync.objects.count(),
    }
    return render(request, "mobile_iot/dashboard.html", context)


def mobile_iot_analytics(request):
    """Mobile & IoT Analytics view."""
    return render(request, "mobile_iot/analytics.html")
