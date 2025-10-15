"""
Enhanced AI & Machine Learning models for advanced capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.organizations.models import Organization
from apps.common.base_models import BaseModel, ConfigurationModel, MetricsModel, AIModel
from apps.common.constants import (
    SHORT_FIELD_LENGTH,
    MEDIUM_FIELD_LENGTH,
    LONG_FIELD_LENGTH,
    VERY_LONG_FIELD_LENGTH,
)
import uuid

User = get_user_model()


class NLPEngine(models.Model):
    """Natural Language Processing Engine for advanced text analysis."""

    ENGINE_TYPES = [
        ("intent_recognition", "Intent Recognition"),
        ("entity_extraction", "Entity Extraction"),
        ("sentiment_analysis", "Sentiment Analysis"),
        ("language_translation", "Language Translation"),
        ("text_summarization", "Text Summarization"),
        ("key_phrase_extraction", "Key Phrase Extraction"),
        ("named_entity_recognition", "Named Entity Recognition"),
        ("text_classification", "Text Classification"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="nlp_engines"
    )
    name = models.CharField(max_length=255)
    engine_type = models.CharField(max_length=50, choices=ENGINE_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    model_name = models.CharField(
        max_length=255, default="bert-base-multilingual-cased"
    )
    language_codes = models.JSONField(default=list)  # Supported languages
    confidence_threshold = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=512)

    # Performance metrics
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)

    # Status
    is_active = models.BooleanField(default=True)
    is_training = models.BooleanField(default=False)
    last_trained = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "engine_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.engine_type})"


class ComputerVisionSuite(models.Model):
    """Computer Vision capabilities for image and video analysis."""

    VISION_TYPES = [
        ("document_ocr", "Document OCR"),
        ("barcode_scanning", "Barcode/QR Code Scanning"),
        ("face_recognition", "Face Recognition"),
        ("object_detection", "Object Detection"),
        ("video_analysis", "Video Analysis"),
        ("image_classification", "Image Classification"),
        ("text_extraction", "Text Extraction"),
        ("quality_assessment", "Quality Assessment"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="vision_suites"
    )
    name = models.CharField(max_length=255)
    vision_type = models.CharField(max_length=50, choices=VISION_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    model_path = models.CharField(max_length=500)
    input_formats = models.JSONField(default=list)  # Supported image/video formats
    output_labels = models.JSONField(default=list)
    confidence_threshold = models.FloatField(default=0.8)

    # Processing settings
    max_image_size = models.CharField(max_length=20, default="1024x1024")
    batch_size = models.IntegerField(default=32)
    processing_timeout = models.IntegerField(default=30)  # seconds

    # Performance metrics
    accuracy = models.FloatField(default=0.0)
    processing_speed = models.FloatField(default=0.0)  # images per second
    memory_usage = models.FloatField(default=0.0)  # MB

    # Status
    is_active = models.BooleanField(default=True)
    is_processing = models.BooleanField(default=False)
    last_used = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "vision_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.vision_type})"


class PredictiveAnalyticsPlatform(models.Model):
    """Advanced predictive analytics for business intelligence."""

    ANALYTICS_TYPES = [
        ("revenue_forecasting", "Revenue Forecasting"),
        ("resource_optimization", "Resource Optimization"),
        ("risk_assessment", "Risk Assessment"),
        ("performance_prediction", "Performance Prediction"),
        ("market_trend_analysis", "Market Trend Analysis"),
        ("customer_lifetime_value", "Customer Lifetime Value"),
        ("churn_prediction", "Churn Prediction"),
        ("demand_forecasting", "Demand Forecasting"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="predictive_analytics"
    )
    name = models.CharField(max_length=255)
    analytics_type = models.CharField(max_length=50, choices=ANALYTICS_TYPES)
    description = models.TextField(blank=True)

    # Data sources
    data_sources = models.JSONField(default=list)
    feature_columns = models.JSONField(default=list)
    target_column = models.CharField(max_length=100)

    # Model configuration
    algorithm = models.CharField(max_length=100, default="random_forest")
    hyperparameters = models.JSONField(default=dict)
    training_data_size = models.IntegerField(default=0)
    test_data_size = models.IntegerField(default=0)

    # Performance metrics
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    mae = models.FloatField(default=0.0)  # Mean Absolute Error
    rmse = models.FloatField(default=0.0)  # Root Mean Square Error

    # Predictions
    last_prediction = models.DateTimeField(blank=True, null=True)
    prediction_frequency = models.CharField(max_length=50, default="daily")
    next_prediction = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_training = models.BooleanField(default=False)
    last_trained = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "analytics_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.analytics_type})"


class AdvancedChatbot(models.Model):
    """Advanced chatbot and virtual assistant with multi-language support."""

    CHATBOT_TYPES = [
        ("rule_based", "Rule-based"),
        ("ai_powered", "AI-powered"),
        ("hybrid", "Hybrid"),
        ("voice_assistant", "Voice Assistant"),
        ("conversational_ai", "Conversational AI"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="chatbots"
    )
    name = models.CharField(max_length=255)
    chatbot_type = models.CharField(max_length=50, choices=CHATBOT_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    language_codes = models.JSONField(default=["en"])  # Supported languages
    model_name = models.CharField(max_length=255, default="gpt-4")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=1000)
    context_window = models.IntegerField(
        default=10
    )  # Number of previous messages to consider

    # Capabilities
    capabilities = models.JSONField(default=list)  # Available features
    knowledge_base_ids = models.JSONField(default=list)  # Connected KB articles
    integration_apis = models.JSONField(default=list)  # Connected APIs

    # Performance metrics
    response_accuracy = models.FloatField(default=0.0)
    user_satisfaction = models.FloatField(default=0.0)
    resolution_rate = models.FloatField(default=0.0)
    escalation_rate = models.FloatField(default=0.0)

    # Usage statistics
    total_conversations = models.IntegerField(default=0)
    successful_resolutions = models.IntegerField(default=0)
    escalations_to_human = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)  # seconds

    # Status
    is_active = models.BooleanField(default=True)
    is_training = models.BooleanField(default=False)
    last_trained = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class AIPoweredAutomation(models.Model):
    """AI-powered automation with intelligent process automation."""

    AUTOMATION_TYPES = [
        ("intelligent_process_automation", "Intelligent Process Automation"),
        ("smart_document_processing", "Smart Document Processing"),
        ("automated_decision_making", "Automated Decision Making"),
        ("predictive_maintenance", "Predictive Maintenance"),
        ("self_healing_systems", "Self-healing Systems"),
        ("cognitive_automation", "Cognitive Automation"),
        ("robotic_process_automation", "Robotic Process Automation"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="ai_automations"
    )
    name = models.CharField(max_length=255)
    automation_type = models.CharField(max_length=50, choices=AUTOMATION_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    trigger_conditions = models.JSONField(default=list)
    automation_rules = models.JSONField(default=list)
    ai_models = models.JSONField(default=list)  # Connected AI models
    data_sources = models.JSONField(default=list)

    # Execution settings
    execution_frequency = models.CharField(max_length=50, default="on_trigger")
    max_execution_time = models.IntegerField(default=300)  # seconds
    retry_attempts = models.IntegerField(default=3)
    timeout_handling = models.CharField(max_length=50, default="fail")

    # Performance metrics
    success_rate = models.FloatField(default=0.0)
    average_execution_time = models.FloatField(default=0.0)
    cost_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    efficiency_improvement = models.FloatField(default=0.0)

    # Execution statistics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)
    last_execution = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_running = models.BooleanField(default=False)
    last_trained = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("organization", "name", "automation_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name} ({self.automation_type})"


class AIProcessingJob(models.Model):
    """Track AI processing jobs and their results."""

    JOB_TYPES = [
        ("nlp_processing", "NLP Processing"),
        ("vision_processing", "Vision Processing"),
        ("prediction", "Prediction"),
        ("chatbot_response", "Chatbot Response"),
        ("automation_execution", "Automation Execution"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="ai_jobs"
    )
    job_type = models.CharField(max_length=50, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Input data
    input_data = models.JSONField(default=dict)
    input_files = models.JSONField(default=list)  # File URLs

    # Processing details
    ai_model_id = models.CharField(max_length=255, blank=True)
    processing_started = models.DateTimeField(blank=True, null=True)
    processing_completed = models.DateTimeField(blank=True, null=True)
    processing_duration = models.FloatField(default=0.0)  # seconds

    # Results
    output_data = models.JSONField(default=dict)
    output_files = models.JSONField(default=list)  # Generated files
    confidence_score = models.FloatField(default=0.0)
    error_message = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.job_type} ({self.status})"


class AIModelPerformance(models.Model):
    """Track AI model performance metrics over time."""

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="ai_performance"
    )
    model_name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=100)

    # Performance metrics
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    processing_time = models.FloatField()  # seconds
    memory_usage = models.FloatField()  # MB

    # Usage statistics
    total_predictions = models.IntegerField()
    successful_predictions = models.IntegerField()
    failed_predictions = models.IntegerField()

    # Timestamp
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.organization.name} - {self.model_name} ({self.recorded_at})"
