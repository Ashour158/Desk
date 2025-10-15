"""
Advanced Analytics views.
"""

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CustomReport, Dashboard, KPIBuilder, DataExport, ReportSchedule
from .serializers import (
    CustomReportSerializer,
    DashboardSerializer,
    KPIBuilderSerializer,
    DataExportSerializer,
    ReportScheduleSerializer,
)


class CustomReportViewSet(viewsets.ModelViewSet):
    """ViewSet for custom report management."""

    queryset = CustomReport.objects.all()
    serializer_class = CustomReportSerializer


class DashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for dashboard management."""

    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer


class KPIBuilderViewSet(viewsets.ModelViewSet):
    """ViewSet for KPI builder management."""

    queryset = KPIBuilder.objects.all()
    serializer_class = KPIBuilderSerializer


class DataExportViewSet(viewsets.ModelViewSet):
    """ViewSet for data export management."""

    queryset = DataExport.objects.all()
    serializer_class = DataExportSerializer


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for report schedule management."""

    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer


def advanced_analytics_dashboard(request):
    """Advanced Analytics Dashboard view."""
    context = {
        "total_reports": CustomReport.objects.count(),
        "active_dashboards": Dashboard.objects.filter(is_active=True).count(),
        "kpi_builders": KPIBuilder.objects.count(),
        "data_exports": DataExport.objects.count(),
    }
    return render(request, "advanced_analytics/dashboard.html", context)


def advanced_analytics_analytics(request):
    """Advanced Analytics Analytics view."""
    return render(request, "advanced_analytics/analytics.html")
