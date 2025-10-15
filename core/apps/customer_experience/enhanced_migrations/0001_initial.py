"""
Enhanced Customer Experience initial migration.
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
            name="CustomerIntelligence",
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
                    "intelligence_type",
                    models.CharField(
                        choices=[
                            ("customer_360", "Customer 360° View"),
                            ("behavioral_analytics", "Behavioral Analytics"),
                            ("purchase_intent", "Purchase Intent Prediction"),
                            ("lifetime_value", "Customer Lifetime Value"),
                            ("real_time_insights", "Real-time Customer Insights"),
                            ("segmentation", "Customer Segmentation"),
                            ("propensity_modeling", "Propensity Modeling"),
                            ("engagement_scoring", "Engagement Scoring"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("data_sources", models.JSONField(default=list)),
                ("integration_apis", models.JSONField(default=list)),
                ("real_time_feeds", models.JSONField(default=list)),
                (
                    "analysis_frequency",
                    models.CharField(default="daily", max_length=50),
                ),
                ("confidence_threshold", models.FloatField(default=0.8)),
                (
                    "update_frequency",
                    models.CharField(default="real_time", max_length=50),
                ),
                ("accuracy", models.FloatField(default=0.0)),
                ("precision", models.FloatField(default=0.0)),
                ("recall", models.FloatField(default=0.0)),
                ("f1_score", models.FloatField(default=0.0)),
                ("total_analyses", models.IntegerField(default=0)),
                ("successful_predictions", models.IntegerField(default=0)),
                ("insights_generated", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_processing", models.BooleanField(default=False)),
                ("last_analysis", models.DateTimeField(blank=True, null=True)),
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
                        related_name="customer_intelligence",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Intelligence",
                "verbose_name_plural": "Customer Intelligence",
                "unique_together": {("organization", "name", "intelligence_type")},
            },
        ),
        migrations.CreateModel(
            name="HyperPersonalizationEngine",
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
                    "personalization_type",
                    models.CharField(
                        choices=[
                            ("dynamic_content", "Dynamic Content Personalization"),
                            ("ai_recommendations", "AI-driven Recommendations"),
                            ("contextual_messaging", "Contextual Messaging"),
                            ("personalized_workflows", "Personalized Workflows"),
                            ("adaptive_ui", "Adaptive User Interfaces"),
                            ("behavioral_targeting", "Behavioral Targeting"),
                            (
                                "predictive_personalization",
                                "Predictive Personalization",
                            ),
                            ("real_time_personalization", "Real-time Personalization"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("target_audience", models.JSONField(default=list)),
                ("personalization_rules", models.JSONField(default=list)),
                ("content_templates", models.JSONField(default=list)),
                ("recommendation_models", models.JSONField(default=list)),
                ("ml_models", models.JSONField(default=list)),
                ("confidence_threshold", models.FloatField(default=0.7)),
                ("learning_rate", models.FloatField(default=0.01)),
                (
                    "update_frequency",
                    models.CharField(default="real_time", max_length=50),
                ),
                ("personalization_accuracy", models.FloatField(default=0.0)),
                ("engagement_improvement", models.FloatField(default=0.0)),
                ("conversion_rate", models.FloatField(default=0.0)),
                ("user_satisfaction", models.FloatField(default=0.0)),
                ("total_personalizations", models.IntegerField(default=0)),
                ("successful_personalizations", models.IntegerField(default=0)),
                ("content_views", models.IntegerField(default=0)),
                ("click_through_rate", models.FloatField(default=0.0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_learning", models.BooleanField(default=False)),
                ("last_updated", models.DateTimeField(blank=True, null=True)),
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
                        related_name="personalization_engines",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Hyper-personalization Engine",
                "verbose_name_plural": "Hyper-personalization Engines",
                "unique_together": {("organization", "name", "personalization_type")},
            },
        ),
        migrations.CreateModel(
            name="CustomerSuccessManagement",
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
                    "success_type",
                    models.CharField(
                        choices=[
                            ("onboarding_automation", "Onboarding Automation"),
                            ("adoption_tracking", "Adoption Tracking"),
                            ("success_metrics", "Success Metrics & KPIs"),
                            ("proactive_intervention", "Proactive Intervention"),
                            ("expansion_detection", "Expansion Opportunity Detection"),
                            ("health_monitoring", "Customer Health Monitoring"),
                            ("success_playbooks", "Success Playbooks"),
                            ("outcome_tracking", "Outcome Tracking"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("target_customers", models.JSONField(default=list)),
                ("success_criteria", models.JSONField(default=list)),
                ("intervention_rules", models.JSONField(default=list)),
                ("playbook_templates", models.JSONField(default=list)),
                ("automation_rules", models.JSONField(default=list)),
                ("trigger_conditions", models.JSONField(default=list)),
                ("action_sequences", models.JSONField(default=list)),
                ("escalation_paths", models.JSONField(default=list)),
                ("success_rate", models.FloatField(default=0.0)),
                ("customer_retention", models.FloatField(default=0.0)),
                ("expansion_rate", models.FloatField(default=0.0)),
                ("time_to_value", models.FloatField(default=0.0)),
                ("total_customers", models.IntegerField(default=0)),
                ("successful_onboardings", models.IntegerField(default=0)),
                ("interventions_triggered", models.IntegerField(default=0)),
                ("expansions_detected", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_monitoring", models.BooleanField(default=False)),
                ("last_monitoring", models.DateTimeField(blank=True, null=True)),
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
                        related_name="success_management",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Success Management",
                "verbose_name_plural": "Customer Success Management",
                "unique_together": {("organization", "name", "success_type")},
            },
        ),
        migrations.CreateModel(
            name="AdvancedFeedbackSystem",
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
                    "feedback_type",
                    models.CharField(
                        choices=[
                            ("multi_channel", "Multi-channel Feedback Collection"),
                            ("sentiment_analysis", "Real-time Sentiment Analysis"),
                            ("automated_surveys", "Automated Survey Distribution"),
                            ("feedback_analytics", "Feedback Analytics & Insights"),
                            (
                                "actionable_recommendations",
                                "Actionable Recommendations",
                            ),
                            ("nps_tracking", "NPS Tracking"),
                            ("csat_monitoring", "CSAT Monitoring"),
                            ("feedback_automation", "Feedback Automation"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("collection_channels", models.JSONField(default=list)),
                ("survey_templates", models.JSONField(default=list)),
                ("sentiment_models", models.JSONField(default=list)),
                ("analysis_rules", models.JSONField(default=list)),
                ("distribution_rules", models.JSONField(default=list)),
                ("analysis_automation", models.JSONField(default=list)),
                ("alert_conditions", models.JSONField(default=list)),
                ("response_automation", models.JSONField(default=list)),
                ("response_rate", models.FloatField(default=0.0)),
                ("sentiment_accuracy", models.FloatField(default=0.0)),
                ("action_completion_rate", models.FloatField(default=0.0)),
                ("customer_satisfaction", models.FloatField(default=0.0)),
                ("total_surveys", models.IntegerField(default=0)),
                ("total_responses", models.IntegerField(default=0)),
                ("sentiment_analyses", models.IntegerField(default=0)),
                ("actions_taken", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_collecting", models.BooleanField(default=False)),
                ("last_collection", models.DateTimeField(blank=True, null=True)),
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
                        related_name="feedback_systems",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Advanced Feedback System",
                "verbose_name_plural": "Advanced Feedback Systems",
                "unique_together": {("organization", "name", "feedback_type")},
            },
        ),
        migrations.CreateModel(
            name="CustomerAdvocacyPlatform",
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
                    "advocacy_type",
                    models.CharField(
                        choices=[
                            ("referral_programs", "Referral Program Management"),
                            ("testimonial_collection", "Testimonial Collection"),
                            ("case_study_generation", "Case Study Generation"),
                            ("social_proof", "Social Proof Integration"),
                            ("community_building", "Community Building Tools"),
                            ("advocate_recognition", "Advocate Recognition"),
                            ("content_amplification", "Content Amplification"),
                            ("advocacy_analytics", "Advocacy Analytics"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("program_rules", models.JSONField(default=list)),
                ("reward_systems", models.JSONField(default=list)),
                ("content_templates", models.JSONField(default=list)),
                ("social_integrations", models.JSONField(default=list)),
                ("referral_automation", models.JSONField(default=list)),
                ("content_automation", models.JSONField(default=list)),
                ("recognition_automation", models.JSONField(default=list)),
                ("analytics_automation", models.JSONField(default=list)),
                ("referral_rate", models.FloatField(default=0.0)),
                ("advocacy_score", models.FloatField(default=0.0)),
                ("community_engagement", models.FloatField(default=0.0)),
                ("content_amplification", models.FloatField(default=0.0)),
                ("total_advocates", models.IntegerField(default=0)),
                ("total_referrals", models.IntegerField(default=0)),
                ("testimonials_collected", models.IntegerField(default=0)),
                ("case_studies_generated", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_running", models.BooleanField(default=False)),
                ("last_activity", models.DateTimeField(blank=True, null=True)),
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
                        related_name="advocacy_platforms",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Advocacy Platform",
                "verbose_name_plural": "Customer Advocacy Platforms",
                "unique_together": {("organization", "name", "advocacy_type")},
            },
        ),
        migrations.CreateModel(
            name="CustomerInsight",
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
                    "insight_type",
                    models.CharField(
                        choices=[
                            ("behavioral", "Behavioral Insight"),
                            ("predictive", "Predictive Insight"),
                            ("sentiment", "Sentiment Insight"),
                            ("engagement", "Engagement Insight"),
                            ("value", "Value Insight"),
                            ("risk", "Risk Insight"),
                            ("opportunity", "Opportunity Insight"),
                            ("preference", "Preference Insight"),
                        ],
                        max_length=50,
                    ),
                ),
                ("insight_data", models.JSONField(default=dict)),
                ("confidence_score", models.FloatField(default=0.0)),
                ("source_systems", models.JSONField(default=list)),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("is_actionable", models.BooleanField(default=True)),
                ("is_processed", models.BooleanField(default=False)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="insights",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_insights",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Insight",
                "verbose_name_plural": "Customer Insights",
                "ordering": ["-generated_at"],
            },
        ),
        migrations.CreateModel(
            name="PersonalizationRule",
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
                    "rule_type",
                    models.CharField(
                        choices=[
                            ("content", "Content Rule"),
                            ("recommendation", "Recommendation Rule"),
                            ("messaging", "Messaging Rule"),
                            ("workflow", "Workflow Rule"),
                            ("ui", "UI Rule"),
                            ("targeting", "Targeting Rule"),
                            ("timing", "Timing Rule"),
                            ("channel", "Channel Rule"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("conditions", models.JSONField(default=list)),
                ("actions", models.JSONField(default=list)),
                ("priority", models.IntegerField(default=0)),
                ("target_segments", models.JSONField(default=list)),
                ("target_attributes", models.JSONField(default=list)),
                ("success_rate", models.FloatField(default=0.0)),
                ("engagement_rate", models.FloatField(default=0.0)),
                ("conversion_rate", models.FloatField(default=0.0)),
                ("is_active", models.BooleanField(default=True)),
                ("is_learning", models.BooleanField(default=False)),
                ("last_updated", models.DateTimeField(auto_now=True)),
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
                        related_name="personalization_rules",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Personalization Rule",
                "verbose_name_plural": "Personalization Rules",
                "ordering": ["-priority", "name"],
            },
        ),
        migrations.CreateModel(
            name="CustomerSegment",
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
                    "segment_type",
                    models.CharField(
                        choices=[
                            ("demographic", "Demographic"),
                            ("behavioral", "Behavioral"),
                            ("psychographic", "Psychographic"),
                            ("geographic", "Geographic"),
                            ("value_based", "Value-based"),
                            ("engagement", "Engagement"),
                            ("lifecycle", "Lifecycle"),
                            ("custom", "Custom"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("criteria", models.JSONField(default=list)),
                ("filters", models.JSONField(default=list)),
                ("segment_size", models.IntegerField(default=0)),
                ("engagement_rate", models.FloatField(default=0.0)),
                ("conversion_rate", models.FloatField(default=0.0)),
                (
                    "lifetime_value",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_auto_updating", models.BooleanField(default=False)),
                ("last_updated", models.DateTimeField(auto_now=True)),
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
                        related_name="customer_segments",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Segment",
                "verbose_name_plural": "Customer Segments",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="CustomerTouchpoint",
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
                    "touchpoint_type",
                    models.CharField(
                        choices=[
                            ("website", "Website"),
                            ("mobile_app", "Mobile App"),
                            ("email", "Email"),
                            ("phone", "Phone"),
                            ("chat", "Live Chat"),
                            ("social", "Social Media"),
                            ("in_person", "In-Person"),
                            ("support", "Support"),
                        ],
                        max_length=50,
                    ),
                ),
                ("interaction_data", models.JSONField(default=dict)),
                ("sentiment_score", models.FloatField(default=0.0)),
                ("satisfaction_score", models.FloatField(default=0.0)),
                ("occurred_at", models.DateTimeField(auto_now_add=True)),
                ("duration", models.FloatField(default=0.0)),
                ("outcome", models.CharField(blank=True, max_length=100)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="touchpoints",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="touchpoints",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Touchpoint",
                "verbose_name_plural": "Customer Touchpoints",
                "ordering": ["-occurred_at"],
            },
        ),
    ]
