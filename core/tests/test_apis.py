"""
Comprehensive API tests for all endpoints and serializers.
"""
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, Mock, MagicMock

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

from .test_utils import (
    TestDataFactory, TestClientFactory, TestAssertions, 
    TestMocks, TestPerformance, TestSecurity
)

User = get_user_model()


class AuthenticationAPITest(APITestCase):
    """Test authentication API endpoints with proper isolation."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.client = APIClient()
    
    def tearDown(self):
        # Clean up test data to prevent isolation issues
        User.objects.all().delete()
        Organization.objects.all().delete()
        super().tearDown()
    
    def test_user_registration_with_valid_data(self):
        """Test user registration with valid data and proper error handling."""
        url = reverse('api:user-register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'organization': self.organization.id
        }
        
        try:
            response = self.client.post(url, data, format='json')
            TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
            
            # Verify user was created
            self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        except Exception as e:
            self.fail(f"User registration failed: {e}")
    
    def test_user_registration_with_invalid_data(self):
        """Test user registration with invalid data returns appropriate errors."""
        url = reverse('api:user-register')
        data = {
            'email': 'invalid-email',
            'password': '123',  # Too short
            'first_name': '',
            'last_name': '',
            'organization': 99999  # Non-existent organization
        }
        
        try:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            
            # Verify user was not created
            self.assertFalse(User.objects.filter(email='invalid-email').exists())
        except Exception as e:
            self.fail(f"User registration validation failed: {e}")
    
    def test_user_login(self):
        """Test user login."""
        url = reverse('api:user-login')
        data = {
            'email': self.user.email,
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify tokens are returned
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh(self):
        """Test token refresh."""
        refresh = RefreshToken.for_user(self.user)
        url = reverse('api:token-refresh')
        data = {'refresh': str(refresh)}
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_200_OK)
        
        # Verify new access token is returned
        self.assertIn('access', response.data)
    
    def test_user_logout(self):
        """Test user logout."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('api:user-logout')
        data = {'refresh': str(refresh)}
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_200_OK)
    
    def test_password_reset(self):
        """Test password reset."""
        url = reverse('api:password-reset')
        data = {'email': self.user.email}
        
        with patch('apps.accounts.tasks.send_password_reset_email.delay') as mock_task:
            response = self.client.post(url, data, format='json')
            TestAssertions.assert_response_success(response, status.HTTP_200_OK)
            mock_task.assert_called_once()
    
    def test_authentication_required(self):
        """Test authentication is required for protected endpoints."""
        url = reverse('api:ticket-list')
        response = self.client.get(url)
        TestSecurity.assert_authentication_required(response)
    
    def test_organization_isolation(self):
        """Test organization isolation in API."""
        other_org = TestDataFactory.create_organization("Other Organization")
        other_user = TestDataFactory.create_user(other_org, "other@example.com")
        
        # Login as user from different organization
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Try to access tickets from different organization
        url = reverse('api:ticket-list')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify only tickets from user's organization are returned
        tickets = response.data['results']
        for ticket in tickets:
            self.assertEqual(ticket['organization'], other_org.id)


