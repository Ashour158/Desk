"""
Enhanced Customer Experience models for advanced capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.organizations.models import Organization
from apps.common.base_models import BaseModel, ConfigurationModel, MetricsModel
from apps.common.constants import (
    SHORT_FIELD_LENGTH,
    MEDIUM_FIELD_LENGTH,
    LONG_FIELD_LENGTH,
    VERY_LONG_FIELD_LENGTH,
)
import uuid

User = get_user_model()


class CustomerIntelligence(models.Model):
    """Advanced customer intelligence with 360° view and behavioral analytics."""

    INTELLIGENCE_TYPES = [
        ("customer_360", "Customer 360° View"),
        ("behavioral_analytics", "Behavioral Analytics"),
        ("purchase_intent", "Purchase Intent Prediction"),
        ("lifetime_value", "Customer Lifetime Value"),
        ("real_time_insights", "Real-time Customer Insights"),
        ("segmentation", "Customer Segmentation"),
        ("propensity_modeling", "Propensity Modeling"),
        ("engagement_scoring", "Engagement Scoring"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="customer_intelligence"
    )
    name = models.CharField(max_length=255)
    intelligence_type = models.CharField(max_length=50, choices=INTELLIGENCE_TYPES)
    description = models.TextField(blank=True)

    # Data sources
    data_sources = models.JSONField(default=list)
    integration_apis = models.JSONField(default=list)
    real_time_feeds = models.JSONField(default=list)

    # Configuration
    analysis_frequency = models.CharField(max_length=50, default="daily")
    confidence_threshold = models.FloatField(default=0.8)
    update_frequency = models.CharField(max_length=50, default="real_time")

    # Performance metrics
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)

    # Usage statistics
    total_analyses = models.IntegerField(default=0)
    successful_predictions = models.IntegerField(default=0)
    insights_generated = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_processing = models.BooleanField(default=False)
    last_analysis = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "intelligence_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.intelligence_type})"


class HyperPersonalizationEngine(models.Model):
    """Hyper-personalization engine with dynamic content and AI-driven recommendations."""

    PERSONALIZATION_TYPES = [
        ("dynamic_content", "Dynamic Content Personalization"),
        ("ai_recommendations", "AI-driven Recommendations"),
        ("contextual_messaging", "Contextual Messaging"),
        ("personalized_workflows", "Personalized Workflows"),
        ("adaptive_ui", "Adaptive User Interfaces"),
        ("behavioral_targeting", "Behavioral Targeting"),
        ("predictive_personalization", "Predictive Personalization"),
        ("real_time_personalization", "Real-time Personalization"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="personalization_engines"
    )
    name = models.CharField(max_length=255)
    personalization_type = models.CharField(
        max_length=50, choices=PERSONALIZATION_TYPES
    )
    description = models.TextField(blank=True)

    # Configuration
    target_audience = models.JSONField(default=list)  # Customer segments
    personalization_rules = models.JSONField(default=list)
    content_templates = models.JSONField(default=list)
    recommendation_models = models.JSONField(default=list)

    # AI/ML settings
    ml_models = models.JSONField(default=list)
    confidence_threshold = models.FloatField(default=0.7)
    learning_rate = models.FloatField(default=0.01)
    update_frequency = models.CharField(max_length=50, default="real_time")

    # Performance metrics
    personalization_accuracy = models.FloatField(default=0.0)
    engagement_improvement = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)
    user_satisfaction = models.FloatField(default=0.0)

    # Usage statistics
    total_personalizations = models.IntegerField(default=0)
    successful_personalizations = models.IntegerField(default=0)
    content_views = models.IntegerField(default=0)
    click_through_rate = models.FloatField(default=0.0)

    # Status
    is_active = models.BooleanField(default=True)
    is_learning = models.BooleanField(default=False)
    last_updated = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "personalization_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.personalization_type})"


class CustomerSuccessManagement(models.Model):
    """Customer success management with onboarding automation and expansion detection."""

    SUCCESS_TYPES = [
        ("onboarding_automation", "Onboarding Automation"),
        ("adoption_tracking", "Adoption Tracking"),
        ("success_metrics", "Success Metrics & KPIs"),
        ("proactive_intervention", "Proactive Intervention"),
        ("expansion_detection", "Expansion Opportunity Detection"),
        ("health_monitoring", "Customer Health Monitoring"),
        ("success_playbooks", "Success Playbooks"),
        ("outcome_tracking", "Outcome Tracking"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="success_management"
    )
    name = models.CharField(max_length=255)
    success_type = models.CharField(max_length=50, choices=SUCCESS_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    target_customers = models.JSONField(default=list)
    success_criteria = models.JSONField(default=list)
    intervention_rules = models.JSONField(default=list)
    playbook_templates = models.JSONField(default=list)

    # Automation settings
    automation_rules = models.JSONField(default=list)
    trigger_conditions = models.JSONField(default=list)
    action_sequences = models.JSONField(default=list)
    escalation_paths = models.JSONField(default=list)

    # Performance metrics
    success_rate = models.FloatField(default=0.0)
    customer_retention = models.FloatField(default=0.0)
    expansion_rate = models.FloatField(default=0.0)
    time_to_value = models.FloatField(default=0.0)

    # Usage statistics
    total_customers = models.IntegerField(default=0)
    successful_onboardings = models.IntegerField(default=0)
    interventions_triggered = models.IntegerField(default=0)
    expansions_detected = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_monitoring = models.BooleanField(default=False)
    last_monitoring = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "success_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.success_type})"


class AdvancedFeedbackSystem(models.Model):
    """Advanced feedback and survey system with real-time sentiment analysis."""

    FEEDBACK_TYPES = [
        ("multi_channel", "Multi-channel Feedback Collection"),
        ("sentiment_analysis", "Real-time Sentiment Analysis"),
        ("automated_surveys", "Automated Survey Distribution"),
        ("feedback_analytics", "Feedback Analytics & Insights"),
        ("actionable_recommendations", "Actionable Recommendations"),
        ("nps_tracking", "NPS Tracking"),
        ("csat_monitoring", "CSAT Monitoring"),
        ("feedback_automation", "Feedback Automation"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="feedback_systems"
    )
    name = models.CharField(max_length=255)
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    collection_channels = models.JSONField(default=list)
    survey_templates = models.JSONField(default=list)
    sentiment_models = models.JSONField(default=list)
    analysis_rules = models.JSONField(default=list)

    # Automation settings
    distribution_rules = models.JSONField(default=list)
    analysis_automation = models.JSONField(default=list)
    alert_conditions = models.JSONField(default=list)
    response_automation = models.JSONField(default=list)

    # Performance metrics
    response_rate = models.FloatField(default=0.0)
    sentiment_accuracy = models.FloatField(default=0.0)
    action_completion_rate = models.FloatField(default=0.0)
    customer_satisfaction = models.FloatField(default=0.0)

    # Usage statistics
    total_surveys = models.IntegerField(default=0)
    total_responses = models.IntegerField(default=0)
    sentiment_analyses = models.IntegerField(default=0)
    actions_taken = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_collecting = models.BooleanField(default=False)
    last_collection = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "feedback_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.feedback_type})"


class CustomerAdvocacyPlatform(models.Model):
    """Customer advocacy platform with referral programs and community building."""

    ADVOCACY_TYPES = [
        ("referral_programs", "Referral Program Management"),
        ("testimonial_collection", "Testimonial Collection"),
        ("case_study_generation", "Case Study Generation"),
        ("social_proof", "Social Proof Integration"),
        ("community_building", "Community Building Tools"),
        ("advocate_recognition", "Advocate Recognition"),
        ("content_amplification", "Content Amplification"),
        ("advocacy_analytics", "Advocacy Analytics"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="advocacy_platforms"
    )
    name = models.CharField(max_length=255)
    advocacy_type = models.CharField(max_length=50, choices=ADVOCACY_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    program_rules = models.JSONField(default=list)
    reward_systems = models.JSONField(default=list)
    content_templates = models.JSONField(default=list)
    social_integrations = models.JSONField(default=list)

    # Automation settings
    referral_automation = models.JSONField(default=list)
    content_automation = models.JSONField(default=list)
    recognition_automation = models.JSONField(default=list)
    analytics_automation = models.JSONField(default=list)

    # Performance metrics
    referral_rate = models.FloatField(default=0.0)
    advocacy_score = models.FloatField(default=0.0)
    community_engagement = models.FloatField(default=0.0)
    content_amplification = models.FloatField(default=0.0)

    # Usage statistics
    total_advocates = models.IntegerField(default=0)
    total_referrals = models.IntegerField(default=0)
    testimonials_collected = models.IntegerField(default=0)
    case_studies_generated = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_running = models.BooleanField(default=False)
    last_activity = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "advocacy_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.advocacy_type})"


class CustomerInsight(models.Model):
    """Individual customer insights and analytics."""

    INSIGHT_TYPES = [
        ("behavioral", "Behavioral Insight"),
        ("predictive", "Predictive Insight"),
        ("sentiment", "Sentiment Insight"),
        ("engagement", "Engagement Insight"),
        ("value", "Value Insight"),
        ("risk", "Risk Insight"),
        ("opportunity", "Opportunity Insight"),
        ("preference", "Preference Insight"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="customer_insights"
    )
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="insights"
    )
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)

    # Insight data
    insight_data = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)
    source_systems = models.JSONField(default=list)

    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_actionable = models.BooleanField(default=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.customer.email} - {self.insight_type} ({self.confidence_score})"


class PersonalizationRule(models.Model):
    """Personalization rules for dynamic content and recommendations."""

    RULE_TYPES = [
        ("content", "Content Rule"),
        ("recommendation", "Recommendation Rule"),
        ("messaging", "Messaging Rule"),
        ("workflow", "Workflow Rule"),
        ("ui", "UI Rule"),
        ("targeting", "Targeting Rule"),
        ("timing", "Timing Rule"),
        ("channel", "Channel Rule"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="personalization_rules"
    )
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    description = models.TextField(blank=True)

    # Rule configuration
    conditions = models.JSONField(default=list)
    actions = models.JSONField(default=list)
    priority = models.IntegerField(default=0)

    # Targeting
    target_segments = models.JSONField(default=list)
    target_attributes = models.JSONField(default=list)

    # Performance
    success_rate = models.FloatField(default=0.0)
    engagement_rate = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)

    # Status
    is_active = models.BooleanField(default=True)
    is_learning = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-priority", "name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.rule_type})"


class CustomerSegment(models.Model):
    """Customer segments for targeting and personalization."""

    SEGMENT_TYPES = [
        ("demographic", "Demographic"),
        ("behavioral", "Behavioral"),
        ("psychographic", "Psychographic"),
        ("geographic", "Geographic"),
        ("value_based", "Value-based"),
        ("engagement", "Engagement"),
        ("lifecycle", "Lifecycle"),
        ("custom", "Custom"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="customer_segments"
    )
    name = models.CharField(max_length=255)
    segment_type = models.CharField(max_length=50, choices=SEGMENT_TYPES)
    description = models.TextField(blank=True)

    # Segment criteria
    criteria = models.JSONField(default=list)
    filters = models.JSONField(default=list)

    # Performance metrics
    segment_size = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)
    lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Status
    is_active = models.BooleanField(default=True)
    is_auto_updating = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.segment_type})"


class CustomerTouchpoint(models.Model):
    """Customer touchpoints for journey mapping and analytics."""

    TOUCHPOINT_TYPES = [
        ("website", "Website"),
        ("mobile_app", "Mobile App"),
        ("email", "Email"),
        ("phone", "Phone"),
        ("chat", "Live Chat"),
        ("social", "Social Media"),
        ("in_person", "In-Person"),
        ("support", "Support"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="touchpoints"
    )
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="touchpoints"
    )
    touchpoint_type = models.CharField(max_length=50, choices=TOUCHPOINT_TYPES)

    # Touchpoint data
    interaction_data = models.JSONField(default=dict)
    sentiment_score = models.FloatField(default=0.0)
    satisfaction_score = models.FloatField(default=0.0)

    # Metadata
    occurred_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(default=0.0)  # seconds
    outcome = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.customer.email} - {self.touchpoint_type} ({self.occurred_at})"
