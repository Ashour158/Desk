"""
API serializers for helpdesk platform.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

# Import models
from apps.accounts.models import User, UserProfile, ActivityLog
from apps.organizations.models import Organization, Department
from apps.tickets.models import (
    Ticket,
    TicketComment,
    TicketAttachment,
    CannedResponse,
    SLAPolicy,
)
from apps.knowledge_base.models import KBArticle, KBCategory, KBFeedback
from apps.field_service.models import (
    WorkOrder,
    Technician,
    Asset,
    InventoryItem,
    ServiceReport,
)
from apps.automation.models import AutomationRule, EmailTemplate, Webhook

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    full_name = serializers.CharField(source="get_full_name", read_only=True)
    is_agent = serializers.BooleanField(read_only=True)
    is_customer = serializers.BooleanField(read_only=True)
    is_technician = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "full_name",
            "role",
            "phone",
            "avatar",
            "timezone",
            "language",
            "is_verified",
            "last_active_at",
            "is_agent",
            "is_customer",
            "is_technician",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer."""

    is_subscription_active = serializers.BooleanField(read_only=True)
    can_create_user = serializers.BooleanField(read_only=True)
    can_create_ticket = serializers.BooleanField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "subscription_tier",
            "subscription_expires_at",
            "max_users",
            "max_tickets_per_month",
            "timezone",
            "language",
            "is_active",
            "is_subscription_active",
            "can_create_user",
            "can_create_ticket",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer."""

    manager_name = serializers.CharField(source="manager.full_name", read_only=True)

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "email",
            "manager",
            "manager_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TicketSerializer(serializers.ModelSerializer):
    """Ticket serializer."""

    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    assigned_agent_name = serializers.CharField(
        source="assigned_agent.full_name", read_only=True
    )
    department_name = serializers.CharField(source="department.name", read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    is_closed = serializers.BooleanField(read_only=True)
    age_in_hours = serializers.FloatField(read_only=True)
    first_response_time = serializers.FloatField(read_only=True)
    resolution_time = serializers.FloatField(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_number",
            "subject",
            "description",
            "status",
            "priority",
            "category",
            "channel",
            "customer",
            "customer_name",
            "assigned_agent",
            "assigned_agent_name",
            "department",
            "department_name",
            "parent_ticket",
            "due_date",
            "resolved_at",
            "closed_at",
            "first_response_at",
            "sla_breach",
            "satisfaction_rating",
            "satisfaction_comment",
            "tags",
            "custom_fields",
            "is_open",
            "is_closed",
            "age_in_hours",
            "first_response_time",
            "resolution_time",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "ticket_number",
            "created_at",
            "updated_at",
            "resolved_at",
            "closed_at",
            "first_response_at",
        ]

    def get_comments_count(self, obj):
        """Get number of comments."""
        return obj.comments.count()


class TicketCommentSerializer(serializers.ModelSerializer):
    """Ticket comment serializer."""

    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = TicketComment
        fields = [
            "id",
            "ticket",
            "user",
            "user_name",
            "user_email",
            "content",
            "is_public",
            "is_note",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Ticket attachment serializer."""

    uploaded_by_name = serializers.CharField(
        source="uploaded_by.full_name", read_only=True
    )
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachment
        fields = [
            "id",
            "ticket",
            "comment",
            "uploaded_by",
            "uploaded_by_name",
            "file_name",
            "file_size",
            "file_size_mb",
            "file_type",
            "storage_url",
            "created_at",
        ]
        read_only_fields = ["id", "uploaded_by", "created_at"]

    def get_file_size_mb(self, obj):
        """Get file size in MB."""
        return round(obj.file_size / (1024 * 1024), 2)


