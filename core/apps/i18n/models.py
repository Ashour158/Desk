"""
Internationalization models for helpdesk platform.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()


class Language(models.Model):
    """Supported languages."""

    code = models.CharField(max_length=10, unique=True)  # en, es, fr, de, etc.
    name = models.CharField(max_length=100)  # English, Spanish, French, etc.
    native_name = models.CharField(max_length=100)  # English, Español, Français, etc.
    is_rtl = models.BooleanField(default=False)  # Right-to-left languages
    is_active = models.BooleanField(default=True)

    # Language metadata
    country_code = models.CharField(max_length=2, blank=True)  # US, ES, FR, etc.
    currency_code = models.CharField(max_length=3, blank=True)  # USD, EUR, etc.
    date_format = models.CharField(max_length=20, default="%Y-%m-%d")
    time_format = models.CharField(max_length=20, default="%H:%M:%S")

    # Translation status
    translation_completeness = models.IntegerField(default=0)  # 0-100%
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Translation(models.Model):
    """Translation entries."""

    TRANSLATION_TYPES = [
        ("ui", "User Interface"),
        ("email", "Email Templates"),
        ("notification", "Notifications"),
        ("kb", "Knowledge Base"),
        ("ticket", "Ticket Content"),
        ("system", "System Messages"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    translation_type = models.CharField(max_length=20, choices=TRANSLATION_TYPES)

    # Translation content
    key = models.CharField(max_length=255)  # Translation key
    original_text = models.TextField()  # Original text in source language
    translated_text = models.TextField()  # Translated text
    context = models.TextField(blank=True)  # Translation context

    # Status
    is_approved = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.0)  # 0.0-1.0

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_translations",
    )

    class Meta:
        unique_together = ["organization", "language", "key"]
        ordering = ["key"]
        indexes = [
            models.Index(fields=["organization", "language"]),
            models.Index(fields=["translation_type", "is_approved"]),
        ]

    def __str__(self):
        return f"{self.key} - {self.language.name}"


class LocalizationSettings(models.Model):
    """Organization localization settings."""

    organization = models.OneToOneField(
        "organizations.Organization", on_delete=models.CASCADE
    )

    # Default language
    default_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="default_organizations"
    )

    # Supported languages
    supported_languages = models.ManyToManyField(
        Language, related_name="supported_organizations"
    )

    # Auto-translation settings
    auto_translate_enabled = models.BooleanField(default=True)
    auto_translate_provider = models.CharField(
        max_length=50, default="google"
    )  # google, azure, aws
    auto_translate_confidence_threshold = models.FloatField(default=0.8)

    # Translation workflow
    require_approval = models.BooleanField(default=True)
    allow_community_translations = models.BooleanField(default=False)

    # RTL support
    rtl_support_enabled = models.BooleanField(default=True)

    # Date/time formatting
    date_format = models.CharField(max_length=20, default="%Y-%m-%d")
    time_format = models.CharField(max_length=20, default="%H:%M:%S")
    timezone = models.CharField(max_length=50, default="UTC")

    # Currency and number formatting
    currency_code = models.CharField(max_length=3, default="USD")
    number_format = models.CharField(max_length=20, default="en_US")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization.name} - Localization Settings"


class TranslationRequest(models.Model):
    """Translation requests from users."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # Request details
    content_type = models.CharField(max_length=50)  # ticket, kb_article, etc.
    content_id = models.UUIDField()
    original_text = models.TextField()
    context = models.TextField(blank=True)
    priority = models.CharField(max_length=20, default="normal")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    translated_text = models.TextField(blank=True)
    translator_notes = models.TextField(blank=True)

    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_translations",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Translation Request - {self.language.name}"


class ContentTranslation(models.Model):
    """Translated content for specific entities."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    # Content reference
    content_type = models.CharField(max_length=50)  # ticket, kb_article, etc.
    content_id = models.UUIDField()
    field_name = models.CharField(max_length=100)  # subject, description, etc.

    # Translation
    original_text = models.TextField()
    translated_text = models.TextField()

    # Status
    is_approved = models.BooleanField(default=False)
    is_auto_translated = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = [
            "organization",
            "language",
            "content_type",
            "content_id",
            "field_name",
        ]
        indexes = [
            models.Index(fields=["content_type", "content_id"]),
            models.Index(fields=["language", "is_approved"]),
        ]

    def __str__(self):
        return f"{self.content_type}:{self.content_id} - {self.field_name} ({self.language.name})"


class TranslationMemory(models.Model):
    """Translation memory for consistency."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    source_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="source_memories"
    )
    target_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="target_memories"
    )

    # Translation pair
    source_text = models.TextField()
    target_text = models.TextField()

    # Quality metrics
    match_score = models.FloatField(default=1.0)
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = [
            "organization",
            "source_language",
            "target_language",
            "source_text",
        ]
        ordering = ["-usage_count", "-match_score"]

    def __str__(self):
        return f"{self.source_language.code} -> {self.target_language.code}: {self.source_text[:50]}"


class LanguagePreference(models.Model):
    """User language preferences."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_language = models.ForeignKey(Language, on_delete=models.CASCADE)

    # UI preferences
    ui_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="ui_users"
    )
    email_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="email_users"
    )
    notification_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="notification_users"
    )

    # Auto-translation preferences
    auto_translate_enabled = models.BooleanField(default=True)
    auto_translate_confidence_threshold = models.FloatField(default=0.8)

    # RTL preferences
    rtl_enabled = models.BooleanField(default=False)

    # Date/time preferences
    date_format = models.CharField(max_length=20, blank=True)
    time_format = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.preferred_language.name}"
