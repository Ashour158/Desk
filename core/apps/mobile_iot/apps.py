"""
Mobile & IoT Platform application configuration.
"""

from django.apps import AppConfig


class MobileIotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mobile_iot"
    verbose_name = "Mobile & IoT Platform"