class TicketAPITest(APITestCase):
    """Test Ticket API endpoints."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.customer = TestDataFactory.create_user(self.organization, "customer@example.com", "customer")
        self.agent = TestDataFactory.create_user(self.organization, "agent@example.com", "agent")
        self.ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        self.client = TestClientFactory.create_authenticated_client(self.agent)
    
    def test_ticket_list(self):
        """Test ticket list endpoint."""
        url = reverse('api:ticket-list')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify ticket data
        tickets = response.data['results']
        self.assertGreater(len(tickets), 0)
        
        ticket = tickets[0]
        self.assertIn('id', ticket)
        self.assertIn('subject', ticket)
        self.assertIn('status', ticket)
        self.assertIn('priority', ticket)
        self.assertIn('created_at', ticket)
    
    def test_ticket_create(self):
        """Test ticket creation."""
        url = reverse('api:ticket-list')
        data = {
            'subject': 'New Test Ticket',
            'description': 'New test ticket description',
            'priority': 'high',
            'channel': 'web',
            'customer': self.customer.id
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify ticket was created
        TestAssertions.assert_ticket_created(data, self.organization)
    
    def test_ticket_detail(self):
        """Test ticket detail endpoint."""
        url = reverse('api:ticket-detail', kwargs={'pk': self.ticket.id})
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify ticket data
        self.assertEqual(response.data['id'], self.ticket.id)
        self.assertEqual(response.data['subject'], self.ticket.subject)
        self.assertEqual(response.data['status'], self.ticket.status)
    
    def test_ticket_update(self):
        """Test ticket update."""
        url = reverse('api:ticket-detail', kwargs={'pk': self.ticket.id})
        data = {
            'status': 'in_progress',
            'priority': 'urgent',
            'assigned_agent': self.agent.id
        }
        
        response = self.client.patch(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify ticket was updated
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'in_progress')
        self.assertEqual(self.ticket.priority, 'urgent')
        self.assertEqual(self.ticket.assigned_agent, self.agent)
    
    def test_ticket_comment_create(self):
        """Test ticket comment creation."""
        url = reverse('api:ticket-comment-list', kwargs={'ticket_pk': self.ticket.id})
        data = {
            'content': 'Test comment content',
            'is_public': True
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify comment was created
        comment = TicketComment.objects.get(ticket=self.ticket)
        self.assertEqual(comment.content, 'Test comment content')
        self.assertTrue(comment.is_public)
    
    def test_ticket_attachment_upload(self):
        """Test ticket attachment upload."""
        url = reverse('api:ticket-attachment-list', kwargs={'ticket_pk': self.ticket.id})
        
        # Create a test file
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile(
            "test.txt",
            b"Test file content",
            content_type="text/plain"
        )
        
        data = {
            'file': test_file,
            'description': 'Test attachment'
        }
        
        response = self.client.post(url, data, format='multipart')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify attachment was created
        attachment = TicketAttachment.objects.get(ticket=self.ticket)
        self.assertEqual(attachment.filename, 'test.txt')
        self.assertEqual(attachment.description, 'Test attachment')
    
    def test_ticket_merge(self):
        """Test ticket merge functionality."""
        other_ticket = TestDataFactory.create_ticket(
            self.organization, 
            self.customer, 
            "Other Ticket"
        )
        
        url = reverse('api:ticket-merge', kwargs={'pk': self.ticket.id})
        data = {
            'merge_with': other_ticket.id,
            'keep_ticket': self.ticket.id
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify tickets were merged
        self.ticket.refresh_from_db()
        other_ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'merged')
        self.assertEqual(other_ticket.status, 'merged')
    
    def test_ticket_bulk_operations(self):
        """Test ticket bulk operations."""
        # Create multiple tickets
        tickets = []
        for i in range(3):
            ticket = TestDataFactory.create_ticket(
                self.organization, 
                self.customer, 
                f"Bulk Ticket {i}"
            )
            tickets.append(ticket.id)
        
        url = reverse('api:ticket-bulk-update')
        data = {
            'ticket_ids': tickets,
            'updates': {
                'status': 'in_progress',
                'priority': 'high'
            }
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify all tickets were updated
        for ticket_id in tickets:
            ticket = Ticket.objects.get(id=ticket_id)
            self.assertEqual(ticket.status, 'in_progress')
            self.assertEqual(ticket.priority, 'high')
    
    def test_ticket_filtering(self):
        """Test ticket filtering."""
        # Create tickets with different statuses
        TestDataFactory.create_ticket(self.organization, self.customer, "Open Ticket", "open")
        TestDataFactory.create_ticket(self.organization, self.customer, "Closed Ticket", "closed")
        
        url = reverse('api:ticket-list')
        
        # Filter by status
        response = self.client.get(url, {'status': 'open'})
        TestAssertions.assert_response_success(response)
        
        tickets = response.data['results']
        for ticket in tickets:
            self.assertEqual(ticket['status'], 'open')
        
        # Filter by priority
        response = self.client.get(url, {'priority': 'high'})
        TestAssertions.assert_response_success(response)
        
        # Filter by date range
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        response = self.client.get(url, {
            'created_after': start_date.isoformat(),
            'created_before': end_date.isoformat()
        })
        TestAssertions.assert_response_success(response)
    
    def test_ticket_search(self):
        """Test ticket search functionality."""
        url = reverse('api:ticket-list')
        
        # Search by subject
        response = self.client.get(url, {'search': 'Test Ticket'})
        TestAssertions.assert_response_success(response)
        
        tickets = response.data['results']
        self.assertGreater(len(tickets), 0)
        
        # Search by description
        response = self.client.get(url, {'search': 'description'})
        TestAssertions.assert_response_success(response)
    
    def test_ticket_analytics(self):
        """Test ticket analytics endpoint."""
        url = reverse('api:ticket-analytics')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify analytics data
        analytics = response.data
        self.assertIn('total_tickets', analytics)
        self.assertIn('open_tickets', analytics)
        self.assertIn('resolved_tickets', analytics)
        self.assertIn('average_resolution_time', analytics)
        self.assertIn('sla_breach_count', analytics)


class WorkOrderAPITest(APITestCase):
    """Test WorkOrder API endpoints."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.customer = TestDataFactory.create_user(self.organization, "customer@example.com", "customer")
        self.technician = TestDataFactory.create_technician(
            self.organization, 
            TestDataFactory.create_user(self.organization, "tech@example.com", "technician")
        )
        self.work_order = TestDataFactory.create_work_order(self.organization, self.customer)
        self.client = TestClientFactory.create_authenticated_client(
            TestDataFactory.create_user(self.organization, "agent@example.com", "agent")
        )
    
    def test_work_order_list(self):
        """Test work order list endpoint."""
        url = reverse('api:workorder-list')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify work order data
        work_orders = response.data['results']
        self.assertGreater(len(work_orders), 0)
        
        work_order = work_orders[0]
        self.assertIn('id', work_order)
        self.assertIn('title', work_order)
        self.assertIn('status', work_order)
        self.assertIn('scheduled_start', work_order)
    
    def test_work_order_create(self):
        """Test work order creation."""
        url = reverse('api:workorder-list')
        data = {
            'title': 'New Work Order',
            'description': 'New work order description',
            'status': 'scheduled',
            'customer': self.customer.id,
            'scheduled_start': (timezone.now() + timedelta(hours=1)).isoformat(),
            'scheduled_end': (timezone.now() + timedelta(hours=2)).isoformat(),
            'location': {
                'address': '123 New Street',
                'city': 'New City',
                'coordinates': [40.7589, -73.9851]
            }
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify work order was created
        TestAssertions.assert_work_order_created(data, self.organization)
    
    def test_work_order_assign_technician(self):
        """Test work order technician assignment."""
        url = reverse('api:workorder-assign', kwargs={'pk': self.work_order.id})
        data = {
            'technician': self.technician.id,
            'assigned_at': timezone.now().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify technician was assigned
        assignment = JobAssignment.objects.get(work_order=self.work_order)
        self.assertEqual(assignment.technician, self.technician)
    
    def test_work_order_route_optimization(self):
        """Test work order route optimization."""
        # Create multiple work orders
        work_orders = []
        for i in range(3):
            wo = TestDataFactory.create_work_order(
                self.organization, 
                self.customer, 
                f"Route Work Order {i}"
            )
            work_orders.append(wo.id)
        
        url = reverse('api:workorder-optimize-route')
        data = {
            'work_order_ids': work_orders,
            'technician': self.technician.id,
            'date': timezone.now().date().isoformat()
        }
        
        with patch('apps.field_service.services.RouteOptimizer.optimize_route') as mock_optimize:
            mock_optimize.return_value = TestMocks.mock_route_optimization_response([
                {'work_order_id': wo_id, 'sequence': i, 'distance': 5.5, 'duration': 15.2}
                for i, wo_id in enumerate(work_orders)
            ])
            
            response = self.client.post(url, data, format='json')
            TestAssertions.assert_response_success(response)
            
            # Verify optimization was called
            mock_optimize.assert_called_once()
    
    def test_work_order_completion(self):
        """Test work order completion."""
        url = reverse('api:workorder-complete', kwargs={'pk': self.work_order.id})
        data = {
            'completed_at': timezone.now().isoformat(),
            'service_report': {
                'work_performed': 'Test work performed',
                'parts_used': ['part1', 'part2'],
                'customer_rating': 5,
                'notes': 'Test completion notes'
            }
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify work order was completed
        self.work_order.refresh_from_db()
        self.assertEqual(self.work_order.status, 'completed')
        self.assertIsNotNone(self.work_order.completed_at)
    
    def test_work_order_gps_tracking(self):
        """Test work order GPS tracking."""
        url = reverse('api:workorder-location', kwargs={'pk': self.work_order.id})
        data = {
            'latitude': 40.7589,
            'longitude': -73.9851,
            'accuracy': 5.0,
            'timestamp': timezone.now().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify location was updated
        self.work_order.refresh_from_db()
        location = self.work_order.current_location
        self.assertEqual(location['latitude'], 40.7589)
        self.assertEqual(location['longitude'], -73.9851)


class KnowledgeBaseAPITest(APITestCase):
    """Test Knowledge Base API endpoints."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.article = TestDataFactory.create_kb_article(self.organization)
        self.client = TestClientFactory.create_authenticated_client(self.user)
    
    def test_kb_article_list(self):
        """Test KB article list endpoint."""
        url = reverse('api:kb-article-list')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify article data
        articles = response.data['results']
        self.assertGreater(len(articles), 0)
        
        article = articles[0]
        self.assertIn('id', article)
        self.assertIn('title', article)
        self.assertIn('content', article)
        self.assertIn('category', article)
    
    def test_kb_article_create(self):
        """Test KB article creation."""
        url = reverse('api:kb-article-list')
        data = {
            'title': 'New KB Article',
            'content': 'New KB article content',
            'category': 'technical',
            'tags': ['troubleshooting', 'setup'],
            'is_published': True
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify article was created
        article = KBArticle.objects.get(title='New KB Article')
        self.assertEqual(article.content, 'New KB article content')
        self.assertEqual(article.category, 'technical')
        self.assertTrue(article.is_published)
    
    def test_kb_article_search(self):
        """Test KB article search."""
        url = reverse('api:kb-article-search')
        response = self.client.get(url, {'q': 'Test'})
        TestAssertions.assert_response_success(response)
        
        # Verify search results
        results = response.data['results']
        self.assertGreater(len(results), 0)
        
        # Verify search relevance
        for result in results:
            self.assertIn('Test', result['title'] or result['content'])
    
    def test_kb_article_feedback(self):
        """Test KB article feedback."""
        url = reverse('api:kb-article-feedback', kwargs={'pk': self.article.id})
        data = {
            'rating': 5,
            'comment': 'Very helpful article',
            'helpful': True
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify feedback was created
        feedback = self.article.feedback.first()
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(feedback.comment, 'Very helpful article')
        self.assertTrue(feedback.helpful)
    
    def test_kb_article_suggestions(self):
        """Test KB article suggestions for tickets."""
        ticket = TestDataFactory.create_ticket(self.organization, self.user)
        
        url = reverse('api:kb-article-suggestions')
        data = {
            'ticket_id': ticket.id,
            'query': ticket.subject
        }
        
        with patch('apps.knowledge_base.services.KBSuggestionService.get_suggestions') as mock_suggestions:
            mock_suggestions.return_value = [
                {
                    'article_id': self.article.id,
                    'title': self.article.title,
                    'relevance_score': 0.85,
                    'snippet': 'Test content snippet'
                }
            ]
            
            response = self.client.post(url, data, format='json')
            TestAssertions.assert_response_success(response)
            
            # Verify suggestions were returned
            suggestions = response.data['suggestions']
            self.assertGreater(len(suggestions), 0)
            self.assertEqual(suggestions[0]['article_id'], self.article.id)


class AutomationAPITest(APITestCase):
    """Test Automation API endpoints."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.rule = TestDataFactory.create_automation_rule(self.organization)
        self.sla_policy = TestDataFactory.create_sla_policy(self.organization)
        self.client = TestClientFactory.create_authenticated_client(self.user)
    
    def test_automation_rule_list(self):
        """Test automation rule list endpoint."""
        url = reverse('api:automation-rule-list')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify rule data
        rules = response.data['results']
        self.assertGreater(len(rules), 0)
        
        rule = rules[0]
        self.assertIn('id', rule)
        self.assertIn('name', rule)
        self.assertIn('trigger_type', rule)
        self.assertIn('is_active', rule)
    
    def test_automation_rule_create(self):
        """Test automation rule creation."""
        url = reverse('api:automation-rule-list')
        data = {
            'name': 'New Automation Rule',
            'trigger_type': 'ticket_updated',
            'conditions': [
                {'field': 'status', 'operator': 'equals', 'value': 'open'}
            ],
            'actions': [
                {'type': 'send_email', 'template_id': 1},
                {'type': 'change_priority', 'priority': 'high'}
            ],
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify rule was created
        rule = AutomationRule.objects.get(name='New Automation Rule')
        self.assertEqual(rule.trigger_type, 'ticket_updated')
        self.assertEqual(len(rule.conditions), 1)
        self.assertEqual(len(rule.actions), 2)
    
    def test_automation_rule_test(self):
        """Test automation rule testing."""
        url = reverse('api:automation-rule-test', kwargs={'pk': self.rule.id})
        data = {
            'test_data': {
                'priority': 'high',
                'status': 'open',
                'customer_id': 1
            }
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify test results
        results = response.data
        self.assertIn('rule_matches', results)
        self.assertIn('actions_executed', results)
        self.assertIn('test_results', results)
    
    def test_sla_policy_list(self):
        """Test SLA policy list endpoint."""
        url = reverse('api:sla-policy-list')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify policy data
        policies = response.data['results']
        self.assertGreater(len(policies), 0)
        
        policy = policies[0]
        self.assertIn('id', policy)
        self.assertIn('name', policy)
        self.assertIn('first_response_time', policy)
        self.assertIn('resolution_time', policy)
    
    def test_sla_policy_create(self):
        """Test SLA policy creation."""
        url = reverse('api:sla-policy-list')
        data = {
            'name': 'New SLA Policy',
            'first_response_time': 30,
            'resolution_time': 240,
            'operational_hours': {
                'monday': {'start': '09:00', 'end': '17:00'},
                'tuesday': {'start': '09:00', 'end': '17:00'}
            },
            'conditions': [
                {'field': 'priority', 'operator': 'equals', 'value': 'high'}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify policy was created
        policy = SLAPolicy.objects.get(name='New SLA Policy')
        self.assertEqual(policy.first_response_time, 30)
        self.assertEqual(policy.resolution_time, 240)
        self.assertEqual(len(policy.conditions), 1)
    
    def test_sla_breach_check(self):
        """Test SLA breach checking."""
        url = reverse('api:sla-breach-check')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify breach data
        breaches = response.data['breaches']
        self.assertIsInstance(breaches, list)
        
        for breach in breaches:
            self.assertIn('ticket_id', breach)
            self.assertIn('breach_type', breach)
            self.assertIn('breach_time', breach)


class AnalyticsAPITest(APITestCase):
    """Test Analytics API endpoints."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.client = TestClientFactory.create_authenticated_client(self.user)
    
    def test_analytics_dashboard(self):
        """Test analytics dashboard endpoint."""
        url = reverse('api:analytics-dashboard')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify dashboard data
        dashboard = response.data
        self.assertIn('ticket_metrics', dashboard)
        self.assertIn('work_order_metrics', dashboard)
        self.assertIn('technician_metrics', dashboard)
        self.assertIn('customer_metrics', dashboard)
        self.assertIn('sla_metrics', dashboard)
    
    def test_analytics_reports(self):
        """Test analytics reports endpoint."""
        url = reverse('api:analytics-reports')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify reports data
        reports = response.data['results']
        self.assertIsInstance(reports, list)
    
    def test_analytics_custom_report(self):
        """Test custom analytics report."""
        url = reverse('api:analytics-custom-report')
        data = {
            'report_type': 'ticket_analysis',
            'date_range': {
                'start': (timezone.now() - timedelta(days=30)).isoformat(),
                'end': timezone.now().isoformat()
            },
            'filters': {
                'status': ['open', 'in_progress'],
                'priority': ['high', 'urgent']
            },
            'group_by': ['status', 'priority'],
            'metrics': ['count', 'avg_resolution_time']
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify report data
        report = response.data
        self.assertIn('data', report)
        self.assertIn('summary', report)
        self.assertIn('generated_at', report)
    
    def test_analytics_export(self):
        """Test analytics data export."""
        url = reverse('api:analytics-export')
        data = {
            'export_type': 'tickets',
            'format': 'csv',
            'date_range': {
                'start': (timezone.now() - timedelta(days=7)).isoformat(),
                'end': timezone.now().isoformat()
            }
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify export data
        export = response.data
        self.assertIn('download_url', export)
        self.assertIn('file_size', export)
        self.assertIn('expires_at', export)


class IntegrationAPITest(APITestCase):
    """Test Integration API endpoints."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.webhook = TestDataFactory.create_webhook(self.organization)
        self.client = TestClientFactory.create_authenticated_client(self.user)
    
    def test_webhook_list(self):
        """Test webhook list endpoint."""
        url = reverse('api:webhook-list')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify webhook data
        webhooks = response.data['results']
        self.assertGreater(len(webhooks), 0)
        
        webhook = webhooks[0]
        self.assertIn('id', webhook)
        self.assertIn('name', webhook)
        self.assertIn('url', webhook)
        self.assertIn('events', webhook)
        self.assertIn('is_active', webhook)
    
    def test_webhook_create(self):
        """Test webhook creation."""
        url = reverse('api:webhook-list')
        data = {
            'name': 'New Webhook',
            'url': 'https://example.com/new-webhook',
            'events': ['ticket_created', 'ticket_updated', 'work_order_created'],
            'secret_key': 'new_secret_key',
            'headers': {
                'Authorization': 'Bearer token123',
                'Content-Type': 'application/json'
            },
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        
        # Verify webhook was created
        webhook = Webhook.objects.get(name='New Webhook')
        self.assertEqual(webhook.url, 'https://example.com/new-webhook')
        self.assertEqual(len(webhook.events), 3)
        self.assertTrue(webhook.is_active)
    
    def test_webhook_test(self):
        """Test webhook testing."""
        url = reverse('api:webhook-test', kwargs={'pk': self.webhook.id})
        data = {
            'test_payload': {
                'event_type': 'test_event',
                'data': {'test': 'data'}
            }
        }
        
        with patch('apps.integrations.services.WebhookService.send_webhook') as mock_send:
            mock_send.return_value = TestMocks.mock_webhook_response()
            
            response = self.client.post(url, data, format='json')
            TestAssertions.assert_response_success(response)
            
            # Verify webhook was called
            mock_send.assert_called_once()
    
    def test_webhook_logs(self):
        """Test webhook logs endpoint."""
        url = reverse('api:webhook-logs', kwargs={'pk': self.webhook.id})
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify logs data
        logs = response.data['results']
        self.assertIsInstance(logs, list)
    
    def test_integration_status(self):
        """Test integration status endpoint."""
        url = reverse('api:integration-status')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify status data
        status = response.data
        self.assertIn('webhooks', status)
        self.assertIn('apis', status)
        self.assertIn('external_services', status)
    
    def test_third_party_integration(self):
        """Test third-party integration."""
        url = reverse('api:third-party-integration')
        data = {
            'service': 'stripe',
            'action': 'create_customer',
            'data': {
                'email': 'customer@example.com',
                'name': 'Test Customer'
            }
        }
        
        with patch('apps.integrations.services.ThirdPartyService.integrate') as mock_integrate:
            mock_integrate.return_value = {
                'success': True,
                'customer_id': 'cus_123456789',
                'response': {'id': 'cus_123456789'}
            }
            
            response = self.client.post(url, data, format='json')
            TestAssertions.assert_response_success(response)
            
            # Verify integration was called
            mock_integrate.assert_called_once()


class NotificationAPITest(APITestCase):
    """Test Notification API endpoints."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.client = TestClientFactory.create_authenticated_client(self.user)
    
    def test_notification_list(self):
        """Test notification list endpoint."""
        # Create test notification
        Notification.objects.create(
            organization=self.organization,
            user=self.user,
            notification_type='ticket_assigned',
            message='Test notification',
            priority='high'
        )
        
        url = reverse('api:notification-list')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify notification data
        notifications = response.data['results']
        self.assertGreater(len(notifications), 0)
        
        notification = notifications[0]
        self.assertIn('id', notification)
        self.assertIn('notification_type', notification)
        self.assertIn('message', notification)
        self.assertIn('is_read', notification)
    
    def test_notification_mark_read(self):
        """Test notification mark as read."""
        notification = Notification.objects.create(
            organization=self.organization,
            user=self.user,
            notification_type='ticket_assigned',
            message='Test notification',
            priority='high'
        )
        
        url = reverse('api:notification-mark-read', kwargs={'pk': notification.id})
        response = self.client.post(url)
        TestAssertions.assert_response_success(response)
        
        # Verify notification was marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)
    
    def test_notification_bulk_mark_read(self):
        """Test bulk notification mark as read."""
        # Create multiple notifications
        notifications = []
        for i in range(3):
            notification = Notification.objects.create(
                organization=self.organization,
                user=self.user,
                notification_type='ticket_assigned',
                message=f'Test notification {i}',
                priority='high'
            )
            notifications.append(notification.id)
        
        url = reverse('api:notification-bulk-mark-read')
        data = {'notification_ids': notifications}
        
        response = self.client.post(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify all notifications were marked as read
        for notification_id in notifications:
            notification = Notification.objects.get(id=notification_id)
            self.assertTrue(notification.is_read)
    
    def test_notification_preferences(self):
        """Test notification preferences."""
        url = reverse('api:notification-preferences')
        
        # Get current preferences
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Update preferences
        data = {
            'email_enabled': True,
            'sms_enabled': False,
            'push_enabled': True,
            'in_app_enabled': True,
            'notification_types': {
                'ticket_assigned': {'email': True, 'sms': False, 'push': True},
                'work_order_created': {'email': True, 'sms': True, 'push': True}
            }
        }
        
        response = self.client.put(url, data, format='json')
        TestAssertions.assert_response_success(response)
        
        # Verify preferences were updated
        preferences = response.data
        self.assertTrue(preferences['email_enabled'])
        self.assertFalse(preferences['sms_enabled'])
        self.assertTrue(preferences['push_enabled'])
    
    def test_notification_send(self):
        """Test notification sending."""
        url = reverse('api:notification-send')
        data = {
            'users': [self.user.id],
            'notification_type': 'system_alert',
            'message': 'System maintenance scheduled',
            'priority': 'high',
            'channels': ['email', 'in_app']
        }
        
        with patch('apps.notifications.services.NotificationService.send_notification') as mock_send:
            mock_send.return_value = {'success': True, 'sent_count': 1}
            
            response = self.client.post(url, data, format='json')
            TestAssertions.assert_response_success(response)
            
            # Verify notification was sent
            mock_send.assert_called_once()


class SystemAPITest(APITestCase):
    """Test System API endpoints."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.client = TestClientFactory.create_authenticated_client(self.user)
    
    def test_system_status(self):
        """Test system status endpoint."""
        url = reverse('api:system-status')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify status data
        status = response.data
        self.assertIn('overall_status', status)
        self.assertIn('services', status)
        self.assertIn('features', status)
        self.assertIn('connections', status)
        self.assertIn('timestamp', status)
    
    def test_feature_status(self):
        """Test feature status endpoint."""
        url = reverse('api:feature-status')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify feature data
        features = response.data
        self.assertIn('core_features', features)
        self.assertIn('advanced_features', features)
        
        # Check core features
        core_features = features['core_features']
        self.assertIn('tickets', core_features)
        self.assertIn('work_orders', core_features)
        self.assertIn('technicians', core_features)
        
        # Check advanced features
        advanced_features = features['advanced_features']
        self.assertIn('ai_ml', advanced_features)
        self.assertIn('customer_experience', advanced_features)
        self.assertIn('advanced_analytics', advanced_features)
    
    def test_feature_connections(self):
        """Test feature connections endpoint."""
        url = reverse('api:feature-connections')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify connection data
        connections = response.data
        self.assertIn('tickets_to_work_orders', connections)
        self.assertIn('tickets_to_knowledge_base', connections)
        self.assertIn('tickets_to_automation', connections)
        self.assertIn('work_orders_to_technicians', connections)
        self.assertIn('analytics_to_all_features', connections)
    
    def test_realtime_capabilities(self):
        """Test real-time capabilities endpoint."""
        url = reverse('api:realtime-capabilities')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify capabilities data
        capabilities = response.data
        self.assertIn('websocket_connection', capabilities)
        self.assertIn('live_notifications', capabilities)
        self.assertIn('gps_tracking', capabilities)
        self.assertIn('system_monitoring', capabilities)
    
    def test_microservice_status(self):
        """Test microservice status endpoint."""
        url = reverse('api:microservice-status')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify microservice data
        services = response.data
        self.assertIn('django_core', services)
        self.assertIn('ai_service', services)
        self.assertIn('realtime_service', services)
        self.assertIn('celery_workers', services)
        self.assertIn('database', services)
        self.assertIn('redis', services)
    
    def test_api_documentation(self):
        """Test API documentation endpoint."""
        url = reverse('api:api-documentation')
        response = self.client.get(url)
        TestAssertions.assert_response_success(response)
        
        # Verify documentation data
        docs = response.data
        self.assertIn('services', docs)
        self.assertIn('endpoints', docs)
        self.assertIn('authentication', docs)
        self.assertIn('rate_limits', docs)
