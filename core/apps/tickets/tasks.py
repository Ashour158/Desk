"""
Celery tasks for ticket system.
"""

from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import imaplib
import email
import re
import logging

from .models import Ticket, TicketComment, SLAPolicy
from apps.accounts.models import User
from apps.organizations.models import Organization
from apps.automation.models import EmailTemplate

logger = logging.getLogger(__name__)


@shared_task
def process_incoming_emails():
    """Process incoming emails and create tickets."""
    organizations = Organization.objects.filter(email_integration_enabled=True)

    for org in organizations:
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(org.imap_host, org.imap_port)
            mail.login(org.imap_user, org.imap_password)
            mail.select("inbox")

            # Search for unseen emails
            _, messages = mail.search(None, "UNSEEN")

            for msg_num in messages[0].split():
                try:
                    _, msg_data = mail.fetch(msg_num, "(RFC822)")
                    email_message = email.message_from_bytes(msg_data[0][1])

                    # Create ticket from email
                    ticket = create_ticket_from_email(email_message, org)
                    if ticket:
                        logger.info(f"Created ticket {ticket.ticket_number} from email")

                        # Send confirmation email
                        send_ticket_created_email.delay(ticket.id)

                except Exception as e:
                    logger.error(f"Error processing email {msg_num}: {str(e)}")
                    continue

            mail.close()
            mail.logout()

        except Exception as e:
            logger.error(
                f"Error processing emails for organization {org.name}: {str(e)}"
            )


def create_ticket_from_email(email_message, organization):
    """Create ticket from email message."""
    try:
        # Extract email details
        subject = email_message.get("Subject", "No Subject")
        from_email = email_message.get("From", "")
        to_email = email_message.get("To", "")

        # Get email body
        body = get_email_body(email_message)

        # Find or create customer
        customer = get_or_create_customer(from_email, organization)

        # Check if this is a reply to existing ticket
        existing_ticket = find_existing_ticket(subject, from_email, organization)

        if existing_ticket:
            # Add as comment to existing ticket
            TicketComment.objects.create(
                ticket=existing_ticket, user=customer, content=body, is_public=True
            )
            return existing_ticket
        else:
            # Create new ticket
            ticket = Ticket.objects.create(
                organization=organization,
                subject=subject,
                description=body,
                channel="email",
                customer=customer,
                priority="medium",  # Default priority
            )

            # Apply SLA policy
            apply_sla_policy(ticket)

            return ticket

    except Exception as e:
        logger.error(f"Error creating ticket from email: {str(e)}")
        return None


def get_email_body(email_message):
    """Extract email body text."""
    body = ""

    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
            elif part.get_content_type() == "text/html" and not body:
                # Fallback to HTML if no plain text
                body = part.get_payload(decode=True).decode()
    else:
        body = email_message.get_payload(decode=True).decode()

    return body


def get_or_create_customer(email_address, organization):
    """Get or create customer from email address."""
    try:
        # Try to find existing user
        user = User.objects.get(email=email_address, organization=organization)
        return user
    except User.DoesNotExist:
        # Create new customer
        username = email_address.split("@")[0]
        user = User.objects.create_user(
            email=email_address,
            username=username,
            organization=organization,
            role="customer",
            full_name=email_address.split("@")[0].replace(".", " ").title(),
        )
        return user


def find_existing_ticket(subject, from_email, organization):
    """Find existing ticket that this email might be replying to."""
    # Look for ticket number in subject
    ticket_number_match = re.search(r"#(\d+)", subject)
    if ticket_number_match:
        ticket_number = ticket_number_match.group(1)
        try:
            return Ticket.objects.get(
                organization=organization, ticket_number__icontains=ticket_number
            )
        except Ticket.DoesNotExist:
            pass

    # Look for recent tickets from same customer
    try:
        customer = User.objects.get(email=from_email, organization=organization)
        recent_ticket = (
            Ticket.objects.filter(
                organization=organization,
                customer=customer,
                created_at__gte=timezone.now() - timedelta(days=7),
            )
            .order_by("-created_at")
            .first()
        )

        if recent_ticket and recent_ticket.status in ["open", "pending", "in_progress"]:
            return recent_ticket
    except User.DoesNotExist:
        pass

    return None


