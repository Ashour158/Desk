"""
Internationalization views for helpdesk platform.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.translation import gettext as _
import json

from .models import (
    Language,
    Translation,
    LocalizationSettings,
    TranslationRequest,
    ContentTranslation,
    TranslationMemory,
    LanguagePreference,
)
from .forms import (
    LanguageForm,
    TranslationForm,
    LocalizationSettingsForm,
    TranslationRequestForm,
    ContentTranslationForm,
)
from apps.organizations.models import Organization


@login_required
def i18n_dashboard(request):
    """Internationalization dashboard."""
    organization = request.user.organization

    # Get organization's localization settings
    try:
        settings = LocalizationSettings.objects.get(organization=organization)
    except LocalizationSettings.DoesNotExist:
        settings = None

    # Translation statistics
    total_translations = Translation.objects.filter(organization=organization).count()
    approved_translations = Translation.objects.filter(
        organization=organization, is_approved=True
    ).count()

    # Language coverage
    supported_languages = settings.supported_languages.all() if settings else []
    language_stats = []

    for language in supported_languages:
        total = Translation.objects.filter(
            organization=organization, language=language
        ).count()
        approved = Translation.objects.filter(
            organization=organization, language=language, is_approved=True
        ).count()

        language_stats.append(
            {
                "language": language,
                "total": total,
                "approved": approved,
                "completeness": (approved / total * 100) if total > 0 else 0,
            }
        )

    # Recent translation requests
    recent_requests = TranslationRequest.objects.filter(
        organization=organization
    ).order_by("-created_at")[:5]

    # Translation memory stats
    memory_count = TranslationMemory.objects.filter(organization=organization).count()

    context = {
        "settings": settings,
        "total_translations": total_translations,
        "approved_translations": approved_translations,
        "language_stats": language_stats,
        "recent_requests": recent_requests,
        "memory_count": memory_count,
        "can_manage": request.user.role in ["admin"],
    }

    return render(request, "i18n/dashboard.html", context)


@login_required
def language_management(request):
    """Language management interface."""
    organization = request.user.organization

    # Get organization's supported languages
    try:
        settings = LocalizationSettings.objects.get(organization=organization)
        supported_languages = settings.supported_languages.all()
    except LocalizationSettings.DoesNotExist:
        supported_languages = []

    # All available languages
    all_languages = Language.objects.filter(is_active=True).order_by("name")

    context = {
        "supported_languages": supported_languages,
        "all_languages": all_languages,
        "can_manage": request.user.role in ["admin"],
    }

    return render(request, "i18n/language_management.html", context)


@login_required
@require_http_methods(["POST"])
def add_supported_language(request):
    """Add language to organization's supported languages."""
    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    language_id = request.POST.get("language_id")
    if not language_id:
        return JsonResponse({"error": "Language ID required"}, status=400)

    try:
        language = Language.objects.get(id=language_id)
        organization = request.user.organization

        # Get or create localization settings
        settings, created = LocalizationSettings.objects.get_or_create(
            organization=organization, defaults={"default_language": language}
        )

        # Add language to supported languages
        settings.supported_languages.add(language)

        return JsonResponse(
            {"success": True, "message": f"Language {language.name} added successfully"}
        )

    except Language.DoesNotExist:
        return JsonResponse({"error": "Language not found"}, status=404)


@login_required
@require_http_methods(["POST"])
def remove_supported_language(request):
    """Remove language from organization's supported languages."""
    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    language_id = request.POST.get("language_id")
    if not language_id:
        return JsonResponse({"error": "Language ID required"}, status=400)

    try:
        language = Language.objects.get(id=language_id)
        organization = request.user.organization

        settings = LocalizationSettings.objects.get(organization=organization)
        settings.supported_languages.remove(language)

        return JsonResponse(
            {
                "success": True,
                "message": f"Language {language.name} removed successfully",
            }
        )

    except (Language.DoesNotExist, LocalizationSettings.DoesNotExist):
        return JsonResponse({"error": "Language or settings not found"}, status=404)


