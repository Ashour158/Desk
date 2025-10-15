"""
Advanced Analytics URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomReportViewSet,
    DashboardViewSet,
    KPIBuilderViewSet,
    DataExportViewSet,
    ReportScheduleViewSet,
    advanced_analytics_dashboard,
    advanced_analytics_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"reports", CustomReportViewSet)
router.register(r"dashboards", DashboardViewSet)
router.register(r"kpi-builders", KPIBuilderViewSet)
router.register(r"data-exports", DataExportViewSet)
router.register(r"report-schedules", ReportScheduleViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path(
        "dashboard/", advanced_analytics_dashboard, name="advanced_analytics_dashboard"
    ),
    path(
        "analytics/", advanced_analytics_analytics, name="advanced_analytics_analytics"
    ),
]
