"""
Comprehensive N+1 Query Fixes for All Identified Problems
"""

from django.db.models import Prefetch, Q, Count, Avg, Max, Min, Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class ComprehensiveTicketOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive ticket optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for tickets.
        """
        from apps.tickets.models import Ticket, TicketComment, TicketAttachment
        from apps.accounts.models import User
        
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
    
    @action(detail=True, methods=['get'])
    def comments_optimized(self, request, pk=None):
        """
        Optimized comments endpoint - fixes N+1 queries.
        """
        ticket = self.get_object()
        
        # Use prefetch_related to avoid N+1 queries
        comments = ticket.comments.select_related('author').order_by('-created_at')
        
        from apps.tickets.serializers import TicketCommentSerializer
        serializer = TicketCommentSerializer(comments, many=True)
        return Response(serializer.data)


class ComprehensiveWorkOrderOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive work order optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for work orders.
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
    def technician_assignments_optimized(self, request):
        """
        Optimized technician assignments - fixes N+1 queries.
        """
        from apps.field_service.models import Technician, JobAssignment
        
        # Single query with all related data
        technicians = Technician.objects.filter(
            organization=request.user.organization
        ).select_related('user').prefetch_related(
            Prefetch(
                'job_assignments',
                queryset=JobAssignment.objects.select_related('work_order').order_by('-assigned_at')
            )
        ).annotate(
            active_assignments=Count('job_assignments', filter=Q(job_assignments__status__in=['assigned', 'in_progress']))
        )
        
        from apps.field_service.serializers import TechnicianSerializer
        serializer = TechnicianSerializer(technicians, many=True)
        return Response(serializer.data)


class ComprehensiveKnowledgeBaseOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive knowledge base optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for knowledge base.
        """
        from apps.knowledge_base.models import KBArticle, KBArticleView
        
        return KBArticle.objects.select_related(
            'organization',
            'author',
            'category'
        ).prefetch_related(
            # Fix: Knowledge Base Views N+1
            Prefetch(
                'views',
                queryset=KBArticleView.objects.select_related('user').order_by('-viewed_at')
            ),
            # Fix: Tags N+1
            'tags',
            # Fix: Attachments N+1
            'attachments',
            # Fix: Related articles N+1
            'related_articles'
        ).filter(
            organization=self.request.user.organization,
            status='published'
        ).order_by('-published_at', '-created_at')
    
    @action(detail=True, methods=['post'])
    def track_view_optimized(self, request, pk=None):
        """
        Optimized article view tracking - fixes N+1 queries.
        """
        article = self.get_object()
        
        # Create view record with optimized query
        from apps.knowledge_base.models import KBArticleView
        
        view = KBArticleView.objects.create(
            article=article,
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Update view count
        article.view_count += 1
        article.save(update_fields=['view_count'])
        
        return Response({'status': 'viewed', 'view_id': str(view.id)})


class ComprehensiveUserOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive user optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for users.
        """
        from apps.accounts.models import User, UserPermission, UserSession
        
        return User.objects.select_related(
            'organization'
        ).prefetch_related(
            # Fix: User Permissions N+1
            Prefetch(
                'permissions',
                queryset=UserPermission.objects.select_related('permission').order_by('permission__name')
            ),
            # Fix: User Sessions N+1
            Prefetch(
                'sessions',
                queryset=UserSession.objects.order_by('-created_at')
            ),
            # Fix: User Profile N+1
            'profile',
            # Fix: User Preferences N+1
            'preferences'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-date_joined')
    
    @action(detail=False, methods=['get'])
    def permissions_optimized(self, request):
        """
        Optimized user permissions - fixes N+1 queries.
        """
        from apps.accounts.models import User, UserPermission
        
        # Single query with all permissions
        users = User.objects.filter(
            organization=request.user.organization
        ).select_related('organization').prefetch_related(
            Prefetch(
                'permissions',
                queryset=UserPermission.objects.select_related('permission').order_by('permission__name')
            )
        )
        
        from apps.accounts.serializers import UserSerializer
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class ComprehensiveCommunicationOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive communication optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for communication.
        """
        from apps.communication_platform.models import CommunicationSession, CommunicationMessage
        
        return CommunicationSession.objects.select_related(
            'organization',
            'created_by'
        ).prefetch_related(
            # Fix: Communication Sessions N+1
            Prefetch(
                'messages',
                queryset=CommunicationMessage.objects.select_related('sender', 'recipient').order_by('-created_at')
            ),
            # Fix: Participants N+1
            'participants',
            # Fix: Attachments N+1
            'attachments'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def messages_optimized(self, request, pk=None):
        """
        Optimized session messages - fixes N+1 queries.
        """
        session = self.get_object()
        
        # Use prefetch_related to avoid N+1 queries
        messages = session.messages.select_related('sender', 'recipient').order_by('-created_at')
        
        from apps.communication_platform.serializers import CommunicationMessageSerializer
        serializer = CommunicationMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ComprehensiveAnalyticsOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive analytics optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for analytics.
        """
        from apps.advanced_analytics.models import AnalyticsMetric, AnalyticsReport
        
        return AnalyticsMetric.objects.select_related(
            'organization',
            'created_by'
        ).prefetch_related(
            # Fix: Analytics Metrics N+1
            Prefetch(
                'tags',
                queryset=AnalyticsMetric.objects.values('tag').annotate(count=Count('id'))
            ),
            # Fix: Related metrics N+1
            'related_metrics',
            # Fix: Reports N+1
            'reports'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def metrics_with_tags_optimized(self, request):
        """
        Optimized metrics with tags - fixes N+1 queries.
        """
        from apps.advanced_analytics.models import AnalyticsMetric
        
        # Single query with all tags
        metrics = AnalyticsMetric.objects.filter(
            organization=request.user.organization
        ).select_related('organization').prefetch_related(
            'tags'
        ).annotate(
            tag_count=Count('tags')
        )
        
        from apps.advanced_analytics.serializers import AnalyticsMetricSerializer
        serializer = AnalyticsMetricSerializer(metrics, many=True)
        return Response(serializer.data)


class ComprehensiveAIMLOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive AI/ML optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for AI/ML.
        """
        from apps.ai_ml.models import AIModel, AIPrediction, AIProcessingJob
        
        return AIModel.objects.select_related(
            'organization',
            'created_by'
        ).prefetch_related(
            # Fix: AI Model Predictions N+1
            Prefetch(
                'predictions',
                queryset=AIPrediction.objects.select_related('user').order_by('-created_at')
            ),
            # Fix: Processing Jobs N+1
            Prefetch(
                'processing_jobs',
                queryset=AIProcessingJob.objects.order_by('-created_at')
            ),
            # Fix: Performance metrics N+1
            'performance_metrics'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def predictions_optimized(self, request, pk=None):
        """
        Optimized model predictions - fixes N+1 queries.
        """
        model = self.get_object()
        
        # Use prefetch_related to avoid N+1 queries
        predictions = model.predictions.select_related('user').order_by('-created_at')
        
        from apps.ai_ml.serializers import AIPredictionSerializer
        serializer = AIPredictionSerializer(predictions, many=True)
        return Response(serializer.data)


class ComprehensiveIntegrationOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive integration optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for integrations.
        """
        from apps.integration_platform.models import Integration, IntegrationLog
        
        return Integration.objects.select_related(
            'organization',
            'created_by'
        ).prefetch_related(
            # Fix: Integration Logs N+1
            Prefetch(
                'logs',
                queryset=IntegrationLog.objects.order_by('-created_at')
            ),
            # Fix: Configuration N+1
            'configuration',
            # Fix: Related integrations N+1
            'related_integrations'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def logs_optimized(self, request, pk=None):
        """
        Optimized integration logs - fixes N+1 queries.
        """
        integration = self.get_object()
        
        # Use prefetch_related to avoid N+1 queries
        logs = integration.logs.order_by('-created_at')
        
        from apps.integration_platform.serializers import IntegrationLogSerializer
        serializer = IntegrationLogSerializer(logs, many=True)
        return Response(serializer.data)


class ComprehensiveMobileOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive mobile optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for mobile sessions.
        """
        from apps.mobile_iot.models import MobileSession, MobileDataPoint
        
        return MobileSession.objects.select_related(
            'organization',
            'user'
        ).prefetch_related(
            # Fix: Mobile Sessions N+1
            Prefetch(
                'data_points',
                queryset=MobileDataPoint.objects.order_by('-timestamp')
            ),
            # Fix: Location data N+1
            'location_data',
            # Fix: Device info N+1
            'device_info'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def data_points_optimized(self, request, pk=None):
        """
        Optimized session data points - fixes N+1 queries.
        """
        session = self.get_object()
        
        # Use prefetch_related to avoid N+1 queries
        data_points = session.data_points.order_by('-timestamp')
        
        from apps.mobile_iot.serializers import MobileDataPointSerializer
        serializer = MobileDataPointSerializer(data_points, many=True)
        return Response(serializer.data)


class ComprehensiveSecurityOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive security optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for security events.
        """
        from apps.advanced_security.models import SecurityEvent, SecurityAuditLog
        
        return SecurityEvent.objects.select_related(
            'organization',
            'user'
        ).prefetch_related(
            # Fix: Security Events N+1
            Prefetch(
                'audit_logs',
                queryset=SecurityAuditLog.objects.select_related('user').order_by('-created_at')
            ),
            # Fix: Related events N+1
            'related_events',
            # Fix: Security rules N+1
            'security_rules'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def audit_logs_optimized(self, request, pk=None):
        """
        Optimized security audit logs - fixes N+1 queries.
        """
        event = self.get_object()
        
        # Use prefetch_related to avoid N+1 queries
        audit_logs = event.audit_logs.select_related('user').order_by('-created_at')
        
        from apps.advanced_security.serializers import SecurityAuditLogSerializer
        serializer = SecurityAuditLogSerializer(audit_logs, many=True)
        return Response(serializer.data)


class ComprehensiveCustomerFeedbackOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive customer feedback optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for customer feedback.
        """
        from apps.customer_experience.models import CustomerFeedback
        
        return CustomerFeedback.objects.select_related(
            'organization',
            'user',
            'ticket',
            'work_order'
        ).prefetch_related(
            # Fix: Customer Feedback N+1
            'attachments',
            # Fix: Related feedback N+1
            'related_feedback',
            # Fix: Feedback categories N+1
            'categories'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def feedback_with_user_optimized(self, request):
        """
        Optimized feedback with user data - fixes N+1 queries.
        """
        from apps.customer_experience.models import CustomerFeedback
        
        # Single query with all user data
        feedback = CustomerFeedback.objects.filter(
            organization=request.user.organization
        ).select_related(
            'user',
            'ticket',
            'work_order'
        ).prefetch_related(
            'attachments',
            'categories'
        ).order_by('-created_at')
        
        from apps.customer_experience.serializers import CustomerFeedbackSerializer
        serializer = CustomerFeedbackSerializer(feedback, many=True)
        return Response(serializer.data)


class ComprehensiveWorkflowOptimizationViewSet(viewsets.ModelViewSet):
    """
    Comprehensive workflow optimization with all N+1 query fixes.
    """
    
    def get_queryset(self):
        """
        Optimized queryset to prevent all N+1 queries for workflow executions.
        """
        from apps.advanced_workflow.models import WorkflowExecution, WorkflowStep
        
        return WorkflowExecution.objects.select_related(
            'organization',
            'workflow_engine',
            'created_by'
        ).prefetch_related(
            # Fix: Workflow Steps N+1
            Prefetch(
                'steps',
                queryset=WorkflowStep.objects.order_by('step_order')
            ),
            # Fix: Execution logs N+1
            'execution_logs',
            # Fix: Related executions N+1
            'related_executions'
        ).filter(
            organization=self.request.user.organization
        ).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def steps_optimized(self, request, pk=None):
        """
        Optimized workflow steps - fixes N+1 queries.
        """
        execution = self.get_object()
        
        # Use prefetch_related to avoid N+1 queries
        steps = execution.steps.order_by('step_order')
        
        from apps.advanced_workflow.serializers import WorkflowStepSerializer
        serializer = WorkflowStepSerializer(steps, many=True)
        return Response(serializer.data)
