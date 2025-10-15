"""
Database connection middleware for connection pooling and monitoring.
"""

import time
import logging
from typing import Optional

from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class DatabaseConnectionMiddleware(MiddlewareMixin):
    """
    Middleware for database connection pooling and monitoring.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.connection_stats = {
            'total_requests': 0,
            'total_queries': 0,
            'total_time': 0,
            'slow_queries': 0,
            'connection_errors': 0,
        }
    
    def process_request(self, request):
        """Process request and start connection monitoring."""
        # Start timing
        request._db_start_time = time.time()
        request._db_initial_queries = len(connection.queries)
        
        # Log connection pool status
        if hasattr(connection, 'pool') and connection.pool:
            pool_stats = {
                'active_connections': connection.pool._pool.qsize(),
                'max_connections': connection.pool._max_connections,
                'min_connections': connection.pool._min_connections,
            }
            logger.debug(f"Database pool status: {pool_stats}")
    
    def process_response(self, request, response):
        """Process response and log database statistics."""
        if hasattr(request, '_db_start_time'):
            # Calculate database time
            db_time = time.time() - request._db_start_time
            query_count = len(connection.queries) - getattr(request, '_db_initial_queries', 0)
            
            # Update statistics
            self.connection_stats['total_requests'] += 1
            self.connection_stats['total_queries'] += query_count
            self.connection_stats['total_time'] += db_time
            
            # Check for slow queries
            slow_query_threshold = getattr(settings, 'DATABASE_MONITORING', {}).get('SLOW_QUERY_THRESHOLD', 1.0)
            if db_time > slow_query_threshold:
                self.connection_stats['slow_queries'] += 1
                logger.warning(f"Slow database request: {request.path} took {db_time:.2f}s with {query_count} queries")
            
            # Log database performance
            if getattr(settings, 'DATABASE_MONITORING', {}).get('LOG_SLOW_QUERIES', False):
                logger.info(f"Database request: {request.path} - {query_count} queries in {db_time:.3f}s")
            
            # Store in request for debugging
            request._db_performance = {
                'query_count': query_count,
                'db_time': db_time,
                'queries': connection.queries[-query_count:] if query_count > 0 else []
            }
        
        return response
    
    def process_exception(self, request, exception):
        """Handle database connection errors."""
        if 'database' in str(exception).lower() or 'connection' in str(exception).lower():
            self.connection_stats['connection_errors'] += 1
            logger.error(f"Database connection error: {exception}")
        
        return None
    
    def get_connection_stats(self):
        """Get database connection statistics."""
        return {
            **self.connection_stats,
            'average_queries_per_request': (
                self.connection_stats['total_queries'] / max(self.connection_stats['total_requests'], 1)
            ),
            'average_db_time': (
                self.connection_stats['total_time'] / max(self.connection_stats['total_requests'], 1)
            ),
            'slow_query_rate': (
                self.connection_stats['slow_queries'] / max(self.connection_stats['total_requests'], 1)
            ),
        }


class CachePerformanceMiddleware(MiddlewareMixin):
    """
    Middleware for cache performance monitoring.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0,
        }
    
    def process_request(self, request):
        """Start cache monitoring."""
        request._cache_start_time = time.time()
        request._cache_operations = []
    
    def process_response(self, request, response):
        """Process response and log cache statistics."""
        if hasattr(request, '_cache_start_time'):
            cache_time = time.time() - request._cache_start_time
            
            # Log cache performance
            if cache_time > 0.1:  # More than 100ms
                logger.info(f"Cache operations for {request.path}: {len(request._cache_operations)} operations in {cache_time:.3f}s")
        
        return response
    
    def get_cache_stats(self):
        """Get cache statistics."""
        total_operations = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / max(total_operations, 1)) * 100
        
        return {
            **self.cache_stats,
            'hit_rate': hit_rate,
            'total_operations': total_operations,
        }


class DatabaseHealthCheckMiddleware(MiddlewareMixin):
    """
    Middleware for database health checks.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.last_health_check = 0
        self.health_check_interval = getattr(settings, 'DATABASE_HEALTH_CHECK', {}).get('INTERVAL', 30)
        self.health_check_timeout = getattr(settings, 'DATABASE_HEALTH_CHECK', {}).get('TIMEOUT', 5)
    
    def process_request(self, request):
        """Perform periodic database health checks."""
        current_time = time.time()
        
        if current_time - self.last_health_check > self.health_check_interval:
            self._perform_health_check()
            self.last_health_check = current_time
    
    def _perform_health_check(self):
        """Perform database health check."""
        try:
            start_time = time.time()
            
            # Simple health check query
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            health_check_time = time.time() - start_time
            
            if health_check_time > self.health_check_timeout:
                logger.warning(f"Database health check took {health_check_time:.3f}s (threshold: {self.health_check_timeout}s)")
            
            logger.debug(f"Database health check passed in {health_check_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
    
    def process_response(self, request, response):
        """Add database health status to response headers."""
        if getattr(settings, 'DATABASE_HEALTH_CHECK', {}).get('ENABLED', False):
            # Add health check timestamp to response headers
            response['X-Database-Health-Check'] = str(int(self.last_health_check))
        
        return response
