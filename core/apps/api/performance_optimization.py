"""
Performance optimization with database query optimization and advanced caching.
"""

from django.core.cache import cache
from django.db import models, connection
from django.db.models import Prefetch, Q, F, Count, Avg, Max, Min
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class DatabaseQueryOptimizer:
    """
    Advanced database query optimization with intelligent caching.
    """
    
    def __init__(self):
        self.query_cache = {}
        self.optimization_rules = {
            'tickets': self._optimize_ticket_queries,
            'users': self._optimize_user_queries,
            'organizations': self._optimize_organization_queries,
            'knowledge_base': self._optimize_knowledge_base_queries,
            'field_service': self._optimize_field_service_queries,
        }
    
    def optimize_queryset(self, queryset: models.QuerySet, model_name: str, 
                         include_related: List[str] = None, 
                         prefetch_related: List[str] = None) -> models.QuerySet:
        """
        Optimize queryset with intelligent query optimization.
        
        Args:
            queryset: Base queryset to optimize
            model_name: Name of the model
            include_related: List of related fields to select_related
            prefetch_related: List of related fields to prefetch_related
            
        Returns:
            Optimized queryset
        """
        try:
            # Apply model-specific optimization
            if model_name in self.optimization_rules:
                queryset = self.optimization_rules[model_name](queryset)
            
            # Apply generic optimizations
            queryset = self._apply_generic_optimizations(queryset, include_related, prefetch_related)
            
            # Apply query analysis and optimization
            queryset = self._analyze_and_optimize_queries(queryset)
            
            return queryset
            
        except Exception as e:
            logger.error(f"Query optimization error: {e}")
            return queryset
    
    def _optimize_ticket_queries(self, queryset: models.QuerySet) -> models.QuerySet:
        """Optimize ticket-related queries."""
        return queryset.select_related(
            'organization', 'customer', 'assigned_agent', 'created_by'
        ).prefetch_related(
            'comments', 'attachments', 'tags', 'comments__author'
        ).annotate(
            comment_count=Count('comments'),
            attachment_count=Count('attachments'),
            tag_count=Count('tags')
        )
    
    def _optimize_user_queries(self, queryset: models.QuerySet) -> models.QuerySet:
        """Optimize user-related queries."""
        return queryset.select_related(
            'organization', 'profile'
        ).prefetch_related(
            'tickets', 'assigned_tickets', 'comments'
        ).annotate(
            ticket_count=Count('tickets'),
            assigned_ticket_count=Count('assigned_tickets'),
            comment_count=Count('comments')
        )
    
    def _optimize_organization_queries(self, queryset: models.QuerySet) -> models.QuerySet:
        """Optimize organization-related queries."""
        return queryset.prefetch_related(
            'users', 'tickets', 'departments'
        ).annotate(
            user_count=Count('users'),
            ticket_count=Count('tickets'),
            department_count=Count('departments')
        )
    
    def _optimize_knowledge_base_queries(self, queryset: models.QuerySet) -> models.QuerySet:
        """Optimize knowledge base queries."""
        return queryset.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'feedback'
        ).annotate(
            feedback_count=Count('feedback'),
            average_rating=Avg('feedback__rating')
        )
    
    def _optimize_field_service_queries(self, queryset: models.QuerySet) -> models.QuerySet:
        """Optimize field service queries."""
        return queryset.select_related(
            'customer', 'technician', 'organization'
        ).prefetch_related(
            'attachments', 'reports'
        ).annotate(
            attachment_count=Count('attachments'),
            report_count=Count('reports')
        )
    
    def _apply_generic_optimizations(self, queryset: models.QuerySet, 
                                   include_related: List[str] = None,
                                   prefetch_related: List[str] = None) -> models.QuerySet:
        """Apply generic query optimizations."""
        # Apply select_related for foreign keys
        if include_related:
            queryset = queryset.select_related(*include_related)
        
        # Apply prefetch_related for many-to-many and reverse foreign keys
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        
        # Apply ordering for consistent results
        if not queryset.query.order_by:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def _analyze_and_optimize_queries(self, queryset: models.QuerySet) -> models.QuerySet:
        """Analyze and optimize queries based on usage patterns."""
        try:
            # Get query SQL for analysis
            query_sql = str(queryset.query)
            
            # Check for common optimization opportunities
            if 'JOIN' in query_sql.upper():
                # Optimize joins
                queryset = self._optimize_joins(queryset)
            
            if 'WHERE' in query_sql.upper():
                # Optimize where clauses
                queryset = self._optimize_where_clauses(queryset)
            
            if 'ORDER BY' in query_sql.upper():
                # Optimize ordering
                queryset = self._optimize_ordering(queryset)
            
            return queryset
            
        except Exception as e:
            logger.error(f"Query analysis error: {e}")
            return queryset
    
    def _optimize_joins(self, queryset: models.QuerySet) -> models.QuerySet:
        """Optimize JOIN operations."""
        # This would implement specific JOIN optimizations
        return queryset
    
    def _optimize_where_clauses(self, queryset: models.QuerySet) -> models.QuerySet:
        """Optimize WHERE clauses."""
        # This would implement specific WHERE clause optimizations
        return queryset
    
    def _optimize_ordering(self, queryset: models.QuerySet) -> models.QuerySet:
        """Optimize ORDER BY clauses."""
        # This would implement specific ordering optimizations
        return queryset


