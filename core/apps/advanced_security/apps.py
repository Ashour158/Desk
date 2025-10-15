"""
Advanced Security & Compliance Suite application configuration.
"""

from django.apps import AppConfig


class AdvancedSecurityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.apps.advanced_security"
    verbose_name = "Advanced Security & Compliance Suite"
