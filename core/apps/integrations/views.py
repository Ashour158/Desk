"""
Integration views for helpdesk platform.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json
import hmac
import hashlib
import requests
import logging

from .models import Webhook, Integration, PaymentGateway, ThirdPartyAPI
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


@login_required
def integrations_list(request):
    """List all integrations for the organization."""
    organization = request.user.organization

    # Get available integrations
    available_integrations = [
        {
            "id": "stripe",
            "name": "Stripe",
            "description": "Payment processing and billing",
            "icon": "fas fa-credit-card",
            "category": "payment",
            "is_connected": PaymentGateway.objects.filter(
                organization=organization, provider="stripe", is_active=True
            ).exists(),
        },
        {
            "id": "twilio",
            "name": "Twilio",
            "description": "SMS and voice communications",
            "icon": "fas fa-sms",
            "category": "communication",
            "is_connected": ThirdPartyAPI.objects.filter(
                organization=organization, provider="twilio", is_active=True
            ).exists(),
        },
        {
            "id": "sendgrid",
            "name": "SendGrid",
            "description": "Email delivery service",
            "icon": "fas fa-envelope",
            "category": "communication",
            "is_connected": ThirdPartyAPI.objects.filter(
                organization=organization, provider="sendgrid", is_active=True
            ).exists(),
        },
        {
            "id": "slack",
            "name": "Slack",
            "description": "Team communication and notifications",
            "icon": "fab fa-slack",
            "category": "communication",
            "is_connected": ThirdPartyAPI.objects.filter(
                organization=organization, provider="slack", is_active=True
            ).exists(),
        },
        {
            "id": "zapier",
            "name": "Zapier",
            "description": "Automation and workflow integration",
            "icon": "fas fa-bolt",
            "category": "automation",
            "is_connected": ThirdPartyAPI.objects.filter(
                organization=organization, provider="zapier", is_active=True
            ).exists(),
        },
        {
            "id": "google_calendar",
            "name": "Google Calendar",
            "description": "Calendar integration for scheduling",
            "icon": "fas fa-calendar",
            "category": "productivity",
            "is_connected": ThirdPartyAPI.objects.filter(
                organization=organization, provider="google_calendar", is_active=True
            ).exists(),
        },
    ]

    # Get webhooks
    webhooks = Webhook.objects.filter(organization=organization).order_by("-created_at")

    context = {
        "available_integrations": available_integrations,
        "webhooks": webhooks,
        "can_manage": request.user.role in ["agent", "admin"],
    }

    return render(request, "integrations/list.html", context)


@login_required
def integration_detail(request, integration_id):
    """View integration details and configuration."""
    integration = get_object_or_404(
        Integration, id=integration_id, organization=request.user.organization
    )

    context = {
        "integration": integration,
        "can_manage": request.user.role in ["agent", "admin"],
    }

    return render(request, "integrations/detail.html", context)


@login_required
@require_http_methods(["POST"])
def connect_integration(request, integration_id):
    """Connect to an integration."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    try:
        data = json.loads(request.body)
        organization = request.user.organization

        if integration_id == "stripe":
            return connect_stripe(organization, data)
        elif integration_id == "twilio":
            return connect_twilio(organization, data)
        elif integration_id == "sendgrid":
            return connect_sendgrid(organization, data)
        elif integration_id == "slack":
            return connect_slack(organization, data)
        elif integration_id == "zapier":
            return connect_zapier(organization, data)
        elif integration_id == "google_calendar":
            return connect_google_calendar(organization, data)
        else:
            return JsonResponse({"error": "Unknown integration"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def connect_stripe(organization, data):
    """Connect Stripe payment gateway."""
    try:
        api_key = data.get("api_key")
        webhook_secret = data.get("webhook_secret")

        if not api_key:
            return JsonResponse({"error": "API key required"}, status=400)

        # Test Stripe connection
        import stripe

        stripe.api_key = api_key

        # Test API call
        stripe.Account.retrieve()

        # Save integration
        payment_gateway, created = PaymentGateway.objects.get_or_create(
            organization=organization,
            provider="stripe",
            defaults={
                "name": "Stripe",
                "api_key": api_key,
                "webhook_secret": webhook_secret,
                "is_active": True,
            },
        )

        if not created:
            payment_gateway.api_key = api_key
            payment_gateway.webhook_secret = webhook_secret
            payment_gateway.is_active = True
            payment_gateway.save()

        return JsonResponse(
            {"success": True, "message": "Stripe connected successfully"}
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"Stripe connection failed: {str(e)}"}, status=400
        )


def connect_twilio(organization, data):
    """Connect Twilio SMS service."""
    try:
        account_sid = data.get("account_sid")
        auth_token = data.get("auth_token")
        phone_number = data.get("phone_number")

        if not all([account_sid, auth_token, phone_number]):
            return JsonResponse(
                {"error": "All Twilio credentials required"}, status=400
            )

        # Test Twilio connection
        from twilio.rest import Client

        client = Client(account_sid, auth_token)

        # Test API call
        client.api.accounts(account_sid).fetch()

        # Save integration
        api, created = ThirdPartyAPI.objects.get_or_create(
            organization=organization,
            provider="twilio",
            defaults={
                "name": "Twilio",
                "api_key": account_sid,
                "api_secret": auth_token,
                "additional_config": {"phone_number": phone_number},
                "is_active": True,
            },
        )

        if not created:
            api.api_key = account_sid
            api.api_secret = auth_token
            api.additional_config = {"phone_number": phone_number}
            api.is_active = True
            api.save()

        return JsonResponse(
            {"success": True, "message": "Twilio connected successfully"}
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"Twilio connection failed: {str(e)}"}, status=400
        )


