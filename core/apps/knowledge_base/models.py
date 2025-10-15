"""
Knowledge Base models for articles and documentation.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.organizations.managers import TenantAwareModel, TenantManager

User = get_user_model()


class KBCategory(TenantAwareModel):
    """
    Categories for knowledge base articles.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Category name")
    description = models.TextField(blank=True, help_text="Category description")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
        help_text="Parent category",
    )
    slug = models.SlugField(max_length=255, help_text="URL-friendly identifier")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or name")
    sort_order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)

    objects = TenantManager()

    class Meta:
        db_table = "kb_categories"
        verbose_name = "KB Category"
        verbose_name_plural = "KB Categories"
        ordering = ["sort_order", "name"]
        unique_together = ["organization", "slug"]

    def __str__(self):
        return self.name

    @property
    def full_path(self):
        """Get full category path."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class KBArticle(TenantAwareModel):
    """
    Knowledge base articles.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500, help_text="Article title")
    content = models.TextField(help_text="Article content (Markdown)")
    summary = models.TextField(blank=True, help_text="Article summary")

    # Categorization
    category = models.ForeignKey(
        KBCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    tags = models.JSONField(default=list, help_text="Article tags")

    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False, help_text="Featured article")
    is_public = models.BooleanField(default=True, help_text="Visible to customers")

    # Author and versioning
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="authored_articles"
    )
    version = models.PositiveIntegerField(default=1, help_text="Article version")
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="modified_articles",
    )

    # SEO
    seo_title = models.CharField(max_length=255, blank=True, help_text="SEO title")
    seo_description = models.TextField(blank=True, help_text="SEO description")
    seo_keywords = models.CharField(
        max_length=500, blank=True, help_text="SEO keywords"
    )

    # Analytics
    views_count = models.PositiveIntegerField(default=0, help_text="Number of views")
    helpful_count = models.PositiveIntegerField(default=0, help_text="Helpful votes")
    not_helpful_count = models.PositiveIntegerField(
        default=0, help_text="Not helpful votes"
    )

    # Timestamps
    published_at = models.DateTimeField(
        null=True, blank=True, help_text="Publication date"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "kb_articles"
        verbose_name = "KB Article"
        verbose_name_plural = "KB Articles"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "category"]),
            models.Index(fields=["organization", "is_featured"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Set published date when status changes to published."""
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_published(self):
        """Check if article is published."""
        return self.status == "published"

    @property
    def helpful_percentage(self):
        """Calculate helpful percentage."""
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes == 0:
            return 0
        return (self.helpful_count / total_votes) * 100

    @property
    def view_count_today(self):
        """Get view count for today."""
        from django.db.models import Count
        from django.utils import timezone

        today = timezone.now().date()
        return self.views.filter(created_at__date=today).count()


class KBArticleView(models.Model):
    """
    Track article views for analytics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(
        KBArticle, on_delete=models.CASCADE, related_name="views"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="article_views",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kb_article_views"
        verbose_name = "KB Article View"
        verbose_name_plural = "KB Article Views"
        ordering = ["-created_at"]

    def __str__(self):
        return f"View of {self.article.title}"


class KBFeedback(models.Model):
    """
    User feedback on knowledge base articles.
    """

    FEEDBACK_TYPES = [
        ("helpful", "Helpful"),
        ("not_helpful", "Not Helpful"),
        ("outdated", "Outdated"),
        ("incorrect", "Incorrect"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(
        KBArticle, on_delete=models.CASCADE, related_name="feedback"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kb_feedback",
    )
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    comment = models.TextField(blank=True, help_text="Additional feedback")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kb_feedback"
        verbose_name = "KB Feedback"
        verbose_name_plural = "KB Feedback"
        ordering = ["-created_at"]
        unique_together = ["article", "user", "feedback_type"]

    def __str__(self):
        return f"Feedback on {self.article.title}"


class KBSearch(models.Model):
    """
    Track search queries for analytics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    query = models.CharField(max_length=500, help_text="Search query")
    results_count = models.PositiveIntegerField(
        default=0, help_text="Number of results"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kb_searches",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kb_searches"
        verbose_name = "KB Search"
        verbose_name_plural = "KB Searches"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Search: {self.query}"
