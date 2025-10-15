"""
Intelligent Cache Invalidation System
Provides smart cache invalidation based on data relationships and patterns
"""

import json
import logging
from typing import Dict, List, Set, Any, Optional, Callable
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.conf import settings
import hashlib

logger = logging.getLogger(__name__)


class IntelligentCacheInvalidator:
    """
    Intelligent cache invalidation system that tracks data relationships
    and invalidates related caches automatically.
    """
    
    def __init__(self):
        self.relationship_map = {}
        self.invalidation_rules = {}
        self.cache_patterns = {}
        self.performance_metrics = {
            'invalidations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'patterns_matched': 0
        }
    
    def register_relationship(self, model_class: str, related_models: List[str], 
                            invalidation_strategy: str = 'immediate'):
        """
        Register a relationship between models for cache invalidation.
        
        Args:
            model_class: The model that triggers invalidation
            related_models: List of related models to invalidate
            invalidation_strategy: 'immediate', 'delayed', or 'batch'
        """
        self.relationship_map[model_class] = {
            'related_models': related_models,
            'strategy': invalidation_strategy
        }
        logger.info(f"Registered relationship: {model_class} -> {related_models}")
    
    def register_invalidation_rule(self, pattern: str, rule: Dict[str, Any]):
        """
        Register a cache invalidation rule.
        
        Args:
            pattern: Cache key pattern to match
            rule: Rule configuration
        """
        self.invalidation_rules[pattern] = rule
        logger.info(f"Registered invalidation rule: {pattern}")
    
    def register_cache_pattern(self, pattern: str, dependencies: List[str]):
        """
        Register a cache pattern with its dependencies.
        
        Args:
            pattern: Cache key pattern
            dependencies: List of model classes this cache depends on
        """
        self.cache_patterns[pattern] = dependencies
        logger.info(f"Registered cache pattern: {pattern} -> {dependencies}")
    
    def invalidate_by_model(self, model_class: str, instance_id: Optional[str] = None):
        """
        Invalidate caches related to a specific model.
        
        Args:
            model_class: The model class that changed
            instance_id: Optional specific instance ID
        """
        try:
            # Get related models
            relationships = self.relationship_map.get(model_class, {})
            related_models = relationships.get('related_models', [])
            strategy = relationships.get('strategy', 'immediate')
            
            # Find cache patterns that depend on this model
            affected_patterns = []
            for pattern, dependencies in self.cache_patterns.items():
                if model_class in dependencies:
                    affected_patterns.append(pattern)
            
            # Invalidate related caches
            if strategy == 'immediate':
                self._immediate_invalidation(related_models, affected_patterns, instance_id)
            elif strategy == 'delayed':
                self._delayed_invalidation(related_models, affected_patterns, instance_id)
            elif strategy == 'batch':
                self._batch_invalidation(related_models, affected_patterns, instance_id)
            
            self.performance_metrics['invalidations'] += 1
            logger.info(f"Invalidated caches for {model_class}: {len(affected_patterns)} patterns")
            
        except Exception as e:
            logger.error(f"Failed to invalidate caches for {model_class}: {e}")
    
    def _immediate_invalidation(self, related_models: List[str], 
                               patterns: List[str], instance_id: Optional[str]):
        """Immediate cache invalidation."""
        for model in related_models:
            self._invalidate_model_caches(model, instance_id)
        
        for pattern in patterns:
            self._invalidate_pattern_caches(pattern, instance_id)
    
    def _delayed_invalidation(self, related_models: List[str], 
                             patterns: List[str], instance_id: Optional[str]):
        """Delayed cache invalidation using Celery."""
        try:
            from celery import shared_task
            
            @shared_task
            def delayed_invalidation_task(models, patterns, instance_id):
                invalidator = IntelligentCacheInvalidator()
                for model in models:
                    invalidator._invalidate_model_caches(model, instance_id)
                for pattern in patterns:
                    invalidator._invalidate_pattern_caches(pattern, instance_id)
            
            # Schedule delayed invalidation
            delayed_invalidation_task.apply_async(
                args=[related_models, patterns, instance_id],
                countdown=5  # 5 seconds delay
            )
            
        except ImportError:
            logger.warning("Celery not available, falling back to immediate invalidation")
            self._immediate_invalidation(related_models, patterns, instance_id)
    
    def _batch_invalidation(self, related_models: List[str], 
                           patterns: List[str], instance_id: Optional[str]):
        """Batch cache invalidation for performance."""
        # Collect all cache keys to invalidate
        keys_to_invalidate = set()
        
        for model in related_models:
            keys_to_invalidate.update(self._get_model_cache_keys(model, instance_id))
        
        for pattern in patterns:
            keys_to_invalidate.update(self._get_pattern_cache_keys(pattern, instance_id))
        
        # Batch invalidate
        if keys_to_invalidate:
            cache.delete_many(keys_to_invalidate)
            logger.info(f"Batch invalidated {len(keys_to_invalidate)} cache keys")
    
    def _invalidate_model_caches(self, model_class: str, instance_id: Optional[str]):
        """Invalidate caches for a specific model."""
        cache_keys = self._get_model_cache_keys(model_class, instance_id)
        if cache_keys:
            cache.delete_many(cache_keys)
            logger.debug(f"Invalidated {len(cache_keys)} cache keys for {model_class}")
    
    def _invalidate_pattern_caches(self, pattern: str, instance_id: Optional[str]):
        """Invalidate caches matching a pattern."""
        cache_keys = self._get_pattern_cache_keys(pattern, instance_id)
        if cache_keys:
            cache.delete_many(cache_keys)
            logger.debug(f"Invalidated {len(cache_keys)} cache keys for pattern {pattern}")
    
    def _get_model_cache_keys(self, model_class: str, instance_id: Optional[str]) -> Set[str]:
        """Get cache keys for a model."""
        keys = set()
        
        # Base model keys
        keys.add(f"{model_class}_*")
        keys.add(f"model_{model_class}_*")
        
        if instance_id:
            keys.add(f"{model_class}_{instance_id}_*")
            keys.add(f"model_{model_class}_{instance_id}_*")
        
        # Get actual cache keys from cache backend
        try:
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_many'):
                # Redis backend
                pattern = f"*{model_class}*"
                if instance_id:
                    pattern = f"*{model_class}_{instance_id}*"
                
                # This is a simplified approach - in production, you'd use SCAN
                keys.update(self._scan_cache_keys(pattern))
        except Exception as e:
            logger.warning(f"Failed to scan cache keys: {e}")
        
        return keys
    
    def _get_pattern_cache_keys(self, pattern: str, instance_id: Optional[str]) -> Set[str]:
        """Get cache keys matching a pattern."""
        keys = set()
        
        # Apply instance ID to pattern if provided
        if instance_id and '{instance_id}' in pattern:
            pattern = pattern.format(instance_id=instance_id)
        
        try:
            keys.update(self._scan_cache_keys(pattern))
        except Exception as e:
            logger.warning(f"Failed to scan cache keys for pattern {pattern}: {e}")
        
        return keys
    
    def _scan_cache_keys(self, pattern: str) -> Set[str]:
        """Scan cache for keys matching pattern."""
        keys = set()
        
        try:
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_many'):
                # Redis backend - use SCAN command
                import redis
                if hasattr(cache._cache, 'get_client'):
                    client = cache._cache.get_client()
                    if hasattr(client, 'scan_iter'):
                        for key in client.scan_iter(match=pattern):
                            keys.add(key.decode('utf-8'))
        except Exception as e:
            logger.warning(f"Failed to scan cache with pattern {pattern}: {e}")
        
        return keys
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.performance_metrics.copy()
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.performance_metrics = {
            'invalidations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'patterns_matched': 0
        }


