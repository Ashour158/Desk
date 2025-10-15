"""
AI & Machine Learning serializers.
"""

from rest_framework import serializers
from .models import (
    TicketCategorization,
    SentimentAnalysis,
    Chatbot,
    AIModel,
    AIProcessingJob,
)


class TicketCategorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategorization
        fields = "__all__"


class SentimentAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentAnalysis
        fields = "__all__"


class ChatbotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatbot
        fields = "__all__"


class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = "__all__"


class AIProcessingJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIProcessingJob
        fields = "__all__"
