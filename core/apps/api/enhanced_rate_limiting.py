"""
Enhanced rate limiting for bulk operations and API endpoints.
"""

from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
import time
import logging
from typing import Dict, Optional, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Enhanced rate limiter with multiple algorithms and bulk operation support.
    """
    
    def __init__(self):
        self.rate_limits = {
            # Standard API endpoints
            'api_general': {'requests': 1000, 'window': 3600},  # 1000/hour
            'api_authentication': {'requests': 10, 'window': 60},  # 10/minute
            'api_file_upload': {'requests': 100, 'window': 3600},  # 100/hour
            
            # Bulk operations (stricter limits)
            'bulk_create': {'requests': 50, 'window': 3600},  # 50/hour
            'bulk_update': {'requests': 50, 'window': 3600},  # 50/hour
            'bulk_delete': {'requests': 20, 'window': 3600},  # 20/hour
            
            # High-risk operations
            'bulk_user_operations': {'requests': 10, 'window': 3600},  # 10/hour
            'bulk_organization_operations': {'requests': 5, 'window': 3600},  # 5/hour
            'bulk_security_operations': {'requests': 3, 'window': 3600},  # 3/hour
        }
    
    def is_allowed(self, key: str, limit_type: str, user_id: Optional[str] = None) -> Tuple[bool, Dict]:
        """
        Check if request is allowed based on rate limits.
        
        Args:
            key: Unique identifier for the request
            limit_type: Type of rate limit to apply
            user_id: Optional user ID for user-specific limits
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        try:
            # Get rate limit configuration
            rate_config = self.rate_limits.get(limit_type)
            if not rate_config:
                return True, {'message': 'No rate limit configured'}
            
            # Create cache key
            cache_key = self._create_cache_key(key, limit_type, user_id)
            
            # Get current request count
            current_count = cache.get(cache_key, 0)
            
            # Check if limit is exceeded
            if current_count >= rate_config['requests']:
                return False, {
                    'limit_exceeded': True,
                    'current_count': current_count,
                    'limit': rate_config['requests'],
                    'window': rate_config['window'],
                    'reset_time': self._get_reset_time(cache_key, rate_config['window'])
                }
            
            # Increment counter
            cache.set(cache_key, current_count + 1, rate_config['window'])
            
            return True, {
                'limit_exceeded': False,
                'current_count': current_count + 1,
                'limit': rate_config['requests'],
                'window': rate_config['window'],
                'remaining': rate_config['requests'] - (current_count + 1)
            }
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True, {'error': str(e)}
    
    def _create_cache_key(self, key: str, limit_type: str, user_id: Optional[str] = None) -> str:
        """Create cache key for rate limiting."""
        if user_id:
            return f"rate_limit:{limit_type}:{user_id}:{key}"
        else:
            return f"rate_limit:{limit_type}:{key}"
    
    def _get_reset_time(self, cache_key: str, window: int) -> str:
        """Get reset time for rate limit."""
        # Get cache TTL
        ttl = cache.ttl(cache_key)
        if ttl:
            reset_time = timezone.now().timestamp() + ttl
            return timezone.datetime.fromtimestamp(reset_time).isoformat()
        else:
            return timezone.now().isoformat()
    
    def get_rate_limit_info(self, limit_type: str, user_id: Optional[str] = None) -> Dict:
        """Get current rate limit information."""
        cache_key = self._create_cache_key('info', limit_type, user_id)
        rate_config = self.rate_limits.get(limit_type, {})
        
        current_count = cache.get(cache_key, 0)
        
        return {
            'limit_type': limit_type,
            'current_count': current_count,
            'limit': rate_config.get('requests', 0),
            'window': rate_config.get('window', 0),
            'remaining': rate_config.get('requests', 0) - current_count,
            'reset_time': self._get_reset_time(cache_key, rate_config.get('window', 0))
        }


