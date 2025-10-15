"""
Settings URL configuration.
"""

from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    # Settings Dashboard
    path(
        "",
        TemplateView.as_view(template_name="settings/dashboard.html"),
        name="settings_dashboard",
    ),
    # General Settings
    path(
        "general/",
        TemplateView.as_view(template_name="settings/general.html"),
        name="settings_general",
    ),
    # Security Settings
    path(
        "security/",
        TemplateView.as_view(template_name="settings/security.html"),
        name="settings_security",
    ),
    # Integration Settings
    path(
        "integrations/",
        TemplateView.as_view(template_name="settings/integrations.html"),
        name="settings_integrations",
    ),
    # Notification Settings
    path(
        "notifications/",
        TemplateView.as_view(template_name="settings/notifications.html"),
        name="settings_notifications",
    ),
    # Automation Settings
    path(
        "automation/",
        TemplateView.as_view(template_name="settings/automation.html"),
        name="settings_automation",
    ),
    # AI & ML Settings
    path(
        "ai-ml/",
        TemplateView.as_view(template_name="settings/ai_ml.html"),
        name="settings_ai_ml",
    ),
    # Analytics Settings
    path(
        "analytics/",
        TemplateView.as_view(template_name="settings/analytics.html"),
        name="settings_analytics",
    ),
    # Mobile & IoT Settings
    path(
        "mobile-iot/",
        TemplateView.as_view(template_name="settings/mobile_iot.html"),
        name="settings_mobile_iot",
    ),
]
