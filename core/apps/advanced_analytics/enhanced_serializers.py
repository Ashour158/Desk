"""
Enhanced Advanced Analytics & Business Intelligence serializers for advanced capabilities.
"""

from rest_framework import serializers
from .enhanced_models import (
    DataSciencePlatform,
    RealTimeAnalyticsEngine,
    AdvancedReportingSuite,
    BusinessIntelligenceTools,
    DataGovernance,
    AnalyticsModel,
    AnalyticsDashboard,
    AnalyticsReport,
    AnalyticsAlert,
)


class DataSciencePlatformSerializer(serializers.ModelSerializer):
    """Serializer for Data Science Platform."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = DataSciencePlatform
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_model_accuracy(self, value):
        """Validate model accuracy."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Model accuracy must be between 0 and 1.")
        return value

    def validate_training_speed(self, value):
        """Validate training speed."""
        if value < 0:
            raise serializers.ValidationError("Training speed must be non-negative.")
        return value


class RealTimeAnalyticsEngineSerializer(serializers.ModelSerializer):
    """Serializer for Real-time Analytics Engine."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = RealTimeAnalyticsEngine
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_processing_latency(self, value):
        """Validate processing latency."""
        if value < 0:
            raise serializers.ValidationError(
                "Processing latency must be non-negative."
            )
        return value

    def validate_throughput(self, value):
        """Validate throughput."""
        if value < 0:
            raise serializers.ValidationError("Throughput must be non-negative.")
        return value


class AdvancedReportingSuiteSerializer(serializers.ModelSerializer):
    """Serializer for Advanced Reporting Suite."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AdvancedReportingSuite
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_report_generation_time(self, value):
        """Validate report generation time."""
        if value < 0:
            raise serializers.ValidationError(
                "Report generation time must be non-negative."
            )
        return value

    def validate_report_accuracy(self, value):
        """Validate report accuracy."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Report accuracy must be between 0 and 1."
            )
        return value


class BusinessIntelligenceToolsSerializer(serializers.ModelSerializer):
    """Serializer for Business Intelligence Tools."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = BusinessIntelligenceTools
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_dashboard_load_time(self, value):
        """Validate dashboard load time."""
        if value < 0:
            raise serializers.ValidationError(
                "Dashboard load time must be non-negative."
            )
        return value

    def validate_data_freshness(self, value):
        """Validate data freshness."""
        if value < 0:
            raise serializers.ValidationError("Data freshness must be non-negative.")
        return value


class DataGovernanceSerializer(serializers.ModelSerializer):
    """Serializer for Data Governance."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = DataGovernance
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_data_quality_score(self, value):
        """Validate data quality score."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Data quality score must be between 0 and 1."
            )
        return value

    def validate_compliance_rate(self, value):
        """Validate compliance rate."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Compliance rate must be between 0 and 1."
            )
        return value


class AnalyticsModelSerializer(serializers.ModelSerializer):
    """Serializer for Analytics Model."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AnalyticsModel
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_accuracy(self, value):
        """Validate accuracy."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Accuracy must be between 0 and 1.")
        return value

    def validate_precision(self, value):
        """Validate precision."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Precision must be between 0 and 1.")
        return value

    def validate_recall(self, value):
        """Validate recall."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Recall must be between 0 and 1.")
        return value

    def validate_f1_score(self, value):
        """Validate F1 score."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("F1 score must be between 0 and 1.")
        return value


class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    """Serializer for Analytics Dashboard."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AnalyticsDashboard
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_load_time(self, value):
        """Validate load time."""
        if value < 0:
            raise serializers.ValidationError("Load time must be non-negative.")
        return value

    def validate_user_engagement(self, value):
        """Validate user engagement."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "User engagement must be between 0 and 1."
            )
        return value


class AnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer for Analytics Report."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AnalyticsReport
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_generation_time(self, value):
        """Validate generation time."""
        if value < 0:
            raise serializers.ValidationError("Generation time must be non-negative.")
        return value

    def validate_file_size(self, value):
        """Validate file size."""
        if value < 0:
            raise serializers.ValidationError("File size must be non-negative.")
        return value


class AnalyticsAlertSerializer(serializers.ModelSerializer):
    """Serializer for Analytics Alert."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AnalyticsAlert
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_alert_accuracy(self, value):
        """Validate alert accuracy."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Alert accuracy must be between 0 and 1.")
        return value

    def validate_response_time(self, value):
        """Validate response time."""
        if value < 0:
            raise serializers.ValidationError("Response time must be non-negative.")
        return value


class MLModelRequestSerializer(serializers.Serializer):
    """Serializer for ML model building requests."""

    name = serializers.CharField(max_length=255)
    model_type = serializers.ChoiceField(
        choices=[
            ("classification", "Classification"),
            ("regression", "Regression"),
            ("clustering", "Clustering"),
            ("anomaly_detection", "Anomaly Detection"),
            ("recommendation", "Recommendation"),
            ("forecasting", "Forecasting"),
            ("nlp", "Natural Language Processing"),
            ("computer_vision", "Computer Vision"),
        ]
    )
    algorithm = serializers.CharField(max_length=100)
    hyperparameters = serializers.JSONField(default=dict, required=False)
    training_data = serializers.JSONField()
    validation_data = serializers.JSONField(required=False)

    def validate_name(self, value):
        """Validate model name."""
        if not value.strip():
            raise serializers.ValidationError("Model name cannot be empty.")
        return value


class StatisticalAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for statistical analysis requests."""

    data = serializers.JSONField()
    analysis_type = serializers.ChoiceField(
        choices=[
            ("descriptive", "Descriptive Statistics"),
            ("inferential", "Inferential Statistics"),
            ("correlation", "Correlation Analysis"),
            ("regression", "Regression Analysis"),
            ("hypothesis_testing", "Hypothesis Testing"),
            ("anova", "ANOVA"),
            ("time_series", "Time Series Analysis"),
        ],
        default="descriptive",
    )
    variables = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False
    )

    def validate_data(self, value):
        """Validate data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data must be a dictionary.")
        return value


class StreamingDataRequestSerializer(serializers.Serializer):
    """Serializer for streaming data processing requests."""

    data_stream = serializers.JSONField()
    stream_id = serializers.CharField(max_length=255, required=False)
    processing_rules = serializers.JSONField(default=list, required=False)
    output_format = serializers.ChoiceField(
        choices=[
            ("json", "JSON"),
            ("csv", "CSV"),
            ("xml", "XML"),
        ],
        default="json",
    )

    def validate_data_stream(self, value):
        """Validate data stream."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data stream must be a dictionary.")
        return value


class ReportGenerationRequestSerializer(serializers.Serializer):
    """Serializer for report generation requests."""

    name = serializers.CharField(max_length=255)
    report_type = serializers.ChoiceField(
        choices=[
            ("scheduled", "Scheduled Report"),
            ("ad_hoc", "Ad-hoc Report"),
            ("automated", "Automated Report"),
            ("interactive", "Interactive Report"),
            ("export", "Export Report"),
        ]
    )
    data_sources = serializers.ListField(child=serializers.CharField(max_length=255))
    format = serializers.ChoiceField(
        choices=[
            ("pdf", "PDF"),
            ("excel", "Excel"),
            ("csv", "CSV"),
            ("html", "HTML"),
        ],
        default="pdf",
    )
    schedule = serializers.JSONField(required=False)

    def validate_name(self, value):
        """Validate report name."""
        if not value.strip():
            raise serializers.ValidationError("Report name cannot be empty.")
        return value


class DashboardCreationRequestSerializer(serializers.Serializer):
    """Serializer for dashboard creation requests."""

    name = serializers.CharField(max_length=255)
    dashboard_type = serializers.ChoiceField(
        choices=[
            ("executive", "Executive Dashboard"),
            ("operational", "Operational Dashboard"),
            ("analytical", "Analytical Dashboard"),
            ("real_time", "Real-time Dashboard"),
            ("mobile", "Mobile Dashboard"),
            ("custom", "Custom Dashboard"),
        ]
    )
    layout_config = serializers.JSONField(default=dict, required=False)
    widgets = serializers.ListField(
        child=serializers.JSONField(), default=list, required=False
    )
    data_sources = serializers.ListField(
        child=serializers.CharField(max_length=255), default=list, required=False
    )

    def validate_name(self, value):
        """Validate dashboard name."""
        if not value.strip():
            raise serializers.ValidationError("Dashboard name cannot be empty.")
        return value


class KPIRequestSerializer(serializers.Serializer):
    """Serializer for KPI scorecard requests."""

    name = serializers.CharField(max_length=255)
    kpis = serializers.ListField(child=serializers.JSONField())
    dashboard_config = serializers.JSONField(default=dict, required=False)
    refresh_interval = serializers.IntegerField(min_value=60, default=300)

    def validate_name(self, value):
        """Validate KPI name."""
        if not value.strip():
            raise serializers.ValidationError("KPI name cannot be empty.")
        return value


class DataQualityRequestSerializer(serializers.Serializer):
    """Serializer for data quality assessment requests."""

    data_source = serializers.CharField(max_length=255)
    quality_metrics = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[
                ("completeness", "Completeness"),
                ("accuracy", "Accuracy"),
                ("consistency", "Consistency"),
                ("timeliness", "Timeliness"),
                ("validity", "Validity"),
            ]
        ),
        default=["completeness", "accuracy", "consistency"],
    )
    threshold = serializers.FloatField(min_value=0, max_value=1, default=0.8)

    def validate_data_source(self, value):
        """Validate data source."""
        if not value.strip():
            raise serializers.ValidationError("Data source cannot be empty.")
        return value


class PrivacyAssessmentRequestSerializer(serializers.Serializer):
    """Serializer for privacy impact assessment requests."""

    data_processing = serializers.JSONField()
    assessment_type = serializers.ChoiceField(
        choices=[
            ("full", "Full Assessment"),
            ("quick", "Quick Assessment"),
            ("targeted", "Targeted Assessment"),
        ],
        default="full",
    )
    compliance_standards = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[
                ("gdpr", "GDPR"),
                ("ccpa", "CCPA"),
                ("hipaa", "HIPAA"),
                ("sox", "SOX"),
                ("iso27001", "ISO 27001"),
            ]
        ),
        default=["gdpr"],
    )

    def validate_data_processing(self, value):
        """Validate data processing information."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data processing must be a dictionary.")
        return value


class ModelPredictionRequestSerializer(serializers.Serializer):
    """Serializer for model prediction requests."""

    input_data = serializers.JSONField()
    model_version = serializers.CharField(max_length=50, required=False)
    prediction_options = serializers.JSONField(default=dict, required=False)

    def validate_input_data(self, value):
        """Validate input data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Input data must be a dictionary.")
        return value


class AlertTestRequestSerializer(serializers.Serializer):
    """Serializer for alert testing requests."""

    test_data = serializers.JSONField()
    test_type = serializers.ChoiceField(
        choices=[
            ("threshold", "Threshold Test"),
            ("anomaly", "Anomaly Test"),
            ("trend", "Trend Test"),
            ("performance", "Performance Test"),
        ],
        default="threshold",
    )
    expected_result = serializers.JSONField(required=False)

    def validate_test_data(self, value):
        """Validate test data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Test data must be a dictionary.")
        return value
