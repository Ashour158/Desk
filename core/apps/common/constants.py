"""
Common constants to eliminate magic numbers across the application.
"""

from datetime import time, timedelta

# Time-related constants
DEFAULT_BUSINESS_START_TIME = time(9, 0)  # 9:00 AM
DEFAULT_BUSINESS_END_TIME = time(17, 0)   # 5:00 PM
DEFAULT_BUSINESS_HOURS = {
    "monday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "tuesday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "wednesday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "thursday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "friday": {"enabled": True, "start": "09:00", "end": "17:00"},
    "saturday": {"enabled": False, "start": "09:00", "end": "17:00"},
    "sunday": {"enabled": False, "start": "09:00", "end": "17:00"},
}

# SLA time constants
SLA_CRITICAL_THRESHOLD = timedelta(hours=1)
SLA_WARNING_THRESHOLD = timedelta(hours=4)
SLA_MAX_DAYS_TO_CHECK = 7

# Model field length constants
SHORT_FIELD_LENGTH = 50
MEDIUM_FIELD_LENGTH = 100
LONG_FIELD_LENGTH = 200
VERY_LONG_FIELD_LENGTH = 255

# Pagination constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Status constants
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"

# Priority constants
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_CRITICAL = "critical"

# Operator constants for condition evaluation
OPERATOR_EQUALS = "equals"
OPERATOR_NOT_EQUALS = "not_equals"
OPERATOR_CONTAINS = "contains"
OPERATOR_NOT_CONTAINS = "not_contains"
OPERATOR_STARTS_WITH = "starts_with"
OPERATOR_ENDS_WITH = "ends_with"
OPERATOR_IN = "in"
OPERATOR_NOT_IN = "not_in"
OPERATOR_GREATER_THAN = "greater_than"
OPERATOR_LESS_THAN = "less_than"
OPERATOR_GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
OPERATOR_LESS_THAN_OR_EQUAL = "less_than_or_equal"
OPERATOR_IS_EMPTY = "is_empty"
OPERATOR_IS_NOT_EMPTY = "is_not_empty"
OPERATOR_REGEX = "regex"

# Common choice definitions
COMMON_STATUS_CHOICES = [
    (STATUS_ACTIVE, "Active"),
    (STATUS_INACTIVE, "Inactive"),
    (STATUS_PENDING, "Pending"),
    (STATUS_COMPLETED, "Completed"),
]

COMMON_PRIORITY_CHOICES = [
    (PRIORITY_LOW, "Low"),
    (PRIORITY_MEDIUM, "Medium"),
    (PRIORITY_HIGH, "High"),
    (PRIORITY_CRITICAL, "Critical"),
]

# Device type choices
DEVICE_TYPE_CHOICES = [
    ("sensor", "Sensor"),
    ("actuator", "Actuator"),
    ("gateway", "Gateway"),
    ("edge_device", "Edge Device"),
    ("smart_device", "Smart Device"),
]

# Platform type choices
PLATFORM_TYPE_CHOICES = [
    ("ios", "iOS"),
    ("android", "Android"),
    ("cross_platform", "Cross Platform"),
    ("progressive_web_app", "Progressive Web App"),
    ("hybrid", "Hybrid"),
]

# AR/VR type choices
ARVR_TYPE_CHOICES = [
    ("augmented_reality", "Augmented Reality"),
    ("virtual_reality", "Virtual Reality"),
    ("mixed_reality", "Mixed Reality"),
    ("remote_assistance", "Remote Assistance"),
]

# Wearable type choices
WEARABLE_TYPE_CHOICES = [
    ("smartwatch", "Smartwatch"),
    ("fitness_tracker", "Fitness Tracker"),
    ("smart_glasses", "Smart Glasses"),
    ("smart_ring", "Smart Ring"),
    ("smart_clothing", "Smart Clothing"),
]

# Location service type choices
LOCATION_SERVICE_TYPE_CHOICES = [
    ("gps_tracking", "GPS Tracking"),
    ("geofencing", "Geofencing"),
    ("location_intelligence", "Location Intelligence"),
    ("route_optimization", "Route Optimization"),
    ("asset_tracking", "Asset Tracking"),
]

# Mobile app type choices
MOBILE_APP_TYPE_CHOICES = [
    ("native", "Native"),
    ("hybrid", "Hybrid"),
    ("progressive_web_app", "Progressive Web App"),
    ("cross_platform", "Cross Platform"),
]
