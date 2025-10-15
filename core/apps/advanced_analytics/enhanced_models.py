"""
Enhanced Advanced Analytics & Business Intelligence models for advanced capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.organizations.models import Organization
from apps.common.base_models import BaseModel, ConfigurationModel, MetricsModel
from apps.common.constants import (
    SHORT_FIELD_LENGTH,
    MEDIUM_FIELD_LENGTH,
    LONG_FIELD_LENGTH,
    VERY_LONG_FIELD_LENGTH,
)
import uuid

User = get_user_model()


class DataSciencePlatform(models.Model):
    """Advanced data science platform with ML model builder and statistical analysis tools."""

    PLATFORM_TYPES = [
        ("ml_model_builder", "ML Model Builder"),
        ("statistical_analysis", "Statistical Analysis Tools"),
        ("data_visualization", "Data Visualization Studio"),
        ("predictive_modeling", "Predictive Modeling Interface"),
        ("ab_testing", "A/B Testing Framework"),
        ("data_mining", "Data Mining Tools"),
        ("machine_learning", "Machine Learning Platform"),
        ("deep_learning", "Deep Learning Platform"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="data_science_platforms"
    )
    name = models.CharField(max_length=255)
    platform_type = models.CharField(max_length=50, choices=PLATFORM_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    data_sources = models.JSONField(default=list)
    ml_frameworks = models.JSONField(
        default=list
    )  # TensorFlow, PyTorch, Scikit-learn, etc.
    supported_algorithms = models.JSONField(default=list)
    compute_resources = models.JSONField(default=dict)

    # Performance metrics
    model_accuracy = models.FloatField(default=0.0)
    training_speed = models.FloatField(default=0.0)  # models per hour
    inference_speed = models.FloatField(default=0.0)  # predictions per second
    resource_utilization = models.FloatField(default=0.0)

    # Usage statistics
    total_models = models.IntegerField(default=0)
    active_models = models.IntegerField(default=0)
    total_predictions = models.IntegerField(default=0)
    successful_predictions = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_training = models.BooleanField(default=False)
    last_training = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "platform_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.platform_type})"


class RealTimeAnalyticsEngine(models.Model):
    """Real-time analytics engine with live dashboard updates and streaming data processing."""

    ENGINE_TYPES = [
        ("live_dashboard", "Live Dashboard Updates"),
        ("real_time_alerts", "Real-time Alerts & Notifications"),
        ("streaming_processing", "Streaming Data Processing"),
        ("event_driven", "Event-driven Analytics"),
        ("instant_insights", "Instant Insights Generation"),
        ("real_time_ml", "Real-time Machine Learning"),
        ("stream_analytics", "Stream Analytics"),
        ("complex_event_processing", "Complex Event Processing"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="real_time_analytics"
    )
    name = models.CharField(max_length=255)
    engine_type = models.CharField(max_length=50, choices=ENGINE_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    data_streams = models.JSONField(default=list)
    processing_rules = models.JSONField(default=list)
    alert_conditions = models.JSONField(default=list)
    output_destinations = models.JSONField(default=list)

    # Performance metrics
    processing_latency = models.FloatField(default=0.0)  # milliseconds
    throughput = models.FloatField(default=0.0)  # events per second
    accuracy = models.FloatField(default=0.0)
    availability = models.FloatField(default=0.0)

    # Usage statistics
    total_events_processed = models.IntegerField(default=0)
    active_streams = models.IntegerField(default=0)
    alerts_generated = models.IntegerField(default=0)
    insights_generated = models.IntegerField(default=0)

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
        unique_together = ("organization", "name", "engine_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.engine_type})"


class AdvancedReportingSuite(models.Model):
    """Advanced reporting suite with automated report generation and interactive report builder."""

    REPORTING_TYPES = [
        ("automated_reports", "Automated Report Generation"),
        ("interactive_builder", "Interactive Report Builder"),
        ("scheduled_reports", "Scheduled Report Distribution"),
        ("white_label", "White-label Reporting"),
        ("mobile_reports", "Mobile Report Access"),
        ("real_time_reports", "Real-time Reports"),
        ("custom_dashboards", "Custom Dashboards"),
        ("data_exports", "Data Exports"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="reporting_suites"
    )
    name = models.CharField(max_length=255)
    reporting_type = models.CharField(max_length=50, choices=REPORTING_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    report_templates = models.JSONField(default=list)
    data_sources = models.JSONField(default=list)
    distribution_channels = models.JSONField(default=list)
    export_formats = models.JSONField(default=list)

    # Performance metrics
    report_generation_time = models.FloatField(default=0.0)  # seconds
    report_accuracy = models.FloatField(default=0.0)
    user_satisfaction = models.FloatField(default=0.0)
    delivery_success_rate = models.FloatField(default=0.0)

    # Usage statistics
    total_reports = models.IntegerField(default=0)
    scheduled_reports = models.IntegerField(default=0)
    report_views = models.IntegerField(default=0)
    exports_generated = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_generating = models.BooleanField(default=False)
    last_generation = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "reporting_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.reporting_type})"


class BusinessIntelligenceTools(models.Model):
    """Business intelligence tools with executive dashboards and strategic planning tools."""

    BI_TYPES = [
        ("executive_dashboards", "Executive Dashboards"),
        ("performance_scorecards", "Performance Scorecards"),
        ("trend_analysis", "Trend Analysis & Forecasting"),
        ("comparative_analytics", "Comparative Analytics"),
        ("strategic_planning", "Strategic Planning Tools"),
        ("kpi_management", "KPI Management"),
        ("benchmarking", "Benchmarking Tools"),
        ("decision_support", "Decision Support Systems"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="bi_tools"
    )
    name = models.CharField(max_length=255)
    bi_type = models.CharField(max_length=50, choices=BI_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    dashboard_config = models.JSONField(default=dict)
    kpi_definitions = models.JSONField(default=list)
    data_connections = models.JSONField(default=list)
    visualization_types = models.JSONField(default=list)

    # Performance metrics
    dashboard_load_time = models.FloatField(default=0.0)  # seconds
    data_freshness = models.FloatField(default=0.0)  # minutes
    user_engagement = models.FloatField(default=0.0)
    decision_impact = models.FloatField(default=0.0)

    # Usage statistics
    total_dashboards = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    dashboard_views = models.IntegerField(default=0)
    kpi_updates = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_updating = models.BooleanField(default=False)
    last_update = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "bi_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.bi_type})"


class DataGovernance(models.Model):
    """Data governance and compliance with data quality management and privacy impact assessment."""

    GOVERNANCE_TYPES = [
        ("data_quality", "Data Quality Management"),
        ("data_lineage", "Data Lineage Tracking"),
        ("privacy_impact", "Privacy Impact Assessment"),
        ("compliance_reporting", "Compliance Reporting"),
        ("data_security", "Data Security Monitoring"),
        ("data_catalog", "Data Catalog Management"),
        ("data_classification", "Data Classification"),
        ("data_retention", "Data Retention Management"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="data_governance"
    )
    name = models.CharField(max_length=255)
    governance_type = models.CharField(max_length=50, choices=GOVERNANCE_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    governance_policies = models.JSONField(default=list)
    data_classifications = models.JSONField(default=list)
    compliance_standards = models.JSONField(default=list)
    monitoring_rules = models.JSONField(default=list)

    # Performance metrics
    data_quality_score = models.FloatField(default=0.0)
    compliance_rate = models.FloatField(default=0.0)
    policy_adherence = models.FloatField(default=0.0)
    risk_score = models.FloatField(default=0.0)

    # Usage statistics
    total_policies = models.IntegerField(default=0)
    active_monitoring = models.IntegerField(default=0)
    compliance_checks = models.IntegerField(default=0)
    violations_detected = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_monitoring = models.BooleanField(default=False)
    last_monitoring = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "governance_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.governance_type})"


class AnalyticsModel(models.Model):
    """Analytics models for data science and machine learning."""

    MODEL_TYPES = [
        ("classification", "Classification"),
        ("regression", "Regression"),
        ("clustering", "Clustering"),
        ("anomaly_detection", "Anomaly Detection"),
        ("recommendation", "Recommendation"),
        ("forecasting", "Forecasting"),
        ("nlp", "Natural Language Processing"),
        ("computer_vision", "Computer Vision"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("training", "Training"),
        ("trained", "Trained"),
        ("deployed", "Deployed"),
        ("retired", "Retired"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="analytics_models"
    )
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    description = models.TextField(blank=True)

    # Model configuration
    algorithm = models.CharField(max_length=100)
    hyperparameters = models.JSONField(default=dict)
    training_data = models.JSONField(default=dict)
    validation_data = models.JSONField(default=dict)

    # Performance metrics
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    auc_score = models.FloatField(default=0.0)

    # Usage statistics
    total_predictions = models.IntegerField(default=0)
    successful_predictions = models.IntegerField(default=0)
    failed_predictions = models.IntegerField(default=0)
    last_prediction = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.model_type})"


class AnalyticsDashboard(models.Model):
    """Analytics dashboards for data visualization and insights."""

    DASHBOARD_TYPES = [
        ("executive", "Executive Dashboard"),
        ("operational", "Operational Dashboard"),
        ("analytical", "Analytical Dashboard"),
        ("real_time", "Real-time Dashboard"),
        ("mobile", "Mobile Dashboard"),
        ("custom", "Custom Dashboard"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="analytics_dashboards"
    )
    name = models.CharField(max_length=255)
    dashboard_type = models.CharField(max_length=50, choices=DASHBOARD_TYPES)
    description = models.TextField(blank=True)

    # Dashboard configuration
    layout_config = models.JSONField(default=dict)
    widgets = models.JSONField(default=list)
    data_sources = models.JSONField(default=list)
    refresh_interval = models.IntegerField(default=300)  # seconds

    # Performance metrics
    load_time = models.FloatField(default=0.0)  # seconds
    user_engagement = models.FloatField(default=0.0)
    data_freshness = models.FloatField(default=0.0)  # minutes
    error_rate = models.FloatField(default=0.0)

    # Usage statistics
    total_views = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.dashboard_type})"


class AnalyticsReport(models.Model):
    """Analytics reports for data analysis and insights."""

    REPORT_TYPES = [
        ("scheduled", "Scheduled Report"),
        ("ad_hoc", "Ad-hoc Report"),
        ("automated", "Automated Report"),
        ("interactive", "Interactive Report"),
        ("export", "Export Report"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="analytics_reports"
    )
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)

    # Report configuration
    report_config = models.JSONField(default=dict)
    data_queries = models.JSONField(default=list)
    visualization_config = models.JSONField(default=dict)
    distribution_config = models.JSONField(default=dict)

    # Performance metrics
    generation_time = models.FloatField(default=0.0)  # seconds
    file_size = models.FloatField(default=0.0)  # MB
    accuracy = models.FloatField(default=0.0)
    user_satisfaction = models.FloatField(default=0.0)

    # Usage statistics
    total_generations = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    last_generated = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_scheduled = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.report_type})"


class AnalyticsAlert(models.Model):
    """Analytics alerts for real-time monitoring and notifications."""

    ALERT_TYPES = [
        ("threshold", "Threshold Alert"),
        ("anomaly", "Anomaly Alert"),
        ("trend", "Trend Alert"),
        ("performance", "Performance Alert"),
        ("data_quality", "Data Quality Alert"),
        ("compliance", "Compliance Alert"),
    ]

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="analytics_alerts"
    )
    name = models.CharField(max_length=255)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(
        max_length=20, choices=SEVERITY_CHOICES, default="medium"
    )
    description = models.TextField(blank=True)

    # Alert configuration
    trigger_conditions = models.JSONField(default=list)
    notification_channels = models.JSONField(default=list)
    escalation_rules = models.JSONField(default=list)
    suppression_rules = models.JSONField(default=list)

    # Performance metrics
    alert_accuracy = models.FloatField(default=0.0)
    response_time = models.FloatField(default=0.0)  # seconds
    false_positive_rate = models.FloatField(default=0.0)
    resolution_time = models.FloatField(default=0.0)  # minutes

    # Usage statistics
    total_alerts = models.IntegerField(default=0)
    active_alerts = models.IntegerField(default=0)
    resolved_alerts = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_enabled = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.alert_type})"
