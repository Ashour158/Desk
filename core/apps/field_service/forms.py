"""
Forms for field service management.
"""

from django import forms
from django.contrib.gis.forms import PointField
from .models import WorkOrder, Technician, Asset, ServiceReport, Inventory
from apps.accounts.models import User
from apps.organizations.models import Organization


class WorkOrderForm(forms.ModelForm):
    """Form for creating and editing work orders."""

    class Meta:
        model = WorkOrder
        fields = [
            "title",
            "description",
            "work_order_type",
            "priority",
            "status",
            "customer",
            "assigned_technician",
            "scheduled_start",
            "scheduled_end",
            "location",
            "estimated_duration",
            "estimated_cost",
            "tags",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Work order title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Detailed description of the work",
                }
            ),
            "work_order_type": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "customer": forms.Select(attrs={"class": "form-control"}),
            "assigned_technician": forms.Select(attrs={"class": "form-control"}),
            "scheduled_start": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "scheduled_end": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "estimated_duration": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Duration in minutes"}
            ),
            "estimated_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Estimated cost",
                }
            ),
            "tags": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Comma-separated tags"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter customers by organization
            self.fields["customer"].queryset = User.objects.filter(
                organization=user.organization, role="customer"
            )

            # Filter technicians by organization
            self.fields["assigned_technician"].queryset = Technician.objects.filter(
                organization=user.organization, is_active=True
            )

            # Set default status
            if not self.instance.pk:
                self.fields["status"].initial = "open"

    def clean_tags(self):
        """Convert comma-separated tags to list."""
        tags = self.cleaned_data.get("tags", "")
        if tags:
            return [tag.strip() for tag in tags.split(",") if tag.strip()]
        return []

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        scheduled_start = cleaned_data.get("scheduled_start")
        scheduled_end = cleaned_data.get("scheduled_end")

        if scheduled_start and scheduled_end:
            if scheduled_start >= scheduled_end:
                raise forms.ValidationError(
                    "Scheduled start must be before scheduled end"
                )

        return cleaned_data


class TechnicianForm(forms.ModelForm):
    """Form for creating and editing technicians."""

    class Meta:
        model = Technician
        fields = [
            "user",
            "employee_id",
            "skills",
            "certifications",
            "availability_status",
            "hourly_rate",
            "max_daily_hours",
            "service_areas",
            "is_active",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "employee_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Employee ID"}
            ),
            "skills": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "List of skills (one per line)",
                }
            ),
            "certifications": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Certifications (JSON format)",
                }
            ),
            "availability_status": forms.Select(attrs={"class": "form-control"}),
            "hourly_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Hourly rate",
                }
            ),
            "max_daily_hours": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Maximum daily hours"}
            ),
            "service_areas": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Service areas (JSON format)",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter users by organization
            self.fields["user"].queryset = User.objects.filter(
                organization=user.organization, role__in=["agent", "admin"]
            )

            # Set default availability status
            if not self.instance.pk:
                self.fields["availability_status"].initial = "available"

    def clean_skills(self):
        """Convert skills to list."""
        skills = self.cleaned_data.get("skills", "")
        if skills:
            return [skill.strip() for skill in skills.split("\n") if skill.strip()]
        return []

    def clean_certifications(self):
        """Validate certifications JSON."""
        certifications = self.cleaned_data.get("certifications", "")
        if certifications:
            try:
                import json

                json.loads(certifications)
            except json.JSONDecodeError:
                raise forms.ValidationError("Certifications must be valid JSON")
        return certifications

    def clean_service_areas(self):
        """Validate service areas JSON."""
        service_areas = self.cleaned_data.get("service_areas", "")
        if service_areas:
            try:
                import json

                json.loads(service_areas)
            except json.JSONDecodeError:
                raise forms.ValidationError("Service areas must be valid JSON")
        return service_areas


