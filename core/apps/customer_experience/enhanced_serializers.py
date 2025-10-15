"""
Enhanced Customer Experience serializers for advanced capabilities.
"""

from rest_framework import serializers
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


class CustomerIntelligenceSerializer(serializers.ModelSerializer):
    """Serializer for Customer Intelligence."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = CustomerIntelligence
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_confidence_threshold(self, value):
        """Validate confidence threshold."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Confidence threshold must be between 0 and 1."
            )
        return value

    def validate_accuracy(self, value):
        """Validate accuracy."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Accuracy must be between 0 and 1.")
        return value


class HyperPersonalizationEngineSerializer(serializers.ModelSerializer):
    """Serializer for Hyper-personalization Engine."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = HyperPersonalizationEngine
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_confidence_threshold(self, value):
        """Validate confidence threshold."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Confidence threshold must be between 0 and 1."
            )
        return value

    def validate_learning_rate(self, value):
        """Validate learning rate."""
        if not 0 < value <= 1:
            raise serializers.ValidationError("Learning rate must be between 0 and 1.")
        return value


class CustomerSuccessManagementSerializer(serializers.ModelSerializer):
    """Serializer for Customer Success Management."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = CustomerSuccessManagement
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_success_rate(self, value):
        """Validate success rate."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Success rate must be between 0 and 1.")
        return value

    def validate_customer_retention(self, value):
        """Validate customer retention."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Customer retention must be between 0 and 1."
            )
        return value


class AdvancedFeedbackSystemSerializer(serializers.ModelSerializer):
    """Serializer for Advanced Feedback System."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AdvancedFeedbackSystem
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_response_rate(self, value):
        """Validate response rate."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Response rate must be between 0 and 1.")
        return value

    def validate_sentiment_accuracy(self, value):
        """Validate sentiment accuracy."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Sentiment accuracy must be between 0 and 1."
            )
        return value


class CustomerAdvocacyPlatformSerializer(serializers.ModelSerializer):
    """Serializer for Customer Advocacy Platform."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = CustomerAdvocacyPlatform
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_referral_rate(self, value):
        """Validate referral rate."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Referral rate must be between 0 and 1.")
        return value

    def validate_advocacy_score(self, value):
        """Validate advocacy score."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Advocacy score must be between 0 and 1.")
        return value


class CustomerInsightSerializer(serializers.ModelSerializer):
    """Serializer for Customer Insight."""

    customer_email = serializers.ReadOnlyField(source="customer.email")

    class Meta:
        model = CustomerInsight
        fields = "__all__"
        read_only_fields = ("organization", "generated_at")

    def validate_confidence_score(self, value):
        """Validate confidence score."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Confidence score must be between 0 and 1."
            )
        return value


class PersonalizationRuleSerializer(serializers.ModelSerializer):
    """Serializer for Personalization Rule."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = PersonalizationRule
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "last_updated")

    def validate_priority(self, value):
        """Validate priority."""
        if value < 0:
            raise serializers.ValidationError("Priority must be non-negative.")
        return value

    def validate_success_rate(self, value):
        """Validate success rate."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Success rate must be between 0 and 1.")
        return value


class CustomerSegmentSerializer(serializers.ModelSerializer):
    """Serializer for Customer Segment."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = CustomerSegment
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "last_updated")

    def validate_engagement_rate(self, value):
        """Validate engagement rate."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Engagement rate must be between 0 and 1."
            )
        return value

    def validate_conversion_rate(self, value):
        """Validate conversion rate."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Conversion rate must be between 0 and 1."
            )
        return value


class CustomerTouchpointSerializer(serializers.ModelSerializer):
    """Serializer for Customer Touchpoint."""

    customer_email = serializers.ReadOnlyField(source="customer.email")

    class Meta:
        model = CustomerTouchpoint
        fields = "__all__"
        read_only_fields = ("organization", "occurred_at")

    def validate_sentiment_score(self, value):
        """Validate sentiment score."""
        if not -1 <= value <= 1:
            raise serializers.ValidationError(
                "Sentiment score must be between -1 and 1."
            )
        return value

    def validate_satisfaction_score(self, value):
        """Validate satisfaction score."""
        if not 0 <= value <= 5:
            raise serializers.ValidationError(
                "Satisfaction score must be between 0 and 5."
            )
        return value


class Customer360RequestSerializer(serializers.Serializer):
    """Serializer for Customer 360° analysis requests."""

    customer_id = serializers.UUIDField()
    analysis_depth = serializers.ChoiceField(
        choices=["basic", "detailed", "comprehensive"], default="detailed"
    )
    include_predictions = serializers.BooleanField(default=True)
    include_recommendations = serializers.BooleanField(default=True)

    def validate_customer_id(self, value):
        """Validate customer ID."""
        if not value:
            raise serializers.ValidationError("Customer ID is required.")
        return value


