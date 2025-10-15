"""
Health Check URL Configuration
"""

from django.urls import path
from .health_views import (
    health_check,
    detailed_health_check,
    readiness_check,
    liveness_check
)

urlpatterns = [
    # Basic health check
    path('', health_check, name='health-check'),
    path('basic/', health_check, name='health-check-basic'),
    
    # Detailed health check
    path('detailed/', detailed_health_check, name='health-check-detailed'),
    
    # Kubernetes probes
    path('ready/', readiness_check, name='readiness-check'),
    path('live/', liveness_check, name='liveness-check'),
]
