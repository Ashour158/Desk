"""
Customer Experience views.
"""

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    CustomerJourney,
    CustomerPersona,
    ProactiveSupport,
    CustomerHealthScore,
    PersonalizationRule,
)
from .serializers import (
    CustomerJourneySerializer,
    CustomerPersonaSerializer,
    ProactiveSupportSerializer,
    CustomerHealthScoreSerializer,
    PersonalizationRuleSerializer,
)


class CustomerJourneyViewSet(viewsets.ModelViewSet):
    """ViewSet for customer journey management."""

    queryset = CustomerJourney.objects.all()
    serializer_class = CustomerJourneySerializer


class CustomerPersonaViewSet(viewsets.ModelViewSet):
    """ViewSet for customer persona management."""

    queryset = CustomerPersona.objects.all()
    serializer_class = CustomerPersonaSerializer


class ProactiveSupportViewSet(viewsets.ModelViewSet):
    """ViewSet for proactive support management."""

    queryset = ProactiveSupport.objects.all()
    serializer_class = ProactiveSupportSerializer


class CustomerHealthScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for customer health score management."""

    queryset = CustomerHealthScore.objects.all()
    serializer_class = CustomerHealthScoreSerializer


class PersonalizationRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for personalization rule management."""

    queryset = PersonalizationRule.objects.all()
    serializer_class = PersonalizationRuleSerializer


def customer_experience_dashboard(request):
    """Customer Experience Dashboard view."""
    context = {
        "total_journeys": CustomerJourney.objects.count(),
        "active_personas": CustomerPersona.objects.filter(is_active=True).count(),
        "proactive_supports": ProactiveSupport.objects.count(),
        "health_scores": CustomerHealthScore.objects.count(),
    }
    return render(request, "customer_experience/dashboard.html", context)


def customer_experience_analytics(request):
    """Customer Experience Analytics view."""
    return render(request, "customer_experience/analytics.html")
