"""
Enhanced Integration & API Platform serializers for advanced capabilities.
"""

from rest_framework import serializers
from .enhanced_models import (
    EnterpriseIntegrationHub,
    APIManagement,
    WorkflowAutomation,
    DataIntegration,
    IntegrationMarketplace,
    IntegrationConnector,
    IntegrationTemplate,
    IntegrationLog,
    IntegrationMetric,
)


class EnterpriseIntegrationHubSerializer(serializers.ModelSerializer):
    """Serializer for Enterprise Integration Hub."""

    class Meta:
        model = EnterpriseIntegrationHub
        fields = [
            "id",
            "name",
            "hub_type",
            "available_connectors",
            "active_connectors",
            "integration_rules",
            "data_mapping",
            "total_integrations",
            "data_processed",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_available_connectors(self, value):
        """Validate available connectors."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Available connectors must be a list.")
        return value

    def validate_active_connectors(self, value):
        """Validate active connectors."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Active connectors must be a list.")
        return value

    def validate_integration_rules(self, value):
        """Validate integration rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Integration rules must be a list.")
        return value

    def validate_data_mapping(self, value):
        """Validate data mapping."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data mapping must be a dictionary.")
        return value


class APIManagementSerializer(serializers.ModelSerializer):
    """Serializer for API Management."""

    class Meta:
        model = APIManagement
        fields = [
            "id",
            "name",
            "api_type",
            "base_url",
            "version",
            "authentication_methods",
            "rate_limits",
            "api_documentation",
            "total_requests",
            "successful_requests",
            "failed_requests",
            "average_response_time",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_authentication_methods(self, value):
        """Validate authentication methods."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Authentication methods must be a list.")
        return value

    def validate_rate_limits(self, value):
        """Validate rate limits."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Rate limits must be a dictionary.")
        return value

    def validate_api_documentation(self, value):
        """Validate API documentation."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("API documentation must be a dictionary.")
        return value


class WorkflowAutomationSerializer(serializers.ModelSerializer):
    """Serializer for Workflow Automation."""

    class Meta:
        model = WorkflowAutomation
        fields = [
            "id",
            "name",
            "workflow_type",
            "workflow_definition",
            "trigger_conditions",
            "action_sequences",
            "approval_rules",
            "total_executions",
            "successful_executions",
            "failed_executions",
            "last_execution",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_workflow_definition(self, value):
        """Validate workflow definition."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Workflow definition must be a dictionary."
            )
        return value

    def validate_trigger_conditions(self, value):
        """Validate trigger conditions."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Trigger conditions must be a list.")
        return value

    def validate_action_sequences(self, value):
        """Validate action sequences."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Action sequences must be a list.")
        return value

    def validate_approval_rules(self, value):
        """Validate approval rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Approval rules must be a list.")
        return value


class DataIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Data Integration."""

    class Meta:
        model = DataIntegration
        fields = [
            "id",
            "name",
            "integration_type",
            "source_systems",
            "target_systems",
            "data_mapping",
            "transformation_rules",
            "total_records_processed",
            "successful_syncs",
            "failed_syncs",
            "last_sync",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_source_systems(self, value):
        """Validate source systems."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Source systems must be a list.")
        return value

    def validate_target_systems(self, value):
        """Validate target systems."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Target systems must be a list.")
        return value

    def validate_data_mapping(self, value):
        """Validate data mapping."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data mapping must be a dictionary.")
        return value

    def validate_transformation_rules(self, value):
        """Validate transformation rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Transformation rules must be a list.")
        return value


class IntegrationMarketplaceSerializer(serializers.ModelSerializer):
    """Serializer for Integration Marketplace."""

    class Meta:
        model = IntegrationMarketplace
        fields = [
            "id",
            "name",
            "marketplace_type",
            "available_apps",
            "revenue_sharing_model",
            "pricing_tiers",
            "approval_process",
            "total_apps",
            "active_apps",
            "total_revenue",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_available_apps(self, value):
        """Validate available apps."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Available apps must be a list.")
        return value

    def validate_revenue_sharing_model(self, value):
        """Validate revenue sharing model."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Revenue sharing model must be a dictionary."
            )
        return value

    def validate_pricing_tiers(self, value):
        """Validate pricing tiers."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Pricing tiers must be a list.")
        return value

    def validate_approval_process(self, value):
        """Validate approval process."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Approval process must be a dictionary.")
        return value


class IntegrationConnectorSerializer(serializers.ModelSerializer):
    """Serializer for Integration Connectors."""

    class Meta:
        model = IntegrationConnector
        fields = [
            "id",
            "name",
            "connector_type",
            "category",
            "description",
            "configuration_schema",
            "authentication_methods",
            "supported_operations",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_configuration_schema(self, value):
        """Validate configuration schema."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Configuration schema must be a dictionary."
            )
        return value

    def validate_authentication_methods(self, value):
        """Validate authentication methods."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Authentication methods must be a list.")
        return value

    def validate_supported_operations(self, value):
        """Validate supported operations."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Supported operations must be a list.")
        return value


class IntegrationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for Integration Templates."""

    class Meta:
        model = IntegrationTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "category",
            "description",
            "template_configuration",
            "required_fields",
            "optional_fields",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_template_configuration(self, value):
        """Validate template configuration."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Template configuration must be a dictionary."
            )
        return value

    def validate_required_fields(self, value):
        """Validate required fields."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Required fields must be a list.")
        return value

    def validate_optional_fields(self, value):
        """Validate optional fields."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Optional fields must be a list.")
        return value


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer for Integration Logs."""

    class Meta:
        model = IntegrationLog
        fields = [
            "id",
            "log_type",
            "severity",
            "message",
            "connector_id",
            "integration_id",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_metadata(self, value):
        """Validate metadata."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a dictionary.")
        return value


class IntegrationMetricSerializer(serializers.ModelSerializer):
    """Serializer for Integration Metrics."""

    class Meta:
        model = IntegrationMetric
        fields = [
            "id",
            "metric_name",
            "metric_type",
            "value",
            "unit",
            "connector_id",
            "integration_id",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_metadata(self, value):
        """Validate metadata."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a dictionary.")
        return value
