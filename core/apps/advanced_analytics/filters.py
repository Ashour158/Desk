"""
Advanced Analytics filters for API endpoints.
"""

import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    DataWarehouse,
    CustomQuery,
    Dashboard,
    Widget,
    KPI,
    Report,
    Benchmark,
    Insight,
    DataSource,
)


class DataWarehouseFilter(django_filters.FilterSet):
    """Data warehouse filters."""

    warehouse_type = django_filters.ChoiceFilter(choices=DataWarehouse.WAREHOUSE_TYPES)
    is_active = django_filters.BooleanFilter()
    is_connected = django_filters.BooleanFilter()
    version = django_filters.CharFilter(lookup_expr="icontains")
    min_rate_limit = django_filters.NumberFilter(
        field_name="rate_limit", lookup_expr="gte"
    )
    max_rate_limit = django_filters.NumberFilter(
        field_name="rate_limit", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    last_sync_after = django_filters.DateTimeFilter(
        field_name="last_sync", lookup_expr="gte"
    )
    last_sync_before = django_filters.DateTimeFilter(
        field_name="last_sync", lookup_expr="lte"
    )

    # Custom filters
    recently_synced = django_filters.BooleanFilter(method="filter_recently_synced")
    high_performance = django_filters.BooleanFilter(method="filter_high_performance")

    class Meta:
        model = DataWarehouse
        fields = ["warehouse_type", "is_active", "is_connected"]

    def filter_recently_synced(self, queryset, name, value):
        """Filter for warehouses synced in the last 24 hours."""
        if value:
            twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
            return queryset.filter(last_sync__gte=twenty_four_hours_ago)
        return queryset

    def filter_high_performance(self, queryset, name, value):
        """Filter for high-performance warehouses."""
        if value:
            return queryset.filter(rate_limit__gte=10000)
        return queryset


class CustomQueryFilter(django_filters.FilterSet):
    """Custom query filters."""

    query_type = django_filters.ChoiceFilter(choices=CustomQuery.QUERY_TYPES)
    is_active = django_filters.BooleanFilter()
    is_validated = django_filters.BooleanFilter()
    is_public = django_filters.BooleanFilter()
    requires_approval = django_filters.BooleanFilter()
    min_execution_time = django_filters.NumberFilter(
        field_name="execution_time_ms", lookup_expr="gte"
    )
    max_execution_time = django_filters.NumberFilter(
        field_name="execution_time_ms", lookup_expr="lte"
    )
    min_row_count = django_filters.NumberFilter(
        field_name="row_count", lookup_expr="gte"
    )
    max_row_count = django_filters.NumberFilter(
        field_name="row_count", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    last_executed_after = django_filters.DateTimeFilter(
        field_name="last_executed", lookup_expr="gte"
    )
    last_executed_before = django_filters.DateTimeFilter(
        field_name="last_executed", lookup_expr="lte"
    )

    # Custom filters
    fast_queries = django_filters.BooleanFilter(method="filter_fast_queries")
    popular_queries = django_filters.BooleanFilter(method="filter_popular_queries")

    class Meta:
        model = CustomQuery
        fields = [
            "query_type",
            "is_active",
            "is_validated",
            "is_public",
            "requires_approval",
        ]

    def filter_fast_queries(self, queryset, name, value):
        """Filter for fast-executing queries."""
        if value:
            return queryset.filter(execution_time_ms__lte=1000)
        return queryset

    def filter_popular_queries(self, queryset, name, value):
        """Filter for frequently executed queries."""
        if value:
            return queryset.filter(row_count__gte=1000)
        return queryset


class DashboardFilter(django_filters.FilterSet):
    """Dashboard filters."""

    dashboard_type = django_filters.ChoiceFilter(choices=Dashboard.DASHBOARD_TYPES)
    is_active = django_filters.BooleanFilter()
    is_public = django_filters.BooleanFilter()
    is_default = django_filters.BooleanFilter()
    min_refresh_interval = django_filters.NumberFilter(
        field_name="refresh_interval", lookup_expr="gte"
    )
    max_refresh_interval = django_filters.NumberFilter(
        field_name="refresh_interval", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    updated_after = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte"
    )
    updated_before = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte"
    )

    # Custom filters
    real_time_dashboards = django_filters.BooleanFilter(
        method="filter_real_time_dashboards"
    )
    public_dashboards = django_filters.BooleanFilter(method="filter_public_dashboards")

    class Meta:
        model = Dashboard
        fields = ["dashboard_type", "is_active", "is_public", "is_default"]

    def filter_real_time_dashboards(self, queryset, name, value):
        """Filter for real-time dashboards."""
        if value:
            return queryset.filter(refresh_interval__lte=60)
        return queryset

    def filter_public_dashboards(self, queryset, name, value):
        """Filter for public dashboards."""
        if value:
            return queryset.filter(is_public=True)
        return queryset


class WidgetFilter(django_filters.FilterSet):
    """Widget filters."""

    widget_type = django_filters.ChoiceFilter(choices=Widget.WIDGET_TYPES)
    chart_type = django_filters.ChoiceFilter(choices=Widget.CHART_TYPES)
    is_active = django_filters.BooleanFilter()
    show_legend = django_filters.BooleanFilter()
    show_tooltip = django_filters.BooleanFilter()
    dashboard = django_filters.NumberFilter()
    data_source = django_filters.NumberFilter()
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    updated_after = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="gte"
    )
    updated_before = django_filters.DateTimeFilter(
        field_name="updated_at", lookup_expr="lte"
    )

    # Custom filters
    chart_widgets = django_filters.BooleanFilter(method="filter_chart_widgets")
    interactive_widgets = django_filters.BooleanFilter(
        method="filter_interactive_widgets"
    )

    class Meta:
        model = Widget
        fields = ["widget_type", "chart_type", "is_active", "dashboard", "data_source"]

    def filter_chart_widgets(self, queryset, name, value):
        """Filter for chart widgets."""
        if value:
            return queryset.filter(widget_type="chart")
        return queryset

    def filter_interactive_widgets(self, queryset, name, value):
        """Filter for interactive widgets."""
        if value:
            return queryset.filter(show_tooltip=True)
        return queryset


