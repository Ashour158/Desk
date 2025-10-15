"""
Initial migration for Enhanced Advanced Security & Compliance Suite.
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
            name="ThreatProtection",
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
                    "threat_type",
                    models.CharField(
                        choices=[
                            ("malware", "Malware"),
                            ("phishing", "Phishing"),
                            ("ddos", "DDoS"),
                            ("insider_threat", "Insider Threat"),
                            (
                                "advanced_persistent_threat",
                                "Advanced Persistent Threat",
                            ),
                            ("zero_day", "Zero Day"),
                        ],
                        max_length=50,
                    ),
                ),
                ("protection_config", models.JSONField(default=dict)),
                ("ai_detection_rules", models.JSONField(default=list)),
                ("behavioral_analytics", models.JSONField(default=dict)),
                ("threat_intelligence", models.JSONField(default=dict)),
                ("incident_response", models.JSONField(default=dict)),
                ("total_threats_detected", models.PositiveIntegerField(default=0)),
                ("threats_blocked", models.PositiveIntegerField(default=0)),
                ("false_positives", models.PositiveIntegerField(default=0)),
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
            name="SecurityManagement",
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
                    "management_type",
                    models.CharField(
                        choices=[
                            ("siem", "SIEM"),
                            ("soar", "SOAR"),
                            ("vulnerability_management", "Vulnerability Management"),
                            ("security_orchestration", "Security Orchestration"),
                            ("incident_management", "Incident Management"),
                        ],
                        max_length=50,
                    ),
                ),
                ("siem_config", models.JSONField(default=dict)),
                ("soar_config", models.JSONField(default=dict)),
                ("vulnerability_scanning", models.JSONField(default=dict)),
                ("security_policies", models.JSONField(default=list)),
                ("incident_workflows", models.JSONField(default=list)),
                ("total_incidents", models.PositiveIntegerField(default=0)),
                ("resolved_incidents", models.PositiveIntegerField(default=0)),
                (
                    "average_resolution_time",
                    models.DurationField(null=True, blank=True),
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
            name="AuthenticationAuthorization",
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
                    "auth_type",
                    models.CharField(
                        choices=[
                            ("multi_factor", "Multi-Factor Authentication"),
                            ("biometric", "Biometric Authentication"),
                            ("privileged_access", "Privileged Access Management"),
                            ("single_sign_on", "Single Sign-On"),
                            ("zero_trust", "Zero Trust Authentication"),
                        ],
                        max_length=50,
                    ),
                ),
                ("authentication_methods", models.JSONField(default=list)),
                ("authorization_rules", models.JSONField(default=list)),
                ("biometric_config", models.JSONField(default=dict)),
                ("pam_config", models.JSONField(default=dict)),
                ("zero_trust_config", models.JSONField(default=dict)),
                ("total_authentications", models.PositiveIntegerField(default=0)),
                ("successful_authentications", models.PositiveIntegerField(default=0)),
                ("failed_authentications", models.PositiveIntegerField(default=0)),
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
            name="DataProtection",
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
                    "protection_type",
                    models.CharField(
                        choices=[
                            ("data_loss_prevention", "Data Loss Prevention"),
                            ("consent_management", "Consent Management"),
                            ("data_anonymization", "Data Anonymization"),
                            ("encryption", "Encryption"),
                            ("data_classification", "Data Classification"),
                        ],
                        max_length=50,
                    ),
                ),
                ("dlp_config", models.JSONField(default=dict)),
                ("consent_management", models.JSONField(default=dict)),
                ("anonymization_rules", models.JSONField(default=list)),
                ("encryption_settings", models.JSONField(default=dict)),
                ("data_classification", models.JSONField(default=dict)),
                ("total_data_protected", models.PositiveIntegerField(default=0)),
                ("data_breaches_prevented", models.PositiveIntegerField(default=0)),
                ("compliance_score", models.FloatField(default=0.0)),
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
            name="ComplianceGovernance",
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
                    "compliance_type",
                    models.CharField(
                        choices=[
                            ("gdpr", "GDPR"),
                            ("hipaa", "HIPAA"),
                            ("sox", "SOX"),
                            ("pci_dss", "PCI DSS"),
                            ("iso_27001", "ISO 27001"),
                            ("custom", "Custom Compliance"),
                        ],
                        max_length=50,
                    ),
                ),
                ("compliance_framework", models.JSONField(default=dict)),
                ("audit_trail_config", models.JSONField(default=dict)),
                ("regulatory_requirements", models.JSONField(default=list)),
                ("compliance_monitoring", models.JSONField(default=dict)),
                ("reporting_automation", models.JSONField(default=dict)),
                ("total_audits", models.PositiveIntegerField(default=0)),
                ("compliance_score", models.FloatField(default=0.0)),
                ("last_audit", models.DateTimeField(null=True, blank=True)),
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
            name="SecurityIncident",
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
                ("incident_id", models.CharField(max_length=100, unique=True)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("critical", "Critical"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("investigating", "Investigating"),
                            ("resolved", "Resolved"),
                            ("closed", "Closed"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "threat_type",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("affected_systems", models.JSONField(default=list)),
                ("incident_data", models.JSONField(default=dict)),
                ("resolution_notes", models.TextField(null=True, blank=True)),
                ("resolved_at", models.DateTimeField(null=True, blank=True)),
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
            name="SecurityAudit",
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
                ("audit_id", models.CharField(max_length=100, unique=True)),
                (
                    "audit_type",
                    models.CharField(
                        choices=[
                            ("compliance", "Compliance Audit"),
                            ("security", "Security Audit"),
                            ("penetration_test", "Penetration Test"),
                            ("vulnerability_assessment", "Vulnerability Assessment"),
                            ("risk_assessment", "Risk Assessment"),
                        ],
                        max_length=50,
                    ),
                ),
                ("audit_scope", models.JSONField(default=dict)),
                ("audit_findings", models.JSONField(default=list)),
                ("compliance_requirements", models.JSONField(default=list)),
                ("audit_results", models.JSONField(default=dict)),
                ("recommendations", models.JSONField(default=list)),
                ("audit_score", models.FloatField(default=0.0)),
                ("audit_date", models.DateTimeField()),
                ("auditor", models.CharField(max_length=200, null=True, blank=True)),
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
            name="SecurityPolicy",
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
                    "policy_type",
                    models.CharField(
                        choices=[
                            ("access_control", "Access Control"),
                            ("data_protection", "Data Protection"),
                            ("incident_response", "Incident Response"),
                            ("password_policy", "Password Policy"),
                            ("network_security", "Network Security"),
                        ],
                        max_length=50,
                    ),
                ),
                ("policy_content", models.TextField()),
                ("policy_rules", models.JSONField(default=list)),
                ("enforcement_config", models.JSONField(default=dict)),
                ("compliance_requirements", models.JSONField(default=list)),
                ("approval_workflow", models.JSONField(default=dict)),
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
            name="SecurityMetric",
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
                            ("threat_detection", "Threat Detection"),
                            ("incident_response", "Incident Response"),
                            ("compliance", "Compliance"),
                            ("vulnerability", "Vulnerability"),
                            ("access_control", "Access Control"),
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
    ]
