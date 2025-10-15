"""
Forms for ticket system.
"""

from django import forms
from django.contrib.auth import get_user_model
from .models import Ticket, TicketComment, CannedResponse, SLAPolicy
from apps.organizations.models import Department

User = get_user_model()


class TicketForm(forms.ModelForm):
    """Form for creating and editing tickets."""

    class Meta:
        model = Ticket
        fields = [
            "subject",
            "description",
            "priority",
            "category",
            "channel",
            "assigned_agent",
            "department",
            "tags",
            "custom_fields",
        ]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Brief description of the issue",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Detailed description of the issue",
                }
            ),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "category": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Technical, Billing, General",
                }
            ),
            "channel": forms.Select(attrs={"class": "form-control"}),
            "assigned_agent": forms.Select(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-control"}),
            "tags": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Comma-separated tags"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter agents by organization
            self.fields["assigned_agent"].queryset = User.objects.filter(
                organization=user.organization, role__in=["agent", "admin"]
            )

            # Filter departments by organization
            self.fields["department"].queryset = Department.objects.filter(
                organization=user.organization, is_active=True
            )

            # Set default channel for customers
            if user.role == "customer":
                self.fields["channel"].initial = "web"
                # Remove agent assignment for customers
                self.fields.pop("assigned_agent", None)
                self.fields.pop("department", None)

    def clean_tags(self):
        """Convert comma-separated tags to list."""
        tags = self.cleaned_data.get("tags", "")
        if tags:
            return [tag.strip() for tag in tags.split(",") if tag.strip()]
        return []

    def clean_custom_fields(self):
        """Validate custom fields JSON."""
        custom_fields = self.cleaned_data.get("custom_fields", {})
        if not isinstance(custom_fields, dict):
            raise forms.ValidationError("Custom fields must be a valid JSON object")
        return custom_fields


class TicketCommentForm(forms.ModelForm):
    """Form for adding comments to tickets."""

    class Meta:
        model = TicketComment
        fields = ["content", "is_public", "is_note"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Add your comment...",
                }
            ),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_note": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Set defaults based on user role
        if user:
            if user.role == "customer":
                self.fields["is_public"].initial = True
                self.fields["is_note"].initial = False
                # Remove note option for customers
                self.fields.pop("is_note", None)
            else:
                self.fields["is_public"].initial = True
                self.fields["is_note"].initial = False


class TicketAttachmentForm(forms.ModelForm):
    """Form for uploading ticket attachments."""

    class Meta:
        model = TicketAttachment
        fields = ["file_name", "file_type", "storage_url"]
        widgets = {
            "file_name": forms.TextInput(attrs={"class": "form-control"}),
            "file_type": forms.TextInput(attrs={"class": "form-control"}),
            "storage_url": forms.URLInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields read-only as they're typically set programmatically
        for field in self.fields:
            self.fields[field].widget.attrs["readonly"] = True


class CannedResponseForm(forms.ModelForm):
    """Form for creating and editing canned responses."""

    class Meta:
        model = CannedResponse
        fields = ["title", "content", "shortcut_key", "category", "is_public"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Response title"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Response content...",
                }
            ),
            "shortcut_key": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., welcome, resolved",
                }
            ),
            "category": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., General, Technical, Billing",
                }
            ),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_shortcut_key(self):
        """Validate shortcut key uniqueness within organization."""
        shortcut_key = self.cleaned_data.get("shortcut_key")
        if shortcut_key:
            # This will be validated in the view with organization context
            pass
        return shortcut_key


class SLAPolicyForm(forms.ModelForm):
    """Form for creating and editing SLA policies."""

    class Meta:
        model = SLAPolicy
        fields = [
            "name",
            "description",
            "conditions",
            "first_response_time",
            "resolution_time",
            "operational_hours",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "conditions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "JSON conditions for this SLA policy",
                }
            ),
            "first_response_time": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Minutes"}
            ),
            "resolution_time": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Minutes"}
            ),
            "operational_hours": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "JSON business hours configuration",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_conditions(self):
        """Validate conditions JSON."""
        conditions = self.cleaned_data.get("conditions")
        if conditions:
            try:
                import json

                json.loads(conditions)
            except json.JSONDecodeError:
                raise forms.ValidationError("Conditions must be valid JSON")
        return conditions

    def clean_operational_hours(self):
        """Validate operational hours JSON."""
        operational_hours = self.cleaned_data.get("operational_hours")
        if operational_hours:
            try:
                import json

                json.loads(operational_hours)
            except json.JSONDecodeError:
                raise forms.ValidationError("Operational hours must be valid JSON")
        return operational_hours


class TicketFilterForm(forms.Form):
    """Form for filtering tickets."""

    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + Ticket.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    priority = forms.ChoiceField(
        choices=[("", "All Priorities")] + Ticket.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    channel = forms.ChoiceField(
        choices=[("", "All Channels")] + Ticket.CHANNEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    assigned_agent = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="All Agents",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search tickets..."}
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter agents by organization
            self.fields["assigned_agent"].queryset = User.objects.filter(
                organization=user.organization, role__in=["agent", "admin"]
            )


class TicketBulkActionForm(forms.Form):
    """Form for bulk actions on tickets."""

    ACTION_CHOICES = [
        ("assign", "Assign to Agent"),
        ("change_status", "Change Status"),
        ("change_priority", "Change Priority"),
        ("add_tag", "Add Tag"),
        ("remove_tag", "Remove Tag"),
        ("delete", "Delete Tickets"),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES, widget=forms.Select(attrs={"class": "form-control"})
    )
    ticket_ids = forms.CharField(widget=forms.HiddenInput())
    target_value = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    target_agent = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter agents by organization
            self.fields["target_agent"].queryset = User.objects.filter(
                organization=user.organization, role__in=["agent", "admin"]
            )
