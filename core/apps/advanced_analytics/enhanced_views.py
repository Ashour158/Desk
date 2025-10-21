"""
Enhanced Advanced Analytics & Business Intelligence views for advanced capabilities.
"""

from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import asyncio
import json

from apps.organizations.utils import get_current_organization
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
from .enhanced_services import (
    EnhancedDataScienceService,
    EnhancedRealTimeAnalyticsService,
    EnhancedReportingService,
    EnhancedBusinessIntelligenceService,
    EnhancedDataGovernanceService,
)
from .serializers import (
    DataSciencePlatformSerializer,
    RealTimeAnalyticsEngineSerializer,
    AdvancedReportingSuiteSerializer,
    BusinessIntelligenceToolsSerializer,
    DataGovernanceSerializer,
    AnalyticsModelSerializer,
    AnalyticsDashboardSerializer,
    AnalyticsReportSerializer,
    AnalyticsAlertSerializer,
)


class BaseAnalyticsViewSet(viewsets.ModelViewSet):
    """Base viewset for Analytics models with organization filtering."""

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        organization = get_current_organization(self.request)
        if organization:
            return self.queryset.filter(organization=organization)
        return self.queryset.none()

    def perform_create(self, serializer):
        organization = get_current_organization(self.request)
        if not organization:
            raise serializers.ValidationError(
                "Organization not found for the current request."
            )
        serializer.save(organization=organization, created_by=self.request.user)


