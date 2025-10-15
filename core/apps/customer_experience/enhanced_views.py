"""
Enhanced Customer Experience views for advanced capabilities.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import asyncio
import json

from apps.organizations.utils import get_current_organization
from .enhanced_models import (
    CustomerIntelligence,
    HyperPersonalizationEngine,
    CustomerSuccessManagement,
    AdvancedFeedbackSystem,
    CustomerAdvocacyPlatform,
    CustomerInsight,
    PersonalizationRule,
    CustomerSegment,
    CustomerTouchpoint,
)
from .enhanced_services import (
    EnhancedCustomerIntelligenceService,
    EnhancedPersonalizationService,
    EnhancedCustomerSuccessService,
    EnhancedFeedbackService,
    EnhancedAdvocacyService,
)
from .serializers import (
    CustomerIntelligenceSerializer,
    HyperPersonalizationEngineSerializer,
    CustomerSuccessManagementSerializer,
    AdvancedFeedbackSystemSerializer,
    CustomerAdvocacyPlatformSerializer,
    CustomerInsightSerializer,
    PersonalizationRuleSerializer,
    CustomerSegmentSerializer,
    CustomerTouchpointSerializer,
)


class BaseCXViewSet(viewsets.ModelViewSet):
    """Base viewset for Customer Experience models with organization filtering."""

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        organization = get_current_organization(self.request)
        if organization:
            return self.queryset.filter(organization=organization)
        return self.queryset.none()

    def perform_create(self, serializer):
        organization = get_current_organization(self.request)
        if not organization:
            raise serializers.ValidationError(
                "Organization not found for the current request."
            )
        serializer.save(organization=organization, created_by=self.request.user)


class CustomerIntelligenceViewSet(BaseCXViewSet):
    """Customer Intelligence management."""

    queryset = CustomerIntelligence.objects.all()
    serializer_class = CustomerIntelligenceSerializer
    search_fields = ["name", "description", "intelligence_type"]
    filterset_fields = ["intelligence_type", "is_active", "analysis_frequency"]
    ordering_fields = ["name", "created_at", "accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def analyze_customer_360(self, request, pk=None):
        """Analyze customer 360° view."""
        intelligence = self.get_object()
        customer_id = request.data.get("customer_id")

        if not customer_id:
            return Response(
                {"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def analyze():
            intelligence_service = EnhancedCustomerIntelligenceService(
                intelligence.organization
            )
            return await intelligence_service.analyze_customer_360(customer_id)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyze())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def predict_purchase_intent(self, request, pk=None):
        """Predict customer purchase intent."""
        intelligence = self.get_object()
        customer_id = request.data.get("customer_id")

        if not customer_id:
            return Response(
                {"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def predict():
            intelligence_service = EnhancedCustomerIntelligenceService(
                intelligence.organization
            )
            return await intelligence_service.predict_purchase_intent(customer_id)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(predict())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def calculate_clv(self, request, pk=None):
        """Calculate customer lifetime value."""
        intelligence = self.get_object()
        customer_id = request.data.get("customer_id")

        if not customer_id:
            return Response(
                {"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def calculate():
            intelligence_service = EnhancedCustomerIntelligenceService(
                intelligence.organization
            )
            return await intelligence_service.calculate_customer_lifetime_value(
                customer_id
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(calculate())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def performance_metrics(self, request, pk=None):
        """Get performance metrics for customer intelligence."""
        intelligence = self.get_object()

        # Get recent insights
        recent_insights = CustomerInsight.objects.filter(
            organization=intelligence.organization,
            insight_type=intelligence.intelligence_type,
        ).order_by("-generated_at")[:10]

        metrics = {
            "current_accuracy": intelligence.accuracy,
            "current_precision": intelligence.precision,
            "current_recall": intelligence.recall,
            "current_f1_score": intelligence.f1_score,
            "total_analyses": intelligence.total_analyses,
            "successful_predictions": intelligence.successful_predictions,
            "insights_generated": intelligence.insights_generated,
            "recent_insights": [
                {
                    "id": str(insight.id),
                    "customer_id": str(insight.customer.id),
                    "insight_type": insight.insight_type,
                    "confidence_score": insight.confidence_score,
                    "generated_at": insight.generated_at.isoformat(),
                }
                for insight in recent_insights
            ],
        }

        return Response(metrics, status=status.HTTP_200_OK)


class HyperPersonalizationEngineViewSet(BaseCXViewSet):
    """Hyper-personalization Engine management."""

    queryset = HyperPersonalizationEngine.objects.all()
    serializer_class = HyperPersonalizationEngineSerializer
    search_fields = ["name", "description", "personalization_type"]
    filterset_fields = ["personalization_type", "is_active", "update_frequency"]
    ordering_fields = ["name", "created_at", "personalization_accuracy"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def personalize_content(self, request, pk=None):
        """Personalize content for customer."""
        engine = self.get_object()
        customer_id = request.data.get("customer_id")
        content_type = request.data.get("content_type")
        base_content = request.data.get("base_content")

        if not all([customer_id, content_type, base_content]):
            return Response(
                {"error": "Customer ID, content type, and base content are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def personalize():
            personalization_service = EnhancedPersonalizationService(
                engine.organization
            )
            return await personalization_service.personalize_content(
                customer_id, content_type, base_content
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(personalize())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def generate_recommendations(self, request, pk=None):
        """Generate AI-driven recommendations."""
        engine = self.get_object()
        customer_id = request.data.get("customer_id")
        recommendation_type = request.data.get("recommendation_type")

        if not all([customer_id, recommendation_type]):
            return Response(
                {"error": "Customer ID and recommendation type are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def generate():
            personalization_service = EnhancedPersonalizationService(
                engine.organization
            )
            return await personalization_service.generate_recommendations(
                customer_id, recommendation_type
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def personalization_rules(self, request, pk=None):
        """Get personalization rules for the engine."""
        engine = self.get_object()

        rules = PersonalizationRule.objects.filter(
            organization=engine.organization, is_active=True
        ).order_by("-priority")

        rule_data = []
        for rule in rules:
            rule_data.append(
                {
                    "id": str(rule.id),
                    "name": rule.name,
                    "rule_type": rule.rule_type,
                    "conditions": rule.conditions,
                    "actions": rule.actions,
                    "priority": rule.priority,
                    "success_rate": rule.success_rate,
                    "engagement_rate": rule.engagement_rate,
                    "conversion_rate": rule.conversion_rate,
                }
            )

        return Response(
            {"rules": rule_data, "total_rules": len(rule_data)},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def performance_metrics(self, request, pk=None):
        """Get performance metrics for personalization engine."""
        engine = self.get_object()

        metrics = {
            "personalization_accuracy": engine.personalization_accuracy,
            "engagement_improvement": engine.engagement_improvement,
            "conversion_rate": engine.conversion_rate,
            "user_satisfaction": engine.user_satisfaction,
            "total_personalizations": engine.total_personalizations,
            "successful_personalizations": engine.successful_personalizations,
            "content_views": engine.content_views,
            "click_through_rate": engine.click_through_rate,
        }

        return Response(metrics, status=status.HTTP_200_OK)


class CustomerSuccessManagementViewSet(BaseCXViewSet):
    """Customer Success Management."""

    queryset = CustomerSuccessManagement.objects.all()
    serializer_class = CustomerSuccessManagementSerializer
    search_fields = ["name", "description", "success_type"]
    filterset_fields = ["success_type", "is_active", "is_monitoring"]
    ordering_fields = ["name", "created_at", "success_rate"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def automate_onboarding(self, request, pk=None):
        """Automate customer onboarding."""
        success_management = self.get_object()
        customer_id = request.data.get("customer_id")

        if not customer_id:
            return Response(
                {"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def automate():
            success_service = EnhancedCustomerSuccessService(
                success_management.organization
            )
            return await success_service.automate_onboarding(customer_id)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(automate())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def detect_expansion_opportunities(self, request, pk=None):
        """Detect expansion opportunities."""
        success_management = self.get_object()
        customer_id = request.data.get("customer_id")

        if not customer_id:
            return Response(
                {"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def detect():
            success_service = EnhancedCustomerSuccessService(
                success_management.organization
            )
            return await success_service.detect_expansion_opportunities(customer_id)

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(detect())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def success_metrics(self, request, pk=None):
        """Get customer success metrics."""
        success_management = self.get_object()

        metrics = {
            "success_rate": success_management.success_rate,
            "customer_retention": success_management.customer_retention,
            "expansion_rate": success_management.expansion_rate,
            "time_to_value": success_management.time_to_value,
            "total_customers": success_management.total_customers,
            "successful_onboardings": success_management.successful_onboardings,
            "interventions_triggered": success_management.interventions_triggered,
            "expansions_detected": success_management.expansions_detected,
        }

        return Response(metrics, status=status.HTTP_200_OK)


class AdvancedFeedbackSystemViewSet(BaseCXViewSet):
    """Advanced Feedback System management."""

    queryset = AdvancedFeedbackSystem.objects.all()
    serializer_class = AdvancedFeedbackSystemSerializer
    search_fields = ["name", "description", "feedback_type"]
    filterset_fields = ["feedback_type", "is_active", "is_collecting"]
    ordering_fields = ["name", "created_at", "response_rate"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def collect_feedback(self, request, pk=None):
        """Collect and process feedback."""
        feedback_system = self.get_object()
        customer_id = request.data.get("customer_id")
        feedback_type = request.data.get("feedback_type")
        feedback_data = request.data.get("feedback_data", {})

        if not all([customer_id, feedback_type]):
            return Response(
                {"error": "Customer ID and feedback type are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create async task
        async def collect():
            feedback_service = EnhancedFeedbackService(feedback_system.organization)
            return await feedback_service.collect_feedback(
                customer_id, feedback_type, feedback_data
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(collect())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def feedback_analytics(self, request, pk=None):
        """Get feedback analytics."""
        feedback_system = self.get_object()

        # Get recent feedback data
        recent_feedback = CustomerTouchpoint.objects.filter(
            organization=feedback_system.organization, touchpoint_type="feedback"
        ).order_by("-occurred_at")[:20]

        analytics = {
            "response_rate": feedback_system.response_rate,
            "sentiment_accuracy": feedback_system.sentiment_accuracy,
            "action_completion_rate": feedback_system.action_completion_rate,
            "customer_satisfaction": feedback_system.customer_satisfaction,
            "total_surveys": feedback_system.total_surveys,
            "total_responses": feedback_system.total_responses,
            "sentiment_analyses": feedback_system.sentiment_analyses,
            "actions_taken": feedback_system.actions_taken,
            "recent_feedback": [
                {
                    "id": str(touchpoint.id),
                    "customer_id": str(touchpoint.customer.id),
                    "sentiment_score": touchpoint.sentiment_score,
                    "satisfaction_score": touchpoint.satisfaction_score,
                    "occurred_at": touchpoint.occurred_at.isoformat(),
                }
                for touchpoint in recent_feedback
            ],
        }

        return Response(analytics, status=status.HTTP_200_OK)


class CustomerAdvocacyPlatformViewSet(BaseCXViewSet):
    """Customer Advocacy Platform management."""

    queryset = CustomerAdvocacyPlatform.objects.all()
    serializer_class = CustomerAdvocacyPlatformSerializer
    search_fields = ["name", "description", "advocacy_type"]
    filterset_fields = ["advocacy_type", "is_active", "is_running"]
    ordering_fields = ["name", "created_at", "referral_rate"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def manage_referral_program(self, request, pk=None):
        """Manage referral program."""
        advocacy_platform = self.get_object()
        customer_id = request.data.get("customer_id")
        referral_data = request.data.get("referral_data", {})

        if not customer_id:
            return Response(
                {"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def manage():
            advocacy_service = EnhancedAdvocacyService(advocacy_platform.organization)
            return await advocacy_service.manage_referral_program(
                customer_id, referral_data
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(manage())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def collect_testimonial(self, request, pk=None):
        """Collect customer testimonial."""
        advocacy_platform = self.get_object()
        customer_id = request.data.get("customer_id")
        testimonial_data = request.data.get("testimonial_data", {})

        if not customer_id:
            return Response(
                {"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create async task
        async def collect():
            advocacy_service = EnhancedAdvocacyService(advocacy_platform.organization)
            return await advocacy_service.collect_testimonial(
                customer_id, testimonial_data
            )

        # Run async task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(collect())
        loop.close()

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def advocacy_metrics(self, request, pk=None):
        """Get advocacy metrics."""
        advocacy_platform = self.get_object()

        metrics = {
            "referral_rate": advocacy_platform.referral_rate,
            "advocacy_score": advocacy_platform.advocacy_score,
            "community_engagement": advocacy_platform.community_engagement,
            "content_amplification": advocacy_platform.content_amplification,
            "total_advocates": advocacy_platform.total_advocates,
            "total_referrals": advocacy_platform.total_referrals,
            "testimonials_collected": advocacy_platform.testimonials_collected,
            "case_studies_generated": advocacy_platform.case_studies_generated,
        }

        return Response(metrics, status=status.HTTP_200_OK)


class CustomerInsightViewSet(BaseCXViewSet):
    """Customer Insight management."""

    queryset = CustomerInsight.objects.all()
    serializer_class = CustomerInsightSerializer
    search_fields = ["insight_type", "customer__email"]
    filterset_fields = ["insight_type", "is_actionable", "is_processed"]
    ordering_fields = ["generated_at", "confidence_score"]
    ordering = ["-generated_at"]

    @action(detail=False, methods=["get"])
    def insights_summary(self, request):
        """Get insights summary."""
        organization = get_current_organization(request)
        if not organization:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get insights for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_insights = CustomerInsight.objects.filter(
            organization=organization, generated_at__gte=thirty_days_ago
        )

        summary = {
            "total_insights": recent_insights.count(),
            "actionable_insights": recent_insights.filter(is_actionable=True).count(),
            "processed_insights": recent_insights.filter(is_processed=True).count(),
            "insights_by_type": {},
            "average_confidence": recent_insights.aggregate(
                avg_confidence=Avg("confidence_score")
            )["avg_confidence"]
            or 0,
            "top_insights": [],
        }

        # Group by insight type
        for insight_type in recent_insights.values_list(
            "insight_type", flat=True
        ).distinct():
            count = recent_insights.filter(insight_type=insight_type).count()
            summary["insights_by_type"][insight_type] = count

        # Get top insights by confidence
        top_insights = recent_insights.order_by("-confidence_score")[:10]
        summary["top_insights"] = [
            {
                "id": str(insight.id),
                "customer_id": str(insight.customer.id),
                "insight_type": insight.insight_type,
                "confidence_score": insight.confidence_score,
                "generated_at": insight.generated_at.isoformat(),
            }
            for insight in top_insights
        ]

        return Response(summary, status=status.HTTP_200_OK)


class PersonalizationRuleViewSet(BaseCXViewSet):
    """Personalization Rule management."""

    queryset = PersonalizationRule.objects.all()
    serializer_class = PersonalizationRuleSerializer
    search_fields = ["name", "description", "rule_type"]
    filterset_fields = ["rule_type", "is_active", "is_learning"]
    ordering_fields = ["name", "created_at", "priority"]
    ordering = ["-priority", "name"]

    @action(detail=True, methods=["post"])
    def test_rule(self, request, pk=None):
        """Test personalization rule."""
        rule = self.get_object()
        test_data = request.data.get("test_data", {})

        if not test_data:
            return Response(
                {"error": "Test data is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Test rule conditions
        conditions_met = True
        for condition in rule.conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")

            if field in test_data:
                test_value = test_data[field]
                if not self._compare_values(test_value, operator, value):
                    conditions_met = False
                    break

        return Response(
            {
                "rule_id": str(rule.id),
                "rule_name": rule.name,
                "conditions_met": conditions_met,
                "test_data": test_data,
                "rule_conditions": rule.conditions,
                "rule_actions": rule.actions,
            },
            status=status.HTTP_200_OK,
        )

    def _compare_values(
        self, actual_value: Any, operator: str, expected_value: Any
    ) -> bool:
        """Compare values based on operator."""
        if operator == "equals":
            return actual_value == expected_value
        elif operator == "contains":
            return expected_value in str(actual_value)
        elif operator == "greater_than":
            return actual_value > expected_value
        elif operator == "less_than":
            return actual_value < expected_value
        return False


class CustomerSegmentViewSet(BaseCXViewSet):
    """Customer Segment management."""

    queryset = CustomerSegment.objects.all()
    serializer_class = CustomerSegmentSerializer
    search_fields = ["name", "description", "segment_type"]
    filterset_fields = ["segment_type", "is_active", "is_auto_updating"]
    ordering_fields = ["name", "created_at", "segment_size"]
    ordering = ["name"]

    @action(detail=True, methods=["get"])
    def segment_analytics(self, request, pk=None):
        """Get segment analytics."""
        segment = self.get_object()

        analytics = {
            "segment_size": segment.segment_size,
            "engagement_rate": segment.engagement_rate,
            "conversion_rate": segment.conversion_rate,
            "lifetime_value": float(segment.lifetime_value),
            "segment_type": segment.segment_type,
            "criteria": segment.criteria,
            "filters": segment.filters,
            "last_updated": segment.last_updated.isoformat(),
        }

        return Response(analytics, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def update_segment(self, request, pk=None):
        """Update segment members."""
        segment = self.get_object()

        # This would trigger segment update logic
        segment.is_auto_updating = True
        segment.save()

        return Response(
            {
                "message": "Segment update initiated",
                "segment_id": str(segment.id),
                "estimated_completion": "5 minutes",
            },
            status=status.HTTP_200_OK,
        )


class CustomerTouchpointViewSet(BaseCXViewSet):
    """Customer Touchpoint management."""

    queryset = CustomerTouchpoint.objects.all()
    serializer_class = CustomerTouchpointSerializer
    search_fields = ["touchpoint_type", "customer__email"]
    filterset_fields = ["touchpoint_type", "outcome"]
    ordering_fields = ["occurred_at", "sentiment_score", "satisfaction_score"]
    ordering = ["-occurred_at"]

    @action(detail=False, methods=["get"])
    def touchpoint_analytics(self, request):
        """Get touchpoint analytics."""
        organization = get_current_organization(request)
        if not organization:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get touchpoints for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_touchpoints = CustomerTouchpoint.objects.filter(
            organization=organization, occurred_at__gte=thirty_days_ago
        )

        analytics = {
            "total_touchpoints": recent_touchpoints.count(),
            "average_sentiment": recent_touchpoints.aggregate(
                avg_sentiment=Avg("sentiment_score")
            )["avg_sentiment"]
            or 0,
            "average_satisfaction": recent_touchpoints.aggregate(
                avg_satisfaction=Avg("satisfaction_score")
            )["avg_satisfaction"]
            or 0,
            "touchpoints_by_type": {},
            "recent_touchpoints": [],
        }

        # Group by touchpoint type
        for touchpoint_type in recent_touchpoints.values_list(
            "touchpoint_type", flat=True
        ).distinct():
            count = recent_touchpoints.filter(touchpoint_type=touchpoint_type).count()
            analytics["touchpoints_by_type"][touchpoint_type] = count

        # Get recent touchpoints
        recent = recent_touchpoints.order_by("-occurred_at")[:20]
        analytics["recent_touchpoints"] = [
            {
                "id": str(touchpoint.id),
                "customer_id": str(touchpoint.customer.id),
                "touchpoint_type": touchpoint.touchpoint_type,
                "sentiment_score": touchpoint.sentiment_score,
                "satisfaction_score": touchpoint.satisfaction_score,
                "occurred_at": touchpoint.occurred_at.isoformat(),
                "duration": touchpoint.duration,
                "outcome": touchpoint.outcome,
            }
            for touchpoint in recent
        ]

        return Response(analytics, status=status.HTTP_200_OK)
