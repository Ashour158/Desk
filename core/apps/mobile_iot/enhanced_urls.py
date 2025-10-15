"""
Enhanced Mobile & IoT Platform URLs for advanced capabilities.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    MobilePlatformViewSet,
    IoTDeviceViewSet,
    ARVRSupportViewSet,
    WearableIntegrationViewSet,
    LocationServiceViewSet,
    MobileAppViewSet,
    IoTDataPointViewSet,
    LocationDataViewSet,
    WearableDataViewSet,
    ARVRSessionViewSet,
    mobile_iot_dashboard,
    mobile_iot_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"mobile-platforms", MobilePlatformViewSet)
router.register(r"iot-devices", IoTDeviceViewSet)
router.register(r"arvr-supports", ARVRSupportViewSet)
router.register(r"wearable-integrations", WearableIntegrationViewSet)
router.register(r"location-services", LocationServiceViewSet)
router.register(r"mobile-apps", MobileAppViewSet)
router.register(r"iot-data-points", IoTDataPointViewSet)
router.register(r"location-data", LocationDataViewSet)
router.register(r"wearable-data", WearableDataViewSet)
router.register(r"arvr-sessions", ARVRSessionViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path("dashboard/", mobile_iot_dashboard, name="mobile_iot_dashboard"),
    path("analytics/", mobile_iot_analytics, name="mobile_iot_analytics"),
]
