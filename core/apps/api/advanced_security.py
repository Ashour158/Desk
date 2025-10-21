"""
Advanced security measures including request size limits and enhanced rate limiting.
"""

import uuid
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
import time
import logging
import hashlib
import hmac
from typing import Dict, Optional, Tuple, List
from functools import wraps
import json

logger = logging.getLogger(__name__)


class RequestSizeLimiter:
    """
    Advanced request size limiting with multiple strategies.
    """
    
    def __init__(self):
        self.size_limits = {
            # General API endpoints
            'api_general': 10 * 1024 * 1024,  # 10MB
            'api_authentication': 1 * 1024 * 1024,  # 1MB
            'api_file_upload': 100 * 1024 * 1024,  # 100MB
            
            # Bulk operations (stricter limits)
            'bulk_create': 50 * 1024 * 1024,  # 50MB
            'bulk_update': 50 * 1024 * 1024,  # 50MB
            'bulk_delete': 10 * 1024 * 1024,  # 10MB
            
            # High-risk operations
            'bulk_user_operations': 25 * 1024 * 1024,  # 25MB
            'bulk_organization_operations': 10 * 1024 * 1024,  # 10MB
            'bulk_security_operations': 5 * 1024 * 1024,  # 5MB
            
            # File uploads
            'file_upload_ticket_attachments': 10 * 1024 * 1024,  # 10MB
            'file_upload_user_avatars': 2 * 1024 * 1024,  # 2MB
            'file_upload_knowledge_base': 20 * 1024 * 1024,  # 20MB
            'file_upload_work_orders': 50 * 1024 * 1024,  # 50MB
        }
    
    def validate_request_size(self, request, limit_type: str) -> Tuple[bool, Dict]:
        """
        Validate request size against limits.
        
        Args:
            request: HTTP request object
            limit_type: Type of size limit to apply
            
        Returns:
            Tuple of (is_allowed, size_info)
        """
        try:
            # Get size limit
            size_limit = self.size_limits.get(limit_type, self.size_limits['api_general'])
            
            # Calculate request size
            request_size = self._calculate_request_size(request)
            
            # Check if size exceeds limit
            if request_size > size_limit:
                return False, {
                    'size_exceeded': True,
                    'request_size': request_size,
                    'size_limit': size_limit,
                    'excess_size': request_size - size_limit,
                    'limit_type': limit_type
                }
            
            return True, {
                'size_exceeded': False,
                'request_size': request_size,
                'size_limit': size_limit,
                'remaining_size': size_limit - request_size,
                'limit_type': limit_type
            }
            
        except Exception as e:
            logger.error(f"Request size validation error: {e}")
            return True, {'error': str(e)}
    
    def _calculate_request_size(self, request) -> int:
        """Calculate total request size."""
        size = 0
        
        # Add request body size
        if hasattr(request, 'body'):
            size += len(request.body)
        
        # Add query parameters size
        if hasattr(request, 'GET'):
            size += len(str(request.GET).encode('utf-8'))
        
        # Add headers size
        if hasattr(request, 'META'):
            for key, value in request.META.items():
                if isinstance(value, str):
                    size += len(key) + len(value)
        
        # Add file uploads size
        if hasattr(request, 'FILES'):
            for field_name, file_list in request.FILES.lists():
                for file in file_list:
                    size += file.size
        
        return size
    
    def get_size_limit_info(self, limit_type: str) -> Dict:
        """Get size limit information for a limit type."""
        return {
            'limit_type': limit_type,
            'size_limit': self.size_limits.get(limit_type, self.size_limits['api_general']),
            'size_limit_mb': self.size_limits.get(limit_type, self.size_limits['api_general']) / (1024 * 1024)
        }


