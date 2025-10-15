"""
URL configuration for ticket system.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Ticket management
    path("", views.ticket_list, name="ticket_list"),
    path("create/", views.ticket_create, name="ticket_create"),
    path("<uuid:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    path("<uuid:ticket_id>/assign/", views.ticket_assign, name="ticket_assign"),
    path(
        "<uuid:ticket_id>/status/",
        views.ticket_status_update,
        name="ticket_status_update",
    ),
    path(
        "<uuid:ticket_id>/comment/", views.ticket_comment_add, name="ticket_comment_add"
    ),
    # Canned responses
    path("canned-responses/", views.canned_responses, name="canned_responses"),
    path(
        "canned-responses/create/",
        views.canned_response_create,
        name="canned_response_create",
    ),
    # Statistics and dashboards
    path("stats/", views.ticket_stats, name="ticket_stats"),
    path("sla-dashboard/", views.sla_dashboard, name="sla_dashboard"),
]
