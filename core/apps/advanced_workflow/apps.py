"""
Advanced Workflow & Automation Platform application configuration.
"""

from django.apps import AppConfig


class AdvancedWorkflowConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.apps.advanced_workflow"
    verbose_name = "Advanced Workflow & Automation Platform"
