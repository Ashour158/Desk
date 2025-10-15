"""
Optimized aggregation queries to replace multiple separate queries.
"""

from django.db.models import Count, Avg, Max, Min, Sum, Q
from django.utils import timezone
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class OptimizedStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optimized statistics viewset with single-query aggregations.
    """
    
    @action(detail=False, methods=['get'])
    def ticket_statistics(self, request):
        """
        Get ticket statistics with single aggregation query.
        """
        from apps.tickets.models import Ticket
        
        cache_key = f"ticket_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all ticket statistics
        stats = Ticket.objects.filter(
            organization=request.user.organization
        ).aggregate(
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
        priority_stats = Ticket.objects.filter(
            organization=request.user.organization
        ).values('priority').annotate(
            count=Count('id')
        )
        stats['priority_breakdown'] = {
            item['priority']: item['count'] 
            for item in priority_stats
        }
        
        # Status breakdown with single query
        status_stats = Ticket.objects.filter(
            organization=request.user.organization
        ).values('status').annotate(
            count=Count('id')
        )
        stats['status_breakdown'] = {
            item['status']: item['count'] 
            for item in status_stats
        }
        
        # SLA compliance with single query
        sla_stats = Ticket.objects.filter(
            organization=request.user.organization
        ).aggregate(
            sla_breached=Count('id', filter=Q(is_sla_breached=True)),
            sla_met=Count('id', filter=Q(is_sla_breached=False)),
            total_with_sla=Count('id', filter=Q(sla_policy__isnull=False))
        )
        stats['sla_compliance'] = sla_stats
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, 600)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def work_order_statistics(self, request):
        """
        Get work order statistics with single aggregation query.
        """
        from apps.field_service.models import WorkOrder
        
        cache_key = f"work_order_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all work order statistics
        stats = WorkOrder.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_work_orders=Count('id'),
            pending_work_orders=Count('id', filter=Q(status='pending')),
            in_progress_work_orders=Count('id', filter=Q(status='in_progress')),
            completed_work_orders=Count('id', filter=Q(status='completed')),
            cancelled_work_orders=Count('id', filter=Q(status='cancelled')),
            avg_completion_time=Avg('completion_time'),
            max_completion_time=Max('completion_time'),
            min_completion_time=Min('completion_time'),
            total_estimated_hours=Sum('estimated_hours'),
            total_actual_hours=Sum('actual_hours')
        )
        
        # Priority breakdown with single query
        priority_stats = WorkOrder.objects.filter(
            organization=request.user.organization
        ).values('priority').annotate(
            count=Count('id')
        )
        stats['priority_breakdown'] = {
            item['priority']: item['count'] 
            for item in priority_stats
        }
        
        # Status breakdown with single query
        status_stats = WorkOrder.objects.filter(
            organization=request.user.organization
        ).values('status').annotate(
            count=Count('id')
        )
        stats['status_breakdown'] = {
            item['status']: item['count'] 
            for item in status_stats
        }
        
        # Technician workload with single query
        technician_stats = WorkOrder.objects.filter(
            organization=request.user.organization,
            technician__isnull=False
        ).values('technician__id', 'technician__first_name', 'technician__last_name').annotate(
            total_assignments=Count('id'),
            completed_assignments=Count('id', filter=Q(status='completed')),
            avg_completion_time=Avg('completion_time')
        )
        stats['technician_workload'] = list(technician_stats)
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, 600)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def knowledge_base_statistics(self, request):
        """
        Get knowledge base statistics with single aggregation query.
        """
        from apps.knowledge_base.models import KBArticle, KBArticleView
        
        cache_key = f"kb_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all KB statistics
        stats = KBArticle.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_articles=Count('id'),
            published_articles=Count('id', filter=Q(status='published')),
            draft_articles=Count('id', filter=Q(status='draft')),
            archived_articles=Count('id', filter=Q(status='archived')),
            total_views=Sum('view_count'),
            total_helpful_votes=Sum('helpful_count'),
            avg_views_per_article=Avg('view_count'),
            avg_helpful_votes_per_article=Avg('helpful_count')
        )
        
        # Category breakdown with single query
        category_stats = KBArticle.objects.filter(
            organization=request.user.organization
        ).values('category__name').annotate(
            count=Count('id'),
            total_views=Sum('view_count'),
            avg_views=Avg('view_count')
        )
        stats['category_breakdown'] = list(category_stats)
        
        # Popular articles with single query
        popular_articles = KBArticle.objects.filter(
            organization=request.user.organization,
            status='published'
        ).order_by('-view_count', '-helpful_count')[:10].values(
            'id', 'title', 'view_count', 'helpful_count'
        )
        stats['popular_articles'] = list(popular_articles)
        
        # Recent views with single query
        recent_views = KBArticleView.objects.filter(
            article__organization=request.user.organization
        ).select_related('article', 'user').order_by('-created_at')[:10].values(
            'article__title', 'user__first_name', 'user__last_name', 'created_at'
        )
        stats['recent_views'] = list(recent_views)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def user_statistics(self, request):
        """
        Get user statistics with single aggregation query.
        """
        from apps.accounts.models import User
        
        cache_key = f"user_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all user statistics
        stats = User.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_users=Count('id'),
            active_users=Count('id', filter=Q(is_active=True)),
            inactive_users=Count('id', filter=Q(is_active=False)),
            admin_users=Count('id', filter=Q(role='admin')),
            agent_users=Count('id', filter=Q(role='agent')),
            customer_users=Count('id', filter=Q(role='customer')),
            recently_joined=Count('id', filter=Q(date_joined__gte=timezone.now() - timezone.timedelta(days=30)))
        )
        
        # Role breakdown with single query
        role_stats = User.objects.filter(
            organization=request.user.organization
        ).values('role').annotate(
            count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True))
        )
        stats['role_breakdown'] = list(role_stats)
        
        # Last login statistics with single query
        login_stats = User.objects.filter(
            organization=request.user.organization,
            last_login__isnull=False
        ).aggregate(
            avg_days_since_login=Avg('last_login'),
            max_days_since_login=Max('last_login'),
            min_days_since_login=Min('last_login')
        )
        stats['login_statistics'] = login_stats
        
        # Cache for 30 minutes
        cache.set(cache_key, stats, 1800)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def communication_statistics(self, request):
        """
        Get communication statistics with single aggregation query.
        """
        from apps.communication_platform.models import CommunicationMessage, CommunicationSession
        
        cache_key = f"communication_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all communication statistics
        stats = CommunicationMessage.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_messages=Count('id'),
            text_messages=Count('id', filter=Q(message_type='text')),
            email_messages=Count('id', filter=Q(message_type='email')),
            phone_messages=Count('id', filter=Q(message_type='phone')),
            video_messages=Count('id', filter=Q(message_type='video')),
            avg_messages_per_session=Avg('session__message_count')
        )
        
        # Message type breakdown with single query
        message_type_stats = CommunicationMessage.objects.filter(
            organization=request.user.organization
        ).values('message_type').annotate(
            count=Count('id')
        )
        stats['message_type_breakdown'] = {
            item['message_type']: item['count'] 
            for item in message_type_stats
        }
        
        # Session statistics with single query
        session_stats = CommunicationSession.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_sessions=Count('id'),
            active_sessions=Count('id', filter=Q(session_status='active')),
            completed_sessions=Count('id', filter=Q(session_status='completed')),
            avg_session_duration=Avg('session_duration'),
            avg_messages_per_session=Avg('message_count')
        )
        stats['session_statistics'] = session_stats
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, 600)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def analytics_statistics(self, request):
        """
        Get analytics statistics with single aggregation query.
        """
        from apps.advanced_analytics.models import AnalyticsMetric, AnalyticsReport
        
        cache_key = f"analytics_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all analytics statistics
        stats = AnalyticsMetric.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_metrics=Count('id'),
            avg_metric_value=Avg('metric_value'),
            max_metric_value=Max('metric_value'),
            min_metric_value=Min('metric_value'),
            total_metric_value=Sum('metric_value')
        )
        
        # Metric type breakdown with single query
        metric_type_stats = AnalyticsMetric.objects.filter(
            organization=request.user.organization
        ).values('metric_name').annotate(
            count=Count('id'),
            avg_value=Avg('metric_value'),
            max_value=Max('metric_value'),
            min_value=Min('metric_value')
        )
        stats['metric_type_breakdown'] = list(metric_type_stats)
        
        # Report statistics with single query
        report_stats = AnalyticsReport.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_reports=Count('id'),
            scheduled_reports=Count('id', filter=Q(report_type='scheduled')),
            ad_hoc_reports=Count('id', filter=Q(report_type='ad_hoc')),
            avg_generation_time=Avg('generation_time')
        )
        stats['report_statistics'] = report_stats
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def ai_ml_statistics(self, request):
        """
        Get AI/ML statistics with single aggregation query.
        """
        from apps.ai_ml.models import AIModel, AIPrediction
        
        cache_key = f"ai_ml_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all AI/ML statistics
        stats = AIModel.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_models=Count('id'),
            active_models=Count('id', filter=Q(status='active')),
            training_models=Count('id', filter=Q(status='training')),
            deployed_models=Count('id', filter=Q(status='deployed')),
            avg_accuracy=Avg('accuracy_score'),
            max_accuracy=Max('accuracy_score'),
            min_accuracy=Min('accuracy_score')
        )
        
        # Model type breakdown with single query
        model_type_stats = AIModel.objects.filter(
            organization=request.user.organization
        ).values('model_type').annotate(
            count=Count('id'),
            avg_accuracy=Avg('accuracy_score')
        )
        stats['model_type_breakdown'] = list(model_type_stats)
        
        # Prediction statistics with single query
        prediction_stats = AIPrediction.objects.filter(
            model__organization=request.user.organization
        ).aggregate(
            total_predictions=Count('id'),
            avg_confidence=Avg('confidence_score'),
            max_confidence=Max('confidence_score'),
            min_confidence=Min('confidence_score'),
            high_confidence_predictions=Count('id', filter=Q(confidence_score__gte=0.8)),
            low_confidence_predictions=Count('id', filter=Q(confidence_score__lt=0.5))
        )
        stats['prediction_statistics'] = prediction_stats
        
        # Cache for 20 minutes
        cache.set(cache_key, stats, 1200)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def integration_statistics(self, request):
        """
        Get integration statistics with single aggregation query.
        """
        from apps.integration_platform.models import Integration, IntegrationLog
        
        cache_key = f"integration_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all integration statistics
        stats = Integration.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_integrations=Count('id'),
            active_integrations=Count('id', filter=Q(is_active=True)),
            inactive_integrations=Count('id', filter=Q(is_active=False)),
            total_calls=Sum('total_calls'),
            successful_calls=Sum('successful_calls'),
            failed_calls=Sum('failed_calls'),
            avg_success_rate=Avg('success_rate')
        )
        
        # Integration type breakdown with single query
        integration_type_stats = Integration.objects.filter(
            organization=request.user.organization
        ).values('integration_type').annotate(
            count=Count('id'),
            total_calls=Sum('total_calls'),
            success_rate=Avg('success_rate')
        )
        stats['integration_type_breakdown'] = list(integration_type_stats)
        
        # Log statistics with single query
        log_stats = IntegrationLog.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_logs=Count('id'),
            info_logs=Count('id', filter=Q(severity='info')),
            warning_logs=Count('id', filter=Q(severity='warning')),
            error_logs=Count('id', filter=Q(severity='error'))
        )
        stats['log_statistics'] = log_stats
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, 600)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def security_statistics(self, request):
        """
        Get security statistics with single aggregation query.
        """
        from apps.security.models import SecurityEvent, AuditLog
        
        cache_key = f"security_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single aggregation query for all security statistics
        stats = SecurityEvent.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_events=Count('id'),
            high_severity_events=Count('id', filter=Q(severity='high')),
            medium_severity_events=Count('id', filter=Q(severity='medium')),
            low_severity_events=Count('id', filter=Q(severity='low')),
            resolved_events=Count('id', filter=Q(status='resolved')),
            open_events=Count('id', filter=Q(status='open'))
        )
        
        # Event type breakdown with single query
        event_type_stats = SecurityEvent.objects.filter(
            organization=request.user.organization
        ).values('event_type').annotate(
            count=Count('id')
        )
        stats['event_type_breakdown'] = {
            item['event_type']: item['count'] 
            for item in event_type_stats
        }
        
        # Audit log statistics with single query
        audit_stats = AuditLog.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_audit_logs=Count('id'),
            user_actions=Count('id', filter=Q(action__icontains='user')),
            system_actions=Count('id', filter=Q(action__icontains='system')),
            security_actions=Count('id', filter=Q(action__icontains='security'))
        )
        stats['audit_statistics'] = audit_stats
        
        # Cache for 5 minutes (security data changes frequently)
        cache.set(cache_key, stats, 300)
        
        return Response(stats)

