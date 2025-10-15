"""
Advanced Analytics app configuration.
"""

from django.apps import AppConfig


class AdvancedAnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.advanced_analytics"
    verbose_name = "Advanced Analytics & BI"

    def ready(self):
        import apps.advanced_analytics.signals
