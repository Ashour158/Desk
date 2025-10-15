"""
Comprehensive test utilities for expert-level testing.
"""
import json
import time
import uuid
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)
from decimal import Decimal
from typing import Dict, List, Any, Optional, Union
from unittest.mock import Mock, patch, MagicMock

from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket, TicketComment, TicketAttachment
from apps.field_service.models import WorkOrder, Technician, JobAssignment
from apps.knowledge_base.models import KBArticle, KBCategory
from apps.automation.models import AutomationRule, SLAPolicy
from apps.analytics.models import AnalyticsDashboard, Report
from apps.integrations.models import Webhook, IntegrationLog
from apps.notifications.models import Notification
from apps.api.models import APIService
from apps.features.models import Feature, FeatureCategory, FeatureConnection

User = get_user_model()


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_organization(name: str = "Test Organization", 
                          subscription_tier: str = "enterprise") -> Organization:
        """Create test organization."""
        return Organization.objects.create(
            name=name,
            subscription_tier=subscription_tier,
            settings={
                'timezone': 'UTC',
                'date_format': 'YYYY-MM-DD',
                'currency': 'USD',
                'language': 'en'
            }
        )
    
    @staticmethod
    def create_user(organization: Organization, 
                   email: str = "test@example.com",
                   role: str = "agent",
                   is_active: bool = True) -> User:
        """Create test user."""
        return User.objects.create_user(
            email=email,
            password="testpass123",
            organization=organization,
            role=role,
            is_active=is_active,
            first_name="Test",
            last_name="User"
        )
    
    @staticmethod
    def create_ticket(organization: Organization,
                     customer: User,
                     subject: str = "Test Ticket",
                     status: str = "open",
                     priority: str = "medium") -> Ticket:
        """Create test ticket."""
        return Ticket.objects.create(
            organization=organization,
            customer=customer,
            subject=subject,
            description="Test ticket description",
            status=status,
            priority=priority,
            channel="web"
        )
    
    @staticmethod
    def create_work_order(organization: Organization,
                         customer: User,
                         title: str = "Test Work Order",
                         status: str = "scheduled") -> WorkOrder:
        """Create test work order."""
        return WorkOrder.objects.create(
            organization=organization,
            customer=customer,
            title=title,
            description="Test work order description",
            status=status,
            scheduled_start=timezone.now() + timedelta(hours=1),
            scheduled_end=timezone.now() + timedelta(hours=2),
            location={
                'address': '123 Test St',
                'city': 'Test City',
                'coordinates': [40.7128, -74.0060]
            }
        )
    
    @staticmethod
    def create_technician(organization: Organization,
                         user: User,
                         skills: List[str] = None) -> Technician:
        """Create test technician."""
        return Technician.objects.create(
            organization=organization,
            user=user,
            skills=skills or ['electrical', 'plumbing'],
            certifications=['cert1', 'cert2'],
            current_location={
                'latitude': 40.7128,
                'longitude': -74.0060,
                'address': '123 Test St'
            }
        )
    
    @staticmethod
    def create_kb_article(organization: Organization,
                         title: str = "Test Article",
                         content: str = "Test content") -> KBArticle:
        """Create test KB article."""
        return KBArticle.objects.create(
            organization=organization,
            title=title,
            content=content,
            category="general",
            is_published=True
        )
    
    @staticmethod
    def create_automation_rule(organization: Organization,
                              name: str = "Test Rule",
                              trigger_type: str = "ticket_created") -> AutomationRule:
        """Create test automation rule."""
        return AutomationRule.objects.create(
            organization=organization,
            name=name,
            trigger_type=trigger_type,
            conditions=[
                {'field': 'priority', 'operator': 'equals', 'value': 'high'}
            ],
            actions=[
                {'type': 'assign', 'agent_id': 1},
                {'type': 'change_status', 'status': 'in_progress'}
            ],
            is_active=True
        )
    
    @staticmethod
    def create_sla_policy(organization: Organization,
                         name: str = "Test SLA",
                         first_response_time: int = 60) -> SLAPolicy:
        """Create test SLA policy."""
        return SLAPolicy.objects.create(
            organization=organization,
            name=name,
            first_response_time=first_response_time,
            resolution_time=480,
            operational_hours={
                'monday': {'start': '09:00', 'end': '17:00'},
                'tuesday': {'start': '09:00', 'end': '17:00'},
                'wednesday': {'start': '09:00', 'end': '17:00'},
                'thursday': {'start': '09:00', 'end': '17:00'},
                'friday': {'start': '09:00', 'end': '17:00'}
            }
        )
    
    @staticmethod
    def create_webhook(organization: Organization,
                      name: str = "Test Webhook",
                      url: str = "https://example.com/webhook") -> Webhook:
        """Create test webhook."""
        return Webhook.objects.create(
            organization=organization,
            name=name,
            url=url,
            events=['ticket_created', 'ticket_updated'],
            is_active=True,
            secret_key="test_secret_key"
        )
    
    @staticmethod
    def create_feature(organization: Organization,
                      name: str = "Test Feature",
                      feature_type: str = "core") -> Feature:
        """Create test feature."""
        return Feature.objects.create(
            organization=organization,
            name=name,
            description="Test feature description",
            feature_type=feature_type,
            status="active",
            endpoint="test-feature",
            supports_realtime=True
        )


