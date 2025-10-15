"""
Field service management views for helpdesk platform.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import WorkOrder, Technician, Asset, Inventory, ServiceReport, Route
from .forms import WorkOrderForm, TechnicianForm, AssetForm, ServiceReportForm
from apps.organizations.models import Organization


@login_required
def work_order_list(request):
    """List work orders for the current organization."""
    organization = request.user.organization

    # Base queryset
    work_orders = WorkOrder.objects.filter(organization=organization)

    # Filtering
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    technician_filter = request.GET.get("technician")
    search_query = request.GET.get("search")

    if status_filter:
        work_orders = work_orders.filter(status=status_filter)
    if priority_filter:
        work_orders = work_orders.filter(priority=priority_filter)
    if technician_filter:
        work_orders = work_orders.filter(assigned_technician_id=technician_filter)
    if search_query:
        work_orders = work_orders.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(work_order_number__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(work_orders.order_by("-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get technicians for filter
    technicians = Technician.objects.filter(organization=organization, is_active=True)

    context = {
        "work_orders": page_obj,
        "technicians": technicians,
        "status_choices": WorkOrder.STATUS_CHOICES,
        "priority_choices": WorkOrder.PRIORITY_CHOICES,
        "current_filters": {
            "status": status_filter,
            "priority": priority_filter,
            "technician": technician_filter,
            "search": search_query,
        },
    }

    return render(request, "field_service/work_order_list.html", context)


@login_required
def work_order_detail(request, work_order_id):
    """View work order details."""
    work_order = get_object_or_404(
        WorkOrder, id=work_order_id, organization=request.user.organization
    )

    # Get related data
    service_reports = work_order.service_reports.all().order_by("-created_at")
    assets = work_order.assets.all()

    context = {
        "work_order": work_order,
        "service_reports": service_reports,
        "assets": assets,
        "can_edit": request.user.role in ["agent", "admin"],
    }

    return render(request, "field_service/work_order_detail.html", context)


@login_required
def work_order_create(request):
    """Create new work order."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    if request.method == "POST":
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            work_order = form.save(commit=False)
            work_order.organization = request.user.organization
            work_order.save()

            return JsonResponse(
                {
                    "success": True,
                    "work_order_id": str(work_order.id),
                    "work_order_number": work_order.work_order_number,
                }
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = WorkOrderForm()
    return render(request, "field_service/work_order_create.html", {"form": form})


@login_required
@require_http_methods(["POST"])
def work_order_assign(request, work_order_id):
    """Assign work order to technician."""
    work_order = get_object_or_404(
        WorkOrder, id=work_order_id, organization=request.user.organization
    )

    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    technician_id = request.POST.get("technician_id")
    if not technician_id:
        return JsonResponse({"error": "Technician ID required"}, status=400)

    try:
        technician = Technician.objects.get(
            id=technician_id, organization=request.user.organization
        )
        work_order.assigned_technician = technician
        work_order.save()

        return JsonResponse(
            {"success": True, "message": "Work order assigned successfully"}
        )
    except Technician.DoesNotExist:
        return JsonResponse({"error": "Technician not found"}, status=404)


@login_required
def technician_list(request):
    """List technicians for the current organization."""
    organization = request.user.organization

    technicians = Technician.objects.filter(
        organization=organization, is_active=True
    ).order_by("user__full_name")

    # Pagination
    paginator = Paginator(technicians, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "technicians": page_obj,
        "can_manage": request.user.role in ["agent", "admin"],
    }

    return render(request, "field_service/technician_list.html", context)


@login_required
def technician_detail(request, technician_id):
    """View technician details."""
    technician = get_object_or_404(
        Technician, id=technician_id, organization=request.user.organization
    )

    # Get technician's work orders
    work_orders = WorkOrder.objects.filter(assigned_technician=technician).order_by(
        "-created_at"
    )[:10]

    # Get technician's routes
    routes = Route.objects.filter(technician=technician).order_by("-route_date")[:5]

    context = {"technician": technician, "work_orders": work_orders, "routes": routes}

    return render(request, "field_service/technician_detail.html", context)


@login_required
def technician_create(request):
    """Create new technician."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    if request.method == "POST":
        form = TechnicianForm(request.POST)
        if form.is_valid():
            technician = form.save(commit=False)
            technician.organization = request.user.organization
            technician.save()

            return JsonResponse({"success": True, "technician_id": str(technician.id)})
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = TechnicianForm()
    return render(request, "field_service/technician_create.html", {"form": form})


@login_required
def asset_list(request):
    """List assets for the current organization."""
    organization = request.user.organization

    assets = Asset.objects.filter(organization=organization)

    # Filtering
    status_filter = request.GET.get("status")
    search_query = request.GET.get("search")

    if status_filter:
        assets = assets.filter(status=status_filter)
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query)
            | Q(serial_number__icontains=search_query)
            | Q(model__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(assets.order_by("-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "assets": page_obj,
        "status_choices": Asset.STATUS_CHOICES,
        "current_filters": {"status": status_filter, "search": search_query},
    }

    return render(request, "field_service/asset_list.html", context)


@login_required
def asset_detail(request, asset_id):
    """View asset details."""
    asset = get_object_or_404(
        Asset, id=asset_id, organization=request.user.organization
    )

    # Get asset's work orders
    work_orders = WorkOrder.objects.filter(assets=asset).order_by("-created_at")[:10]

    # Get asset's service reports
    service_reports = ServiceReport.objects.filter(work_order__assets=asset).order_by(
        "-created_at"
    )[:10]

    context = {
        "asset": asset,
        "work_orders": work_orders,
        "service_reports": service_reports,
    }

    return render(request, "field_service/asset_detail.html", context)


@login_required
def service_report_create(request, work_order_id):
    """Create service report for work order."""
    work_order = get_object_or_404(
        WorkOrder, id=work_order_id, organization=request.user.organization
    )

    if request.method == "POST":
        form = ServiceReportForm(request.POST)
        if form.is_valid():
            service_report = form.save(commit=False)
            service_report.work_order = work_order
            service_report.technician = work_order.assigned_technician
            service_report.save()

            # Update work order status if completed
            if service_report.status == "completed":
                work_order.status = "completed"
                work_order.completed_at = timezone.now()
                work_order.save()

            return JsonResponse(
                {"success": True, "service_report_id": str(service_report.id)}
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = ServiceReportForm()
    return render(
        request,
        "field_service/service_report_create.html",
        {"form": form, "work_order": work_order},
    )


@login_required
def route_optimization(request):
    """Route optimization dashboard."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    organization = request.user.organization

    # Get date for optimization
    date = request.GET.get("date")
    if not date:
        date = timezone.now().date()
    else:
        from datetime import datetime

        date = datetime.strptime(date, "%Y-%m-%d").date()

    # Get work orders for the date
    work_orders = WorkOrder.objects.filter(
        organization=organization, scheduled_start__date=date, status="scheduled"
    )

    # Get available technicians
    technicians = Technician.objects.filter(
        organization=organization, is_active=True, availability_status="available"
    )

    context = {"date": date, "work_orders": work_orders, "technicians": technicians}

    return render(request, "field_service/route_optimization.html", context)


@login_required
@require_http_methods(["POST"])
def optimize_routes(request):
    """Optimize routes for technicians."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    date = request.POST.get("date")
    if not date:
        return JsonResponse({"error": "Date required"}, status=400)

    try:
        from .route_optimizer import RouteOptimizer

        optimizer = RouteOptimizer()
        optimized_routes = optimizer.optimize_daily_routes(
            date, request.user.organization
        )

        return JsonResponse({"success": True, "routes": optimized_routes})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def field_service_dashboard(request):
    """Field service dashboard."""
    organization = request.user.organization

    # Get statistics
    total_work_orders = WorkOrder.objects.filter(organization=organization).count()
    open_work_orders = WorkOrder.objects.filter(
        organization=organization, status__in=["open", "scheduled", "in_progress"]
    ).count()
    completed_work_orders = WorkOrder.objects.filter(
        organization=organization, status="completed"
    ).count()

    # Get active technicians
    active_technicians = Technician.objects.filter(
        organization=organization, is_active=True
    ).count()

    # Get recent work orders
    recent_work_orders = WorkOrder.objects.filter(organization=organization).order_by(
        "-created_at"
    )[:5]

    # Get upcoming work orders
    upcoming_work_orders = WorkOrder.objects.filter(
        organization=organization,
        status="scheduled",
        scheduled_start__gte=timezone.now(),
    ).order_by("scheduled_start")[:5]

    # Get SLA metrics
    sla_breached = WorkOrder.objects.filter(
        organization=organization,
        sla_breach=True,
        status__in=["open", "scheduled", "in_progress"],
    ).count()

    stats = {
        "total_work_orders": total_work_orders,
        "open_work_orders": open_work_orders,
        "completed_work_orders": completed_work_orders,
        "active_technicians": active_technicians,
        "sla_breached": sla_breached,
        "recent_work_orders": [
            {
                "id": str(wo.id),
                "work_order_number": wo.work_order_number,
                "title": wo.title,
                "status": wo.status,
                "priority": wo.priority,
                "created_at": wo.created_at.isoformat(),
            }
            for wo in recent_work_orders
        ],
        "upcoming_work_orders": [
            {
                "id": str(wo.id),
                "work_order_number": wo.work_order_number,
                "title": wo.title,
                "scheduled_start": (
                    wo.scheduled_start.isoformat() if wo.scheduled_start else None
                ),
                "assigned_technician": (
                    wo.assigned_technician.user.full_name
                    if wo.assigned_technician
                    else None
                ),
            }
            for wo in upcoming_work_orders
        ],
    }

    return JsonResponse(stats)


@login_required
@require_http_methods(["POST"])
def update_technician_location(request, technician_id):
    """Update technician location."""
    technician = get_object_or_404(
        Technician, id=technician_id, organization=request.user.organization
    )

    latitude = request.POST.get("latitude")
    longitude = request.POST.get("longitude")

    if not latitude or not longitude:
        return JsonResponse({"error": "Latitude and longitude required"}, status=400)

    try:
        from django.contrib.gis.geos import Point

        # Update location
        point = Point(float(longitude), float(latitude))
        technician.current_location = point
        technician.last_location_update = timezone.now()
        technician.save()

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
