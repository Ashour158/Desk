"""
Enhanced Advanced Communication Platform models for advanced capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class UnifiedCommunicationHub(models.Model):
    """Unified Communication Hub with multi-channel communication and real-time collaboration."""

    HUB_TYPE_CHOICES = [
        ("multi_channel", "Multi-Channel"),
        ("real_time_collaboration", "Real-time Collaboration"),
        ("unified_messaging", "Unified Messaging"),
        ("presence_management", "Presence Management"),
        ("contact_center", "Contact Center"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    hub_type = models.CharField(max_length=50, choices=HUB_TYPE_CHOICES)
    communication_channels = models.JSONField(default=list)
    collaboration_features = models.JSONField(default=dict)
    presence_management = models.JSONField(default=dict)
    contact_center_config = models.JSONField(default=dict)
    integration_settings = models.JSONField(default=dict)
    total_users = models.PositiveIntegerField(default=0)
    active_sessions = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Unified Communication Hub"
        verbose_name_plural = "Unified Communication Hubs"

    def __str__(self):
        return self.name


class VideoAudioFeatures(models.Model):
    """Advanced Video & Audio Features with HD video conferencing and noise cancellation."""

    FEATURE_TYPE_CHOICES = [
        ("hd_video_conferencing", "HD Video Conferencing"),
        ("noise_cancellation", "Noise Cancellation"),
        ("audio_enhancement", "Audio Enhancement"),
        ("screen_sharing", "Screen Sharing"),
        ("recording_capabilities", "Recording Capabilities"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    feature_type = models.CharField(max_length=50, choices=FEATURE_TYPE_CHOICES)
    video_config = models.JSONField(default=dict)
    audio_config = models.JSONField(default=dict)
    recording_settings = models.JSONField(default=dict)
    quality_settings = models.JSONField(default=dict)
    accessibility_features = models.JSONField(default=dict)
    total_sessions = models.PositiveIntegerField(default=0)
    active_sessions = models.PositiveIntegerField(default=0)
    total_recordings = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Video & Audio Feature"
        verbose_name_plural = "Video & Audio Features"

    def __str__(self):
        return self.name


class AIPoweredCommunication(models.Model):
    """AI-Powered Communication with smart transcription and real-time translation."""

    AI_TYPE_CHOICES = [
        ("smart_transcription", "Smart Transcription"),
        ("real_time_translation", "Real-time Translation"),
        ("sentiment_analysis", "Sentiment Analysis"),
        ("intent_recognition", "Intent Recognition"),
        ("automated_responses", "Automated Responses"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    ai_type = models.CharField(max_length=50, choices=AI_TYPE_CHOICES)
    transcription_config = models.JSONField(default=dict)
    translation_config = models.JSONField(default=dict)
    sentiment_analysis = models.JSONField(default=dict)
    intent_recognition = models.JSONField(default=dict)
    automated_responses = models.JSONField(default=dict)
    total_transcriptions = models.PositiveIntegerField(default=0)
    total_translations = models.PositiveIntegerField(default=0)
    accuracy_score = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI-Powered Communication"
        verbose_name_plural = "AI-Powered Communications"

    def __str__(self):
        return self.name


class SocialMediaManagement(models.Model):
    """Social Media Management with multi-platform posting and engagement analytics."""

    PLATFORM_CHOICES = [
        ("facebook", "Facebook"),
        ("twitter", "Twitter"),
        ("linkedin", "LinkedIn"),
        ("instagram", "Instagram"),
        ("youtube", "YouTube"),
        ("tiktok", "TikTok"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    account_config = models.JSONField(default=dict)
    posting_schedule = models.JSONField(default=dict)
    content_management = models.JSONField(default=dict)
    engagement_analytics = models.JSONField(default=dict)
    automation_rules = models.JSONField(default=list)
    total_posts = models.PositiveIntegerField(default=0)
    total_engagement = models.PositiveIntegerField(default=0)
    follower_growth = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Social Media Management"
        verbose_name_plural = "Social Media Managements"

    def __str__(self):
        return self.name


class CommunicationIntelligence(models.Model):
    """Communication Intelligence with communication analytics and ROI measurement."""

    INTELLIGENCE_TYPE_CHOICES = [
        ("communication_analytics", "Communication Analytics"),
        ("roi_measurement", "ROI Measurement"),
        ("engagement_metrics", "Engagement Metrics"),
        ("content_analysis", "Content Analysis"),
        ("trend_analysis", "Trend Analysis"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    intelligence_type = models.CharField(
        max_length=50, choices=INTELLIGENCE_TYPE_CHOICES
    )
    analytics_config = models.JSONField(default=dict)
    roi_measurement = models.JSONField(default=dict)
    engagement_metrics = models.JSONField(default=dict)
    content_analysis = models.JSONField(default=dict)
    trend_analysis = models.JSONField(default=dict)
    total_analyses = models.PositiveIntegerField(default=0)
    insights_generated = models.PositiveIntegerField(default=0)
    roi_score = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Communication Intelligence"
        verbose_name_plural = "Communication Intelligences"

    def __str__(self):
        return self.name


class CommunicationSession(models.Model):
    """Communication Session for tracking communication activities."""

    SESSION_TYPE_CHOICES = [
        ("video_call", "Video Call"),
        ("audio_call", "Audio Call"),
        ("chat", "Chat"),
        ("email", "Email"),
        ("social_media", "Social Media"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    session_type = models.CharField(max_length=50, choices=SESSION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    participants = models.JSONField(default=list)
    session_data = models.JSONField(default=dict)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    quality_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Communication Session"
        verbose_name_plural = "Communication Sessions"

    def __str__(self):
        return f"{self.session_id} - {self.session_type}"


class CommunicationMessage(models.Model):
    """Communication Message for storing communication content."""

    MESSAGE_TYPE_CHOICES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("file", "File"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    session = models.ForeignKey(CommunicationSession, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    sender = models.CharField(max_length=200)
    recipient = models.CharField(max_length=200)
    message_data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Communication Message"
        verbose_name_plural = "Communication Messages"

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.content[:50]}"


class CommunicationAnalytic(models.Model):
    """Communication Analytic for tracking communication performance."""

    ANALYTIC_TYPE_CHOICES = [
        ("engagement", "Engagement"),
        ("reach", "Reach"),
        ("sentiment", "Sentiment"),
        ("response_time", "Response Time"),
        ("satisfaction", "Satisfaction"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    analytic_name = models.CharField(max_length=200)
    analytic_type = models.CharField(max_length=50, choices=ANALYTIC_TYPE_CHOICES)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=50)
    target_value = models.FloatField(null=True, blank=True)
    analytic_data = models.JSONField(default=dict)
    measurement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Communication Analytic"
        verbose_name_plural = "Communication Analytics"

    def __str__(self):
        return f"{self.analytic_name}: {self.metric_value} {self.metric_unit}"


class CommunicationTemplate(models.Model):
    """Communication Template for reusable communication content."""

    TEMPLATE_TYPE_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("social_media", "Social Media"),
        ("chat", "Chat"),
        ("announcement", "Announcement"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    template_content = models.TextField()
    template_variables = models.JSONField(default=list)
    template_category = models.CharField(max_length=100)
    template_description = models.TextField()
    total_uses = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Communication Template"
        verbose_name_plural = "Communication Templates"

    def __str__(self):
        return self.name
