"""
Signal handlers for ticket-related events.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Ticket, TicketHistory
from apps.accounts.signals import log_activity


@receiver(pre_save, sender=Ticket)
def track_ticket_changes(sender, instance, **kwargs):
    """Track ticket field changes for history."""
    if instance.pk:
        try:
            old_instance = Ticket.objects.get(pk=instance.pk)
            instance._old_instance = old_instance
        except Ticket.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Ticket)
def log_ticket_changes(sender, instance, created, **kwargs):
    """Log ticket changes to history and activity log."""
    if created:
        # Log ticket creation
        TicketHistory.objects.create(
            ticket=instance,
            field_name="status",
            old_value="",
            new_value=instance.status,
            change_type="created",
        )

        log_activity(
            action="create",
            entity_type="ticket",
            entity_id=instance.id,
            old_values={},
            new_values={
                "ticket_number": instance.ticket_number,
                "subject": instance.subject,
                "status": instance.status,
                "priority": instance.priority,
            },
            changes={"created": True},
            user=instance.customer,
            description=f"Ticket {instance.ticket_number} created",
        )
    else:
        # Log ticket updates
        old_instance = getattr(instance, "_old_instance", None)
        if old_instance:
            # Track status changes
            if old_instance.status != instance.status:
                TicketHistory.objects.create(
                    ticket=instance,
                    field_name="status",
                    old_value=old_instance.status,
                    new_value=instance.status,
                    change_type="status_changed",
                )

            # Track priority changes
            if old_instance.priority != instance.priority:
                TicketHistory.objects.create(
                    ticket=instance,
                    field_name="priority",
                    old_value=old_instance.priority,
                    new_value=instance.priority,
                    change_type="priority_changed",
                )

            # Track assignment changes
            if old_instance.assigned_agent != instance.assigned_agent:
                TicketHistory.objects.create(
                    ticket=instance,
                    field_name="assigned_agent",
                    old_value=(
                        str(old_instance.assigned_agent)
                        if old_instance.assigned_agent
                        else ""
                    ),
                    new_value=(
                        str(instance.assigned_agent) if instance.assigned_agent else ""
                    ),
                    change_type="assigned",
                )

            # Log activity
            changes = {}
            if old_instance.status != instance.status:
                changes["status"] = {"old": old_instance.status, "new": instance.status}
            if old_instance.priority != instance.priority:
                changes["priority"] = {
                    "old": old_instance.priority,
                    "new": instance.priority,
                }
            if old_instance.assigned_agent != instance.assigned_agent:
                changes["assigned_agent"] = {
                    "old": (
                        str(old_instance.assigned_agent)
                        if old_instance.assigned_agent
                        else None
                    ),
                    "new": (
                        str(instance.assigned_agent)
                        if instance.assigned_agent
                        else None
                    ),
                }

            if changes:
                log_activity(
                    action="update",
                    entity_type="ticket",
                    entity_id=instance.id,
                    old_values={},
                    new_values={},
                    changes=changes,
                    user=instance.assigned_agent,
                    description=f"Ticket {instance.ticket_number} updated",
                )


@receiver(post_save, sender=Ticket)
def handle_ticket_status_changes(sender, instance, created, **kwargs):
    """Handle special status change logic."""
    if not created:
        old_instance = getattr(instance, "_old_instance", None)
        if old_instance and old_instance.status != instance.status:
            # Handle resolution
            if instance.status == "resolved" and not instance.resolved_at:
                instance.resolved_at = timezone.now()
                instance.save(update_fields=["resolved_at"])

            # Handle closure
            if instance.status == "closed" and not instance.closed_at:
                instance.closed_at = timezone.now()
                instance.save(update_fields=["closed_at"])

            # Handle first response
            if (
                instance.status in ["in_progress", "pending"]
                and not instance.first_response_at
                and instance.assigned_agent
            ):
                instance.first_response_at = timezone.now()
                instance.save(update_fields=["first_response_at"])