@login_required
def translation_management(request):
    """Translation management interface."""
    organization = request.user.organization

    translations = Translation.objects.filter(organization=organization)

    # Filtering
    language_filter = request.GET.get("language")
    type_filter = request.GET.get("type")
    status_filter = request.GET.get("status")
    search_query = request.GET.get("search")

    if language_filter:
        translations = translations.filter(language_id=language_filter)
    if type_filter:
        translations = translations.filter(translation_type=type_filter)
    if status_filter == "approved":
        translations = translations.filter(is_approved=True)
    elif status_filter == "pending":
        translations = translations.filter(is_approved=False)
    if search_query:
        translations = translations.filter(
            Q(key__icontains=search_query)
            | Q(original_text__icontains=search_query)
            | Q(translated_text__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(translations.order_by("-updated_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get filter options
    languages = Language.objects.filter(supported_organizations=organization).order_by(
        "name"
    )

    context = {
        "translations": page_obj,
        "languages": languages,
        "translation_types": Translation.TRANSLATION_TYPES,
        "current_filters": {
            "language": language_filter,
            "type": type_filter,
            "status": status_filter,
            "search": search_query,
        },
    }

    return render(request, "i18n/translation_management.html", context)


@login_required
def translation_edit(request, translation_id):
    """Edit translation."""
    translation = get_object_or_404(
        Translation, id=translation_id, organization=request.user.organization
    )

    if request.method == "POST":
        form = TranslationForm(request.POST, instance=translation)
        if form.is_valid():
            translation = form.save(commit=False)
            translation.updated_at = timezone.now()
            translation.save()

            return JsonResponse(
                {"success": True, "message": "Translation updated successfully"}
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = TranslationForm(instance=translation)
    return render(
        request,
        "i18n/translation_edit.html",
        {"form": form, "translation": translation},
    )


@login_required
@require_http_methods(["POST"])
def approve_translation(request, translation_id):
    """Approve translation."""
    translation = get_object_or_404(
        Translation, id=translation_id, organization=request.user.organization
    )

    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    translation.is_approved = True
    translation.approved_by = request.user
    translation.save()

    return JsonResponse(
        {"success": True, "message": "Translation approved successfully"}
    )


@login_required
def translation_requests(request):
    """Translation requests management."""
    organization = request.user.organization

    requests = TranslationRequest.objects.filter(organization=organization)

    # Filtering
    status_filter = request.GET.get("status")
    language_filter = request.GET.get("language")
    assigned_to_me = request.GET.get("assigned_to_me") == "true"

    if status_filter:
        requests = requests.filter(status=status_filter)
    if language_filter:
        requests = requests.filter(language_id=language_filter)
    if assigned_to_me:
        requests = requests.filter(assigned_to=request.user)

    # Pagination
    paginator = Paginator(requests.order_by("-created_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "requests": page_obj,
        "status_choices": TranslationRequest.STATUS_CHOICES,
        "current_filters": {
            "status": status_filter,
            "language": language_filter,
            "assigned_to_me": assigned_to_me,
        },
    }

    return render(request, "i18n/translation_requests.html", context)


@login_required
def translation_request_create(request):
    """Create translation request."""
    if request.method == "POST":
        form = TranslationRequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.organization = request.user.organization
            request_obj.requested_by = request.user
            request_obj.save()

            return JsonResponse({"success": True, "request_id": str(request_obj.id)})
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = TranslationRequestForm()
    return render(request, "i18n/translation_request_create.html", {"form": form})


@login_required
@require_http_methods(["POST"])
def assign_translation_request(request, request_id):
    """Assign translation request to user."""
    translation_request = get_object_or_404(
        TranslationRequest, id=request_id, organization=request.user.organization
    )

    if request.user.role not in ["admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    assigned_to_id = request.POST.get("assigned_to_id")
    if not assigned_to_id:
        return JsonResponse({"error": "Assigned to ID required"}, status=400)

    try:
        from apps.accounts.models import User

        assigned_to = User.objects.get(
            id=assigned_to_id, organization=request.user.organization
        )

        translation_request.assigned_to = assigned_to
        translation_request.status = "in_progress"
        translation_request.save()

        return JsonResponse(
            {"success": True, "message": "Translation request assigned successfully"}
        )

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)


@login_required
def content_translations(request):
    """Content translations management."""
    organization = request.user.organization

    translations = ContentTranslation.objects.filter(organization=organization)

    # Filtering
    content_type_filter = request.GET.get("content_type")
    language_filter = request.GET.get("language")
    status_filter = request.GET.get("status")

    if content_type_filter:
        translations = translations.filter(content_type=content_type_filter)
    if language_filter:
        translations = translations.filter(language_id=language_filter)
    if status_filter == "approved":
        translations = translations.filter(is_approved=True)
    elif status_filter == "pending":
        translations = translations.filter(is_approved=False)

    # Pagination
    paginator = Paginator(translations.order_by("-updated_at"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "translations": page_obj,
        "current_filters": {
            "content_type": content_type_filter,
            "language": language_filter,
            "status": status_filter,
        },
    }

    return render(request, "i18n/content_translations.html", context)


@login_required
def translation_memory(request):
    """Translation memory management."""
    organization = request.user.organization

    memory = TranslationMemory.objects.filter(organization=organization)

    # Filtering
    source_language_filter = request.GET.get("source_language")
    target_language_filter = request.GET.get("target_language")
    search_query = request.GET.get("search")

    if source_language_filter:
        memory = memory.filter(source_language_id=source_language_filter)
    if target_language_filter:
        memory = memory.filter(target_language_id=target_language_filter)
    if search_query:
        memory = memory.filter(
            Q(source_text__icontains=search_query)
            | Q(target_text__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(memory.order_by("-usage_count", "-match_score"), 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "memory": page_obj,
        "current_filters": {
            "source_language": source_language_filter,
            "target_language": target_language_filter,
            "search": search_query,
        },
    }

    return render(request, "i18n/translation_memory.html", context)


@login_required
def user_language_preferences(request):
    """User language preferences."""
    try:
        preferences = LanguagePreference.objects.get(user=request.user)
    except LanguagePreference.DoesNotExist:
        preferences = None

    if request.method == "POST":
        form = LanguagePreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            preferences = form.save(commit=False)
            preferences.user = request.user
            preferences.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Language preferences updated successfully",
                }
            )
        else:
            return JsonResponse({"errors": form.errors}, status=400)

    form = LanguagePreferenceForm(instance=preferences)
    return render(request, "i18n/user_preferences.html", {"form": form})


@login_required
def auto_translate(request):
    """Auto-translate content."""
    if request.method == "POST":
        data = json.loads(request.body)

        source_text = data.get("source_text")
        source_language = data.get("source_language")
        target_language = data.get("target_language")

        if not all([source_text, source_language, target_language]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        try:
            # Call translation service
            from .services import TranslationService

            service = TranslationService()

            result = service.translate_text(
                text=source_text,
                source_language=source_language,
                target_language=target_language,
            )

            return JsonResponse(
                {
                    "success": True,
                    "translated_text": result["translated_text"],
                    "confidence": result["confidence"],
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def translation_statistics(request):
    """Get translation statistics."""
    organization = request.user.organization

    # Overall statistics
    total_translations = Translation.objects.filter(organization=organization).count()
    approved_translations = Translation.objects.filter(
        organization=organization, is_approved=True
    ).count()

    # Language statistics
    language_stats = []
    for language in Language.objects.filter(supported_organizations=organization):
        total = Translation.objects.filter(
            organization=organization, language=language
        ).count()
        approved = Translation.objects.filter(
            organization=organization, language=language, is_approved=True
        ).count()

        language_stats.append(
            {
                "language": language.name,
                "code": language.code,
                "total": total,
                "approved": approved,
                "completeness": (approved / total * 100) if total > 0 else 0,
            }
        )

    # Recent activity
    recent_translations = Translation.objects.filter(
        organization=organization
    ).order_by("-updated_at")[:10]

    statistics = {
        "total_translations": total_translations,
        "approved_translations": approved_translations,
        "approval_rate": (
            (approved_translations / total_translations * 100)
            if total_translations > 0
            else 0
        ),
        "language_stats": language_stats,
        "recent_translations": [
            {
                "id": str(t.id),
                "key": t.key,
                "language": t.language.name,
                "type": t.translation_type,
                "is_approved": t.is_approved,
                "updated_at": t.updated_at.isoformat(),
            }
            for t in recent_translations
        ],
    }

    return JsonResponse(statistics)
