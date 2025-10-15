"""
Communication Platform app configuration.
"""

from django.apps import AppConfig


class CommunicationPlatformConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.communication_platform"
    verbose_name = "Communication Platform"

    def ready(self):
        import apps.communication_platform.signals
