"""
Feature Flag Serializers
"""

from rest_framework import serializers
from .models import (
    Feature, FeatureCategory, FeaturePermission, FeatureConnection,
    FeatureUsage, FeatureHealth, FeatureConfiguration
)


class FeatureCategorySerializer(serializers.ModelSerializer):
    """Serializer for FeatureCategory model"""
    
    class Meta:
        model = FeatureCategory
        fields = [
            'id', 'name', 'description', 'icon', 'color', 'order', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeaturePermissionSerializer(serializers.ModelSerializer):
    """Serializer for FeaturePermission model"""
    
    class Meta:
        model = FeaturePermission
        fields = [
            'id', 'permission_name', 'description', 'is_required', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FeatureConnectionSerializer(serializers.ModelSerializer):
    """Serializer for FeatureConnection model"""
    
    source_feature_name = serializers.CharField(source='source_feature.name', read_only=True)
    target_feature_name = serializers.CharField(source='target_feature.name', read_only=True)
    
    class Meta:
        model = FeatureConnection
        fields = [
            'id', 'source_feature', 'target_feature', 'source_feature_name',
            'target_feature_name', 'connection_type', 'description', 'is_active',
            'configuration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FeatureUsageSerializer(serializers.ModelSerializer):
    """Serializer for FeatureUsage model"""
    
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = FeatureUsage
        fields = [
            'id', 'feature', 'user', 'organization', 'feature_name',
            'user_username', 'organization_name', 'access_count', 'last_accessed',
            'session_duration', 'response_time', 'error_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FeatureHealthSerializer(serializers.ModelSerializer):
    """Serializer for FeatureHealth model"""
    
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    
    class Meta:
        model = FeatureHealth
        fields = [
            'id', 'feature', 'feature_name', 'status', 'response_time',
            'error_rate', 'last_check', 'error_message', 'metadata'
        ]
        read_only_fields = ['id']


class FeatureConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for FeatureConfiguration model"""
    
    feature_name = serializers.CharField(source='feature.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = FeatureConfiguration
        fields = [
            'id', 'feature', 'organization', 'feature_name', 'organization_name',
            'config_key', 'config_value', 'config_type', 'is_encrypted',
            'is_required', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeatureSerializer(serializers.ModelSerializer):
    """Serializer for Feature model"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    permissions = FeaturePermissionSerializer(many=True, read_only=True)
    outgoing_connections = FeatureConnectionSerializer(many=True, read_only=True)
    incoming_connections = FeatureConnectionSerializer(many=True, read_only=True)
    usage_stats = FeatureUsageSerializer(many=True, read_only=True)
    health_checks = FeatureHealthSerializer(many=True, read_only=True)
    configurations = FeatureConfigurationSerializer(many=True, read_only=True)
    
    # Computed fields
    is_available = serializers.ReadOnlyField()
    full_endpoint = serializers.ReadOnlyField()
    
    class Meta:
        model = Feature
        fields = [
            'id', 'name', 'description', 'feature_type', 'category', 'category_name',
            'status', 'endpoint', 'api_version', 'requires_auth', 'requires_permission',
            'supports_realtime', 'websocket_channel', 'microservice', 'external_service',
            'icon', 'color', 'order', 'version', 'last_updated', 'created_at',
            'organization', 'organization_name', 'is_global', 'is_available',
            'full_endpoint', 'permissions', 'outgoing_connections', 'incoming_connections',
            'usage_stats', 'health_checks', 'configurations'
        ]
        read_only_fields = ['id', 'created_at', 'last_updated']


class FeatureFlagSerializer(serializers.Serializer):
    """Serializer for feature flag data"""
    
    flag_name = serializers.CharField(max_length=100)
    enabled = serializers.BooleanField()
    value = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    environment = serializers.CharField(required=False, allow_blank=True)
    timestamp = serializers.DateTimeField(required=False)


class FeatureFlagUpdateSerializer(serializers.Serializer):
    """Serializer for updating feature flags"""
    
    value = serializers.BooleanField()
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)


class FeatureFlagToggleSerializer(serializers.Serializer):
    """Serializer for toggling feature flags"""
    
    flag_name = serializers.CharField(max_length=100)
    enabled = serializers.BooleanField()
    previous_state = serializers.BooleanField()
    toggled = serializers.BooleanField()
    timestamp = serializers.DateTimeField()


class FeatureUsageStatsSerializer(serializers.Serializer):
    """Serializer for feature usage statistics"""
    
    feature_name = serializers.CharField()
    total_access = serializers.IntegerField()
    unique_users = serializers.IntegerField()
    last_accessed = serializers.DateTimeField(allow_null=True)
    average_response_time = serializers.FloatField(allow_null=True)
    error_rate = serializers.FloatField()


class FeatureHealthStatsSerializer(serializers.Serializer):
    """Serializer for feature health data"""
    
    feature_name = serializers.CharField()
    status = serializers.CharField()
    response_time = serializers.FloatField(allow_null=True)
    error_rate = serializers.FloatField()
    last_check = serializers.DateTimeField()
    error_message = serializers.CharField(allow_null=True, allow_blank=True)


class FeatureConfigurationSerializer(serializers.Serializer):
    """Serializer for feature configuration data"""
    
    config_key = serializers.CharField()
    value = serializers.CharField()
    type = serializers.CharField()
    required = serializers.BooleanField()
    encrypted = serializers.BooleanField()


class FeatureFlagResponseSerializer(serializers.Serializer):
    """Serializer for feature flag API responses"""
    
    features = serializers.DictField()
    user_id = serializers.IntegerField()
    organization_id = serializers.IntegerField(allow_null=True)
    timestamp = serializers.DateTimeField()
    environment = serializers.CharField()


class FeatureFlagErrorSerializer(serializers.Serializer):
    """Serializer for feature flag error responses"""
    
    error = serializers.CharField()
    details = serializers.CharField(required=False, allow_blank=True)
    timestamp = serializers.DateTimeField()
