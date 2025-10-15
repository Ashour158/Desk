"""
AI & Machine Learning views.
"""

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    TicketCategorization,
    SentimentAnalysis,
    Chatbot,
    AIModel,
    AIProcessingJob,
)
from .serializers import (
    TicketCategorizationSerializer,
    SentimentAnalysisSerializer,
    ChatbotSerializer,
    AIModelSerializer,
    AIProcessingJobSerializer,
)


class TicketCategorizationViewSet(viewsets.ModelViewSet):
    """ViewSet for ticket categorization."""

    queryset = TicketCategorization.objects.all()
    serializer_class = TicketCategorizationSerializer

    @action(detail=False, methods=["post"])
    def categorize_ticket(self, request):
        """Categorize a ticket using AI."""
        # Implementation for AI categorization
        return Response({"category": "Technical", "confidence": 0.95})


class SentimentAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for sentiment analysis."""

    queryset = SentimentAnalysis.objects.all()
    serializer_class = SentimentAnalysisSerializer


class ChatbotViewSet(viewsets.ModelViewSet):
    """ViewSet for chatbot management."""

    queryset = Chatbot.objects.all()
    serializer_class = ChatbotSerializer


class AIModelViewSet(viewsets.ModelViewSet):
    """ViewSet for AI model management."""

    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer


class AIProcessingJobViewSet(viewsets.ModelViewSet):
    """ViewSet for AI processing jobs."""

    queryset = AIProcessingJob.objects.all()
    serializer_class = AIProcessingJobSerializer


def ai_ml_dashboard(request):
    """AI & ML Dashboard view."""
    context = {
        "total_models": AIModel.objects.count(),
        "active_jobs": AIProcessingJob.objects.filter(status="running").count(),
        "total_categorizations": TicketCategorization.objects.count(),
        "sentiment_analyses": SentimentAnalysis.objects.count(),
    }
    return render(request, "ai_ml/dashboard.html", context)


def ai_ml_analytics(request):
    """AI & ML Analytics view."""
    return render(request, "ai_ml/analytics.html")
