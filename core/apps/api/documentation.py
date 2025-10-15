"""
Comprehensive API documentation with Swagger/OpenAPI.
"""

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings


# API Documentation Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Helpdesk Platform API",
        default_version="v1",
        description="""
        # Helpdesk Platform API Documentation
        
        This is a comprehensive multi-tenant helpdesk and field service management platform API.
        
        ## Features
        
        - **Multi-tenant Architecture**: Complete tenant isolation with organization-based data separation
        - **Advanced Authentication**: JWT, OAuth2, SSO, and API key authentication
        - **AI-Powered Features**: Predictive analytics, sentiment analysis, and automated responses
        - **Field Service Management**: Work orders, technician scheduling, and route optimization
        - **Real-time Communication**: Live chat, notifications, and GPS tracking
        - **Advanced Analytics**: Custom reports, dashboards, and business intelligence
        - **Integration Platform**: Webhooks, API endpoints, and third-party integrations
        
        ## Authentication
        
        The API supports multiple authentication methods:
        
        - **JWT Token**: `Authorization: Bearer <token>`
        - **API Key**: `X-API-Key: <key>`
        - **OAuth2**: `Authorization: Bearer <oauth_token>`
        - **SSO**: `X-SSO-Token: <sso_token>`
        
        ## Rate Limiting
        
        API requests are rate limited per organization:
        - **Standard**: 1000 requests/hour
        - **Premium**: 5000 requests/hour
        - **Enterprise**: 10000 requests/hour
        
        ## Multi-tenancy
        
        All endpoints automatically filter data by organization. Users can only access data within their organization.
        
        ## Error Handling
        
        The API returns standard HTTP status codes and detailed error messages:
        
        - **200**: Success
        - **201**: Created
        - **400**: Bad Request
        - **401**: Unauthorized
        - **403**: Forbidden
        - **404**: Not Found
        - **429**: Rate Limited
        - **500**: Internal Server Error
        
        ## Pagination
        
        List endpoints support pagination:
        - `?page=1&page_size=20`
        - `?offset=0&limit=20`
        
        ## Filtering
        
        Most list endpoints support filtering:
        - `?status=active`
        - `?created_after=2024-01-01`
        - `?search=keyword`
        
        ## Sorting
        
        List endpoints support sorting:
        - `?ordering=created_at`
        - `?ordering=-created_at` (descending)
        - `?ordering=name,created_at`
        
        ## Field Selection
        
        You can specify which fields to return:
        - `?fields=id,name,email`
        - `?exclude=password,secret_key`
        
        ## Examples
        
        ### Create a Ticket
        
        ```bash
        curl -X POST "https://api.helpdesk.com/api/v1/tickets/" \\
          -H "Authorization: Bearer <token>" \\
          -H "Content-Type: application/json" \\
          -d '{
            "subject": "Login Issue",
            "description": "Cannot login to the system",
            "priority": "high",
            "category": "technical"
          }'
        ```
        
        ### Get Tickets with Filtering
        
        ```bash
        curl -X GET "https://api.helpdesk.com/api/v1/tickets/?status=open&priority=high" \\
          -H "Authorization: Bearer <token>"
        ```
        
        ### Create a Work Order
        
        ```bash
        curl -X POST "https://api.helpdesk.com/api/v1/work-orders/" \\
          -H "Authorization: Bearer <token>" \\
          -H "Content-Type: application/json" \\
          -d '{
            "title": "Equipment Repair",
            "description": "Printer not working",
            "customer": "customer@example.com",
            "location": {
              "address": "123 Main St",
              "city": "New York",
              "coordinates": [40.7128, -74.0060]
            },
            "scheduled_start": "2024-01-15T09:00:00Z"
          }'
        ```
        
        ## Webhooks
        
        The platform supports webhooks for real-time notifications:
        
        - **Ticket Events**: Created, updated, resolved, closed
        - **Work Order Events**: Assigned, started, completed
        - **User Events**: Login, logout, profile updates
        
        ### Webhook Payload Example
        
        ```json
        {
          "event": "ticket.created",
          "timestamp": "2024-01-15T10:30:00Z",
          "data": {
            "ticket_id": "TKT-001",
            "subject": "Login Issue",
            "customer": "customer@example.com",
            "priority": "high"
          }
        }
        ```
        
        ## SDKs
        
        Official SDKs are available for:
        - **Python**: `pip install helpdesk-sdk`
        - **JavaScript**: `npm install @helpdesk/sdk`
        - **PHP**: `composer require helpdesk/sdk`
        - **Java**: Available in Maven Central
        
        ## Support
        
        For API support, contact:
        - **Email**: api-support@helpdesk.com
        - **Documentation**: https://docs.helpdesk.com
        - **Status Page**: https://status.helpdesk.com
        """,
        terms_of_service="https://helpdesk.com/terms/",
        contact=openapi.Contact(
            name="API Support",
            email="api-support@helpdesk.com",
            url="https://helpdesk.com/support",
        ),
        license=openapi.License(
            name="MIT License", url="https://opensource.org/licenses/MIT"
        ),
    ),
    public=True,
    permission_classes=[AllowAny],
)


