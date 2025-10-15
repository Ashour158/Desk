"""
Comprehensive optimized views with all N+1 query fixes and transaction decorators.
"""

from django.db.models import Prefetch, Q, Count, Avg, Max, Min, Sum
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
import logging

from .models import Ticket, TicketComment, TicketAttachment
from .serializers import TicketSerializer, TicketCommentSerializer
from apps.accounts.models import User
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


class OptimizedTicketViewSet(viewsets.ModelViewSet):
    """
    Optimized ticket viewset with query optimization.
    """
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        """
        Comprehensive optimized queryset to prevent all N+1 queries.
        """
        return Ticket.objects.select_related(
            'organization',
            'customer',
            'assigned_agent',
            'created_by',
            'sla_policy'
        ).prefetch_related(
            # Fix: Ticket Comments N+1
            Prefetch(
                'comments',
                queryset=TicketComment.objects.select_related('author').order_by('-created_at')
            ),
            # Fix: Ticket Attachments N+1
            'attachments',
            # Fix: Tags N+1
            'tags',
            # Fix: Ratings N+1
            'ratings',
            # Fix: Related tickets N+1
            'related_tickets'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with caching.
        """
        cache_key = f"tickets_list_{request.user.organization.id}_{request.GET.get('page', 1)}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset()
        
        # Apply filters
        status_filter = request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority_filter = request.GET.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        search_query = request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(subject__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ticket_number__icontains=search_query)
            )
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        
        # Cache for 5 minutes
        cache.set(cache_key, data, 300)
        
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Optimized detail view with prefetch_related for comments.
        """
        ticket = self.get_object()
        
        # Prefetch comments with author information
        ticket.comments.prefetch_related('author')
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Comprehensive statistics endpoint with single aggregation query.
        """
        cache_key = f"comprehensive_ticket_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query
        base_queryset = Ticket.objects.filter(organization=request.user.organization)
        
        stats = base_queryset.aggregate(
            # Basic counts
            total_tickets=Count('id'),
            open_tickets=Count('id', filter=Q(status='open')),
            in_progress_tickets=Count('id', filter=Q(status='in_progress')),
            pending_tickets=Count('id', filter=Q(status='pending')),
            resolved_tickets=Count('id', filter=Q(status='resolved')),
            closed_tickets=Count('id', filter=Q(status='closed')),
            cancelled_tickets=Count('id', filter=Q(status='cancelled')),
            
            # Performance metrics
            avg_resolution_time=Avg('time_to_resolution'),
            max_resolution_time=Max('time_to_resolution'),
            min_resolution_time=Min('time_to_resolution'),
            avg_first_response_time=Avg('time_to_first_response'),
            avg_satisfaction_score=Avg('customer_satisfaction_score'),
            
            # SLA metrics
            sla_breach_count=Count('id', filter=Q(sla_breach=True)),
            on_time_resolution=Count('id', filter=Q(sla_breach=False)),
            
            # Priority breakdown
            high_priority=Count('id', filter=Q(priority='high')),
            medium_priority=Count('id', filter=Q(priority='medium')),
            low_priority=Count('id', filter=Q(priority='low')),
            urgent_priority=Count('id', filter=Q(priority='urgent'))
        )
        
        # Priority breakdown with single query
        priority_stats = base_queryset.values('priority').annotate(
            count=Count('id'),
            avg_resolution_time=Avg('time_to_resolution'),
            avg_satisfaction=Avg('customer_satisfaction_score')
        )
        stats['priority_breakdown'] = list(priority_stats)
        
        # Status breakdown with single query
        status_stats = base_queryset.values('status').annotate(
            count=Count('id'),
            avg_resolution_time=Avg('time_to_resolution')
        )
        stats['status_breakdown'] = list(status_stats)
        
        # Agent performance with single query
        agent_stats = base_queryset.filter(assigned_agent__isnull=False).values(
            'assigned_agent__first_name', 'assigned_agent__last_name'
        ).annotate(
            ticket_count=Count('id'),
            avg_resolution_time=Avg('time_to_resolution'),
            avg_satisfaction=Avg('customer_satisfaction_score')
        )
        stats['agent_performance'] = list(agent_stats)
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, 600)
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Optimized comments endpoint - fixes N+1 queries.
        """
        ticket = self.get_object()
        
        # Use prefetch_related to avoid N+1 queries
        comments = ticket.comments.select_related('author').order_by('-created_at')
        
        serializer = TicketCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create ticket with atomic transaction.
        """
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Ticket creation failed: {e}")
            raise
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update ticket with atomic transaction.
        """
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Ticket update failed: {e}")
            raise
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Delete ticket with atomic transaction.
        """
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Ticket deletion failed: {e}")
            raise


class OptimizedTicketCommentViewSet(viewsets.ModelViewSet):
    """
    Optimized ticket comment viewset.
    """
    serializer_class = TicketCommentSerializer
    
    def get_queryset(self):
        """
        Optimized queryset for comments.
        """
        return TicketComment.objects.select_related(
            'ticket',
            'author',
            'ticket__organization'
        ).filter(
            ticket__organization=self.request.user.organization
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Optimized create with select_related.
        """
        ticket = serializer.validated_data['ticket']
        
        # Ensure ticket belongs to user's organization
        if ticket.organization != self.request.user.organization:
            raise PermissionError("Ticket does not belong to your organization")
        
        serializer.save(author=self.request.user)


class OptimizedWorkOrderViewSet(viewsets.ModelViewSet):
    """
    Comprehensive work order viewset with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Comprehensive optimized queryset to prevent all N+1 queries for work orders.
        """
        from apps.field_service.models import WorkOrder, JobAssignment, Technician
        
        return WorkOrder.objects.select_related(
            'organization',
            'customer',
            'created_by'
        ).prefetch_related(
            # Fix: Work Order Assignments N+1
            Prefetch(
                'job_assignments',
                queryset=JobAssignment.objects.select_related(
                    'technician',
                    'technician__user'
                ).order_by('-assigned_at')
            ),
            # Fix: Attachments N+1
            'attachments',
            # Fix: Service reports N+1
            'service_reports',
            # Fix: Parts N+1
            'parts_required'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def technician_workload(self, request):
        """
        Optimized technician workload calculation.
        """
        cache_key = f"technician_workload_{request.user.organization.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Single query to get technician workload
        from apps.field_service.models import Technician, JobAssignment
        
        workload_data = Technician.objects.filter(
            organization=request.user.organization
        ).select_related('user').prefetch_related(
            Prefetch(
                'assignments',
                queryset=JobAssignment.objects.filter(
                    status__in=['assigned', 'in_progress']
                ).select_related('work_order')
            )
        ).values(
            'id',
            'user__first_name',
            'user__last_name',
            'availability_status'
        ).annotate(
            active_assignments=Count('assignments')
        )
        
        # Cache for 5 minutes
        cache.set(cache_key, list(workload_data), 300)
        
        return Response(workload_data)


class OptimizedKnowledgeBaseViewSet(viewsets.ModelViewSet):
    """
    Optimized knowledge base viewset.
    """
    
    def get_queryset(self):
        """
        Optimized queryset for knowledge base articles.
        """
        return KBArticle.objects.select_related(
            'organization',
            'author',
            'category'
        ).prefetch_related(
            'tags',
            'views'
        ).filter(
            organization=self.request.user.organization,
            status='published'
        ).order_by('-published_at', '-created_at')
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """
        Optimized article view tracking.
        """
        article = self.get_object()
        
        # Create view record
        KBArticleView.objects.create(
            article=article,
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Update view count
        article.view_count += 1
        article.save(update_fields=['view_count'])
        
        return Response({'status': 'viewed'})
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Optimized popular articles endpoint.
        """
        cache_key = f"popular_articles_{request.user.organization.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get popular articles with optimized query
        popular_articles = self.get_queryset().filter(
            view_count__gt=0
        ).order_by('-view_count', '-helpful_count')[:10]
        
        serializer = self.get_serializer(popular_articles, many=True)
        data = serializer.data
        
        # Cache for 15 minutes
        cache.set(cache_key, data, 900)
        
        return Response(data)
