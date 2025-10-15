"""
Optimized viewsets with advanced query optimization
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.db.models import Q, F, Count, Sum, Avg
import logging

from .query_optimizers import QueryOptimizer, AdvancedQueryOptimizer, PerformanceMonitor

logger = logging.getLogger(__name__)

class OptimizedTicketViewSet(viewsets.ModelViewSet):
    """
    Optimized ticket viewset with advanced query optimization
    """
    
    def get_queryset(self):
        """
        Get optimized queryset based on action
        """
        if self.action == 'list':
            return QueryOptimizer.optimize_ticket_queries()
        elif self.action == 'retrieve':
            return QueryOptimizer.optimize_ticket_queries()
        else:
            return super().get_queryset()
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with caching
        """
        import time
        start_time = time.time()
        
        # Get cached results if available
        cache_key = f"tickets_list_{request.user.id}_{request.GET.urlencode()}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            PerformanceMonitor.log_query_performance(
                'tickets_list_cached', 
                (time.time() - start_time) * 1000, 
                0
            )
            return Response(cached_result)
        
        # Get optimized queryset
        queryset = self.get_queryset()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        search_query = request.query_params.get('search')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            result = Response(serializer.data)
        
        # Cache the result
        cache.set(cache_key, result.data, 300)  # 5 minutes
        
        execution_time = (time.time() - start_time) * 1000
        PerformanceMonitor.log_query_performance(
            'tickets_list', 
            execution_time, 
            1
        )
        
        return result
    
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def retrieve(self, request, *args, **kwargs):
        """
        Optimized retrieve view with caching
        """
        import time
        start_time = time.time()
        
        ticket_id = kwargs.get('pk')
        cache_key = f"ticket_detail_{ticket_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            PerformanceMonitor.log_query_performance(
                'ticket_detail_cached', 
                (time.time() - start_time) * 1000, 
                0
            )
            return Response(cached_result)
        
        # Get optimized ticket
        ticket = QueryOptimizer.optimize_ticket_detail(ticket_id)
        serializer = self.get_serializer(ticket)
        
        # Cache the result
        cache.set(cache_key, serializer.data, 600)  # 10 minutes
        
        execution_time = (time.time() - start_time) * 1000
        PerformanceMonitor.log_query_performance(
            'ticket_detail', 
            execution_time, 
            1
        )
        
        return Response(serializer.data)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Optimized create with transaction
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create ticket
        ticket = serializer.save(created_by=request.user)
        
        # Invalidate related caches
        cache.delete_many([
            f"tickets_list_{request.user.id}_*",
            "dashboard_stats_*"
        ])
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Optimized update with transaction
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Update ticket
        ticket = serializer.save()
        
        # Invalidate related caches
        cache.delete_many([
            f"tickets_list_{request.user.id}_*",
            f"ticket_detail_{ticket.id}",
            "dashboard_stats_*"
        ])
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get ticket statistics with single query
        """
        import time
        start_time = time.time()
        
        cache_key = f"ticket_stats_{request.user.id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        # Get optimized statistics
        stats = QueryOptimizer.optimize_dashboard_stats()
        
        # Cache the result
        cache.set(cache_key, stats, 300)  # 5 minutes
        
        execution_time = (time.time() - start_time) * 1000
        PerformanceMonitor.log_query_performance(
            'ticket_stats', 
            execution_time, 
            1
        )
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Optimized search with full-text search
        """
        import time
        start_time = time.time()
        
        search_term = request.query_params.get('q', '')
        if not search_term:
            return Response({'results': [], 'count': 0})
        
        cache_key = f"ticket_search_{search_term}_{request.user.id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        # Get optimized search results
        tickets, articles = AdvancedQueryOptimizer.optimized_search_queries(search_term)
        
        # Serialize results
        ticket_serializer = self.get_serializer(tickets, many=True)
        
        result = {
            'tickets': ticket_serializer.data,
            'count': tickets.count()
        }
        
        # Cache the result
        cache.set(cache_key, result, 300)  # 5 minutes
        
        execution_time = (time.time() - start_time) * 1000
        PerformanceMonitor.log_query_performance(
            'ticket_search', 
            execution_time, 
            1
        )
        
        return Response(result)

class OptimizedKnowledgeBaseViewSet(viewsets.ModelViewSet):
    """
    Optimized knowledge base viewset
    """
    
    def get_queryset(self):
        """
        Get optimized knowledge base queryset
        """
        return QueryOptimizer.optimize_knowledge_base_queries()
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with caching
        """
        import time
        start_time = time.time()
        
        cache_key = f"knowledge_base_list_{request.GET.urlencode()}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        queryset = self.get_queryset()
        
        # Apply filters
        category_filter = request.query_params.get('category')
        search_query = request.query_params.get('search')
        
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query)
            )
        
        serializer = self.get_serializer(queryset, many=True)
        result = serializer.data
        
        # Cache the result
        cache.set(cache_key, result, 900)  # 15 minutes
        
        execution_time = (time.time() - start_time) * 1000
        PerformanceMonitor.log_query_performance(
            'knowledge_base_list', 
            execution_time, 
            1
        )
        
        return Response(result)

class OptimizedDashboardViewSet(viewsets.ViewSet):
    """
    Optimized dashboard viewset
    """
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def list(self, request):
        """
        Get dashboard statistics with single optimized query
        """
        import time
        start_time = time.time()
        
        cache_key = f"dashboard_stats_{request.user.id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        # Get optimized statistics
        stats = QueryOptimizer.optimize_dashboard_stats()
        
        # Cache the result
        cache.set(cache_key, stats, 300)  # 5 minutes
        
        execution_time = (time.time() - start_time) * 1000
        PerformanceMonitor.log_query_performance(
            'dashboard_stats', 
            execution_time, 
            1
        )
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def performance(self, request):
        """
        Get query performance statistics
        """
        stats = PerformanceMonitor.get_performance_stats()
        return Response(stats)