"""
Advanced Communication Platform application configuration.
"""

from django.apps import AppConfig


class AdvancedCommunicationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.apps.advanced_communication"
    verbose_name = "Advanced Communication Platform"
