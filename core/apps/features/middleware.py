"""
Feature Flag Middleware for Django
Provides feature flags to request context
"""

import json
import logging
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from apps.features.models import Feature, FeatureConfiguration
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


class FeatureFlagMiddleware(MiddlewareMixin):
    """
    Middleware to add feature flags to request context
    """
    
    def process_request(self, request):
        """
        Add feature flags to request object
        """
        try:
            # Get user and organization
            user = getattr(request, 'user', None)
            organization = self._get_organization(request, user)
            
            # Get feature flags
            feature_flags = self._get_feature_flags(user, organization)
            
            # Add to request
            request.feature_flags = feature_flags
            request.is_feature_enabled = self._create_feature_checker(feature_flags)
            
            logger.debug(f"Feature flags loaded for user {user}: {len(feature_flags)} flags")
            
        except Exception as e:
            logger.error(f"Error loading feature flags: {e}")
            # Set default empty flags on error
            request.feature_flags = {}
            request.is_feature_enabled = lambda flag: False
    
    def _get_organization(self, request, user):
        """
        Get organization from request or user
        """
        if hasattr(request, 'organization'):
            return request.organization
        
        if user and hasattr(user, 'organization'):
            return user.organization
        
        # Try to get from session
        organization_id = request.session.get('organization_id')
        if organization_id:
            try:
                return Organization.objects.get(id=organization_id)
            except Organization.DoesNotExist:
                pass
        
        return None
    
    def _get_feature_flags(self, user, organization):
        """
        Get feature flags for user and organization
        """
        cache_key = f"feature_flags_{user.id if user else 'anonymous'}_{organization.id if organization else 'none'}"
        
        # Try to get from cache first
        cached_flags = cache.get(cache_key)
        if cached_flags:
            return cached_flags
        
        # Build feature flags
        feature_flags = {}
        
        # Get global features with optimized queries
        global_features = Feature.objects.filter(
            is_global=True,
            status='active'
        ).select_related('category').prefetch_related('permissions', 'configurations')
        
        for feature in global_features:
            feature_flags[feature.name.upper()] = True
        
        # Get organization-specific features with optimized queries
        if organization:
            org_features = Feature.objects.filter(
                organization=organization,
                status='active'
            ).select_related('category').prefetch_related('permissions', 'configurations')
            
            for feature in org_features:
                feature_flags[feature.name.upper()] = True
        
        # Get feature configurations
        if organization:
            configurations = FeatureConfiguration.objects.filter(
                organization=organization
            ).select_related('feature')
            
            for config in configurations:
                flag_name = f"{config.feature.name.upper()}_{config.config_key.upper()}"
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
                    
                    feature_flags[flag_name] = value
                except (ValueError, json.JSONDecodeError) as e:
                    logger.warning(f"Invalid configuration value for {flag_name}: {e}")
                    continue
        
        # Add environment-specific flags
        env_flags = getattr(settings, 'FEATURE_FLAGS', {})
        feature_flags.update(env_flags)
        
        # Cache the results for 5 minutes
        cache.set(cache_key, feature_flags, 300)
        
        return feature_flags
    
    def _create_feature_checker(self, feature_flags):
        """
        Create a feature checker function
        """
        def is_feature_enabled(flag_name, default=False):
            """
            Check if a feature flag is enabled
            
            Args:
                flag_name (str): Name of the feature flag
                default (bool): Default value if flag not found
            
            Returns:
                bool: Whether the feature is enabled
            """
            return feature_flags.get(flag_name.upper(), default)
        
        return is_feature_enabled


class FeatureFlagContextMiddleware(MiddlewareMixin):
    """
    Middleware to add feature flag context to template context
    """
    
    def process_template_response(self, request, response):
        """
        Add feature flags to template context
        """
        if hasattr(response, 'context_data'):
            response.context_data['feature_flags'] = getattr(request, 'feature_flags', {})
            response.context_data['is_feature_enabled'] = getattr(request, 'is_feature_enabled', lambda x: False)
        
        return response


