"""
Enhanced AI & Machine Learning URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    NLPEngineViewSet,
    ComputerVisionSuiteViewSet,
    PredictiveAnalyticsPlatformViewSet,
    AdvancedChatbotViewSet,
    AIPoweredAutomationViewSet,
    AIProcessingJobViewSet,
    AIModelPerformanceViewSet,
)

# Create router for enhanced AI/ML endpoints
router = DefaultRouter()
router.register(r"nlp-engines", NLPEngineViewSet)
router.register(r"vision-suites", ComputerVisionSuiteViewSet)
router.register(r"predictive-analytics", PredictiveAnalyticsPlatformViewSet)
router.register(r"chatbots", AdvancedChatbotViewSet)
router.register(r"ai-automations", AIPoweredAutomationViewSet)
router.register(r"processing-jobs", AIProcessingJobViewSet)
router.register(r"performance-metrics", AIModelPerformanceViewSet)

urlpatterns = [
    path("enhanced/", include(router.urls)),
]
