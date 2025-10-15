"""
Initial migration for Enhanced Integration & API Platform.
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
            name="EnterpriseIntegrationHub",
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
                    "hub_type",
                    models.CharField(
                        choices=[
                            ("pre_built_connectors", "Pre-built Connectors"),
                            ("legacy_system_integration", "Legacy System Integration"),
                            ("custom_integration", "Custom Integration"),
                        ],
                        max_length=50,
                    ),
                ),
                ("available_connectors", models.JSONField(default=list)),
                ("active_connectors", models.JSONField(default=list)),
                ("integration_rules", models.JSONField(default=list)),
                ("data_mapping", models.JSONField(default=dict)),
                ("total_integrations", models.PositiveIntegerField(default=0)),
                ("data_processed", models.PositiveIntegerField(default=0)),
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
            name="APIManagement",
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
                    "api_type",
                    models.CharField(
                        choices=[
                            ("rest_api", "REST API"),
                            ("graphql_api", "GraphQL API"),
                            ("soap_api", "SOAP API"),
                            ("webhook_api", "Webhook API"),
                        ],
                        max_length=50,
                    ),
                ),
                ("base_url", models.URLField()),
                ("version", models.CharField(max_length=20)),
                ("authentication_methods", models.JSONField(default=list)),
                ("rate_limits", models.JSONField(default=dict)),
                ("api_documentation", models.JSONField(default=dict)),
                ("total_requests", models.PositiveIntegerField(default=0)),
                ("successful_requests", models.PositiveIntegerField(default=0)),
                ("failed_requests", models.PositiveIntegerField(default=0)),
                ("average_response_time", models.FloatField(default=0.0)),
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
            name="WorkflowAutomation",
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
                    "workflow_type",
                    models.CharField(
                        choices=[
                            ("visual_designer", "Visual Designer"),
                            ("conditional_logic", "Conditional Logic"),
                            ("approval_workflow", "Approval Workflow"),
                        ],
                        max_length=50,
                    ),
                ),
                ("workflow_definition", models.JSONField(default=dict)),
                ("trigger_conditions", models.JSONField(default=list)),
                ("action_sequences", models.JSONField(default=list)),
                ("approval_rules", models.JSONField(default=list)),
                ("total_executions", models.PositiveIntegerField(default=0)),
                ("successful_executions", models.PositiveIntegerField(default=0)),
                ("failed_executions", models.PositiveIntegerField(default=0)),
                ("last_execution", models.DateTimeField(null=True)),
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
            name="DataIntegration",
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
                    "integration_type",
                    models.CharField(
                        choices=[
                            ("etl_pipeline", "ETL Pipeline"),
                            ("elt_pipeline", "ELT Pipeline"),
                            ("real_time_sync", "Real-time Sync"),
                            ("batch_processing", "Batch Processing"),
                        ],
                        max_length=50,
                    ),
                ),
                ("source_systems", models.JSONField(default=list)),
                ("target_systems", models.JSONField(default=list)),
                ("data_mapping", models.JSONField(default=dict)),
                ("transformation_rules", models.JSONField(default=list)),
                ("total_records_processed", models.PositiveIntegerField(default=0)),
                ("successful_syncs", models.PositiveIntegerField(default=0)),
                ("failed_syncs", models.PositiveIntegerField(default=0)),
                ("last_sync", models.DateTimeField(null=True)),
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
            name="IntegrationMarketplace",
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
                    "marketplace_type",
                    models.CharField(
                        choices=[
                            ("app_store", "App Store"),
                            ("integration_marketplace", "Integration Marketplace"),
                            ("custom_marketplace", "Custom Marketplace"),
                        ],
                        max_length=50,
                    ),
                ),
                ("available_apps", models.JSONField(default=list)),
                ("revenue_sharing_model", models.JSONField(default=dict)),
                ("pricing_tiers", models.JSONField(default=list)),
                ("approval_process", models.JSONField(default=dict)),
                ("total_apps", models.PositiveIntegerField(default=0)),
                ("active_apps", models.PositiveIntegerField(default=0)),
                (
                    "total_revenue",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
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
            name="IntegrationConnector",
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
                    "connector_type",
                    models.CharField(
                        choices=[
                            ("database", "Database"),
                            ("api", "API"),
                            ("file", "File"),
                            ("cloud_service", "Cloud Service"),
                        ],
                        max_length=50,
                    ),
                ),
                ("category", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("configuration_schema", models.JSONField(default=dict)),
                ("authentication_methods", models.JSONField(default=list)),
                ("supported_operations", models.JSONField(default=list)),
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
            name="IntegrationTemplate",
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
                    "template_type",
                    models.CharField(
                        choices=[
                            ("workflow", "Workflow"),
                            ("integration", "Integration"),
                            ("api", "API"),
                            ("data_pipeline", "Data Pipeline"),
                        ],
                        max_length=50,
                    ),
                ),
                ("category", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("template_configuration", models.JSONField(default=dict)),
                ("required_fields", models.JSONField(default=list)),
                ("optional_fields", models.JSONField(default=list)),
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
            name="IntegrationLog",
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
                (
                    "log_type",
                    models.CharField(
                        choices=[
                            ("connection", "Connection"),
                            ("data_transfer", "Data Transfer"),
                            ("workflow", "Workflow"),
                            ("api", "API"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("info", "Info"),
                            ("warning", "Warning"),
                            ("error", "Error"),
                            ("critical", "Critical"),
                        ],
                        max_length=20,
                    ),
                ),
                ("message", models.TextField()),
                ("connector_id", models.CharField(max_length=100, null=True)),
                ("integration_id", models.CharField(max_length=100, null=True)),
                ("metadata", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
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
            name="IntegrationMetric",
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
                ("metric_name", models.CharField(max_length=200)),
                (
                    "metric_type",
                    models.CharField(
                        choices=[
                            ("performance", "Performance"),
                            ("usage", "Usage"),
                            ("error", "Error"),
                            ("custom", "Custom"),
                        ],
                        max_length=50,
                    ),
                ),
                ("value", models.FloatField()),
                ("unit", models.CharField(max_length=50)),
                ("connector_id", models.CharField(max_length=100, null=True)),
                ("integration_id", models.CharField(max_length=100, null=True)),
                ("metadata", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
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
