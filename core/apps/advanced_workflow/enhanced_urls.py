"""
Enhanced Advanced Workflow & Automation Platform URLs for advanced capabilities.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    IntelligentProcessAutomationViewSet,
    WorkflowEngineViewSet,
    ProcessIntelligenceViewSet,
    AutomationMarketplaceViewSet,
    IntegrationAutomationViewSet,
    WorkflowTemplateViewSet,
    WorkflowExecutionViewSet,
    ProcessMetricViewSet,
    AutomationRuleViewSet,
    advanced_workflow_dashboard,
    advanced_workflow_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"intelligent-process-automations", IntelligentProcessAutomationViewSet)
router.register(r"workflow-engines", WorkflowEngineViewSet)
router.register(r"process-intelligences", ProcessIntelligenceViewSet)
router.register(r"automation-marketplaces", AutomationMarketplaceViewSet)
router.register(r"integration-automations", IntegrationAutomationViewSet)
router.register(r"workflow-templates", WorkflowTemplateViewSet)
router.register(r"workflow-executions", WorkflowExecutionViewSet)
router.register(r"process-metrics", ProcessMetricViewSet)
router.register(r"automation-rules", AutomationRuleViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path("dashboard/", advanced_workflow_dashboard, name="advanced_workflow_dashboard"),
    path("analytics/", advanced_workflow_analytics, name="advanced_workflow_analytics"),
]
