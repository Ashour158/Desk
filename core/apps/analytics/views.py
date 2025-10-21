"""
Analytics and reporting views for helpdesk platform.
"""

import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json
import csv
import io

from .models import Report, ReportTemplate, Dashboard, DashboardWidget
from apps.tickets.models import Ticket, TicketComment
from apps.field_service.models import WorkOrder, ServiceReport
from apps.accounts.models import User
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard."""
    organization = request.user.organization

    # Get dashboard widgets
    widgets = DashboardWidget.objects.filter(
        dashboard__organization=organization, is_active=True
    ).order_by("position")

    context = {
        "widgets": widgets,
        "can_manage": request.user.role in ["agent", "admin"],
    }

    return render(request, "analytics/dashboard.html", context)


@login_required
def ticket_analytics(request):
    """Ticket analytics and metrics."""
    organization = request.user.organization

    # Date range
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Base queryset
    tickets = Ticket.objects.filter(
        organization=organization,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    )

    # Basic metrics
    total_tickets = tickets.count()
    open_tickets = tickets.filter(status__in=["open", "pending", "in_progress"]).count()
    resolved_tickets = tickets.filter(status="resolved").count()
    closed_tickets = tickets.filter(status="closed").count()

    # SLA metrics
    sla_breached = tickets.filter(sla_breach=True).count()
    sla_compliance = (
        ((total_tickets - sla_breached) / total_tickets * 100)
        if total_tickets > 0
        else 100
    )

    # Response time metrics
    responded_tickets = tickets.filter(first_response_at__isnull=False)
    avg_response_time = None
    if responded_tickets.exists():
        response_times = []
        for ticket in responded_tickets:
            response_time = (
                ticket.first_response_at - ticket.created_at
            ).total_seconds() / 3600
            response_times.append(response_time)
        avg_response_time = sum(response_times) / len(response_times)

    # Resolution time metrics
    resolved_tickets_with_time = tickets.filter(resolved_at__isnull=False)
    avg_resolution_time = None
    if resolved_tickets_with_time.exists():
        resolution_times = []
        for ticket in resolved_tickets_with_time:
            resolution_time = (
                ticket.resolved_at - ticket.created_at
            ).total_seconds() / 3600
            resolution_times.append(resolution_time)
        avg_resolution_time = sum(resolution_times) / len(resolution_times)

    # Status distribution
    status_distribution = tickets.values("status").annotate(count=Count("id"))

    # Priority distribution
    priority_distribution = tickets.values("priority").annotate(count=Count("id"))

    # Channel distribution
    channel_distribution = tickets.values("channel").annotate(count=Count("id"))

    # Daily trends
    daily_trends = []
    current_date = start_date
    while current_date <= end_date:
        day_tickets = tickets.filter(created_at__date=current_date)
        daily_trends.append(
            {
                "date": current_date.isoformat(),
                "created": day_tickets.count(),
                "resolved": day_tickets.filter(resolved_at__date=current_date).count(),
            }
        )
        current_date += timedelta(days=1)

    # Top agents
    top_agents = (
        User.objects.filter(organization=organization, role__in=["agent", "admin"])
        .annotate(
            tickets_resolved=Count(
                "assigned_tickets", filter=Q(assigned_tickets__status="resolved")
            )
        )
        .order_by("-tickets_resolved")[:5]
    )

    analytics = {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
        "sla_breached": sla_breached,
        "sla_compliance": round(sla_compliance, 2),
        "avg_response_time": round(avg_response_time, 2) if avg_response_time else None,
        "avg_resolution_time": (
            round(avg_resolution_time, 2) if avg_resolution_time else None
        ),
        "status_distribution": list(status_distribution),
        "priority_distribution": list(priority_distribution),
        "channel_distribution": list(channel_distribution),
        "daily_trends": daily_trends,
        "top_agents": [
            {
                "id": str(agent.id),
                "name": agent.full_name,
                "tickets_resolved": agent.tickets_resolved,
            }
            for agent in top_agents
        ],
    }

    return JsonResponse(analytics)


@login_required
def field_service_analytics(request):
    """Field service analytics and metrics."""
    organization = request.user.organization

    # Date range
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Base queryset
    work_orders = WorkOrder.objects.filter(
        organization=organization,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    )

    # Basic metrics
    total_work_orders = work_orders.count()
    completed_work_orders = work_orders.filter(status="completed").count()
    in_progress_work_orders = work_orders.filter(status="in_progress").count()
    scheduled_work_orders = work_orders.filter(status="scheduled").count()

    # Completion rate
    completion_rate = (
        (completed_work_orders / total_work_orders * 100)
        if total_work_orders > 0
        else 0
    )

    # Average completion time
    completed_with_time = work_orders.filter(
        status="completed", completed_at__isnull=False
    )
    avg_completion_time = None
    if completed_with_time.exists():
        completion_times = []
        for wo in completed_with_time:
            completion_time = (wo.completed_at - wo.created_at).total_seconds() / 3600
            completion_times.append(completion_time)
        avg_completion_time = sum(completion_times) / len(completion_times)

    # Technician performance
    technician_performance = []
    technicians = User.objects.filter(
        organization=organization, role__in=["agent", "admin"]
    )

    for tech in technicians:
        tech_work_orders = work_orders.filter(assigned_technician__user=tech)
        tech_completed = tech_work_orders.filter(status="completed").count()
        tech_total = tech_work_orders.count()

        technician_performance.append(
            {
                "id": str(tech.id),
                "name": tech.full_name,
                "total_work_orders": tech_total,
                "completed_work_orders": tech_completed,
                "completion_rate": (
                    (tech_completed / tech_total * 100) if tech_total > 0 else 0
                ),
            }
        )

    # Work order type distribution
    type_distribution = work_orders.values("work_order_type").annotate(
        count=Count("id")
    )

    # Priority distribution
    priority_distribution = work_orders.values("priority").annotate(count=Count("id"))

    # Daily trends
    daily_trends = []
    current_date = start_date
    while current_date <= end_date:
        day_work_orders = work_orders.filter(created_at__date=current_date)
        daily_trends.append(
            {
                "date": current_date.isoformat(),
                "created": day_work_orders.count(),
                "completed": day_work_orders.filter(
                    completed_at__date=current_date
                ).count(),
            }
        )
        current_date += timedelta(days=1)

    analytics = {
        "total_work_orders": total_work_orders,
        "completed_work_orders": completed_work_orders,
        "in_progress_work_orders": in_progress_work_orders,
        "scheduled_work_orders": scheduled_work_orders,
        "completion_rate": round(completion_rate, 2),
        "avg_completion_time": (
            round(avg_completion_time, 2) if avg_completion_time else None
        ),
        "technician_performance": technician_performance,
        "type_distribution": list(type_distribution),
        "priority_distribution": list(priority_distribution),
        "daily_trends": daily_trends,
    }

    return JsonResponse(analytics)


@login_required
def customer_satisfaction_analytics(request):
    """Customer satisfaction analytics."""
    organization = request.user.organization

    # Date range
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date:
        start_date = (timezone.now() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Get service reports with ratings
    service_reports = ServiceReport.objects.filter(
        work_order__organization=organization,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        customer_rating__isnull=False,
    )

    # Rating metrics
    total_ratings = service_reports.count()
    avg_rating = service_reports.aggregate(avg_rating=Avg("customer_rating"))[
        "avg_rating"
    ]

    # Rating distribution
    rating_distribution = service_reports.values("customer_rating").annotate(
        count=Count("id")
    )

    # Top performing technicians
    top_technicians = (
        service_reports.values("technician__user__full_name")
        .annotate(avg_rating=Avg("customer_rating"), total_ratings=Count("id"))
        .order_by("-avg_rating")[:5]
    )

    # Customer feedback analysis
    feedback_analysis = {
        "total_ratings": total_ratings,
        "avg_rating": round(avg_rating, 2) if avg_rating else None,
        "rating_distribution": list(rating_distribution),
        "top_technicians": list(top_technicians),
    }

    return JsonResponse(feedback_analysis)


@login_required
def custom_report_builder(request):
    """Custom report builder interface."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    organization = request.user.organization

    # Get available report templates
    templates = ReportTemplate.objects.filter(organization=organization, is_active=True)

    # Get user's custom reports
    reports = Report.objects.filter(
        organization=organization, created_by=request.user
    ).order_by("-created_at")

    context = {"templates": templates, "reports": reports}

    return render(request, "analytics/report_builder.html", context)