class BulkOperationRateLimiter:
    """
    Specialized rate limiter for bulk operations.
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.bulk_limits = {
            'bulk_create_tickets': {'requests': 20, 'window': 3600, 'items_per_request': 100},
            'bulk_update_tickets': {'requests': 20, 'window': 3600, 'items_per_request': 100},
            'bulk_delete_tickets': {'requests': 10, 'window': 3600, 'items_per_request': 50},
            'bulk_create_users': {'requests': 5, 'window': 3600, 'items_per_request': 50},
            'bulk_update_users': {'requests': 5, 'window': 3600, 'items_per_request': 50},
            'bulk_delete_users': {'requests': 3, 'window': 3600, 'items_per_request': 25},
            'bulk_create_organizations': {'requests': 2, 'window': 3600, 'items_per_request': 10},
            'bulk_update_organizations': {'requests': 2, 'window': 3600, 'items_per_request': 10},
            'bulk_delete_organizations': {'requests': 1, 'window': 3600, 'items_per_request': 5},
        }
    
    def validate_bulk_request(self, operation_type: str, item_count: int, user_id: str) -> Tuple[bool, Dict]:
        """
        Validate bulk operation request.
        
        Args:
            operation_type: Type of bulk operation
            item_count: Number of items in the request
            user_id: User ID making the request
            
        Returns:
            Tuple of (is_allowed, validation_info)
        """
        try:
            # Get bulk operation limits
            bulk_config = self.bulk_limits.get(operation_type)
            if not bulk_config:
                return False, {'error': 'Unknown bulk operation type'}
            
            # Check item count limit
            if item_count > bulk_config['items_per_request']:
                return False, {
                    'error': 'Item count exceeds limit',
                    'item_count': item_count,
                    'max_items': bulk_config['items_per_request']
                }
            
            # Check rate limit
            is_allowed, rate_info = self.rate_limiter.is_allowed(
                f"bulk_{operation_type}",
                operation_type,
                user_id
            )
            
            if not is_allowed:
                return False, {
                    'error': 'Rate limit exceeded',
                    'rate_info': rate_info
                }
            
            return True, {
                'valid': True,
                'item_count': item_count,
                'max_items': bulk_config['items_per_request'],
                'rate_info': rate_info
            }
            
        except Exception as e:
            logger.error(f"Bulk operation validation error: {e}")
            return False, {'error': str(e)}
    
    def get_bulk_operation_limits(self, operation_type: str) -> Dict:
        """Get limits for bulk operation type."""
        return self.bulk_limits.get(operation_type, {})


def rate_limit(limit_type: str, user_based: bool = False):
    """
    Decorator for rate limiting API endpoints.
    
    Args:
        limit_type: Type of rate limit to apply
        user_based: Whether to apply user-specific limits
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get user ID if user-based limiting
            user_id = None
            if user_based and hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
            
            # Create rate limiter
            rate_limiter = RateLimiter()
            
            # Check rate limit
            is_allowed, rate_info = rate_limiter.is_allowed(
                f"{request.method}_{request.path}",
                limit_type,
                user_id
            )
            
            if not is_allowed:
                return JsonResponse({
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Rate limit exceeded',
                        'details': rate_info,
                        'timestamp': timezone.now().isoformat()
                    },
                    'meta': {
                        'timestamp': timezone.now().isoformat(),
                        'version': 'v1',
                        'request_id': str(uuid.uuid4()),
                    }
                }, status=429)
            
            # Add rate limit headers
            response = view_func(request, *args, **kwargs)
            if hasattr(response, 'data'):
                response['X-RateLimit-Limit'] = rate_info.get('limit', 0)
                response['X-RateLimit-Remaining'] = rate_info.get('remaining', 0)
                response['X-RateLimit-Reset'] = rate_info.get('reset_time', '')
            
            return response
        
        return wrapper
    return decorator


def bulk_operation_rate_limit(operation_type: str):
    """
    Decorator for rate limiting bulk operations.
    
    Args:
        operation_type: Type of bulk operation
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get user ID
            user_id = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
            
            # Get item count from request data
            item_count = 0
            if hasattr(request, 'data') and isinstance(request.data, list):
                item_count = len(request.data)
            elif hasattr(request, 'data') and 'ids' in request.data:
                item_count = len(request.data.get('ids', []))
            
            # Create bulk rate limiter
            bulk_limiter = BulkOperationRateLimiter()
            
            # Validate bulk request
            is_allowed, validation_info = bulk_limiter.validate_bulk_request(
                operation_type,
                item_count,
                user_id
            )
            
            if not is_allowed:
                return JsonResponse({
                    'error': {
                        'code': 'BULK_OPERATION_LIMIT_EXCEEDED',
                        'message': 'Bulk operation limit exceeded',
                        'details': validation_info,
                        'timestamp': timezone.now().isoformat()
                    },
                    'meta': {
                        'timestamp': timezone.now().isoformat(),
                        'version': 'v1',
                        'request_id': str(uuid.uuid4()),
                    }
                }, status=429)
            
            # Add rate limit headers
            response = view_func(request, *args, **kwargs)
            if hasattr(response, 'data'):
                response['X-BulkLimit-Limit'] = validation_info.get('max_items', 0)
                response['X-BulkLimit-Count'] = validation_info.get('item_count', 0)
            
            return response
        
        return wrapper
    return decorator


class RateLimitMiddleware:
    """
    Middleware for applying rate limits to all requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limiter = RateLimiter()
    
    def __call__(self, request):
        # Apply rate limiting based on request path
        limit_type = self._get_limit_type(request.path)
        
        if limit_type:
            user_id = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
            
            is_allowed, rate_info = self.rate_limiter.is_allowed(
                f"{request.method}_{request.path}",
                limit_type,
                user_id
            )
            
            if not is_allowed:
                return JsonResponse({
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Rate limit exceeded',
                        'details': rate_info,
                        'timestamp': timezone.now().isoformat()
                    },
                    'meta': {
                        'timestamp': timezone.now().isoformat(),
                        'version': 'v1',
                        'request_id': str(uuid.uuid4()),
                    }
                }, status=429)
        
        response = self.get_response(request)
        
        # Add rate limit headers
        if limit_type:
            response['X-RateLimit-Limit'] = rate_info.get('limit', 0)
            response['X-RateLimit-Remaining'] = rate_info.get('remaining', 0)
            response['X-RateLimit-Reset'] = rate_info.get('reset_time', '')
        
        return response
    
    def _get_limit_type(self, path: str) -> Optional[str]:
        """Get rate limit type based on request path."""
        if '/api/v1/users/' in path:
            return 'api_authentication'
        elif '/api/v1/tickets/' in path:
            return 'api_general'
        elif '/api/v1/upload/' in path:
            return 'api_file_upload'
        elif '/bulk_' in path:
            return 'bulk_create'  # Default bulk limit
        else:
            return 'api_general'


# Global rate limiter instances
rate_limiter = RateLimiter()
bulk_rate_limiter = BulkOperationRateLimiter()
