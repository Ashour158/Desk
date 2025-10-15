"""
Comprehensive Aggregation Optimizations - Single Query Statistics
"""

from django.db.models import Count, Avg, Max, Min, Sum, Q, F, Case, When, Value, CharField
from django.utils import timezone
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class ComprehensiveStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Comprehensive statistics with single aggregation queries.
    """
    
    @action(detail=False, methods=['get'])
    def ticket_statistics_comprehensive(self, request):
        """
        Get comprehensive ticket statistics with single aggregation query.
        """
        from apps.tickets.models import Ticket
        
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
            urgent_priority=Count('id', filter=Q(priority='urgent')),
            
            # Time-based metrics
            today_tickets=Count('id', filter=Q(created_at__date=timezone.now().date())),
            this_week_tickets=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=7))),
            this_month_tickets=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=30)))
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
    
    @action(detail=False, methods=['get'])
    def work_order_statistics_comprehensive(self, request):
        """
        Get comprehensive work order statistics with single aggregation query.
        """
        from apps.field_service.models import WorkOrder, JobAssignment
        
        cache_key = f"comprehensive_work_order_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query
        base_queryset = WorkOrder.objects.filter(organization=request.user.organization)
        
        stats = base_queryset.aggregate(
            # Basic counts
            total_work_orders=Count('id'),
            scheduled_work_orders=Count('id', filter=Q(status='scheduled')),
            in_progress_work_orders=Count('id', filter=Q(status='in_progress')),
            completed_work_orders=Count('id', filter=Q(status='completed')),
            cancelled_work_orders=Count('id', filter=Q(status='cancelled')),
            
            # Performance metrics
            avg_completion_time=Avg('duration_minutes'),
            max_completion_time=Max('duration_minutes'),
            min_completion_time=Min('duration_minutes'),
            avg_travel_time=Avg('travel_time'),
            avg_work_time=Avg('work_time'),
            
            # Cost metrics
            total_estimated_cost=Sum('cost_estimate'),
            total_final_cost=Sum('final_cost'),
            avg_cost_difference=Avg(F('final_cost') - F('cost_estimate')),
            
            # Time-based metrics
            today_work_orders=Count('id', filter=Q(created_at__date=timezone.now().date())),
            this_week_work_orders=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=7))),
            overdue_work_orders=Count('id', filter=Q(scheduled_end__lt=timezone.now(), status__in=['scheduled', 'in_progress']))
        )
        
        # Work type breakdown with single query
        work_type_stats = base_queryset.values('work_type').annotate(
            count=Count('id'),
            avg_duration=Avg('duration_minutes'),
            avg_cost=Avg('final_cost')
        )
        stats['work_type_breakdown'] = list(work_type_stats)
        
        # Technician performance with single query
        technician_stats = JobAssignment.objects.filter(
            work_order__organization=request.user.organization
        ).values(
            'technician__user__first_name', 'technician__user__last_name'
        ).annotate(
            assignment_count=Count('id'),
            completed_count=Count('id', filter=Q(status='completed')),
            avg_travel_time=Avg('travel_time'),
            avg_work_time=Avg('work_time'),
            avg_rating=Avg('customer_rating')
        )
        stats['technician_performance'] = list(technician_stats)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def user_statistics_comprehensive(self, request):
        """
        Get comprehensive user statistics with single aggregation query.
        """
        from apps.accounts.models import User, UserSession, UserPermission
        
        cache_key = f"comprehensive_user_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query
        base_queryset = User.objects.filter(organization=request.user.organization)
        
        stats = base_queryset.aggregate(
            # Basic counts
            total_users=Count('id'),
            active_users=Count('id', filter=Q(is_active=True)),
            inactive_users=Count('id', filter=Q(is_active=False)),
            admin_users=Count('id', filter=Q(role='admin')),
            agent_users=Count('id', filter=Q(role='agent')),
            customer_users=Count('id', filter=Q(role='customer')),
            
            # Session metrics
            users_with_sessions=Count('id', filter=Q(sessions__isnull=False)),
            avg_sessions_per_user=Avg('sessions__count'),
            
            # Permission metrics
            users_with_permissions=Count('id', filter=Q(permissions__isnull=False)),
            avg_permissions_per_user=Avg('permissions__count'),
            
            # Time-based metrics
            new_users_today=Count('id', filter=Q(date_joined__date=timezone.now().date())),
            new_users_this_week=Count('id', filter=Q(date_joined__gte=timezone.now().date() - timedelta(days=7))),
            new_users_this_month=Count('id', filter=Q(date_joined__gte=timezone.now().date() - timedelta(days=30))),
            last_login_today=Count('id', filter=Q(last_login__date=timezone.now().date()))
        )
        
        # Role breakdown with single query
        role_stats = base_queryset.values('role').annotate(
            count=Count('id'),
            active_count=Count('id', filter=Q(is_active=True)),
            avg_sessions=Avg('sessions__count')
        )
        stats['role_breakdown'] = list(role_stats)
        
        # Permission breakdown with single query
        permission_stats = UserPermission.objects.filter(
            user__organization=request.user.organization
        ).values('permission__name').annotate(
            user_count=Count('user', distinct=True)
        )
        stats['permission_breakdown'] = list(permission_stats)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def communication_statistics_comprehensive(self, request):
        """
        Get comprehensive communication statistics with single aggregation query.
        """
        from apps.communication_platform.models import CommunicationSession, CommunicationMessage
        
        cache_key = f"comprehensive_communication_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query for sessions
        session_stats = CommunicationSession.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_sessions=Count('id'),
            active_sessions=Count('id', filter=Q(status='active')),
            completed_sessions=Count('id', filter=Q(status='completed')),
            avg_session_duration=Avg('duration_minutes'),
            total_participants=Count('participants'),
            avg_participants_per_session=Avg('participants__count')
        )
        
        # Single comprehensive aggregation query for messages
        message_stats = CommunicationMessage.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_messages=Count('id'),
            text_messages=Count('id', filter=Q(message_type='text')),
            file_messages=Count('id', filter=Q(message_type='file')),
            image_messages=Count('id', filter=Q(message_type='image')),
            avg_messages_per_session=Avg('session__message_count'),
            today_messages=Count('id', filter=Q(created_at__date=timezone.now().date())),
            this_week_messages=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=7)))
        )
        
        # Combine stats
        stats = {**session_stats, **message_stats}
        
        # Message type breakdown with single query
        message_type_stats = CommunicationMessage.objects.filter(
            organization=request.user.organization
        ).values('message_type').annotate(
            count=Count('id'),
            avg_length=Avg('content__length')
        )
        stats['message_type_breakdown'] = list(message_type_stats)
        
        # Session type breakdown with single query
        session_type_stats = CommunicationSession.objects.filter(
            organization=request.user.organization
        ).values('session_type').annotate(
            count=Count('id'),
            avg_duration=Avg('duration_minutes'),
            avg_participants=Avg('participants__count')
        )
        stats['session_type_breakdown'] = list(session_type_stats)
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, 600)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def analytics_statistics_comprehensive(self, request):
        """
        Get comprehensive analytics statistics with single aggregation query.
        """
        from apps.advanced_analytics.models import AnalyticsMetric, AnalyticsReport
        
        cache_key = f"comprehensive_analytics_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query for metrics
        metric_stats = AnalyticsMetric.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_metrics=Count('id'),
            avg_metric_value=Avg('metric_value'),
            max_metric_value=Max('metric_value'),
            min_metric_value=Min('metric_value'),
            total_metric_value=Sum('metric_value'),
            today_metrics=Count('id', filter=Q(created_at__date=timezone.now().date())),
            this_week_metrics=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=7)))
        )
        
        # Single comprehensive aggregation query for reports
        report_stats = AnalyticsReport.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_reports=Count('id'),
            scheduled_reports=Count('id', filter=Q(report_type='scheduled')),
            ad_hoc_reports=Count('id', filter=Q(report_type='ad_hoc')),
            avg_generation_time=Avg('generation_time'),
            successful_reports=Count('id', filter=Q(status='completed')),
            failed_reports=Count('id', filter=Q(status='failed'))
        )
        
        # Combine stats
        stats = {**metric_stats, **report_stats}
        
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
        
        # Report type breakdown with single query
        report_type_stats = AnalyticsReport.objects.filter(
            organization=request.user.organization
        ).values('report_type').annotate(
            count=Count('id'),
            avg_generation_time=Avg('generation_time'),
            success_rate=Count('id', filter=Q(status='completed')) / Count('id') * 100
        )
        stats['report_type_breakdown'] = list(report_type_stats)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def ai_ml_statistics_comprehensive(self, request):
        """
        Get comprehensive AI/ML statistics with single aggregation query.
        """
        from apps.ai_ml.models import AIModel, AIPrediction, AIProcessingJob
        
        cache_key = f"comprehensive_ai_ml_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query for models
        model_stats = AIModel.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_models=Count('id'),
            active_models=Count('id', filter=Q(is_active=True)),
            inactive_models=Count('id', filter=Q(is_active=False)),
            avg_accuracy=Avg('accuracy'),
            max_accuracy=Max('accuracy'),
            min_accuracy=Min('accuracy'),
            total_training_time=Sum('training_time'),
            avg_training_time=Avg('training_time')
        )
        
        # Single comprehensive aggregation query for predictions
        prediction_stats = AIPrediction.objects.filter(
            model__organization=request.user.organization
        ).aggregate(
            total_predictions=Count('id'),
            successful_predictions=Count('id', filter=Q(status='success')),
            failed_predictions=Count('id', filter=Q(status='failed')),
            avg_confidence=Avg('confidence_score'),
            max_confidence=Max('confidence_score'),
            min_confidence=Min('confidence_score'),
            today_predictions=Count('id', filter=Q(created_at__date=timezone.now().date())),
            this_week_predictions=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=7)))
        )
        
        # Single comprehensive aggregation query for jobs
        job_stats = AIProcessingJob.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_jobs=Count('id'),
            running_jobs=Count('id', filter=Q(status='running')),
            completed_jobs=Count('id', filter=Q(status='completed')),
            failed_jobs=Count('id', filter=Q(status='failed')),
            avg_processing_time=Avg('processing_time'),
            max_processing_time=Max('processing_time'),
            min_processing_time=Min('processing_time')
        )
        
        # Combine stats
        stats = {**model_stats, **prediction_stats, **job_stats}
        
        # Model type breakdown with single query
        model_type_stats = AIModel.objects.filter(
            organization=request.user.organization
        ).values('model_type').annotate(
            count=Count('id'),
            avg_accuracy=Avg('accuracy'),
            avg_training_time=Avg('training_time')
        )
        stats['model_type_breakdown'] = list(model_type_stats)
        
        # Prediction status breakdown with single query
        prediction_status_stats = AIPrediction.objects.filter(
            model__organization=request.user.organization
        ).values('status').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence_score')
        )
        stats['prediction_status_breakdown'] = list(prediction_status_stats)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def integration_statistics_comprehensive(self, request):
        """
        Get comprehensive integration statistics with single aggregation query.
        """
        from apps.integration_platform.models import Integration, IntegrationLog
        
        cache_key = f"comprehensive_integration_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query for integrations
        integration_stats = Integration.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_integrations=Count('id'),
            active_integrations=Count('id', filter=Q(is_active=True)),
            inactive_integrations=Count('id', filter=Q(is_active=False)),
            total_calls=Sum('total_calls'),
            successful_calls=Sum('successful_calls'),
            failed_calls=Sum('failed_calls'),
            avg_success_rate=Avg('success_rate'),
            total_response_time=Sum('avg_response_time'),
            avg_response_time=Avg('avg_response_time')
        )
        
        # Single comprehensive aggregation query for logs
        log_stats = IntegrationLog.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_logs=Count('id'),
            info_logs=Count('id', filter=Q(severity='info')),
            warning_logs=Count('id', filter=Q(severity='warning')),
            error_logs=Count('id', filter=Q(severity='error')),
            today_logs=Count('id', filter=Q(created_at__date=timezone.now().date())),
            this_week_logs=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=7)))
        )
        
        # Combine stats
        stats = {**integration_stats, **log_stats}
        
        # Integration type breakdown with single query
        integration_type_stats = Integration.objects.filter(
            organization=request.user.organization
        ).values('integration_type').annotate(
            count=Count('id'),
            total_calls=Sum('total_calls'),
            successful_calls=Sum('successful_calls'),
            avg_success_rate=Avg('success_rate')
        )
        stats['integration_type_breakdown'] = list(integration_type_stats)
        
        # Log severity breakdown with single query
        log_severity_stats = IntegrationLog.objects.filter(
            organization=request.user.organization
        ).values('severity').annotate(
            count=Count('id'),
            percentage=Count('id') / Count('id') * 100
        )
        stats['log_severity_breakdown'] = list(log_severity_stats)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def security_statistics_comprehensive(self, request):
        """
        Get comprehensive security statistics with single aggregation query.
        """
        from apps.advanced_security.models import SecurityEvent, SecurityAuditLog
        
        cache_key = f"comprehensive_security_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query for events
        event_stats = SecurityEvent.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_events=Count('id'),
            high_severity_events=Count('id', filter=Q(severity='high')),
            medium_severity_events=Count('id', filter=Q(severity='medium')),
            low_severity_events=Count('id', filter=Q(severity='low')),
            critical_severity_events=Count('id', filter=Q(severity='critical')),
            today_events=Count('id', filter=Q(occurred_at__date=timezone.now().date())),
            this_week_events=Count('id', filter=Q(occurred_at__gte=timezone.now().date() - timedelta(days=7))),
            this_month_events=Count('id', filter=Q(occurred_at__gte=timezone.now().date() - timedelta(days=30)))
        )
        
        # Single comprehensive aggregation query for audit logs
        audit_stats = SecurityAuditLog.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_audit_logs=Count('id'),
            info_audit_logs=Count('id', filter=Q(severity='info')),
            warning_audit_logs=Count('id', filter=Q(severity='warning')),
            error_audit_logs=Count('id', filter=Q(severity='error')),
            critical_audit_logs=Count('id', filter=Q(severity='critical'))
        )
        
        # Combine stats
        stats = {**event_stats, **audit_stats}
        
        # Event type breakdown with single query
        event_type_stats = SecurityEvent.objects.filter(
            organization=request.user.organization
        ).values('event_type').annotate(
            count=Count('id'),
            avg_severity_score=Avg('severity_score')
        )
        stats['event_type_breakdown'] = list(event_type_stats)
        
        # Severity breakdown with single query
        severity_stats = SecurityEvent.objects.filter(
            organization=request.user.organization
        ).values('severity').annotate(
            count=Count('id'),
            percentage=Count('id') / Count('id') * 100
        )
        stats['severity_breakdown'] = list(severity_stats)
        
        # Cache for 10 minutes
        cache.set(cache_key, stats, 600)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def mobile_statistics_comprehensive(self, request):
        """
        Get comprehensive mobile statistics with single aggregation query.
        """
        from apps.mobile_iot.models import MobileSession, MobileDataPoint
        
        cache_key = f"comprehensive_mobile_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query for sessions
        session_stats = MobileSession.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_sessions=Count('id'),
            active_sessions=Count('id', filter=Q(status='active')),
            completed_sessions=Count('id', filter=Q(status='completed')),
            avg_session_duration=Avg('duration_minutes'),
            total_data_points=Sum('data_points__count'),
            avg_data_points_per_session=Avg('data_points__count')
        )
        
        # Single comprehensive aggregation query for data points
        data_point_stats = MobileDataPoint.objects.filter(
            session__organization=request.user.organization
        ).aggregate(
            total_data_points=Count('id'),
            today_data_points=Count('id', filter=Q(timestamp__date=timezone.now().date())),
            this_week_data_points=Count('id', filter=Q(timestamp__gte=timezone.now().date() - timedelta(days=7))),
            avg_value=Avg('value'),
            max_value=Max('value'),
            min_value=Min('value')
        )
        
        # Combine stats
        stats = {**session_stats, **data_point_stats}
        
        # Session type breakdown with single query
        session_type_stats = MobileSession.objects.filter(
            organization=request.user.organization
        ).values('session_type').annotate(
            count=Count('id'),
            avg_duration=Avg('duration_minutes'),
            total_data_points=Sum('data_points__count')
        )
        stats['session_type_breakdown'] = list(session_type_stats)
        
        # Data point type breakdown with single query
        data_point_type_stats = MobileDataPoint.objects.filter(
            session__organization=request.user.organization
        ).values('data_type').annotate(
            count=Count('id'),
            avg_value=Avg('value'),
            max_value=Max('value'),
            min_value=Min('value')
        )
        stats['data_point_type_breakdown'] = list(data_point_type_stats)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def customer_feedback_statistics_comprehensive(self, request):
        """
        Get comprehensive customer feedback statistics with single aggregation query.
        """
        from apps.customer_experience.models import CustomerFeedback
        
        cache_key = f"comprehensive_customer_feedback_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query
        base_queryset = CustomerFeedback.objects.filter(organization=request.user.organization)
        
        stats = base_queryset.aggregate(
            # Basic counts
            total_feedback=Count('id'),
            positive_feedback=Count('id', filter=Q(sentiment='positive')),
            negative_feedback=Count('id', filter=Q(sentiment='negative')),
            neutral_feedback=Count('id', filter=Q(sentiment='neutral')),
            
            # Rating metrics
            avg_rating=Avg('rating'),
            max_rating=Max('rating'),
            min_rating=Min('rating'),
            five_star_ratings=Count('id', filter=Q(rating=5)),
            four_star_ratings=Count('id', filter=Q(rating=4)),
            three_star_ratings=Count('id', filter=Q(rating=3)),
            two_star_ratings=Count('id', filter=Q(rating=2)),
            one_star_ratings=Count('id', filter=Q(rating=1)),
            
            # Time-based metrics
            today_feedback=Count('id', filter=Q(created_at__date=timezone.now().date())),
            this_week_feedback=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=7))),
            this_month_feedback=Count('id', filter=Q(created_at__gte=timezone.now().date() - timedelta(days=30))),
            
            # Response metrics
            responded_feedback=Count('id', filter=Q(response__isnull=False)),
            avg_response_time=Avg('response_time_hours')
        )
        
        # Sentiment breakdown with single query
        sentiment_stats = base_queryset.values('sentiment').annotate(
            count=Count('id'),
            avg_rating=Avg('rating'),
            avg_response_time=Avg('response_time_hours')
        )
        stats['sentiment_breakdown'] = list(sentiment_stats)
        
        # Rating breakdown with single query
        rating_stats = base_queryset.values('rating').annotate(
            count=Count('id'),
            sentiment_distribution=Count('id', filter=Q(sentiment='positive')) / Count('id') * 100
        )
        stats['rating_breakdown'] = list(rating_stats)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def workflow_statistics_comprehensive(self, request):
        """
        Get comprehensive workflow statistics with single aggregation query.
        """
        from apps.advanced_workflow.models import WorkflowExecution, WorkflowStep
        
        cache_key = f"comprehensive_workflow_stats_{request.user.organization.id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Single comprehensive aggregation query for executions
        execution_stats = WorkflowExecution.objects.filter(
            organization=request.user.organization
        ).aggregate(
            total_executions=Count('id'),
            running_executions=Count('id', filter=Q(status='running')),
            completed_executions=Count('id', filter=Q(status='completed')),
            failed_executions=Count('id', filter=Q(status='failed')),
            cancelled_executions=Count('id', filter=Q(status='cancelled')),
            avg_execution_time=Avg('execution_time'),
            max_execution_time=Max('execution_time'),
            min_execution_time=Min('execution_time'),
            today_executions=Count('id', filter=Q(started_at__date=timezone.now().date())),
            this_week_executions=Count('id', filter=Q(started_at__gte=timezone.now().date() - timedelta(days=7)))
        )
        
        # Single comprehensive aggregation query for steps
        step_stats = WorkflowStep.objects.filter(
            workflow__organization=request.user.organization
        ).aggregate(
            total_steps=Count('id'),
            active_steps=Count('id', filter=Q(is_active=True)),
            inactive_steps=Count('id', filter=Q(is_active=False)),
            avg_step_order=Avg('step_order'),
            max_step_order=Max('step_order'),
            min_step_order=Min('step_order')
        )
        
        # Combine stats
        stats = {**execution_stats, **step_stats}
        
        # Execution status breakdown with single query
        execution_status_stats = WorkflowExecution.objects.filter(
            organization=request.user.organization
        ).values('status').annotate(
            count=Count('id'),
            avg_execution_time=Avg('execution_time')
        )
        stats['execution_status_breakdown'] = list(execution_status_stats)
        
        # Step type breakdown with single query
        step_type_stats = WorkflowStep.objects.filter(
            workflow__organization=request.user.organization
        ).values('step_type').annotate(
            count=Count('id'),
            avg_order=Avg('step_order')
        )
        stats['step_type_breakdown'] = list(step_type_stats)
        
        # Cache for 15 minutes
        cache.set(cache_key, stats, 900)
        
        return Response(stats)
