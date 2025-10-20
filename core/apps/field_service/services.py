"""
Field Service automation services.
"""

from typing import Optional, Dict, Any
from django.db import transaction, models as django_models
from django.utils import timezone
from datetime import timedelta
import logging

from .models import WorkOrder, TicketToWorkOrderRule, Technician, JobAssignment

logger = logging.getLogger(__name__)


class WorkOrderAutomationService:
    """Service for automatic work order creation from tickets."""

    def __init__(self, organization):
        self.organization = organization

    @transaction.atomic
    def create_work_order_from_ticket(
        self, ticket, rule: Optional[TicketToWorkOrderRule] = None
    ) -> Optional[WorkOrder]:
        """
        Create a work order from a ticket based on rules.

        Args:
            ticket: The source ticket
            rule: Optional specific rule to apply (otherwise finds matching rule)

        Returns:
            Created WorkOrder or None if no rule matches
        """
        try:
            # Find matching rule if not provided
            if not rule:
                rule = self._find_matching_rule(ticket)

            if not rule:
                logger.info(
                    f"No matching rule found for ticket {ticket.ticket_number}"
                )
                return None

            # Check if work order already exists for this ticket
            if WorkOrder.objects.filter(source_ticket=ticket).exists():
                logger.warning(
                    f"Work order already exists for ticket {ticket.ticket_number}"
                )
                return None

            # Create work order
            work_order = self._create_work_order(ticket, rule)

            # Auto-assign technician if configured
            if rule.auto_assign:
                technician = self._find_best_technician(work_order, rule)
                if technician:
                    self._assign_technician(work_order, technician)

            # Auto-schedule if configured
            if rule.auto_schedule:
                self._schedule_work_order(work_order, rule)

            # Send notifications
            if rule.notify_customer:
                self._notify_customer(work_order, ticket)

            if rule.notify_technician and work_order.assigned_technicians:
                self._notify_technician(work_order)

            # Log the automation
            logger.info(
                f"Created work order {work_order.work_order_number} "
                f"from ticket {ticket.ticket_number} using rule {rule.name}"
            )

            return work_order

        except Exception as e:
            logger.error(
                f"Error creating work order from ticket {ticket.ticket_number}: {e}"
            )
            raise

    def _find_matching_rule(self, ticket) -> Optional[TicketToWorkOrderRule]:
        """Find the first matching rule for the ticket."""
        rules = TicketToWorkOrderRule.objects.filter(
            organization=self.organization, is_active=True
        ).order_by("-priority", "name")

        for rule in rules:
            if rule.matches_ticket(ticket):
                return rule

        return None

    def _create_work_order(self, ticket, rule: TicketToWorkOrderRule) -> WorkOrder:
        """Create the work order from ticket and rule."""
        # Get customer location if available
        customer_location = getattr(ticket, "customer_location", None)

        work_order = WorkOrder.objects.create(
            organization=self.organization,
            source_ticket=ticket,
            source="ticket",
            customer=ticket.customer,
            service_location=customer_location or {},
            work_type=rule.work_order_type,
            priority=rule.work_order_priority,
            status="draft",
            title=f"Work Order for Ticket {ticket.ticket_number}",
            description=f"Auto-generated from ticket {ticket.ticket_number}\n\nSubject: {ticket.subject}\n\n{ticket.description}",
            estimated_duration=rule.default_duration_hours * 60,  # Convert to minutes
        )

        return work_order

    def _find_best_technician(
        self, work_order: WorkOrder, rule: TicketToWorkOrderRule
    ) -> Optional[Technician]:
        """Find the best technician based on assignment logic."""
        # Get available technicians with required skills
        technicians = Technician.objects.filter(
            organization=self.organization,
            user__is_active=True,
            availability_status="available",
        )

        # Filter by required skills
        if rule.required_skills:
            # Filter technicians who have all required skills
            for skill in rule.required_skills:
                technicians = technicians.filter(
                    skills__contains=[skill]
                )

        if not technicians.exists():
            logger.warning(
                f"No available technicians found for work order {work_order.work_order_number}"
            )
            return None

        # Apply assignment logic
        if rule.assignment_logic == "nearest":
            return self._find_nearest_technician(technicians, work_order)
        elif rule.assignment_logic == "skill_match":
            return self._find_best_skill_match(technicians, work_order)
        elif rule.assignment_logic == "workload":
            return self._find_least_workload_technician(technicians)
        elif rule.assignment_logic == "round_robin":
            return self._find_round_robin_technician(technicians)

        return technicians.first()

    def _find_nearest_technician(self, technicians, work_order):
        """Find nearest technician using PostGIS distance calculation."""
        if not work_order.location_coordinates:
            return technicians.first()

        from django.contrib.gis.db.models.functions import Distance

        nearest = (
            technicians.filter(current_location__isnull=False)
            .annotate(distance=Distance("current_location", work_order.location_coordinates))
            .order_by("distance")
            .first()
        )

        return nearest or technicians.first()

    def _find_best_skill_match(self, technicians, work_order):
        """Find technician with best skill match."""
        # Score technicians based on number of skills
        scored_technicians = []

        for tech in technicians:
            skill_count = len(tech.skills) if isinstance(tech.skills, list) else 0
            scored_technicians.append((tech, skill_count))

        # Sort by skill count descending
        scored_technicians.sort(key=lambda x: x[1], reverse=True)

        return scored_technicians[0][0] if scored_technicians else None

    def _find_least_workload_technician(self, technicians):
        """Find technician with least current workload."""
        return (
            technicians.annotate(
                active_jobs=django_models.Count(
                    "job_assignments",
                    filter=django_models.Q(
                        job_assignments__status__in=["assigned", "in_progress"]
                    ),
                )
            )
            .order_by("active_jobs")
            .first()
        )

    def _find_round_robin_technician(self, technicians):
        """Find next technician in round-robin rotation."""
        # Get last assigned technician
        last_assignment = (
            JobAssignment.objects.filter(
                work_order__organization=self.organization
            )
            .order_by("-created_at")
            .first()
        )

        if not last_assignment:
            return technicians.first()

        # Find next technician after last assigned
        tech_list = list(technicians)
        try:
            last_index = tech_list.index(last_assignment.technician)
            next_index = (last_index + 1) % len(tech_list)
            return tech_list[next_index]
        except (ValueError, IndexError):
            return technicians.first()

    def _assign_technician(self, work_order: WorkOrder, technician: Technician):
        """Assign technician to work order."""
        JobAssignment.objects.create(
            work_order=work_order,
            technician=technician,
            status="assigned",
        )

        # Update work order status
        work_order.status = "assigned"
        # Add technician ID to assigned_technicians list
        if not work_order.assigned_technicians:
            work_order.assigned_technicians = []
        work_order.assigned_technicians.append(str(technician.id))
        work_order.save()

    def _schedule_work_order(self, work_order: WorkOrder, rule: TicketToWorkOrderRule):
        """Schedule the work order."""
        scheduled_time = timezone.now() + timedelta(hours=rule.schedule_offset_hours)

        work_order.scheduled_start = scheduled_time
        work_order.scheduled_end = scheduled_time + timedelta(
            minutes=work_order.estimated_duration
        )
        work_order.status = "scheduled"
        work_order.save()

    def _notify_customer(self, work_order: WorkOrder, ticket):
        """Send notification to customer."""
        try:
            from apps.notifications.tasks import send_notification

            send_notification.delay(
                organization_id=str(self.organization.id),
                user_id=str(ticket.customer.id),
                notification_type="work_order_created",
                title="Work Order Created",
                message=f"A work order has been created for your ticket {ticket.ticket_number}",
                data={
                    "ticket_id": str(ticket.id),
                    "work_order_id": str(work_order.id),
                    "work_order_number": work_order.work_order_number,
                },
            )
        except Exception as e:
            logger.error(f"Failed to send customer notification: {e}")

    def _notify_technician(self, work_order: WorkOrder):
        """Send notification to assigned technician."""
        try:
            from apps.notifications.tasks import send_notification

            # Get first assigned technician
            if work_order.assigned_technicians:
                technician_id = work_order.assigned_technicians[0]
                technician = Technician.objects.get(id=technician_id)

                send_notification.delay(
                    organization_id=str(self.organization.id),
                    user_id=str(technician.user.id),
                    notification_type="work_order_assigned",
                    title="New Work Order Assigned",
                    message=f"You have been assigned work order {work_order.work_order_number}",
                    data={
                        "work_order_id": str(work_order.id),
                        "work_order_number": work_order.work_order_number,
                        "customer_name": work_order.customer.get_full_name(),
                    },
                )
        except Exception as e:
            logger.error(f"Failed to send technician notification: {e}")

