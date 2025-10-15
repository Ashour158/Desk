"""
Integration Platform app configuration.
"""

from django.apps import AppConfig


class IntegrationPlatformConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.integration_platform"
    verbose_name = "Integration Platform"

    def ready(self):
        import apps.integration_platform.signals
