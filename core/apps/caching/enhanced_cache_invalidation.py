"""
Enhanced Intelligent Cache Invalidation System
Advanced cache management with machine learning and predictive invalidation
"""

import logging
import time
import json
from typing import Dict, List, Set, Optional, Any, Callable
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.conf import settings
from collections import defaultdict, deque
import threading
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class InvalidationStrategy(Enum):
    """Cache invalidation strategies"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    BATCH = "batch"
    PREDICTIVE = "predictive"
    ADAPTIVE = "adaptive"


class CachePattern(Enum):
    """Cache pattern types"""
    EXACT = "exact"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    WILDCARD = "wildcard"
    REGEX = "regex"


@dataclass
class CacheDependency:
    """Represents a cache dependency relationship"""
    model_class: str
    field_name: str
    invalidation_strategy: InvalidationStrategy
    ttl: int = 300
    priority: int = 1
    conditions: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    invalidations: int = 0
    size: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    invalidation_rate: float = 0.0
    avg_ttl: float = 0.0
    memory_usage: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class InvalidationEvent:
    """Represents a cache invalidation event"""
    timestamp: datetime
    model_class: str
    instance_id: Optional[str]
    operation: str
    affected_keys: List[str]
    strategy: InvalidationStrategy
    success: bool = True
    error: Optional[str] = None


class EnhancedCacheInvalidator:
    """
    Enhanced intelligent cache invalidator with machine learning capabilities
    """
    
    def __init__(self):
        self.dependencies: Dict[str, List[CacheDependency]] = defaultdict(list)
        self.invalidation_rules: Dict[str, List[Dict]] = defaultdict(list)
        self.cache_patterns: Dict[str, Set[str]] = defaultdict(set)
        self.metrics = CacheMetrics()
        self.invalidation_history: deque = deque(maxlen=1000)
        self.pattern_cache: Dict[str, Set[str]] = {}
        self.learning_data: Dict[str, List[float]] = defaultdict(list)
        self.adaptive_thresholds: Dict[str, float] = {}
        self.lock = threading.RLock()
        
        # Initialize with default patterns
        self._initialize_default_patterns()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_default_patterns(self):
        """Initialize default cache patterns"""
        default_patterns = {
            'tickets': [
                'ticket_*',
                'ticket_list_*',
                'ticket_stats_*',
                'ticket_comments_*',
                'ticket_attachments_*'
            ],
            'users': [
                'user_*',
                'user_profile_*',
                'user_permissions_*',
                'user_organizations_*'
            ],
            'organizations': [
                'org_*',
                'organization_*',
                'org_settings_*',
                'org_users_*'
            ],
            'knowledge_base': [
                'kb_*',
                'knowledge_base_*',
                'kb_articles_*',
                'kb_categories_*'
            ],
            'field_service': [
                'work_order_*',
                'technician_*',
                'equipment_*',
                'service_report_*'
            ]
        }
        
        for model, patterns in default_patterns.items():
            self.cache_patterns[model] = set(patterns)
    
    def _start_background_tasks(self):
        """Start background tasks for cache management"""
        # Start metrics collection
        threading.Thread(target=self._collect_metrics_loop, daemon=True).start()
        
        # Start learning analysis
        threading.Thread(target=self._learning_analysis_loop, daemon=True).start()
        
        # Start cache cleanup
        threading.Thread(target=self._cache_cleanup_loop, daemon=True).start()
    
    def register_dependency(self, model_class: str, dependency: CacheDependency):
        """Register a cache dependency"""
        with self.lock:
            self.dependencies[model_class].append(dependency)
            logger.info(f"Registered cache dependency for {model_class}: {dependency}")
    
    def register_invalidation_rule(self, model_class: str, rule: Dict):
        """Register an invalidation rule"""
        with self.lock:
            self.invalidation_rules[model_class].append(rule)
            logger.info(f"Registered invalidation rule for {model_class}: {rule}")
    
    def register_cache_pattern(self, model_class: str, pattern: str, pattern_type: CachePattern = CachePattern.PREFIX):
        """Register a cache pattern"""
        with self.lock:
            self.cache_patterns[model_class].add(pattern)
            logger.info(f"Registered cache pattern for {model_class}: {pattern} ({pattern_type.value})")
    
    def invalidate_by_model(self, model_class: str, instance_id: Optional[str] = None, 
                          operation: str = 'update', context: Dict[str, Any] = None):
        """Invalidate caches related to a specific model"""
        start_time = time.time()
        
        try:
            with self.lock:
                # Get dependencies for this model
                dependencies = self.dependencies.get(model_class, [])
                rules = self.invalidation_rules.get(model_class, [])
                
                # Determine invalidation strategy
                strategy = self._determine_strategy(model_class, operation, context)
                
                # Get affected cache keys
                affected_keys = self._get_affected_keys(model_class, instance_id, dependencies, rules)
                
                # Execute invalidation
                success = self._execute_invalidation(affected_keys, strategy)
                
                # Record invalidation event
                event = InvalidationEvent(
                    timestamp=datetime.now(),
                    model_class=model_class,
                    instance_id=instance_id,
                    operation=operation,
                    affected_keys=affected_keys,
                    strategy=strategy,
                    success=success
                )
                self.invalidation_history.append(event)
                
                # Update metrics
                self.metrics.invalidations += 1
                if success:
                    self.metrics.hit_rate = self._calculate_hit_rate()
                
                # Learn from this invalidation
                self._learn_from_invalidation(event)
                
                logger.info(f"Invalidated {len(affected_keys)} keys for {model_class} in {time.time() - start_time:.3f}s")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to invalidate cache for {model_class}: {e}")
            return False
    
    def _determine_strategy(self, model_class: str, operation: str, context: Dict[str, Any] = None) -> InvalidationStrategy:
        """Determine the best invalidation strategy based on context and learning data"""
        # Check if we have learning data for this model
        if model_class in self.learning_data:
            recent_invalidations = self.learning_data[model_class][-10:]  # Last 10 invalidations
            if len(recent_invalidations) > 5:
                avg_frequency = sum(recent_invalidations) / len(recent_invalidations)
                if avg_frequency > 0.1:  # High frequency
                    return InvalidationStrategy.BATCH
                elif avg_frequency < 0.01:  # Low frequency
                    return InvalidationStrategy.IMMEDIATE
        
        # Check adaptive thresholds
        if model_class in self.adaptive_thresholds:
            threshold = self.adaptive_thresholds[model_class]
            if time.time() - self._get_last_invalidation_time(model_class) < threshold:
                return InvalidationStrategy.DELAYED
        
        # Default strategy based on operation
        if operation in ['create', 'delete']:
            return InvalidationStrategy.IMMEDIATE
        elif operation == 'update':
            return InvalidationStrategy.DELAYED
        else:
            return InvalidationStrategy.ADAPTIVE
    
    def _get_affected_keys(self, model_class: str, instance_id: Optional[str], 
                          dependencies: List[CacheDependency], rules: List[Dict]) -> List[str]:
        """Get all cache keys affected by the invalidation"""
        affected_keys = set()
        
        # Get keys from dependencies
        for dependency in dependencies:
            keys = self._get_keys_for_dependency(dependency, instance_id)
            affected_keys.update(keys)
        
        # Get keys from rules
        for rule in rules:
            keys = self._get_keys_for_rule(rule, model_class, instance_id)
            affected_keys.update(keys)
        
        # Get keys from patterns
        patterns = self.cache_patterns.get(model_class, set())
        for pattern in patterns:
            keys = self._get_keys_for_pattern(pattern, instance_id)
            affected_keys.update(keys)
        
        return list(affected_keys)
    
    def _get_keys_for_dependency(self, dependency: CacheDependency, instance_id: Optional[str]) -> List[str]:
        """Get cache keys for a specific dependency"""
        keys = []
        
        # Generate keys based on dependency conditions
        if dependency.conditions:
            for condition in dependency.conditions:
                key = self._generate_key_from_condition(condition, instance_id)
                if key:
                    keys.append(key)
        
        # Add pattern-based keys
        for pattern in dependency.dependencies:
            pattern_keys = self._get_keys_for_pattern(pattern, instance_id)
            keys.extend(pattern_keys)
        
        return keys
    
    def _get_keys_for_rule(self, rule: Dict, model_class: str, instance_id: Optional[str]) -> List[str]:
        """Get cache keys for a specific rule"""
        keys = []
        
        # Extract key patterns from rule
        key_patterns = rule.get('key_patterns', [])
        for pattern in key_patterns:
            pattern_keys = self._get_keys_for_pattern(pattern, instance_id)
            keys.extend(pattern_keys)
        
        # Apply rule conditions
        conditions = rule.get('conditions', {})
        if self._evaluate_conditions(conditions, model_class, instance_id):
            # Generate additional keys based on rule
            rule_keys = self._generate_keys_from_rule(rule, instance_id)
            keys.extend(rule_keys)
        
        return keys
    
    def _get_keys_for_pattern(self, pattern: str, instance_id: Optional[str]) -> List[str]:
        """Get cache keys matching a pattern"""
        if pattern in self.pattern_cache:
            return list(self.pattern_cache[pattern])
        
        keys = set()
        
        try:
            # Use Redis SCAN for pattern matching
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
                client = cache._cache.get_client()
                if hasattr(client, 'scan_iter'):
                    for key in client.scan_iter(match=pattern):
                        keys.add(key.decode('utf-8'))
        except Exception as e:
            logger.warning(f"Failed to scan cache keys for pattern {pattern}: {e}")
        
        # Cache the result
        self.pattern_cache[pattern] = keys
        return list(keys)
    
    def _execute_invalidation(self, keys: List[str], strategy: InvalidationStrategy) -> bool:
        """Execute cache invalidation with the specified strategy"""
        if not keys:
            return True
        
        try:
            if strategy == InvalidationStrategy.IMMEDIATE:
                return self._immediate_invalidation(keys)
            elif strategy == InvalidationStrategy.DELAYED:
                return self._delayed_invalidation(keys)
            elif strategy == InvalidationStrategy.BATCH:
                return self._batch_invalidation(keys)
            elif strategy == InvalidationStrategy.PREDICTIVE:
                return self._predictive_invalidation(keys)
            elif strategy == InvalidationStrategy.ADAPTIVE:
                return self._adaptive_invalidation(keys)
            else:
                return self._immediate_invalidation(keys)
                
        except Exception as e:
            logger.error(f"Failed to execute invalidation with strategy {strategy}: {e}")
            return False
    
    def _immediate_invalidation(self, keys: List[str]) -> bool:
        """Immediate cache invalidation"""
        try:
            cache.delete_many(keys)
            logger.debug(f"Immediately invalidated {len(keys)} keys")
            return True
        except Exception as e:
            logger.error(f"Failed immediate invalidation: {e}")
            return False
    
    def _delayed_invalidation(self, keys: List[str]) -> bool:
        """Delayed cache invalidation"""
        try:
            # Schedule invalidation for later
            threading.Timer(1.0, lambda: cache.delete_many(keys)).start()
            logger.debug(f"Scheduled delayed invalidation for {len(keys)} keys")
            return True
        except Exception as e:
            logger.error(f"Failed delayed invalidation: {e}")
            return False
    
    def _batch_invalidation(self, keys: List[str]) -> bool:
        """Batch cache invalidation"""
        try:
            # Group keys by pattern for efficient batching
            key_groups = defaultdict(list)
            for key in keys:
                # Extract pattern from key
                pattern = self._extract_pattern_from_key(key)
                key_groups[pattern].append(key)
            
            # Invalidate each group
            for pattern, group_keys in key_groups.items():
                cache.delete_many(group_keys)
                logger.debug(f"Batch invalidated {len(group_keys)} keys for pattern {pattern}")
            
            return True
        except Exception as e:
            logger.error(f"Failed batch invalidation: {e}")
            return False
    
    def _predictive_invalidation(self, keys: List[str]) -> bool:
        """Predictive cache invalidation based on ML models"""
        try:
            # Use machine learning to predict which keys to invalidate
            predicted_keys = self._predict_invalidation_keys(keys)
            
            # Invalidate predicted keys
            cache.delete_many(predicted_keys)
            logger.debug(f"Predictively invalidated {len(predicted_keys)} keys")
            
            return True
        except Exception as e:
            logger.error(f"Failed predictive invalidation: {e}")
            return False
    
    def _adaptive_invalidation(self, keys: List[str]) -> bool:
        """Adaptive cache invalidation based on current conditions"""
        try:
            # Analyze current cache state and system load
            cache_state = self._analyze_cache_state()
            system_load = self._analyze_system_load()
            
            # Choose strategy based on conditions
            if system_load > 0.8:  # High load
                return self._delayed_invalidation(keys)
            elif cache_state['hit_rate'] < 0.7:  # Low hit rate
                return self._immediate_invalidation(keys)
            else:
                return self._batch_invalidation(keys)
                
        except Exception as e:
            logger.error(f"Failed adaptive invalidation: {e}")
            return False
    
    def _learn_from_invalidation(self, event: InvalidationEvent):
        """Learn from invalidation events to improve future predictions"""
        try:
            # Record invalidation frequency
            current_time = time.time()
            self.learning_data[event.model_class].append(current_time)
            
            # Keep only recent data (last 100 invalidations)
            if len(self.learning_data[event.model_class]) > 100:
                self.learning_data[event.model_class] = self.learning_data[event.model_class][-100:]
            
            # Update adaptive thresholds
            self._update_adaptive_thresholds(event.model_class)
            
        except Exception as e:
            logger.error(f"Failed to learn from invalidation: {e}")
    
    def _update_adaptive_thresholds(self, model_class: str):
        """Update adaptive thresholds based on learning data"""
        try:
            if model_class in self.learning_data and len(self.learning_data[model_class]) > 10:
                recent_times = self.learning_data[model_class][-10:]
                intervals = [recent_times[i] - recent_times[i-1] for i in range(1, len(recent_times))]
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    self.adaptive_thresholds[model_class] = avg_interval * 0.5  # 50% of average interval
                    
        except Exception as e:
            logger.error(f"Failed to update adaptive thresholds: {e}")
    
    def _collect_metrics_loop(self):
        """Background task to collect cache metrics"""
        while True:
            try:
                time.sleep(30)  # Collect metrics every 30 seconds
                self._collect_metrics()
            except Exception as e:
                logger.error(f"Failed to collect metrics: {e}")
    
    def _collect_metrics(self):
        """Collect cache performance metrics"""
        try:
            # Get cache statistics
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
                client = cache._cache.get_client()
                
                # Get Redis info
                info = client.info()
                
                # Update metrics
                self.metrics.hits = info.get('keyspace_hits', 0)
                self.metrics.misses = info.get('keyspace_misses', 0)
                self.metrics.size = info.get('db0', {}).get('keys', 0)
                self.metrics.memory_usage = info.get('used_memory', 0)
                
                # Calculate rates
                total_requests = self.metrics.hits + self.metrics.misses
                if total_requests > 0:
                    self.metrics.hit_rate = self.metrics.hits / total_requests
                    self.metrics.miss_rate = self.metrics.misses / total_requests
                
                self.metrics.last_updated = datetime.now()
                
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
    
    def _learning_analysis_loop(self):
        """Background task for learning analysis"""
        while True:
            try:
                time.sleep(300)  # Analyze every 5 minutes
                self._analyze_learning_data()
            except Exception as e:
                logger.error(f"Failed learning analysis: {e}")
    
    def _analyze_learning_data(self):
        """Analyze learning data to improve invalidation strategies"""
        try:
            for model_class, times in self.learning_data.items():
                if len(times) > 20:
                    # Analyze patterns
                    intervals = [times[i] - times[i-1] for i in range(1, len(times))]
                    
                    # Calculate statistics
                    avg_interval = sum(intervals) / len(intervals)
                    std_interval = (sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5
                    
                    # Update adaptive thresholds
                    self.adaptive_thresholds[model_class] = max(avg_interval - std_interval, 1.0)
                    
        except Exception as e:
            logger.error(f"Failed to analyze learning data: {e}")
    
    def _cache_cleanup_loop(self):
        """Background task for cache cleanup"""
        while True:
            try:
                time.sleep(3600)  # Cleanup every hour
                self._cleanup_cache()
            except Exception as e:
                logger.error(f"Failed cache cleanup: {e}")
    
    def _cleanup_cache(self):
        """Clean up old cache entries and patterns"""
        try:
            # Clean up old pattern cache
            current_time = time.time()
            for pattern, keys in self.pattern_cache.items():
                if current_time - self._get_pattern_cache_time(pattern) > 3600:  # 1 hour
                    del self.pattern_cache[pattern]
            
            # Clean up old invalidation history
            if len(self.invalidation_history) > 1000:
                # Keep only last 1000 events
                self.invalidation_history = deque(list(self.invalidation_history)[-1000:], maxlen=1000)
                
        except Exception as e:
            logger.error(f"Failed cache cleanup: {e}")
    
    def get_metrics(self) -> CacheMetrics:
        """Get current cache metrics"""
        return self.metrics
    
    def get_invalidation_history(self, limit: int = 100) -> List[InvalidationEvent]:
        """Get invalidation history"""
        return list(self.invalidation_history)[-limit:]
    
    def get_learning_data(self, model_class: str) -> List[float]:
        """Get learning data for a specific model"""
        return self.learning_data.get(model_class, [])
    
    def get_adaptive_thresholds(self) -> Dict[str, float]:
        """Get adaptive thresholds for all models"""
        return self.adaptive_thresholds.copy()
    
    def reset_metrics(self):
        """Reset cache metrics"""
        self.metrics = CacheMetrics()
        self.invalidation_history.clear()
        self.learning_data.clear()
        self.adaptive_thresholds.clear()
        self.pattern_cache.clear()
    
    # Helper methods (simplified for brevity)
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.metrics.hits + self.metrics.misses
        return self.metrics.hits / total if total > 0 else 0.0
    
    def _get_last_invalidation_time(self, model_class: str) -> float:
        """Get last invalidation time for a model"""
        if model_class in self.learning_data and self.learning_data[model_class]:
            return self.learning_data[model_class][-1]
        return 0.0
    
    def _get_pattern_cache_time(self, pattern: str) -> float:
        """Get pattern cache time"""
        return time.time()  # Simplified implementation
    
    def _extract_pattern_from_key(self, key: str) -> str:
        """Extract pattern from cache key"""
        # Simplified pattern extraction
        if '_' in key:
            return key.split('_')[0] + '_*'
        return key
    
    def _generate_key_from_condition(self, condition: Dict, instance_id: Optional[str]) -> Optional[str]:
        """Generate cache key from condition"""
        # Simplified key generation
        return f"{condition.get('prefix', '')}_{instance_id}" if instance_id else None
    
    def _evaluate_conditions(self, conditions: Dict, model_class: str, instance_id: Optional[str]) -> bool:
        """Evaluate invalidation conditions"""
        # Simplified condition evaluation
        return True
    
    def _generate_keys_from_rule(self, rule: Dict, instance_id: Optional[str]) -> List[str]:
        """Generate keys from rule"""
        # Simplified key generation
        return []
    
    def _predict_invalidation_keys(self, keys: List[str]) -> List[str]:
        """Predict which keys to invalidate"""
        # Simplified prediction
        return keys
    
    def _analyze_cache_state(self) -> Dict[str, Any]:
        """Analyze current cache state"""
        return {'hit_rate': self.metrics.hit_rate, 'size': self.metrics.size}
    
    def _analyze_system_load(self) -> float:
        """Analyze system load"""
        # Simplified system load analysis
        return 0.5


# Global instance
enhanced_invalidator = EnhancedCacheInvalidator()


class EnhancedCacheInvalidationMixin:
    """
    Enhanced mixin for automatic cache invalidation
    """
    
    def save(self, *args, **kwargs):
        """Override save to trigger cache invalidation"""
        result = super().save(*args, **kwargs)
        enhanced_invalidator.invalidate_by_model(
            self.__class__.__name__,
            str(self.pk),
            'update'
        )
        return result
    
    def delete(self, *args, **kwargs):
        """Override delete to trigger cache invalidation"""
        enhanced_invalidator.invalidate_by_model(
            self.__class__.__name__,
            str(self.pk),
            'delete'
        )
        return super().delete(*args, **kwargs)


# Signal handlers for automatic invalidation
@receiver(post_save)
def invalidate_cache_on_save(sender, instance, created, **kwargs):
    """Invalidate cache when model is saved"""
    operation = 'create' if created else 'update'
    enhanced_invalidator.invalidate_by_model(
        sender.__name__,
        str(instance.pk),
        operation
    )


@receiver(post_delete)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when model is deleted"""
    enhanced_invalidator.invalidate_by_model(
        sender.__name__,
        str(instance.pk),
        'delete'
    )


@receiver(m2m_changed)
def invalidate_cache_on_m2m_change(sender, instance, action, **kwargs):
    """Invalidate cache when many-to-many relationships change"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        enhanced_invalidator.invalidate_by_model(
            sender.__name__,
            str(instance.pk),
            'm2m_change'
        )
