"""
Main URL configuration for the helpdesk platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Main Dashboard
    path('', TemplateView.as_view(template_name='dashboard_zoho.html'), name='home'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard_zoho.html'), name='dashboard'),
    
    # Features Dashboard
    path('features/', TemplateView.as_view(template_name='features/dashboard.html'), name='features'),
    path('system/', TemplateView.as_view(template_name='system/dashboard.html'), name='system_dashboard'),
    path('features/comprehensive/', TemplateView.as_view(template_name='features/comprehensive_dashboard.html'), name='features_comprehensive'),
    
    # Settings
    path('settings/', include('apps.settings.urls')),
    
    # Core API endpoints
    path('api/v1/', include('apps.api.urls')),
    
    # Health Check endpoints
    path('health/', include('apps.api.health_urls')),
    
    # Feature Flag API endpoints
    path('api/v1/features/', include('apps.features.urls')),
    
    # Core Features
    path('api/v1/tickets/', include('apps.tickets.urls')),
    path('api/v1/work-orders/', include('apps.field_service.urls')),
    path('api/v1/technicians/', include('apps.field_service.urls')),
    path('api/v1/knowledge-base/', include('apps.knowledge_base.urls')),
    
    # Ticket Pages
    path('tickets/', TemplateView.as_view(template_name='tickets/list_zoho.html'), name='tickets_list'),
    path('tickets/<int:ticket_id>/', TemplateView.as_view(template_name='tickets/detail_zoho.html'), name='ticket_detail'),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/automation/', include('apps.automation.urls')),
    path('api/v1/integrations/', include('apps.integrations.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    
    # Strategic Enhancement APIs
    path('api/v1/ai-ml/', include('apps.ai_ml.urls')),
    path('api/v1/customer-experience/', include('apps.customer_experience.urls')),
    path('api/v1/advanced-analytics/', include('apps.advanced_analytics.urls')),
    path('api/v1/integration-platform/', include('apps.integration_platform.urls')),
    path('api/v1/mobile-iot/', include('apps.mobile_iot.urls')),
    path('api/v1/advanced-security/', include('apps.advanced_security.urls')),
    path('api/v1/advanced-workflow/', include('apps.advanced_workflow.urls')),
    path('api/v1/advanced-communication/', include('apps.advanced_communication.urls')),
    
    # Enhanced Enterprise Features
    path('api/v1/security/', include('apps.security.urls')),
    path('api/v1/i18n/', include('apps.i18n.urls')),
    path('api/v1/customization/', include('apps.customization.urls')),
    path('api/v1/compliance/', include('apps.compliance.urls')),
    
    # Additional Features
    path('api/v1/security-compliance/', include('apps.security_compliance.urls')),
    path('api/v1/workflow-automation/', include('apps.workflow_automation.urls')),
    path('api/v1/communication-platform/', include('apps.communication_platform.urls')),
    
    # User Management
    path('api/v1/users/', include('apps.accounts.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    
    # Reports
    path('reports/', TemplateView.as_view(template_name='reports/dashboard.html'), name='reports'),
    
    # API Documentation
    path('api/docs/', TemplateView.as_view(template_name='api/documentation.html'), name='api_docs'),
    
    # OpenAPI/Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Microservices Status
    path('microservices/', TemplateView.as_view(template_name='microservices/status.html'), name='microservices_status'),
    
    # Health Check
    path('health/', include('apps.api.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)