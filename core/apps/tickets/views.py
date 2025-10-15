"""
Ticket system views for helpdesk platform.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
import json

from .models import Ticket, TicketComment, TicketAttachment, CannedResponse, SLAPolicy
from .forms import TicketForm, TicketCommentForm, CannedResponseForm
from apps.accounts.models import User
from apps.organizations.models import Organization


@login_required
def ticket_list(request):
    """List all tickets for the current user/organization."""
    user = request.user
    organization = user.organization

    # Base queryset
    if user.role == "customer":
        tickets = Ticket.objects.filter(organization=organization, customer=user)
    else:
        tickets = Ticket.objects.filter(organization=organization)

    # Filtering
    status_filter = request.GET.get("status")
    priority_filter = request.GET.get("priority")
    search_query = request.GET.get("search")

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if search_query:
        tickets = tickets.filter(
            Q(subject__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(ticket_number__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(tickets.order_by("-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "tickets": page_obj,
        "status_choices": Ticket.STATUS_CHOICES,
        "priority_choices": Ticket.PRIORITY_CHOICES,
        "current_filters": {
            "status": status_filter,
            "priority": priority_filter,
            "search": search_query,
        },
    }

    return render(request, "tickets/list.html", context)


@login_required
def ticket_detail(request, ticket_id):
    """View ticket details."""
    ticket = get_object_or_404(
        Ticket, id=ticket_id, organization=request.user.organization
    )

    # Check permissions
    if request.user.role == "customer" and ticket.customer != request.user:
        return JsonResponse({"error": "Access denied"}, status=403)

    # Get comments
    comments = ticket.comments.all().order_by("created_at")

    # Get canned responses for agents
    canned_responses = []
    if request.user.role in ["agent", "admin"]:
        canned_responses = CannedResponse.objects.filter(
            organization=request.user.organization, is_public=True
        )

    context = {
        "ticket": ticket,
        "comments": comments,
        "canned_responses": canned_responses,
        "can_edit": request.user.role in ["agent", "admin"]
        or ticket.customer == request.user,
    }

    return render(request, "tickets/detail.html", context)


@login_required
def ticket_create(request):
    """Create a new ticket."""
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.organization = request.user.organization
            ticket.customer = request.user
            ticket.save()

            # Log activity
            from apps.accounts.signals import log_activity

            log_activity(
                action="create",
                entity_type="ticket",
                entity_id=ticket.id,
                old_values={},
                new_values={
                    "ticket_number": ticket.ticket_number,
                    "subject": ticket.subject,
                    "status": ticket.status,
                    "priority": ticket.priority,
                },
                changes={"created": True},
                user=request.user,
                description=f"Ticket {ticket.ticket_number} created",
            )

            return JsonResponse(
                {
                    "success": True,
                    "ticket_id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                }
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = TicketForm()
    return render(request, "tickets/create.html", {"form": form})


@login_required
@require_http_methods(["POST"])
def ticket_assign(request, ticket_id):
    """Assign ticket to agent."""
    ticket = get_object_or_404(
        Ticket, id=ticket_id, organization=request.user.organization
    )

    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    agent_id = request.POST.get("agent_id")
    if not agent_id:
        return JsonResponse({"error": "Agent ID required"}, status=400)

    try:
        agent = User.objects.get(id=agent_id, organization=request.user.organization)
        ticket.assigned_agent = agent
        ticket.save()

        # Log activity
        from apps.accounts.signals import log_activity

        log_activity(
            action="assign",
            entity_type="ticket",
            entity_id=ticket.id,
            old_values={
                "assigned_agent": (
                    str(ticket.assigned_agent) if ticket.assigned_agent else None
                )
            },
            new_values={"assigned_agent": str(agent)},
            changes={
                "assigned_agent": {"old": str(ticket.assigned_agent), "new": str(agent)}
            },
            user=request.user,
            description=f"Ticket assigned to {agent.full_name}",
        )

        return JsonResponse(
            {"success": True, "message": "Ticket assigned successfully"}
        )
    except User.DoesNotExist:
        return JsonResponse({"error": "Agent not found"}, status=404)


@login_required
@require_http_methods(["POST"])
def ticket_status_update(request, ticket_id):
    """Update ticket status."""
    ticket = get_object_or_404(
        Ticket, id=ticket_id, organization=request.user.organization
    )

    # Check permissions
    if request.user.role == "customer" and ticket.customer != request.user:
        return JsonResponse({"error": "Access denied"}, status=403)

    new_status = request.POST.get("status")
    if not new_status:
        return JsonResponse({"error": "Status required"}, status=400)

    old_status = ticket.status
    ticket.status = new_status

    # Handle status-specific logic
    if new_status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = timezone.now()
    elif new_status == "closed" and not ticket.closed_at:
        ticket.closed_at = timezone.now()
    elif (
        new_status in ["in_progress", "pending"]
        and not ticket.first_response_at
        and ticket.assigned_agent
    ):
        ticket.first_response_at = timezone.now()

    ticket.save()

    # Log activity
    from apps.accounts.signals import log_activity

    log_activity(
        action="update",
        entity_type="ticket",
        entity_id=ticket.id,
        old_values={"status": old_status},
        new_values={"status": new_status},
        changes={"status": {"old": old_status, "new": new_status}},
        user=request.user,
        description=f"Ticket status changed from {old_status} to {new_status}",
    )

    return JsonResponse({"success": True, "message": "Status updated successfully"})


@login_required
@require_http_methods(["POST"])
def ticket_comment_add(request, ticket_id):
    """Add comment to ticket."""
    ticket = get_object_or_404(
        Ticket, id=ticket_id, organization=request.user.organization
    )

    # Check permissions
    if request.user.role == "customer" and ticket.customer != request.user:
        return JsonResponse({"error": "Access denied"}, status=403)

    form = TicketCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.ticket = ticket
        comment.user = request.user
        comment.save()

        # Log activity
        from apps.accounts.signals import log_activity

        log_activity(
            action="comment",
            entity_type="ticket",
            entity_id=ticket.id,
            old_values={},
            new_values={"comment": comment.content[:100]},
            changes={"comment_added": True},
            user=request.user,
            description=f"Comment added to ticket {ticket.ticket_number}",
        )

        return JsonResponse(
            {
                "success": True,
                "comment": {
                    "id": str(comment.id),
                    "content": comment.content,
                    "user": comment.user.full_name,
                    "created_at": comment.created_at.isoformat(),
                    "is_public": comment.is_public,
                },
            }
        )
    else:
        return JsonResponse({"errors": form.errors}, status=400)


@login_required
def canned_responses(request):
    """List canned responses."""
    responses = CannedResponse.objects.filter(
        organization=request.user.organization
    ).order_by("title")

    context = {
        "responses": responses,
        "can_create": request.user.role in ["agent", "admin"],
    }

    return render(request, "tickets/canned_responses.html", context)


@login_required
@require_http_methods(["POST"])
def canned_response_create(request):
    """Create canned response."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    form = CannedResponseForm(request.POST)
    if form.is_valid():
        response = form.save(commit=False)
        response.organization = request.user.organization
        response.created_by = request.user
        response.save()

        return JsonResponse(
            {
                "success": True,
                "response": {
                    "id": str(response.id),
                    "title": response.title,
                    "content": response.content,
                    "shortcut_key": response.shortcut_key,
                },
            }
        )
    else:
        return JsonResponse({"errors": form.errors}, status=400)