class AdvancedRateLimiter:
    """
    Advanced rate limiter with multiple algorithms and adaptive limits.
    """
    
    def __init__(self):
        self.rate_limits = {
            # Standard API endpoints
            'api_general': {'requests': 1000, 'window': 3600, 'burst': 100},  # 1000/hour, 100 burst
            'api_authentication': {'requests': 10, 'window': 60, 'burst': 5},  # 10/minute, 5 burst
            'api_file_upload': {'requests': 100, 'window': 3600, 'burst': 10},  # 100/hour, 10 burst
            
            # Bulk operations (stricter limits)
            'bulk_create': {'requests': 50, 'window': 3600, 'burst': 5},  # 50/hour, 5 burst
            'bulk_update': {'requests': 50, 'window': 3600, 'burst': 5},  # 50/hour, 5 burst
            'bulk_delete': {'requests': 20, 'window': 3600, 'burst': 2},  # 20/hour, 2 burst
            
            # High-risk operations
            'bulk_user_operations': {'requests': 10, 'window': 3600, 'burst': 1},  # 10/hour, 1 burst
            'bulk_organization_operations': {'requests': 5, 'window': 3600, 'burst': 1},  # 5/hour, 1 burst
            'bulk_security_operations': {'requests': 3, 'window': 3600, 'burst': 1},  # 3/hour, 1 burst
        }
        
        self.adaptive_limits = {}  # Dynamic limits based on system load
        self.user_limits = {}  # User-specific limits
    
    def is_allowed(self, key: str, limit_type: str, user_id: Optional[str] = None, 
                   request_size: int = 0) -> Tuple[bool, Dict]:
        """
        Check if request is allowed with advanced rate limiting.
        
        Args:
            key: Unique identifier for the request
            limit_type: Type of rate limit to apply
            user_id: Optional user ID for user-specific limits
            request_size: Size of the request for adaptive limiting
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        try:
            # Get base rate limit configuration
            rate_config = self.rate_limits.get(limit_type)
            if not rate_config:
                return True, {'message': 'No rate limit configured'}
            
            # Apply adaptive limits based on system load
            adaptive_config = self._get_adaptive_limits(limit_type, request_size)
            if adaptive_config:
                rate_config = {**rate_config, **adaptive_config}
            
            # Apply user-specific limits
            user_config = self._get_user_limits(user_id, limit_type)
            if user_config:
                rate_config = {**rate_config, **user_config}
            
            # Create cache keys for different time windows
            cache_keys = self._create_cache_keys(key, limit_type, user_id)
            
            # Check rate limits for different time windows
            rate_check_results = []
            
            # Check main window limit
            main_result = self._check_rate_limit(cache_keys['main'], rate_config['requests'], rate_config['window'])
            rate_check_results.append(main_result)
            
            # Check burst limit (shorter window)
            if 'burst' in rate_config:
                burst_window = min(rate_config['window'] // 10, 300)  # 10% of main window, max 5 minutes
                burst_result = self._check_rate_limit(cache_keys['burst'], rate_config['burst'], burst_window)
                rate_check_results.append(burst_result)
            
            # Check if any limit is exceeded
            for result in rate_check_results:
                if not result['allowed']:
                    return False, {
                        'limit_exceeded': True,
                        'current_count': result['current_count'],
                        'limit': result['limit'],
                        'window': result['window'],
                        'reset_time': result['reset_time'],
                        'limit_type': limit_type,
                        'user_id': user_id
                    }
            
            # Update counters
            for cache_key, count in [(cache_keys['main'], 1), (cache_keys['burst'], 1)]:
                cache.set(cache_key, count, rate_config['window'])
            
            return True, {
                'limit_exceeded': False,
                'current_count': main_result['current_count'] + 1,
                'limit': rate_config['requests'],
                'window': rate_config['window'],
                'remaining': rate_config['requests'] - (main_result['current_count'] + 1),
                'burst_remaining': rate_config.get('burst', 0) - (rate_check_results[1]['current_count'] + 1) if len(rate_check_results) > 1 else 0
            }
            
        except Exception as e:
            logger.error(f"Advanced rate limiting error: {e}")
            return True, {'error': str(e)}
    
    def _get_adaptive_limits(self, limit_type: str, request_size: int) -> Optional[Dict]:
        """Get adaptive limits based on system load and request size."""
        try:
            # Check system load
            system_load = self._get_system_load()
            
            # Adjust limits based on system load
            if system_load > 0.8:  # High load
                return {'requests': int(self.rate_limits[limit_type]['requests'] * 0.5)}
            elif system_load > 0.6:  # Medium load
                return {'requests': int(self.rate_limits[limit_type]['requests'] * 0.7)}
            
            # Adjust limits based on request size
            if request_size > 10 * 1024 * 1024:  # Large request
                return {'requests': int(self.rate_limits[limit_type]['requests'] * 0.5)}
            elif request_size > 5 * 1024 * 1024:  # Medium request
                return {'requests': int(self.rate_limits[limit_type]['requests'] * 0.7)}
            
            return None
            
        except Exception as e:
            logger.error(f"Adaptive limits error: {e}")
            return None
    
    def _get_user_limits(self, user_id: Optional[str], limit_type: str) -> Optional[Dict]:
        """Get user-specific limits."""
        if not user_id:
            return None
        
        try:
            # Check if user has custom limits
            user_limit_key = f"user_limits:{user_id}:{limit_type}"
            user_limits = cache.get(user_limit_key)
            
            if user_limits:
                return user_limits
            
            # Check user role for different limits
            # This would typically query the user's role from the database
            # For now, we'll use a simple cache-based approach
            
            return None
            
        except Exception as e:
            logger.error(f"User limits error: {e}")
            return None
    
    def _get_system_load(self) -> float:
        """Get current system load (0.0 to 1.0)."""
        try:
            # This would typically check CPU, memory, database connections, etc.
            # For now, we'll use a simple cache-based approach
            load_key = "system_load"
            load = cache.get(load_key, 0.0)
            return float(load)
        except:
            return 0.0
    
    def _create_cache_keys(self, key: str, limit_type: str, user_id: Optional[str] = None) -> Dict[str, str]:
        """Create cache keys for different time windows."""
        base_key = f"rate_limit:{limit_type}"
        if user_id:
            base_key += f":{user_id}"
        
        return {
            'main': f"{base_key}:main:{key}",
            'burst': f"{base_key}:burst:{key}",
            'hourly': f"{base_key}:hourly:{key}",
            'daily': f"{base_key}:daily:{key}"
        }
    
    def _check_rate_limit(self, cache_key: str, limit: int, window: int) -> Dict:
        """Check rate limit for a specific cache key."""
        try:
            current_count = cache.get(cache_key, 0)
            
            if current_count >= limit:
                return {
                    'allowed': False,
                    'current_count': current_count,
                    'limit': limit,
                    'window': window,
                    'reset_time': self._get_reset_time(cache_key, window)
                }
            
            # Increment counter
            cache.set(cache_key, current_count + 1, window)
            
            return {
                'allowed': True,
                'current_count': current_count + 1,
                'limit': limit,
                'window': window,
                'reset_time': self._get_reset_time(cache_key, window)
            }
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return {
                'allowed': True,
                'current_count': 0,
                'limit': limit,
                'window': window,
                'error': str(e)
            }
    
    def _get_reset_time(self, cache_key: str, window: int) -> str:
        """Get reset time for rate limit."""
        try:
            ttl = cache.ttl(cache_key)
            if ttl:
                reset_time = timezone.now().timestamp() + ttl
                return timezone.datetime.fromtimestamp(reset_time).isoformat()
            else:
                return timezone.now().isoformat()
        except:
            return timezone.now().isoformat()


class SecurityHeadersMiddleware:
    """
    Middleware for adding security headers to all responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Content-Security-Policy'] = "default-src 'self'"
        
        return response


