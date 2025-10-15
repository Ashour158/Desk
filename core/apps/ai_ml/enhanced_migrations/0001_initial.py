"""
Enhanced AI & Machine Learning initial migration.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organizations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="NLPEngine",
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
                ("name", models.CharField(max_length=255)),
                (
                    "engine_type",
                    models.CharField(
                        choices=[
                            ("intent_recognition", "Intent Recognition"),
                            ("entity_extraction", "Entity Extraction"),
                            ("sentiment_analysis", "Sentiment Analysis"),
                            ("language_translation", "Language Translation"),
                            ("text_summarization", "Text Summarization"),
                            ("key_phrase_extraction", "Key Phrase Extraction"),
                            ("named_entity_recognition", "Named Entity Recognition"),
                            ("text_classification", "Text Classification"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "model_name",
                    models.CharField(
                        default="bert-base-multilingual-cased", max_length=255
                    ),
                ),
                ("language_codes", models.JSONField(default=list)),
                ("confidence_threshold", models.FloatField(default=0.7)),
                ("max_tokens", models.IntegerField(default=512)),
                ("accuracy", models.FloatField(default=0.0)),
                ("precision", models.FloatField(default=0.0)),
                ("recall", models.FloatField(default=0.0)),
                ("f1_score", models.FloatField(default=0.0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_training", models.BooleanField(default=False)),
                ("last_trained", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nlp_engines",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "NLP Engine",
                "verbose_name_plural": "NLP Engines",
                "unique_together": {("organization", "name", "engine_type")},
            },
        ),
        migrations.CreateModel(
            name="ComputerVisionSuite",
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
                ("name", models.CharField(max_length=255)),
                (
                    "vision_type",
                    models.CharField(
                        choices=[
                            ("document_ocr", "Document OCR"),
                            ("barcode_scanning", "Barcode/QR Code Scanning"),
                            ("face_recognition", "Face Recognition"),
                            ("object_detection", "Object Detection"),
                            ("video_analysis", "Video Analysis"),
                            ("image_classification", "Image Classification"),
                            ("text_extraction", "Text Extraction"),
                            ("quality_assessment", "Quality Assessment"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("model_path", models.CharField(max_length=500)),
                ("input_formats", models.JSONField(default=list)),
                ("output_labels", models.JSONField(default=list)),
                ("confidence_threshold", models.FloatField(default=0.8)),
                (
                    "max_image_size",
                    models.CharField(default="1024x1024", max_length=20),
                ),
                ("batch_size", models.IntegerField(default=32)),
                ("processing_timeout", models.IntegerField(default=30)),
                ("accuracy", models.FloatField(default=0.0)),
                ("processing_speed", models.FloatField(default=0.0)),
                ("memory_usage", models.FloatField(default=0.0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_processing", models.BooleanField(default=False)),
                ("last_used", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vision_suites",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Computer Vision Suite",
                "verbose_name_plural": "Computer Vision Suites",
                "unique_together": {("organization", "name", "vision_type")},
            },
        ),
        migrations.CreateModel(
            name="PredictiveAnalyticsPlatform",
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
                ("name", models.CharField(max_length=255)),
                (
                    "analytics_type",
                    models.CharField(
                        choices=[
                            ("revenue_forecasting", "Revenue Forecasting"),
                            ("resource_optimization", "Resource Optimization"),
                            ("risk_assessment", "Risk Assessment"),
                            ("performance_prediction", "Performance Prediction"),
                            ("market_trend_analysis", "Market Trend Analysis"),
                            ("customer_lifetime_value", "Customer Lifetime Value"),
                            ("churn_prediction", "Churn Prediction"),
                            ("demand_forecasting", "Demand Forecasting"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("data_sources", models.JSONField(default=list)),
                ("feature_columns", models.JSONField(default=list)),
                ("target_column", models.CharField(max_length=100)),
                (
                    "algorithm",
                    models.CharField(default="random_forest", max_length=100),
                ),
                ("hyperparameters", models.JSONField(default=dict)),
                ("training_data_size", models.IntegerField(default=0)),
                ("test_data_size", models.IntegerField(default=0)),
                ("accuracy", models.FloatField(default=0.0)),
                ("precision", models.FloatField(default=0.0)),
                ("recall", models.FloatField(default=0.0)),
                ("f1_score", models.FloatField(default=0.0)),
                ("mae", models.FloatField(default=0.0)),
                ("rmse", models.FloatField(default=0.0)),
                ("last_prediction", models.DateTimeField(blank=True, null=True)),
                (
                    "prediction_frequency",
                    models.CharField(default="daily", max_length=50),
                ),
                ("next_prediction", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_training", models.BooleanField(default=False)),
                ("last_trained", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="predictive_analytics",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Predictive Analytics Platform",
                "verbose_name_plural": "Predictive Analytics Platforms",
                "unique_together": {("organization", "name", "analytics_type")},
            },
        ),
        migrations.CreateModel(
            name="AdvancedChatbot",
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
                ("name", models.CharField(max_length=255)),
                (
                    "chatbot_type",
                    models.CharField(
                        choices=[
                            ("rule_based", "Rule-based"),
                            ("ai_powered", "AI-powered"),
                            ("hybrid", "Hybrid"),
                            ("voice_assistant", "Voice Assistant"),
                            ("conversational_ai", "Conversational AI"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("language_codes", models.JSONField(default=["en"])),
                ("model_name", models.CharField(default="gpt-4", max_length=255)),
                ("temperature", models.FloatField(default=0.7)),
                ("max_tokens", models.IntegerField(default=1000)),
                ("context_window", models.IntegerField(default=10)),
                ("capabilities", models.JSONField(default=list)),
                ("knowledge_base_ids", models.JSONField(default=list)),
                ("integration_apis", models.JSONField(default=list)),
                ("response_accuracy", models.FloatField(default=0.0)),
                ("user_satisfaction", models.FloatField(default=0.0)),
                ("resolution_rate", models.FloatField(default=0.0)),
                ("escalation_rate", models.FloatField(default=0.0)),
                ("total_conversations", models.IntegerField(default=0)),
                ("successful_resolutions", models.IntegerField(default=0)),
                ("escalations_to_human", models.IntegerField(default=0)),
                ("average_response_time", models.FloatField(default=0.0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_training", models.BooleanField(default=False)),
                ("last_trained", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chatbots",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Advanced Chatbot",
                "verbose_name_plural": "Advanced Chatbots",
                "unique_together": {("organization", "name")},
            },
        ),
        migrations.CreateModel(
            name="AIPoweredAutomation",
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
                ("name", models.CharField(max_length=255)),
                (
                    "automation_type",
                    models.CharField(
                        choices=[
                            (
                                "intelligent_process_automation",
                                "Intelligent Process Automation",
                            ),
                            ("smart_document_processing", "Smart Document Processing"),
                            ("automated_decision_making", "Automated Decision Making"),
                            ("predictive_maintenance", "Predictive Maintenance"),
                            ("self_healing_systems", "Self-healing Systems"),
                            ("cognitive_automation", "Cognitive Automation"),
                            (
                                "robotic_process_automation",
                                "Robotic Process Automation",
                            ),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("trigger_conditions", models.JSONField(default=list)),
                ("automation_rules", models.JSONField(default=list)),
                ("ai_models", models.JSONField(default=list)),
                ("data_sources", models.JSONField(default=list)),
                (
                    "execution_frequency",
                    models.CharField(default="on_trigger", max_length=50),
                ),
                ("max_execution_time", models.IntegerField(default=300)),
                ("retry_attempts", models.IntegerField(default=3)),
                ("timeout_handling", models.CharField(default="fail", max_length=50)),
                ("success_rate", models.FloatField(default=0.0)),
                ("average_execution_time", models.FloatField(default=0.0)),
                (
                    "cost_savings",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                ("efficiency_improvement", models.FloatField(default=0.0)),
                ("total_executions", models.IntegerField(default=0)),
                ("successful_executions", models.IntegerField(default=0)),
                ("failed_executions", models.IntegerField(default=0)),
                ("last_execution", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_running", models.BooleanField(default=False)),
                ("last_trained", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_automations",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "AI-Powered Automation",
                "verbose_name_plural": "AI-Powered Automations",
                "unique_together": {("organization", "name", "automation_type")},
            },
        ),
        migrations.CreateModel(
            name="AIProcessingJob",
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
                    "job_type",
                    models.CharField(
                        choices=[
                            ("nlp_processing", "NLP Processing"),
                            ("vision_processing", "Vision Processing"),
                            ("prediction", "Prediction"),
                            ("chatbot_response", "Chatbot Response"),
                            ("automation_execution", "Automation Execution"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("input_data", models.JSONField(default=dict)),
                ("input_files", models.JSONField(default=list)),
                ("ai_model_id", models.CharField(blank=True, max_length=255)),
                ("processing_started", models.DateTimeField(blank=True, null=True)),
                ("processing_completed", models.DateTimeField(blank=True, null=True)),
                ("processing_duration", models.FloatField(default=0.0)),
                ("output_data", models.JSONField(default=dict)),
                ("output_files", models.JSONField(default=list)),
                ("confidence_score", models.FloatField(default=0.0)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_jobs",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "AI Processing Job",
                "verbose_name_plural": "AI Processing Jobs",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AIModelPerformance",
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
                ("model_name", models.CharField(max_length=255)),
                ("model_type", models.CharField(max_length=100)),
                ("accuracy", models.FloatField()),
                ("precision", models.FloatField()),
                ("recall", models.FloatField()),
                ("f1_score", models.FloatField()),
                ("processing_time", models.FloatField()),
                ("memory_usage", models.FloatField()),
                ("total_predictions", models.IntegerField()),
                ("successful_predictions", models.IntegerField()),
                ("failed_predictions", models.IntegerField()),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_performance",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "AI Model Performance",
                "verbose_name_plural": "AI Model Performance",
                "ordering": ["-recorded_at"],
            },
        ),
    ]