class FeatureUsageMiddleware(MiddlewareMixin):
    """
    Middleware to track feature usage
    """
    
    def process_request(self, request):
        """
        Track feature usage based on URL patterns
        """
        try:
            # Map URL patterns to features
            url_feature_map = {
                '/api/v1/tickets/': 'TICKETS',
                '/api/v1/work-orders/': 'WORK_ORDERS',
                '/api/v1/technicians/': 'TECHNICIANS',
                '/api/v1/knowledge-base/': 'KNOWLEDGE_BASE',
                '/api/v1/automation/': 'AUTOMATION',
                '/api/v1/analytics/': 'ANALYTICS',
                '/api/v1/integrations/': 'INTEGRATIONS',
                '/api/v1/notifications/': 'NOTIFICATIONS',
                '/api/v1/ai-ml/': 'AI_ML',
                '/api/v1/customer-experience/': 'CUSTOMER_EXPERIENCE',
                '/api/v1/advanced-analytics/': 'ADVANCED_ANALYTICS',
                '/api/v1/integration-platform/': 'INTEGRATION_PLATFORM',
                '/api/v1/mobile-iot/': 'MOBILE_IOT',
                '/api/v1/advanced-security/': 'ADVANCED_SECURITY',
                '/api/v1/advanced-workflow/': 'ADVANCED_WORKFLOW',
                '/api/v1/advanced-communication/': 'ADVANCED_COMMUNICATION',
            }
            
            # Check if current path matches any feature
            path = request.path
            for pattern, feature_name in url_feature_map.items():
                if path.startswith(pattern):
                    self._track_feature_usage(request, feature_name)
                    break
                    
        except Exception as e:
            logger.error(f"Error tracking feature usage: {e}")
    
    def _track_feature_usage(self, request, feature_name):
        """
        Track feature usage
        """
        try:
            from apps.features.models import FeatureUsage
            
            user = getattr(request, 'user', None)
            organization = getattr(request, 'organization', None)
            
            if not user or not organization:
                return
            
            # Get or create feature
            feature, created = Feature.objects.get_or_create(
                name=feature_name,
                defaults={
                    'description': f'Feature flag for {feature_name}',
                    'feature_type': 'core',
                    'status': 'active',
                    'is_global': True,
                }
            )
            
            # Get or create usage record
            usage, created = FeatureUsage.objects.get_or_create(
                feature=feature,
                user=user,
                organization=organization,
                defaults={'access_count': 0}
            )
            
            # Update usage count
            usage.access_count += 1
            usage.save(update_fields=['access_count', 'last_accessed'])
            
            logger.debug(f"Tracked usage for feature {feature_name} by user {user.id}")
            
        except Exception as e:
            logger.error(f"Error tracking feature usage for {feature_name}: {e}")


class FeatureHealthMiddleware(MiddlewareMixin):
    """
    Middleware to monitor feature health
    """
    
    def process_response(self, request, response):
        """
        Monitor feature health based on response
        """
        try:
            # Only monitor API responses
            if not request.path.startswith('/api/'):
                return response
            
            # Get feature from URL
            feature_name = self._get_feature_from_url(request.path)
            if not feature_name:
                return response
            
            # Record health status
            self._record_feature_health(feature_name, response.status_code)
            
        except Exception as e:
            logger.error(f"Error monitoring feature health: {e}")
        
        return response
    
    def _get_feature_from_url(self, path):
        """
        Extract feature name from URL
        """
        url_feature_map = {
            '/api/v1/tickets/': 'TICKETS',
            '/api/v1/work-orders/': 'WORK_ORDERS',
            '/api/v1/technicians/': 'TECHNICIANS',
            '/api/v1/knowledge-base/': 'KNOWLEDGE_BASE',
            '/api/v1/automation/': 'AUTOMATION',
            '/api/v1/analytics/': 'ANALYTICS',
            '/api/v1/integrations/': 'INTEGRATIONS',
            '/api/v1/notifications/': 'NOTIFICATIONS',
            '/api/v1/ai-ml/': 'AI_ML',
            '/api/v1/customer-experience/': 'CUSTOMER_EXPERIENCE',
            '/api/v1/advanced-analytics/': 'ADVANCED_ANALYTICS',
            '/api/v1/integration-platform/': 'INTEGRATION_PLATFORM',
            '/api/v1/mobile-iot/': 'MOBILE_IOT',
            '/api/v1/advanced-security/': 'ADVANCED_SECURITY',
            '/api/v1/advanced-workflow/': 'ADVANCED_WORKFLOW',
            '/api/v1/advanced-communication/': 'ADVANCED_COMMUNICATION',
        }
        
        for pattern, feature_name in url_feature_map.items():
            if path.startswith(pattern):
                return feature_name
        
        return None
    
    def _record_feature_health(self, feature_name, status_code):
        """
        Record feature health status
        """
        try:
            from apps.features.models import FeatureHealth, Feature
            
            # Get feature
            try:
                feature = Feature.objects.get(name=feature_name)
            except Feature.DoesNotExist:
                return
            
            # Determine health status
            if status_code < 400:
                health_status = 'healthy'
            elif status_code < 500:
                health_status = 'degraded'
            else:
                health_status = 'unhealthy'
            
            # Create health record
            FeatureHealth.objects.create(
                feature=feature,
                status=health_status,
                metadata={'status_code': status_code}
            )
            
            logger.debug(f"Recorded health status for {feature_name}: {health_status}")
            
        except Exception as e:
            logger.error(f"Error recording feature health for {feature_name}: {e}")
