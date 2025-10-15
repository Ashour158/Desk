"""
Signal handlers for user-related events.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import User, UserProfile, ActivityLog, UserSession
from apps.organizations.middleware import get_current_organization


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Log user changes for audit trail."""
    if not created:
        # Log user updates
        log_activity(
            action="update",
            entity_type="user",
            entity_id=instance.id,
            old_values={},
            new_values={},
            changes={"updated_fields": list(instance.get_dirty_fields().keys())},
            user=instance,
            description=f"User {instance.email} was updated",
        )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login activity."""
    # Update last active timestamp
    user.update_last_active(request.META.get("REMOTE_ADDR"))

    # Create or update session
    session_key = request.session.session_key
    if session_key:
        UserSession.objects.update_or_create(
            session_key=session_key,
            defaults={
                "user": user,
                "ip_address": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "is_active": True,
            },
        )

    # Log login activity
    log_activity(
        action="login",
        entity_type="user",
        entity_id=user.id,
        old_values={},
        new_values={},
        changes={},
        user=user,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        request_path=request.path,
        request_method=request.method,
        description=f"User {user.email} logged in",
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout activity."""
    if user:
        # Deactivate session
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.filter(session_key=session_key, user=user).update(
                is_active=False
            )

        # Log logout activity
        log_activity(
            action="logout",
            entity_type="user",
            entity_id=user.id,
            old_values={},
            new_values={},
            changes={},
            user=user,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            description=f"User {user.email} logged out",
        )


def log_activity(
    action,
    entity_type,
    entity_id,
    old_values=None,
    new_values=None,
    changes=None,
    user=None,
    ip_address=None,
    user_agent=None,
    request_path=None,
    request_method=None,
    description=None,
):
    """
    Helper function to log activities.
    """
    organization = get_current_organization()
    if not organization:
        return

    ActivityLog.objects.create(
        organization=organization,
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values or {},
        new_values=new_values or {},
        changes=changes or {},
        ip_address=ip_address or "",
        user_agent=user_agent or "",
        request_path=request_path or "",
        request_method=request_method or "",
        description=description or f"{action} {entity_type} {entity_id}",
    )
