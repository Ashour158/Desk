"""
Advanced Communication serializers.
"""

from rest_framework import serializers
from .models import (
    CommunicationChannel,
    VideoConference,
    CommunicationTemplate,
    CommunicationLog,
)


class CommunicationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationChannel
        fields = "__all__"


class VideoConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoConference
        fields = "__all__"


class CommunicationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationTemplate
        fields = "__all__"


class CommunicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationLog
        fields = "__all__"
