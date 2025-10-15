"""
Security & Compliance app configuration.
"""

from django.apps import AppConfig


class SecurityComplianceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.security_compliance"
    verbose_name = "Security & Compliance"

    def ready(self):
        import apps.security_compliance.signals
