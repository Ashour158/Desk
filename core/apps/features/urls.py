"""
Feature Flag URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    get_feature_flags, get_feature_flag, update_feature_flag,
    get_feature_categories, get_features_by_category, get_feature_usage,
    get_feature_health, toggle_feature_flag, get_feature_configurations
)

# Create router for feature management
router = DefaultRouter()

urlpatterns = [
    # Feature Flag Endpoints
    path('flags/', get_feature_flags, name='feature-flags'),
    path('flags/<str:flag_name>/', get_feature_flag, name='feature-flag-detail'),
    path('flags/<str:flag_name>/update/', update_feature_flag, name='feature-flag-update'),
    path('flags/<str:flag_name>/toggle/', toggle_feature_flag, name='feature-flag-toggle'),
    path('flags/<str:flag_name>/configurations/', get_feature_configurations, name='feature-flag-configurations'),
    
    # Feature Management Endpoints
    path('categories/', get_feature_categories, name='feature-categories'),
    path('categories/<int:category_id>/features/', get_features_by_category, name='features-by-category'),
    
    # Analytics Endpoints
    path('usage/', get_feature_usage, name='feature-usage'),
    path('health/', get_feature_health, name='feature-health'),
    
    # Include router URLs
    path('', include(router.urls)),
]
