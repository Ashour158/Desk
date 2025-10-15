"""
Mobile & IoT Platform URL configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MobileAppViewSet,
    IoTDeviceViewSet,
    LocationTrackingViewSet,
    OfflineSyncViewSet,
    mobile_iot_dashboard,
    mobile_iot_analytics,
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r"mobile-apps", MobileAppViewSet)
router.register(r"iot-devices", IoTDeviceViewSet)
router.register(r"location-tracking", LocationTrackingViewSet)
router.register(r"offline-sync", OfflineSyncViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard views
    path("dashboard/", mobile_iot_dashboard, name="mobile_iot_dashboard"),
    path("analytics/", mobile_iot_analytics, name="mobile_iot_analytics"),
]
