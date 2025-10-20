"""
Admin configuration for Field Service Management.
"""

from django.contrib import admin
from .models import (
    Technician,
    WorkOrder,
    JobAssignment,
    TicketToWorkOrderRule,
)


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "employee_id",
        "availability_status",
        "total_jobs_completed",
        "average_rating",
    ]
    list_filter = ["availability_status", "organization"]
    search_fields = ["user__full_name", "user__email", "employee_id"]
    readonly_fields = [
        "total_jobs_completed",
        "average_rating",
        "on_time_percentage",
        "created_at",
        "updated_at",
    ]


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [
        "work_order_number",
        "title",
        "customer",
        "status",
        "priority",
        "work_type",
        "source",
        "created_at",
    ]
    list_filter = ["status", "priority", "work_type", "source", "organization"]
    search_fields = ["work_order_number", "title", "customer__full_name"]
    readonly_fields = ["work_order_number", "created_at", "updated_at"]
    raw_id_fields = ["customer", "source_ticket"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "organization",
                    "work_order_number",
                    "title",
                    "description",
                    "status",
                    "priority",
                    "work_type",
                )
            },
        ),
        (
            "Source Tracking",
            {"fields": ("source", "source_ticket")},
        ),
        (
            "Customer & Location",
            {
                "fields": (
                    "customer",
                    "service_location",
                    "location_coordinates",
                )
            },
        ),
        (
            "Scheduling",
            {
                "fields": (
                    "scheduled_start",
                    "scheduled_end",
                    "estimated_duration",
                    "actual_start",
                    "actual_end",
                )
            },
        ),
        (
            "Assignment",
            {"fields": ("assigned_technicians", "required_skills")},
        ),
        (
            "Parts & Cost",
            {
                "fields": (
                    "parts_required",
                    "parts_used",
                    "cost_estimate",
                    "final_cost",
                    "invoice_id",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("custom_fields", "created_at", "updated_at")},
        ),
    )


@admin.register(JobAssignment)
class JobAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "work_order",
        "technician",
        "status",
        "assigned_at",
        "customer_rating",
    ]
    list_filter = ["status"]
    search_fields = [
        "work_order__work_order_number",
        "technician__user__full_name",
    ]
    readonly_fields = ["assigned_at", "created_at", "updated_at"]


@admin.register(TicketToWorkOrderRule)
class TicketToWorkOrderRuleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "organization",
        "is_active",
        "priority",
        "auto_assign",
        "auto_schedule",
        "created_at",
    ]
    list_filter = ["is_active", "auto_assign", "auto_schedule", "assignment_logic"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "organization",
                    "name",
                    "description",
                    "is_active",
                    "priority",
                )
            },
        ),
        (
            "Trigger Conditions",
            {
                "fields": (
                    "ticket_categories",
                    "ticket_priorities",
                    "ticket_tags",
                    "customer_types",
                )
            },
        ),
        (
            "Work Order Configuration",
            {
                "fields": (
                    "work_order_type",
                    "work_order_priority",
                    "default_duration_hours",
                )
            },
        ),
        (
            "Assignment Rules",
            {"fields": ("auto_assign", "assignment_logic", "required_skills")},
        ),
        (
            "Scheduling",
            {"fields": ("auto_schedule", "schedule_offset_hours")},
        ),
        (
            "Notifications",
            {"fields": ("notify_customer", "notify_technician")},
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at", "created_by")},
        ),
    )