class AdvancedCachingSystem:
    """
    Advanced caching system with intelligent cache management.
    """
    
    def __init__(self):
        self.cache_configs = {
            'tickets': {'ttl': 300, 'max_size': 1000},  # 5 minutes, 1000 items
            'users': {'ttl': 600, 'max_size': 500},     # 10 minutes, 500 items
            'organizations': {'ttl': 1800, 'max_size': 100},  # 30 minutes, 100 items
            'knowledge_base': {'ttl': 900, 'max_size': 200},  # 15 minutes, 200 items
            'field_service': {'ttl': 600, 'max_size': 300},  # 10 minutes, 300 items
        }
        
        self.cache_stats = {}
        self.cache_invalidation_rules = {}
    
    def get_cached_data(self, cache_key: str, model_name: str, 
                       fetch_func: callable, *args, **kwargs) -> Any:
        """
        Get cached data with intelligent cache management.
        
        Args:
            cache_key: Unique cache key
            model_name: Name of the model for cache configuration
            fetch_func: Function to fetch data if not cached
            *args: Arguments for fetch function
            **kwargs: Keyword arguments for fetch function
            
        Returns:
            Cached or fetched data
        """
        try:
            # Check cache first
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                self._update_cache_stats(cache_key, 'hit')
                return cached_data
            
            # Fetch data if not cached
            data = fetch_func(*args, **kwargs)
            
            # Cache the data
            cache_config = self.cache_configs.get(model_name, {'ttl': 300, 'max_size': 1000})
            cache.set(cache_key, data, cache_config['ttl'])
            
            self._update_cache_stats(cache_key, 'miss')
            return data
            
        except Exception as e:
            logger.error(f"Cache error: {e}")
            # Fallback to direct fetch
            return fetch_func(*args, **kwargs)
    
    def invalidate_cache(self, pattern: str, model_name: str = None):
        """
        Invalidate cache based on pattern.
        
        Args:
            pattern: Cache key pattern to invalidate
            model_name: Optional model name for targeted invalidation
        """
        try:
            # This would implement cache invalidation logic
            # For now, we'll use a simple approach
            cache.delete_many([pattern])
            
            logger.info(f"Cache invalidated for pattern: {pattern}")
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def _update_cache_stats(self, cache_key: str, hit_type: str):
        """Update cache statistics."""
        if cache_key not in self.cache_stats:
            self.cache_stats[cache_key] = {'hits': 0, 'misses': 0}
        
        if hit_type == 'hit':
            self.cache_stats[cache_key]['hits'] += 1
        else:
            self.cache_stats[cache_key]['misses'] += 1
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = sum(stats['hits'] for stats in self.cache_stats.values())
        total_misses = sum(stats['misses'] for stats in self.cache_stats.values())
        total_requests = total_hits + total_misses
        
        return {
            'total_requests': total_requests,
            'total_hits': total_hits,
            'total_misses': total_misses,
            'hit_rate': total_hits / total_requests if total_requests > 0 else 0,
            'cache_stats': self.cache_stats
        }