@login_required
def ticket_stats(request):
    """Get ticket statistics for dashboard with optimized single query."""
    organization = request.user.organization

    # Single optimized query for all statistics
    from django.db.models import Case, When, IntegerField
    
    # Get all statistics in a single query with aggregation
    stats_data = Ticket.objects.filter(organization=organization).aggregate(
        total_tickets=Count('id'),
        open_tickets=Count('id', filter=Q(status='open')),
        resolved_tickets=Count('id', filter=Q(status='resolved')),
        closed_tickets=Count('id', filter=Q(status='closed')),
        in_progress_tickets=Count('id', filter=Q(status='in_progress')),
        pending_tickets=Count('id', filter=Q(status='pending')),
        cancelled_tickets=Count('id', filter=Q(status='cancelled')),
        high_priority_tickets=Count('id', filter=Q(priority='high')),
        medium_priority_tickets=Count('id', filter=Q(priority='medium')),
        low_priority_tickets=Count('id', filter=Q(priority='low')),
        urgent_priority_tickets=Count('id', filter=Q(priority='urgent'))
    )

    # Get status distribution in single query
    status_counts = list(
        Ticket.objects.filter(organization=organization)
        .values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    # Get priority distribution in single query
    priority_counts = list(
        Ticket.objects.filter(organization=organization)
        .values("priority")
        .annotate(count=Count("id"))
        .order_by("priority")
    )

    # Get recent tickets with optimized query
    recent_tickets = list(
        Ticket.objects.filter(organization=organization)
        .select_related('customer', 'assigned_agent')
        .order_by("-created_at")[:5]
        .values(
            'id', 'ticket_number', 'subject', 'status', 
            'priority', 'created_at', 'customer__full_name', 'assigned_agent__full_name'
        )
    )

    # Format recent tickets data
    formatted_recent_tickets = []
    for ticket in recent_tickets:
        formatted_recent_tickets.append({
            "id": str(ticket['id']),
            "ticket_number": ticket['ticket_number'],
            "subject": ticket['subject'],
            "status": ticket['status'],
            "priority": ticket['priority'],
            "created_at": ticket['created_at'].isoformat(),
            "customer_name": ticket['customer__full_name'],
            "assigned_agent_name": ticket['assigned_agent__full_name']
        })

    # Combine all statistics
    stats = {
        **stats_data,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "recent_tickets": formatted_recent_tickets,
    }

    return JsonResponse(stats)


@staff_member_required
def sla_dashboard(request):
    """SLA dashboard for administrators."""
    organization = request.user.organization

    # SLA policies
    policies = SLAPolicy.objects.filter(organization=organization, is_active=True)

    # SLA breach analysis
    breached_tickets = Ticket.objects.filter(
        organization=organization, sla_breach=True
    ).count()

    # Average response times
    tickets_with_response = Ticket.objects.filter(
        organization=organization, first_response_at__isnull=False
    )

    avg_response_time = None
    if tickets_with_response.exists():
        # Calculate average response time in hours
        response_times = []
        for ticket in tickets_with_response:
            if ticket.first_response_at:
                response_time = (
                    ticket.first_response_at - ticket.created_at
                ).total_seconds() / 3600
                response_times.append(response_time)

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)

    context = {
        "policies": policies,
        "breached_tickets": breached_tickets,
        "avg_response_time": avg_response_time,
        "total_tickets": Ticket.objects.filter(organization=organization).count(),
    }

    return render(request, "tickets/sla_dashboard.html", context)
