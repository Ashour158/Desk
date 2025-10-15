"""
Forms for knowledge base system.
"""

from django import forms
from .models import KBArticle, KBCategory, KBFeedback


class KBArticleForm(forms.ModelForm):
    """Form for creating and editing knowledge base articles."""

    class Meta:
        model = KBArticle
        fields = [
            "title",
            "content",
            "summary",
            "category",
            "tags",
            "status",
            "is_featured",
            "seo_title",
            "seo_description",
            "seo_keywords",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Article title"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 15,
                    "placeholder": "Article content (Markdown supported)",
                }
            ),
            "summary": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Brief summary of the article",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "tags": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Comma-separated tags"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "seo_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "SEO title (optional)"}
            ),
            "seo_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "SEO description (optional)",
                }
            ),
            "seo_keywords": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "SEO keywords (optional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter categories by organization
            self.fields["category"].queryset = KBCategory.objects.filter(
                organization=user.organization, is_active=True
            )

            # Set default status
            if not self.instance.pk:
                self.fields["status"].initial = "draft"

    def clean_tags(self):
        """Convert comma-separated tags to list."""
        tags = self.cleaned_data.get("tags", "")
        if tags:
            return [tag.strip() for tag in tags.split(",") if tag.strip()]
        return []

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()

        # Auto-generate summary if not provided
        if not cleaned_data.get("summary") and cleaned_data.get("content"):
            content = cleaned_data["content"]
            # Extract first paragraph or first 200 characters
            summary = content.split("\n")[0][:200]
            if len(content.split("\n")[0]) > 200:
                summary += "..."
            cleaned_data["summary"] = summary

        # Auto-generate SEO title if not provided
        if not cleaned_data.get("seo_title") and cleaned_data.get("title"):
            cleaned_data["seo_title"] = cleaned_data["title"]

        # Auto-generate SEO description if not provided
        if not cleaned_data.get("seo_description") and cleaned_data.get("summary"):
            cleaned_data["seo_description"] = cleaned_data["summary"]

        return cleaned_data


class KBCategoryForm(forms.ModelForm):
    """Form for creating and editing knowledge base categories."""

    class Meta:
        model = KBCategory
        fields = ["name", "description", "parent", "sort_order", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Category name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Category description",
                }
            ),
            "parent": forms.Select(attrs={"class": "form-control"}),
            "sort_order": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sort order (lower numbers first)",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter parent categories by organization
            self.fields["parent"].queryset = KBCategory.objects.filter(
                organization=user.organization, is_active=True
            )

            # Set default sort order
            if not self.instance.pk:
                max_order = (
                    KBCategory.objects.filter(organization=user.organization).aggregate(
                        max_order=models.Max("sort_order")
                    )["max_order"]
                    or 0
                )
                self.fields["sort_order"].initial = max_order + 1

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        parent = cleaned_data.get("parent")

        # Prevent circular references
        if parent and self.instance.pk:
            if parent == self.instance:
                raise forms.ValidationError("Category cannot be its own parent")

            # Check for circular reference in hierarchy
            current = parent
            while current:
                if current == self.instance:
                    raise forms.ValidationError(
                        "Circular reference detected in category hierarchy"
                    )
                current = current.parent

        return cleaned_data


class KBFeedbackForm(forms.ModelForm):
    """Form for submitting knowledge base feedback."""

    class Meta:
        model = KBFeedback
        fields = ["feedback_type", "rating", "comment"]
        widgets = {
            "feedback_type": forms.Select(attrs={"class": "form-control"}),
            "rating": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 5,
                    "placeholder": "Rating (1-5)",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Additional comments (optional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default rating
        if not self.instance.pk:
            self.fields["rating"].initial = 5

    def clean_rating(self):
        """Validate rating value."""
        rating = self.cleaned_data.get("rating")
        if rating is not None and (rating < 1 or rating > 5):
            raise forms.ValidationError("Rating must be between 1 and 5")
        return rating


class KBSearchForm(forms.Form):
    """Form for knowledge base search."""

    query = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search knowledge base...",
                "autocomplete": "off",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=KBCategory.objects.none(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    featured_only = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter categories by organization
            self.fields["category"].queryset = KBCategory.objects.filter(
                organization=user.organization, is_active=True
            )


class KBArticleFilterForm(forms.Form):
    """Form for filtering knowledge base articles."""

    category = forms.ModelChoiceField(
        queryset=KBCategory.objects.none(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + KBArticle.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    featured = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Search articles..."}
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter categories by organization
            self.fields["category"].queryset = KBCategory.objects.filter(
                organization=user.organization, is_active=True
            )


class KBArticleBulkActionForm(forms.Form):
    """Form for bulk actions on knowledge base articles."""

    ACTION_CHOICES = [
        ("publish", "Publish Articles"),
        ("unpublish", "Unpublish Articles"),
        ("feature", "Feature Articles"),
        ("unfeature", "Unfeature Articles"),
        ("change_category", "Change Category"),
        ("delete", "Delete Articles"),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES, widget=forms.Select(attrs={"class": "form-control"})
    )
    article_ids = forms.CharField(widget=forms.HiddenInput())
    target_category = forms.ModelChoiceField(
        queryset=KBCategory.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.organization:
            # Filter categories by organization
            self.fields["target_category"].queryset = KBCategory.objects.filter(
                organization=user.organization, is_active=True
            )
