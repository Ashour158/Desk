"""
Fixes for N+1 query problems across the platform.
"""

from django.db.models import Prefetch, Q, Count, Avg, Max, Min
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response


class OptimizedTicketViewSet(viewsets.ModelViewSet):
    """
    Optimized ticket viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.tickets.models import Ticket, TicketComment, TicketAttachment
        
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
        Optimized list view with single query.
        """
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
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedWorkOrderViewSet(viewsets.ModelViewSet):
    """
    Optimized work order viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.field_service.models import WorkOrder, JobAssignment
        
        return WorkOrder.objects.select_related(
            'organization',
            'customer',
            'created_by'
        ).prefetch_related(
            Prefetch(
                'assignments',
                queryset=JobAssignment.objects.select_related('technician', 'technician__user')
            ),
            'attachments',
            'technician'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        status_filter = request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        technician_filter = request.GET.get('technician')
        if technician_filter:
            queryset = queryset.filter(technician_id=technician_filter)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedKnowledgeBaseViewSet(viewsets.ModelViewSet):
    """
    Optimized knowledge base viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.knowledge_base.models import KBArticle, KBArticleView
        
        return KBArticle.objects.select_related(
            'organization',
            'author',
            'category'
        ).prefetch_related(
            'tags',
            Prefetch(
                'views',
                queryset=KBArticleView.objects.select_related('user').order_by('-created_at')
            )
        ).filter(
            organization=self.request.user.organization,
            status='published'
        ).order_by('-published_at', '-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        category_filter = request.GET.get('category')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        search_query = request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedUserViewSet(viewsets.ModelViewSet):
    """
    Optimized user viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.accounts.models import User
        
        return User.objects.select_related(
            'organization'
        ).prefetch_related(
            'groups',
            'user_permissions'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-date_joined')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        role_filter = request.GET.get('role')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        is_active_filter = request.GET.get('is_active')
        if is_active_filter is not None:
            queryset = queryset.filter(is_active=is_active_filter.lower() == 'true')
        
        search_query = request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedCommunicationViewSet(viewsets.ModelViewSet):
    """
    Optimized communication viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.communication_platform.models import CommunicationMessage, CommunicationSession
        
        return CommunicationMessage.objects.select_related(
            'organization'
        ).prefetch_related(
            Prefetch(
                'session',
                queryset=CommunicationSession.objects.select_related('user')
            )
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        message_type_filter = request.GET.get('message_type')
        if message_type_filter:
            queryset = queryset.filter(message_type=message_type_filter)
        
        session_filter = request.GET.get('session')
        if session_filter:
            queryset = queryset.filter(session_id=session_filter)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optimized analytics viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.advanced_analytics.models import AnalyticsMetric, AnalyticsReport
        
        return AnalyticsMetric.objects.select_related(
            'organization'
        ).prefetch_related(
            'tags'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-metric_date', '-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        metric_name_filter = request.GET.get('metric_name')
        if metric_name_filter:
            queryset = queryset.filter(metric_name=metric_name_filter)
        
        date_from = request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(metric_date__gte=date_from)
        
        date_to = request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(metric_date__lte=date_to)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedAIModelViewSet(viewsets.ModelViewSet):
    """
    Optimized AI model viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.ai_ml.models import AIModel, AIPrediction
        
        return AIModel.objects.select_related(
            'organization'
        ).prefetch_related(
            Prefetch(
                'predictions',
                queryset=AIPrediction.objects.select_related('user').order_by('-prediction_date')
            )
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        model_type_filter = request.GET.get('model_type')
        if model_type_filter:
            queryset = queryset.filter(model_type=model_type_filter)
        
        status_filter = request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedIntegrationViewSet(viewsets.ModelViewSet):
    """
    Optimized integration viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.integration_platform.models import Integration, IntegrationLog
        
        return Integration.objects.select_related(
            'organization'
        ).prefetch_related(
            Prefetch(
                'logs',
                queryset=IntegrationLog.objects.order_by('-created_at')
            )
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        integration_type_filter = request.GET.get('integration_type')
        if integration_type_filter:
            queryset = queryset.filter(integration_type=integration_type_filter)
        
        is_active_filter = request.GET.get('is_active')
        if is_active_filter is not None:
            queryset = queryset.filter(is_active=is_active_filter.lower() == 'true')
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedMobileIoTViewSet(viewsets.ModelViewSet):
    """
    Optimized mobile/IoT viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.mobile_iot.models import MobileSession, IoTDataPoint
        
        return MobileSession.objects.select_related(
            'organization',
            'user'
        ).prefetch_related(
            Prefetch(
                'data_points',
                queryset=IoTDataPoint.objects.order_by('-timestamp')
            )
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        session_status_filter = request.GET.get('session_status')
        if session_status_filter:
            queryset = queryset.filter(session_status=session_status_filter)
        
        user_filter = request.GET.get('user')
        if user_filter:
            queryset = queryset.filter(user_id=user_filter)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OptimizedSecurityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optimized security viewset with N+1 query prevention.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent N+1 queries.
        """
        from apps.security.models import SecurityEvent, AuditLog
        
        return SecurityEvent.objects.select_related(
            'organization',
            'user'
        ).prefetch_related(
            Prefetch(
                'audit_logs',
                queryset=AuditLog.objects.select_related('user').order_by('-created_at')
            )
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list view with single query.
        """
        queryset = self.get_queryset()
        
        # Apply filters
        event_type_filter = request.GET.get('event_type')
        if event_type_filter:
            queryset = queryset.filter(event_type=event_type_filter)
        
        severity_filter = request.GET.get('severity')
        if severity_filter:
            queryset = queryset.filter(severity=severity_filter)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

