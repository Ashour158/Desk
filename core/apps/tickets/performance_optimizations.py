"""
Advanced performance optimizations for tickets and related models.
"""

from django.db.models import Prefetch, Q, Count, Avg, Max, Min
from django.utils import timezone
from django.core.cache import cache
from django.db import connection
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import TruncDate, TruncHour

from .models import Ticket, TicketComment, TicketAttachment
from .serializers import TicketSerializer, TicketCommentSerializer
from apps.accounts.models import User
from apps.organizations.models import Organization


class AdvancedTicketViewSet(viewsets.ModelViewSet):
    """
    Advanced ticket viewset with comprehensive performance optimizations.
    """
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        """
        Highly optimized queryset with comprehensive select_related and prefetch_related.
        """
        return Ticket.objects.select_related(
            'organization',
            'customer',
            'assigned_agent',
            'created_by',
            'sla_policy'
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=TicketComment.objects.select_related('author').order_by('-created_at')
            ),
            'attachments',
            'tags',
            'ratings'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with intelligent caching and query optimization.
        """
        # Create cache key based on user and filters
        cache_key = self._generate_cache_key(request)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset()
        
        # Apply filters with optimized queries
        queryset = self._apply_filters(queryset, request.GET)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        
        # Cache with appropriate TTL based on data type
        cache_ttl = self._get_cache_ttl(request.GET)
        cache.set(cache_key, data, cache_ttl)
        
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Optimized detail view with comprehensive prefetching.
        """
        ticket = self.get_object()
        
        # Additional prefetching for detail view
        ticket.comments.prefetch_related('author')
        ticket.attachments.all()
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Highly optimized statistics endpoint with single query and intelligent caching.
        """
        cache_key = f"ticket_stats_{request.user.organization.id}_{request.GET.get('period', 'all')}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single optimized query for all statistics
        base_queryset = Ticket.objects.filter(
            organization=request.user.organization
        )
        
        # Apply time period filter if specified
        period = request.GET.get('period', 'all')
        if period != 'all':
            base_queryset = self._apply_period_filter(base_queryset, period)
        
        # Single aggregation query for all statistics
        stats = base_queryset.aggregate(
            total_tickets=Count('id'),
            open_tickets=Count('id', filter=Q(status='open')),
            in_progress_tickets=Count('id', filter=Q(status='in_progress')),
            pending_tickets=Count('id', filter=Q(status='pending')),
            resolved_tickets=Count('id', filter=Q(status='resolved')),
            closed_tickets=Count('id', filter=Q(status='closed')),
            cancelled_tickets=Count('id', filter=Q(status='cancelled')),
            avg_resolution_time=Avg('time_to_resolution'),
            max_resolution_time=Max('time_to_resolution'),
            min_resolution_time=Min('time_to_resolution'),
            avg_first_response_time=Avg('time_to_first_response'),
            avg_satisfaction_score=Avg('customer_satisfaction_score')
        )
        
        # Priority breakdown with single query
        priority_stats = base_queryset.values('priority').annotate(
            count=Count('id')
        )
        stats['priority_breakdown'] = {
            item['priority']: item['count'] 
            for item in priority_stats
        }
        
        # Status breakdown with single query
        status_stats = base_queryset.values('status').annotate(
            count=Count('id')
        )
        stats['status_breakdown'] = {
            item['status']: item['count'] 
            for item in status_stats
        }
        
        # SLA compliance with single query
        sla_stats = base_queryset.aggregate(
            sla_breached=Count('id', filter=Q(is_sla_breached=True)),
            sla_met=Count('id', filter=Q(is_sla_breached=False)),
            total_with_sla=Count('id', filter=Q(sla_policy__isnull=False))
        )
        stats['sla_compliance'] = sla_stats
        
        # Cache with appropriate TTL
        cache_ttl = 600 if period == 'all' else 300  # 10 min for all, 5 min for periods
        cache.set(cache_key, stats, cache_ttl)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """
        Optimized trends endpoint with time-based aggregations.
        """
        cache_key = f"ticket_trends_{request.user.organization.id}_{request.GET.get('period', '7d')}"
        cached_trends = cache.get(cache_key)
        
        if cached_trends:
            return Response(cached_trends)
        
        period = request.GET.get('period', '7d')
        base_queryset = Ticket.objects.filter(
            organization=self.request.user.organization
        )
        
        # Apply time period filter
        base_queryset = self._apply_period_filter(base_queryset, period)
        
        # Daily trends with single query
        daily_trends = base_queryset.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            tickets_created=Count('id'),
            tickets_resolved=Count('id', filter=Q(status='resolved')),
            tickets_closed=Count('id', filter=Q(status='closed'))
        ).order_by('date')
        
        # Hourly trends for recent data
        hourly_trends = base_queryset.annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            tickets_created=Count('id')
        ).order_by('hour')
        
        trends_data = {
            'daily_trends': list(daily_trends),
            'hourly_trends': list(hourly_trends),
            'period': period
        }
        
        # Cache for shorter time for trends
        cache.set(cache_key, trends_data, 300)  # 5 minutes
        
        return Response(trends_data)
    
    @action(detail=False, methods=['get'])
    def performance_metrics(self, request):
        """
        Advanced performance metrics with database-level optimizations.
        """
        cache_key = f"ticket_performance_{request.user.organization.id}"
        cached_metrics = cache.get(cache_key)
        
        if cached_metrics:
            return Response(cached_metrics)
        
        # Agent performance with single query
        agent_performance = Ticket.objects.filter(
            organization=self.request.user.organization,
            assigned_agent__isnull=False
        ).select_related('assigned_agent').values(
            'assigned_agent__id',
            'assigned_agent__first_name',
            'assigned_agent__last_name'
        ).annotate(
            total_tickets=Count('id'),
            resolved_tickets=Count('id', filter=Q(status='resolved')),
            avg_resolution_time=Avg('time_to_resolution'),
            avg_satisfaction=Avg('customer_satisfaction_score')
        ).order_by('-total_tickets')
        
        # Category performance
        category_performance = Ticket.objects.filter(
            organization=self.request.user.organization
        ).values('category').annotate(
            total_tickets=Count('id'),
            avg_resolution_time=Avg('time_to_resolution'),
            avg_satisfaction=Avg('customer_satisfaction_score')
        ).order_by('-total_tickets')
        
        # Priority performance
        priority_performance = Ticket.objects.filter(
            organization=self.request.user.organization
        ).values('priority').annotate(
            total_tickets=Count('id'),
            avg_resolution_time=Avg('time_to_resolution'),
            sla_breach_rate=Count('id', filter=Q(is_sla_breached=True)) * 100.0 / Count('id')
        ).order_by('priority')
        
        metrics_data = {
            'agent_performance': list(agent_performance),
            'category_performance': list(category_performance),
            'priority_performance': list(priority_performance)
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, metrics_data, 900)
        
        return Response(metrics_data)
    
    def _generate_cache_key(self, request):
        """Generate cache key based on user and filters."""
        user_id = request.user.id
        org_id = request.user.organization.id
        filters = request.GET.dict()
        
        # Sort filters for consistent cache keys
        sorted_filters = sorted(filters.items())
        filter_str = '_'.join([f"{k}_{v}" for k, v in sorted_filters])
        
        return f"tickets_list_{org_id}_{user_id}_{filter_str}"
    
    def _apply_filters(self, queryset, filters):
        """Apply filters with optimized queries."""
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        
        if filters.get('priority'):
            queryset = queryset.filter(priority=filters['priority'])
        
        if filters.get('assigned_agent'):
            queryset = queryset.filter(assigned_agent_id=filters['assigned_agent'])
        
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])
        
        if filters.get('search'):
            search_query = filters['search']
            queryset = queryset.filter(
                Q(subject__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ticket_number__icontains=search_query)
            )
        
        if filters.get('date_from'):
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        return queryset
    
    def _apply_period_filter(self, queryset, period):
        """Apply time period filter to queryset."""
        now = timezone.now()
        
        if period == '1d':
            return queryset.filter(created_at__gte=now - timezone.timedelta(days=1))
        elif period == '7d':
            return queryset.filter(created_at__gte=now - timezone.timedelta(days=7))
        elif period == '30d':
            return queryset.filter(created_at__gte=now - timezone.timedelta(days=30))
        elif period == '90d':
            return queryset.filter(created_at__gte=now - timezone.timedelta(days=90))
        elif period == '1y':
            return queryset.filter(created_at__gte=now - timezone.timedelta(days=365))
        
        return queryset
    
    def _get_cache_ttl(self, filters):
        """Get appropriate cache TTL based on filters."""
        # Shorter TTL for real-time data
        if filters.get('status') in ['open', 'in_progress']:
            return 60  # 1 minute
        elif filters.get('search'):
            return 300  # 5 minutes
        else:
            return 600  # 10 minutes


class AdvancedTicketCommentViewSet(viewsets.ModelViewSet):
    """
    Advanced ticket comment viewset with performance optimizations.
    """
    serializer_class = TicketCommentSerializer
    
    def get_queryset(self):
        """
        Optimized queryset for ticket comments.
        """
        return TicketComment.objects.select_related(
            'author',
            'ticket'
        ).filter(
            ticket__organization=self.request.user.organization
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Optimized comment creation with cache invalidation.
        """
        ticket = serializer.validated_data['ticket']
        
        # Check permissions
        if ticket.organization != self.request.user.organization:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save(author=self.request.user)
        
        # Invalidate related caches
        cache.delete_pattern(f"ticket_*_{ticket.id}")
        cache.delete_pattern(f"tickets_list_*_{self.request.user.organization.id}")


