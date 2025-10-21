"""
Security forms for helpdesk platform.
"""

from django import forms
from django.contrib.auth import get_user_model
from .models import (
    SecurityPolicy,
    SecurityEvent,
    SSOConfiguration,
    DeviceTrust,
    ComplianceAudit,
    DataRetentionPolicy,
)

User = get_user_model()


class SecurityPolicyForm(forms.ModelForm):
    """Form for creating and editing security policies."""

    class Meta:
        model = SecurityPolicy
        fields = ["policy_type", "name", "description", "config", "is_active"]
        widgets = {
            "policy_type": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Policy name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Policy description",
                }
            ),
            "config": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "JSON configuration",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_config(self):
        """Validate JSON configuration."""
        config = self.cleaned_data.get("config")
        if config:
            try:
                import json

                json.loads(config)
            except json.JSONDecodeError:
                raise forms.ValidationError("Configuration must be valid JSON")
        return config


class SSOConfigurationForm(forms.ModelForm):
    """Form for SSO configuration."""

    class Meta:
        model = SSOConfiguration
        fields = [
            "sso_type",
            "name",
            "client_id",
            "client_secret",
            "issuer_url",
            "metadata_url",
            "certificate",
            "attribute_mapping",
            "auto_provision",
            "sync_groups",
            "logout_url",
            "is_active",
        ]
        widgets = {
            "sso_type": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "SSO configuration name"}
            ),
            "client_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Client ID"}
            ),
            "client_secret": forms.PasswordInput(
                attrs={"class": "form-control", "placeholder": "Client Secret"}
            ),
            "issuer_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "Issuer URL"}
            ),
            "metadata_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "Metadata URL"}
            ),
            "certificate": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Certificate (PEM format)",
                }
            ),
            "attribute_mapping": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Attribute mapping (JSON)",
                }
            ),
            "auto_provision": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "sync_groups": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "logout_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "Logout URL"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_attribute_mapping(self):
        """Validate attribute mapping JSON."""
        mapping = self.cleaned_data.get("attribute_mapping")
        if mapping:
            try:
                import json

                json.loads(mapping)
            except json.JSONDecodeError:
                raise forms.ValidationError("Attribute mapping must be valid JSON")
        return mapping


class DeviceTrustForm(forms.ModelForm):
    """Form for device trust management."""

    class Meta:
        model = DeviceTrust
        fields = [
            "device_name",
            "device_type",
            "trust_level",
            "is_verified",
            "verification_method",
            "country",
            "city",
            "timezone",
        ]
        widgets = {
            "device_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Device name"}
            ),
            "device_type": forms.Select(attrs={"class": "form-control"}),
            "trust_level": forms.Select(attrs={"class": "form-control"}),
            "is_verified": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "verification_method": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Verification method"}
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Country code (e.g., US)",
                }
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City"}
            ),
            "timezone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Timezone (e.g., America/New_York)",
                }
            ),
        }


class ComplianceAuditForm(forms.ModelForm):
    """Form for compliance audits."""

    class Meta:
        model = ComplianceAudit
        fields = [
            "framework",
            "audit_type",
            "title",
            "description",
            "requirements",
            "findings",
            "recommendations",
            "audit_date",
            "due_date",
            "status",
            "score",
            "max_score",
        ]
        widgets = {
            "framework": forms.Select(attrs={"class": "form-control"}),
            "audit_type": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Audit type"}
            ),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Audit title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Audit description",
                }
            ),
            "requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Requirements (JSON)",
                }
            ),
            "findings": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Findings (JSON)",
                }
            ),
            "recommendations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Recommendations (JSON)",
                }
            ),
            "audit_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "due_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "score": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Score"}
            ),
            "max_score": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Maximum score"}
            ),
        }

    def clean_requirements(self):
        """Validate requirements JSON."""
        requirements = self.cleaned_data.get("requirements")
        if requirements:
            try:
                import json

                json.loads(requirements)
            except json.JSONDecodeError:
                raise forms.ValidationError("Requirements must be valid JSON")
        return requirements

    def clean_findings(self):
        """Validate findings JSON."""
        findings = self.cleaned_data.get("findings")
        if findings:
            try:
                import json

                json.loads(findings)
            except json.JSONDecodeError:
                raise forms.ValidationError("Findings must be valid JSON")
        return findings

    def clean_recommendations(self):
        """Validate recommendations JSON."""
        recommendations = self.cleaned_data.get("recommendations")
        if recommendations:
            try:
                import json

                json.loads(recommendations)
            except json.JSONDecodeError:
                raise forms.ValidationError("Recommendations must be valid JSON")
        return recommendations


class DataRetentionPolicyForm(forms.ModelForm):
    """Form for data retention policies."""

    class Meta:
        model = DataRetentionPolicy
        fields = [
            "retention_type",
            "name",
            "description",
            "retention_period_days",
            "archive_before_delete",
            "anonymize_personal_data",
            "legal_basis",
            "compliance_framework",
            "is_active",
        ]
        widgets = {
            "retention_type": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Policy name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Policy description",
                }
            ),
            "retention_period_days": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Retention period in days",
                }
            ),
            "archive_before_delete": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "anonymize_personal_data": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "legal_basis": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Legal basis"}
            ),
            "compliance_framework": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Compliance framework"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_retention_period_days(self):
        """Validate retention period."""
        days = self.cleaned_data.get("retention_period_days")
        if days and days < 0:
            raise forms.ValidationError("Retention period must be positive")
        return days


class SecurityEventFilterForm(forms.Form):
    """Form for filtering security events."""

    event_type = forms.ChoiceField(
        choices=[("", "All Event Types")] + SecurityEvent.EVENT_TYPES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    severity = forms.ChoiceField(
        choices=[("", "All Severities")] + SecurityEvent.SEVERITY_LEVELS,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    resolved = forms.ChoiceField(
        choices=[("", "All"), ("true", "Resolved"), ("false", "Unresolved")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    date_from = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"}
        ),
    )
    date_to = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"}
        ),
    )


class DeviceTrustFilterForm(forms.Form):
    """Form for filtering device trust."""

    trust_level = forms.ChoiceField(
        choices=[("", "All Trust Levels")] + DeviceTrust.TRUST_LEVELS,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    device_type = forms.ChoiceField(
        choices=[
            ("", "All Device Types"),
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    is_verified = forms.ChoiceField(
        choices=[("", "All"), ("true", "Verified"), ("false", "Unverified")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search devices..."}
        ),
    )


class APIAccessLogFilterForm(forms.Form):
    """Form for filtering API access logs."""

    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="All Users",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    endpoint = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Filter by endpoint..."}
        ),
    )
    status_code = forms.ChoiceField(
        choices=[
            ("", "All Status Codes"),
            ("200", "200 - OK"),
            ("400", "400 - Bad Request"),
            ("401", "401 - Unauthorized"),
            ("403", "403 - Forbidden"),
            ("404", "404 - Not Found"),
            ("500", "500 - Server Error"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    date_from = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"}
        ),
    )
    date_to = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"}
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter users by organization
            self.fields["user"].queryset = User.objects.filter(
                organization=user.organization
            )