def connect_sendgrid(organization, data):
    """Connect SendGrid email service."""
    try:
        api_key = data.get("api_key")

        if not api_key:
            return JsonResponse({"error": "API key required"}, status=400)

        # Test SendGrid connection
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            "https://api.sendgrid.com/v3/user/profile", headers=headers, timeout=30
        )
        response.raise_for_status()

        # Save integration
        api, created = ThirdPartyAPI.objects.get_or_create(
            organization=organization,
            provider="sendgrid",
            defaults={"name": "SendGrid", "api_key": api_key, "is_active": True},
        )

        if not created:
            api.api_key = api_key
            api.is_active = True
            api.save()

        return JsonResponse(
            {"success": True, "message": "SendGrid connected successfully"}
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"SendGrid connection failed: {str(e)}"}, status=400
        )


def connect_slack(organization, data):
    """Connect Slack workspace."""
    try:
        webhook_url = data.get("webhook_url")

        if not webhook_url:
            return JsonResponse({"error": "Webhook URL required"}, status=400)

        # Test Slack webhook
        payload = {"text": "Test message from Helpdesk Platform"}

        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()

        # Save integration
        api, created = ThirdPartyAPI.objects.get_or_create(
            organization=organization,
            provider="slack",
            defaults={"name": "Slack", "webhook_url": webhook_url, "is_active": True},
        )

        if not created:
            api.webhook_url = webhook_url
            api.is_active = True
            api.save()

        return JsonResponse(
            {"success": True, "message": "Slack connected successfully"}
        )

    except Exception as e:
        return JsonResponse({"error": f"Slack connection failed: {str(e)}"}, status=400)


def connect_zapier(organization, data):
    """Connect Zapier automation."""
    try:
        webhook_url = data.get("webhook_url")

        if not webhook_url:
            return JsonResponse({"error": "Webhook URL required"}, status=400)

        # Save integration
        api, created = ThirdPartyAPI.objects.get_or_create(
            organization=organization,
            provider="zapier",
            defaults={"name": "Zapier", "webhook_url": webhook_url, "is_active": True},
        )

        if not created:
            api.webhook_url = webhook_url
            api.is_active = True
            api.save()

        return JsonResponse(
            {"success": True, "message": "Zapier connected successfully"}
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"Zapier connection failed: {str(e)}"}, status=400
        )


def connect_google_calendar(organization, data):
    """Connect Google Calendar."""
    try:
        # This would typically involve OAuth2 flow
        # For now, we'll just save the integration
        api, created = ThirdPartyAPI.objects.get_or_create(
            organization=organization,
            provider="google_calendar",
            defaults={"name": "Google Calendar", "is_active": True},
        )

        if not created:
            api.is_active = True
            api.save()

        return JsonResponse(
            {"success": True, "message": "Google Calendar connected successfully"}
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"Google Calendar connection failed: {str(e)}"}, status=400
        )


