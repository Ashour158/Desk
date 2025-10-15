"""
Advanced caching system with Redis and multi-level caching.
"""

import json
import pickle
import hashlib
import logging
from datetime import timedelta

# Configure logging
logger = logging.getLogger(__name__)
from django.core.cache import cache
from django.conf import settings
from django.core.cache.utils import make_template_fragment_key
from django.utils.encoding import force_str
from django.db.models import Model
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()


class CacheManager:
    """Advanced cache manager with multi-level caching."""

    def __init__(self):
        self.default_timeout = getattr(settings, "CACHE_DEFAULT_TIMEOUT", 300)
        self.redis_client = cache._cache.get_client()

    def get_cache_key(self, prefix, *args, **kwargs):
        """Generate cache key with prefix and arguments."""
        key_parts = [prefix]

        # Add positional arguments
        for arg in args:
            if isinstance(arg, Model):
                key_parts.append(f"{arg._meta.model_name}_{arg.pk}")
            else:
                key_parts.append(str(arg))

        # Add keyword arguments
        for key, value in sorted(kwargs.items()):
            if isinstance(value, Model):
                key_parts.append(f"{key}_{value._meta.model_name}_{value.pk}")
            else:
                key_parts.append(f"{key}_{value}")

        # Create hash for long keys
        key = "_".join(key_parts)
        if len(key) > 250:
            key = f"{prefix}_{hashlib.md5(key.encode()).hexdigest()}"

        return key

    def get(self, key, default=None):
        """Get value from cache."""
        try:
            value = cache.get(key)
            if value is None:
                return default
            return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default

    def set(self, key, value, timeout=None):
        """Set value in cache."""
        try:
            if timeout is None:
                timeout = self.default_timeout
            cache.set(key, value, timeout)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key):
        """Delete value from cache."""
        try:
            cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def get_or_set(self, key, callable_func, timeout=None):
        """Get value from cache or set it using callable."""
        value = self.get(key)
        if value is None:
            value = callable_func()
            self.set(key, value, timeout)
        return value

    def invalidate_pattern(self, pattern):
        """Invalidate cache keys matching pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache pattern invalidation error: {e}")
            return False

    def get_many(self, keys):
        """Get multiple values from cache."""
        try:
            return cache.get_many(keys)
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return {}

    def set_many(self, data, timeout=None):
        """Set multiple values in cache."""
        try:
            if timeout is None:
                timeout = self.default_timeout
            cache.set_many(data, timeout)
            return True
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False


class ModelCache:
    """Model-specific caching utilities."""

    def __init__(self, model_class):
        self.model_class = model_class
        self.cache_manager = CacheManager()
        self.model_name = model_class._meta.model_name

    def get_cache_key(self, pk, suffix=""):
        """Get cache key for model instance."""
        key = f"{self.model_name}_{pk}"
        if suffix:
            key += f"_{suffix}"
        return key

    def get(self, pk, default=None):
        """Get model instance from cache."""
        key = self.get_cache_key(pk)
        return self.cache_manager.get(key, default)

    def set(self, instance, timeout=None):
        """Set model instance in cache."""
        key = self.get_cache_key(instance.pk)
        return self.cache_manager.set(key, instance, timeout)

    def delete(self, pk):
        """Delete model instance from cache."""
        key = self.get_cache_key(pk)
        return self.cache_manager.delete(key)

    def invalidate_all(self):
        """Invalidate all cache entries for this model."""
        pattern = f"{self.model_name}_*"
        return self.cache_manager.invalidate_pattern(pattern)


class QueryCache:
    """Query result caching."""

    def __init__(self):
        self.cache_manager = CacheManager()

    def get_query_key(self, queryset, *args, **kwargs):
        """Generate cache key for queryset."""
        # Create hash of queryset SQL
        sql = str(queryset.query)
        sql_hash = hashlib.md5(sql.encode()).hexdigest()

        # Add additional parameters
        key_parts = [f"query_{sql_hash}"]
        for arg in args:
            key_parts.append(str(arg))
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}_{value}")

        return "_".join(key_parts)

    def get_queryset(self, queryset, timeout=None, *args, **kwargs):
        """Get queryset results from cache."""
        key = self.get_query_key(queryset, *args, **kwargs)
        return self.cache_manager.get_or_set(key, lambda: list(queryset), timeout)

    def invalidate_model(self, model_class):
        """Invalidate all queries for a model."""
        pattern = f"query_*{model_class._meta.model_name}*"
        return self.cache_manager.invalidate_pattern(pattern)


class TemplateCache:
    """Template fragment caching."""

    def __init__(self):
        self.cache_manager = CacheManager()

    def get_template_key(self, fragment_name, vary_on=None):
        """Get cache key for template fragment."""
        if vary_on is None:
            vary_on = []

        key = make_template_fragment_key(fragment_name, vary_on)
        return key

    def get_template(self, fragment_name, vary_on=None):
        """Get template fragment from cache."""
        key = self.get_template_key(fragment_name, vary_on)
        return self.cache_manager.get(key)

    def set_template(self, fragment_name, content, timeout=None, vary_on=None):
        """Set template fragment in cache."""
        key = self.get_template_key(fragment_name, vary_on)
        return self.cache_manager.set(key, content, timeout)

    def delete_template(self, fragment_name, vary_on=None):
        """Delete template fragment from cache."""
        key = self.get_template_key(fragment_name, vary_on)
        return self.cache_manager.delete(key)


class APICache:
    """API response caching."""

    def __init__(self):
        self.cache_manager = CacheManager()

    def get_api_key(self, endpoint, method, params=None, user=None):
        """Get cache key for API endpoint."""
        key_parts = [f"api_{method.lower()}_{endpoint}"]

        if params:
            for key, value in sorted(params.items()):
                key_parts.append(f"{key}_{value}")

        if user:
            key_parts.append(f"user_{user.pk}")

        return "_".join(key_parts)

    def get_api_response(self, endpoint, method, params=None, user=None, timeout=None):
        """Get API response from cache."""
        key = self.get_api_key(endpoint, method, params, user)
        return self.cache_manager.get(key)

    def set_api_response(
        self, endpoint, method, response, timeout=None, params=None, user=None
    ):
        """Set API response in cache."""
        key = self.get_api_key(endpoint, method, params, user)
        return self.cache_manager.set(key, response, timeout)

    def invalidate_api(self, endpoint=None, method=None):
        """Invalidate API cache."""
        if endpoint and method:
            pattern = f"api_{method.lower()}_{endpoint}*"
        elif endpoint:
            pattern = f"api_*_{endpoint}*"
        else:
            pattern = "api_*"

        return self.cache_manager.invalidate_pattern(pattern)


class OrganizationCache:
    """Organization-specific caching."""

    def __init__(self):
        self.cache_manager = CacheManager()

    def get_org_key(self, organization, suffix=""):
        """Get cache key for organization."""
        key = f"org_{organization.pk}"
        if suffix:
            key += f"_{suffix}"
        return key

    def get_org_data(self, organization, data_type, default=None):
        """Get organization data from cache."""
        key = self.get_org_key(organization, data_type)
        return self.cache_manager.get(key, default)

    def set_org_data(self, organization, data_type, data, timeout=None):
        """Set organization data in cache."""
        key = self.get_org_key(organization, data_type)
        return self.cache_manager.set(key, data, timeout)

    def invalidate_org(self, organization):
        """Invalidate all cache for organization."""
        pattern = f"org_{organization.pk}_*"
        return self.cache_manager.invalidate_pattern(pattern)


class CacheDecorators:
    """Cache decorators for functions and methods."""

    @staticmethod
    def cache_result(timeout=None, key_prefix="", key_func=None):
        """Decorator to cache function results."""

        def decorator(func):
            def wrapper(*args, **kwargs):
                cache_manager = CacheManager()

                # Generate cache key
                if key_func:
                    key = key_func(*args, **kwargs)
                else:
                    key_parts = [key_prefix, func.__name__]
                    for arg in args:
                        key_parts.append(str(arg))
                    for key, value in sorted(kwargs.items()):
                        key_parts.append(f"{key}_{value}")
                    key = "_".join(key_parts)

                # Try to get from cache
                result = cache_manager.get(key)
                if result is None:
                    result = func(*args, **kwargs)
                    cache_manager.set(key, result, timeout)

                return result

            return wrapper

        return decorator

    @staticmethod
    def cache_invalidate(pattern=None, model_class=None):
        """Decorator to invalidate cache after function execution."""

        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                cache_manager = CacheManager()
                if pattern:
                    cache_manager.invalidate_pattern(pattern)
                elif model_class:
                    model_cache = ModelCache(model_class)
                    model_cache.invalidate_all()

                return result

            return wrapper

        return decorator


class CacheStats:
    """Cache statistics and monitoring."""

    def __init__(self):
        self.cache_manager = CacheManager()

    def get_stats(self):
        """Get cache statistics."""
        try:
            redis_client = self.cache_manager.redis_client
            info = redis_client.info()

            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self.calculate_hit_rate(info),
            }
        except Exception as e:
            return {"error": str(e)}

    def calculate_hit_rate(self, info):
        """Calculate cache hit rate."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses

        if total == 0:
            return 0

        return round((hits / total) * 100, 2)

    def get_key_count(self, pattern="*"):
        """Get count of keys matching pattern."""
        try:
            keys = self.cache_manager.redis_client.keys(pattern)
            return len(keys)
        except Exception as e:
            return 0

    def get_memory_usage(self, pattern="*"):
        """Get memory usage for keys matching pattern."""
        try:
            keys = self.cache_manager.redis_client.keys(pattern)
            if not keys:
                return 0

            total_memory = 0
            for key in keys:
                memory = self.cache_manager.redis_client.memory_usage(key)
                if memory:
                    total_memory += memory

            return total_memory
        except Exception as e:
            return 0


# Global cache instances
cache_manager = CacheManager()
query_cache = QueryCache()
template_cache = TemplateCache()
api_cache = APICache()
org_cache = OrganizationCache()
cache_stats = CacheStats()
