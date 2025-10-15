"""
Advanced query caching system for expensive database operations.
"""

import hashlib
import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

from django.core.cache import cache
from django.db.models import QuerySet, Model
from django.conf import settings
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)


class QueryCache:
    """
    Advanced query caching system with automatic invalidation.
    """
    
    def __init__(self, timeout: int = 300, key_prefix: str = 'query_cache'):
        self.timeout = timeout
        self.key_prefix = key_prefix
        self.cache = cache
    
    def _generate_cache_key(self, query: Union[QuerySet, str], params: Dict = None) -> str:
        """
        Generate a unique cache key for a query.
        """
        if isinstance(query, QuerySet):
            # Convert QuerySet to string representation
            query_str = str(query.query)
        else:
            query_str = str(query)
        
        # Add parameters to the key
        if params:
            query_str += f"_{json.dumps(params, sort_keys=True)}"
        
        # Create hash for long keys
        query_hash = hashlib.md5(query_str.encode()).hexdigest()
        return f"{self.key_prefix}:{query_hash}"
    
    def get(self, query: Union[QuerySet, str], params: Dict = None) -> Optional[Any]:
        """
        Get cached result for a query.
        """
        try:
            cache_key = self._generate_cache_key(query, params)
            result = self.cache.get(cache_key)
            
            if result is not None:
                logger.debug(f"Cache hit for query: {cache_key}")
                return result
            
            logger.debug(f"Cache miss for query: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached query: {e}")
            return None
    
    def set(self, query: Union[QuerySet, str], result: Any, timeout: int = None, params: Dict = None) -> bool:
        """
        Cache the result of a query.
        """
        try:
            cache_key = self._generate_cache_key(query, params)
            timeout = timeout or self.timeout
            
            # Serialize result if it's a QuerySet
            if isinstance(result, QuerySet):
                result = list(result.values())
            
            self.cache.set(cache_key, result, timeout)
            logger.debug(f"Cached query result: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching query result: {e}")
            return False
    
    def get_or_set(self, query: Union[QuerySet, str], callable_func, timeout: int = None, params: Dict = None) -> Any:
        """
        Get cached result or execute query and cache the result.
        """
        result = self.get(query, params)
        
        if result is None:
            logger.debug("Executing query and caching result")
            result = callable_func()
            self.set(query, result, timeout, params)
        
        return result
    
    def invalidate_pattern(self, pattern: str) -> bool:
        """
        Invalidate cache keys matching a pattern.
        """
        try:
            # This would need Redis for pattern matching
            if hasattr(self.cache, '_cache') and hasattr(self.cache._cache, 'get_client'):
                redis_client = self.cache._cache.get_client()
                keys = redis_client.keys(f"{self.key_prefix}:{pattern}")
                if keys:
                    redis_client.delete(*keys)
                    logger.debug(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
                    return True
            
            logger.warning("Pattern invalidation not supported with current cache backend")
            return False
            
        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {e}")
            return False
    
    def invalidate_model(self, model: Model) -> bool:
        """
        Invalidate all cache entries for a specific model.
        """
        model_name = model._meta.model_name
        return self.invalidate_pattern(f"*{model_name}*")
    
    def clear(self) -> bool:
        """
        Clear all cached queries.
        """
        try:
            return self.invalidate_pattern("*")
        except Exception as e:
            logger.error(f"Error clearing query cache: {e}")
            return False


class ModelCache:
    """
    Model-specific caching utilities.
    """
    
    def __init__(self, model_class, timeout: int = 300):
        self.model_class = model_class
        self.timeout = timeout
        self.query_cache = QueryCache(timeout=timeout, key_prefix=f"model_cache_{model_class._meta.model_name}")
    
    def get_by_id(self, id: int) -> Optional[Model]:
        """
        Get model instance by ID with caching.
        """
        cache_key = f"model_{self.model_class._meta.model_name}_{id}"
        cached_instance = cache.get(cache_key)
        
        if cached_instance is not None:
            return cached_instance
        
        try:
            instance = self.model_class.objects.get(id=id)
            cache.set(cache_key, instance, self.timeout)
            return instance
        except self.model_class.DoesNotExist:
            return None
    
    def get_by_field(self, field: str, value: Any) -> Optional[Model]:
        """
        Get model instance by field value with caching.
        """
        cache_key = f"model_{self.model_class._meta.model_name}_{field}_{value}"
        cached_instance = cache.get(cache_key)
        
        if cached_instance is not None:
            return cached_instance
        
        try:
            instance = self.model_class.objects.get(**{field: value})
            cache.set(cache_key, instance, self.timeout)
            return instance
        except self.model_class.DoesNotExist:
            return None
    
    def get_queryset(self, **filters) -> List[Model]:
        """
        Get filtered queryset with caching.
        """
        cache_key = f"queryset_{self.model_class._meta.model_name}_{hashlib.md5(str(filters).encode()).hexdigest()}"
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            return cached_results
        
        queryset = self.model_class.objects.filter(**filters)
        results = list(queryset)
        cache.set(cache_key, results, self.timeout)
        return results
    
    def invalidate_instance(self, instance: Model) -> bool:
        """
        Invalidate cache for a specific instance.
        """
        try:
            # Invalidate by ID
            cache_key = f"model_{self.model_class._meta.model_name}_{instance.id}"
            cache.delete(cache_key)
            
            # Invalidate related caches
            self.query_cache.invalidate_model(instance)
            
            return True
        except Exception as e:
            logger.error(f"Error invalidating model cache: {e}")
            return False


class APICache:
    """
    API response caching with automatic invalidation.
    """
    
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.cache = cache
    
    def get_api_key(self, endpoint: str, method: str, params: Dict = None, user_id: int = None) -> str:
        """
        Generate cache key for API endpoint.
        """
        key_parts = [f"api_{method.lower()}_{endpoint}"]
        
        if params:
            for key, value in sorted(params.items()):
                key_parts.append(f"{key}_{value}")
        
        if user_id:
            key_parts.append(f"user_{user_id}")
        
        return "_".join(key_parts)
    
    def get_response(self, endpoint: str, method: str, params: Dict = None, user_id: int = None) -> Optional[Any]:
        """
        Get cached API response.
        """
        cache_key = self.get_api_key(endpoint, method, params, user_id)
        return self.cache.get(cache_key)
    
    def set_response(self, endpoint: str, method: str, response: Any, params: Dict = None, user_id: int = None, timeout: int = None) -> bool:
        """
        Cache API response.
        """
        cache_key = self.get_api_key(endpoint, method, params, user_id)
        timeout = timeout or self.timeout
        
        try:
            self.cache.set(cache_key, response, timeout)
            return True
        except Exception as e:
            logger.error(f"Error caching API response: {e}")
            return False
    
    def invalidate_endpoint(self, endpoint: str, method: str = None) -> bool:
        """
        Invalidate cache for an endpoint.
        """
        try:
            if method:
                pattern = f"api_{method.lower()}_{endpoint}*"
            else:
                pattern = f"api_*_{endpoint}*"
            
            # This would need Redis for pattern matching
            if hasattr(self.cache, '_cache') and hasattr(self.cache._cache, 'get_client'):
                redis_client = self.cache._cache.get_client()
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error invalidating API cache: {e}")
            return False


# Global cache instances
query_cache = QueryCache(timeout=300)
api_cache = APICache(timeout=300)


# Decorators for automatic caching
def cache_query(timeout: int = 300, key_prefix: str = None):
    """
    Decorator to cache function results.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}_{hashlib.md5(str(args) + str(kwargs).encode()).hexdigest()}"
            if key_prefix:
                cache_key = f"{key_prefix}_{cache_key}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def cache_invalidate(pattern: str = None, model_class: Model = None):
    """
    Decorator to invalidate cache after function execution.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache
            if pattern:
                query_cache.invalidate_pattern(pattern)
            elif model_class:
                query_cache.invalidate_model(model_class)
            
            return result
        
        return wrapper
    return decorator
