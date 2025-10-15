"""
Enhanced AI & Machine Learning serializers for advanced capabilities.
"""

from rest_framework import serializers
from .enhanced_models import (
    NLPEngine,
    ComputerVisionSuite,
    PredictiveAnalyticsPlatform,
    AdvancedChatbot,
    AIPoweredAutomation,
    AIProcessingJob,
    AIModelPerformance,
)


class NLPEngineSerializer(serializers.ModelSerializer):
    """Serializer for NLP Engine."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = NLPEngine
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_language_codes(self, value):
        """Validate language codes."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Language codes must be a list.")

        valid_codes = [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ru",
            "zh",
            "ja",
            "ko",
            "ar",
            "hi",
        ]
        for code in value:
            if code not in valid_codes:
                raise serializers.ValidationError(f"Invalid language code: {code}")

        return value

    def validate_confidence_threshold(self, value):
        """Validate confidence threshold."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Confidence threshold must be between 0 and 1."
            )
        return value


class ComputerVisionSuiteSerializer(serializers.ModelSerializer):
    """Serializer for Computer Vision Suite."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = ComputerVisionSuite
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_input_formats(self, value):
        """Validate input formats."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Input formats must be a list.")

        valid_formats = [
            "jpg",
            "jpeg",
            "png",
            "gif",
            "bmp",
            "tiff",
            "webp",
            "mp4",
            "avi",
            "mov",
        ]
        for format in value:
            if format.lower() not in valid_formats:
                raise serializers.ValidationError(f"Invalid input format: {format}")

        return value

    def validate_confidence_threshold(self, value):
        """Validate confidence threshold."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Confidence threshold must be between 0 and 1."
            )
        return value


class PredictiveAnalyticsPlatformSerializer(serializers.ModelSerializer):
    """Serializer for Predictive Analytics Platform."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = PredictiveAnalyticsPlatform
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_algorithm(self, value):
        """Validate algorithm."""
        valid_algorithms = [
            "random_forest",
            "gradient_boosting",
            "neural_network",
            "svm",
            "linear_regression",
            "logistic_regression",
            "decision_tree",
            "kmeans",
            "dbscan",
            "lstm",
            "transformer",
        ]

        if value not in valid_algorithms:
            raise serializers.ValidationError(f"Invalid algorithm: {value}")

        return value

    def validate_accuracy(self, value):
        """Validate accuracy."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Accuracy must be between 0 and 1.")
        return value


class AdvancedChatbotSerializer(serializers.ModelSerializer):
    """Serializer for Advanced Chatbot."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AdvancedChatbot
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_language_codes(self, value):
        """Validate language codes."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Language codes must be a list.")

        valid_codes = [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ru",
            "zh",
            "ja",
            "ko",
            "ar",
            "hi",
        ]
        for code in value:
            if code not in valid_codes:
                raise serializers.ValidationError(f"Invalid language code: {code}")

        return value

    def validate_temperature(self, value):
        """Validate temperature."""
        if not 0 <= value <= 2:
            raise serializers.ValidationError("Temperature must be between 0 and 2.")
        return value

    def validate_max_tokens(self, value):
        """Validate max tokens."""
        if value <= 0:
            raise serializers.ValidationError("Max tokens must be greater than 0.")
        return value


class AIPoweredAutomationSerializer(serializers.ModelSerializer):
    """Serializer for AI-Powered Automation."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AIPoweredAutomation
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "updated_at", "created_by")

    def validate_execution_frequency(self, value):
        """Validate execution frequency."""
        valid_frequencies = [
            "on_trigger",
            "hourly",
            "daily",
            "weekly",
            "monthly",
            "cron",
            "continuous",
            "batch",
        ]

        if value not in valid_frequencies:
            raise serializers.ValidationError(f"Invalid execution frequency: {value}")

        return value

    def validate_max_execution_time(self, value):
        """Validate max execution time."""
        if value <= 0:
            raise serializers.ValidationError(
                "Max execution time must be greater than 0."
            )
        return value

    def validate_retry_attempts(self, value):
        """Validate retry attempts."""
        if value < 0:
            raise serializers.ValidationError("Retry attempts must be non-negative.")
        return value


class AIProcessingJobSerializer(serializers.ModelSerializer):
    """Serializer for AI Processing Job."""

    created_by_name = serializers.ReadOnlyField(source="created_by.full_name")

    class Meta:
        model = AIProcessingJob
        fields = "__all__"
        read_only_fields = ("organization", "created_at", "created_by")

    def validate_confidence_score(self, value):
        """Validate confidence score."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "Confidence score must be between 0 and 1."
            )
        return value


class AIModelPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for AI Model Performance."""

    class Meta:
        model = AIModelPerformance
        fields = "__all__"
        read_only_fields = ("organization", "recorded_at")

    def validate_accuracy(self, value):
        """Validate accuracy."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Accuracy must be between 0 and 1.")
        return value

    def validate_precision(self, value):
        """Validate precision."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Precision must be between 0 and 1.")
        return value

    def validate_recall(self, value):
        """Validate recall."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Recall must be between 0 and 1.")
        return value

    def validate_f1_score(self, value):
        """Validate F1 score."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError("F1 score must be between 0 and 1.")
        return value


class NLPProcessingRequestSerializer(serializers.Serializer):
    """Serializer for NLP processing requests."""

    text = serializers.CharField(max_length=10000)
    language = serializers.CharField(max_length=10, default="en")
    options = serializers.JSONField(default=dict, required=False)

    def validate_text(self, value):
        """Validate text."""
        if not value.strip():
            raise serializers.ValidationError("Text cannot be empty.")
        return value


class VisionProcessingRequestSerializer(serializers.Serializer):
    """Serializer for vision processing requests."""

    image_url = serializers.URLField()
    options = serializers.JSONField(default=dict, required=False)

    def validate_image_url(self, value):
        """Validate image URL."""
        if not value:
            raise serializers.ValidationError("Image URL is required.")
        return value


class PredictionRequestSerializer(serializers.Serializer):
    """Serializer for prediction requests."""

    input_data = serializers.JSONField()
    options = serializers.JSONField(default=dict, required=False)

    def validate_input_data(self, value):
        """Validate input data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Input data must be a dictionary.")
        return value


class ChatbotRequestSerializer(serializers.Serializer):
    """Serializer for chatbot requests."""

    message = serializers.CharField(max_length=1000)
    context = serializers.ListField(
        child=serializers.DictField(), default=list, required=False
    )
    options = serializers.JSONField(default=dict, required=False)

    def validate_message(self, value):
        """Validate message."""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value


class AutomationRequestSerializer(serializers.Serializer):
    """Serializer for automation requests."""

    trigger_data = serializers.JSONField()
    options = serializers.JSONField(default=dict, required=False)

    def validate_trigger_data(self, value):
        """Validate trigger data."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Trigger data must be a dictionary.")
        return value


class BatchProcessingRequestSerializer(serializers.Serializer):
    """Serializer for batch processing requests."""

    items = serializers.ListField(
        child=serializers.DictField(), min_length=1, max_length=100
    )
    options = serializers.JSONField(default=dict, required=False)

    def validate_items(self, value):
        """Validate items."""
        if not value:
            raise serializers.ValidationError("Items list cannot be empty.")
        return value


class TrainingRequestSerializer(serializers.Serializer):
    """Serializer for training requests."""

    training_data = serializers.ListField(child=serializers.DictField(), min_length=1)
    validation_data = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    hyperparameters = serializers.JSONField(default=dict, required=False)

    def validate_training_data(self, value):
        """Validate training data."""
        if not value:
            raise serializers.ValidationError("Training data cannot be empty.")
        return value


class PerformanceMetricsSerializer(serializers.Serializer):
    """Serializer for performance metrics."""

    accuracy = serializers.FloatField(min_value=0, max_value=1)
    precision = serializers.FloatField(min_value=0, max_value=1)
    recall = serializers.FloatField(min_value=0, max_value=1)
    f1_score = serializers.FloatField(min_value=0, max_value=1)
    processing_time = serializers.FloatField(min_value=0)
    memory_usage = serializers.FloatField(min_value=0)
    total_predictions = serializers.IntegerField(min_value=0)
    successful_predictions = serializers.IntegerField(min_value=0)
    failed_predictions = serializers.IntegerField(min_value=0)

    def validate(self, data):
        """Validate performance metrics."""
        if (
            data["successful_predictions"] + data["failed_predictions"]
            != data["total_predictions"]
        ):
            raise serializers.ValidationError(
                "Successful predictions + failed predictions must equal total predictions."
            )
        return data


class ModelConfigurationSerializer(serializers.Serializer):
    """Serializer for model configuration."""

    model_name = serializers.CharField(max_length=255)
    model_type = serializers.CharField(max_length=100)
    hyperparameters = serializers.JSONField(default=dict)
    training_config = serializers.JSONField(default=dict)
    inference_config = serializers.JSONField(default=dict)

    def validate_model_name(self, value):
        """Validate model name."""
        if not value.strip():
            raise serializers.ValidationError("Model name cannot be empty.")
        return value


class DeploymentRequestSerializer(serializers.Serializer):
    """Serializer for deployment requests."""

    model_id = serializers.UUIDField()
    environment = serializers.ChoiceField(
        choices=["development", "staging", "production"]
    )
    scaling_config = serializers.JSONField(default=dict)
    monitoring_config = serializers.JSONField(default=dict)

    def validate_environment(self, value):
        """Validate environment."""
        if value not in ["development", "staging", "production"]:
            raise serializers.ValidationError("Invalid environment.")
        return value


class ModelEvaluationSerializer(serializers.Serializer):
    """Serializer for model evaluation."""

    model_id = serializers.UUIDField()
    test_data = serializers.ListField(child=serializers.DictField(), min_length=1)
    evaluation_metrics = serializers.ListField(
        child=serializers.CharField(),
        default=["accuracy", "precision", "recall", "f1_score"],
    )
    cross_validation = serializers.BooleanField(default=False)
    k_folds = serializers.IntegerField(min_value=2, max_value=10, default=5)

    def validate_test_data(self, value):
        """Validate test data."""
        if not value:
            raise serializers.ValidationError("Test data cannot be empty.")
        return value