class AssetForm(forms.ModelForm):
    """Form for creating and editing assets."""

    class Meta:
        model = Asset
        fields = [
            "name",
            "asset_type",
            "model",
            "serial_number",
            "manufacturer",
            "purchase_date",
            "warranty_expiry",
            "status",
            "location",
            "customer",
            "maintenance_schedule",
            "notes",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Asset name"}
            ),
            "asset_type": forms.Select(attrs={"class": "form-control"}),
            "model": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Model number"}
            ),
            "serial_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Serial number"}
            ),
            "manufacturer": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Manufacturer"}
            ),
            "purchase_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "warranty_expiry": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "customer": forms.Select(attrs={"class": "form-control"}),
            "maintenance_schedule": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Maintenance schedule (JSON format)",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional notes",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter customers by organization
            self.fields["customer"].queryset = User.objects.filter(
                organization=user.organization, role="customer"
            )

            # Set default status
            if not self.instance.pk:
                self.fields["status"].initial = "active"

    def clean_maintenance_schedule(self):
        """Validate maintenance schedule JSON."""
        maintenance_schedule = self.cleaned_data.get("maintenance_schedule", "")
        if maintenance_schedule:
            try:
                import json

                json.loads(maintenance_schedule)
            except json.JSONDecodeError:
                raise forms.ValidationError("Maintenance schedule must be valid JSON")
        return maintenance_schedule


class ServiceReportForm(forms.ModelForm):
    """Form for creating service reports."""

    class Meta:
        model = ServiceReport
        fields = [
            "work_performed",
            "parts_used",
            "time_spent",
            "status",
            "customer_signature",
            "technician_notes",
            "customer_rating",
            "photos",
            "next_maintenance_date",
        ]
        widgets = {
            "work_performed": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Detailed description of work performed",
                }
            ),
            "parts_used": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "List of parts used (one per line)",
                }
            ),
            "time_spent": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Time spent in minutes"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "customer_signature": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Customer signature (base64 encoded)",
                }
            ),
            "technician_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Technician notes",
                }
            ),
            "customer_rating": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 5,
                    "placeholder": "Customer rating (1-5)",
                }
            ),
            "photos": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Photo URLs (one per line)",
                }
            ),
            "next_maintenance_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default status
        if not self.instance.pk:
            self.fields["status"].initial = "completed"

    def clean_parts_used(self):
        """Convert parts used to list."""
        parts_used = self.cleaned_data.get("parts_used", "")
        if parts_used:
            return [part.strip() for part in parts_used.split("\n") if part.strip()]
        return []

    def clean_photos(self):
        """Convert photos to list."""
        photos = self.cleaned_data.get("photos", "")
        if photos:
            return [photo.strip() for photo in photos.split("\n") if photo.strip()]
        return []

    def clean_customer_rating(self):
        """Validate customer rating."""
        rating = self.cleaned_data.get("customer_rating")
        if rating is not None and (rating < 1 or rating > 5):
            raise forms.ValidationError("Customer rating must be between 1 and 5")
        return rating


class InventoryForm(forms.ModelForm):
    """Form for managing inventory."""

    class Meta:
        model = Inventory
        fields = [
            "name",
            "sku",
            "description",
            "category",
            "quantity",
            "unit_cost",
            "reorder_level",
            "supplier",
            "location",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Item name"}
            ),
            "sku": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "SKU"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Item description",
                }
            ),
            "category": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Category"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Quantity"}
            ),
            "unit_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Unit cost",
                }
            ),
            "reorder_level": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Reorder level"}
            ),
            "supplier": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Supplier"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Storage location"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Set default quantity
            if not self.instance.pk:
                self.fields["quantity"].initial = 0


class WorkOrderFilterForm(forms.Form):
    """Form for filtering work orders."""

    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + WorkOrder.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    priority = forms.ChoiceField(
        choices=[("", "All Priorities")] + WorkOrder.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    work_order_type = forms.ChoiceField(
        choices=[("", "All Types")] + WorkOrder.WORK_ORDER_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    assigned_technician = forms.ModelChoiceField(
        queryset=Technician.objects.none(),
        required=False,
        empty_label="All Technicians",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search work orders..."}
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter technicians by organization
            self.fields["assigned_technician"].queryset = Technician.objects.filter(
                organization=user.organization, is_active=True
            )


class TechnicianFilterForm(forms.Form):
    """Form for filtering technicians."""

    availability_status = forms.ChoiceField(
        choices=[("", "All Statuses")] + Technician.AVAILABILITY_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Filter by skills..."}
        ),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search technicians..."}
        ),
    )


class AssetFilterForm(forms.Form):
    """Form for filtering assets."""

    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + Asset.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    asset_type = forms.ChoiceField(
        choices=[("", "All Types")] + Asset.ASSET_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    customer = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="All Customers",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search assets..."}
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter customers by organization
            self.fields["customer"].queryset = User.objects.filter(
                organization=user.organization, role="customer"
            )
