"""
Enhanced Integration & API Platform models for advanced capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.organizations.models import Organization
import uuid

User = get_user_model()


class EnterpriseIntegrationHub(models.Model):
    """Enterprise integration hub with 500+ pre-built connectors and legacy system integration."""

    HUB_TYPES = [
        ("pre_built_connectors", "Pre-built Connectors"),
        ("legacy_system_integration", "Legacy System Integration"),
        ("cloud_integration", "Cloud Integration"),
        ("api_integration", "API Integration"),
        ("data_integration", "Data Integration"),
        ("workflow_integration", "Workflow Integration"),
        ("real_time_integration", "Real-time Integration"),
        ("batch_integration", "Batch Integration"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="integration_hubs"
    )
    name = models.CharField(max_length=255)
    hub_type = models.CharField(max_length=50, choices=HUB_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    available_connectors = models.JSONField(
        default=list
    )  # List of available connectors
    active_connectors = models.JSONField(default=list)  # List of active connectors
    integration_rules = models.JSONField(default=list)
    data_mapping = models.JSONField(default=dict)

    # Performance metrics
    integration_success_rate = models.FloatField(default=0.0)
    data_throughput = models.FloatField(default=0.0)  # records per second
    latency = models.FloatField(default=0.0)  # milliseconds
    error_rate = models.FloatField(default=0.0)

    # Usage statistics
    total_integrations = models.IntegerField(default=0)
    active_integrations = models.IntegerField(default=0)
    data_processed = models.IntegerField(default=0)
    errors_encountered = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_processing = models.BooleanField(default=False)
    last_processing = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "hub_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.hub_type})"


class APIManagement(models.Model):
    """Advanced API management with versioning, rate limiting, and developer portal."""

    API_TYPES = [
        ("rest_api", "REST API"),
        ("graphql_api", "GraphQL API"),
        ("soap_api", "SOAP API"),
        ("webhook_api", "Webhook API"),
        ("streaming_api", "Streaming API"),
        ("batch_api", "Batch API"),
        ("real_time_api", "Real-time API"),
        ("microservice_api", "Microservice API"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="api_management"
    )
    name = models.CharField(max_length=255)
    api_type = models.CharField(max_length=50, choices=API_TYPES)
    description = models.TextField(blank=True)

    # API Configuration
    base_url = models.URLField()
    version = models.CharField(max_length=20, default="v1")
    authentication_methods = models.JSONField(default=list)
    rate_limits = models.JSONField(default=dict)
    api_documentation = models.JSONField(default=dict)

    # Performance metrics
    response_time = models.FloatField(default=0.0)  # milliseconds
    availability = models.FloatField(default=0.0)
    throughput = models.FloatField(default=0.0)  # requests per second
    error_rate = models.FloatField(default=0.0)

    # Usage statistics
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    active_consumers = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "version")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.api_type})"


class WorkflowAutomation(models.Model):
    """Workflow automation with visual workflow designer and conditional logic builder."""

    WORKFLOW_TYPES = [
        ("visual_designer", "Visual Workflow Designer"),
        ("conditional_logic", "Conditional Logic Builder"),
        ("event_driven", "Event-driven Workflows"),
        ("scheduled_workflows", "Scheduled Workflows"),
        ("approval_workflows", "Approval Workflows"),
        ("data_workflows", "Data Processing Workflows"),
        ("integration_workflows", "Integration Workflows"),
        ("notification_workflows", "Notification Workflows"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="workflow_automations"
    )
    name = models.CharField(max_length=255)
    workflow_type = models.CharField(max_length=50, choices=WORKFLOW_TYPES)
    description = models.TextField(blank=True)

    # Workflow Configuration
    workflow_definition = models.JSONField(default=dict)
    trigger_conditions = models.JSONField(default=list)
    action_sequences = models.JSONField(default=list)
    approval_rules = models.JSONField(default=list)

    # Performance metrics
    execution_success_rate = models.FloatField(default=0.0)
    average_execution_time = models.FloatField(default=0.0)  # seconds
    automation_efficiency = models.FloatField(default=0.0)
    cost_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Usage statistics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)
    last_execution = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_running = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "workflow_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.workflow_type})"


class DataIntegration(models.Model):
    """Data integration suite with ETL/ELT data pipelines and data transformation tools."""

    INTEGRATION_TYPES = [
        ("etl_pipeline", "ETL Pipeline"),
        ("elt_pipeline", "ELT Pipeline"),
        ("real_time_sync", "Real-time Synchronization"),
        ("batch_processing", "Batch Processing"),
        ("data_warehouse", "Data Warehouse Integration"),
        ("data_lake", "Data Lake Integration"),
        ("cloud_storage", "Cloud Storage Integration"),
        ("database_sync", "Database Synchronization"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="data_integrations"
    )
    name = models.CharField(max_length=255)
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    description = models.TextField(blank=True)

    # Integration Configuration
    source_systems = models.JSONField(default=list)
    target_systems = models.JSONField(default=list)
    data_mapping = models.JSONField(default=dict)
    transformation_rules = models.JSONField(default=list)

    # Performance metrics
    data_quality_score = models.FloatField(default=0.0)
    processing_speed = models.FloatField(default=0.0)  # records per second
    sync_accuracy = models.FloatField(default=0.0)
    data_freshness = models.FloatField(default=0.0)  # minutes

    # Usage statistics
    total_records_processed = models.IntegerField(default=0)
    successful_syncs = models.IntegerField(default=0)
    failed_syncs = models.IntegerField(default=0)
    last_sync = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_syncing = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "integration_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.integration_type})"


class IntegrationMarketplace(models.Model):
    """Integration marketplace with third-party app store and revenue sharing model."""

    MARKETPLACE_TYPES = [
        ("app_store", "App Store"),
        ("connector_marketplace", "Connector Marketplace"),
        ("template_marketplace", "Template Marketplace"),
        ("service_marketplace", "Service Marketplace"),
        ("api_marketplace", "API Marketplace"),
        ("workflow_marketplace", "Workflow Marketplace"),
        ("integration_marketplace", "Integration Marketplace"),
        ("custom_marketplace", "Custom Marketplace"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="integration_marketplaces"
    )
    name = models.CharField(max_length=255)
    marketplace_type = models.CharField(max_length=50, choices=MARKETPLACE_TYPES)
    description = models.TextField(blank=True)

    # Marketplace Configuration
    available_apps = models.JSONField(default=list)
    revenue_sharing_model = models.JSONField(default=dict)
    pricing_tiers = models.JSONField(default=list)
    approval_process = models.JSONField(default=dict)

    # Performance metrics
    marketplace_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    app_downloads = models.IntegerField(default=0)
    user_satisfaction = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)

    # Usage statistics
    total_apps = models.IntegerField(default=0)
    active_apps = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "marketplace_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.marketplace_type})"


class IntegrationConnector(models.Model):
    """Integration connector for specific systems and services."""

    CONNECTOR_TYPES = [
        ("database", "Database Connector"),
        ("api", "API Connector"),
        ("file", "File Connector"),
        ("cloud", "Cloud Connector"),
        ("legacy", "Legacy System Connector"),
        ("social", "Social Media Connector"),
        ("communication", "Communication Connector"),
        ("business", "Business Application Connector"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="integration_connectors"
    )
    name = models.CharField(max_length=255)
    connector_type = models.CharField(max_length=50, choices=CONNECTOR_TYPES)
    description = models.TextField(blank=True)

    # Connector Configuration
    system_info = models.JSONField(default=dict)
    connection_config = models.JSONField(default=dict)
    authentication_config = models.JSONField(default=dict)
    data_schema = models.JSONField(default=dict)

    # Performance metrics
    connection_success_rate = models.FloatField(default=0.0)
    data_transfer_speed = models.FloatField(default=0.0)  # MB/s
    latency = models.FloatField(default=0.0)  # milliseconds
    reliability = models.FloatField(default=0.0)

    # Usage statistics
    total_connections = models.IntegerField(default=0)
    successful_connections = models.IntegerField(default=0)
    failed_connections = models.IntegerField(default=0)
    last_connection = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_connected = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "connector_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.connector_type})"


class IntegrationTemplate(models.Model):
    """Integration template for common integration patterns."""

    TEMPLATE_TYPES = [
        ("data_sync", "Data Synchronization"),
        ("api_integration", "API Integration"),
        ("workflow_automation", "Workflow Automation"),
        ("notification_integration", "Notification Integration"),
        ("reporting_integration", "Reporting Integration"),
        ("authentication_integration", "Authentication Integration"),
        ("payment_integration", "Payment Integration"),
        ("communication_integration", "Communication Integration"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="integration_templates"
    )
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True)

    # Template Configuration
    template_definition = models.JSONField(default=dict)
    required_connectors = models.JSONField(default=list)
    configuration_options = models.JSONField(default=dict)
    usage_instructions = models.TextField(blank=True)

    # Performance metrics
    template_usage_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    user_rating = models.FloatField(default=0.0)
    complexity_score = models.FloatField(default=0.0)

    # Usage statistics
    total_instances = models.IntegerField(default=0)
    active_instances = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "template_type")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.template_type})"


class IntegrationLog(models.Model):
    """Integration log for tracking integration activities and errors."""

    LOG_TYPES = [
        ("connection", "Connection Log"),
        ("data_transfer", "Data Transfer Log"),
        ("error", "Error Log"),
        ("performance", "Performance Log"),
        ("audit", "Audit Log"),
        ("debug", "Debug Log"),
        ("security", "Security Log"),
        ("compliance", "Compliance Log"),
    ]

    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("critical", "Critical"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="integration_logs"
    )
    log_type = models.CharField(max_length=50, choices=LOG_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="info")
    message = models.TextField()

    # Context
    integration_id = models.CharField(max_length=255, blank=True)
    connector_id = models.CharField(max_length=255, blank=True)
    user_id = models.CharField(max_length=255, blank=True)
    request_id = models.CharField(max_length=255, blank=True)

    # Additional data
    metadata = models.JSONField(default=dict)
    stack_trace = models.TextField(blank=True)
    resolution = models.TextField(blank=True)

    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.organization.name} - {self.log_type} ({self.severity}) - {self.timestamp}"


class IntegrationMetric(models.Model):
    """Integration metrics for monitoring and analytics."""

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="integration_metrics"
    )
    metric_name = models.CharField(max_length=255)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=50)

    # Context
    integration_id = models.CharField(max_length=255, blank=True)
    connector_id = models.CharField(max_length=255, blank=True)
    time_period = models.CharField(max_length=50, default="hourly")

    # Additional data
    metadata = models.JSONField(default=dict)

    # Timestamp
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.metric_name}: {self.metric_value} {self.metric_unit}"
