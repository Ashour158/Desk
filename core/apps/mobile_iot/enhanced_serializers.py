"""
Enhanced Mobile & IoT Platform serializers for advanced capabilities.
"""

from rest_framework import serializers
from .enhanced_models import (
    MobilePlatform,
    IoTDevice,
    ARVRSupport,
    WearableIntegration,
    LocationService,
    MobileApp,
    IoTDataPoint,
    LocationData,
    WearableData,
    ARVRSession,
)


class MobilePlatformSerializer(serializers.ModelSerializer):
    """Serializer for Mobile Platform."""

    class Meta:
        model = MobilePlatform
        fields = [
            "id",
            "name",
            "platform_type",
            "app_configuration",
            "offline_capabilities",
            "push_notifications",
            "user_authentication",
            "data_synchronization",
            "total_users",
            "active_users",
            "app_downloads",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_app_configuration(self, value):
        """Validate app configuration."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("App configuration must be a dictionary.")
        return value

    def validate_offline_capabilities(self, value):
        """Validate offline capabilities."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Offline capabilities must be a dictionary."
            )
        return value

    def validate_push_notifications(self, value):
        """Validate push notifications."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Push notifications must be a dictionary."
            )
        return value

    def validate_user_authentication(self, value):
        """Validate user authentication."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "User authentication must be a dictionary."
            )
        return value

    def validate_data_synchronization(self, value):
        """Validate data synchronization."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Data synchronization must be a dictionary."
            )
        return value


class IoTDeviceSerializer(serializers.ModelSerializer):
    """Serializer for IoT Devices."""

    class Meta:
        model = IoTDevice
        fields = [
            "id",
            "name",
            "device_type",
            "device_id",
            "device_configuration",
            "connectivity_protocols",
            "data_schema",
            "edge_analytics_config",
            "security_settings",
            "total_data_points",
            "last_data_received",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_device_configuration(self, value):
        """Validate device configuration."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Device configuration must be a dictionary."
            )
        return value

    def validate_connectivity_protocols(self, value):
        """Validate connectivity protocols."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Connectivity protocols must be a list.")
        return value

    def validate_data_schema(self, value):
        """Validate data schema."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data schema must be a dictionary.")
        return value

    def validate_edge_analytics_config(self, value):
        """Validate edge analytics config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Edge analytics config must be a dictionary."
            )
        return value

    def validate_security_settings(self, value):
        """Validate security settings."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Security settings must be a dictionary.")
        return value


class ARVRSupportSerializer(serializers.ModelSerializer):
    """Serializer for AR/VR Support."""

    class Meta:
        model = ARVRSupport
        fields = [
            "id",
            "name",
            "arvr_type",
            "arvr_configuration",
            "remote_assistance_config",
            "vr_training_config",
            "device_requirements",
            "content_management",
            "total_sessions",
            "active_sessions",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_arvr_configuration(self, value):
        """Validate AR/VR configuration."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "AR/VR configuration must be a dictionary."
            )
        return value

    def validate_remote_assistance_config(self, value):
        """Validate remote assistance config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Remote assistance config must be a dictionary."
            )
        return value

    def validate_vr_training_config(self, value):
        """Validate VR training config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "VR training config must be a dictionary."
            )
        return value

    def validate_device_requirements(self, value):
        """Validate device requirements."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Device requirements must be a dictionary."
            )
        return value

    def validate_content_management(self, value):
        """Validate content management."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Content management must be a dictionary."
            )
        return value


class WearableIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Wearable Integration."""

    class Meta:
        model = WearableIntegration
        fields = [
            "id",
            "name",
            "wearable_type",
            "wearable_configuration",
            "biometric_authentication",
            "health_monitoring",
            "notification_settings",
            "data_collection",
            "total_wearables",
            "active_wearables",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_wearable_configuration(self, value):
        """Validate wearable configuration."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Wearable configuration must be a dictionary."
            )
        return value

    def validate_biometric_authentication(self, value):
        """Validate biometric authentication."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Biometric authentication must be a dictionary."
            )
        return value

    def validate_health_monitoring(self, value):
        """Validate health monitoring."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Health monitoring must be a dictionary.")
        return value

    def validate_notification_settings(self, value):
        """Validate notification settings."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Notification settings must be a dictionary."
            )
        return value

    def validate_data_collection(self, value):
        """Validate data collection."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data collection must be a dictionary.")
        return value


class LocationServiceSerializer(serializers.ModelSerializer):
    """Serializer for Location Services."""

    class Meta:
        model = LocationService
        fields = [
            "id",
            "name",
            "service_type",
            "location_configuration",
            "gps_settings",
            "geofencing_rules",
            "location_analytics",
            "privacy_settings",
            "total_locations",
            "active_tracking",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_location_configuration(self, value):
        """Validate location configuration."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Location configuration must be a dictionary."
            )
        return value

    def validate_gps_settings(self, value):
        """Validate GPS settings."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("GPS settings must be a dictionary.")
        return value

    def validate_geofencing_rules(self, value):
        """Validate geofencing rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Geofencing rules must be a list.")
        return value

    def validate_location_analytics(self, value):
        """Validate location analytics."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Location analytics must be a dictionary."
            )
        return value

    def validate_privacy_settings(self, value):
        """Validate privacy settings."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Privacy settings must be a dictionary.")
        return value


class MobileAppSerializer(serializers.ModelSerializer):
    """Serializer for Mobile Apps."""

    class Meta:
        model = MobileApp
        fields = [
            "id",
            "name",
            "app_type",
            "app_configuration",
            "features",
            "user_interface",
            "performance_metrics",
            "total_downloads",
            "active_users",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_app_configuration(self, value):
        """Validate app configuration."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("App configuration must be a dictionary.")
        return value

    def validate_features(self, value):
        """Validate features."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Features must be a list.")
        return value

    def validate_user_interface(self, value):
        """Validate user interface."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("User interface must be a dictionary.")
        return value

    def validate_performance_metrics(self, value):
        """Validate performance metrics."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Performance metrics must be a dictionary."
            )
        return value


class IoTDataPointSerializer(serializers.ModelSerializer):
    """Serializer for IoT Data Points."""

    class Meta:
        model = IoTDataPoint
        fields = ["id", "device", "data_type", "value", "unit", "timestamp", "metadata"]
        read_only_fields = ["id", "timestamp"]

    def validate_metadata(self, value):
        """Validate metadata."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a dictionary.")
        return value


class LocationDataSerializer(serializers.ModelSerializer):
    """Serializer for Location Data."""

    class Meta:
        model = LocationData
        fields = [
            "id",
            "service",
            "latitude",
            "longitude",
            "altitude",
            "accuracy",
            "timestamp",
            "metadata",
        ]
        read_only_fields = ["id", "timestamp"]

    def validate_metadata(self, value):
        """Validate metadata."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a dictionary.")
        return value


class WearableDataSerializer(serializers.ModelSerializer):
    """Serializer for Wearable Data."""

    class Meta:
        model = WearableData
        fields = [
            "id",
            "wearable",
            "data_type",
            "value",
            "unit",
            "timestamp",
            "metadata",
        ]
        read_only_fields = ["id", "timestamp"]

    def validate_metadata(self, value):
        """Validate metadata."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a dictionary.")
        return value


class ARVRSessionSerializer(serializers.ModelSerializer):
    """Serializer for AR/VR Sessions."""

    class Meta:
        model = ARVRSession
        fields = [
            "id",
            "arvr_support",
            "session_type",
            "session_data",
            "duration",
            "is_active",
            "created_at",
            "ended_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_session_data(self, value):
        """Validate session data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Session data must be a dictionary.")
        return value
