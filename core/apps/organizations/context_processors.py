"""
Context processors for organization-related template variables.
"""

from .middleware import get_current_organization


def organization(request):
    """
    Add current organization to template context.
    """
    return {
        "current_organization": get_current_organization(),
    }
