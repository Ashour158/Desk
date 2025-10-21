"""
AI/ML filters for API endpoints.
"""

import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    MLModel,
    Prediction,
    AnomalyDetection,
    CustomerInsight,
    DemandForecast,
    Recommendation,
    MLTrainingJob,
    DataPipeline,
)


class MLModelFilter(django_filters.FilterSet):
    """ML Model filters."""

    model_type = django_filters.ChoiceFilter(choices=MLModel.MODEL_TYPES)
    status = django_filters.ChoiceFilter(choices=MLModel.STATUS_CHOICES)
    is_active = django_filters.BooleanFilter()
    algorithm = django_filters.CharFilter(lookup_expr="icontains")
    min_accuracy = django_filters.NumberFilter(field_name="accuracy", lookup_expr="gte")
    max_accuracy = django_filters.NumberFilter(field_name="accuracy", lookup_expr="lte")
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    trained_after = django_filters.DateTimeFilter(
        field_name="last_trained", lookup_expr="gte"
    )
    trained_before = django_filters.DateTimeFilter(
        field_name="last_trained", lookup_expr="lte"
    )

    class Meta:
        model = MLModel
        fields = ["model_type", "status", "is_active", "algorithm"]


class PredictionFilter(django_filters.FilterSet):
    """Prediction filters."""

    model = django_filters.ModelChoiceFilter(queryset=MLModel.objects.all())
    model_type = django_filters.CharFilter(field_name="model__model_type")
    entity_type = django_filters.CharFilter()
    is_validated = django_filters.BooleanFilter()
    min_confidence = django_filters.NumberFilter(
        field_name="confidence", lookup_expr="gte"
    )
    max_confidence = django_filters.NumberFilter(
        field_name="confidence", lookup_expr="lte"
    )
    min_probability = django_filters.NumberFilter(
        field_name="probability", lookup_expr="gte"
    )
    max_probability = django_filters.NumberFilter(
        field_name="probability", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Prediction
        fields = ["model", "entity_type", "is_validated"]


class AnomalyDetectionFilter(django_filters.FilterSet):
    """Anomaly Detection filters."""

    anomaly_type = django_filters.ChoiceFilter(choices=AnomalyDetection.ANOMALY_TYPES)
    severity = django_filters.ChoiceFilter(choices=AnomalyDetection.SEVERITY_LEVELS)
    is_resolved = django_filters.BooleanFilter()
    min_deviation_score = django_filters.NumberFilter(
        field_name="deviation_score", lookup_expr="gte"
    )
    max_deviation_score = django_filters.NumberFilter(
        field_name="deviation_score", lookup_expr="lte"
    )
    detected_after = django_filters.DateTimeFilter(
        field_name="detected_at", lookup_expr="gte"
    )
    detected_before = django_filters.DateTimeFilter(
        field_name="detected_at", lookup_expr="lte"
    )
    resolved_after = django_filters.DateTimeFilter(
        field_name="resolved_at", lookup_expr="gte"
    )
    resolved_before = django_filters.DateTimeFilter(
        field_name="resolved_at", lookup_expr="lte"
    )

    # Custom filters
    recent_only = django_filters.BooleanFilter(method="filter_recent_only")
    high_severity_only = django_filters.BooleanFilter(
        method="filter_high_severity_only"
    )

    class Meta:
        model = AnomalyDetection
        fields = ["anomaly_type", "severity", "is_resolved"]

    def filter_recent_only(self, queryset, name, value):
        """Filter for anomalies detected in the last 7 days."""
        if value:
            seven_days_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(detected_at__gte=seven_days_ago)
        return queryset

    def filter_high_severity_only(self, queryset, name, value):
        """Filter for high and critical severity anomalies."""
        if value:
            return queryset.filter(severity__in=["high", "critical"])
        return queryset


class CustomerInsightFilter(django_filters.FilterSet):
    """Customer Insight filters."""

    is_at_risk = django_filters.BooleanFilter()
    min_health_score = django_filters.NumberFilter(
        field_name="health_score", lookup_expr="gte"
    )
    max_health_score = django_filters.NumberFilter(
        field_name="health_score", lookup_expr="lte"
    )
    min_churn_probability = django_filters.NumberFilter(
        field_name="churn_probability", lookup_expr="gte"
    )
    max_churn_probability = django_filters.NumberFilter(
        field_name="churn_probability", lookup_expr="lte"
    )
    preferred_channel = django_filters.CharFilter()
    customer_name = django_filters.CharFilter(
        field_name="customer__full_name", lookup_expr="icontains"
    )
    customer_email = django_filters.CharFilter(
        field_name="customer__email", lookup_expr="icontains"
    )

    class Meta:
        model = CustomerInsight
        fields = ["is_at_risk", "preferred_channel"]


class DemandForecastFilter(django_filters.FilterSet):
    """Demand Forecast filters."""

    forecast_type = django_filters.ChoiceFilter(choices=DemandForecast.FORECAST_TYPES)
    forecast_date_after = django_filters.DateFilter(
        field_name="forecast_date", lookup_expr="gte"
    )
    forecast_date_before = django_filters.DateFilter(
        field_name="forecast_date", lookup_expr="lte"
    )
    min_predicted_value = django_filters.NumberFilter(
        field_name="predicted_value", lookup_expr="gte"
    )
    max_predicted_value = django_filters.NumberFilter(
        field_name="predicted_value", lookup_expr="lte"
    )
    has_actual_value = django_filters.BooleanFilter(
        field_name="actual_value", lookup_expr="isnull", exclude=True
    )

    class Meta:
        model = DemandForecast
        fields = ["forecast_type"]


class RecommendationFilter(django_filters.FilterSet):
    """Recommendation filters."""

    recommendation_type = django_filters.ChoiceFilter(
        choices=Recommendation.RECOMMENDATION_TYPES
    )
    is_accepted = django_filters.BooleanFilter()
    is_implemented = django_filters.BooleanFilter()
    min_confidence = django_filters.NumberFilter(
        field_name="confidence", lookup_expr="gte"
    )
    max_confidence = django_filters.NumberFilter(
        field_name="confidence", lookup_expr="lte"
    )
    entity_type = django_filters.CharFilter()
    target_user = django_filters.NumberFilter()
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    # Custom filters
    pending_only = django_filters.BooleanFilter(method="filter_pending_only")
    high_confidence_only = django_filters.BooleanFilter(
        method="filter_high_confidence_only"
    )

    class Meta:
        model = Recommendation
        fields = ["recommendation_type", "is_accepted", "is_implemented", "entity_type"]

    def filter_pending_only(self, queryset, name, value):
        """Filter for pending recommendations."""
        if value:
            return queryset.filter(is_accepted=False, is_implemented=False)
        return queryset

    def filter_high_confidence_only(self, queryset, name, value):
        """Filter for high confidence recommendations."""
        if value:
            return queryset.filter(confidence__gte=0.8)
        return queryset


class MLTrainingJobFilter(django_filters.FilterSet):
    """ML Training Job filters."""

    status = django_filters.ChoiceFilter(choices=MLTrainingJob.STATUS_CHOICES)
    model = django_filters.ModelChoiceFilter(queryset=MLModel.objects.all())
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    started_after = django_filters.DateTimeFilter(
        field_name="started_at", lookup_expr="gte"
    )
    started_before = django_filters.DateTimeFilter(
        field_name="started_at", lookup_expr="lte"
    )
    completed_after = django_filters.DateTimeFilter(
        field_name="completed_at", lookup_expr="gte"
    )
    completed_before = django_filters.DateTimeFilter(
        field_name="completed_at", lookup_expr="lte"
    )

    class Meta:
        model = MLTrainingJob
        fields = ["status", "model"]


class DataPipelineFilter(django_filters.FilterSet):
    """Data Pipeline filters."""

    pipeline_type = django_filters.ChoiceFilter(choices=DataPipeline.PIPELINE_TYPES)
    is_active = django_filters.BooleanFilter()
    has_schedule = django_filters.BooleanFilter(
        field_name="schedule", lookup_expr="isnull", exclude=True
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    last_run_after = django_filters.DateTimeFilter(
        field_name="last_run", lookup_expr="gte"
    )
    last_run_before = django_filters.DateTimeFilter(
        field_name="last_run", lookup_expr="lte"
    )

    # Custom filters
    successful_only = django_filters.BooleanFilter(method="filter_successful_only")
    failed_only = django_filters.BooleanFilter(method="filter_failed_only")

    class Meta:
        model = DataPipeline
        fields = ["pipeline_type", "is_active"]

    def filter_successful_only(self, queryset, name, value):
        """Filter for pipelines with high success rate."""
        if value:
            return queryset.filter(success_count__gt=0).exclude(success_count=0)
        return queryset

    def filter_failed_only(self, queryset, name, value):
        """Filter for pipelines with failures."""
        if value:
            return queryset.filter(failure_count__gt=0)
        return queryset