def apply_sla_policy(ticket):
    """Apply SLA policy to ticket."""
    try:
        policy = SLAPolicy.objects.filter(
            organization=ticket.organization, is_active=True
        ).first()

        if policy:
            # Calculate due date based on policy
            from apps.tickets.sla import SLAManager

            sla_manager = SLAManager()
            ticket.due_date = sla_manager.calculate_due_date(ticket)
            ticket.save()
    except Exception as e:
        logger.error(f"Error applying SLA policy: {str(e)}")


@shared_task
def send_ticket_created_email(ticket_id):
    """Send ticket created confirmation email."""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        customer = ticket.customer

        # Get email template
        template = EmailTemplate.objects.filter(
            organization=ticket.organization,
            template_type="ticket_created",
            is_active=True,
        ).first()

        if template:
            # Render email content
            subject = template.subject.format(
                ticket_number=ticket.ticket_number, ticket=ticket
            )

            html_content = template.body_html.format(
                ticket_number=ticket.ticket_number, ticket=ticket, customer=customer
            )

            text_content = template.body_text.format(
                ticket_number=ticket.ticket_number, ticket=ticket, customer=customer
            )

            # Send email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[customer.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            logger.info(f"Sent ticket created email for {ticket.ticket_number}")

    except Exception as e:
        logger.error(f"Error sending ticket created email: {str(e)}")


@shared_task
def send_ticket_updated_email(ticket_id, update_type):
    """Send ticket update notification email."""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        customer = ticket.customer

        # Get appropriate email template
        template_type = f"ticket_{update_type}"
        template = EmailTemplate.objects.filter(
            organization=ticket.organization,
            template_type=template_type,
            is_active=True,
        ).first()

        if template:
            subject = template.subject.format(
                ticket_number=ticket.ticket_number, ticket=ticket
            )

            html_content = template.body_html.format(
                ticket_number=ticket.ticket_number, ticket=ticket, customer=customer
            )

            text_content = template.body_text.format(
                ticket_number=ticket.ticket_number, ticket=ticket, customer=customer
            )

            # Send email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[customer.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            logger.info(f"Sent ticket {update_type} email for {ticket.ticket_number}")

    except Exception as e:
        logger.error(f"Error sending ticket {update_type} email: {str(e)}")


@shared_task
def check_sla_breaches():
    """Check for SLA breaches and send notifications."""
    try:
        # Find tickets that are approaching or have breached SLA
        current_time = timezone.now()

        # Tickets approaching SLA (within 1 hour)
        approaching_tickets = Ticket.objects.filter(
            due_date__lte=current_time + timedelta(hours=1),
            due_date__gt=current_time,
            sla_breach=False,
            status__in=["open", "pending", "in_progress"],
        )

        for ticket in approaching_tickets:
            # Send warning notification
            send_sla_warning_email.delay(ticket.id)

        # Tickets that have breached SLA
        breached_tickets = Ticket.objects.filter(
            due_date__lt=current_time,
            sla_breach=False,
            status__in=["open", "pending", "in_progress"],
        )

        for ticket in breached_tickets:
            # Mark as breached
            ticket.sla_breach = True
            ticket.save()

            # Send breach notification
            send_sla_breach_email.delay(ticket.id)

            # Log activity
            from apps.accounts.signals import log_activity

            log_activity(
                action="sla_breach",
                entity_type="ticket",
                entity_id=ticket.id,
                old_values={},
                new_values={"sla_breach": True},
                changes={"sla_breach": True},
                user=None,  # System action
                description=f"SLA breached for ticket {ticket.ticket_number}",
            )

        logger.info(
            f"Checked SLA for {approaching_tickets.count()} approaching and {breached_tickets.count()} breached tickets"
        )

    except Exception as e:
        logger.error(f"Error checking SLA breaches: {str(e)}")