class KPIFilter(django_filters.FilterSet):
    """KPI filters."""

    kpi_type = django_filters.ChoiceFilter(choices=KPI.KPI_TYPES)
    is_active = django_filters.BooleanFilter()
    unit = django_filters.CharFilter(lookup_expr="icontains")
    min_current_value = django_filters.NumberFilter(
        field_name="current_value", lookup_expr="gte"
    )
    max_current_value = django_filters.NumberFilter(
        field_name="current_value", lookup_expr="lte"
    )
    min_target_value = django_filters.NumberFilter(
        field_name="target_value", lookup_expr="gte"
    )
    max_target_value = django_filters.NumberFilter(
        field_name="target_value", lookup_expr="lte"
    )
    min_warning_threshold = django_filters.NumberFilter(
        field_name="warning_threshold", lookup_expr="gte"
    )
    max_warning_threshold = django_filters.NumberFilter(
        field_name="warning_threshold", lookup_expr="lte"
    )
    min_critical_threshold = django_filters.NumberFilter(
        field_name="critical_threshold", lookup_expr="gte"
    )
    max_critical_threshold = django_filters.NumberFilter(
        field_name="critical_threshold", lookup_expr="lte"
    )
    min_refresh_interval = django_filters.NumberFilter(
        field_name="refresh_interval", lookup_expr="gte"
    )
    max_refresh_interval = django_filters.NumberFilter(
        field_name="refresh_interval", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    last_calculated_after = django_filters.DateTimeFilter(
        field_name="last_calculated", lookup_expr="gte"
    )
    last_calculated_before = django_filters.DateTimeFilter(
        field_name="last_calculated", lookup_expr="lte"
    )

    # Custom filters
    above_target = django_filters.BooleanFilter(method="filter_above_target")
    below_threshold = django_filters.BooleanFilter(method="filter_below_threshold")
    trending_up = django_filters.BooleanFilter(method="filter_trending_up")

    class Meta:
        model = KPI
        fields = ["kpi_type", "is_active", "unit"]

    def filter_above_target(self, queryset, name, value):
        """Filter for KPIs above target value."""
        if value:
            return queryset.filter(current_value__gte=models.F("target_value"))
        return queryset

    def filter_below_threshold(self, queryset, name, value):
        """Filter for KPIs below warning threshold."""
        if value:
            return queryset.filter(current_value__lt=models.F("warning_threshold"))
        return queryset

    def filter_trending_up(self, queryset, name, value):
        """Filter for KPIs trending up."""
        if value:
            return queryset.filter(trend_direction="up")
        return queryset


class ReportFilter(django_filters.FilterSet):
    """Report filters."""

    report_type = django_filters.ChoiceFilter(choices=Report.REPORT_TYPES)
    format = django_filters.ChoiceFilter(choices=Report.EXPORT_FORMATS)
    is_active = django_filters.BooleanFilter()
    is_public = django_filters.BooleanFilter()
    is_scheduled = django_filters.BooleanFilter()
    query = django_filters.NumberFilter()
    min_run_count = django_filters.NumberFilter(
        field_name="run_count", lookup_expr="gte"
    )
    max_run_count = django_filters.NumberFilter(
        field_name="run_count", lookup_expr="lte"
    )
    min_success_count = django_filters.NumberFilter(
        field_name="success_count", lookup_expr="gte"
    )
    max_success_count = django_filters.NumberFilter(
        field_name="success_count", lookup_expr="lte"
    )
    min_failure_count = django_filters.NumberFilter(
        field_name="failure_count", lookup_expr="gte"
    )
    max_failure_count = django_filters.NumberFilter(
        field_name="failure_count", lookup_expr="lte"
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
    next_run_after = django_filters.DateTimeFilter(
        field_name="next_run", lookup_expr="gte"
    )
    next_run_before = django_filters.DateTimeFilter(
        field_name="next_run", lookup_expr="lte"
    )

    # Custom filters
    successful_reports = django_filters.BooleanFilter(
        method="filter_successful_reports"
    )
    scheduled_reports = django_filters.BooleanFilter(method="filter_scheduled_reports")
    recent_reports = django_filters.BooleanFilter(method="filter_recent_reports")

    class Meta:
        model = Report
        fields = [
            "report_type",
            "format",
            "is_active",
            "is_public",
            "is_scheduled",
            "query",
        ]

    def filter_successful_reports(self, queryset, name, value):
        """Filter for successful reports."""
        if value:
            return queryset.filter(success_count__gt=0).exclude(success_count=0)
        return queryset

    def filter_scheduled_reports(self, queryset, name, value):
        """Filter for scheduled reports."""
        if value:
            return queryset.filter(is_scheduled=True)
        return queryset

    def filter_recent_reports(self, queryset, name, value):
        """Filter for recently run reports."""
        if value:
            seven_days_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(last_run__gte=seven_days_ago)
        return queryset


class BenchmarkFilter(django_filters.FilterSet):
    """Benchmark filters."""

    benchmark_type = django_filters.ChoiceFilter(choices=Benchmark.BENCHMARK_TYPES)
    is_active = django_filters.BooleanFilter()
    metric_name = django_filters.CharFilter(lookup_expr="icontains")
    data_source = django_filters.CharFilter(lookup_expr="icontains")
    min_industry_average = django_filters.NumberFilter(
        field_name="industry_average", lookup_expr="gte"
    )
    max_industry_average = django_filters.NumberFilter(
        field_name="industry_average", lookup_expr="lte"
    )
    min_top_quartile = django_filters.NumberFilter(
        field_name="top_quartile", lookup_expr="gte"
    )
    max_top_quartile = django_filters.NumberFilter(
        field_name="top_quartile", lookup_expr="lte"
    )
    min_bottom_quartile = django_filters.NumberFilter(
        field_name="bottom_quartile", lookup_expr="gte"
    )
    max_bottom_quartile = django_filters.NumberFilter(
        field_name="bottom_quartile", lookup_expr="lte"
    )
    min_our_value = django_filters.NumberFilter(
        field_name="our_value", lookup_expr="gte"
    )
    max_our_value = django_filters.NumberFilter(
        field_name="our_value", lookup_expr="lte"
    )
    min_percentile_rank = django_filters.NumberFilter(
        field_name="percentile_rank", lookup_expr="gte"
    )
    max_percentile_rank = django_filters.NumberFilter(
        field_name="percentile_rank", lookup_expr="lte"
    )
    min_performance_gap = django_filters.NumberFilter(
        field_name="performance_gap", lookup_expr="gte"
    )
    max_performance_gap = django_filters.NumberFilter(
        field_name="performance_gap", lookup_expr="lte"
    )
    min_improvement_potential = django_filters.NumberFilter(
        field_name="improvement_potential", lookup_expr="gte"
    )
    max_improvement_potential = django_filters.NumberFilter(
        field_name="improvement_potential", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    last_updated_after = django_filters.DateTimeFilter(
        field_name="last_updated", lookup_expr="gte"
    )
    last_updated_before = django_filters.DateTimeFilter(
        field_name="last_updated", lookup_expr="lte"
    )

    # Custom filters
    above_average = django_filters.BooleanFilter(method="filter_above_average")
    top_performers = django_filters.BooleanFilter(method="filter_top_performers")
    improvement_opportunities = django_filters.BooleanFilter(
        method="filter_improvement_opportunities"
    )

    class Meta:
        model = Benchmark
        fields = ["benchmark_type", "is_active", "metric_name", "data_source"]

    def filter_above_average(self, queryset, name, value):
        """Filter for benchmarks above industry average."""
        if value:
            return queryset.filter(our_value__gte=models.F("industry_average"))
        return queryset

    def filter_top_performers(self, queryset, name, value):
        """Filter for top performing benchmarks."""
        if value:
            return queryset.filter(percentile_rank__gte=75)
        return queryset

    def filter_improvement_opportunities(self, queryset, name, value):
        """Filter for benchmarks with improvement opportunities."""
        if value:
            return queryset.filter(improvement_potential__gte=10)
        return queryset


class InsightFilter(django_filters.FilterSet):
    """Insight filters."""

    insight_type = django_filters.ChoiceFilter(choices=Insight.INSIGHT_TYPES)
    priority = django_filters.ChoiceFilter(choices=Insight.PRIORITY_LEVELS)
    is_read = django_filters.BooleanFilter()
    is_acknowledged = django_filters.BooleanFilter()
    is_implemented = django_filters.BooleanFilter()
    created_by = django_filters.NumberFilter()
    generated_after = django_filters.DateTimeFilter(
        field_name="generated_at", lookup_expr="gte"
    )
    generated_before = django_filters.DateTimeFilter(
        field_name="generated_at", lookup_expr="lte"
    )
    acknowledged_after = django_filters.DateTimeFilter(
        field_name="acknowledged_at", lookup_expr="gte"
    )
    acknowledged_before = django_filters.DateTimeFilter(
        field_name="acknowledged_at", lookup_expr="lte"
    )
    implemented_after = django_filters.DateTimeFilter(
        field_name="implemented_at", lookup_expr="gte"
    )
    implemented_before = django_filters.DateTimeFilter(
        field_name="implemented_at", lookup_expr="lte"
    )

    # Custom filters
    unread_insights = django_filters.BooleanFilter(method="filter_unread_insights")
    high_priority_insights = django_filters.BooleanFilter(
        method="filter_high_priority_insights"
    )
    actionable_insights = django_filters.BooleanFilter(
        method="filter_actionable_insights"
    )

    class Meta:
        model = Insight
        fields = [
            "insight_type",
            "priority",
            "is_read",
            "is_acknowledged",
            "is_implemented",
            "created_by",
        ]

    def filter_unread_insights(self, queryset, name, value):
        """Filter for unread insights."""
        if value:
            return queryset.filter(is_read=False)
        return queryset

    def filter_high_priority_insights(self, queryset, name, value):
        """Filter for high priority insights."""
        if value:
            return queryset.filter(priority__in=["high", "critical"])
        return queryset

    def filter_actionable_insights(self, queryset, name, value):
        """Filter for actionable insights."""
        if value:
            return queryset.filter(is_implemented=False, is_acknowledged=False)
        return queryset


class DataSourceFilter(django_filters.FilterSet):
    """Data source filters."""

    source_type = django_filters.ChoiceFilter(choices=DataSource.SOURCE_TYPES)
    is_active = django_filters.BooleanFilter()
    is_connected = django_filters.BooleanFilter()
    sync_frequency = django_filters.CharFilter(lookup_expr="icontains")
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    last_sync_after = django_filters.DateTimeFilter(
        field_name="last_sync", lookup_expr="gte"
    )
    last_sync_before = django_filters.DateTimeFilter(
        field_name="last_sync", lookup_expr="lte"
    )

    # Custom filters
    connected_sources = django_filters.BooleanFilter(method="filter_connected_sources")
    recently_synced = django_filters.BooleanFilter(method="filter_recently_synced")
    active_sources = django_filters.BooleanFilter(method="filter_active_sources")

    class Meta:
        model = DataSource
        fields = ["source_type", "is_active", "is_connected"]

    def filter_connected_sources(self, queryset, name, value):
        """Filter for connected data sources."""
        if value:
            return queryset.filter(is_connected=True)
        return queryset

    def filter_recently_synced(self, queryset, name, value):
        """Filter for recently synced data sources."""
        if value:
            seven_days_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(last_sync__gte=seven_days_ago)
        return queryset

    def filter_active_sources(self, queryset, name, value):
        """Filter for active data sources."""
        if value:
            return queryset.filter(is_active=True)
        return queryset
