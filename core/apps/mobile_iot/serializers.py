"""
Mobile & IoT Platform serializers.
"""

from rest_framework import serializers
from .models import MobileApp, IoTDevice, LocationTracking, OfflineSync


class MobileAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileApp
        fields = "__all__"


class IoTDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IoTDevice
        fields = "__all__"


class LocationTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationTracking
        fields = "__all__"


class OfflineSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflineSync
        fields = "__all__"
