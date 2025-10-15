"""
Customer Experience URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerJourneyViewSet,
    CustomerPersonaViewSet,
    ProactiveSupportViewSet,
    CustomerHealthScoreViewSet,
    PersonalizationRuleViewSet,
    customer_experience_dashboard,
    customer_experience_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"journeys", CustomerJourneyViewSet)
router.register(r"personas", CustomerPersonaViewSet)
router.register(r"proactive-support", ProactiveSupportViewSet)
router.register(r"health-scores", CustomerHealthScoreViewSet)
router.register(r"personalization-rules", PersonalizationRuleViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path(
        "dashboard/",
        customer_experience_dashboard,
        name="customer_experience_dashboard",
    ),
    path(
        "analytics/",
        customer_experience_analytics,
        name="customer_experience_analytics",
    ),
]
