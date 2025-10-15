"""
Feature Flag API Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import json
import logging

from .models import Feature, FeatureCategory, FeatureUsage, FeatureHealth, FeatureConfiguration
from .serializers import FeatureSerializer, FeatureCategorySerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feature_flags(request):
    """
    Get feature flags for the current user
    """
    try:
        user = request.user
        organization = getattr(request, 'organization', None)
        
        # Get feature flags from middleware
        feature_flags = getattr(request, 'feature_flags', {})
        
        # Add additional context
        response_data = {
            'features': feature_flags,
            'user_id': user.id,
            'organization_id': organization.id if organization else None,
            'timestamp': timezone.now().isoformat(),
            'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting feature flags: {e}")
        return Response(
            {'error': 'Failed to get feature flags'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feature_flag(request, flag_name):
    """
    Get a specific feature flag
    """
    try:
        is_enabled = getattr(request, 'is_feature_enabled', lambda x: False)(flag_name)
        
        response_data = {
            'flag': flag_name,
            'enabled': is_enabled,
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting feature flag {flag_name}: {e}")
        return Response(
            {'error': f'Failed to get feature flag {flag_name}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_feature_flag(request, flag_name):
    """
    Update a feature flag (admin only)
    """
    try:
        # Check if user has permission to update feature flags
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        value = request.data.get('value')
        if value is None:
            return Response(
                {'error': 'Value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update feature flag in database
        feature, created = Feature.objects.get_or_create(
            name=flag_name,
            defaults={
                'description': f'Feature flag for {flag_name}',
                'feature_type': 'core',
                'status': 'active' if value else 'inactive',
                'is_global': True,
            }
        )
        
        if not created:
            feature.status = 'active' if value else 'inactive'
            feature.save()
        
        # Clear cache
        cache_key = f"feature_flags_{request.user.id}_{getattr(request, 'organization', None).id if hasattr(request, 'organization') else 'none'}"
        cache.delete(cache_key)
        
        response_data = {
            'flag': flag_name,
            'enabled': value,
            'updated': True,
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating feature flag {flag_name}: {e}")
        return Response(
            {'error': f'Failed to update feature flag {flag_name}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feature_categories(request):
    """
    Get all feature categories
    """
    try:
        categories = FeatureCategory.objects.filter(is_active=True).order_by('order', 'name')
        serializer = FeatureCategorySerializer(categories, many=True)
        
        return Response({
            'categories': serializer.data,
            'count': categories.count(),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting feature categories: {e}")
        return Response(
            {'error': 'Failed to get feature categories'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_features_by_category(request, category_id):
    """
    Get features by category
    """
    try:
        features = Feature.objects.filter(
            category_id=category_id,
            status='active'
        ).order_by('order', 'name')
        
        serializer = FeatureSerializer(features, many=True)
        
        return Response({
            'features': serializer.data,
            'count': features.count(),
            'category_id': category_id,
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting features for category {category_id}: {e}")
        return Response(
            {'error': f'Failed to get features for category {category_id}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feature_usage(request):
    """
    Get feature usage statistics
    """
    try:
        user = request.user
        organization = getattr(request, 'organization', None)
        
        if not organization:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get usage statistics
        usage_stats = FeatureUsage.objects.filter(
            organization=organization
        ).select_related('feature', 'user')
        
        # Aggregate usage data
        usage_data = {}
        for usage in usage_stats:
            feature_name = usage.feature.name
            if feature_name not in usage_data:
                usage_data[feature_name] = {
                    'feature_name': feature_name,
                    'total_access': 0,
                    'unique_users': set(),
                    'last_accessed': None,
                }
            
            usage_data[feature_name]['total_access'] += usage.access_count
            usage_data[feature_name]['unique_users'].add(usage.user.id)
            if not usage_data[feature_name]['last_accessed'] or usage.last_accessed > usage_data[feature_name]['last_accessed']:
                usage_data[feature_name]['last_accessed'] = usage.last_accessed
        
        # Convert sets to counts
        for feature_name, data in usage_data.items():
            data['unique_users'] = len(data['unique_users'])
            data['last_accessed'] = data['last_accessed'].isoformat() if data['last_accessed'] else None
        
        return Response({
            'usage_stats': list(usage_data.values()),
            'total_features': len(usage_data),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting feature usage: {e}")
        return Response(
            {'error': 'Failed to get feature usage'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feature_health(request):
    """
    Get feature health status
    """
    try:
        # Get recent health records
        health_records = FeatureHealth.objects.select_related('feature').order_by('-last_check')[:50]
        
        health_data = {}
        for record in health_records:
            feature_name = record.feature.name
            if feature_name not in health_data:
                health_data[feature_name] = {
                    'feature_name': feature_name,
                    'status': record.status,
                    'response_time': record.response_time,
                    'error_rate': record.error_rate,
                    'last_check': record.last_check.isoformat(),
                    'error_message': record.error_message,
                }
        
        return Response({
            'health_status': list(health_data.values()),
            'total_features': len(health_data),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting feature health: {e}")
        return Response(
            {'error': 'Failed to get feature health'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_feature_flag(request, flag_name):
    """
    Toggle a feature flag
    """
    try:
        # Check if user has permission
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get current state
        is_enabled = getattr(request, 'is_feature_enabled', lambda x: False)(flag_name)
        new_state = not is_enabled
        
        # Update feature flag
        feature, created = Feature.objects.get_or_create(
            name=flag_name,
            defaults={
                'description': f'Feature flag for {flag_name}',
                'feature_type': 'core',
                'status': 'active' if new_state else 'inactive',
                'is_global': True,
            }
        )
        
        if not created:
            feature.status = 'active' if new_state else 'inactive'
            feature.save()
        
        # Clear cache
        cache_key = f"feature_flags_{request.user.id}_{getattr(request, 'organization', None).id if hasattr(request, 'organization') else 'none'}"
        cache.delete(cache_key)
        
        response_data = {
            'flag': flag_name,
            'enabled': new_state,
            'previous_state': is_enabled,
            'toggled': True,
            'timestamp': timezone.now().isoformat(),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error toggling feature flag {flag_name}: {e}")
        return Response(
            {'error': f'Failed to toggle feature flag {flag_name}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feature_configurations(request, flag_name):
    """
    Get feature configurations
    """
    try:
        organization = getattr(request, 'organization', None)
        
        if not organization:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get feature
        try:
            feature = Feature.objects.get(name=flag_name)
        except Feature.DoesNotExist:
            return Response(
                {'error': f'Feature {flag_name} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get configurations
        configurations = FeatureConfiguration.objects.filter(
            feature=feature,
            organization=organization
        )
        
        config_data = {}
        for config in configurations:
            try:
                # Parse configuration value based on type
                if config.config_type == 'boolean':
                    value = config.config_value.lower() in ('true', '1', 'yes', 'on')
                elif config.config_type == 'integer':
                    value = int(config.config_value)
                elif config.config_type == 'json':
                    value = json.loads(config.config_value)
                else:
                    value = config.config_value
                
                config_data[config.config_key] = {
                    'value': value,
                    'type': config.config_type,
                    'required': config.is_required,
                    'encrypted': config.is_encrypted,
                }
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Invalid configuration value for {config.config_key}: {e}")
                continue
        
        return Response({
            'feature': flag_name,
            'configurations': config_data,
            'count': len(config_data),
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting feature configurations for {flag_name}: {e}")
        return Response(
            {'error': f'Failed to get feature configurations for {flag_name}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
