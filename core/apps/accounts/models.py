"""
User and authentication models with multi-tenant support.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_cryptography.fields import encrypt
from apps.organizations.models import Organization


class User(AbstractUser):
    """Extended user model with multi-tenant support."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )

    # User profile fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    timezone = models.CharField(max_length=50, default="UTC")
    language = models.CharField(max_length=10, default="en")

    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=[
            ("admin", "Administrator"),
            ("manager", "Manager"),
            ("agent", "Agent"),
            ("customer", "Customer"),
        ],
        default="customer",
    )

    # Security fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = encrypt(models.CharField(max_length=32, blank=True))
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_active_at = models.DateTimeField(auto_now=True)

    # Customer-specific fields
    company = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    customer_tier = models.CharField(
        max_length=20,
        choices=[
            ("basic", "Basic"),
            ("premium", "Premium"),
            ("enterprise", "Enterprise"),
        ],
        default="basic",
    )

    # Agent-specific fields
    skills = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    max_concurrent_tickets = models.IntegerField(default=10)
    availability_status = models.CharField(
        max_length=20,
        choices=[
            ("available", "Available"),
            ("busy", "Busy"),
            ("away", "Away"),
            ("offline", "Offline"),
        ],
        default="offline",
    )

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_user"
        indexes = [
            models.Index(fields=["organization", "role"]),
            models.Index(fields=["email"]),
            models.Index(fields=["last_active_at"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username

    def is_admin(self):
        """Check if user is an administrator."""
        return self.role == "admin" or self.is_superuser

    def is_agent(self):
        """Check if user is an agent or higher."""
        return self.role in ["admin", "manager", "agent"]

    def is_customer(self):
        """Check if user is a customer."""
        return self.role == "customer"

    def can_access_ticket(self, ticket):
        """Check if user can access a specific ticket."""
        if self.is_admin():
            return True
        if self.is_agent() and ticket.assigned_agent == self:
            return True
        if self.is_customer() and ticket.customer == self:
            return True
        return False

    def update_last_active(self, ip_address=None):
        """Update last active timestamp and IP."""
        self.last_active_at = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address
        self.save(update_fields=["last_active_at", "last_login_ip"])


class UserSession(models.Model):
    """Track user sessions for security and analytics."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "accounts_user_session"
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.session_key[:8]}"


class UserPermission(models.Model):
    """Custom permissions for users."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="custom_permissions"
    )
    permission = models.CharField(max_length=100)
    granted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="granted_permissions"
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "accounts_user_permission"
        unique_together = ["user", "permission"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.permission}"

    def is_valid(self):
        """Check if permission is still valid."""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