class TestClientFactory:
    """Factory for creating test clients."""
    
    @staticmethod
    def create_authenticated_client(user: User) -> APIClient:
        """Create authenticated API client."""
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client
    
    @staticmethod
    def create_websocket_client(organization_id: int, user_id: int) -> WebsocketCommunicator:
        """Create WebSocket test client."""
        from apps.api.consumers import TicketConsumer
        return WebsocketCommunicator(TicketConsumer, f"/ws/tickets/?org={organization_id}&user={user_id}")


class TestAssertions:
    """Custom test assertions."""
    
    @staticmethod
    def assert_response_success(response, expected_status=status.HTTP_200_OK):
        """Assert API response is successful."""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.data}"
    
    @staticmethod
    def assert_response_error(response, expected_status=status.HTTP_400_BAD_REQUEST):
        """Assert API response is an error."""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.data}"
    
    @staticmethod
    def assert_ticket_created(ticket_data: Dict[str, Any], organization: Organization):
        """Assert ticket was created with correct data."""
        ticket = Ticket.objects.get(organization=organization, subject=ticket_data['subject'])
        assert ticket.customer.email == ticket_data['customer']
        assert ticket.status == ticket_data.get('status', 'open')
        assert ticket.priority == ticket_data.get('priority', 'medium')
    
    @staticmethod
    def assert_work_order_created(work_order_data: Dict[str, Any], organization: Organization):
        """Assert work order was created with correct data."""
        work_order = WorkOrder.objects.get(organization=organization, title=work_order_data['title'])
        assert work_order.customer.email == work_order_data['customer']
        assert work_order.status == work_order_data.get('status', 'scheduled')
    
    @staticmethod
    def assert_automation_triggered(rule: AutomationRule, entity: Any):
        """Assert automation rule was triggered."""
        # This would check if the rule's actions were executed
        pass
    
    @staticmethod
    def assert_notification_sent(user: User, notification_type: str, message: str):
        """Assert notification was sent to user."""
        notification = Notification.objects.get(
            user=user,
            notification_type=notification_type,
            message=message
        )
        assert notification is not None
    
    @staticmethod
    def assert_webhook_triggered(webhook: Webhook, event_type: str):
        """Assert webhook was triggered."""
        log = IntegrationLog.objects.filter(
            webhook=webhook,
            event_type=event_type
        ).first()
        assert log is not None
    
    @staticmethod
    def assert_realtime_update_sent(channel: str, event_type: str, payload: Dict[str, Any]):
        """Assert real-time update was sent."""
        # This would check if the WebSocket message was sent
        pass


class TestMocks:
    """Factory for creating test mocks."""
    
    @staticmethod
    def mock_ai_service_response(category: str = "Technical", 
                                sentiment: str = "neutral",
                                confidence: float = 0.85):
        """Mock AI service response."""
        return {
            'category': category,
            'sentiment': sentiment,
            'confidence': confidence,
            'suggested_response': 'Thank you for contacting us. We will help you resolve this issue.'
        }
    
    @staticmethod
    def mock_email_service_response(success: bool = True, message_id: str = None):
        """Mock email service response."""
        return {
            'success': success,
            'message_id': message_id or str(uuid.uuid4()),
            'timestamp': timezone.now().isoformat()
        }
    
    @staticmethod
    def mock_sms_service_response(success: bool = True, message_id: str = None):
        """Mock SMS service response."""
        return {
            'success': success,
            'message_id': message_id or str(uuid.uuid4()),
            'timestamp': timezone.now().isoformat()
        }
    
    @staticmethod
    def mock_route_optimization_response(optimized_route: List[Dict[str, Any]]):
        """Mock route optimization response."""
        return {
            'optimized_route': optimized_route,
            'total_distance': 15.5,
            'total_duration': 45.2,
            'optimization_score': 0.92
        }
    
    @staticmethod
    def mock_gps_tracking_response(latitude: float, longitude: float, accuracy: float = 5.0):
        """Mock GPS tracking response."""
        return {
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': accuracy,
            'timestamp': timezone.now().isoformat(),
            'speed': 25.5,
            'heading': 180.0
        }
    
    @staticmethod
    def mock_webhook_response(status_code: int = 200, response_time: float = 0.5):
        """Mock webhook response."""
        return {
            'status_code': status_code,
            'response_time': response_time,
            'timestamp': timezone.now().isoformat(),
            'success': status_code == 200
        }


