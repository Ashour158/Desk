"""
Monitoring application configuration.
"""

from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    """Monitoring application configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoring'
    verbose_name = 'System Monitoring'
    
    def ready(self):
        """Initialize monitoring when app is ready."""
        from . import signals
