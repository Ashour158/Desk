"""
Initial migration for Enhanced Mobile & IoT Platform.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MobilePlatform",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "platform_type",
                    models.CharField(
                        choices=[
                            ("ios", "iOS"),
                            ("android", "Android"),
                            ("cross_platform", "Cross Platform"),
                            ("progressive_web_app", "Progressive Web App"),
                            ("hybrid", "Hybrid"),
                        ],
                        max_length=50,
                    ),
                ),
                ("app_configuration", models.JSONField(default=dict)),
                ("offline_capabilities", models.JSONField(default=dict)),
                ("push_notifications", models.JSONField(default=dict)),
                ("user_authentication", models.JSONField(default=dict)),
                ("data_synchronization", models.JSONField(default=dict)),
                ("total_users", models.PositiveIntegerField(default=0)),
                ("active_users", models.PositiveIntegerField(default=0)),
                ("app_downloads", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="IoTDevice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "device_type",
                    models.CharField(
                        choices=[
                            ("sensor", "Sensor"),
                            ("actuator", "Actuator"),
                            ("gateway", "Gateway"),
                            ("edge_device", "Edge Device"),
                            ("smart_device", "Smart Device"),
                        ],
                        max_length=50,
                    ),
                ),
                ("device_id", models.CharField(max_length=100, unique=True)),
                ("device_configuration", models.JSONField(default=dict)),
                ("connectivity_protocols", models.JSONField(default=list)),
                ("data_schema", models.JSONField(default=dict)),
                ("edge_analytics_config", models.JSONField(default=dict)),
                ("security_settings", models.JSONField(default=dict)),
                ("total_data_points", models.PositiveIntegerField(default=0)),
                ("last_data_received", models.DateTimeField(null=True, blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ARVRSupport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "arvr_type",
                    models.CharField(
                        choices=[
                            ("augmented_reality", "Augmented Reality"),
                            ("virtual_reality", "Virtual Reality"),
                            ("mixed_reality", "Mixed Reality"),
                            ("remote_assistance", "Remote Assistance"),
                        ],
                        max_length=50,
                    ),
                ),
                ("arvr_configuration", models.JSONField(default=dict)),
                ("remote_assistance_config", models.JSONField(default=dict)),
                ("vr_training_config", models.JSONField(default=dict)),
                ("device_requirements", models.JSONField(default=dict)),
                ("content_management", models.JSONField(default=dict)),
                ("total_sessions", models.PositiveIntegerField(default=0)),
                ("active_sessions", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WearableIntegration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "wearable_type",
                    models.CharField(
                        choices=[
                            ("smartwatch", "Smartwatch"),
                            ("fitness_tracker", "Fitness Tracker"),
                            ("smart_glasses", "Smart Glasses"),
                            ("smart_ring", "Smart Ring"),
                            ("smart_clothing", "Smart Clothing"),
                        ],
                        max_length=50,
                    ),
                ),
                ("wearable_configuration", models.JSONField(default=dict)),
                ("biometric_authentication", models.JSONField(default=dict)),
                ("health_monitoring", models.JSONField(default=dict)),
                ("notification_settings", models.JSONField(default=dict)),
                ("data_collection", models.JSONField(default=dict)),
                ("total_wearables", models.PositiveIntegerField(default=0)),
                ("active_wearables", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LocationService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "service_type",
                    models.CharField(
                        choices=[
                            ("gps_tracking", "GPS Tracking"),
                            ("geofencing", "Geofencing"),
                            ("location_intelligence", "Location Intelligence"),
                            ("route_optimization", "Route Optimization"),
                            ("asset_tracking", "Asset Tracking"),
                        ],
                        max_length=50,
                    ),
                ),
                ("location_configuration", models.JSONField(default=dict)),
                ("gps_settings", models.JSONField(default=dict)),
                ("geofencing_rules", models.JSONField(default=list)),
                ("location_analytics", models.JSONField(default=dict)),
                ("privacy_settings", models.JSONField(default=dict)),
                ("total_locations", models.PositiveIntegerField(default=0)),
                ("active_tracking", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MobileApp",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "app_type",
                    models.CharField(
                        choices=[
                            ("native", "Native"),
                            ("hybrid", "Hybrid"),
                            ("progressive_web_app", "Progressive Web App"),
                            ("cross_platform", "Cross Platform"),
                        ],
                        max_length=50,
                    ),
                ),
                ("app_configuration", models.JSONField(default=dict)),
                ("features", models.JSONField(default=list)),
                ("user_interface", models.JSONField(default=dict)),
                ("performance_metrics", models.JSONField(default=dict)),
                ("total_downloads", models.PositiveIntegerField(default=0)),
                ("active_users", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="IoTDataPoint",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data_type", models.CharField(max_length=100)),
                ("value", models.FloatField()),
                ("unit", models.CharField(max_length=50)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("metadata", models.JSONField(default=dict)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mobile_iot.iotdevice",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LocationData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("altitude", models.FloatField(null=True, blank=True)),
                ("accuracy", models.FloatField(null=True, blank=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("metadata", models.JSONField(default=dict)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mobile_iot.locationservice",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WearableData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data_type", models.CharField(max_length=100)),
                ("value", models.FloatField()),
                ("unit", models.CharField(max_length=50)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("metadata", models.JSONField(default=dict)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
                (
                    "wearable",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mobile_iot.wearableintegration",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ARVRSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("session_type", models.CharField(max_length=100)),
                ("session_data", models.JSONField(default=dict)),
                ("duration", models.DurationField(null=True, blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(null=True, blank=True)),
                (
                    "arvr_support",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mobile_iot.arvrsupport",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
            ],
        ),
    ]