@shared_task
def send_sla_warning_email(ticket_id):
    """Send SLA warning email."""
    try:
        ticket = Ticket.objects.get(id=ticket_id)

        # Send warning to assigned agent and customer
        recipients = [ticket.customer.email]
        if ticket.assigned_agent:
            recipients.append(ticket.assigned_agent.email)

        subject = f"SLA Warning: Ticket {ticket.ticket_number}"
        message = f"""
        Ticket {ticket.ticket_number} is approaching its SLA deadline.
        
        Subject: {ticket.subject}
        Due: {ticket.due_date}
        Priority: {ticket.priority}
        
        Please take action to resolve this ticket.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        logger.info(f"Sent SLA warning for ticket {ticket.ticket_number}")

    except Exception as e:
        logger.error(f"Error sending SLA warning email: {str(e)}")


@shared_task
def send_sla_breach_email(ticket_id):
    """Send SLA breach notification email."""
    try:
        ticket = Ticket.objects.get(id=ticket_id)

        # Send breach notification to managers and customer
        recipients = [ticket.customer.email]

        # Add organization managers
        managers = User.objects.filter(organization=ticket.organization, role="admin")
        recipients.extend([manager.email for manager in managers])

        subject = f"SLA BREACH: Ticket {ticket.ticket_number}"
        message = f"""
        URGENT: Ticket {ticket.ticket_number} has breached its SLA.
        
        Subject: {ticket.subject}
        Due: {ticket.due_date}
        Priority: {ticket.priority}
        Status: {ticket.status}
        
        This ticket requires immediate attention.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        logger.info(f"Sent SLA breach notification for ticket {ticket.ticket_number}")

    except Exception as e:
        logger.error(f"Error sending SLA breach email: {str(e)}")


@shared_task
def auto_assign_tickets():
    """Automatically assign tickets based on rules."""
    try:
        # Get unassigned tickets
        unassigned_tickets = Ticket.objects.filter(
            assigned_agent__isnull=True, status__in=["open", "pending"]
        )

        for ticket in unassigned_tickets:
            # Find best agent based on workload and skills
            best_agent = find_best_agent_for_ticket(ticket)

            if best_agent:
                ticket.assigned_agent = best_agent
                ticket.save()

                # Send assignment notification
                send_assignment_notification.delay(ticket.id, best_agent.id)

                logger.info(
                    f"Auto-assigned ticket {ticket.ticket_number} to {best_agent.full_name}"
                )

    except Exception as e:
        logger.error(f"Error in auto-assignment: {str(e)}")


def find_best_agent_for_ticket(ticket):
    """Find the best agent for a ticket based on workload and skills."""
    try:
        # Get available agents in the same organization
        agents = User.objects.filter(
            organization=ticket.organization,
            role__in=["agent", "admin"],
            is_active=True,
        )

        if not agents.exists():
            return None

        # Find agent with least workload
        best_agent = None
        min_workload = float("inf")

        for agent in agents:
            # Count current assigned tickets
            current_tickets = Ticket.objects.filter(
                assigned_agent=agent, status__in=["open", "pending", "in_progress"]
            ).count()

            if current_tickets < min_workload:
                min_workload = current_tickets
                best_agent = agent

        return best_agent

    except Exception as e:
        logger.error(f"Error finding best agent: {str(e)}")
        return None


@shared_task
def send_assignment_notification(ticket_id, agent_id):
    """Send assignment notification to agent."""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        agent = User.objects.get(id=agent_id)

        subject = f"New Ticket Assignment: {ticket.ticket_number}"
        message = f"""
        You have been assigned a new ticket.
        
        Ticket: {ticket.ticket_number}
        Subject: {ticket.subject}
        Priority: {ticket.priority}
        Customer: {ticket.customer.full_name}
        
        Please review and respond promptly.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[agent.email],
            fail_silently=False,
        )

        logger.info(f"Sent assignment notification for ticket {ticket.ticket_number}")

    except Exception as e:
        logger.error(f"Error sending assignment notification: {str(e)}")
