"""
Customer Experience app configuration.
"""

from django.apps import AppConfig


class CustomerExperienceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customer_experience"
    verbose_name = "Customer Experience"

    def ready(self):
        import apps.customer_experience.signals
