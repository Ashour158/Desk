"""
Enhanced Customer Experience URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    CustomerIntelligenceViewSet,
    HyperPersonalizationEngineViewSet,
    CustomerSuccessManagementViewSet,
    AdvancedFeedbackSystemViewSet,
    CustomerAdvocacyPlatformViewSet,
    CustomerInsightViewSet,
    PersonalizationRuleViewSet,
    CustomerSegmentViewSet,
    CustomerTouchpointViewSet,
)

# Create router for enhanced Customer Experience endpoints
router = DefaultRouter()
router.register(r"customer-intelligence", CustomerIntelligenceViewSet)
router.register(r"personalization-engines", HyperPersonalizationEngineViewSet)
router.register(r"success-management", CustomerSuccessManagementViewSet)
router.register(r"feedback-systems", AdvancedFeedbackSystemViewSet)
router.register(r"advocacy-platforms", CustomerAdvocacyPlatformViewSet)
router.register(r"customer-insights", CustomerInsightViewSet)
router.register(r"personalization-rules", PersonalizationRuleViewSet)
router.register(r"customer-segments", CustomerSegmentViewSet)
router.register(r"customer-touchpoints", CustomerTouchpointViewSet)

urlpatterns = [
    path("enhanced/", include(router.urls)),
]
