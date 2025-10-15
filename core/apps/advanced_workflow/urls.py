"""
Advanced Workflow URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkflowTemplateViewSet,
    ProcessAutomationViewSet,
    WorkflowExecutionViewSet,
    WorkflowRuleViewSet,
    advanced_workflow_dashboard,
    advanced_workflow_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"workflow-templates", WorkflowTemplateViewSet)
router.register(r"process-automation", ProcessAutomationViewSet)
router.register(r"workflow-executions", WorkflowExecutionViewSet)
router.register(r"workflow-rules", WorkflowRuleViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path("dashboard/", advanced_workflow_dashboard, name="advanced_workflow_dashboard"),
    path("analytics/", advanced_workflow_analytics, name="advanced_workflow_analytics"),
]
