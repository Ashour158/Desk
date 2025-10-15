"""
Celery tasks for notification system.
"""

from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
import requests
import json

from .models import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    NotificationLog,
)
from apps.accounts.models import User
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


@shared_task
def send_notification(notification_id):
    """Send a single notification through all enabled channels."""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user

        # Get user preferences
        preferences = getattr(user, "notification_preferences", None)
        if not preferences:
            preferences = NotificationPreference.objects.create(user=user)

        # Check if user is in quiet hours
        if preferences.is_quiet_hours():
            logger.info(f"User {user.id} is in quiet hours, skipping notification")
            return

        # Send through each channel
        if preferences.email_enabled and preferences.should_send_notification(
            notification.notification_type, "email"
        ):
            send_email_notification.delay(notification_id)

        if preferences.sms_enabled and preferences.should_send_notification(
            notification.notification_type, "sms"
        ):
            send_sms_notification.delay(notification_id)

        if preferences.push_enabled and preferences.should_send_notification(
            notification.notification_type, "push"
        ):
            send_push_notification.delay(notification_id)

        # Mark as sent
        notification.is_sent = True
        notification.save(update_fields=["is_sent"])

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as e:
        logger.error(f"Error sending notification {notification_id}: {str(e)}")


@shared_task
def send_email_notification(notification_id):
    """Send email notification."""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user

        # Get email template
        template = NotificationTemplate.objects.filter(
            organization=notification.organization,
            template_type="email",
            notification_type=notification.notification_type,
            is_active=True,
        ).first()

        if not template:
            # Use default template
            subject = notification.title
            message = notification.message
        else:
            # Render template
            context = {
                "user": user,
                "notification": notification,
                "organization": notification.organization,
                "ticket": getattr(notification, "ticket", None),
                "work_order": getattr(notification, "work_order", None),
            }
            subject = template.render(context)
            message = template.render(context)

        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # Log delivery
        NotificationLog.objects.create(
            notification=notification,
            channel="email",
            status="sent",
            recipient=user.email,
            subject=subject,
            message=message,
            sent_at=timezone.now(),
        )

        # Mark notification as sent via email
        notification.mark_as_sent("email")

        logger.info(f"Email notification sent to {user.email}")

    except Exception as e:
        logger.error(f"Error sending email notification {notification_id}: {str(e)}")

        # Log failure
        try:
            NotificationLog.objects.create(
                notification=notification,
                channel="email",
                status="failed",
                recipient=user.email,
                error_message=str(e),
            )
        except:
            pass


@shared_task
def send_sms_notification(notification_id):
    """Send SMS notification."""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user

        # Get SMS template
        template = NotificationTemplate.objects.filter(
            organization=notification.organization,
            template_type="sms",
            notification_type=notification.notification_type,
            is_active=True,
        ).first()

        if not template:
            message = notification.message
        else:
            context = {
                "user": user,
                "notification": notification,
                "organization": notification.organization,
            }
            message = template.render(context)

        # Truncate message for SMS
        if len(message) > 160:
            message = message[:157] + "..."

        # Send SMS via Twilio
        if hasattr(settings, "TWILIO_ACCOUNT_SID") and hasattr(
            settings, "TWILIO_AUTH_TOKEN"
        ):
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            response = client.messages.create(
                body=message, from_=settings.TWILIO_PHONE_NUMBER, to=user.phone_number
            )

            # Log delivery
            NotificationLog.objects.create(
                notification=notification,
                channel="sms",
                status="sent",
                recipient=user.phone_number,
                message=message,
                sent_at=timezone.now(),
                response_data={"sid": response.sid},
            )

            # Mark notification as sent via SMS
            notification.mark_as_sent("sms")

            logger.info(f"SMS notification sent to {user.phone_number}")
        else:
            logger.warning("Twilio not configured, skipping SMS notification")

    except Exception as e:
        logger.error(f"Error sending SMS notification {notification_id}: {str(e)}")

        # Log failure
        try:
            NotificationLog.objects.create(
                notification=notification,
                channel="sms",
                status="failed",
                recipient=user.phone_number,
                error_message=str(e),
            )
        except:
            pass


@shared_task
def send_push_notification(notification_id):
    """Send push notification."""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user

        # Get push template
        template = NotificationTemplate.objects.filter(
            organization=notification.organization,
            template_type="push",
            notification_type=notification.notification_type,
            is_active=True,
        ).first()

        if not template:
            title = notification.title
            message = notification.message
        else:
            context = {
                "user": user,
                "notification": notification,
                "organization": notification.organization,
            }
            title = template.render(context)
            message = template.render(context)

        # Send push notification via FCM
        if hasattr(settings, "FCM_SERVER_KEY"):
            send_fcm_notification.delay(user.id, title, message, notification.id)
        else:
            logger.warning("FCM not configured, skipping push notification")

    except Exception as e:
        logger.error(f"Error sending push notification {notification_id}: {str(e)}")