class KBCategorySerializer(serializers.ModelSerializer):
    """Knowledge base category serializer."""

    full_path = serializers.CharField(read_only=True)
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = KBCategory
        fields = [
            "id",
            "name",
            "description",
            "parent",
            "slug",
            "icon",
            "sort_order",
            "is_active",
            "full_path",
            "articles_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_articles_count(self, obj):
        """Get number of articles in category."""
        return obj.articles.filter(status="published").count()


class KBArticleSerializer(serializers.ModelSerializer):
    """Knowledge base article serializer."""

    author_name = serializers.CharField(source="author.full_name", read_only=True)
    last_modified_by_name = serializers.CharField(
        source="last_modified_by.full_name", read_only=True
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    helpful_percentage = serializers.FloatField(read_only=True)
    view_count_today = serializers.IntegerField(read_only=True)

    class Meta:
        model = KBArticle
        fields = [
            "id",
            "title",
            "content",
            "summary",
            "category",
            "category_name",
            "tags",
            "status",
            "is_featured",
            "is_public",
            "author",
            "author_name",
            "version",
            "last_modified_by",
            "last_modified_by_name",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "views_count",
            "helpful_count",
            "not_helpful_count",
            "is_published",
            "helpful_percentage",
            "view_count_today",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "version",
            "views_count",
            "helpful_count",
            "not_helpful_count",
            "published_at",
            "created_at",
            "updated_at",
        ]


class WorkOrderSerializer(serializers.ModelSerializer):
    """Work order serializer."""

    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    duration_minutes = serializers.FloatField(read_only=True)
    assigned_technicians_names = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "work_order_number",
            "title",
            "description",
            "status",
            "priority",
            "work_type",
            "customer",
            "customer_name",
            "service_location",
            "location_coordinates",
            "scheduled_start",
            "scheduled_end",
            "estimated_duration",
            "actual_start",
            "actual_end",
            "assigned_technicians",
            "assigned_technicians_names",
            "required_skills",
            "parts_required",
            "parts_used",
            "cost_estimate",
            "final_cost",
            "invoice_id",
            "custom_fields",
            "is_active",
            "is_completed",
            "duration_minutes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "work_order_number",
            "actual_start",
            "actual_end",
            "created_at",
            "updated_at",
        ]

    def get_assigned_technicians_names(self, obj):
        """Get names of assigned technicians."""
        if not obj.assigned_technicians:
            return []

        technicians = Technician.objects.filter(
            id__in=obj.assigned_technicians, organization=obj.organization
        )
        return [tech.user.full_name for tech in technicians]


class TechnicianSerializer(serializers.ModelSerializer):
    """Technician serializer."""

    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    current_jobs_count = serializers.IntegerField(read_only=True)
    can_take_more_jobs = serializers.BooleanField(read_only=True)

    class Meta:
        model = Technician
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "employee_id",
            "skills",
            "certifications",
            "experience_years",
            "current_location",
            "availability_status",
            "working_hours",
            "max_jobs_per_day",
            "tools_assigned",
            "vehicle_info",
            "total_jobs_completed",
            "average_rating",
            "on_time_percentage",
            "is_available",
            "current_jobs_count",
            "can_take_more_jobs",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "total_jobs_completed",
            "average_rating",
            "on_time_percentage",
            "created_at",
            "updated_at",
        ]


class AssetSerializer(serializers.ModelSerializer):
    """Asset serializer."""

    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    is_under_warranty = serializers.BooleanField(read_only=True)
    is_due_for_service = serializers.BooleanField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id",
            "customer",
            "customer_name",
            "asset_type",
            "name",
            "model",
            "serial_number",
            "manufacturer",
            "location",
            "status",
            "installation_date",
            "warranty_expiry",
            "last_service_date",
            "next_service_date",
            "maintenance_schedule",
            "service_history",
            "custom_fields",
            "is_under_warranty",
            "is_due_for_service",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryItemSerializer(serializers.ModelSerializer):
    """Inventory item serializer."""

    is_low_stock = serializers.BooleanField(read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "item_name",
            "sku",
            "description",
            "category",
            "quantity_on_hand",
            "reorder_level",
            "max_stock_level",
            "unit_cost",
            "selling_price",
            "supplier",
            "supplier_sku",
            "supplier_contact",
            "warehouse_location",
            "bin_location",
            "is_active",
            "is_tracked",
            "is_low_stock",
            "needs_reorder",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ServiceReportSerializer(serializers.ModelSerializer):
    """Service report serializer."""

    technician_name = serializers.CharField(
        source="technician.user.full_name", read_only=True
    )

    class Meta:
        model = ServiceReport
        fields = [
            "id",
            "work_order",
            "technician",
            "technician_name",
            "work_performed",
            "parts_used",
            "labor_hours",
            "customer_signature",
            "customer_feedback",
            "customer_rating",
            "photos",
            "documents",
            "reported_issues",
            "recommendations",
            "follow_up_required",
            "follow_up_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AutomationRuleSerializer(serializers.ModelSerializer):
    """Automation rule serializer."""

    class Meta:
        model = AutomationRule
        fields = [
            "id",
            "name",
            "description",
            "trigger_type",
            "trigger_conditions",
            "actions",
            "execution_order",
            "is_active",
            "stop_on_match",
            "execution_count",
            "last_executed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "execution_count",
            "last_executed",
            "created_at",
            "updated_at",
        ]


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Email template serializer."""

    class Meta:
        model = EmailTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "subject",
            "body_html",
            "body_text",
            "variables",
            "is_active",
            "is_system",
            "usage_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "usage_count", "created_at", "updated_at"]


class WebhookSerializer(serializers.ModelSerializer):
    """Webhook serializer."""

    class Meta:
        model = Webhook
        fields = [
            "id",
            "name",
            "url",
            "events",
            "is_active",
            "retry_count",
            "timeout_seconds",
            "success_count",
            "failure_count",
            "last_triggered",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "success_count",
            "failure_count",
            "last_triggered",
            "created_at",
            "updated_at",
        ]


class ActivityLogSerializer(serializers.ModelSerializer):
    """Activity log serializer."""

    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "organization",
            "user",
            "user_name",
            "action",
            "entity_type",
            "entity_id",
            "old_values",
            "new_values",
            "changes",
            "ip_address",
            "user_agent",
            "request_path",
            "request_method",
            "timestamp",
            "description",
        ]
        read_only_fields = ["id", "timestamp"]


class AnalyticsSerializer(serializers.Serializer):
    """Analytics serializer."""

    # This is a dynamic serializer for analytics data
    pass
