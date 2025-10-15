"""
Advanced Communication URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunicationChannelViewSet,
    VideoConferenceViewSet,
    CommunicationTemplateViewSet,
    CommunicationLogViewSet,
    advanced_communication_dashboard,
    advanced_communication_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"communication-channels", CommunicationChannelViewSet)
router.register(r"video-conferences", VideoConferenceViewSet)
router.register(r"communication-templates", CommunicationTemplateViewSet)
router.register(r"communication-logs", CommunicationLogViewSet)

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
