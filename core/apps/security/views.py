"""
Enterprise security views for helpdesk platform.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    SecurityPolicy,
    SSOConfiguration,
    DeviceTrust,
    SecurityEvent,
    ComplianceAudit,
    DataRetentionPolicy,
    APIAccessLog,
    SecurityScan,
)
from .forms import (
    SecurityPolicyForm,
    SSOConfigurationForm,
    DeviceTrustForm,
    ComplianceAuditForm,
    DataRetentionPolicyForm,
)
from apps.organizations.models import Organization


@login_required
def security_dashboard(request):
    """Security dashboard with overview metrics."""
    organization = request.user.organization

    # Security metrics
    total_events = SecurityEvent.objects.filter(organization=organization).count()
    critical_events = SecurityEvent.objects.filter(
        organization=organization, severity="critical", is_resolved=False
    ).count()

    # Recent security events
    recent_events = SecurityEvent.objects.filter(organization=organization).order_by(
        "-created_at"
    )[:10]

    # Device trust status
    trusted_devices = DeviceTrust.objects.filter(
        organization=organization, trust_level="trusted"
    ).count()

    suspicious_devices = DeviceTrust.objects.filter(
        organization=organization, trust_level="suspicious"
    ).count()

    # Compliance status
    compliance_audits = ComplianceAudit.objects.filter(
        organization=organization
    ).order_by("-audit_date")[:5]

    # API usage
    api_usage = APIAccessLog.objects.filter(
        organization=organization, timestamp__gte=timezone.now() - timedelta(days=7)
    ).count()

    context = {
        "total_events": total_events,
        "critical_events": critical_events,
        "trusted_devices": trusted_devices,
        "suspicious_devices": suspicious_devices,
        "recent_events": recent_events,
        "compliance_audits": compliance_audits,
        "api_usage": api_usage,
    }

    return render(request, "security/dashboard.html", context)


@login_required
def security_policies(request):
    """Security policies management."""
    organization = request.user.organization

    policies = SecurityPolicy.objects.filter(organization=organization).order_by(
        "policy_type", "name"
    )

    context = {"policies": policies, "can_manage": request.user.role in ["admin"]}

    return render(request, "security/policies.html", context)


@login_required
def security_policy_create(request):
    """Create new security policy."""
    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    if request.method == "POST":
        form = SecurityPolicyForm(request.POST)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.organization = request.user.organization
            policy.created_by = request.user
            policy.save()

            return JsonResponse({"success": True, "policy_id": str(policy.id)})
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = SecurityPolicyForm()
    return render(request, "security/policy_create.html", {"form": form})


@login_required
def sso_configuration(request):
    """SSO configuration management."""
    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    organization = request.user.organization

    try:
        sso_config = SSOConfiguration.objects.get(organization=organization)
    except SSOConfiguration.DoesNotExist:
        sso_config = None

    if request.method == "POST":
        form = SSOConfigurationForm(request.POST, instance=sso_config)
        if form.is_valid():
            sso_config = form.save(commit=False)
            sso_config.organization = organization
            sso_config.save()

            return JsonResponse(
                {"success": True, "message": "SSO configuration updated successfully"}
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = SSOConfigurationForm(instance=sso_config)
    context = {"sso_config": sso_config, "form": form}

    return render(request, "security/sso_configuration.html", context)


@login_required
def device_trust(request):
    """Device trust management."""
    organization = request.user.organization

    devices = DeviceTrust.objects.filter(organization=organization).order_by(
        "-last_seen"
    )

    # Filtering
    trust_level_filter = request.GET.get("trust_level")
    if trust_level_filter:
        devices = devices.filter(trust_level=trust_level_filter)

    # Pagination
    paginator = Paginator(devices, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "devices": page_obj,
        "trust_levels": DeviceTrust.TRUST_LEVELS,
        "current_filter": trust_level_filter,
    }

    return render(request, "security/device_trust.html", context)


@login_required
@require_http_methods(["POST"])
def update_device_trust(request, device_id):
    """Update device trust level."""
    device = get_object_or_404(
        DeviceTrust, id=device_id, organization=request.user.organization
    )

    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    trust_level = request.POST.get("trust_level")
    if not trust_level:
        return JsonResponse({"error": "Trust level required"}, status=400)

    device.trust_level = trust_level
    device.save()

    # Log security event
    SecurityEvent.objects.create(
        organization=request.user.organization,
        user=request.user,
        event_type="admin_action",
        title="Device Trust Updated",
        description=f"Device trust level changed to {trust_level}",
        details={
            "device_id": str(device.id),
            "old_level": device.trust_level,
            "new_level": trust_level,
        },
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    return JsonResponse(
        {"success": True, "message": "Device trust level updated successfully"}
    )


@login_required
def security_events(request):
    """Security events and alerts."""
    organization = request.user.organization

    events = SecurityEvent.objects.filter(organization=organization)

    # Filtering
    event_type_filter = request.GET.get("event_type")
    severity_filter = request.GET.get("severity")
    resolved_filter = request.GET.get("resolved")

    if event_type_filter:
        events = events.filter(event_type=event_type_filter)
    if severity_filter:
        events = events.filter(severity=severity_filter)
    if resolved_filter == "true":
        events = events.filter(is_resolved=True)
    elif resolved_filter == "false":
        events = events.filter(is_resolved=False)

    # Pagination
    paginator = Paginator(events.order_by("-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "events": page_obj,
        "event_types": SecurityEvent.EVENT_TYPES,
        "severity_levels": SecurityEvent.SEVERITY_LEVELS,
        "current_filters": {
            "event_type": event_type_filter,
            "severity": severity_filter,
            "resolved": resolved_filter,
        },
    }

    return render(request, "security/events.html", context)


@login_required
@require_http_methods(["POST"])
def resolve_security_event(request, event_id):
    """Resolve security event."""
    event = get_object_or_404(
        SecurityEvent, id=event_id, organization=request.user.organization
    )

    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    resolution_notes = request.POST.get("resolution_notes", "")

    event.is_resolved = True
    event.resolved_at = timezone.now()
    event.resolved_by = request.user
    event.resolution_notes = resolution_notes
    event.save()

    return JsonResponse(
        {"success": True, "message": "Security event resolved successfully"}
    )


@login_required
def compliance_audits(request):
    """Compliance audits management."""
    organization = request.user.organization

    audits = ComplianceAudit.objects.filter(organization=organization).order_by(
        "-audit_date"
    )

    context = {"audits": audits, "can_manage": request.user.role in ["admin"]}

    return render(request, "security/compliance_audits.html", context)


@login_required
def compliance_audit_create(request):
    """Create new compliance audit."""
    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    if request.method == "POST":
        form = ComplianceAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.organization = request.user.organization
            audit.auditor = request.user
            audit.save()

            return JsonResponse({"success": True, "audit_id": str(audit.id)})
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = ComplianceAuditForm()
    return render(request, "security/compliance_audit_create.html", {"form": form})


@login_required
def data_retention(request):
    """Data retention policies management."""
    organization = request.user.organization

    policies = DataRetentionPolicy.objects.filter(organization=organization).order_by(
        "retention_type"
    )

    context = {"policies": policies, "can_manage": request.user.role in ["admin"]}

    return render(request, "security/data_retention.html", context)


@login_required
def data_retention_create(request):
    """Create new data retention policy."""
    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    if request.method == "POST":
        form = DataRetentionPolicyForm(request.POST)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.organization = request.user.organization
            policy.save()

            return JsonResponse({"success": True, "policy_id": str(policy.id)})
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = DataRetentionPolicyForm()
    return render(request, "security/data_retention_create.html", {"form": form})


@login_required
def api_access_logs(request):
    """API access logs."""
    organization = request.user.organization

    logs = APIAccessLog.objects.filter(organization=organization)

    # Filtering
    user_filter = request.GET.get("user")
    endpoint_filter = request.GET.get("endpoint")
    status_filter = request.GET.get("status")

    if user_filter:
        logs = logs.filter(user_id=user_filter)
    if endpoint_filter:
        logs = logs.filter(endpoint__icontains=endpoint_filter)
    if status_filter:
        logs = logs.filter(status_code=status_filter)

    # Pagination
    paginator = Paginator(logs.order_by("-timestamp"), 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "logs": page_obj,
        "current_filters": {
            "user": user_filter,
            "endpoint": endpoint_filter,
            "status": status_filter,
        },
    }

    return render(request, "security/api_logs.html", context)


@login_required
def security_scans(request):
    """Security vulnerability scans."""
    organization = request.user.organization

    scans = SecurityScan.objects.filter(organization=organization).order_by(
        "-started_at"
    )

    context = {"scans": scans, "can_manage": request.user.role in ["admin"]}

    return render(request, "security/scans.html", context)


@login_required
@require_http_methods(["POST"])
def run_security_scan(request):
    """Run security scan."""
    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    scan_type = request.POST.get("scan_type")
    name = request.POST.get("name")

    if not scan_type or not name:
        return JsonResponse({"error": "Scan type and name required"}, status=400)

    # Create scan record
    scan = SecurityScan.objects.create(
        organization=request.user.organization,
        scan_type=scan_type,
        name=name,
        created_by=request.user,
    )

    # Start scan (this would trigger actual scan in production)
    from .tasks import run_security_scan_task

    run_security_scan_task.delay(scan.id)

    return JsonResponse(
        {"success": True, "scan_id": str(scan.id), "message": "Security scan started"}
    )


@login_required
def security_metrics(request):
    """Get security metrics for dashboard."""
    organization = request.user.organization

    # Time ranges
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)

    # Event metrics
    events_24h = SecurityEvent.objects.filter(
        organization=organization, created_at__gte=last_24h
    ).count()

    events_7d = SecurityEvent.objects.filter(
        organization=organization, created_at__gte=last_7d
    ).count()

    # Severity breakdown
    severity_breakdown = (
        SecurityEvent.objects.filter(organization=organization, created_at__gte=last_7d)
        .values("severity")
        .annotate(count=Count("id"))
    )

    # Device trust metrics
    device_metrics = (
        DeviceTrust.objects.filter(organization=organization)
        .values("trust_level")
        .annotate(count=Count("id"))
    )

    # API usage metrics
    api_requests_24h = APIAccessLog.objects.filter(
        organization=organization, timestamp__gte=last_24h
    ).count()

    api_requests_7d = APIAccessLog.objects.filter(
        organization=organization, timestamp__gte=last_7d
    ).count()

    # Top endpoints
    top_endpoints = (
        APIAccessLog.objects.filter(organization=organization, timestamp__gte=last_7d)
        .values("endpoint")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    metrics = {
        "events_24h": events_24h,
        "events_7d": events_7d,
        "severity_breakdown": list(severity_breakdown),
        "device_metrics": list(device_metrics),
        "api_requests_24h": api_requests_24h,
        "api_requests_7d": api_requests_7d,
        "top_endpoints": list(top_endpoints),
    }

    return JsonResponse(metrics)
