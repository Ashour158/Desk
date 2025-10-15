"""
Customer Experience filters for API endpoints.
"""

import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    CustomerJourney,
    CustomerTouchpoint,
    CustomerPersona,
    CustomerSegment,
    PersonalizationRule,
    ProactiveSupport,
    CustomerFeedback,
    CustomerHealthScore,
    OmnichannelExperience,
)


class CustomerJourneyFilter(django_filters.FilterSet):
    """Customer journey filters."""

    current_stage = django_filters.ChoiceFilter(choices=CustomerJourney.JOURNEY_STAGES)
    is_active = django_filters.BooleanFilter()
    is_completed = django_filters.BooleanFilter()
    min_health_score = django_filters.NumberFilter(
        field_name="health_score", lookup_expr="gte"
    )
    max_health_score = django_filters.NumberFilter(
        field_name="health_score", lookup_expr="lte"
    )
    min_satisfaction_score = django_filters.NumberFilter(
        field_name="satisfaction_score", lookup_expr="gte"
    )
    max_satisfaction_score = django_filters.NumberFilter(
        field_name="satisfaction_score", lookup_expr="lte"
    )
    min_engagement_score = django_filters.NumberFilter(
        field_name="engagement_score", lookup_expr="gte"
    )
    max_engagement_score = django_filters.NumberFilter(
        field_name="engagement_score", lookup_expr="lte"
    )
    journey_start_after = django_filters.DateTimeFilter(
        field_name="journey_start", lookup_expr="gte"
    )
    journey_start_before = django_filters.DateTimeFilter(
        field_name="journey_start", lookup_expr="lte"
    )
    last_activity_after = django_filters.DateTimeFilter(
        field_name="last_activity", lookup_expr="gte"
    )
    last_activity_before = django_filters.DateTimeFilter(
        field_name="last_activity", lookup_expr="lte"
    )

    # Custom filters
    long_running = django_filters.BooleanFilter(method="filter_long_running")
    high_satisfaction = django_filters.BooleanFilter(method="filter_high_satisfaction")

    class Meta:
        model = CustomerJourney
        fields = ["current_stage", "is_active", "is_completed"]

    def filter_long_running(self, queryset, name, value):
        """Filter for journeys running longer than 30 days."""
        if value:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(journey_start__lte=thirty_days_ago)
        return queryset

    def filter_high_satisfaction(self, queryset, name, value):
        """Filter for journeys with high satisfaction scores."""
        if value:
            return queryset.filter(satisfaction_score__gte=4.0)
        return queryset


class CustomerTouchpointFilter(django_filters.FilterSet):
    """Customer touchpoint filters."""

    touchpoint_type = django_filters.ChoiceFilter(
        choices=CustomerTouchpoint.TOUCHPOINT_TYPES
    )
    channel = django_filters.ChoiceFilter(choices=CustomerTouchpoint.CHANNELS)
    min_satisfaction_rating = django_filters.NumberFilter(
        field_name="satisfaction_rating", lookup_expr="gte"
    )
    max_satisfaction_rating = django_filters.NumberFilter(
        field_name="satisfaction_rating", lookup_expr="lte"
    )
    min_sentiment_score = django_filters.NumberFilter(
        field_name="sentiment_score", lookup_expr="gte"
    )
    max_sentiment_score = django_filters.NumberFilter(
        field_name="sentiment_score", lookup_expr="lte"
    )
    min_duration_minutes = django_filters.NumberFilter(
        field_name="duration_minutes", lookup_expr="gte"
    )
    max_duration_minutes = django_filters.NumberFilter(
        field_name="duration_minutes", lookup_expr="lte"
    )
    occurred_after = django_filters.DateTimeFilter(
        field_name="occurred_at", lookup_expr="gte"
    )
    occurred_before = django_filters.DateTimeFilter(
        field_name="occurred_at", lookup_expr="lte"
    )
    related_entity_type = django_filters.CharFilter()

    # Custom filters
    positive_sentiment = django_filters.BooleanFilter(
        method="filter_positive_sentiment"
    )
    high_satisfaction = django_filters.BooleanFilter(method="filter_high_satisfaction")
    recent_touchpoints = django_filters.BooleanFilter(
        method="filter_recent_touchpoints"
    )

    class Meta:
        model = CustomerTouchpoint
        fields = ["touchpoint_type", "channel", "related_entity_type"]

    def filter_positive_sentiment(self, queryset, name, value):
        """Filter for touchpoints with positive sentiment."""
        if value:
            return queryset.filter(sentiment_score__gte=0.1)
        return queryset

    def filter_high_satisfaction(self, queryset, name, value):
        """Filter for touchpoints with high satisfaction ratings."""
        if value:
            return queryset.filter(satisfaction_rating__gte=4)
        return queryset

    def filter_recent_touchpoints(self, queryset, name, value):
        """Filter for touchpoints from the last 7 days."""
        if value:
            seven_days_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(occurred_at__gte=seven_days_ago)
        return queryset


