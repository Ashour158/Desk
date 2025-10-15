"""
Workflow automation engine for helpdesk platform.
"""

import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from .models import AutomationRule, SLAPolicy, EmailTemplate
from apps.tickets.models import Ticket, TicketComment
from apps.accounts.models import User
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Main workflow automation engine."""

    def __init__(self):
        self.condition_evaluator = ConditionEvaluator()
        self.action_executor = ActionExecutor()

    def execute_rules(self, trigger_type, entity, context=None):
        """Execute automation rules for a given trigger."""
        try:
            # Get applicable rules
            rules = self.get_applicable_rules(trigger_type, entity)

            for rule in rules:
                if self.condition_evaluator.evaluate(rule.conditions, entity, context):
                    logger.info(f"Executing rule {rule.name} for {trigger_type}")
                    self.action_executor.execute(rule.actions, entity, context)

                    # Update rule usage
                    rule.usage_count += 1
                    rule.save(update_fields=["usage_count"])

        except Exception as e:
            logger.error(f"Error executing rules for {trigger_type}: {str(e)}")

    def get_applicable_rules(self, trigger_type, entity):
        """Get applicable automation rules."""
        return AutomationRule.objects.filter(
            organization=entity.organization, trigger_type=trigger_type, is_active=True
        ).order_by("execution_order")

    def test_rule(self, rule, test_entity):
        """Test a rule against a test entity."""
        try:
            if self.condition_evaluator.evaluate(rule.conditions, test_entity):
                return {
                    "success": True,
                    "message": "Rule conditions matched",
                    "actions": rule.actions,
                }
            else:
                return {"success": False, "message": "Rule conditions did not match"}
        except Exception as e:
            return {"success": False, "message": f"Error testing rule: {str(e)}"}


class ConditionEvaluator:
    """Evaluates automation rule conditions."""

    def evaluate(self, conditions, entity, context=None):
        """Evaluate conditions against entity."""
        if not conditions:
            return True

        try:
            if isinstance(conditions, str):
                conditions = json.loads(conditions)

            for condition in conditions:
                if not self.evaluate_condition(condition, entity, context):
                    return False

            return True

        except Exception as e:
            logger.error(f"Error evaluating conditions: {str(e)}")
            return False

    def evaluate_condition(self, condition, entity, context):
        """Evaluate a single condition."""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        if not field or not operator:
            return False

        # Get field value
        field_value = self.get_field_value(field, entity, context)

        # Compare values
        return self.compare_values(field_value, operator, value)

    def get_field_value(self, field, entity, context):
        """Get field value from entity or context."""
        # Handle nested fields (e.g., 'customer.email')
        if "." in field:
            parts = field.split(".")
            value = entity
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return None
            return value

        # Handle direct fields
        if hasattr(entity, field):
            return getattr(entity, field)

        # Handle context fields
        if context and field in context:
            return context[field]

        return None

    def compare_values(self, field_value, operator, expected_value):
        """Compare field value with expected value."""
        from apps.common.operators import OperatorEvaluator
        
        evaluator = OperatorEvaluator()
        return evaluator.evaluate(field_value, operator, expected_value)


class ActionExecutor:
    """Executes automation rule actions."""

    def execute(self, actions, entity, context=None):
        """Execute actions for an entity."""
        if not actions:
            return

        try:
            if isinstance(actions, str):
                actions = json.loads(actions)

            for action in actions:
                self.execute_action(action, entity, context)

        except Exception as e:
            logger.error(f"Error executing actions: {str(e)}")

    def execute_action(self, action, entity, context):
        """Execute a single action."""
        action_type = action.get("type")
        
        # Action handlers mapping
        action_handlers = {
            "assign": self.assign_entity,
            "change_status": self.change_status,
            "change_priority": self.change_priority,
            "add_tag": self.add_tag,
            "remove_tag": self.remove_tag,
            "send_email": self.send_email,
            "create_comment": self.create_comment,
            "escalate": self.escalate_entity,
            "webhook": self.trigger_webhook,
            "slack_notification": self.send_slack_notification,
            "create_ticket": self.create_ticket,
            "update_custom_field": self.update_custom_field,
            "schedule_follow_up": self.schedule_follow_up,
        }
        
        handler = action_handlers.get(action_type)
        if handler:
            if action_type in ["send_email", "webhook", "slack_notification", "create_ticket", "schedule_follow_up"]:
                handler(action, entity, context)
            else:
                handler(action, entity)
        else:
            logger.warning(f"Unknown action type: {action_type}")

    def assign_entity(self, action, entity):
        """Assign entity to user."""
        if not hasattr(entity, "assigned_agent"):
            return

        agent_id = action.get("agent_id")
        if not agent_id:
            return

        try:
            agent = User.objects.get(id=agent_id, organization=entity.organization)
            entity.assigned_agent = agent
            entity.save(update_fields=["assigned_agent"])

            logger.info(
                f"Assigned {entity.__class__.__name__} {entity.id} to {agent.full_name}"
            )

        except User.DoesNotExist:
            logger.error(f"Agent {agent_id} not found")

    def change_status(self, action, entity):
        """Change entity status."""
        if not hasattr(entity, "status"):
            return

        new_status = action.get("status")
        if not new_status:
            return

        old_status = entity.status
        entity.status = new_status

        # Handle status-specific logic
        if hasattr(entity, "first_response_at") and not entity.first_response_at:
            if new_status in ["in_progress", "pending"]:
                entity.first_response_at = timezone.now()

        if hasattr(entity, "resolved_at") and not entity.resolved_at:
            if new_status == "resolved":
                entity.resolved_at = timezone.now()

        if hasattr(entity, "closed_at") and not entity.closed_at:
            if new_status == "closed":
                entity.closed_at = timezone.now()

        entity.save()

        logger.info(
            f"Changed {entity.__class__.__name__} {entity.id} status from {old_status} to {new_status}"
        )

    def change_priority(self, action, entity):
        """Change entity priority."""
        if not hasattr(entity, "priority"):
            return

        new_priority = action.get("priority")
        if not new_priority:
            return

        old_priority = entity.priority
        entity.priority = new_priority
        entity.save(update_fields=["priority"])

        logger.info(
            f"Changed {entity.__class__.__name__} {entity.id} priority from {old_priority} to {new_priority}"
        )

    def add_tag(self, action, entity):
        """Add tag to entity."""
        if not hasattr(entity, "tags"):
            return

        tag = action.get("tag")
        if not tag:
            return

        current_tags = entity.tags or []
        if tag not in current_tags:
            current_tags.append(tag)
            entity.tags = current_tags
            entity.save(update_fields=["tags"])

            logger.info(f"Added tag '{tag}' to {entity.__class__.__name__} {entity.id}")

    def remove_tag(self, action, entity):
        """Remove tag from entity."""
        if not hasattr(entity, "tags"):
            return

        tag = action.get("tag")
        if not tag:
            return

        current_tags = entity.tags or []
        if tag in current_tags:
            current_tags.remove(tag)
            entity.tags = current_tags
            entity.save(update_fields=["tags"])

            logger.info(
                f"Removed tag '{tag}' from {entity.__class__.__name__} {entity.id}"
            )

    def send_email(self, action, entity, context):
        """Send email notification."""
        template_id = action.get("template_id")
        recipient_email = action.get("recipient_email")

        if not template_id or not recipient_email:
            return

        try:
            template = EmailTemplate.objects.get(
                id=template_id, organization=entity.organization
            )

            # Render email content
            subject = self.render_template(template.subject, entity, context)
            body_html = self.render_template(template.body_html, entity, context)
            body_text = self.render_template(template.body_text, entity, context)

            # Send email
            send_mail(
                subject=subject,
                message=body_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=body_html,
                fail_silently=False,
            )

            logger.info(
                f"Sent email to {recipient_email} for {entity.__class__.__name__} {entity.id}"
            )

        except EmailTemplate.DoesNotExist:
            logger.error(f"Email template {template_id} not found")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")

    def create_comment(self, action, entity):
        """Create comment on entity."""
        if not hasattr(entity, "comments"):
            return

        content = action.get("content")
        is_public = action.get("is_public", True)
        is_note = action.get("is_note", False)

        if not content:
            return

        try:
            # Get system user or first admin
            system_user = User.objects.filter(
                organization=entity.organization, role="admin"
            ).first()

            if not system_user:
                return

            # Render comment content
            rendered_content = self.render_template(content, entity, {})

            TicketComment.objects.create(
                ticket=entity,
                user=system_user,
                content=rendered_content,
                is_public=is_public,
                is_note=is_note,
            )

            logger.info(f"Created comment on {entity.__class__.__name__} {entity.id}")

        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")

    def escalate_entity(self, action, entity):
        """Escalate entity."""
        if not hasattr(entity, "priority"):
            return

        # Increase priority
        priority_order = ["low", "medium", "high", "urgent"]
        current_priority = entity.priority

        try:
            current_index = priority_order.index(current_priority)
            if current_index < len(priority_order) - 1:
                new_priority = priority_order[current_index + 1]
                entity.priority = new_priority
                entity.save(update_fields=["priority"])

                logger.info(
                    f"Escalated {entity.__class__.__name__} {entity.id} to {new_priority}"
                )

        except ValueError:
            logger.error(f"Invalid priority: {current_priority}")

    def trigger_webhook(self, action, entity, context):
        """Trigger webhook."""
        webhook_url = action.get("webhook_url")
        webhook_data = action.get("webhook_data", {})

        if not webhook_url:
            return

        try:
            import requests

            # Prepare webhook data
            data = {
                "entity_type": entity.__class__.__name__,
                "entity_id": str(entity.id),
                "organization_id": str(entity.organization.id),
                "timestamp": timezone.now().isoformat(),
                **webhook_data,
            }

            # Send webhook
            response = requests.post(webhook_url, json=data, timeout=30)
            response.raise_for_status()

            logger.info(
                f"Triggered webhook for {entity.__class__.__name__} {entity.id}"
            )

        except Exception as e:
            logger.error(f"Error triggering webhook: {str(e)}")

    def send_slack_notification(self, action, entity, context):
        """Send Slack notification."""
        webhook_url = action.get("webhook_url")
        message = action.get("message", "")

        if not webhook_url or not message:
            return

        try:
            import requests

            # Render message
            rendered_message = self.render_template(message, entity, context)

            # Prepare Slack payload
            payload = {
                "text": rendered_message,
                "username": "Helpdesk Bot",
                "icon_emoji": ":robot_face:",
            }

            # Send to Slack
            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()

            logger.info(
                f"Sent Slack notification for {entity.__class__.__name__} {entity.id}"
            )

        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")

    def create_ticket(self, action, entity, context):
        """Create new ticket."""
        ticket_data = action.get("ticket_data", {})

        if not ticket_data:
            return

        try:
            # Create ticket
            ticket = Ticket.objects.create(
                organization=entity.organization,
                subject=ticket_data.get("subject", "Auto-generated ticket"),
                description=ticket_data.get("description", ""),
                priority=ticket_data.get("priority", "medium"),
                channel="automation",
                customer=entity.customer if hasattr(entity, "customer") else None,
            )

            logger.info(f"Created ticket {ticket.ticket_number} from automation")

        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")

    def update_custom_field(self, action, entity):
        """Update custom field."""
        if not hasattr(entity, "custom_fields"):
            return

        field_name = action.get("field_name")
        field_value = action.get("field_value")

        if not field_name:
            return

        try:
            custom_fields = entity.custom_fields or {}
            custom_fields[field_name] = field_value
            entity.custom_fields = custom_fields
            entity.save(update_fields=["custom_fields"])

            logger.info(
                f"Updated custom field '{field_name}' for {entity.__class__.__name__} {entity.id}"
            )

        except Exception as e:
            logger.error(f"Error updating custom field: {str(e)}")

    def schedule_follow_up(self, action, entity, context):
        """Schedule follow-up task."""
        follow_up_time = action.get("follow_up_time")  # in hours
        follow_up_action = action.get("follow_up_action")

        if not follow_up_time or not follow_up_action:
            return

        try:
            from apps.tickets.tasks import schedule_follow_up_task

            # Schedule follow-up
            follow_up_datetime = timezone.now() + timedelta(hours=follow_up_time)

            schedule_follow_up_task.apply_async(
                args=[entity.id, follow_up_action], eta=follow_up_datetime
            )

            logger.info(
                f"Scheduled follow-up for {entity.__class__.__name__} {entity.id}"
            )

        except Exception as e:
            logger.error(f"Error scheduling follow-up: {str(e)}")

    def render_template(self, template, entity, context):
        """Render template with entity data."""
        try:
            # Simple template rendering
            # Replace {{field}} with entity field values
            rendered = template

            # Replace entity fields
            for field in ["id", "subject", "status", "priority", "description"]:
                if hasattr(entity, field):
                    value = getattr(entity, field)
                    rendered = rendered.replace(f"{{{{{field}}}}}", str(value))

            # Replace context variables
            if context:
                for key, value in context.items():
                    rendered = rendered.replace(f"{{{{{key}}}}}", str(value))

            return rendered

        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            return template
