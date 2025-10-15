"""
AI/ML app configuration.
"""

from django.apps import AppConfig


class AiMlConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai_ml"
    verbose_name = "AI & Machine Learning"

    def ready(self):
        import apps.ai_ml.signals