class CustomerPersonaFilter(django_filters.FilterSet):
    """Customer persona filters."""

    is_active = django_filters.BooleanFilter()
    min_customer_count = django_filters.NumberFilter(
        field_name="customer_count", lookup_expr="gte"
    )
    max_customer_count = django_filters.NumberFilter(
        field_name="customer_count", lookup_expr="lte"
    )
    min_avg_satisfaction = django_filters.NumberFilter(
        field_name="avg_satisfaction", lookup_expr="gte"
    )
    max_avg_satisfaction = django_filters.NumberFilter(
        field_name="avg_satisfaction", lookup_expr="lte"
    )
    min_avg_engagement = django_filters.NumberFilter(
        field_name="avg_engagement", lookup_expr="gte"
    )
    max_avg_engagement = django_filters.NumberFilter(
        field_name="avg_engagement", lookup_expr="lte"
    )
    min_churn_rate = django_filters.NumberFilter(
        field_name="churn_rate", lookup_expr="gte"
    )
    max_churn_rate = django_filters.NumberFilter(
        field_name="churn_rate", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    # Custom filters
    popular_personas = django_filters.BooleanFilter(method="filter_popular_personas")
    high_satisfaction_personas = django_filters.BooleanFilter(
        method="filter_high_satisfaction_personas"
    )

    class Meta:
        model = CustomerPersona
        fields = ["is_active"]

    def filter_popular_personas(self, queryset, name, value):
        """Filter for personas with many customers."""
        if value:
            return queryset.filter(customer_count__gte=10)
        return queryset

    def filter_high_satisfaction_personas(self, queryset, name, value):
        """Filter for personas with high satisfaction scores."""
        if value:
            return queryset.filter(avg_satisfaction__gte=4.0)
        return queryset


class CustomerSegmentFilter(django_filters.FilterSet):
    """Customer segment filters."""

    is_active = django_filters.BooleanFilter()
    is_auto_generated = django_filters.BooleanFilter()
    min_customer_count = django_filters.NumberFilter(
        field_name="customer_count", lookup_expr="gte"
    )
    max_customer_count = django_filters.NumberFilter(
        field_name="customer_count", lookup_expr="lte"
    )
    min_avg_value = django_filters.NumberFilter(
        field_name="avg_value", lookup_expr="gte"
    )
    max_avg_value = django_filters.NumberFilter(
        field_name="avg_value", lookup_expr="lte"
    )
    min_growth_rate = django_filters.NumberFilter(
        field_name="growth_rate", lookup_expr="gte"
    )
    max_growth_rate = django_filters.NumberFilter(
        field_name="growth_rate", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    # Custom filters
    large_segments = django_filters.BooleanFilter(method="filter_large_segments")
    growing_segments = django_filters.BooleanFilter(method="filter_growing_segments")

    class Meta:
        model = CustomerSegment
        fields = ["is_active", "is_auto_generated"]

    def filter_large_segments(self, queryset, name, value):
        """Filter for segments with many customers."""
        if value:
            return queryset.filter(customer_count__gte=50)
        return queryset

    def filter_growing_segments(self, queryset, name, value):
        """Filter for segments with positive growth."""
        if value:
            return queryset.filter(growth_rate__gt=0)
        return queryset


class PersonalizationRuleFilter(django_filters.FilterSet):
    """Personalization rule filters."""

    rule_type = django_filters.ChoiceFilter(choices=PersonalizationRule.RULE_TYPES)
    is_active = django_filters.BooleanFilter()
    is_auto_generated = django_filters.BooleanFilter()
    min_priority = django_filters.NumberFilter(field_name="priority", lookup_expr="gte")
    max_priority = django_filters.NumberFilter(field_name="priority", lookup_expr="lte")
    min_trigger_count = django_filters.NumberFilter(
        field_name="trigger_count", lookup_expr="gte"
    )
    max_trigger_count = django_filters.NumberFilter(
        field_name="trigger_count", lookup_expr="lte"
    )
    min_success_rate = django_filters.NumberFilter(
        field_name="success_rate", lookup_expr="gte"
    )
    max_success_rate = django_filters.NumberFilter(
        field_name="success_rate", lookup_expr="lte"
    )
    min_impact_score = django_filters.NumberFilter(
        field_name="impact_score", lookup_expr="gte"
    )
    max_impact_score = django_filters.NumberFilter(
        field_name="impact_score", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    # Custom filters
    high_priority = django_filters.BooleanFilter(method="filter_high_priority")
    successful_rules = django_filters.BooleanFilter(method="filter_successful_rules")

    class Meta:
        model = PersonalizationRule
        fields = ["rule_type", "is_active", "is_auto_generated"]

    def filter_high_priority(self, queryset, name, value):
        """Filter for high priority rules."""
        if value:
            return queryset.filter(priority__gte=8)
        return queryset

    def filter_successful_rules(self, queryset, name, value):
        """Filter for rules with high success rates."""
        if value:
            return queryset.filter(success_rate__gte=80)
        return queryset


class ProactiveSupportFilter(django_filters.FilterSet):
    """Proactive support filters."""

    trigger_type = django_filters.ChoiceFilter(choices=ProactiveSupport.TRIGGER_TYPES)
    action_type = django_filters.ChoiceFilter(choices=ProactiveSupport.ACTION_TYPES)
    is_active = django_filters.BooleanFilter()
    min_trigger_count = django_filters.NumberFilter(
        field_name="trigger_count", lookup_expr="gte"
    )
    max_trigger_count = django_filters.NumberFilter(
        field_name="trigger_count", lookup_expr="lte"
    )
    min_success_count = django_filters.NumberFilter(
        field_name="success_count", lookup_expr="gte"
    )
    max_success_count = django_filters.NumberFilter(
        field_name="success_count", lookup_expr="lte"
    )
    min_response_rate = django_filters.NumberFilter(
        field_name="response_rate", lookup_expr="gte"
    )
    max_response_rate = django_filters.NumberFilter(
        field_name="response_rate", lookup_expr="lte"
    )
    last_triggered_after = django_filters.DateTimeFilter(
        field_name="last_triggered", lookup_expr="gte"
    )
    last_triggered_before = django_filters.DateTimeFilter(
        field_name="last_triggered", lookup_expr="lte"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    # Custom filters
    active_supports = django_filters.BooleanFilter(method="filter_active_supports")
    successful_supports = django_filters.BooleanFilter(
        method="filter_successful_supports"
    )

    class Meta:
        model = ProactiveSupport
        fields = ["trigger_type", "action_type", "is_active"]

    def filter_active_supports(self, queryset, name, value):
        """Filter for supports that have been triggered recently."""
        if value:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(last_triggered__gte=thirty_days_ago)
        return queryset

    def filter_successful_supports(self, queryset, name, value):
        """Filter for supports with high success rates."""
        if value:
            return queryset.filter(response_rate__gte=70)
        return queryset


class CustomerFeedbackFilter(django_filters.FilterSet):
    """Customer feedback filters."""

    feedback_type = django_filters.ChoiceFilter(choices=CustomerFeedback.FEEDBACK_TYPES)
    is_processed = django_filters.BooleanFilter()
    is_public = django_filters.BooleanFilter()
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    max_rating = django_filters.NumberFilter(field_name="rating", lookup_expr="lte")
    min_sentiment_score = django_filters.NumberFilter(
        field_name="sentiment_score", lookup_expr="gte"
    )
    max_sentiment_score = django_filters.NumberFilter(
        field_name="sentiment_score", lookup_expr="lte"
    )
    sentiment_label = django_filters.CharFilter()
    related_entity_type = django_filters.CharFilter()
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )
    processed_after = django_filters.DateTimeFilter(
        field_name="processed_at", lookup_expr="gte"
    )
    processed_before = django_filters.DateTimeFilter(
        field_name="processed_at", lookup_expr="lte"
    )

    # Custom filters
    positive_feedback = django_filters.BooleanFilter(method="filter_positive_feedback")
    high_rating_feedback = django_filters.BooleanFilter(
        method="filter_high_rating_feedback"
    )
    unprocessed_feedback = django_filters.BooleanFilter(
        method="filter_unprocessed_feedback"
    )

    class Meta:
        model = CustomerFeedback
        fields = [
            "feedback_type",
            "is_processed",
            "is_public",
            "sentiment_label",
            "related_entity_type",
        ]

    def filter_positive_feedback(self, queryset, name, value):
        """Filter for positive sentiment feedback."""
        if value:
            return queryset.filter(sentiment_score__gte=0.1)
        return queryset

    def filter_high_rating_feedback(self, queryset, name, value):
        """Filter for high rating feedback."""
        if value:
            return queryset.filter(rating__gte=4)
        return queryset

    def filter_unprocessed_feedback(self, queryset, name, value):
        """Filter for unprocessed feedback."""
        if value:
            return queryset.filter(is_processed=False)
        return queryset


class CustomerHealthScoreFilter(django_filters.FilterSet):
    """Customer health score filters."""

    is_at_risk = django_filters.BooleanFilter()
    requires_attention = django_filters.BooleanFilter()
    min_overall_score = django_filters.NumberFilter(
        field_name="overall_score", lookup_expr="gte"
    )
    max_overall_score = django_filters.NumberFilter(
        field_name="overall_score", lookup_expr="lte"
    )
    min_engagement_score = django_filters.NumberFilter(
        field_name="engagement_score", lookup_expr="gte"
    )
    max_engagement_score = django_filters.NumberFilter(
        field_name="engagement_score", lookup_expr="lte"
    )
    min_satisfaction_score = django_filters.NumberFilter(
        field_name="satisfaction_score", lookup_expr="gte"
    )
    max_satisfaction_score = django_filters.NumberFilter(
        field_name="satisfaction_score", lookup_expr="lte"
    )
    min_usage_score = django_filters.NumberFilter(
        field_name="usage_score", lookup_expr="gte"
    )
    max_usage_score = django_filters.NumberFilter(
        field_name="usage_score", lookup_expr="lte"
    )
    min_support_score = django_filters.NumberFilter(
        field_name="support_score", lookup_expr="gte"
    )
    max_support_score = django_filters.NumberFilter(
        field_name="support_score", lookup_expr="lte"
    )
    min_churn_risk = django_filters.NumberFilter(
        field_name="churn_risk", lookup_expr="gte"
    )
    max_churn_risk = django_filters.NumberFilter(
        field_name="churn_risk", lookup_expr="lte"
    )
    calculated_after = django_filters.DateTimeFilter(
        field_name="calculated_at", lookup_expr="gte"
    )
    calculated_before = django_filters.DateTimeFilter(
        field_name="calculated_at", lookup_expr="lte"
    )
    next_review_after = django_filters.DateTimeFilter(
        field_name="next_review_date", lookup_expr="gte"
    )
    next_review_before = django_filters.DateTimeFilter(
        field_name="next_review_date", lookup_expr="lte"
    )

    # Custom filters
    healthy_customers = django_filters.BooleanFilter(method="filter_healthy_customers")
    at_risk_customers = django_filters.BooleanFilter(method="filter_at_risk_customers")
    high_churn_risk = django_filters.BooleanFilter(method="filter_high_churn_risk")

    class Meta:
        model = CustomerHealthScore
        fields = ["is_at_risk", "requires_attention"]

    def filter_healthy_customers(self, queryset, name, value):
        """Filter for customers with good health scores."""
        if value:
            return queryset.filter(overall_score__gte=70, churn_risk__lte=0.3)
        return queryset

    def filter_at_risk_customers(self, queryset, name, value):
        """Filter for customers at risk."""
        if value:
            return queryset.filter(is_at_risk=True)
        return queryset

    def filter_high_churn_risk(self, queryset, name, value):
        """Filter for customers with high churn risk."""
        if value:
            return queryset.filter(churn_risk__gte=0.7)
        return queryset


class OmnichannelExperienceFilter(django_filters.FilterSet):
    """Omnichannel experience filters."""

    is_completed = django_filters.BooleanFilter()
    is_successful = django_filters.BooleanFilter()
    primary_channel = django_filters.CharFilter()
    min_duration_minutes = django_filters.NumberFilter(
        field_name="duration_minutes", lookup_expr="gte"
    )
    max_duration_minutes = django_filters.NumberFilter(
        field_name="duration_minutes", lookup_expr="lte"
    )
    min_satisfaction_score = django_filters.NumberFilter(
        field_name="satisfaction_score", lookup_expr="gte"
    )
    max_satisfaction_score = django_filters.NumberFilter(
        field_name="satisfaction_score", lookup_expr="lte"
    )
    min_effort_score = django_filters.NumberFilter(
        field_name="effort_score", lookup_expr="gte"
    )
    max_effort_score = django_filters.NumberFilter(
        field_name="effort_score", lookup_expr="lte"
    )
    resolution_achieved = django_filters.BooleanFilter()
    journey_stage = django_filters.CharFilter()
    start_time_after = django_filters.DateTimeFilter(
        field_name="start_time", lookup_expr="gte"
    )
    start_time_before = django_filters.DateTimeFilter(
        field_name="start_time", lookup_expr="lte"
    )
    end_time_after = django_filters.DateTimeFilter(
        field_name="end_time", lookup_expr="gte"
    )
    end_time_before = django_filters.DateTimeFilter(
        field_name="end_time", lookup_expr="lte"
    )

    # Custom filters
    successful_experiences = django_filters.BooleanFilter(
        method="filter_successful_experiences"
    )
    high_satisfaction_experiences = django_filters.BooleanFilter(
        method="filter_high_satisfaction_experiences"
    )
    multi_channel_experiences = django_filters.BooleanFilter(
        method="filter_multi_channel_experiences"
    )

    class Meta:
        model = OmnichannelExperience
        fields = [
            "is_completed",
            "is_successful",
            "primary_channel",
            "resolution_achieved",
            "journey_stage",
        ]

    def filter_successful_experiences(self, queryset, name, value):
        """Filter for successful experiences."""
        if value:
            return queryset.filter(is_successful=True)
        return queryset

    def filter_high_satisfaction_experiences(self, queryset, name, value):
        """Filter for experiences with high satisfaction."""
        if value:
            return queryset.filter(satisfaction_score__gte=4)
        return queryset

    def filter_multi_channel_experiences(self, queryset, name, value):
        """Filter for experiences using multiple channels."""
        if value:
            return queryset.filter(channel_switches__gte=1)
        return queryset