class RequestSizeMiddleware:
    """
    Middleware for enforcing request size limits.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.size_limiter = RequestSizeLimiter()
    
    def __call__(self, request):
        # Determine limit type based on request path
        limit_type = self._get_limit_type(request.path)
        
        if limit_type:
            is_allowed, size_info = self.size_limiter.validate_request_size(request, limit_type)
            
            if not is_allowed:
                return JsonResponse({
                    'error': {
                        'code': 'REQUEST_SIZE_EXCEEDED',
                        'message': 'Request size exceeds limit',
                        'details': size_info,
                        'timestamp': timezone.now().isoformat()
                    },
                    'meta': {
                        'timestamp': timezone.now().isoformat(),
                        'version': 'v1',
                        'request_id': str(uuid.uuid4()),
                    }
                }, status=413)
        
        response = self.get_response(request)
        
        # Add size limit headers
        if limit_type:
            size_info = self.size_limiter.get_size_limit_info(limit_type)
            response['X-Request-Size-Limit'] = str(size_info['size_limit'])
            response['X-Request-Size-Limit-MB'] = str(size_info['size_limit_mb'])
        
        return response
    
    def _get_limit_type(self, path: str) -> Optional[str]:
        """Get limit type based on request path."""
        if '/api/v1/users/' in path:
            return 'api_authentication'
        elif '/api/v1/upload/' in path:
            return 'api_file_upload'
        elif '/bulk_' in path:
            return 'bulk_create'
        else:
            return 'api_general'


def advanced_rate_limit(limit_type: str, user_based: bool = False, size_aware: bool = False):
    """
    Decorator for advanced rate limiting.
    
    Args:
        limit_type: Type of rate limit to apply
        user_based: Whether to apply user-specific limits
        size_aware: Whether to consider request size in rate limiting
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get user ID if user-based limiting
            user_id = None
            if user_based and hasattr(request, 'user') and request.user.is_authenticated:
                user_id = str(request.user.id)
            
            # Calculate request size if size-aware
            request_size = 0
            if size_aware:
                size_limiter = RequestSizeLimiter()
                _, size_info = size_limiter.validate_request_size(request, limit_type)
                request_size = size_info.get('request_size', 0)
            
            # Create advanced rate limiter
            rate_limiter = AdvancedRateLimiter()
            
            # Check rate limit
            is_allowed, rate_info = rate_limiter.is_allowed(
                f"{request.method}_{request.path}",
                limit_type,
                user_id,
                request_size
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
                if 'burst_remaining' in rate_info:
                    response['X-RateLimit-Burst-Remaining'] = rate_info['burst_remaining']
            
            return response
        
        return wrapper
    return decorator


# Global instances
request_size_limiter = RequestSizeLimiter()
advanced_rate_limiter = AdvancedRateLimiter()
