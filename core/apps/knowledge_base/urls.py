"""
URL configuration for knowledge base system.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Article management
    path("", views.kb_article_list, name="kb_article_list"),
    path("search/", views.kb_search, name="kb_search"),
    path("articles/create/", views.kb_article_create, name="kb_article_create"),
    path(
        "articles/<uuid:article_id>/", views.kb_article_detail, name="kb_article_detail"
    ),
    path(
        "articles/<uuid:article_id>/edit/",
        views.kb_article_edit,
        name="kb_article_edit",
    ),
    path(
        "articles/<uuid:article_id>/publish/",
        views.kb_article_publish,
        name="kb_article_publish",
    ),
    path("articles/<uuid:article_id>/feedback/", views.kb_feedback, name="kb_feedback"),
    # Category management
    path("categories/", views.kb_category_list, name="kb_category_list"),
    path(
        "categories/<uuid:category_id>/",
        views.kb_category_detail,
        name="kb_category_detail",
    ),
    # Analytics
    path("analytics/", views.kb_analytics, name="kb_analytics"),
]