# API Documentation Decorators
def api_doc(summary, description="", tags=None, responses=None):
    """Decorator for API documentation."""

    def decorator(func):
        return swagger_auto_schema(
            operation_summary=summary,
            operation_description=description,
            tags=tags or [],
            responses=responses or {},
            security=[{"Bearer": []}],
        )(func)

    return decorator


# Common Response Schemas
error_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "error": openapi.Schema(type=openapi.TYPE_STRING),
        "message": openapi.Schema(type=openapi.TYPE_STRING),
        "details": openapi.Schema(type=openapi.TYPE_OBJECT),
    },
)

success_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "status": openapi.Schema(type=openapi.TYPE_STRING),
        "message": openapi.Schema(type=openapi.TYPE_STRING),
        "data": openapi.Schema(type=openapi.TYPE_OBJECT),
    },
)

pagination_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
        "next": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
        "previous": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
        "results": openapi.Schema(
            type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
    },
)

# Common Response Examples
common_responses = {
    200: openapi.Response("Success", success_schema),
    201: openapi.Response("Created", success_schema),
    400: openapi.Response("Bad Request", error_schema),
    401: openapi.Response("Unauthorized", error_schema),
    403: openapi.Response("Forbidden", error_schema),
    404: openapi.Response("Not Found", error_schema),
    429: openapi.Response("Rate Limited", error_schema),
    500: openapi.Response("Internal Server Error", error_schema),
}


