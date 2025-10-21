"""
Enhanced AI & Machine Learning views for advanced capabilities.
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
    NLPEngine,
    ComputerVisionSuite,
    PredictiveAnalyticsPlatform,
    AdvancedChatbot,
    AIPoweredAutomation,
    AIProcessingJob,
    AIModelPerformance,
)
from .enhanced_services import (
    EnhancedNLPService,
    EnhancedComputerVisionService,
    EnhancedPredictiveAnalyticsService,
    EnhancedChatbotService,
    EnhancedAIAutomationService,
)
from .serializers import (
    NLPEngineSerializer,
    ComputerVisionSuiteSerializer,
    PredictiveAnalyticsPlatformSerializer,
    AdvancedChatbotSerializer,
    AIPoweredAutomationSerializer,
    AIProcessingJobSerializer,
    AIModelPerformanceSerializer,
)


class BaseAIViewSet(viewsets.ModelViewSet):
    """Base viewset for AI models with organization filtering."""

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


class NLPEngineViewSet(BaseAIViewSet):
    """NLP Engine management."""

    queryset = NLPEngine.objects.all()
    serializer_class = NLPEngineSerializer
    search_fields = ["name", "description", "engine_type"]
    filterset_fields = ["engine_type", "is_active", "language_codes"]
    ordering_fields = ["name", "created_at", "accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def process_text(self, request, pk=None):
        """Process text using the NLP engine."""
        engine = self.get_object()
        text = request.data.get("text")
        language = request.data.get("language", "en")

        if not text:
            return Response(
                {"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def process():
            nlp_service = EnhancedNLPService(engine.organization)
            return await nlp_service.process_text(text, engine.engine_type, language)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def train(self, request, pk=None):
        """Train the NLP engine."""
        engine = self.get_object()
        training_data = request.data.get("training_data", [])

        if not training_data:
            return Response(
                {"error": "Training data is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update engine status
        engine.is_training = True
        engine.save()

        # Simulate training process
        # In production, this would trigger actual ML training
        return Response(
            {
                "message": "Training started",
                "training_data_size": len(training_data),
                "estimated_time": "30 minutes",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def performance_metrics(self, request, pk=None):
        """Get performance metrics for the NLP engine."""
        engine = self.get_object()

        # Get recent performance data
        recent_performance = AIModelPerformance.objects.filter(
            organization=engine.organization,
            model_name=engine.name,
            model_type=engine.engine_type,
        ).order_by("-recorded_at")[:10]

        metrics = {
            "current_accuracy": engine.accuracy,
            "current_precision": engine.precision,
            "current_recall": engine.recall,
            "current_f1_score": engine.f1_score,
            "recent_performance": [
                {
                    "date": perf.recorded_at.isoformat(),
                    "accuracy": perf.accuracy,
                    "precision": perf.precision,
                    "recall": perf.recall,
                    "f1_score": perf.f1_score,
                }
                for perf in recent_performance
            ],
        }

        return Response(metrics, status=status.HTTP_200_OK)


class ComputerVisionSuiteViewSet(BaseAIViewSet):
    """Computer Vision Suite management."""

    queryset = ComputerVisionSuite.objects.all()
    serializer_class = ComputerVisionSuiteSerializer
    search_fields = ["name", "description", "vision_type"]
    filterset_fields = ["vision_type", "is_active", "input_formats"]
    ordering_fields = ["name", "created_at", "accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def process_image(self, request, pk=None):
        """Process image using the vision suite."""
        suite = self.get_object()
        image_url = request.data.get("image_url")

        if not image_url:
            return Response(
                {"error": "Image URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def process():
            vision_service = EnhancedComputerVisionService(suite.organization)
            return await vision_service.process_image(image_url, suite.vision_type)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def batch_process(self, request, pk=None):
        """Process multiple images in batch."""
        suite = self.get_object()
        image_urls = request.data.get("image_urls", [])

        if not image_urls:
            return Response(
                {"error": "Image URLs are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Process images in batch
        results = []
        for image_url in image_urls:

            async def process():
                vision_service = EnhancedComputerVisionService(suite.organization)
                return await vision_service.process_image(image_url, suite.vision_type)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(process())
            loop.close()

            results.append({"image_url": image_url, "result": result})

        return Response(
            {
                "batch_results": results,
                "total_processed": len(image_urls),
                "successful": len(
                    [r for r in results if r["result"].get("error") is None]
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def performance_metrics(self, request, pk=None):
        """Get performance metrics for the vision suite."""
        suite = self.get_object()

        # Get recent performance data
        recent_performance = AIModelPerformance.objects.filter(
            organization=suite.organization,
            model_name=suite.name,
            model_type=suite.vision_type,
        ).order_by("-recorded_at")[:10]

        metrics = {
            "current_accuracy": suite.accuracy,
            "current_processing_speed": suite.processing_speed,
            "current_memory_usage": suite.memory_usage,
            "recent_performance": [
                {
                    "date": perf.recorded_at.isoformat(),
                    "accuracy": perf.accuracy,
                    "processing_time": perf.processing_time,
                    "memory_usage": perf.memory_usage,
                }
                for perf in recent_performance
            ],
        }

        return Response(metrics, status=status.HTTP_200_OK)


class PredictiveAnalyticsPlatformViewSet(BaseAIViewSet):
    """Predictive Analytics Platform management."""

    queryset = PredictiveAnalyticsPlatform.objects.all()
    serializer_class = PredictiveAnalyticsPlatformSerializer
    search_fields = ["name", "description", "analytics_type"]
    filterset_fields = ["analytics_type", "is_active", "algorithm"]
    ordering_fields = ["name", "created_at", "accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def generate_prediction(self, request, pk=None):
        """Generate prediction using the analytics platform."""
        platform = self.get_object()
        input_data = request.data.get("input_data", {})

        if not input_data:
            return Response(
                {"error": "Input data is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def process():
            analytics_service = EnhancedPredictiveAnalyticsService(
                platform.organization
            )
            return await analytics_service.generate_prediction(
                platform.analytics_type, input_data
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def train_model(self, request, pk=None):
        """Train the predictive analytics model."""
        platform = self.get_object()
        training_data = request.data.get("training_data", [])

        if not training_data:
            return Response(
                {"error": "Training data is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update platform status
        platform.is_training = True
        platform.training_data_size = len(training_data)
        platform.save()

        # Simulate training process
        return Response(
            {
                "message": "Model training started",
                "training_data_size": len(training_data),
                "estimated_time": "2 hours",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def prediction_history(self, request, pk=None):
        """Get prediction history for the platform."""
        platform = self.get_object()

        # Get recent predictions
        recent_predictions = AIProcessingJob.objects.filter(
            organization=platform.organization,
            job_type="prediction",
            ai_model_id=str(platform.id),
        ).order_by("-created_at")[:20]

        predictions = []
        for job in recent_predictions:
            predictions.append(
                {
                    "id": str(job.id),
                    "created_at": job.created_at.isoformat(),
                    "status": job.status,
                    "input_data": job.input_data,
                    "output_data": job.output_data,
                    "confidence_score": job.confidence_score,
                    "processing_duration": job.processing_duration,
                }
            )

        return Response(
            {"predictions": predictions, "total_predictions": len(predictions)},
            status=status.HTTP_200_OK,
        )


class AdvancedChatbotViewSet(BaseAIViewSet):
    """Advanced Chatbot management."""

    queryset = AdvancedChatbot.objects.all()
    serializer_class = AdvancedChatbotSerializer
    search_fields = ["name", "description", "chatbot_type"]
    filterset_fields = ["chatbot_type", "is_active", "language_codes"]
    ordering_fields = ["name", "created_at", "response_accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def chat(self, request, pk=None):
        """Chat with the chatbot."""
        chatbot = self.get_object()
        message = request.data.get("message")
        context = request.data.get("context", [])

        if not message:
            return Response(
                {"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def process():
            chatbot_service = EnhancedChatbotService(chatbot.organization)
            return await chatbot_service.generate_response(
                message, context, str(chatbot.id)
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def train(self, request, pk=None):
        """Train the chatbot."""
        chatbot = self.get_object()
        training_data = request.data.get("training_data", [])

        if not training_data:
            return Response(
                {"error": "Training data is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update chatbot status
        chatbot.is_training = True
        chatbot.save()

        # Simulate training process
        return Response(
            {
                "message": "Chatbot training started",
                "training_data_size": len(training_data),
                "estimated_time": "1 hour",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def conversation_stats(self, request, pk=None):
        """Get conversation statistics for the chatbot."""
        chatbot = self.get_object()

        # Get recent conversations
        recent_conversations = AIProcessingJob.objects.filter(
            organization=chatbot.organization,
            job_type="chatbot_response",
            ai_model_id=str(chatbot.id),
        ).order_by("-created_at")[:100]

        stats = {
            "total_conversations": chatbot.total_conversations,
            "successful_resolutions": chatbot.successful_resolutions,
            "escalations_to_human": chatbot.escalations_to_human,
            "average_response_time": chatbot.average_response_time,
            "response_accuracy": chatbot.response_accuracy,
            "user_satisfaction": chatbot.user_satisfaction,
            "resolution_rate": chatbot.resolution_rate,
            "escalation_rate": chatbot.escalation_rate,
            "recent_conversations": [
                {
                    "id": str(job.id),
                    "created_at": job.created_at.isoformat(),
                    "status": job.status,
                    "confidence_score": job.confidence_score,
                    "processing_duration": job.processing_duration,
                }
                for job in recent_conversations
            ],
        }

        return Response(stats, status=status.HTTP_200_OK)


class AIPoweredAutomationViewSet(BaseAIViewSet):
    """AI-Powered Automation management."""

    queryset = AIPoweredAutomation.objects.all()
    serializer_class = AIPoweredAutomationSerializer
    search_fields = ["name", "description", "automation_type"]
    filterset_fields = ["automation_type", "is_active", "execution_frequency"]
    ordering_fields = ["name", "created_at", "success_rate"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        """Execute the AI automation."""
        automation = self.get_object()
        trigger_data = request.data.get("trigger_data", {})

        if not trigger_data:
            return Response(
                {"error": "Trigger data is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def process():
            automation_service = EnhancedAIAutomationService(automation.organization)
            return await automation_service.execute_automation(
                str(automation.id), trigger_data
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def schedule_execution(self, request, pk=None):
        """Schedule automation execution."""
        automation = self.get_object()
        schedule_time = request.data.get("schedule_time")
        trigger_data = request.data.get("trigger_data", {})

        if not schedule_time:
            return Response(
                {"error": "Schedule time is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Schedule the automation
        # In production, this would use Celery or similar task scheduler
        return Response(
            {
                "message": "Automation scheduled",
                "schedule_time": schedule_time,
                "automation_id": str(automation.id),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def execution_history(self, request, pk=None):
        """Get execution history for the automation."""
        automation = self.get_object()

        # Get recent executions
        recent_executions = AIProcessingJob.objects.filter(
            organization=automation.organization,
            job_type="automation_execution",
            ai_model_id=str(automation.id),
        ).order_by("-created_at")[:20]

        executions = []
        for job in recent_executions:
            executions.append(
                {
                    "id": str(job.id),
                    "created_at": job.created_at.isoformat(),
                    "status": job.status,
                    "trigger_data": job.input_data,
                    "result": job.output_data,
                    "processing_duration": job.processing_duration,
                }
            )

        return Response(
            {
                "executions": executions,
                "total_executions": automation.total_executions,
                "successful_executions": automation.successful_executions,
                "failed_executions": automation.failed_executions,
                "success_rate": automation.success_rate,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def performance_metrics(self, request, pk=None):
        """Get performance metrics for the automation."""
        automation = self.get_object()

        # Get recent performance data
        recent_performance = AIModelPerformance.objects.filter(
            organization=automation.organization,
            model_name=automation.name,
            model_type=automation.automation_type,
        ).order_by("-recorded_at")[:10]

        metrics = {
            "current_success_rate": automation.success_rate,
            "current_average_execution_time": automation.average_execution_time,
            "current_cost_savings": float(automation.cost_savings),
            "current_efficiency_improvement": automation.efficiency_improvement,
            "recent_performance": [
                {
                    "date": perf.recorded_at.isoformat(),
                    "accuracy": perf.accuracy,
                    "processing_time": perf.processing_time,
                    "memory_usage": perf.memory_usage,
                }
                for perf in recent_performance
            ],
        }

        return Response(metrics, status=status.HTTP_200_OK)


class AIProcessingJobViewSet(BaseAIViewSet):
    """AI Processing Job management."""

    queryset = AIProcessingJob.objects.all()
    serializer_class = AIProcessingJobSerializer
    search_fields = ["job_type", "status"]
    filterset_fields = ["job_type", "status", "created_at"]
    ordering_fields = ["created_at", "processing_duration", "confidence_score"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        """Get job status."""
        job = self.get_object()

        return Response(
            {
                "id": str(job.id),
                "status": job.status,
                "job_type": job.job_type,
                "created_at": job.created_at.isoformat(),
                "processing_started": (
                    job.processing_started.isoformat()
                    if job.processing_started
                    else None
                ),
                "processing_completed": (
                    job.processing_completed.isoformat()
                    if job.processing_completed
                    else None
                ),
                "processing_duration": job.processing_duration,
                "confidence_score": job.confidence_score,
                "error_message": job.error_message,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel the job."""
        job = self.get_object()

        if job.status in ["completed", "failed", "cancelled"]:
            return Response(
                {"error": "Job cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST
            )

        job.status = "cancelled"
        job.save()

        return Response({"message": "Job cancelled"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def results(self, request, pk=None):
        """Get job results."""
        job = self.get_object()

        if job.status != "completed":
            return Response(
                {"error": "Job not completed"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "id": str(job.id),
                "output_data": job.output_data,
                "output_files": job.output_files,
                "confidence_score": job.confidence_score,
                "processing_duration": job.processing_duration,
            },
            status=status.HTTP_200_OK,
        )


class AIModelPerformanceViewSet(BaseAIViewSet):
    """AI Model Performance management."""

    queryset = AIModelPerformance.objects.all()
    serializer_class = AIModelPerformanceSerializer
    search_fields = ["model_name", "model_type"]
    filterset_fields = ["model_type", "recorded_at"]
    ordering_fields = ["recorded_at", "accuracy", "processing_time"]
    ordering = ["-recorded_at"]

    @action(detail=False, methods=["get"])
    def performance_summary(self, request):
        """Get performance summary for all models."""
        organization = get_current_organization(request)
        if not organization:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get performance data for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_performance = AIModelPerformance.objects.filter(
            organization=organization, recorded_at__gte=thirty_days_ago
        )

        # Calculate summary statistics
        summary = {
            "total_models": recent_performance.values("model_name").distinct().count(),
            "average_accuracy": recent_performance.aggregate(
                avg_accuracy=Avg("accuracy")
            )["avg_accuracy"]
            or 0,
            "average_processing_time": recent_performance.aggregate(
                avg_time=Avg("processing_time")
            )["avg_time"]
            or 0,
            "total_predictions": recent_performance.aggregate(
                total=Count("total_predictions")
            )["total"]
            or 0,
            "successful_predictions": recent_performance.aggregate(
                successful=Count("successful_predictions")
            )["successful"]
            or 0,
            "model_performance": [],
        }

        # Get performance by model
        for model_name in recent_performance.values_list(
            "model_name", flat=True
        ).distinct():
            model_perf = (
                recent_performance.filter(model_name=model_name)
                .order_by("-recorded_at")
                .first()
            )
            if model_perf:
                summary["model_performance"].append(
                    {
                        "model_name": model_name,
                        "model_type": model_perf.model_type,
                        "accuracy": model_perf.accuracy,
                        "processing_time": model_perf.processing_time,
                        "memory_usage": model_perf.memory_usage,
                        "total_predictions": model_perf.total_predictions,
                        "successful_predictions": model_perf.successful_predictions,
                        "last_updated": model_perf.recorded_at.isoformat(),
                    }
                )

        return Response(summary, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def performance_trends(self, request):
        """Get performance trends over time."""
        organization = get_current_organization(request)
        if not organization:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get performance data for the last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_performance = AIModelPerformance.objects.filter(
            organization=organization, recorded_at__gte=seven_days_ago
        ).order_by("recorded_at")

        # Group by date
        trends = {}
        for perf in recent_performance:
            date_key = perf.recorded_at.date().isoformat()
            if date_key not in trends:
                trends[date_key] = {
                    "date": date_key,
                    "models": [],
                    "average_accuracy": 0,
                    "average_processing_time": 0,
                    "total_predictions": 0,
                }

            trends[date_key]["models"].append(
                {
                    "model_name": perf.model_name,
                    "accuracy": perf.accuracy,
                    "processing_time": perf.processing_time,
                }
            )

        # Calculate daily averages
        for date_key, data in trends.items():
            if data["models"]:
                data["average_accuracy"] = sum(
                    m["accuracy"] for m in data["models"]
                ) / len(data["models"])
                data["average_processing_time"] = sum(
                    m["processing_time"] for m in data["models"]
                ) / len(data["models"])
                data["total_predictions"] = sum(
                    perf.total_predictions
                    for perf in recent_performance.filter(
                        recorded_at__date=perf.recorded_at.date()
                    )
                )

        return Response(
            {
                "trends": list(trends.values()),
                "period": "7 days",
                "total_data_points": len(recent_performance),
            },
            status=status.HTTP_200_OK,
        )
