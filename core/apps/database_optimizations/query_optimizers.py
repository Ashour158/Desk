"""
Advanced database query optimization utilities
"""

from django.db import models
from django.db.models import Prefetch, Q, F, Count, Sum, Avg, Max, Min
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """
    Advanced query optimization utilities
    """
    
    @staticmethod
    def optimize_ticket_queries():
        """
        Optimize ticket-related queries with select_related and prefetch_related
        """
        from core.apps.tickets.models import Ticket, TicketComment
        
        # Optimized ticket list query
        tickets = Ticket.objects.select_related(
            'assigned_agent',
            'created_by',
            'category'
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=TicketComment.objects.select_related('author').order_by('-created_at')
            ),
            'tags',
            'attachments'
        ).order_by('-created_at')
        
        return tickets
    
    @staticmethod
    def optimize_ticket_detail(ticket_id):
        """
        Optimize single ticket detail query
        """
        from core.apps.tickets.models import Ticket, TicketComment
        
        ticket = Ticket.objects.select_related(
            'assigned_agent',
            'created_by',
            'category',
            'priority',
            'status'
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=TicketComment.objects.select_related('author').order_by('-created_at')
            ),
            'tags',
            'attachments',
            'work_orders__assigned_technician',
            'work_orders__equipment'
        ).get(id=ticket_id)
        
        return ticket
    
    @staticmethod
    def optimize_dashboard_stats():
        """
        Optimize dashboard statistics with single query
        """
        from core.apps.tickets.models import Ticket
        
        # Single query for all dashboard statistics
        stats = Ticket.objects.aggregate(
            total_tickets=Count('id'),
            open_tickets=Count('id', filter=Q(status='open')),
            closed_tickets=Count('id', filter=Q(status='closed')),
            high_priority=Count('id', filter=Q(priority='high')),
            avg_resolution_time=Avg('resolution_time'),
            oldest_ticket=Min('created_at'),
            newest_ticket=Max('created_at')
        )
        
        return stats
    
    @staticmethod
    def optimize_knowledge_base_queries():
        """
        Optimize knowledge base queries
        """
        from core.apps.knowledge_base.models import Article, Category
        
        articles = Article.objects.select_related(
            'category',
            'author'
        ).prefetch_related(
            'tags',
            'related_articles'
        ).filter(is_published=True).order_by('-updated_at')
        
        return articles
    
    @staticmethod
    def optimize_user_queries():
        """
        Optimize user-related queries
        """
        from core.apps.accounts.models import User
        
        users = User.objects.select_related(
            'profile',
            'organization'
        ).prefetch_related(
            'groups',
            'user_permissions',
            'tickets_created',
            'tickets_assigned'
        )
        
        return users
    
    @staticmethod
    def optimize_work_order_queries():
        """
        Optimize work order queries
        """
        from core.apps.workflow_automation.models import WorkOrder
        
        work_orders = WorkOrder.objects.select_related(
            'ticket',
            'assigned_technician',
            'equipment',
            'location'
        ).prefetch_related(
            'steps',
            'attachments',
            'time_entries'
        ).order_by('-created_at')
        
        return work_orders
    
    @staticmethod
    def get_cached_query(key, query_func, timeout=300):
        """
        Get cached query result
        """
        result = cache.get(key)
        if result is None:
            result = query_func()
            cache.set(key, result, timeout)
            logger.info(f"Cached query result for key: {key}")
        else:
            logger.info(f"Retrieved cached query result for key: {key}")
        
        return result
    
    @staticmethod
    def invalidate_cache_pattern(pattern):
        """
        Invalidate cache entries matching pattern
        """
        from django.core.cache import cache
        cache.delete_many(cache.keys(pattern))
        logger.info(f"Invalidated cache entries matching pattern: {pattern}")

class AdvancedQueryOptimizer:
    """
    Advanced query optimization with caching and performance monitoring
    """
    
    @staticmethod
    def optimized_ticket_list_with_stats():
        """
        Get ticket list with statistics in single query
        """
        from core.apps.tickets.models import Ticket
        
        # Use subquery for statistics
        tickets = Ticket.objects.select_related(
            'assigned_agent',
            'created_by',
            'category'
        ).prefetch_related(
            'comments',
            'tags'
        ).annotate(
            comment_count=Count('comments'),
            days_since_created=F('created_at') - F('created_at'),
            is_overdue=Q(priority='high', created_at__lt=F('created_at') - models.F('created_at'))
        ).order_by('-created_at')
        
        return tickets
    
    @staticmethod
    def optimized_search_queries(search_term):
        """
        Optimize search queries with full-text search
        """
        from core.apps.tickets.models import Ticket
        from core.apps.knowledge_base.models import Article
        
        # Use database full-text search if available
        if hasattr(Ticket, 'objects') and hasattr(Ticket.objects, 'search'):
            tickets = Ticket.objects.search(search_term).select_related(
                'assigned_agent',
                'created_by'
            )
        else:
            # Fallback to Q objects
            tickets = Ticket.objects.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(comments__content__icontains=search_term)
            ).select_related(
                'assigned_agent',
                'created_by'
            ).distinct()
        
        # Similar optimization for knowledge base
        if hasattr(Article, 'objects') and hasattr(Article.objects, 'search'):
            articles = Article.objects.search(search_term).select_related(
                'category',
                'author'
            )
        else:
            articles = Article.objects.filter(
                Q(title__icontains=search_term) |
                Q(content__icontains=search_term) |
                Q(summary__icontains=search_term)
            ).select_related(
                'category',
                'author'
            ).distinct()
        
        return tickets, articles
    
    @staticmethod
    def bulk_optimize_queries(queries):
        """
        Optimize multiple queries in bulk
        """
        results = {}
        
        for query_name, query_func in queries.items():
            try:
                results[query_name] = query_func()
            except Exception as e:
                logger.error(f"Error in query {query_name}: {e}")
                results[query_name] = None
        
        return results

class PerformanceMonitor:
    """
    Query performance monitoring
    """
    
    @staticmethod
    def log_query_performance(query_name, execution_time, query_count):
        """
        Log query performance metrics
        """
        logger.info(f"Query {query_name}: {execution_time}ms, {query_count} queries")
        
        # Store in cache for monitoring
        cache_key = f"query_performance_{query_name}"
        cache.set(cache_key, {
            'execution_time': execution_time,
            'query_count': query_count,
            'timestamp': models.DateTimeField().auto_now
        }, 3600)  # 1 hour
    
    @staticmethod
    def get_performance_stats():
        """
        Get query performance statistics
        """
        stats = {}
        
        # Get cached performance data
        for key in cache.keys("query_performance_*"):
            data = cache.get(key)
            if data:
                query_name = key.replace("query_performance_", "")
                stats[query_name] = data
        
        return stats

# Export optimization functions
__all__ = [
    'QueryOptimizer',
    'AdvancedQueryOptimizer', 
    'PerformanceMonitor'
]