class PersonalizationRequestSerializer(serializers.Serializer):
    """Serializer for personalization requests."""

    customer_id = serializers.UUIDField()
    content_type = serializers.CharField(max_length=100)
    base_content = serializers.CharField(max_length=10000)
    personalization_options = serializers.JSONField(default=dict, required=False)

    def validate_customer_id(self, value):
        """Validate customer ID."""
        if not value:
            raise serializers.ValidationError("Customer ID is required.")
        return value

    def validate_base_content(self, value):
        """Validate base content."""
        if not value.strip():
            raise serializers.ValidationError("Base content cannot be empty.")
        return value


class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer for recommendation requests."""

    customer_id = serializers.UUIDField()
    recommendation_type = serializers.CharField(max_length=100)
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)
    include_explanations = serializers.BooleanField(default=True)

    def validate_customer_id(self, value):
        """Validate customer ID."""
        if not value:
            raise serializers.ValidationError("Customer ID is required.")
        return value


class OnboardingRequestSerializer(serializers.Serializer):
    """Serializer for onboarding automation requests."""

    customer_id = serializers.UUIDField()
    onboarding_type = serializers.ChoiceField(
        choices=["standard", "premium", "enterprise"], default="standard"
    )
    custom_steps = serializers.JSONField(default=list, required=False)
    success_criteria = serializers.JSONField(default=list, required=False)

    def validate_customer_id(self, value):
        """Validate customer ID."""
        if not value:
            raise serializers.ValidationError("Customer ID is required.")
        return value


class FeedbackRequestSerializer(serializers.Serializer):
    """Serializer for feedback collection requests."""

    customer_id = serializers.UUIDField()
    feedback_type = serializers.CharField(max_length=100)
    feedback_data = serializers.JSONField()
    collection_channel = serializers.CharField(max_length=100, default="web")
    priority = serializers.ChoiceField(
        choices=["low", "medium", "high"], default="medium"
    )

    def validate_customer_id(self, value):
        """Validate customer ID."""
        if not value:
            raise serializers.ValidationError("Customer ID is required.")
        return value

    def validate_feedback_data(self, value):
        """Validate feedback data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Feedback data must be a dictionary.")
        return value


class ReferralRequestSerializer(serializers.Serializer):
    """Serializer for referral program requests."""

    customer_id = serializers.UUIDField()
    referral_data = serializers.JSONField()
    program_type = serializers.CharField(max_length=100, default="standard")
    reward_type = serializers.ChoiceField(
        choices=["credit", "discount", "cash"], default="credit"
    )

    def validate_customer_id(self, value):
        """Validate customer ID."""
        if not value:
            raise serializers.ValidationError("Customer ID is required.")
        return value

    def validate_referral_data(self, value):
        """Validate referral data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Referral data must be a dictionary.")
        return value


class TestimonialRequestSerializer(serializers.Serializer):
    """Serializer for testimonial collection requests."""

    customer_id = serializers.UUIDField()
    testimonial_data = serializers.JSONField()
    collection_method = serializers.ChoiceField(
        choices=["survey", "interview", "video"], default="survey"
    )
    consent_required = serializers.BooleanField(default=True)

    def validate_customer_id(self, value):
        """Validate customer ID."""
        if not value:
            raise serializers.ValidationError("Customer ID is required.")
        return value

    def validate_testimonial_data(self, value):
        """Validate testimonial data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Testimonial data must be a dictionary.")
        return value


class SegmentUpdateRequestSerializer(serializers.Serializer):
    """Serializer for segment update requests."""

    segment_id = serializers.UUIDField()
    update_type = serializers.ChoiceField(
        choices=["manual", "automatic", "scheduled"], default="automatic"
    )
    criteria_changes = serializers.JSONField(default=dict, required=False)
    force_update = serializers.BooleanField(default=False)

    def validate_segment_id(self, value):
        """Validate segment ID."""
        if not value:
            raise serializers.ValidationError("Segment ID is required.")
        return value


class TouchpointAnalyticsRequestSerializer(serializers.Serializer):
    """Serializer for touchpoint analytics requests."""

    date_range = serializers.ChoiceField(
        choices=["7_days", "30_days", "90_days", "custom"], default="30_days"
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    touchpoint_types = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False
    )
    customer_segments = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )

    def validate(self, data):
        """Validate date range and custom dates."""
        if data.get("date_range") == "custom":
            if not data.get("start_date") or not data.get("end_date"):
                raise serializers.ValidationError(
                    "Start date and end date are required for custom date range."
                )
            if data["start_date"] > data["end_date"]:
                raise serializers.ValidationError("Start date must be before end date.")
        return data