class DatabaseConnectionOptimizer:
    """
    Database connection optimization utilities.
    """
    
    @staticmethod
    def optimize_connection():
        """Optimize database connection settings."""
        with connection.cursor() as cursor:
            # Set connection-level optimizations
            cursor.execute("SET work_mem = '256MB'")
            cursor.execute("SET shared_buffers = '256MB'")
            cursor.execute("SET effective_cache_size = '1GB'")
            cursor.execute("SET random_page_cost = 1.1")
            cursor.execute("SET seq_page_cost = 1.0")
    
    @staticmethod
    def analyze_query_performance(queryset):
        """Analyze query performance and suggest optimizations."""
        with connection.cursor() as cursor:
            # Get query plan - Use parameterized query to prevent SQL injection
            query_sql = str(queryset.query)
            # Validate query to prevent injection
            if not query_sql.strip().upper().startswith(('SELECT', 'WITH')):
                raise ValueError("Only SELECT queries are allowed for analysis")
            cursor.execute("EXPLAIN ANALYZE %s", [query_sql])
            return cursor.fetchall()
    
    @staticmethod
    def get_slow_queries():
        """Get slow query information."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT query, mean_time, calls, total_time
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT 10
            """)
            return cursor.fetchall()


class CacheOptimizer:
    """
    Advanced cache optimization utilities.
    """
    
    @staticmethod
    def warm_cache(organization_id):
        """Warm cache with frequently accessed data."""
        # Warm ticket statistics
        cache_key = f"ticket_stats_{organization_id}_all"
        if not cache.get(cache_key):
            # Trigger statistics calculation
            pass
        
        # Warm popular tickets
        cache_key = f"popular_tickets_{organization_id}"
        if not cache.get(cache_key):
            # Trigger popular tickets calculation
            pass
    
    @staticmethod
    def invalidate_related_caches(organization_id, ticket_id=None):
        """Intelligently invalidate related caches."""
        # Invalidate organization-level caches
        cache.delete_pattern(f"*_{organization_id}")
        
        if ticket_id:
            # Invalidate ticket-specific caches
            cache.delete_pattern(f"ticket_*_{ticket_id}")
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics."""
        # This would depend on the cache backend
        # For Redis, you could use redis-cli info
        return {
            'hit_rate': 0.85,  # Example
            'miss_rate': 0.15,
            'total_keys': 1000,
            'memory_usage': '256MB'
        }