@login_required
@require_http_methods(["POST"])
def create_custom_report(request):
    """Create a custom report."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    try:
        data = json.loads(request.body)

        report = Report.objects.create(
            organization=request.user.organization,
            created_by=request.user,
            name=data.get("name"),
            description=data.get("description"),
            report_type=data.get("report_type"),
            parameters=data.get("parameters", {}),
            query=data.get("query"),
            is_public=data.get("is_public", False),
        )

        return JsonResponse({"success": True, "report_id": str(report.id)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def export_report(request, report_id):
    """Export report to CSV/Excel."""
    report = get_object_or_404(
        Report, id=report_id, organization=request.user.organization
    )

    format_type = request.GET.get("format", "csv")

    if format_type == "csv":
        return export_csv_report(report)
    elif format_type == "excel":
        return export_excel_report(report)
    else:
        return JsonResponse({"error": "Invalid format"}, status=400)


def export_csv_report(report):
    """Export report as CSV."""
    try:
        # Execute report query
        # This is a simplified version - in practice, you'd need to handle SQL queries safely
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{report.name}.csv"'

        writer = csv.writer(response)

        # Add headers
        writer.writerow(["Report", "Generated", "Parameters"])
        writer.writerow(
            [report.name, timezone.now().isoformat(), str(report.parameters)]
        )

        # Add data rows (simplified)
        writer.writerow(["Data would be here based on report query"])

        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def export_excel_report(report):
    """Export report as Excel."""
    try:
        # This would require openpyxl or xlsxwriter
        # For now, return a placeholder response
        return JsonResponse({"message": "Excel export not implemented yet"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def real_time_metrics(request):
    """Get real-time metrics for dashboard."""
    organization = request.user.organization

    # Current metrics
    current_time = timezone.now()

    # Tickets created today
    tickets_today = Ticket.objects.filter(
        organization=organization, created_at__date=current_time.date()
    ).count()

    # Work orders completed today
    work_orders_completed_today = WorkOrder.objects.filter(
        organization=organization, completed_at__date=current_time.date()
    ).count()

    # Active technicians
    active_technicians = User.objects.filter(
        organization=organization,
        role__in=["agent", "admin"],
        last_activity__gte=current_time - timedelta(hours=1),
    ).count()

    # SLA breaches in last 24 hours
    sla_breaches_24h = Ticket.objects.filter(
        organization=organization,
        sla_breach=True,
        created_at__gte=current_time - timedelta(hours=24),
    ).count()

    metrics = {
        "tickets_today": tickets_today,
        "work_orders_completed_today": work_orders_completed_today,
        "active_technicians": active_technicians,
        "sla_breaches_24h": sla_breaches_24h,
        "timestamp": current_time.isoformat(),
    }

    return JsonResponse(metrics)


@login_required
def dashboard_widgets(request):
    """Get dashboard widgets data."""
    organization = request.user.organization

    widgets = DashboardWidget.objects.filter(
        dashboard__organization=organization, is_active=True
    ).order_by("position")

    widget_data = []

    for widget in widgets:
        data = {
            "id": str(widget.id),
            "title": widget.title,
            "widget_type": widget.widget_type,
            "position": widget.position,
            "size": widget.size,
            "config": widget.config,
            "data": get_widget_data(widget),
        }
        widget_data.append(data)

    return JsonResponse({"widgets": widget_data})


def get_widget_data(widget):
    """Get data for a specific widget."""
    try:
        if widget.widget_type == "ticket_stats":
            return get_ticket_stats_data(widget)
        elif widget.widget_type == "work_order_stats":
            return get_work_order_stats_data(widget)
        elif widget.widget_type == "sla_compliance":
            return get_sla_compliance_data(widget)
        elif widget.widget_type == "technician_performance":
            return get_technician_performance_data(widget)
        else:
            return {}
    except Exception as e:
        logger.error(f"Error getting widget data: {str(e)}")
        return {}


def get_ticket_stats_data(widget):
    """Get ticket statistics data."""
    organization = widget.dashboard.organization

    # Optimized single query for all ticket statistics
    from django.db.models import Count, Q
    
    stats = Ticket.objects.filter(organization=organization).aggregate(
        total_tickets=Count('id'),
        open_tickets=Count('id', filter=Q(status__in=["open", "pending", "in_progress"])),
        resolved_tickets=Count('id', filter=Q(status="resolved"))
    )
    
    total_tickets = stats['total_tickets']
    open_tickets = stats['open_tickets']
    resolved_tickets = stats['resolved_tickets']

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
    }


def get_work_order_stats_data(widget):
    """Get work order statistics data."""
    organization = widget.dashboard.organization

    total_work_orders = WorkOrder.objects.filter(organization=organization).count()
    completed_work_orders = WorkOrder.objects.filter(
        organization=organization, status="completed"
    ).count()
    in_progress_work_orders = WorkOrder.objects.filter(
        organization=organization, status="in_progress"
    ).count()

    return {
        "total_work_orders": total_work_orders,
        "completed_work_orders": completed_work_orders,
        "in_progress_work_orders": in_progress_work_orders,
    }


def get_sla_compliance_data(widget):
    """Get SLA compliance data."""
    organization = widget.dashboard.organization

    # Optimized single query for SLA compliance statistics
    from django.db.models import Count, Q
    
    sla_stats = Ticket.objects.filter(organization=organization).aggregate(
        total_tickets=Count('id'),
        breached_tickets=Count('id', filter=Q(sla_breach=True))
    )
    
    total_tickets = sla_stats['total_tickets']
    breached_tickets = sla_stats['breached_tickets']

    compliance_rate = (
        ((total_tickets - breached_tickets) / total_tickets * 100)
        if total_tickets > 0
        else 100
    )

    return {
        "total_tickets": total_tickets,
        "breached_tickets": breached_tickets,
        "compliance_rate": round(compliance_rate, 2),
    }


def get_technician_performance_data(widget):
    """Get technician performance data."""
    organization = widget.dashboard.organization

    technicians = (
        User.objects.filter(organization=organization, role__in=["agent", "admin"])
        .annotate(
            tickets_resolved=Count(
                "assigned_tickets", filter=Q(assigned_tickets__status="resolved")
            )
        )
        .order_by("-tickets_resolved")[:5]
    )

    return [
        {"name": tech.full_name, "tickets_resolved": tech.tickets_resolved}
        for tech in technicians
    ]
