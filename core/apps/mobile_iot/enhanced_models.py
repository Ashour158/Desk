"""
Enhanced Mobile & IoT Platform models for advanced capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization
from apps.common.base_models import BaseModel, ConfigurationModel, MetricsModel, DataPointModel, LocationModel
from apps.common.constants import (
    DEVICE_TYPE_CHOICES,
    PLATFORM_TYPE_CHOICES,
    ARVR_TYPE_CHOICES,
    WEARABLE_TYPE_CHOICES,
    LOCATION_SERVICE_TYPE_CHOICES,
    MOBILE_APP_TYPE_CHOICES,
)

User = get_user_model()


class MobilePlatform(models.Model):
    """Advanced Mobile Platform with cross-platform apps and offline-first architecture."""

    PLATFORM_CHOICES = [
        ("ios", "iOS"),
        ("android", "Android"),
        ("cross_platform", "Cross Platform"),
        ("progressive_web_app", "Progressive Web App"),
        ("hybrid", "Hybrid"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    platform_type = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    app_configuration = models.JSONField(default=dict)
    offline_capabilities = models.JSONField(default=dict)
    push_notifications = models.JSONField(default=dict)
    user_authentication = models.JSONField(default=dict)
    data_synchronization = models.JSONField(default=dict)
    total_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    app_downloads = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mobile Platform"
        verbose_name_plural = "Mobile Platforms"

    def __str__(self):
        return self.name


class IoTDevice(models.Model):
    """IoT Device Integration with device management and edge analytics."""

    DEVICE_TYPE_CHOICES = [
        ("sensor", "Sensor"),
        ("actuator", "Actuator"),
        ("gateway", "Gateway"),
        ("edge_device", "Edge Device"),
        ("smart_device", "Smart Device"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES)
    device_id = models.CharField(max_length=100, unique=True)
    device_configuration = models.JSONField(default=dict)
    connectivity_protocols = models.JSONField(default=list)
    data_schema = models.JSONField(default=dict)
    edge_analytics_config = models.JSONField(default=dict)
    security_settings = models.JSONField(default=dict)
    total_data_points = models.PositiveIntegerField(default=0)
    last_data_received = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "IoT Device"
        verbose_name_plural = "IoT Devices"

    def __str__(self):
        return self.name


class ARVRSupport(models.Model):
    """AR/VR Support with remote assistance and VR training simulations."""

    ARVR_TYPE_CHOICES = [
        ("augmented_reality", "Augmented Reality"),
        ("virtual_reality", "Virtual Reality"),
        ("mixed_reality", "Mixed Reality"),
        ("remote_assistance", "Remote Assistance"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    arvr_type = models.CharField(max_length=50, choices=ARVR_TYPE_CHOICES)
    arvr_configuration = models.JSONField(default=dict)
    remote_assistance_config = models.JSONField(default=dict)
    vr_training_config = models.JSONField(default=dict)
    device_requirements = models.JSONField(default=dict)
    content_management = models.JSONField(default=dict)
    total_sessions = models.PositiveIntegerField(default=0)
    active_sessions = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AR/VR Support"
        verbose_name_plural = "AR/VR Supports"

    def __str__(self):
        return self.name


class WearableIntegration(models.Model):
    """Wearable Technology Integration with smartwatch apps and biometric authentication."""

    WEARABLE_TYPE_CHOICES = [
        ("smartwatch", "Smartwatch"),
        ("fitness_tracker", "Fitness Tracker"),
        ("smart_glasses", "Smart Glasses"),
        ("smart_ring", "Smart Ring"),
        ("smart_clothing", "Smart Clothing"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    wearable_type = models.CharField(max_length=50, choices=WEARABLE_TYPE_CHOICES)
    wearable_configuration = models.JSONField(default=dict)
    biometric_authentication = models.JSONField(default=dict)
    health_monitoring = models.JSONField(default=dict)
    notification_settings = models.JSONField(default=dict)
    data_collection = models.JSONField(default=dict)
    total_wearables = models.PositiveIntegerField(default=0)
    active_wearables = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wearable Integration"
        verbose_name_plural = "Wearable Integrations"

    def __str__(self):
        return self.name


class LocationService(models.Model):
    """Location-based Services with GPS tracking, geofencing, and location intelligence."""

    SERVICE_TYPE_CHOICES = [
        ("gps_tracking", "GPS Tracking"),
        ("geofencing", "Geofencing"),
        ("location_intelligence", "Location Intelligence"),
        ("route_optimization", "Route Optimization"),
        ("asset_tracking", "Asset Tracking"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    location_configuration = models.JSONField(default=dict)
    gps_settings = models.JSONField(default=dict)
    geofencing_rules = models.JSONField(default=list)
    location_analytics = models.JSONField(default=dict)
    privacy_settings = models.JSONField(default=dict)
    total_locations = models.PositiveIntegerField(default=0)
    active_tracking = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Location Service"
        verbose_name_plural = "Location Services"

    def __str__(self):
        return self.name


class MobileApp(models.Model):
    """Mobile Application with cross-platform support and offline capabilities."""

    APP_TYPE_CHOICES = [
        ("native", "Native"),
        ("hybrid", "Hybrid"),
        ("progressive_web_app", "Progressive Web App"),
        ("cross_platform", "Cross Platform"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    app_type = models.CharField(max_length=50, choices=APP_TYPE_CHOICES)
    app_configuration = models.JSONField(default=dict)
    features = models.JSONField(default=list)
    user_interface = models.JSONField(default=dict)
    performance_metrics = models.JSONField(default=dict)
    total_downloads = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mobile App"
        verbose_name_plural = "Mobile Apps"

    def __str__(self):
        return self.name


class IoTDataPoint(models.Model):
    """IoT Data Point for storing sensor data and analytics."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        verbose_name = "IoT Data Point"
        verbose_name_plural = "IoT Data Points"

    def __str__(self):
        return f"{self.device.name} - {self.data_type}: {self.value} {self.unit}"


class LocationData(models.Model):
    """Location Data for GPS tracking and geofencing."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    service = models.ForeignKey(LocationService, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Location Data"
        verbose_name_plural = "Location Data"

    def __str__(self):
        return f"Location: {self.latitude}, {self.longitude}"


class WearableData(models.Model):
    """Wearable Data for health monitoring and biometric authentication."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    wearable = models.ForeignKey(WearableIntegration, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Wearable Data"
        verbose_name_plural = "Wearable Data"

    def __str__(self):
        return f"{self.wearable.name} - {self.data_type}: {self.value} {self.unit}"


class ARVRSession(models.Model):
    """AR/VR Session for remote assistance and training."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    arvr_support = models.ForeignKey(ARVRSupport, on_delete=models.CASCADE)
    session_type = models.CharField(max_length=100)
    session_data = models.JSONField(default=dict)
    duration = models.DurationField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "AR/VR Session"
        verbose_name_plural = "AR/VR Sessions"

    def __str__(self):
        return f"{self.arvr_support.name} - {self.session_type}"
