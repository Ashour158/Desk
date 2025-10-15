"""
Customer Experience serializers.
"""

from rest_framework import serializers
from .models import (
    CustomerJourney,
    CustomerPersona,
    ProactiveSupport,
    CustomerHealthScore,
    PersonalizationRule,
)


class CustomerJourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerJourney
        fields = "__all__"


class CustomerPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPersona
        fields = "__all__"


class ProactiveSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProactiveSupport
        fields = "__all__"


class CustomerHealthScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerHealthScore
        fields = "__all__"


class PersonalizationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalizationRule
        fields = "__all__"
