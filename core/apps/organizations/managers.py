"""
Multi-tenant managers for organization isolation.
"""

from django.db import models
from django.contrib.auth.models import User


class TenantManager(models.Manager):
    """
    Manager that filters by organization.
    """

    def get_queryset(self):
        """Filter queryset by current organization."""
        from .middleware import get_current_organization

        queryset = super().get_queryset()
        organization = get_current_organization()

        if organization:
            return queryset.filter(organization=organization)
        return queryset.none()

    def for_organization(self, organization):
        """Get queryset for specific organization."""
        return super().get_queryset().filter(organization=organization)


class TenantAwareModel(models.Model):
    """
    Abstract base model for multi-tenant models.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Auto-set organization if not provided."""
        if not self.organization_id:
            from .middleware import get_current_organization

            organization = get_current_organization()
            if organization:
                self.organization = organization
        super().save(*args, **kwargs)


class OrganizationUserManager(models.Manager):
    """
    Manager for organization users with additional methods.
    """

    def get_queryset(self):
        """Filter users by organization."""
        from .middleware import get_current_organization

        queryset = super().get_queryset()
        organization = get_current_organization()

        if organization:
            return queryset.filter(organization=organization)
        return queryset.none()

    def agents(self):
        """Get all agents for the organization."""
        return self.get_queryset().filter(role__in=["admin", "manager", "agent"])

    def customers(self):
        """Get all customers for the organization."""
        return self.get_queryset().filter(role="customer")

    def active_users(self):
        """Get all active users for the organization."""
        return self.get_queryset().filter(is_active=True)

    def available_agents(self):
        """Get available agents for ticket assignment."""
        return self.agents().filter(availability_status="available", is_active=True)


class TicketManager(TenantManager):
    """
    Manager for tickets with organization filtering.
    """

    def get_queryset(self):
        """Filter tickets by organization."""
        return super().get_queryset()

    def open_tickets(self):
        """Get all open tickets."""
        return self.get_queryset().filter(status__in=["new", "open", "pending"])

    def assigned_to(self, user):
        """Get tickets assigned to specific user."""
        return self.get_queryset().filter(assigned_agent=user)

    def created_by(self, user):
        """Get tickets created by specific user."""
        return self.get_queryset().filter(created_by=user)

    def overdue(self):
        """Get overdue tickets."""
        from django.utils import timezone

        return self.get_queryset().filter(
            resolution_due__lt=timezone.now(), status__in=["new", "open", "pending"]
        )

    def high_priority(self):
        """Get high priority tickets."""
        return self.get_queryset().filter(priority__in=["high", "urgent"])

    def by_status(self, status):
        """Get tickets by status."""
        return self.get_queryset().filter(status=status)

    def by_priority(self, priority):
        """Get tickets by priority."""
        return self.get_queryset().filter(priority=priority)

    def by_channel(self, channel):
        """Get tickets by channel."""
        return self.get_queryset().filter(channel=channel)

    def recent(self, days=7):
        """Get recent tickets."""
        from django.utils import timezone
        from datetime import timedelta

        since = timezone.now() - timedelta(days=days)
        return self.get_queryset().filter(created_at__gte=since)


class WorkOrderManager(TenantManager):
    """
    Manager for work orders with organization filtering.
    """

    def get_queryset(self):
        """Filter work orders by organization."""
        return super().get_queryset()

    def scheduled(self):
        """Get scheduled work orders."""
        return self.get_queryset().filter(status="scheduled")

    def in_progress(self):
        """Get in-progress work orders."""
        return self.get_queryset().filter(status="in_progress")

    def completed(self):
        """Get completed work orders."""
        return self.get_queryset().filter(status="completed")

    def assigned_to(self, technician):
        """Get work orders assigned to technician."""
        return self.get_queryset().filter(assigned_technician=technician)

    def by_date(self, date):
        """Get work orders for specific date."""
        return self.get_queryset().filter(scheduled_start__date=date)

    def overdue(self):
        """Get overdue work orders."""
        from django.utils import timezone

        return self.get_queryset().filter(
            scheduled_start__lt=timezone.now(), status__in=["scheduled", "in_progress"]
        )


class TechnicianManager(TenantManager):
    """
    Manager for technicians with organization filtering.
    """

    def get_queryset(self):
        """Filter technicians by organization."""
        return super().get_queryset()

    def available(self):
        """Get available technicians."""
        return self.get_queryset().filter(availability_status="available")

    def with_skill(self, skill):
        """Get technicians with specific skill."""
        return self.get_queryset().filter(skills__contains=[skill])

    def certified(self, certification):
        """Get technicians with specific certification."""
        return self.get_queryset().filter(certifications__contains=[certification])

    def by_location(self, location):
        """Get technicians near location."""
        # This would use PostGIS for location-based filtering
        return self.get_queryset().filter(
            current_location__distance_lte=(location, 50000)  # 50km radius
        )


class KnowledgeBaseManager(TenantManager):
    """
    Manager for knowledge base articles with organization filtering.
    """

    def get_queryset(self):
        """Filter KB articles by organization."""
        return super().get_queryset()

    def published(self):
        """Get published articles."""
        return self.get_queryset().filter(status="published")

    def by_category(self, category):
        """Get articles by category."""
        return self.get_queryset().filter(category=category)

    def popular(self):
        """Get popular articles."""
        return self.get_queryset().order_by("-view_count")

    def recent(self):
        """Get recent articles."""
        return self.get_queryset().order_by("-created_at")

    def search(self, query):
        """Search articles by query."""
        return self.get_queryset().filter(
            models.Q(title__icontains=query)
            | models.Q(content__icontains=query)
            | models.Q(tags__icontains=query)
        )
