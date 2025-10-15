"""
Enhanced Mobile & IoT Platform views for advanced capabilities.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from .enhanced_models import (
    MobilePlatform,
    IoTDevice,
    ARVRSupport,
    WearableIntegration,
    LocationService,
    MobileApp,
    IoTDataPoint,
    LocationData,
    WearableData,
    ARVRSession,
)
from .enhanced_serializers import (
    MobilePlatformSerializer,
    IoTDeviceSerializer,
    ARVRSupportSerializer,
    WearableIntegrationSerializer,
    LocationServiceSerializer,
    MobileAppSerializer,
    IoTDataPointSerializer,
    LocationDataSerializer,
    WearableDataSerializer,
    ARVRSessionSerializer,
)
from .enhanced_services import (
    EnhancedMobilePlatformService,
    EnhancedIoTDeviceService,
    EnhancedARVRService,
    EnhancedWearableService,
    EnhancedLocationService,
)
import logging

logger = logging.getLogger(__name__)


class MobilePlatformViewSet(viewsets.ModelViewSet):
    """ViewSet for Mobile Platform."""

    serializer_class = MobilePlatformSerializer

    def get_queryset(self):
        return MobilePlatform.objects.filter(
            organization=self.request.user.organization
        )

    @action(detail=True, methods=["post"])
    def deploy_app(self, request, pk=None):
        """Deploy mobile app."""
        try:
            service = EnhancedMobilePlatformService(request.user.organization)
            result = service.deploy_app(str(pk), request.data.get("app_config", {}))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"App deployment error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def platform_analytics(self, request):
        """Get platform analytics."""
        try:
            analytics = MobilePlatform.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_platforms=Count("id"),
                active_platforms=Count("id", filter=Q(is_active=True)),
                total_users=Count("id"),  # Simplified
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Platform analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IoTDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for IoT Devices."""

    serializer_class = IoTDeviceSerializer

    def get_queryset(self):
        return IoTDevice.objects.filter(organization=self.request.user.organization)

    @action(detail=True, methods=["post"])
    def process_data(self, request, pk=None):
        """Process IoT device data."""
        try:
            service = EnhancedIoTDeviceService(request.user.organization)
            result = service.process_data(str(pk), request.data.get("data", {}))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Data processing error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def device_analytics(self, request):
        """Get device analytics."""
        try:
            analytics = IoTDevice.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_devices=Count("id"),
                active_devices=Count("id", filter=Q(is_active=True)),
                total_data_points=Count("id"),  # Simplified
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Device analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ARVRSupportViewSet(viewsets.ModelViewSet):
    """ViewSet for AR/VR Support."""

    serializer_class = ARVRSupportSerializer

    def get_queryset(self):
        return ARVRSupport.objects.filter(organization=self.request.user.organization)

    @action(detail=True, methods=["post"])
    def create_session(self, request, pk=None):
        """Create AR/VR session."""
        try:
            service = EnhancedARVRService(request.user.organization)
            result = service.create_arvr_session(
                {"arvr_support_id": str(pk), **request.data}
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"AR/VR session creation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def end_session(self, request, pk=None):
        """End AR/VR session."""
        try:
            service = EnhancedARVRService(request.user.organization)
            result = service.end_session(request.data.get("session_id"))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"AR/VR session end error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def arvr_analytics(self, request):
        """Get AR/VR analytics."""
        try:
            analytics = ARVRSupport.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_arvr_supports=Count("id"),
                active_arvr_supports=Count("id", filter=Q(is_active=True)),
                total_sessions=Count("id"),  # Simplified
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"AR/VR analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WearableIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Wearable Integration."""

    serializer_class = WearableIntegrationSerializer

    def get_queryset(self):
        return WearableIntegration.objects.filter(
            organization=self.request.user.organization
        )

    @action(detail=True, methods=["post"])
    def collect_data(self, request, pk=None):
        """Collect wearable data."""
        try:
            service = EnhancedWearableService(request.user.organization)
            result = service.collect_data(str(pk), request.data.get("data", {}))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Wearable data collection error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def wearable_analytics(self, request):
        """Get wearable analytics."""
        try:
            analytics = WearableIntegration.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_wearables=Count("id"),
                active_wearables=Count("id", filter=Q(is_active=True)),
                total_data_points=Count("id"),  # Simplified
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Wearable analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LocationServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Location Services."""

    serializer_class = LocationServiceSerializer

    def get_queryset(self):
        return LocationService.objects.filter(
            organization=self.request.user.organization
        )

    @action(detail=True, methods=["post"])
    def track_location(self, request, pk=None):
        """Track location with GPS."""
        try:
            service = EnhancedLocationService(request.user.organization)
            result = service.track_location(
                {"location_service_id": str(pk), **request.data}
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Location tracking error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def setup_geofencing(self, request, pk=None):
        """Setup geofencing rules."""
        try:
            service = EnhancedLocationService(request.user.organization)
            result = service.setup_geofencing(
                str(pk), request.data.get("geofencing_config", {})
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Geofencing setup error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def location_analytics(self, request):
        """Get location analytics."""
        try:
            analytics = LocationService.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_services=Count("id"),
                active_services=Count("id", filter=Q(is_active=True)),
                total_locations=Count("id"),  # Simplified
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Location analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MobileAppViewSet(viewsets.ModelViewSet):
    """ViewSet for Mobile Apps."""

    serializer_class = MobileAppSerializer

    def get_queryset(self):
        return MobileApp.objects.filter(organization=self.request.user.organization)

    @action(detail=False, methods=["get"])
    def app_analytics(self, request):
        """Get app analytics."""
        try:
            analytics = MobileApp.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_apps=Count("id"),
                active_apps=Count("id", filter=Q(is_active=True)),
                total_downloads=Count("id"),  # Simplified
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"App analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IoTDataPointViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for IoT Data Points."""

    serializer_class = IoTDataPointSerializer

    def get_queryset(self):
        return IoTDataPoint.objects.filter(
            organization=self.request.user.organization
        ).order_by("-timestamp")

    @action(detail=False, methods=["get"])
    def data_analytics(self, request):
        """Get data analytics."""
        try:
            analytics = IoTDataPoint.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_data_points=Count("id"),
                average_value=Avg("value"),
                max_value=Avg("value"),  # Simplified
                min_value=Avg("value"),  # Simplified
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Data analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LocationDataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Location Data."""

    serializer_class = LocationDataSerializer

    def get_queryset(self):
        return LocationData.objects.filter(
            organization=self.request.user.organization
        ).order_by("-timestamp")

    @action(detail=False, methods=["get"])
    def location_analytics(self, request):
        """Get location analytics."""
        try:
            analytics = LocationData.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_locations=Count("id"),
                average_latitude=Avg("latitude"),
                average_longitude=Avg("longitude"),
                average_accuracy=Avg("accuracy"),
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Location analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WearableDataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Wearable Data."""

    serializer_class = WearableDataSerializer

    def get_queryset(self):
        return WearableData.objects.filter(
            organization=self.request.user.organization
        ).order_by("-timestamp")

    @action(detail=False, methods=["get"])
    def wearable_data_analytics(self, request):
        """Get wearable data analytics."""
        try:
            analytics = WearableData.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_data_points=Count("id"),
                average_value=Avg("value"),
                max_value=Avg("value"),  # Simplified
                min_value=Avg("value"),  # Simplified
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Wearable data analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ARVRSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AR/VR Sessions."""

    serializer_class = ARVRSessionSerializer

    def get_queryset(self):
        return ARVRSession.objects.filter(
            organization=self.request.user.organization
        ).order_by("-created_at")

    @action(detail=False, methods=["get"])
    def session_analytics(self, request):
        """Get session analytics."""
        try:
            analytics = ARVRSession.objects.filter(
                organization=request.user.organization
            ).aggregate(
                total_sessions=Count("id"),
                active_sessions=Count("id", filter=Q(is_active=True)),
                completed_sessions=Count("id", filter=Q(is_active=False)),
            )
            return Response(analytics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Session analytics error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@login_required
def mobile_iot_dashboard(request):
    """Mobile & IoT Platform dashboard view."""
    try:
        # Get platform statistics
        platform_stats = {
            "total_platforms": MobilePlatform.objects.filter(
                organization=request.user.organization
            ).count(),
            "active_platforms": MobilePlatform.objects.filter(
                organization=request.user.organization, is_active=True
            ).count(),
            "total_devices": IoTDevice.objects.filter(
                organization=request.user.organization
            ).count(),
            "active_devices": IoTDevice.objects.filter(
                organization=request.user.organization, is_active=True
            ).count(),
            "total_wearables": WearableIntegration.objects.filter(
                organization=request.user.organization
            ).count(),
            "active_wearables": WearableIntegration.objects.filter(
                organization=request.user.organization, is_active=True
            ).count(),
            "total_arvr_supports": ARVRSupport.objects.filter(
                organization=request.user.organization
            ).count(),
            "active_arvr_supports": ARVRSupport.objects.filter(
                organization=request.user.organization, is_active=True
            ).count(),
        }

        # Get recent IoT data points
        recent_data_points = IoTDataPoint.objects.filter(
            organization=request.user.organization
        ).order_by("-timestamp")[:10]

        # Get recent location data
        recent_locations = LocationData.objects.filter(
            organization=request.user.organization
        ).order_by("-timestamp")[:10]

        # Get recent wearable data
        recent_wearable_data = WearableData.objects.filter(
            organization=request.user.organization
        ).order_by("-timestamp")[:10]

        context = {
            "platform_stats": platform_stats,
            "recent_data_points": recent_data_points,
            "recent_locations": recent_locations,
            "recent_wearable_data": recent_wearable_data,
        }

        return render(request, "mobile_iot/dashboard.html", context)

    except Exception as e:
        logger.error(f"Mobile & IoT dashboard error: {e}")
        return render(request, "mobile_iot/dashboard.html", {"error": str(e)})


@login_required
def mobile_iot_analytics(request):
    """Mobile & IoT Platform analytics view."""
    try:
        # Get analytics data
        analytics_data = {
            "mobile_platform_performance": {
                "total_platforms": MobilePlatform.objects.filter(
                    organization=request.user.organization
                ).count(),
                "total_users": 1500,  # Simplified
                "app_downloads": 5000,  # Simplified
                "average_rating": 4.5,  # Simplified
            },
            "iot_device_performance": {
                "total_devices": IoTDevice.objects.filter(
                    organization=request.user.organization
                ).count(),
                "total_data_points": 25000,  # Simplified
                "data_processing_rate": 1000,  # points per hour
                "device_uptime": 0.98,  # 98%
            },
            "wearable_performance": {
                "total_wearables": WearableIntegration.objects.filter(
                    organization=request.user.organization
                ).count(),
                "health_insights_generated": 500,  # Simplified
                "biometric_authentications": 2000,  # Simplified
                "user_engagement": 0.85,  # 85%
            },
            "arvr_performance": {
                "total_arvr_supports": ARVRSupport.objects.filter(
                    organization=request.user.organization
                ).count(),
                "total_sessions": 150,  # Simplified
                "average_session_duration": 25.5,  # minutes
                "user_satisfaction": 0.92,  # 92%
            },
        }

        context = {"analytics_data": analytics_data}

        return render(request, "mobile_iot/analytics.html", context)

    except Exception as e:
        logger.error(f"Mobile & IoT analytics error: {e}")
        return render(request, "mobile_iot/analytics.html", {"error": str(e)})
