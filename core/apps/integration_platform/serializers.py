"""
Integration Platform serializers.
"""

from rest_framework import serializers
from .models import (
    Webhook,
    APIIntegration,
    ThirdPartyService,
    IntegrationLog,
    Connector,
)


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = "__all__"


class APIIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIIntegration
        fields = "__all__"


class ThirdPartyServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThirdPartyService
        fields = "__all__"


class IntegrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationLog
        fields = "__all__"


class ConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connector
        fields = "__all__"
