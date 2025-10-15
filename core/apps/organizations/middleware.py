"""
Multi-tenant middleware for organization isolation.
"""

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin
from .models import Organization


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenant organization isolation.
    """

    def process_request(self, request):
        """Set organization context for the request."""
        request.organization = None

        # Skip for admin, API, and static files
        if (
            request.path.startswith("/admin/")
            or request.path.startswith("/api/")
            or request.path.startswith("/static/")
            or request.path.startswith("/media/")
        ):
            return

        # Get organization from subdomain
        if hasattr(request, "subdomain") and request.subdomain:
            try:
                request.organization = Organization.objects.get(
                    subdomain=request.subdomain, is_active=True
                )
            except Organization.DoesNotExist:
                raise Http404("Organization not found")

        # Get organization from user if authenticated
        elif request.user.is_authenticated and hasattr(request.user, "organization"):
            request.organization = request.user.organization

        # Get organization from session
        elif "organization_id" in request.session:
            try:
                request.organization = Organization.objects.get(
                    id=request.session["organization_id"], is_active=True
                )
            except Organization.DoesNotExist:
                del request.session["organization_id"]

        # Set organization in thread local for models
        if request.organization:
            set_organization(request.organization)


class SubdomainMiddleware(MiddlewareMixin):
    """
    Middleware to extract subdomain from request.
    """

    def process_request(self, request):
        """Extract subdomain from request host."""
        host = request.get_host().split(":")[0]
        parts = host.split(".")

        if len(parts) >= 3:
            # Extract subdomain (e.g., company.helpdesk.com -> company)
            request.subdomain = parts[0]
        else:
            request.subdomain = None


def get_current_organization():
    """Get current organization from thread local."""
    from threading import local

    _thread_locals = local()
    return getattr(_thread_locals, "organization", None)


def set_organization(organization):
    """Set organization in thread local."""
    from threading import local

    _thread_locals = local()
    _thread_locals.organization = organization


class OrganizationContextProcessor:
    """
    Context processor to add organization to template context.
    """

    def __call__(self, request):
        return {
            "organization": getattr(request, "organization", None),
        }