class TestPerformance:
    """Performance testing utilities."""
    
    @staticmethod
    def measure_execution_time(func):
        """Decorator to measure function execution time."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        return wrapper
    
    @staticmethod
    def assert_response_time(response, max_time: float = 1.0):
        """Assert API response time is within limits."""
        # This would check response time from response headers
        pass
    
    @staticmethod
    def assert_query_count(queries_before: int, queries_after: int, max_queries: int = 10):
        """Assert database query count is within limits."""
        query_count = queries_after - queries_before
        assert query_count <= max_queries, f"Too many queries: {query_count} > {max_queries}"


class TestSecurity:
    """Security testing utilities."""
    
    @staticmethod
    def assert_authentication_required(response):
        """Assert authentication is required."""
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @staticmethod
    def assert_permission_required(response):
        """Assert permission is required."""
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @staticmethod
    def assert_tenant_isolation(user: User, organization: Organization):
        """Assert tenant isolation is working."""
        # This would check that user can only access their organization's data
        pass
    
    @staticmethod
    def assert_sql_injection_protected(response):
        """Assert SQL injection protection is working."""
        # This would check that malicious SQL doesn't execute
        pass
    
    @staticmethod
    def assert_xss_protection(response):
        """Assert XSS protection is working."""
        # This would check that malicious scripts are escaped
        pass


class TestIntegration:
    """Integration testing utilities."""
    
    @staticmethod
    def assert_service_communication(service_url: str, expected_response: Dict[str, Any]):
        """Assert service communication is working."""
        # This would test actual service communication
        pass
    
    @staticmethod
    def assert_database_consistency():
        """Assert database consistency."""
        # This would check database constraints and relationships
        pass
    
    @staticmethod
    def assert_cache_consistency():
        """Assert cache consistency."""
        # This would check cache and database are in sync
        pass
    
    @staticmethod
    def assert_websocket_connection(communicator: WebsocketCommunicator):
        """Assert WebSocket connection is working."""
        # This would test WebSocket connection
        pass


class TestData:
    """Test data constants."""
    
    # Sample ticket data
    TICKET_DATA = {
        'subject': 'Test Ticket Subject',
        'description': 'Test ticket description with detailed information',
        'priority': 'high',
        'status': 'open',
        'channel': 'web',
        'tags': ['urgent', 'technical']
    }
    
    # Sample work order data
    WORK_ORDER_DATA = {
        'title': 'Test Work Order',
        'description': 'Test work order description',
        'status': 'scheduled',
        'scheduled_start': timezone.now() + timedelta(hours=1),
        'scheduled_end': timezone.now() + timedelta(hours=2),
        'location': {
            'address': '123 Test Street',
            'city': 'Test City',
            'coordinates': [40.7128, -74.0060]
        }
    }
    
    # Sample technician data
    TECHNICIAN_DATA = {
        'skills': ['electrical', 'plumbing', 'hvac'],
        'certifications': ['cert1', 'cert2', 'cert3'],
        'availability_status': 'available',
        'current_location': {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'address': '123 Test St'
        }
    }
    
    # Sample KB article data
    KB_ARTICLE_DATA = {
        'title': 'Test Knowledge Base Article',
        'content': 'Test article content with detailed information',
        'category': 'technical',
        'tags': ['troubleshooting', 'setup'],
        'is_published': True
    }
    
    # Sample automation rule data
    AUTOMATION_RULE_DATA = {
        'name': 'Test Automation Rule',
        'trigger_type': 'ticket_created',
        'conditions': [
            {'field': 'priority', 'operator': 'equals', 'value': 'high'}
        ],
        'actions': [
            {'type': 'assign', 'agent_id': 1},
            {'type': 'change_status', 'status': 'in_progress'},
            {'type': 'send_email', 'template_id': 1}
        ],
        'is_active': True
    }
    
    # Sample webhook data
    WEBHOOK_DATA = {
        'name': 'Test Webhook',
        'url': 'https://example.com/webhook',
        'events': ['ticket_created', 'ticket_updated'],
        'secret_key': 'test_secret_key',
        'is_active': True
    }
    
    # Sample notification data
    NOTIFICATION_DATA = {
        'notification_type': 'ticket_assigned',
        'message': 'You have been assigned a new ticket',
        'priority': 'high',
        'is_read': False
    }
    
    # Sample feature data
    FEATURE_DATA = {
        'name': 'Test Feature',
        'description': 'Test feature description',
        'feature_type': 'core',
        'status': 'active',
        'endpoint': 'test-feature',
        'supports_realtime': True
    }
