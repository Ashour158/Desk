"""
Initial migration for Enhanced Advanced Communication Platform.
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
            name="UnifiedCommunicationHub",
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
                            ("multi_channel", "Multi-Channel"),
                            ("real_time_collaboration", "Real-time Collaboration"),
                            ("unified_messaging", "Unified Messaging"),
                            ("presence_management", "Presence Management"),
                            ("contact_center", "Contact Center"),
                        ],
                        max_length=50,
                    ),
                ),
                ("communication_channels", models.JSONField(default=list)),
                ("collaboration_features", models.JSONField(default=dict)),
                ("presence_management", models.JSONField(default=dict)),
                ("contact_center_config", models.JSONField(default=dict)),
                ("integration_settings", models.JSONField(default=dict)),
                ("total_users", models.PositiveIntegerField(default=0)),
                ("active_sessions", models.PositiveIntegerField(default=0)),
                ("total_messages", models.PositiveIntegerField(default=0)),
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
            name="VideoAudioFeatures",
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
                    "feature_type",
                    models.CharField(
                        choices=[
                            ("hd_video_conferencing", "HD Video Conferencing"),
                            ("noise_cancellation", "Noise Cancellation"),
                            ("audio_enhancement", "Audio Enhancement"),
                            ("screen_sharing", "Screen Sharing"),
                            ("recording_capabilities", "Recording Capabilities"),
                        ],
                        max_length=50,
                    ),
                ),
                ("video_config", models.JSONField(default=dict)),
                ("audio_config", models.JSONField(default=dict)),
                ("recording_settings", models.JSONField(default=dict)),
                ("quality_settings", models.JSONField(default=dict)),
                ("accessibility_features", models.JSONField(default=dict)),
                ("total_sessions", models.PositiveIntegerField(default=0)),
                ("active_sessions", models.PositiveIntegerField(default=0)),
                ("total_recordings", models.PositiveIntegerField(default=0)),
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
            name="AIPoweredCommunication",
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
                    "ai_type",
                    models.CharField(
                        choices=[
                            ("smart_transcription", "Smart Transcription"),
                            ("real_time_translation", "Real-time Translation"),
                            ("sentiment_analysis", "Sentiment Analysis"),
                            ("intent_recognition", "Intent Recognition"),
                            ("automated_responses", "Automated Responses"),
                        ],
                        max_length=50,
                    ),
                ),
                ("transcription_config", models.JSONField(default=dict)),
                ("translation_config", models.JSONField(default=dict)),
                ("sentiment_analysis", models.JSONField(default=dict)),
                ("intent_recognition", models.JSONField(default=dict)),
                ("automated_responses", models.JSONField(default=dict)),
                ("total_transcriptions", models.PositiveIntegerField(default=0)),
                ("total_translations", models.PositiveIntegerField(default=0)),
                ("accuracy_score", models.FloatField(default=0.0)),
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
            name="SocialMediaManagement",
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
                    "platform",
                    models.CharField(
                        choices=[
                            ("facebook", "Facebook"),
                            ("twitter", "Twitter"),
                            ("linkedin", "LinkedIn"),
                            ("instagram", "Instagram"),
                            ("youtube", "YouTube"),
                            ("tiktok", "TikTok"),
                        ],
                        max_length=50,
                    ),
                ),
                ("account_config", models.JSONField(default=dict)),
                ("posting_schedule", models.JSONField(default=dict)),
                ("content_management", models.JSONField(default=dict)),
                ("engagement_analytics", models.JSONField(default=dict)),
                ("automation_rules", models.JSONField(default=list)),
                ("total_posts", models.PositiveIntegerField(default=0)),
                ("total_engagement", models.PositiveIntegerField(default=0)),
                ("follower_growth", models.IntegerField(default=0)),
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
            name="CommunicationIntelligence",
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
                            ("communication_analytics", "Communication Analytics"),
                            ("roi_measurement", "ROI Measurement"),
                            ("engagement_metrics", "Engagement Metrics"),
                            ("content_analysis", "Content Analysis"),
                            ("trend_analysis", "Trend Analysis"),
                        ],
                        max_length=50,
                    ),
                ),
                ("analytics_config", models.JSONField(default=dict)),
                ("roi_measurement", models.JSONField(default=dict)),
                ("engagement_metrics", models.JSONField(default=dict)),
                ("content_analysis", models.JSONField(default=dict)),
                ("trend_analysis", models.JSONField(default=dict)),
                ("total_analyses", models.PositiveIntegerField(default=0)),
                ("insights_generated", models.PositiveIntegerField(default=0)),
                ("roi_score", models.FloatField(default=0.0)),
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
            name="CommunicationSession",
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
                ("session_id", models.CharField(max_length=100, unique=True)),
                (
                    "session_type",
                    models.CharField(
                        choices=[
                            ("video_call", "Video Call"),
                            ("audio_call", "Audio Call"),
                            ("chat", "Chat"),
                            ("email", "Email"),
                            ("social_media", "Social Media"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        max_length=20,
                    ),
                ),
                ("participants", models.JSONField(default=list)),
                ("session_data", models.JSONField(default=dict)),
                ("start_time", models.DateTimeField(auto_now_add=True)),
                ("end_time", models.DateTimeField(null=True, blank=True)),
                ("duration", models.DurationField(null=True, blank=True)),
                ("quality_score", models.FloatField(default=0.0)),
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
            name="CommunicationMessage",
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
                    "message_type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("image", "Image"),
                            ("video", "Video"),
                            ("audio", "Audio"),
                            ("file", "File"),
                        ],
                        max_length=20,
                    ),
                ),
                ("content", models.TextField()),
                ("sender", models.CharField(max_length=200)),
                ("recipient", models.CharField(max_length=200)),
                ("message_data", models.JSONField(default=dict)),
                ("is_read", models.BooleanField(default=False)),
                ("read_at", models.DateTimeField(null=True, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organizations.organization",
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="advanced_communication.communicationsession",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CommunicationAnalytic",
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
                ("analytic_name", models.CharField(max_length=200)),
                (
                    "analytic_type",
                    models.CharField(
                        choices=[
                            ("engagement", "Engagement"),
                            ("reach", "Reach"),
                            ("sentiment", "Sentiment"),
                            ("response_time", "Response Time"),
                            ("satisfaction", "Satisfaction"),
                        ],
                        max_length=50,
                    ),
                ),
                ("metric_value", models.FloatField()),
                ("metric_unit", models.CharField(max_length=50)),
                ("target_value", models.FloatField(null=True, blank=True)),
                ("analytic_data", models.JSONField(default=dict)),
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
            name="CommunicationTemplate",
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
                            ("email", "Email"),
                            ("sms", "SMS"),
                            ("social_media", "Social Media"),
                            ("chat", "Chat"),
                            ("announcement", "Announcement"),
                        ],
                        max_length=50,
                    ),
                ),
                ("template_content", models.TextField()),
                ("template_variables", models.JSONField(default=list)),
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
    ]
