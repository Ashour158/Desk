"""
Advanced Workflow serializers.
"""

from rest_framework import serializers
from .models import WorkflowTemplate, ProcessAutomation, WorkflowExecution, WorkflowRule


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTemplate
        fields = "__all__"


class ProcessAutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessAutomation
        fields = "__all__"


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowExecution
        fields = "__all__"


class WorkflowRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowRule
        fields = "__all__"