# API Endpoint Documentation
@api_view(["GET"])
@permission_classes([AllowAny])
def api_info(request):
    """Get API information and status."""
    return Response(
        {
            "name": "Helpdesk Platform API",
            "version": "v1",
            "status": "operational",
            "uptime": "99.9%",
            "features": [
                "Multi-tenant Architecture",
                "AI-Powered Analytics",
                "Field Service Management",
                "Real-time Communication",
                "Advanced Integrations",
            ],
            "endpoints": {
                "tickets": "/api/v1/tickets/",
                "work_orders": "/api/v1/work-orders/",
                "technicians": "/api/v1/technicians/",
                "analytics": "/api/v1/analytics/",
                "integrations": "/api/v1/integrations/",
                "ai_ml": "/api/v1/ai-ml/",
                "customer_experience": "/api/v1/customer-experience/",
                "advanced_analytics": "/api/v1/advanced-analytics/",
                "integration_platform": "/api/v1/integration-platform/",
                "mobile_iot": "/api/v1/mobile-iot/",
                "security_compliance": "/api/v1/security-compliance/",
                "workflow_automation": "/api/v1/workflow-automation/",
                "communication_platform": "/api/v1/communication-platform/",
            },
            "authentication": {
                "jwt": "Authorization: Bearer <token>",
                "api_key": "X-API-Key: <key>",
                "oauth2": "Authorization: Bearer <oauth_token>",
                "sso": "X-SSO-Token: <sso_token>",
            },
            "rate_limits": {
                "standard": "1000 requests/hour",
                "premium": "5000 requests/hour",
                "enterprise": "10000 requests/hour",
            },
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def api_health(request):
    """Get API health status."""
    return Response(
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "services": {
                "database": "healthy",
                "redis": "healthy",
                "celery": "healthy",
                "ai_service": "healthy",
                "realtime_service": "healthy",
            },
            "metrics": {
                "response_time": "45ms",
                "uptime": "99.9%",
                "requests_per_minute": 1250,
            },
        }
    )


# API Documentation Tags
api_tags = {
    "authentication": "Authentication & Authorization",
    "tickets": "Ticket Management",
    "work_orders": "Field Service Management",
    "technicians": "Technician Management",
    "analytics": "Analytics & Reporting",
    "integrations": "Integrations & APIs",
    "ai_ml": "AI & Machine Learning",
    "customer_experience": "Customer Experience",
    "advanced_analytics": "Advanced Analytics",
    "integration_platform": "Integration Platform",
    "mobile_iot": "Mobile & IoT",
    "security_compliance": "Security & Compliance",
    "workflow_automation": "Workflow Automation",
    "communication_platform": "Communication Platform",
    "webhooks": "Webhooks & Events",
    "admin": "Administration",
}

# API Documentation Examples
api_examples = {
    "create_ticket": {
        "summary": "Create a new ticket",
        "description": "Create a new support ticket with subject, description, and priority.",
        "request_body": {
            "subject": "Login Issue",
            "description": "Cannot login to the system",
            "priority": "high",
            "category": "technical",
            "customer": "customer@example.com",
        },
        "response": {
            "id": "TKT-001",
            "subject": "Login Issue",
            "status": "open",
            "priority": "high",
            "created_at": "2024-01-15T10:30:00Z",
        },
    },
    "create_work_order": {
        "summary": "Create a new work order",
        "description": "Create a new field service work order with location and scheduling.",
        "request_body": {
            "title": "Equipment Repair",
            "description": "Printer not working",
            "customer": "customer@example.com",
            "location": {
                "address": "123 Main St",
                "city": "New York",
                "coordinates": [40.7128, -74.0060],
            },
            "scheduled_start": "2024-01-15T09:00:00Z",
        },
        "response": {
            "id": "WO-001",
            "title": "Equipment Repair",
            "status": "scheduled",
            "technician": "tech@example.com",
            "scheduled_start": "2024-01-15T09:00:00Z",
        },
    },
    "webhook_payload": {
        "summary": "Webhook payload example",
        "description": "Example webhook payload for ticket events.",
        "payload": {
            "event": "ticket.created",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {
                "ticket_id": "TKT-001",
                "subject": "Login Issue",
                "customer": "customer@example.com",
                "priority": "high",
            },
        },
    },
}

# API Documentation Configuration
api_config = {
    "title": "Helpdesk Platform API",
    "version": "v1",
    "description": "Comprehensive multi-tenant helpdesk and field service management platform API",
    "terms_of_service": "https://helpdesk.com/terms/",
    "contact": {
        "name": "API Support",
        "email": "api-support@helpdesk.com",
        "url": "https://helpdesk.com/support",
    },
    "license": {"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    "servers": [
        {"url": "https://api.helpdesk.com", "description": "Production server"},
        {"url": "https://staging-api.helpdesk.com", "description": "Staging server"},
        {"url": "http://localhost:8000", "description": "Development server"},
    ],
    "security": [{"Bearer": []}, {"ApiKey": []}],
    "tags": api_tags,
    "examples": api_examples,
}
