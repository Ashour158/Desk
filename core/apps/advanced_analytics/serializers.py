"""
Advanced Analytics serializers.
"""

from rest_framework import serializers
from .models import CustomReport, Dashboard, KPIBuilder, DataExport, ReportSchedule


class CustomReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomReport
        fields = "__all__"


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = "__all__"


class KPIBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIBuilder
        fields = "__all__"


class DataExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataExport
        fields = "__all__"


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = "__all__"
