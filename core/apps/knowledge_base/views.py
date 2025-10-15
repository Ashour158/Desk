"""
Knowledge base views for helpdesk platform.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone

from .models import KBArticle, KBCategory, KBFeedback, KBSearch
from .forms import KBArticleForm, KBCategoryForm, KBFeedbackForm
from apps.organizations.models import Organization


@login_required
def kb_article_list(request):
    """List knowledge base articles."""
    organization = request.user.organization

    # Base queryset
    articles = KBArticle.objects.filter(organization=organization, status="published")

    # Filtering
    category_filter = request.GET.get("category")
    search_query = request.GET.get("search")
    featured_only = request.GET.get("featured") == "true"

    if category_filter:
        articles = articles.filter(category_id=category_filter)

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(tags__icontains=search_query)
        )

    if featured_only:
        articles = articles.filter(is_featured=True)

    # Get categories for filter
    categories = KBCategory.objects.filter(
        organization=organization, is_active=True
    ).order_by("name")

    # Pagination
    paginator = Paginator(articles.order_by("-published_at", "-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "articles": page_obj,
        "categories": categories,
        "current_filters": {
            "category": category_filter,
            "search": search_query,
            "featured": featured_only,
        },
    }

    return render(request, "knowledge_base/article_list.html", context)


@login_required
def kb_article_detail(request, article_id):
    """View knowledge base article."""
    article = get_object_or_404(
        KBArticle,
        id=article_id,
        organization=request.user.organization,
        status="published",
    )

    # Track view
    track_article_view(article, request)

    # Get related articles
    related_articles = KBArticle.objects.filter(
        organization=request.user.organization,
        status="published",
        category=article.category,
    ).exclude(id=article.id)[:5]

    # Get feedback
    feedback = KBFeedback.objects.filter(article=article).order_by("-created_at")

    context = {
        "article": article,
        "related_articles": related_articles,
        "feedback": feedback,
        "can_edit": request.user.role in ["agent", "admin"],
    }

    return render(request, "knowledge_base/article_detail.html", context)


@login_required
def kb_search(request):
    """Search knowledge base articles."""
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"articles": [], "suggestions": []})

    organization = request.user.organization

    # Search articles
    articles = (
        KBArticle.objects.filter(organization=organization, status="published")
        .filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__icontains=query)
        )
        .order_by("-helpful_count", "-views_count")[:10]
    )

    # Track search
    KBSearch.objects.create(
        organization=organization,
        query=query,
        results_count=articles.count(),
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get("REMOTE_ADDR"),
    )

    # Format results
    results = []
    for article in articles:
        results.append(
            {
                "id": str(article.id),
                "title": article.title,
                "summary": (
                    article.summary[:200] + "..."
                    if len(article.summary) > 200
                    else article.summary
                ),
                "category": article.category.name if article.category else None,
                "helpful_count": article.helpful_count,
                "views_count": article.views_count,
                "url": f"/kb/articles/{article.id}/",
            }
        )

    # Get search suggestions
    suggestions = get_search_suggestions(query, organization)

    return JsonResponse({"articles": results, "suggestions": suggestions})


def get_search_suggestions(query, organization):
    """Get search suggestions based on query."""
    # Get popular searches
    popular_searches = (
        KBSearch.objects.filter(organization=organization, query__icontains=query)
        .values("query")
        .annotate(count=Count("query"))
        .order_by("-count")[:5]
    )

    return [search["query"] for search in popular_searches]


def track_article_view(article, request):
    """Track article view for analytics."""
    from .models import KBArticleView

    KBArticleView.objects.create(
        article=article,
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        referrer=request.META.get("HTTP_REFERER", ""),
    )

    # Update view count
    article.views_count += 1
    article.save(update_fields=["views_count"])


@login_required
@require_http_methods(["POST"])
def kb_feedback(request, article_id):
    """Submit feedback for knowledge base article."""
    article = get_object_or_404(
        KBArticle, id=article_id, organization=request.user.organization
    )

    form = KBFeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.article = article
        feedback.user = request.user if request.user.is_authenticated else None
        feedback.ip_address = request.META.get("REMOTE_ADDR")
        feedback.save()

        # Update article feedback counts
        if feedback.feedback_type == "helpful":
            article.helpful_count += 1
        elif feedback.feedback_type == "not_helpful":
            article.not_helpful_count += 1

        article.save(update_fields=["helpful_count", "not_helpful_count"])

        return JsonResponse(
            {"success": True, "message": "Feedback submitted successfully"}
        )
    else:
        return JsonResponse({"errors": form.errors}, status=400)


@login_required
def kb_category_list(request):
    """List knowledge base categories."""
    organization = request.user.organization

    categories = KBCategory.objects.filter(
        organization=organization, is_active=True
    ).order_by("sort_order", "name")

    context = {
        "categories": categories,
        "can_manage": request.user.role in ["agent", "admin"],
    }

    return render(request, "knowledge_base/category_list.html", context)


@login_required
def kb_category_detail(request, category_id):
    """View articles in a category."""
    category = get_object_or_404(
        KBCategory,
        id=category_id,
        organization=request.user.organization,
        is_active=True,
    )

    articles = KBArticle.objects.filter(
        organization=request.user.organization, category=category, status="published"
    ).order_by("-published_at", "-created_at")

    # Pagination
    paginator = Paginator(articles, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"category": category, "articles": page_obj}

    return render(request, "knowledge_base/category_detail.html", context)


@login_required
def kb_article_create(request):
    """Create new knowledge base article."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    if request.method == "POST":
        form = KBArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.organization = request.user.organization
            article.author = request.user
            article.save()

            return JsonResponse(
                {
                    "success": True,
                    "article_id": str(article.id),
                    "message": "Article created successfully",
                }
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = KBArticleForm()
    return render(request, "knowledge_base/article_create.html", {"form": form})


@login_required
def kb_article_edit(request, article_id):
    """Edit knowledge base article."""
    article = get_object_or_404(
        KBArticle, id=article_id, organization=request.user.organization
    )

    if request.user.role not in ["agent", "admin"] and article.author != request.user:
        return JsonResponse({"error": "Permission denied"}, status=403)

    if request.method == "POST":
        form = KBArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.last_modified_by = request.user
            article.version += 1
            article.save()

            return JsonResponse(
                {"success": True, "message": "Article updated successfully"}
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = KBArticleForm(instance=article)
    return render(
        request, "knowledge_base/article_edit.html", {"form": form, "article": article}
    )


@login_required
@require_http_methods(["POST"])
def kb_article_publish(request, article_id):
    """Publish knowledge base article."""
    article = get_object_or_404(
        KBArticle, id=article_id, organization=request.user.organization
    )

    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    article.status = "published"
    article.published_at = timezone.now()
    article.save()

    return JsonResponse({"success": True, "message": "Article published successfully"})


@login_required
def kb_analytics(request):
    """Knowledge base analytics dashboard."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    organization = request.user.organization

    # Article statistics
    total_articles = KBArticle.objects.filter(organization=organization).count()
    published_articles = KBArticle.objects.filter(
        organization=organization, status="published"
    ).count()
    draft_articles = KBArticle.objects.filter(
        organization=organization, status="draft"
    ).count()

    # Most viewed articles
    most_viewed = KBArticle.objects.filter(
        organization=organization, status="published"
    ).order_by("-views_count")[:10]

    # Most helpful articles
    most_helpful = KBArticle.objects.filter(
        organization=organization, status="published"
    ).order_by("-helpful_count")[:10]

    # Search analytics
    popular_searches = (
        KBSearch.objects.filter(organization=organization)
        .values("query")
        .annotate(count=Count("query"))
        .order_by("-count")[:10]
    )

    # Category statistics
    category_stats = (
        KBCategory.objects.filter(organization=organization, is_active=True)
        .annotate(article_count=Count("articles"))
        .order_by("-article_count")
    )

    analytics = {
        "total_articles": total_articles,
        "published_articles": published_articles,
        "draft_articles": draft_articles,
        "most_viewed": [
            {
                "id": str(article.id),
                "title": article.title,
                "views_count": article.views_count,
                "helpful_count": article.helpful_count,
            }
            for article in most_viewed
        ],
        "most_helpful": [
            {
                "id": str(article.id),
                "title": article.title,
                "helpful_count": article.helpful_count,
                "not_helpful_count": article.not_helpful_count,
            }
            for article in most_helpful
        ],
        "popular_searches": [
            {"query": search["query"], "count": search["count"]}
            for search in popular_searches
        ],
        "category_stats": [
            {
                "id": str(category.id),
                "name": category.name,
                "article_count": category.article_count,
            }
            for category in category_stats
        ],
    }

    return JsonResponse(analytics)
