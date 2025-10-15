"""
Workflow Automation app configuration.
"""

from django.apps import AppConfig


class WorkflowAutomationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.workflow_automation"
    verbose_name = "Workflow Automation"

    def ready(self):
        import apps.workflow_automation.signals