@shared_task
def send_fcm_notification(user_id, title, message, notification_id):
    """Send FCM push notification."""
    try:
        from apps.accounts.models import User

        user = User.objects.get(id=user_id)

        # Get user's FCM tokens
        fcm_tokens = getattr(user, "fcm_tokens", [])
        if not fcm_tokens:
            logger.warning(f"No FCM tokens for user {user_id}")
            return

        # Prepare FCM payload
        payload = {
            "registration_ids": fcm_tokens,
            "notification": {
                "title": title,
                "body": message,
                "icon": "/static/images/icon.png",
                "click_action": f"/notifications/{notification_id}",
            },
            "data": {"notification_id": str(notification_id), "type": "notification"},
        }

        # Send to FCM
        headers = {
            "Authorization": f"key={settings.FCM_SERVER_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            headers=headers,
            data=json.dumps(payload),
            timeout=30,
        )

        response.raise_for_status()
        response_data = response.json()

        # Log delivery
        NotificationLog.objects.create(
            notification=Notification.objects.get(id=notification_id),
            channel="push",
            status="sent",
            recipient=user.email,
            message=message,
            sent_at=timezone.now(),
            response_data=response_data,
        )

        # Mark notification as sent via push
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_sent("push")

        logger.info(f"Push notification sent to user {user_id}")

    except Exception as e:
        logger.error(f"Error sending FCM notification: {str(e)}")


@shared_task
def send_digest_notifications():
    """Send daily/weekly digest notifications."""
    try:
        # Get users with digest preferences
        users = User.objects.filter(
            notification_preferences__email_digest__in=["daily", "weekly"]
        )

        for user in users:
            preferences = user.notification_preferences

            # Determine digest period
            if preferences.email_digest == "daily":
                start_date = timezone.now() - timedelta(days=1)
            elif preferences.email_digest == "weekly":
                start_date = timezone.now() - timedelta(days=7)
            else:
                continue

            # Get unread notifications
            notifications = Notification.objects.filter(
                user=user, is_read=False, created_at__gte=start_date
            ).order_by("-created_at")

            if notifications.exists():
                send_digest_email.delay(user.id, [n.id for n in notifications])

    except Exception as e:
        logger.error(f"Error sending digest notifications: {str(e)}")


@shared_task
def send_digest_email(user_id, notification_ids):
    """Send digest email to user."""
    try:
        user = User.objects.get(id=user_id)
        notifications = Notification.objects.filter(id__in=notification_ids)

        # Prepare digest content
        subject = f"Daily Digest - {notifications.count()} notifications"

        # Create HTML email
        html_content = f"""
        <html>
        <body>
            <h2>Your Daily Digest</h2>
            <p>You have {notifications.count()} unread notifications:</p>
            <ul>
        """

        for notification in notifications:
            html_content += f"""
                <li>
                    <strong>{notification.title}</strong><br>
                    {notification.message}<br>
                    <small>{notification.created_at.strftime('%Y-%m-%d %H:%M')}</small>
                </li>
            """

        html_content += """
            </ul>
            <p><a href="/notifications/">View all notifications</a></p>
        </body>
        </html>
        """

        # Send email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Digest email sent to {user.email}")

    except Exception as e:
        logger.error(f"Error sending digest email: {str(e)}")


@shared_task
def cleanup_old_notifications():
    """Clean up old notifications and logs."""
    try:
        # Delete notifications older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)

        old_notifications = Notification.objects.filter(
            created_at__lt=cutoff_date, is_read=True
        )

        deleted_count = old_notifications.count()
        old_notifications.delete()

        # Delete notification logs older than 30 days
        old_logs = NotificationLog.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=30)
        )

        deleted_logs = old_logs.count()
        old_logs.delete()

        logger.info(f"Cleaned up {deleted_count} notifications and {deleted_logs} logs")

    except Exception as e:
        logger.error(f"Error cleaning up notifications: {str(e)}")


@shared_task
def send_bulk_notifications(notification_data_list):
    """Send multiple notifications efficiently."""
    try:
        for notification_data in notification_data_list:
            # Create notification
            notification = Notification.objects.create(
                organization_id=notification_data["organization_id"],
                user_id=notification_data["user_id"],
                notification_type=notification_data["notification_type"],
                title=notification_data["title"],
                message=notification_data["message"],
                priority=notification_data.get("priority", "medium"),
                entity_type=notification_data.get("entity_type"),
                entity_id=notification_data.get("entity_id"),
                metadata=notification_data.get("metadata", {}),
            )

            # Send notification
            send_notification.delay(notification.id)

        logger.info(f"Queued {len(notification_data_list)} notifications for sending")

    except Exception as e:
        logger.error(f"Error sending bulk notifications: {str(e)}")


@shared_task
def test_notification_delivery():
    """Test notification delivery for all channels."""
    try:
        # Create test notification
        test_org = Organization.objects.first()
        if not test_org:
            return

        test_user = User.objects.filter(organization=test_org).first()
        if not test_user:
            return

        notification = Notification.objects.create(
            organization=test_org,
            user=test_user,
            notification_type="system_alert",
            title="Test Notification",
            message="This is a test notification to verify delivery channels.",
            priority="low",
        )

        # Send test notification
        send_notification.delay(notification.id)

        logger.info("Test notification sent")

    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