@login_required
@require_http_methods(["POST"])
def disconnect_integration(request, integration_id):
    """Disconnect an integration."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    try:
        organization = request.user.organization

        if integration_id == "stripe":
            PaymentGateway.objects.filter(
                organization=organization, provider="stripe"
            ).update(is_active=False)
        else:
            ThirdPartyAPI.objects.filter(
                organization=organization, provider=integration_id
            ).update(is_active=False)

        return JsonResponse(
            {"success": True, "message": "Integration disconnected successfully"}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def webhook_list(request):
    """List webhooks for the organization."""
    organization = request.user.organization

    webhooks = Webhook.objects.filter(organization=organization).order_by("-created_at")

    context = {
        "webhooks": webhooks,
        "can_manage": request.user.role in ["agent", "admin"],
    }

    return render(request, "integrations/webhook_list.html", context)


@login_required
@require_http_methods(["POST"])
def create_webhook(request):
    """Create a new webhook."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    try:
        data = json.loads(request.body)

        webhook = Webhook.objects.create(
            organization=request.user.organization,
            name=data.get("name"),
            url=data.get("url"),
            events=data.get("events", []),
            secret_key=data.get("secret_key"),
            is_active=data.get("is_active", True),
        )

        return JsonResponse({"success": True, "webhook_id": str(webhook.id)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def test_webhook(request, webhook_id):
    """Test a webhook."""
    webhook = get_object_or_404(
        Webhook, id=webhook_id, organization=request.user.organization
    )

    try:
        # Send test payload
        payload = {
            "event": "test",
            "timestamp": timezone.now().isoformat(),
            "data": {"message": "This is a test webhook from Helpdesk Platform"},
        }

        # Add signature if secret key is set
        headers = {}
        if webhook.secret_key:
            signature = hmac.new(
                webhook.secret_key.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256,
            ).hexdigest()
            headers["X-Signature"] = f"sha256={signature}"

        response = requests.post(webhook.url, json=payload, headers=headers, timeout=30)

        return JsonResponse(
            {
                "success": True,
                "status_code": response.status_code,
                "response": response.text,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def webhook_receiver(request, webhook_id):
    """Receive webhook from external services."""
    try:
        webhook = Webhook.objects.get(id=webhook_id, is_active=True)

        # Verify signature if secret key is set
        if webhook.secret_key:
            signature = request.headers.get("X-Signature")
            if not signature:
                return HttpResponse("Missing signature", status=400)

            expected_signature = hmac.new(
                webhook.secret_key.encode(), request.body, hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, f"sha256={expected_signature}"):
                return HttpResponse("Invalid signature", status=400)

        # Process webhook
        data = json.loads(request.body)
        process_webhook.delay(webhook.id, data)

        return HttpResponse("OK", status=200)

    except Webhook.DoesNotExist:
        return HttpResponse("Webhook not found", status=404)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse("Internal error", status=500)


@login_required
def payment_gateway_config(request):
    """Configure payment gateway settings."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    organization = request.user.organization

    # Get Stripe configuration
    stripe_config = PaymentGateway.objects.filter(
        organization=organization, provider="stripe", is_active=True
    ).first()

    context = {
        "stripe_config": stripe_config,
        "can_manage": request.user.role in ["agent", "admin"],
    }

    return render(request, "integrations/payment_config.html", context)


@login_required
@require_http_methods(["POST"])
def create_payment_intent(request):
    """Create payment intent for Stripe."""
    if request.user.role not in ["agent", "admin"]:
        return JsonResponse({"error": "Permission denied"}, status=403)

    try:
        data = json.loads(request.body)

        # Get Stripe configuration
        stripe_config = PaymentGateway.objects.filter(
            organization=request.user.organization, provider="stripe", is_active=True
        ).first()

        if not stripe_config:
            return JsonResponse({"error": "Stripe not configured"}, status=400)

        # Create payment intent
        import stripe

        stripe.api_key = stripe_config.api_key

        intent = stripe.PaymentIntent.create(
            amount=int(data.get("amount", 0) * 100),  # Convert to cents
            currency=data.get("currency", "usd"),
            metadata={
                "organization_id": str(request.user.organization.id),
                "user_id": str(request.user.id),
            },
        )

        return JsonResponse({"success": True, "client_secret": intent.client_secret})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def integration_logs(request, integration_id):
    """View integration logs."""
    integration = get_object_or_404(
        Integration, id=integration_id, organization=request.user.organization
    )

    # Get logs (this would be implemented based on your logging system)
    logs = []

    context = {"integration": integration, "logs": logs}

    return render(request, "integrations/logs.html", context)
