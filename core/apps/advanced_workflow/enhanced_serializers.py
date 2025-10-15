"""
Enhanced Advanced Workflow & Automation Platform serializers for advanced capabilities.
"""

from rest_framework import serializers
from .enhanced_models import (
    IntelligentProcessAutomation,
    WorkflowEngine,
    ProcessIntelligence,
    AutomationMarketplace,
    IntegrationAutomation,
    WorkflowTemplate,
    WorkflowExecution,
    ProcessMetric,
    AutomationRule,
)


class IntelligentProcessAutomationSerializer(serializers.ModelSerializer):
    """Serializer for Intelligent Process Automation."""

    class Meta:
        model = IntelligentProcessAutomation
        fields = [
            "id",
            "name",
            "ipa_type",
            "process_definition",
            "ai_models",
            "self_healing_config",
            "process_discovery_rules",
            "intelligent_routing",
            "total_processes",
            "automated_processes",
            "self_healing_events",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_process_definition(self, value):
        """Validate process definition."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Process definition must be a dictionary."
            )
        return value

    def validate_ai_models(self, value):
        """Validate AI models."""
        if not isinstance(value, list):
            raise serializers.ValidationError("AI models must be a list.")
        return value

    def validate_self_healing_config(self, value):
        """Validate self-healing config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Self-healing config must be a dictionary."
            )
        return value

    def validate_process_discovery_rules(self, value):
        """Validate process discovery rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Process discovery rules must be a list.")
        return value

    def validate_intelligent_routing(self, value):
        """Validate intelligent routing."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Intelligent routing must be a dictionary."
            )
        return value


class WorkflowEngineSerializer(serializers.ModelSerializer):
    """Serializer for Workflow Engine."""

    class Meta:
        model = WorkflowEngine
        fields = [
            "id",
            "name",
            "engine_type",
            "workflow_definition",
            "execution_engine",
            "parallel_processing",
            "conditional_logic",
            "event_handlers",
            "total_workflows",
            "active_workflows",
            "total_executions",
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

    def validate_execution_engine(self, value):
        """Validate execution engine."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Execution engine must be a dictionary.")
        return value

    def validate_parallel_processing(self, value):
        """Validate parallel processing."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Parallel processing must be a dictionary."
            )
        return value

    def validate_conditional_logic(self, value):
        """Validate conditional logic."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Conditional logic must be a dictionary.")
        return value

    def validate_event_handlers(self, value):
        """Validate event handlers."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Event handlers must be a list.")
        return value


class ProcessIntelligenceSerializer(serializers.ModelSerializer):
    """Serializer for Process Intelligence."""

    class Meta:
        model = ProcessIntelligence
        fields = [
            "id",
            "name",
            "intelligence_type",
            "process_mining_config",
            "performance_analytics",
            "optimization_rules",
            "bottleneck_detection",
            "resource_optimization",
            "total_processes_analyzed",
            "optimization_recommendations",
            "performance_improvements",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_process_mining_config(self, value):
        """Validate process mining config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Process mining config must be a dictionary."
            )
        return value

    def validate_performance_analytics(self, value):
        """Validate performance analytics."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Performance analytics must be a dictionary."
            )
        return value

    def validate_optimization_rules(self, value):
        """Validate optimization rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Optimization rules must be a list.")
        return value

    def validate_bottleneck_detection(self, value):
        """Validate bottleneck detection."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Bottleneck detection must be a dictionary."
            )
        return value

    def validate_resource_optimization(self, value):
        """Validate resource optimization."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Resource optimization must be a dictionary."
            )
        return value


class AutomationMarketplaceSerializer(serializers.ModelSerializer):
    """Serializer for Automation Marketplace."""

    class Meta:
        model = AutomationMarketplace
        fields = [
            "id",
            "name",
            "marketplace_type",
            "automation_templates",
            "community_library",
            "enterprise_automations",
            "custom_automations",
            "ai_automations",
            "total_templates",
            "downloads",
            "community_contributions",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_automation_templates(self, value):
        """Validate automation templates."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Automation templates must be a list.")
        return value

    def validate_community_library(self, value):
        """Validate community library."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Community library must be a dictionary.")
        return value

    def validate_enterprise_automations(self, value):
        """Validate enterprise automations."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Enterprise automations must be a list.")
        return value

    def validate_custom_automations(self, value):
        """Validate custom automations."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Custom automations must be a list.")
        return value

    def validate_ai_automations(self, value):
        """Validate AI automations."""
        if not isinstance(value, list):
            raise serializers.ValidationError("AI automations must be a list.")
        return value


class IntegrationAutomationSerializer(serializers.ModelSerializer):
    """Serializer for Integration Automation."""

    class Meta:
        model = IntegrationAutomation
        fields = [
            "id",
            "name",
            "automation_type",
            "integration_config",
            "event_driven_config",
            "api_automation",
            "data_automation",
            "workflow_automation",
            "total_integrations",
            "automated_integrations",
            "cross_system_automations",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_integration_config(self, value):
        """Validate integration config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Integration config must be a dictionary."
            )
        return value

    def validate_event_driven_config(self, value):
        """Validate event-driven config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Event-driven config must be a dictionary."
            )
        return value

    def validate_api_automation(self, value):
        """Validate API automation."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("API automation must be a dictionary.")
        return value

    def validate_data_automation(self, value):
        """Validate data automation."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data automation must be a dictionary.")
        return value

    def validate_workflow_automation(self, value):
        """Validate workflow automation."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Workflow automation must be a dictionary."
            )
        return value


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """Serializer for Workflow Templates."""

    class Meta:
        model = WorkflowTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "template_definition",
            "template_config",
            "required_fields",
            "optional_fields",
            "template_category",
            "template_description",
            "total_uses",
            "is_public",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_template_definition(self, value):
        """Validate template definition."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Template definition must be a dictionary."
            )
        return value

    def validate_template_config(self, value):
        """Validate template config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Template config must be a dictionary.")
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


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """Serializer for Workflow Executions."""

    class Meta:
        model = WorkflowExecution
        fields = [
            "id",
            "workflow_engine",
            "execution_id",
            "workflow_name",
            "status",
            "execution_data",
            "execution_log",
            "start_time",
            "end_time",
            "duration",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_execution_data(self, value):
        """Validate execution data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Execution data must be a dictionary.")
        return value

    def validate_execution_log(self, value):
        """Validate execution log."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Execution log must be a list.")
        return value


class ProcessMetricSerializer(serializers.ModelSerializer):
    """Serializer for Process Metrics."""

    class Meta:
        model = ProcessMetric
        fields = [
            "id",
            "metric_name",
            "metric_type",
            "metric_value",
            "metric_unit",
            "target_value",
            "metric_data",
            "measurement_date",
        ]
        read_only_fields = ["id", "measurement_date"]

    def validate_metric_data(self, value):
        """Validate metric data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metric data must be a dictionary.")
        return value


class AutomationRuleSerializer(serializers.ModelSerializer):
    """Serializer for Automation Rules."""

    class Meta:
        model = AutomationRule
        fields = [
            "id",
            "name",
            "rule_type",
            "rule_definition",
            "trigger_conditions",
            "action_sequences",
            "exception_handling",
            "escalation_rules",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_rule_definition(self, value):
        """Validate rule definition."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Rule definition must be a dictionary.")
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

    def validate_exception_handling(self, value):
        """Validate exception handling."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Exception handling must be a dictionary."
            )
        return value

    def validate_escalation_rules(self, value):
        """Validate escalation rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Escalation rules must be a list.")
        return value
