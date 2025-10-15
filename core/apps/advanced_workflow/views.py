"""
Advanced Workflow views.
"""

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WorkflowTemplate, ProcessAutomation, WorkflowExecution, WorkflowRule
from .serializers import (
    WorkflowTemplateSerializer,
    ProcessAutomationSerializer,
    WorkflowExecutionSerializer,
    WorkflowRuleSerializer,
)


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow template management."""

    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer


class ProcessAutomationViewSet(viewsets.ModelViewSet):
    """ViewSet for process automation management."""

    queryset = ProcessAutomation.objects.all()
    serializer_class = ProcessAutomationSerializer


class WorkflowExecutionViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow execution management."""

    queryset = WorkflowExecution.objects.all()
    serializer_class = WorkflowExecutionSerializer


class WorkflowRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow rule management."""

    queryset = WorkflowRule.objects.all()
    serializer_class = WorkflowRuleSerializer


def advanced_workflow_dashboard(request):
    """Advanced Workflow Dashboard view."""
    context = {
        "total_templates": WorkflowTemplate.objects.count(),
        "active_automations": ProcessAutomation.objects.filter(is_active=True).count(),
        "workflow_executions": WorkflowExecution.objects.count(),
        "workflow_rules": WorkflowRule.objects.count(),
    }
    return render(request, "advanced_workflow/dashboard.html", context)


def advanced_workflow_analytics(request):
    """Advanced Workflow Analytics view."""
    return render(request, "advanced_workflow/analytics.html")