class PerformanceMonitor:
    """
    Performance monitoring and optimization.
    """
    
    def __init__(self):
        self.performance_metrics = {}
        self.query_metrics = {}
        self.response_metrics = {}
    
    def monitor_query_performance(self, query_func: callable, *args, **kwargs) -> Tuple[Any, Dict]:
        """
        Monitor query performance.
        
        Args:
            query_func: Function to monitor
            *args: Arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Tuple of (result, performance_metrics)
        """
        start_time = time.time()
        start_queries = len(connection.queries)
        
        try:
            result = query_func(*args, **kwargs)
            
            end_time = time.time()
            end_queries = len(connection.queries)
            
            performance_metrics = {
                'execution_time': end_time - start_time,
                'query_count': end_queries - start_queries,
                'queries': connection.queries[start_queries:end_queries],
                'timestamp': timezone.now().isoformat()
            }
            
            # Store metrics
            query_key = f"query_{hash(str(args) + str(kwargs))}"
            self.query_metrics[query_key] = performance_metrics
            
            return result, performance_metrics
            
        except Exception as e:
            logger.error(f"Query performance monitoring error: {e}")
            return None, {'error': str(e)}
    
    def monitor_response_performance(self, response_func: callable, *args, **kwargs) -> Tuple[Any, Dict]:
        """
        Monitor response performance.
        
        Args:
            response_func: Function to monitor
            *args: Arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Tuple of (result, performance_metrics)
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            result = response_func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            performance_metrics = {
                'execution_time': end_time - start_time,
                'memory_usage': end_memory - start_memory,
                'timestamp': timezone.now().isoformat()
            }
            
            # Store metrics
            response_key = f"response_{hash(str(args) + str(kwargs))}"
            self.response_metrics[response_key] = performance_metrics
            
            return result, performance_metrics
            
        except Exception as e:
            logger.error(f"Response performance monitoring error: {e}")
            return None, {'error': str(e)}
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except:
            return 0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            'query_metrics': self.query_metrics,
            'response_metrics': self.response_metrics,
            'total_queries': len(self.query_metrics),
            'total_responses': len(self.response_metrics),
            'average_query_time': self._calculate_average_query_time(),
            'average_response_time': self._calculate_average_response_time()
        }
    
    def _calculate_average_query_time(self) -> float:
        """Calculate average query time."""
        if not self.query_metrics:
            return 0.0
        
        total_time = sum(metrics['execution_time'] for metrics in self.query_metrics.values())
        return total_time / len(self.query_metrics)
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time."""
        if not self.response_metrics:
            return 0.0
        
        total_time = sum(metrics['execution_time'] for metrics in self.response_metrics.values())
        return total_time / len(self.response_metrics)


def performance_optimized_view(model_name: str, include_related: List[str] = None, 
                              prefetch_related: List[str] = None):
    """
    Decorator for performance-optimized views.
    
    Args:
        model_name: Name of the model
        include_related: List of related fields to select_related
        prefetch_related: List of related fields to prefetch_related
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Create performance monitor
            monitor = PerformanceMonitor()
            
            # Create query optimizer
            optimizer = DatabaseQueryOptimizer()
            
            # Create caching system
            caching_system = AdvancedCachingSystem()
            
            # Monitor performance
            result, metrics = monitor.monitor_response_performance(
                view_func, request, *args, **kwargs
            )
            
            # Add performance headers
            if hasattr(result, 'data'):
                result['X-Performance-Time'] = str(metrics.get('execution_time', 0))
                result['X-Performance-Memory'] = str(metrics.get('memory_usage', 0))
            
            return result
        
        return wrapper
    return decorator


def cached_view(cache_key_func: callable, ttl: int = 300, model_name: str = None):
    """
    Decorator for cached views.
    
    Args:
        cache_key_func: Function to generate cache key
        ttl: Time to live in seconds
        model_name: Model name for cache configuration
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key
            cache_key = cache_key_func(request, *args, **kwargs)
            
            # Create caching system
            caching_system = AdvancedCachingSystem()
            
            # Get cached data
            result = caching_system.get_cached_data(
                cache_key, model_name or 'default', view_func, request, *args, **kwargs
            )
            
            return result
        
        return wrapper
    return decorator


# Global instances
query_optimizer = DatabaseQueryOptimizer()
caching_system = AdvancedCachingSystem()
performance_monitor = PerformanceMonitor()
