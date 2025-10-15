"""
AI & Machine Learning URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketCategorizationViewSet,
    SentimentAnalysisViewSet,
    ChatbotViewSet,
    AIModelViewSet,
    AIProcessingJobViewSet,
    ai_ml_dashboard,
    ai_ml_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"categorization", TicketCategorizationViewSet)
router.register(r"sentiment", SentimentAnalysisViewSet)
router.register(r"chatbot", ChatbotViewSet)
router.register(r"models", AIModelViewSet)
router.register(r"processing-jobs", AIProcessingJobViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path("dashboard/", ai_ml_dashboard, name="ai_ml_dashboard"),
    path("analytics/", ai_ml_analytics, name="ai_ml_analytics"),
]
