"""
Communication platform models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class VideoConference(models.Model):
    """Video conferencing and meetings."""

    CONFERENCE_TYPES = [
        ("support_call", "Support Call"),
        ("team_meeting", "Team Meeting"),
        ("customer_meeting", "Customer Meeting"),
        ("training_session", "Training Session"),
        ("webinar", "Webinar"),
        ("interview", "Interview"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    conference_type = models.CharField(max_length=50, choices=CONFERENCE_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Conference details
    meeting_id = models.CharField(max_length=255, unique=True)
    meeting_url = models.URLField()
    password = models.CharField(max_length=100, blank=True)

    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=0)

    # Participants
    host = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="hosted_conferences"
    )
    participants = models.ManyToManyField(
        User, blank=True, related_name="participated_conferences"
    )
    max_participants = models.IntegerField(default=100)

    # Features
    recording_enabled = models.BooleanField(default=False)
    screen_sharing_enabled = models.BooleanField(default=True)
    chat_enabled = models.BooleanField(default=True)
    breakout_rooms_enabled = models.BooleanField(default=False)

    # Status
    status = models.CharField(max_length=20, default="scheduled")
    is_active = models.BooleanField(default=True)
    is_recorded = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-scheduled_start"]

    def __str__(self):
        return f"{self.organization.name} - {self.title}"


class VoiceAI(models.Model):
    """Voice AI and speech processing."""

    AI_TYPES = [
        ("speech_to_text", "Speech to Text"),
        ("text_to_speech", "Text to Speech"),
        ("voice_commands", "Voice Commands"),
        ("voice_biometrics", "Voice Biometrics"),
        ("sentiment_analysis", "Sentiment Analysis"),
        ("language_detection", "Language Detection"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    ai_type = models.CharField(max_length=50, choices=AI_TYPES)
    description = models.TextField(blank=True)

    # AI configuration
    model_name = models.CharField(max_length=255)
    model_version = models.CharField(max_length=50)
    language = models.CharField(max_length=10, default="en")
    accent = models.CharField(max_length=50, blank=True)

    # Performance
    accuracy = models.FloatField(default=0.0)
    response_time = models.FloatField(default=0.0)
    confidence_threshold = models.FloatField(default=0.8)

    # Usage
    request_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_trained = models.BooleanField(default=False)
    last_used = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class SocialMediaIntegration(models.Model):
    """Social media monitoring and integration."""

    PLATFORMS = [
        ("twitter", "Twitter"),
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("linkedin", "LinkedIn"),
        ("youtube", "YouTube"),
        ("tiktok", "TikTok"),
        ("reddit", "Reddit"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    platform = models.CharField(max_length=50, choices=PLATFORMS)
    account_name = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255)

    # Integration details
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires = models.DateTimeField(blank=True, null=True)

    # Monitoring
    keywords = models.JSONField(default=list)
    hashtags = models.JSONField(default=list)
    mentions_enabled = models.BooleanField(default=True)
    direct_messages_enabled = models.BooleanField(default=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_connected = models.BooleanField(default=False)
    last_sync = models.DateTimeField(blank=True, null=True)

    # Statistics
    posts_count = models.IntegerField(default=0)
    mentions_count = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["platform", "account_name"]
        unique_together = ["organization", "platform", "account_id"]

    def __str__(self):
        return f"{self.organization.name} - {self.platform}: {self.account_name}"


class CommunicationAnalytics(models.Model):
    """Communication analytics and metrics."""

    METRIC_TYPES = [
        ("response_time", "Response Time"),
        ("resolution_time", "Resolution Time"),
        ("satisfaction_score", "Satisfaction Score"),
        ("engagement_rate", "Engagement Rate"),
        ("conversion_rate", "Conversion Rate"),
        ("sentiment_score", "Sentiment Score"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    channel = models.CharField(max_length=50)

    # Metrics
    value = models.FloatField()
    target_value = models.FloatField(blank=True, null=True)
    previous_value = models.FloatField(blank=True, null=True)
    change_percentage = models.FloatField(default=0.0)

    # Context
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    sample_size = models.IntegerField(default=0)

    # Analysis
    trend = models.CharField(max_length=20, blank=True)  # up, down, stable
    benchmark = models.FloatField(blank=True, null=True)
    percentile_rank = models.FloatField(blank=True, null=True)

    # Status
    is_anomaly = models.BooleanField(default=False)
    requires_attention = models.BooleanField(default=False)

    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-calculated_at"]
        indexes = [
            models.Index(fields=["organization", "metric_type"]),
            models.Index(fields=["channel", "calculated_at"]),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.metric_type}: {self.value}"


class MultiLanguageSupport(models.Model):
    """Multi-language support and translation."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    language_code = models.CharField(max_length=10)
    language_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # Translation settings
    auto_translate = models.BooleanField(default=False)
    translation_service = models.CharField(max_length=50, default="google")
    translation_confidence = models.FloatField(default=0.8)

    # Content
    translated_content = models.JSONField(default=dict)
    translation_status = models.JSONField(default=dict)

    # Statistics
    translation_count = models.IntegerField(default=0)
    accuracy_score = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["language_name"]
        unique_together = ["organization", "language_code"]

    def __str__(self):
        return f"{self.organization.name} - {self.language_name}"


