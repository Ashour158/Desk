"""
Enhanced Advanced Communication Platform serializers for advanced capabilities.
"""

from rest_framework import serializers
from .enhanced_models import (
    UnifiedCommunicationHub,
    VideoAudioFeatures,
    AIPoweredCommunication,
    SocialMediaManagement,
    CommunicationIntelligence,
    CommunicationSession,
    CommunicationMessage,
    CommunicationAnalytic,
    CommunicationTemplate,
)


class UnifiedCommunicationHubSerializer(serializers.ModelSerializer):
    """Serializer for Unified Communication Hub."""

    class Meta:
        model = UnifiedCommunicationHub
        fields = [
            "id",
            "name",
            "hub_type",
            "communication_channels",
            "collaboration_features",
            "presence_management",
            "contact_center_config",
            "integration_settings",
            "total_users",
            "active_sessions",
            "total_messages",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_communication_channels(self, value):
        """Validate communication channels."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Communication channels must be a list.")
        return value

    def validate_collaboration_features(self, value):
        """Validate collaboration features."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Collaboration features must be a dictionary."
            )
        return value

    def validate_presence_management(self, value):
        """Validate presence management."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Presence management must be a dictionary."
            )
        return value

    def validate_contact_center_config(self, value):
        """Validate contact center config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Contact center config must be a dictionary."
            )
        return value

    def validate_integration_settings(self, value):
        """Validate integration settings."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Integration settings must be a dictionary."
            )
        return value


class VideoAudioFeaturesSerializer(serializers.ModelSerializer):
    """Serializer for Video & Audio Features."""

    class Meta:
        model = VideoAudioFeatures
        fields = [
            "id",
            "name",
            "feature_type",
            "video_config",
            "audio_config",
            "recording_settings",
            "quality_settings",
            "accessibility_features",
            "total_sessions",
            "active_sessions",
            "total_recordings",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_video_config(self, value):
        """Validate video config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Video config must be a dictionary.")
        return value

    def validate_audio_config(self, value):
        """Validate audio config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Audio config must be a dictionary.")
        return value

    def validate_recording_settings(self, value):
        """Validate recording settings."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Recording settings must be a dictionary."
            )
        return value

    def validate_quality_settings(self, value):
        """Validate quality settings."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Quality settings must be a dictionary.")
        return value

    def validate_accessibility_features(self, value):
        """Validate accessibility features."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Accessibility features must be a dictionary."
            )
        return value


class AIPoweredCommunicationSerializer(serializers.ModelSerializer):
    """Serializer for AI-Powered Communication."""

    class Meta:
        model = AIPoweredCommunication
        fields = [
            "id",
            "name",
            "ai_type",
            "transcription_config",
            "translation_config",
            "sentiment_analysis",
            "intent_recognition",
            "automated_responses",
            "total_transcriptions",
            "total_translations",
            "accuracy_score",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_transcription_config(self, value):
        """Validate transcription config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Transcription config must be a dictionary."
            )
        return value

    def validate_translation_config(self, value):
        """Validate translation config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Translation config must be a dictionary."
            )
        return value

    def validate_sentiment_analysis(self, value):
        """Validate sentiment analysis."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Sentiment analysis must be a dictionary."
            )
        return value

    def validate_intent_recognition(self, value):
        """Validate intent recognition."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Intent recognition must be a dictionary."
            )
        return value

    def validate_automated_responses(self, value):
        """Validate automated responses."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Automated responses must be a dictionary."
            )
        return value


class SocialMediaManagementSerializer(serializers.ModelSerializer):
    """Serializer for Social Media Management."""

    class Meta:
        model = SocialMediaManagement
        fields = [
            "id",
            "name",
            "platform",
            "account_config",
            "posting_schedule",
            "content_management",
            "engagement_analytics",
            "automation_rules",
            "total_posts",
            "total_engagement",
            "follower_growth",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_account_config(self, value):
        """Validate account config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Account config must be a dictionary.")
        return value

    def validate_posting_schedule(self, value):
        """Validate posting schedule."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Posting schedule must be a dictionary.")
        return value

    def validate_content_management(self, value):
        """Validate content management."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Content management must be a dictionary."
            )
        return value

    def validate_engagement_analytics(self, value):
        """Validate engagement analytics."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Engagement analytics must be a dictionary."
            )
        return value

    def validate_automation_rules(self, value):
        """Validate automation rules."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Automation rules must be a list.")
        return value


class CommunicationIntelligenceSerializer(serializers.ModelSerializer):
    """Serializer for Communication Intelligence."""

    class Meta:
        model = CommunicationIntelligence
        fields = [
            "id",
            "name",
            "intelligence_type",
            "analytics_config",
            "roi_measurement",
            "engagement_metrics",
            "content_analysis",
            "trend_analysis",
            "total_analyses",
            "insights_generated",
            "roi_score",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_analytics_config(self, value):
        """Validate analytics config."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Analytics config must be a dictionary.")
        return value

    def validate_roi_measurement(self, value):
        """Validate ROI measurement."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("ROI measurement must be a dictionary.")
        return value

    def validate_engagement_metrics(self, value):
        """Validate engagement metrics."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Engagement metrics must be a dictionary."
            )
        return value

    def validate_content_analysis(self, value):
        """Validate content analysis."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Content analysis must be a dictionary.")
        return value

    def validate_trend_analysis(self, value):
        """Validate trend analysis."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Trend analysis must be a dictionary.")
        return value


class CommunicationSessionSerializer(serializers.ModelSerializer):
    """Serializer for Communication Sessions."""

    class Meta:
        model = CommunicationSession
        fields = [
            "id",
            "session_id",
            "session_type",
            "status",
            "participants",
            "session_data",
            "start_time",
            "end_time",
            "duration",
            "quality_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_participants(self, value):
        """Validate participants."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Participants must be a list.")
        return value

    def validate_session_data(self, value):
        """Validate session data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Session data must be a dictionary.")
        return value


class CommunicationMessageSerializer(serializers.ModelSerializer):
    """Serializer for Communication Messages."""

    class Meta:
        model = CommunicationMessage
        fields = [
            "id",
            "session",
            "message_type",
            "content",
            "sender",
            "recipient",
            "message_data",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_message_data(self, value):
        """Validate message data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Message data must be a dictionary.")
        return value


class CommunicationAnalyticSerializer(serializers.ModelSerializer):
    """Serializer for Communication Analytics."""

    class Meta:
        model = CommunicationAnalytic
        fields = [
            "id",
            "analytic_name",
            "analytic_type",
            "metric_value",
            "metric_unit",
            "target_value",
            "analytic_data",
            "measurement_date",
        ]
        read_only_fields = ["id", "measurement_date"]

    def validate_analytic_data(self, value):
        """Validate analytic data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Analytic data must be a dictionary.")
        return value


class CommunicationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for Communication Templates."""

    class Meta:
        model = CommunicationTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "template_content",
            "template_variables",
            "template_category",
            "template_description",
            "total_uses",
            "is_public",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_template_variables(self, value):
        """Validate template variables."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Template variables must be a list.")
        return value
