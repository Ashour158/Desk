"""
Advanced caching strategies with cache warming, compression, and intelligent invalidation.
"""

import json
import pickle
import zlib
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.conf import settings
from django.db.models import Model, QuerySet
from django.utils.encoding import force_str
from django.utils import timezone

logger = logging.getLogger(__name__)


class AdvancedCacheManager:
    """
    Advanced cache manager with intelligent strategies.
    """
    
    def __init__(self):
        self.cache = cache
        self.compression_enabled = getattr(settings, 'CACHE_COMPRESSION', True)
        self.compression_threshold = getattr(settings, 'CACHE_COMPRESSION_THRESHOLD', 1024)  # 1KB
        self.default_timeout = getattr(settings, 'CACHE_DEFAULT_TIMEOUT', 300)
        
    def _compress_data(self, data: Any) -> bytes:
        """
        Compress data if it's large enough.
        """
        if not self.compression_enabled:
            return pickle.dumps(data)
        
        serialized = pickle.dumps(data)
        
        if len(serialized) > self.compression_threshold:
            compressed = zlib.compress(serialized)
            # Add compression marker
            return b'COMPRESSED:' + compressed
        
        return serialized
    
    def _decompress_data(self, data: bytes) -> Any:
        """
        Decompress data if it was compressed.
        """
        if data.startswith(b'COMPRESSED:'):
            compressed_data = data[11:]  # Remove 'COMPRESSED:' prefix
            decompressed = zlib.decompress(compressed_data)
            return pickle.loads(decompressed)
        
        return pickle.loads(data)
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a unique cache key.
        """
        key_parts = [prefix]
        
        for arg in args:
            if isinstance(arg, Model):
                key_parts.append(f"{arg._meta.model_name}_{arg.pk}")
            else:
                key_parts.append(str(arg))
        
        for key, value in sorted(kwargs.items()):
            if isinstance(value, Model):
                key_parts.append(f"{key}_{value._meta.model_name}_{value.pk}")
            else:
                key_parts.append(f"{key}_{value}")
        
        key = "_".join(key_parts)
        
        # Hash long keys
        if len(key) > 250:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}_{key_hash}"
        
        return key
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache with decompression.
        """
        try:
            data = self.cache.get(key)
            if data is None:
                return default
            
            if isinstance(data, bytes):
                return self._decompress_data(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting cached value: {e}")
            return default
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """
        Set value in cache with compression.
        """
        try:
            timeout = timeout or self.default_timeout
            
            # Compress large data
            if isinstance(value, (dict, list, tuple)) and len(str(value)) > self.compression_threshold:
                compressed_data = self._compress_data(value)
                return self.cache.set(key, compressed_data, timeout)
            
            return self.cache.set(key, value, timeout)
            
        except Exception as e:
            logger.error(f"Error setting cached value: {e}")
            return False
    
    def get_or_set(self, key: str, callable_func: Callable, timeout: int = None) -> Any:
        """
        Get value from cache or set it using callable.
        """
        value = self.get(key)
        if value is None:
            value = callable_func()
            self.set(key, value, timeout)
        return value
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        """
        try:
            return self.cache.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cached value: {e}")
            return False
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        """
        try:
            values = self.cache.get_many(keys)
            result = {}
            
            for key, value in values.items():
                if isinstance(value, bytes):
                    result[key] = self._decompress_data(value)
                else:
                    result[key] = value
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting multiple cached values: {e}")
            return {}
    
    def set_many(self, data: Dict[str, Any], timeout: int = None) -> bool:
        """
        Set multiple values in cache.
        """
        try:
            timeout = timeout or self.default_timeout
            compressed_data = {}
            
            for key, value in data.items():
                if isinstance(value, (dict, list, tuple)) and len(str(value)) > self.compression_threshold:
                    compressed_data[key] = self._compress_data(value)
                else:
                    compressed_data[key] = value
            
            return self.cache.set_many(compressed_data, timeout)
            
        except Exception as e:
            logger.error(f"Error setting multiple cached values: {e}")
            return False


class CacheWarmer:
    """
    Cache warming system for frequently accessed data.
    """
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.warming_tasks = []
    
    def register_warming_task(self, name: str, callable_func: Callable, timeout: int = 300):
        """
        Register a cache warming task.
        """
        self.warming_tasks.append({
            'name': name,
            'func': callable_func,
            'timeout': timeout
        })
    
    def warm_cache(self, organization_id: int = None):
        """
        Warm up cache with frequently accessed data.
        """
        logger.info("Starting cache warming process")
        
        for task in self.warming_tasks:
            try:
                cache_key = f"warm_{task['name']}"
                if organization_id:
                    cache_key += f"_org_{organization_id}"
                
                # Check if already warmed recently
                if self.cache_manager.get(cache_key):
                    continue
                
                # Execute warming function
                data = task['func'](organization_id)
                
                # Cache the result
                self.cache_manager.set(cache_key, data, task['timeout'])
                
                logger.info(f"Cache warmed for task: {task['name']}")
                
            except Exception as e:
                logger.error(f"Error warming cache for task {task['name']}: {e}")
    
    def warm_user_data(self, user_id: int):
        """
        Warm cache for specific user data.
        """
        from apps.accounts.models import User
        from apps.tickets.models import Ticket
        
        try:
            user = User.objects.select_related('organization').get(id=user_id)
            
            # Warm user's tickets
            tickets = Ticket.objects.filter(
                organization=user.organization
            ).select_related('customer', 'assigned_agent')[:50]
            
            cache_key = f"user_tickets_{user_id}"
            self.cache_manager.set(cache_key, list(tickets.values()), 600)
            
            # Warm user's organization data
            org_data = {
                'name': user.organization.name,
                'settings': user.organization.settings,
                'features': user.organization.features
            }
            
            cache_key = f"user_org_{user_id}"
            self.cache_manager.set(cache_key, org_data, 1800)
            
            logger.info(f"User data warmed for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error warming user data: {e}")


class IntelligentCacheInvalidation:
    """
    Intelligent cache invalidation system.
    """
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.invalidation_rules = {}
    
    def register_invalidation_rule(self, model_class: Model, pattern: str, callable_func: Callable = None):
        """
        Register cache invalidation rule for a model.
        """
        model_name = model_class._meta.model_name
        self.invalidation_rules[model_name] = {
            'pattern': pattern,
            'func': callable_func
        }
    
    def invalidate_on_model_change(self, model_class: Model, instance: Model, created: bool = False):
        """
        Invalidate cache when model instance changes.
        """
        model_name = model_class._meta.model_name
        
        if model_name in self.invalidation_rules:
            rule = self.invalidation_rules[model_name]
            pattern = rule['pattern']
            
            # Replace placeholders in pattern
            if '{id}' in pattern:
                pattern = pattern.replace('{id}', str(instance.id))
            if '{organization_id}' in pattern and hasattr(instance, 'organization'):
                pattern = pattern.replace('{organization_id}', str(instance.organization.id))
            
            # Invalidate matching keys
            self._invalidate_pattern(pattern)
            
            # Execute custom invalidation function
            if rule['func']:
                rule['func'](instance, created)
    
    def _invalidate_pattern(self, pattern: str):
        """
        Invalidate cache keys matching pattern.
        """
        try:
            # This requires Redis for pattern matching
            if hasattr(self.cache_manager.cache, '_cache') and hasattr(self.cache_manager.cache._cache, 'get_client'):
                redis_client = self.cache_manager.cache._cache.get_client()
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    logger.info(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
                    return True
            
            logger.warning("Pattern invalidation not supported with current cache backend")
            return False
            
        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {e}")
            return False


class CacheAnalytics:
    """
    Cache analytics and monitoring.
    """
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    def record_hit(self):
        """Record cache hit."""
        self.stats['hits'] += 1
    
    def record_miss(self):
        """Record cache miss."""
        self.stats['misses'] += 1
    
    def record_set(self):
        """Record cache set."""
        self.stats['sets'] += 1
    
    def record_delete(self):
        """Record cache delete."""
        self.stats['deletes'] += 1
    
    def record_error(self):
        """Record cache error."""
        self.stats['errors'] += 1
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.stats['hits'] + self.stats['misses']
        if total == 0:
            return 0.0
        return (self.stats['hits'] / total) * 100
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            **self.stats,
            'hit_rate': self.get_hit_rate(),
            'timestamp': timezone.now().isoformat()
        }
    
    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }


# Global instances
advanced_cache = AdvancedCacheManager()
cache_warmer = CacheWarmer(advanced_cache)
cache_invalidation = IntelligentCacheInvalidation(advanced_cache)
cache_analytics = CacheAnalytics(advanced_cache)

# Register default warming tasks
def warm_ticket_statistics(organization_id=None):
    """Warm ticket statistics cache."""
    from apps.tickets.models import Ticket
    from django.db.models import Count, Q
    
    if organization_id:
        queryset = Ticket.objects.filter(organization_id=organization_id)
    else:
        queryset = Ticket.objects.all()
    
    return queryset.aggregate(
        total=Count('id'),
        open=Count('id', filter=Q(status='open')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        resolved=Count('id', filter=Q(status='resolved')),
        closed=Count('id', filter=Q(status='closed'))
    )

def warm_user_permissions(organization_id=None):
    """Warm user permissions cache."""
    from apps.accounts.models import User
    
    if organization_id:
        users = User.objects.filter(organization_id=organization_id)
    else:
        users = User.objects.all()
    
    return {
        user.id: {
            'role': user.role,
            'permissions': user.get_all_permissions(),
            'is_active': user.is_active
        }
        for user in users.select_related('organization')
    }

# Register warming tasks
cache_warmer.register_warming_task('ticket_statistics', warm_ticket_statistics, 600)
cache_warmer.register_warming_task('user_permissions', warm_user_permissions, 1800)

# Register invalidation rules
from apps.tickets.models import Ticket
from apps.accounts.models import User

cache_invalidation.register_invalidation_rule(
    Ticket, 
    'tickets_*',
    lambda instance, created: cache_warmer.warm_cache(instance.organization.id)
)

cache_invalidation.register_invalidation_rule(
    User,
    'user_*',
    lambda instance, created: cache_warmer.warm_user_data(instance.id)
)