class DataSciencePlatformViewSet(BaseAnalyticsViewSet):
    """Data Science Platform management."""

    queryset = DataSciencePlatform.objects.all()
    serializer_class = DataSciencePlatformSerializer
    search_fields = ["name", "description", "platform_type"]
    filterset_fields = ["platform_type", "is_active", "is_training"]
    ordering_fields = ["name", "created_at", "model_accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def build_ml_model(self, request, pk=None):
        """Build ML model using the platform."""
        platform = self.get_object()
        model_config = request.data.get("model_config", {})

        if not model_config:
            return Response(
                {"error": "Model configuration is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def build():
            data_science_service = EnhancedDataScienceService(platform.organization)
            return await data_science_service.build_ml_model(model_config)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(build())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def perform_statistical_analysis(self, request, pk=None):
        """Perform statistical analysis."""
        platform = self.get_object()
        data = request.data.get("data", {})
        analysis_type = request.data.get("analysis_type", "descriptive")

        if not data:
            return Response(
                {"error": "Data is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def analyze():
            data_science_service = EnhancedDataScienceService(platform.organization)
            return await data_science_service.perform_statistical_analysis(
                data, analysis_type
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyze())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def performance_metrics(self, request, pk=None):
        """Get performance metrics for the platform."""
        platform = self.get_object()

        # Get recent models
        recent_models = AnalyticsModel.objects.filter(
            organization=platform.organization
        ).order_by("-created_at")[:10]

        metrics = {
            "model_accuracy": platform.model_accuracy,
            "training_speed": platform.training_speed,
            "inference_speed": platform.inference_speed,
            "resource_utilization": platform.resource_utilization,
            "total_models": platform.total_models,
            "active_models": platform.active_models,
            "total_predictions": platform.total_predictions,
            "successful_predictions": platform.successful_predictions,
            "recent_models": [
                {
                    "id": str(model.id),
                    "name": model.name,
                    "model_type": model.model_type,
                    "status": model.status,
                    "accuracy": model.accuracy,
                    "created_at": model.created_at.isoformat(),
                }
                for model in recent_models
            ],
        }

        return Response(metrics, status=status.HTTP_200_OK)


class RealTimeAnalyticsEngineViewSet(BaseAnalyticsViewSet):
    """Real-time Analytics Engine management."""

    queryset = RealTimeAnalyticsEngine.objects.all()
    serializer_class = RealTimeAnalyticsEngineSerializer
    search_fields = ["name", "description", "engine_type"]
    filterset_fields = ["engine_type", "is_active", "is_processing"]
    ordering_fields = ["name", "created_at", "processing_latency"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def process_streaming_data(self, request, pk=None):
        """Process streaming data."""
        engine = self.get_object()
        data_stream = request.data.get("data_stream", {})

        if not data_stream:
            return Response(
                {"error": "Data stream is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def process():
            real_time_service = EnhancedRealTimeAnalyticsService(engine.organization)
            return await real_time_service.process_streaming_data(data_stream)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def generate_insights(self, request, pk=None):
        """Generate real-time insights."""
        engine = self.get_object()
        data = request.data.get("data", {})

        if not data:
            return Response(
                {"error": "Data is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def generate():
            real_time_service = EnhancedRealTimeAnalyticsService(engine.organization)
            return await real_time_service.generate_real_time_insights(data)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def performance_metrics(self, request, pk=None):
        """Get performance metrics for the engine."""
        engine = self.get_object()

        metrics = {
            "processing_latency": engine.processing_latency,
            "throughput": engine.throughput,
            "accuracy": engine.accuracy,
            "availability": engine.availability,
            "total_events_processed": engine.total_events_processed,
            "active_streams": engine.active_streams,
            "alerts_generated": engine.alerts_generated,
            "insights_generated": engine.insights_generated,
        }

        return Response(metrics, status=status.HTTP_200_OK)


class AdvancedReportingSuiteViewSet(BaseAnalyticsViewSet):
    """Advanced Reporting Suite management."""

    queryset = AdvancedReportingSuite.objects.all()
    serializer_class = AdvancedReportingSuiteSerializer
    search_fields = ["name", "description", "reporting_type"]
    filterset_fields = ["reporting_type", "is_active", "is_generating"]
    ordering_fields = ["name", "created_at", "report_accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def generate_automated_report(self, request, pk=None):
        """Generate automated report."""
        suite = self.get_object()
        report_config = request.data.get("report_config", {})

        if not report_config:
            return Response(
                {"error": "Report configuration is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def generate():
            reporting_service = EnhancedReportingService(suite.organization)
            return await reporting_service.generate_automated_report(report_config)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def build_interactive_report(self, request, pk=None):
        """Build interactive report."""
        suite = self.get_object()
        builder_config = request.data.get("builder_config", {})

        if not builder_config:
            return Response(
                {"error": "Builder configuration is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def build():
            reporting_service = EnhancedReportingService(suite.organization)
            return await reporting_service.build_interactive_report(builder_config)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(build())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def reporting_metrics(self, request, pk=None):
        """Get reporting metrics."""
        suite = self.get_object()

        # Get recent reports
        recent_reports = AnalyticsReport.objects.filter(
            organization=suite.organization
        ).order_by("-created_at")[:10]

        metrics = {
            "report_generation_time": suite.report_generation_time,
            "report_accuracy": suite.report_accuracy,
            "user_satisfaction": suite.user_satisfaction,
            "delivery_success_rate": suite.delivery_success_rate,
            "total_reports": suite.total_reports,
            "scheduled_reports": suite.scheduled_reports,
            "report_views": suite.report_views,
            "exports_generated": suite.exports_generated,
            "recent_reports": [
                {
                    "id": str(report.id),
                    "name": report.name,
                    "report_type": report.report_type,
                    "generation_time": report.generation_time,
                    "file_size": report.file_size,
                    "created_at": report.created_at.isoformat(),
                }
                for report in recent_reports
            ],
        }

        return Response(metrics, status=status.HTTP_200_OK)


class BusinessIntelligenceToolsViewSet(BaseAnalyticsViewSet):
    """Business Intelligence Tools management."""

    queryset = BusinessIntelligenceTools.objects.all()
    serializer_class = BusinessIntelligenceToolsSerializer
    search_fields = ["name", "description", "bi_type"]
    filterset_fields = ["bi_type", "is_active", "is_updating"]
    ordering_fields = ["name", "created_at", "dashboard_load_time"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def create_executive_dashboard(self, request, pk=None):
        """Create executive dashboard."""
        bi_tools = self.get_object()
        dashboard_config = request.data.get("dashboard_config", {})

        if not dashboard_config:
            return Response(
                {"error": "Dashboard configuration is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def create():
            bi_service = EnhancedBusinessIntelligenceService(bi_tools.organization)
            return await bi_service.create_executive_dashboard(dashboard_config)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(create())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def generate_kpi_scorecard(self, request, pk=None):
        """Generate KPI scorecard."""
        bi_tools = self.get_object()
        kpi_config = request.data.get("kpi_config", {})

        if not kpi_config:
            return Response(
                {"error": "KPI configuration is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def generate():
            bi_service = EnhancedBusinessIntelligenceService(bi_tools.organization)
            return await bi_service.generate_kpi_scorecard(kpi_config)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def bi_metrics(self, request, pk=None):
        """Get BI metrics."""
        bi_tools = self.get_object()

        # Get recent dashboards
        recent_dashboards = AnalyticsDashboard.objects.filter(
            organization=bi_tools.organization
        ).order_by("-created_at")[:10]

        metrics = {
            "dashboard_load_time": bi_tools.dashboard_load_time,
            "data_freshness": bi_tools.data_freshness,
            "user_engagement": bi_tools.user_engagement,
            "decision_impact": bi_tools.decision_impact,
            "total_dashboards": bi_tools.total_dashboards,
            "active_users": bi_tools.active_users,
            "dashboard_views": bi_tools.dashboard_views,
            "kpi_updates": bi_tools.kpi_updates,
            "recent_dashboards": [
                {
                    "id": str(dashboard.id),
                    "name": dashboard.name,
                    "dashboard_type": dashboard.dashboard_type,
                    "load_time": dashboard.load_time,
                    "user_engagement": dashboard.user_engagement,
                    "created_at": dashboard.created_at.isoformat(),
                }
                for dashboard in recent_dashboards
            ],
        }

        return Response(metrics, status=status.HTTP_200_OK)


class DataGovernanceViewSet(BaseAnalyticsViewSet):
    """Data Governance management."""

    queryset = DataGovernance.objects.all()
    serializer_class = DataGovernanceSerializer
    search_fields = ["name", "description", "governance_type"]
    filterset_fields = ["governance_type", "is_active", "is_monitoring"]
    ordering_fields = ["name", "created_at", "data_quality_score"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def assess_data_quality(self, request, pk=None):
        """Assess data quality."""
        governance = self.get_object()
        data_source = request.data.get("data_source")

        if not data_source:
            return Response(
                {"error": "Data source is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def assess():
            governance_service = EnhancedDataGovernanceService(governance.organization)
            return await governance_service.assess_data_quality(data_source)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(assess())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def perform_privacy_assessment(self, request, pk=None):
        """Perform privacy impact assessment."""
        governance = self.get_object()
        data_processing = request.data.get("data_processing", {})

        if not data_processing:
            return Response(
                {"error": "Data processing information is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def assess():
            governance_service = EnhancedDataGovernanceService(governance.organization)
            return await governance_service.perform_privacy_impact_assessment(
                data_processing
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(assess())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def governance_metrics(self, request, pk=None):
        """Get governance metrics."""
        governance = self.get_object()

        metrics = {
            "data_quality_score": governance.data_quality_score,
            "compliance_rate": governance.compliance_rate,
            "policy_adherence": governance.policy_adherence,
            "risk_score": governance.risk_score,
            "total_policies": governance.total_policies,
            "active_monitoring": governance.active_monitoring,
            "compliance_checks": governance.compliance_checks,
            "violations_detected": governance.violations_detected,
        }

        return Response(metrics, status=status.HTTP_200_OK)


class AnalyticsModelViewSet(BaseAnalyticsViewSet):
    """Analytics Model management."""

    queryset = AnalyticsModel.objects.all()
    serializer_class = AnalyticsModelSerializer
    search_fields = ["name", "description", "model_type"]
    filterset_fields = ["model_type", "status", "algorithm"]
    ordering_fields = ["name", "created_at", "accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def deploy_model(self, request, pk=None):
        """Deploy model for production use."""
        model = self.get_object()

        if model.status != "trained":
            return Response(
                {"error": "Model must be trained before deployment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model.status = "deployed"
        model.save()

        return Response(
            {
                "model_id": str(model.id),
                "model_name": model.name,
                "status": model.status,
                "deployment_url": f"/models/{model.id}/predict",
                "api_endpoint": f"/api/v1/models/{model.id}/predict",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def make_prediction(self, request, pk=None):
        """Make prediction using the model."""
        model = self.get_object()
        input_data = request.data.get("input_data", {})

        if not input_data:
            return Response(
                {"error": "Input data is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if model.status != "deployed":
            return Response(
                {"error": "Model must be deployed to make predictions"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Simulate prediction
        prediction = {
            "model_id": str(model.id),
            "prediction": "predicted_value",
            "confidence": 0.85,
            "input_data": input_data,
            "timestamp": timezone.now().isoformat(),
        }

        # Update model statistics
        model.total_predictions += 1
        model.successful_predictions += 1
        model.last_prediction = timezone.now()
        model.save()

        return Response(prediction, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def model_metrics(self, request, pk=None):
        """Get model performance metrics."""
        model = self.get_object()

        metrics = {
            "accuracy": model.accuracy,
            "precision": model.precision,
            "recall": model.recall,
            "f1_score": model.f1_score,
            "auc_score": model.auc_score,
            "total_predictions": model.total_predictions,
            "successful_predictions": model.successful_predictions,
            "failed_predictions": model.failed_predictions,
            "success_rate": model.successful_predictions
            / max(model.total_predictions, 1),
            "last_prediction": (
                model.last_prediction.isoformat() if model.last_prediction else None
            ),
        }

        return Response(metrics, status=status.HTTP_200_OK)


class AnalyticsDashboardViewSet(BaseAnalyticsViewSet):
    """Analytics Dashboard management."""

    queryset = AnalyticsDashboard.objects.all()
    serializer_class = AnalyticsDashboardSerializer
    search_fields = ["name", "description", "dashboard_type"]
    filterset_fields = ["dashboard_type", "is_active", "is_public"]
    ordering_fields = ["name", "created_at", "load_time"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["get"])
    def dashboard_data(self, request, pk=None):
        """Get dashboard data."""
        dashboard = self.get_object()

        # Simulate dashboard data
        dashboard_data = {
            "dashboard_id": str(dashboard.id),
            "dashboard_name": dashboard.name,
            "widgets": dashboard.widgets,
            "data_sources": dashboard.data_sources,
            "refresh_interval": dashboard.refresh_interval,
            "last_updated": timezone.now().isoformat(),
        }

        return Response(dashboard_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def update_widget(self, request, pk=None):
        """Update dashboard widget."""
        dashboard = self.get_object()
        widget_id = request.data.get("widget_id")
        widget_config = request.data.get("widget_config", {})

        if not widget_id:
            return Response(
                {"error": "Widget ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Update widget configuration
        widgets = dashboard.widgets
        for widget in widgets:
            if widget.get("id") == widget_id:
                widget.update(widget_config)
                break

        dashboard.widgets = widgets
        dashboard.save()

        return Response(
            {
                "dashboard_id": str(dashboard.id),
                "widget_id": widget_id,
                "updated": True,
            },
            status=status.HTTP_200_OK,
        )


class AnalyticsReportViewSet(BaseAnalyticsViewSet):
    """Analytics Report management."""

    queryset = AnalyticsReport.objects.all()
    serializer_class = AnalyticsReportSerializer
    search_fields = ["name", "description", "report_type"]
    filterset_fields = ["report_type", "is_active", "is_scheduled"]
    ordering_fields = ["name", "created_at", "generation_time"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def generate_report(self, request, pk=None):
        """Generate report."""
        report = self.get_object()

        # Simulate report generation
        generation_result = {
            "report_id": str(report.id),
            "generation_time": 15.5,
            "file_size": 2.3,
            "file_url": f"/reports/{report.id}/download",
            "format": "PDF",
            "pages": 12,
        }

        # Update report statistics
        report.total_generations += 1
        report.last_generated = timezone.now()
        report.save()

        return Response(generation_result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def download_report(self, request, pk=None):
        """Download report."""
        report = self.get_object()

        # Simulate file download
        return Response(
            {
                "report_id": str(report.id),
                "download_url": f"/reports/{report.id}/download",
                "file_size": report.file_size,
                "format": "PDF",
                "expires_at": (timezone.now() + timedelta(hours=24)).isoformat(),
            },
            status=status.HTTP_200_OK,
        )


class AnalyticsAlertViewSet(BaseAnalyticsViewSet):
    """Analytics Alert management."""

    queryset = AnalyticsAlert.objects.all()
    serializer_class = AnalyticsAlertSerializer
    search_fields = ["name", "description", "alert_type"]
    filterset_fields = ["alert_type", "severity", "is_active", "is_enabled"]
    ordering_fields = ["name", "created_at", "alert_accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def test_alert(self, request, pk=None):
        """Test alert configuration."""
        alert = self.get_object()
        test_data = request.data.get("test_data", {})

        if not test_data:
            return Response(
                {"error": "Test data is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Simulate alert testing
        test_result = {
            "alert_id": str(alert.id),
            "alert_name": alert.name,
            "test_data": test_data,
            "triggered": True,
            "confidence": 0.85,
            "test_timestamp": timezone.now().isoformat(),
        }

        return Response(test_result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def alert_metrics(self, request, pk=None):
        """Get alert performance metrics."""
        alert = self.get_object()

        metrics = {
            "alert_accuracy": alert.alert_accuracy,
            "response_time": alert.response_time,
            "false_positive_rate": alert.false_positive_rate,
            "resolution_time": alert.resolution_time,
            "total_alerts": alert.total_alerts,
            "active_alerts": alert.active_alerts,
            "resolved_alerts": alert.resolved_alerts,
            "last_triggered": (
                alert.last_triggered.isoformat() if alert.last_triggered else None
            ),
        }

        return Response(metrics, status=status.HTTP_200_OK)
