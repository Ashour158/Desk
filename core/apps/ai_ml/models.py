"""
AI & Machine Learning models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class TicketCategorization(models.Model):
    """AI-powered ticket categorization."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    ticket = models.ForeignKey("tickets.Ticket", on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class SentimentAnalysis(models.Model):
    """Sentiment analysis for tickets and comments."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    content = models.TextField()
    sentiment = models.CharField(max_length=20)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class Chatbot(models.Model):
    """AI chatbot configuration."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class AIModel(models.Model):
    """AI model management."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AIProcessingJob(models.Model):
    """AI processing job tracking."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