# Global instance
intelligent_invalidator = IntelligentCacheInvalidator()


class CacheInvalidationMixin:
    """
    Mixin for models to enable automatic cache invalidation.
    """
    
    def save(self, *args, **kwargs):
        """Override save to trigger cache invalidation."""
        super().save(*args, **kwargs)
        intelligent_invalidator.invalidate_by_model(
            self.__class__.__name__, 
            str(self.pk)
        )
    
    def delete(self, *args, **kwargs):
        """Override delete to trigger cache invalidation."""
        intelligent_invalidator.invalidate_by_model(
            self.__class__.__name__, 
            str(self.pk)
        )
        super().delete(*args, **kwargs)


class SmartCacheManager:
    """
    Smart cache manager with intelligent invalidation.
    """
    
    def __init__(self, cache_key_prefix: str, ttl: int = 300):
        self.cache_key_prefix = cache_key_prefix
        self.ttl = ttl
        self.invalidator = intelligent_invalidator
    
    def get_or_set(self, key: str, callable_func: Callable, 
                   dependencies: List[str] = None, **kwargs) -> Any:
        """
        Get from cache or set using callable with dependency tracking.
        
        Args:
            key: Cache key
            callable_func: Function to call if cache miss
            dependencies: List of model classes this cache depends on
            **kwargs: Arguments for callable_func
        """
        cache_key = f"{self.cache_key_prefix}_{key}"
        
        # Try to get from cache
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            self.invalidator.performance_metrics['cache_hits'] += 1
            return cached_value
        
        # Cache miss - call function and cache result
        self.invalidator.performance_metrics['cache_misses'] += 1
        value = callable_func(**kwargs)
        
        # Cache the result
        cache.set(cache_key, value, self.ttl)
        
        # Register dependencies
        if dependencies:
            self.invalidator.register_cache_pattern(cache_key, dependencies)
        
        return value
    
    def invalidate(self, key: str):
        """Invalidate a specific cache key."""
        cache_key = f"{self.cache_key_prefix}_{key}"
        cache.delete(cache_key)
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache keys matching pattern."""
        keys = self.invalidator._scan_cache_keys(f"{self.cache_key_prefix}_{pattern}")
        if keys:
            cache.delete_many(keys)
    
    def clear_all(self):
        """Clear all cache keys with this prefix."""
        keys = self.invalidator._scan_cache_keys(f"{self.cache_key_prefix}_*")
        if keys:
            cache.delete_many(keys)


# Signal handlers for automatic cache invalidation
@receiver(post_save)
def invalidate_cache_on_save(sender, instance, created, **kwargs):
    """Invalidate cache when model is saved."""
    model_class = sender.__name__
    intelligent_invalidator.invalidate_by_model(model_class, str(instance.pk))


@receiver(post_delete)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when model is deleted."""
    model_class = sender.__name__
    intelligent_invalidator.invalidate_by_model(model_class, str(instance.pk))


