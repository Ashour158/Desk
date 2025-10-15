"""
Enhanced Advanced Communication Platform URLs for advanced capabilities.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    UnifiedCommunicationHubViewSet,
    VideoAudioFeaturesViewSet,
    AIPoweredCommunicationViewSet,
    SocialMediaManagementViewSet,
    CommunicationIntelligenceViewSet,
    CommunicationSessionViewSet,
    CommunicationMessageViewSet,
    CommunicationAnalyticViewSet,
    CommunicationTemplateViewSet,
    advanced_communication_dashboard,
    advanced_communication_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"unified-communication-hubs", UnifiedCommunicationHubViewSet)
router.register(r"video-audio-features", VideoAudioFeaturesViewSet)
router.register(r"ai-powered-communications", AIPoweredCommunicationViewSet)
router.register(r"social-media-managements", SocialMediaManagementViewSet)
router.register(r"communication-intelligences", CommunicationIntelligenceViewSet)
router.register(r"communication-sessions", CommunicationSessionViewSet)
router.register(r"communication-messages", CommunicationMessageViewSet)
router.register(r"communication-analytics", CommunicationAnalyticViewSet)
router.register(r"communication-templates", CommunicationTemplateViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path(
        "dashboard/",
        advanced_communication_dashboard,
        name="advanced_communication_dashboard",
    ),
    path(
        "analytics/",
        advanced_communication_analytics,
        name="advanced_communication_analytics",
    ),
]