class AccessibilityFeature(models.Model):
    """Accessibility features and support."""

    FEATURE_TYPES = [
        ("screen_reader", "Screen Reader"),
        ("voice_control", "Voice Control"),
        ("keyboard_navigation", "Keyboard Navigation"),
        ("high_contrast", "High Contrast"),
        ("large_text", "Large Text"),
        ("color_blind_support", "Color Blind Support"),
        ("sign_language", "Sign Language"),
        ("braille_support", "Braille Support"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    feature_type = models.CharField(max_length=50, choices=FEATURE_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Feature configuration
    is_enabled = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict)
    compatibility = models.JSONField(default=list)

    # Usage
    usage_count = models.IntegerField(default=0)
    user_satisfaction = models.FloatField(default=0.0)
    feedback_count = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_beta = models.BooleanField(default=False)
    last_updated = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["feature_type", "name"]
        unique_together = ["organization", "feature_type", "name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class CommunicationTemplate(models.Model):
    """Communication templates and templates."""

    TEMPLATE_TYPES = [
        ("email", "Email Template"),
        ("sms", "SMS Template"),
        ("chat", "Chat Template"),
        ("phone", "Phone Script"),
        ("social_media", "Social Media Post"),
        ("notification", "Notification Template"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Template content
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    variables = models.JSONField(default=list)

    # Personalization
    personalization_enabled = models.BooleanField(default=True)
    personalization_fields = models.JSONField(default=list)

    # Usage
    usage_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)

    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["template_type", "name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class CommunicationChannel(models.Model):
    """Communication channels and preferences."""

    CHANNEL_TYPES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("phone", "Phone"),
        ("chat", "Chat"),
        ("social_media", "Social Media"),
        ("push_notification", "Push Notification"),
        ("in_app", "In-App Notification"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="communication_channels"
    )
    channel_type = models.CharField(max_length=50, choices=CHANNEL_TYPES)

    # Channel details
    address = models.CharField(max_length=255)  # email, phone number, etc.
    is_verified = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)

    # Preferences
    is_enabled = models.BooleanField(default=True)
    notification_types = models.JSONField(default=list)
    quiet_hours_start = models.TimeField(blank=True, null=True)
    quiet_hours_end = models.TimeField(blank=True, null=True)
    timezone = models.CharField(max_length=50, default="UTC")

    # Usage
    message_count = models.IntegerField(default=0)
    delivery_rate = models.FloatField(default=0.0)
    response_rate = models.FloatField(default=0.0)

    # Status
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(blank=True, null=True)
    last_verified = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user", "channel_type"]
        unique_together = ["organization", "user", "channel_type", "address"]

    def __str__(self):
        return f"{self.user.full_name} - {self.channel_type}: {self.address}"


class CommunicationLog(models.Model):
    """Communication logs and history."""

    LOG_TYPES = [
        ("sent", "Sent"),
        ("received", "Received"),
        ("delivered", "Delivered"),
        ("read", "Read"),
        ("failed", "Failed"),
        ("bounced", "Bounced"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    channel_type = models.CharField(max_length=50)

    # Communication details
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_communications",
        null=True,
        blank=True,
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_communications",
        null=True,
        blank=True,
    )
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField()

    # Context
    related_entity_type = models.CharField(max_length=50, blank=True)
    related_entity_id = models.UUIDField(blank=True, null=True)
    template_used = models.ForeignKey(
        CommunicationTemplate, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Delivery
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    delivery_status = models.CharField(max_length=50, default="pending")

    # Response
    response_received = models.BooleanField(default=False)
    response_time_minutes = models.FloatField(blank=True, null=True)
    satisfaction_rating = models.IntegerField(blank=True, null=True)

    # Metadata
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["organization", "log_type"]),
            models.Index(fields=["channel_type", "sent_at"]),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.log_type}: {self.subject}"