@receiver(m2m_changed)
def invalidate_cache_on_m2m_change(sender, instance, action, **kwargs):
    """Invalidate cache when many-to-many relationships change."""
    if action in ['post_add', 'post_remove', 'post_clear']:
        model_class = sender.__name__
        intelligent_invalidator.invalidate_by_model(model_class, str(instance.pk))


# Initialize intelligent cache invalidation
def initialize_intelligent_cache_invalidation():
    """Initialize the intelligent cache invalidation system."""
    
    # Register common relationships
    intelligent_invalidator.register_relationship(
        'Ticket', 
        ['TicketComment', 'TicketAttachment', 'TicketTag'],
        'immediate'
    )
    
    intelligent_invalidator.register_relationship(
        'User', 
        ['Ticket', 'TicketComment', 'WorkOrder'],
        'delayed'
    )
    
    intelligent_invalidator.register_relationship(
        'Organization', 
        ['Ticket', 'User', 'WorkOrder', 'KnowledgeBaseArticle'],
        'batch'
    )
    
    # Register common cache patterns
    intelligent_invalidator.register_cache_pattern(
        'tickets_list_*', 
        ['Ticket', 'User', 'Organization']
    )
    
    intelligent_invalidator.register_cache_pattern(
        'user_profile_*', 
        ['User', 'Organization']
    )
    
    intelligent_invalidator.register_cache_pattern(
        'dashboard_stats_*', 
        ['Ticket', 'WorkOrder', 'User']
    )
    
    logger.info("Intelligent cache invalidation system initialized")


# Initialize on module import
initialize_intelligent_cache_invalidation()
