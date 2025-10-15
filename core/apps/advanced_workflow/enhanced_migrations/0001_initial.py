"""
Initial migration for Enhanced Advanced Workflow & Automation Platform.
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
            name="IntelligentProcessAutomation",
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
                    "ipa_type",
                    models.CharField(
                        choices=[
                            ("process_discovery", "Process Discovery"),
                            ("self_healing", "Self-Healing"),
                            ("intelligent_routing", "Intelligent Routing"),
                            ("predictive_automation", "Predictive Automation"),
                            ("cognitive_automation", "Cognitive Automation"),
                        ],
                        max_length=50,
                    ),
                ),
                ("process_definition", models.JSONField(default=dict)),
                ("ai_models", models.JSONField(default=list)),
                ("self_healing_config", models.JSONField(default=dict)),
                ("process_discovery_rules", models.JSONField(default=list)),
                ("intelligent_routing", models.JSONField(default=dict)),
                ("total_processes", models.PositiveIntegerField(default=0)),
                ("automated_processes", models.PositiveIntegerField(default=0)),
                ("self_healing_events", models.PositiveIntegerField(default=0)),
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
            name="WorkflowEngine",
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
                    "engine_type",
                    models.CharField(
                        choices=[
                            ("visual_designer", "Visual Designer"),
                            ("parallel_execution", "Parallel Execution"),
                            ("conditional_logic", "Conditional Logic"),
                            ("event_driven", "Event-Driven"),
                            ("state_machine", "State Machine"),
                        ],
                        max_length=50,
                    ),
                ),
                ("workflow_definition", models.JSONField(default=dict)),
                ("execution_engine", models.JSONField(default=dict)),
                ("parallel_processing", models.JSONField(default=dict)),
                ("conditional_logic", models.JSONField(default=dict)),
                ("event_handlers", models.JSONField(default=list)),
                ("total_workflows", models.PositiveIntegerField(default=0)),
                ("active_workflows", models.PositiveIntegerField(default=0)),
                ("total_executions", models.PositiveIntegerField(default=0)),
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
            name="ProcessIntelligence",
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
                    "intelligence_type",
                    models.CharField(
                        choices=[
                            ("process_mining", "Process Mining"),
                            ("performance_analytics", "Performance Analytics"),
                            (
                                "optimization_recommendations",
                                "Optimization Recommendations",
                            ),
                            ("bottleneck_analysis", "Bottleneck Analysis"),
                            ("resource_optimization", "Resource Optimization"),
                        ],
                        max_length=50,
                    ),
                ),
                ("process_mining_config", models.JSONField(default=dict)),
                ("performance_analytics", models.JSONField(default=dict)),
                ("optimization_rules", models.JSONField(default=list)),
                ("bottleneck_detection", models.JSONField(default=dict)),
                ("resource_optimization", models.JSONField(default=dict)),
                ("total_processes_analyzed", models.PositiveIntegerField(default=0)),
                (
                    "optimization_recommendations",
                    models.PositiveIntegerField(default=0),
                ),
                ("performance_improvements", models.FloatField(default=0.0)),
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
            name="AutomationMarketplace",
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
                            ("template_library", "Template Library"),
                            ("community_automation", "Community Automation"),
                            ("enterprise_automation", "Enterprise Automation"),
                            ("custom_automation", "Custom Automation"),
                            ("ai_automation", "AI Automation"),
                        ],
                        max_length=50,
                    ),
                ),
                ("automation_templates", models.JSONField(default=list)),
                ("community_library", models.JSONField(default=dict)),
                ("enterprise_automations", models.JSONField(default=list)),
                ("custom_automations", models.JSONField(default=list)),
                ("ai_automations", models.JSONField(default=list)),
                ("total_templates", models.PositiveIntegerField(default=0)),
                ("downloads", models.PositiveIntegerField(default=0)),
                ("community_contributions", models.PositiveIntegerField(default=0)),
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
            name="IntegrationAutomation",
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
                    "automation_type",
                    models.CharField(
                        choices=[
                            ("cross_system", "Cross-System"),
                            ("event_driven", "Event-Driven"),
                            ("api_automation", "API Automation"),
                            ("data_automation", "Data Automation"),
                            ("workflow_automation", "Workflow Automation"),
                        ],
                        max_length=50,
                    ),
                ),
                ("integration_config", models.JSONField(default=dict)),
                ("event_driven_config", models.JSONField(default=dict)),
                ("api_automation", models.JSONField(default=dict)),
                ("data_automation", models.JSONField(default=dict)),
                ("workflow_automation", models.JSONField(default=dict)),
                ("total_integrations", models.PositiveIntegerField(default=0)),
                ("automated_integrations", models.PositiveIntegerField(default=0)),
                ("cross_system_automations", models.PositiveIntegerField(default=0)),
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
            name="WorkflowTemplate",
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
                            ("business_process", "Business Process"),
                            ("technical_process", "Technical Process"),
                            ("approval_process", "Approval Process"),
                            ("data_process", "Data Process"),
                            ("integration_process", "Integration Process"),
                        ],
                        max_length=50,
                    ),
                ),
                ("template_definition", models.JSONField(default=dict)),
                ("template_config", models.JSONField(default=dict)),
                ("required_fields", models.JSONField(default=list)),
                ("optional_fields", models.JSONField(default=list)),
                ("template_category", models.CharField(max_length=100)),
                ("template_description", models.TextField()),
                ("total_uses", models.PositiveIntegerField(default=0)),
                ("is_public", models.BooleanField(default=False)),
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
            name="WorkflowExecution",
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
                ("execution_id", models.CharField(max_length=100, unique=True)),
                ("workflow_name", models.CharField(max_length=200)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        max_length=20,
                    ),
                ),
                ("execution_data", models.JSONField(default=dict)),
                ("execution_log", models.JSONField(default=list)),
                ("start_time", models.DateTimeField(auto_now_add=True)),
                ("end_time", models.DateTimeField(null=True, blank=True)),
                ("duration", models.DurationField(null=True, blank=True)),
                ("error_message", models.TextField(null=True, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
                (
                    "workflow_engine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="advanced_workflow.workflowengine",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProcessMetric",
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
                            ("execution_time", "Execution Time"),
                            ("success_rate", "Success Rate"),
                            ("error_rate", "Error Rate"),
                            ("throughput", "Throughput"),
                            ("resource_usage", "Resource Usage"),
                        ],
                        max_length=50,
                    ),
                ),
                ("metric_value", models.FloatField()),
                ("metric_unit", models.CharField(max_length=50)),
                ("target_value", models.FloatField(null=True, blank=True)),
                ("metric_data", models.JSONField(default=dict)),
                ("measurement_date", models.DateTimeField(auto_now_add=True)),
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
            name="AutomationRule",
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
                    "rule_type",
                    models.CharField(
                        choices=[
                            ("trigger", "Trigger"),
                            ("action", "Action"),
                            ("condition", "Condition"),
                            ("exception", "Exception"),
                            ("escalation", "Escalation"),
                        ],
                        max_length=50,
                    ),
                ),
                ("rule_definition", models.JSONField(default=dict)),
                ("trigger_conditions", models.JSONField(default=list)),
                ("action_sequences", models.JSONField(default=list)),
                ("exception_handling", models.JSONField(default=dict)),
                ("escalation_rules", models.JSONField(default=list)),
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
    ]
