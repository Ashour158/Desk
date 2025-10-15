"""
Comprehensive service tests for all microservices and integrations.
"""
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock, AsyncMock
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from channels.testing import WebsocketCommunicator
from asgiref.sync import async_to_sync

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket
from apps.field_service.models import WorkOrder, Technician
from apps.automation.models import AutomationRule, SLAPolicy
from apps.integrations.models import Webhook, IntegrationLog
from apps.notifications.models import Notification
from apps.api.models import APIService
from apps.api.system_checker import system_checker
from apps.api.real_time_integration import realtime_integration

from .test_utils import (
    TestDataFactory, TestClientFactory, TestAssertions, 
    TestMocks, TestPerformance, TestSecurity, TestIntegration
)

User = get_user_model()


class AIServiceTest(TransactionTestCase):
    """Test AI service integration with proper isolation."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.ticket = TestDataFactory.create_ticket(self.organization, self.user)
    
    def tearDown(self):
        # Clean up test data to prevent isolation issues
        from apps.tickets.models import Ticket
        Ticket.objects.all().delete()
        User.objects.all().delete()
        Organization.objects.all().delete()
        super().tearDown()
    
    @patch('requests.post')
    async def test_ticket_categorization(self, mock_post):
        """Test AI ticket categorization with minimal mocking."""
        # Mock only the HTTP response, not the entire service
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'category': 'Technical',
            'confidence': 0.85,
            'subcategory': 'Hardware Issue'
        }
        mock_post.return_value = mock_response
        
        # Test categorization with proper async handling
        from apps.ai_ml.services import AICategorizationService
        service = AICategorizationService()
        
        try:
            result = await service.categorize_ticket(
                subject=self.ticket.subject,
                description=self.ticket.description
            )
            
            self.assertEqual(result['category'], 'Technical')
            self.assertEqual(result['confidence'], 0.85)
            self.assertEqual(result['subcategory'], 'Hardware Issue')
            
            # Verify API call was made with correct parameters
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            self.assertIn('url', call_args.kwargs)
            self.assertIn('json', call_args.kwargs)
        except Exception as e:
            self.fail(f"AI categorization failed: {e}")
    
    @patch('requests.post')
    def test_sentiment_analysis(self, mock_post):
        """Test AI sentiment analysis."""
        # Mock AI service response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'sentiment': 'negative',
            'score': 0.75,
            'emotions': ['frustration', 'urgency']
        }
        mock_post.return_value = mock_response
        
        # Test sentiment analysis
        from apps.ai_ml.services import AISentimentService
        service = AISentimentService()
        
        result = service.analyze_sentiment(
            text="I'm very frustrated with this issue!"
        )
        
        self.assertEqual(result['sentiment'], 'negative')
        self.assertEqual(result['score'], 0.75)
        self.assertIn('frustration', result['emotions'])
        
        # Verify API call was made
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_response_suggestion(self, mock_post):
        """Test AI response suggestion."""
        # Mock AI service response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'suggested_response': 'Thank you for contacting us. We understand your frustration and will help resolve this issue.',
            'confidence': 0.90,
            'tone': 'empathetic',
            'key_points': ['acknowledge_frustration', 'offer_help', 'assure_resolution']
        }
        mock_post.return_value = mock_response
        
        # Test response suggestion
        from apps.ai_ml.services import AIResponseService
        service = AIResponseService()
        
        result = service.suggest_response(
            ticket_content=self.ticket.description,
            kb_context=['Common solutions', 'Troubleshooting steps']
        )
        
        self.assertIn('Thank you for contacting us', result['suggested_response'])
        self.assertEqual(result['confidence'], 0.90)
        self.assertEqual(result['tone'], 'empathetic')
        self.assertIn('acknowledge_frustration', result['key_points'])
        
        # Verify API call was made
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_chatbot_interaction(self, mock_post):
        """Test AI chatbot interaction."""
        # Mock AI service response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': 'I can help you with that. Let me check our knowledge base.',
            'intent': 'troubleshooting',
            'confidence': 0.88,
            'suggested_actions': ['search_kb', 'create_ticket', 'escalate']
        }
        mock_post.return_value = mock_response
        
        # Test chatbot interaction
        from apps.ai_ml.services import AIChatbotService
        service = AIChatbotService()
        
        result = service.process_message(
            message="I'm having trouble with my account",
            context={'user_id': self.user.id, 'organization_id': self.organization.id}
        )
        
        self.assertIn('I can help you', result['response'])
        self.assertEqual(result['intent'], 'troubleshooting')
        self.assertEqual(result['confidence'], 0.88)
        self.assertIn('search_kb', result['suggested_actions'])
        
        # Verify API call was made
        mock_post.assert_called_once()
    
    def test_ai_service_health_check(self):
        """Test AI service health check."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'healthy',
                'version': '1.0.0',
                'uptime': '99.9%'
            }
            mock_get.return_value = mock_response
            
            # Test health check
            from apps.api.system_checker import system_checker
            
            async def test_health():
                return await system_checker.check_http_service('http://ai-service:8001')
            
            result = asyncio.run(test_health())
            
            self.assertEqual(result['status'], 'healthy')
            self.assertIn('version', result['data'])
            self.assertIn('uptime', result['data'])


class RealTimeServiceTest(TestCase):
    """Test real-time service integration."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.ticket = TestDataFactory.create_ticket(self.organization, self.user)
    
    async def test_websocket_connection(self):
        """Test WebSocket connection."""
        from apps.api.consumers import TicketConsumer
        
        communicator = WebsocketCommunicator(
            TicketConsumer,
            f"/ws/tickets/?org={self.organization.id}&user={self.user.id}"
        )
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Test sending message
        await communicator.send_json_to({
            'type': 'ticket_message',
            'ticket_id': self.ticket.id,
            'message': 'Test message',
            'user_id': self.user.id
        })
        
        # Test receiving message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'ticket_message')
        self.assertEqual(response['ticket_id'], self.ticket.id)
        self.assertEqual(response['message'], 'Test message')
        
        await communicator.disconnect()
    
    async def test_typing_indicator(self):
        """Test typing indicator."""
        from apps.api.consumers import TicketConsumer
        
        communicator = WebsocketCommunicator(
            TicketConsumer,
            f"/ws/tickets/?org={self.organization.id}&user={self.user.id}"
        )
        
        await communicator.connect()
        
        # Test typing indicator
        await communicator.send_json_to({
            'type': 'typing',
            'ticket_id': self.ticket.id,
            'user_id': self.user.id,
            'is_typing': True
        })
        
        # Test receiving typing indicator
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'typing')
        self.assertEqual(response['ticket_id'], self.ticket.id)
        self.assertTrue(response['is_typing'])
        
        await communicator.disconnect()
    
    async def test_live_notifications(self):
        """Test live notifications."""
        from apps.api.consumers import NotificationConsumer
        
        communicator = WebsocketCommunicator(
            NotificationConsumer,
            f"/ws/notifications/?org={self.organization.id}&user={self.user.id}"
        )
        
        await communicator.connect()
        
        # Test notification
        await communicator.send_json_to({
            'type': 'notification',
            'notification_type': 'ticket_assigned',
            'message': 'You have been assigned a new ticket',
            'user_id': self.user.id
        })
        
        # Test receiving notification
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'notification')
        self.assertEqual(response['notification_type'], 'ticket_assigned')
        self.assertEqual(response['message'], 'You have been assigned a new ticket')
        
        await communicator.disconnect()
    
    async def test_gps_tracking(self):
        """Test GPS tracking."""
        from apps.api.consumers import GPSTrackingConsumer
        
        communicator = WebsocketCommunicator(
            GPSTrackingConsumer,
            f"/ws/gps/?org={self.organization.id}&user={self.user.id}"
        )
        
        await communicator.connect()
        
        # Test GPS update
        await communicator.send_json_to({
            'type': 'location_update',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'accuracy': 5.0,
            'timestamp': timezone.now().isoformat()
        })
        
        # Test receiving GPS update
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'location_update')
        self.assertEqual(response['latitude'], 40.7128)
        self.assertEqual(response['longitude'], -74.0060)
        self.assertEqual(response['accuracy'], 5.0)
        
        await communicator.disconnect()
    
    def test_realtime_service_health_check(self):
        """Test real-time service health check."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'healthy',
                'connections': 150,
                'uptime': '99.9%'
            }
            mock_get.return_value = mock_response
            
            # Test health check
            from apps.api.system_checker import system_checker
            
            async def test_health():
                return await system_checker.check_http_service('http://realtime-service:8002')
            
            result = asyncio.run(test_health())
            
            self.assertEqual(result['status'], 'healthy')
            self.assertIn('connections', result['data'])
            self.assertIn('uptime', result['data'])


class EmailServiceTest(TestCase):
    """Test email service integration."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.ticket = TestDataFactory.create_ticket(self.organization, self.user)
    
    @patch('apps.notifications.tasks.send_email.delay')
    def test_email_sending(self, mock_send_email):
        """Test email sending."""
        from apps.notifications.services import EmailService
        service = EmailService()
        
        # Test email sending
        result = service.send_email(
            to_email=self.user.email,
            subject='Test Email',
            template='ticket_assigned',
            context={'ticket': self.ticket}
        )
        
        self.assertTrue(result['success'])
        self.assertIn('message_id', result)
        
        # Verify task was queued
        mock_send_email.assert_called_once()
    
    @patch('apps.notifications.tasks.send_bulk_email.delay')
    def test_bulk_email_sending(self, mock_send_bulk_email):
        """Test bulk email sending."""
        from apps.notifications.services import EmailService
        service = EmailService()
        
        # Test bulk email sending
        recipients = [
            {'email': 'user1@example.com', 'name': 'User 1'},
            {'email': 'user2@example.com', 'name': 'User 2'},
            {'email': 'user3@example.com', 'name': 'User 3'}
        ]
        
        result = service.send_bulk_email(
            recipients=recipients,
            subject='Bulk Test Email',
            template='newsletter',
            context={'organization': self.organization}
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['recipient_count'], 3)
        
        # Verify task was queued
        mock_send_bulk_email.assert_called_once()
    
    @patch('apps.notifications.tasks.send_email_template.delay')
    def test_email_template_sending(self, mock_send_template):
        """Test email template sending."""
        from apps.notifications.services import EmailService
        service = EmailService()
        
        # Test template email sending
        result = service.send_template_email(
            to_email=self.user.email,
            template_id=1,
            context={'ticket': self.ticket, 'user': self.user}
        )
        
        self.assertTrue(result['success'])
        self.assertIn('template_id', result)
        
        # Verify task was queued
        mock_send_template.assert_called_once()
    
    def test_email_validation(self):
        """Test email validation."""
        from apps.notifications.services import EmailService
        service = EmailService()
        
        # Test valid email
        self.assertTrue(service.validate_email('user@example.com'))
        self.assertTrue(service.validate_email('user.name@example.com'))
        self.assertTrue(service.validate_email('user+tag@example.com'))
        
        # Test invalid email
        self.assertFalse(service.validate_email('invalid-email'))
        self.assertFalse(service.validate_email('user@'))
        self.assertFalse(service.validate_email('@example.com'))
    
    def test_email_rate_limiting(self):
        """Test email rate limiting."""
        from apps.notifications.services import EmailService
        service = EmailService()
        
        # Test rate limiting
        for i in range(10):
            result = service.send_email(
                to_email=f'user{i}@example.com',
                subject='Test Email',
                template='test',
                context={}
            )
            
            if i < 5:  # First 5 should succeed
                self.assertTrue(result['success'])
            else:  # Next 5 should be rate limited
                self.assertFalse(result['success'])
                self.assertIn('rate_limit', result)


class SMSServiceTest(TestCase):
    """Test SMS service integration."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.ticket = TestDataFactory.create_ticket(self.organization, self.user)
    
    @patch('apps.notifications.tasks.send_sms.delay')
    def test_sms_sending(self, mock_send_sms):
        """Test SMS sending."""
        from apps.notifications.services import SMSService
        service = SMSService()
        
        # Test SMS sending
        result = service.send_sms(
            to_phone='+1234567890',
            message='Test SMS message',
            template='ticket_assigned'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('message_id', result)
        
        # Verify task was queued
        mock_send_sms.assert_called_once()
    
    @patch('apps.notifications.tasks.send_bulk_sms.delay')
    def test_bulk_sms_sending(self, mock_send_bulk_sms):
        """Test bulk SMS sending."""
        from apps.notifications.services import SMSService
        service = SMSService()
        
        # Test bulk SMS sending
        recipients = [
            {'phone': '+1234567890', 'name': 'User 1'},
            {'phone': '+1234567891', 'name': 'User 2'},
            {'phone': '+1234567892', 'name': 'User 3'}
        ]
        
        result = service.send_bulk_sms(
            recipients=recipients,
            message='Bulk SMS message',
            template='alert'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['recipient_count'], 3)
        
        # Verify task was queued
        mock_send_bulk_sms.assert_called_once()
    
    def test_sms_validation(self):
        """Test SMS validation."""
        from apps.notifications.services import SMSService
        service = SMSService()
        
        # Test valid phone numbers
        self.assertTrue(service.validate_phone('+1234567890'))
        self.assertTrue(service.validate_phone('+44123456789'))
        self.assertTrue(service.validate_phone('+33123456789'))
        
        # Test invalid phone numbers
        self.assertFalse(service.validate_phone('1234567890'))
        self.assertFalse(service.validate_phone('+123'))
        self.assertFalse(service.validate_phone('invalid'))
    
    def test_sms_rate_limiting(self):
        """Test SMS rate limiting."""
        from apps.notifications.services import SMSService
        service = SMSService()
        
        # Test rate limiting
        for i in range(10):
            result = service.send_sms(
                to_phone=f'+123456789{i}',
                message='Test SMS',
                template='test'
            )
            
            if i < 5:  # First 5 should succeed
                self.assertTrue(result['success'])
            else:  # Next 5 should be rate limited
                self.assertFalse(result['success'])
                self.assertIn('rate_limit', result)


class RouteOptimizationServiceTest(TestCase):
    """Test route optimization service."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.technician = TestDataFactory.create_technician(
            self.organization,
            TestDataFactory.create_user(self.organization, "tech@example.com", "technician")
        )
        self.work_orders = [
            TestDataFactory.create_work_order(self.organization, 
                TestDataFactory.create_user(self.organization, f"customer{i}@example.com", "customer"),
                f"Work Order {i}")
            for i in range(5)
        ]
    
    @patch('apps.field_service.services.RouteOptimizer.optimize_route')
    def test_route_optimization(self, mock_optimize):
        """Test route optimization."""
        # Mock optimization response
        mock_optimize.return_value = {
            'optimized_route': [
                {'work_order_id': wo.id, 'sequence': i, 'distance': 5.5, 'duration': 15.2}
                for i, wo in enumerate(self.work_orders)
            ],
            'total_distance': 25.5,
            'total_duration': 75.2,
            'optimization_score': 0.92
        }
        
        from apps.field_service.services import RouteOptimizationService
        service = RouteOptimizationService()
        
        result = service.optimize_route(
            technician=self.technician,
            work_orders=self.work_orders,
            date=timezone.now().date()
        )
        
        self.assertEqual(result['total_distance'], 25.5)
        self.assertEqual(result['total_duration'], 75.2)
        self.assertEqual(result['optimization_score'], 0.92)
        self.assertEqual(len(result['optimized_route']), 5)
        
        # Verify optimization was called
        mock_optimize.assert_called_once()
    
    def test_skill_matching(self):
        """Test skill matching."""
        from apps.field_service.services import RouteOptimizationService
        service = RouteOptimizationService()
        
        # Test skill matching
        required_skills = ['electrical', 'plumbing']
        technician_skills = ['electrical', 'plumbing', 'hvac']
        
        match_score = service.match_skills(required_skills, technician_skills)
        
        self.assertEqual(match_score, 1.0)  # Perfect match
        
        # Test partial match
        required_skills = ['electrical', 'plumbing', 'hvac']
        technician_skills = ['electrical', 'plumbing']
        
        match_score = service.match_skills(required_skills, technician_skills)
        
        self.assertEqual(match_score, 0.67)  # Partial match
    
    def test_time_window_optimization(self):
        """Test time window optimization."""
        from apps.field_service.services import RouteOptimizationService
        service = RouteOptimizationService()
        
        # Test time window optimization
        work_orders = self.work_orders[:3]
        for i, wo in enumerate(work_orders):
            wo.scheduled_start = timezone.now() + timedelta(hours=i)
            wo.scheduled_end = timezone.now() + timedelta(hours=i+1)
            wo.save()
        
        result = service.optimize_time_windows(work_orders)
        
        self.assertIn('optimized_schedule', result)
        self.assertIn('total_travel_time', result)
        self.assertIn('efficiency_score', result)
    
    def test_geolocation_optimization(self):
        """Test geolocation optimization."""
        from apps.field_service.services import RouteOptimizationService
        service = RouteOptimizationService()
        
        # Test geolocation optimization
        locations = [
            {'latitude': 40.7128, 'longitude': -74.0060, 'address': 'Location 1'},
            {'latitude': 40.7589, 'longitude': -73.9851, 'address': 'Location 2'},
            {'latitude': 40.6892, 'longitude': -74.0445, 'address': 'Location 3'}
        ]
        
        result = service.optimize_geolocation(locations)
        
        self.assertIn('optimized_route', result)
        self.assertIn('total_distance', result)
        self.assertIn('total_duration', result)


class WebhookServiceTest(TestCase):
    """Test webhook service integration."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.webhook = TestDataFactory.create_webhook(self.organization)
        self.ticket = TestDataFactory.create_ticket(self.organization, 
            TestDataFactory.create_user(self.organization, "customer@example.com", "customer"))
    
    @patch('requests.post')
    def test_webhook_triggering(self, mock_post):
        """Test webhook triggering."""
        # Mock webhook response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        from apps.integrations.services import WebhookService
        service = WebhookService()
        
        # Test webhook triggering
        result = service.trigger_webhook(
            webhook=self.webhook,
            event_type='ticket_created',
            payload={'ticket_id': self.ticket.id, 'ticket_number': self.ticket.number}
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 200)
        
        # Verify webhook was called
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_webhook_retry_logic(self, mock_post):
        """Test webhook retry logic."""
        # Mock webhook failure then success
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.json.return_value = {'error': 'Internal Server Error'}
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'success': True}
        
        mock_post.side_effect = [mock_response_fail, mock_response_success]
        
        from apps.integrations.services import WebhookService
        service = WebhookService()
        
        # Test webhook with retry
        result = service.trigger_webhook_with_retry(
            webhook=self.webhook,
            event_type='ticket_created',
            payload={'ticket_id': self.ticket.id}
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['retry_count'], 1)
        
        # Verify webhook was called twice (initial + retry)
        self.assertEqual(mock_post.call_count, 2)
    
    def test_webhook_signature_validation(self):
        """Test webhook signature validation."""
        from apps.integrations.services import WebhookService
        service = WebhookService()
        
        # Test signature generation
        payload = {'ticket_id': self.ticket.id, 'event': 'ticket_created'}
        signature = service.generate_signature(payload, self.webhook.secret_key)
        
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, str)
        
        # Test signature validation
        is_valid = service.validate_signature(payload, signature, self.webhook.secret_key)
        self.assertTrue(is_valid)
        
        # Test invalid signature
        invalid_signature = 'invalid_signature'
        is_valid = service.validate_signature(payload, invalid_signature, self.webhook.secret_key)
        self.assertFalse(is_valid)
    
    def test_webhook_rate_limiting(self):
        """Test webhook rate limiting."""
        from apps.integrations.services import WebhookService
        service = WebhookService()
        
        # Test rate limiting
        for i in range(10):
            result = service.trigger_webhook(
                webhook=self.webhook,
                event_type='ticket_created',
                payload={'ticket_id': i}
            )
            
            if i < 5:  # First 5 should succeed
                self.assertTrue(result['success'])
            else:  # Next 5 should be rate limited
                self.assertFalse(result['success'])
                self.assertIn('rate_limit', result)


class SystemCheckerTest(TestCase):
    """Test system checker service."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
    
    async def test_system_health_check(self):
        """Test system health check."""
        # Test system health check
        report = await system_checker.generate_system_report()
        
        self.assertIn('timestamp', report)
        self.assertIn('services', report)
        self.assertIn('features', report)
        self.assertIn('connections', report)
        self.assertIn('overall_status', report)
    
    async def test_service_health_check(self):
        """Test service health check."""
        # Test individual service health checks
        services = await system_checker.check_all_services()
        
        self.assertIn('django_core', services)
        self.assertIn('ai_service', services)
        self.assertIn('realtime_service', services)
        self.assertIn('celery_workers', services)
        self.assertIn('database', services)
        self.assertIn('redis', services)
    
    async def test_feature_health_check(self):
        """Test feature health check."""
        # Test feature health check
        features = await system_checker.check_feature_functionality()
        
        self.assertIn('tickets', features)
        self.assertIn('work_orders', features)
        self.assertIn('technicians', features)
        self.assertIn('knowledge_base', features)
        self.assertIn('automation', features)
        self.assertIn('analytics', features)
    
    async def test_realtime_capabilities_check(self):
        """Test real-time capabilities check."""
        # Test real-time capabilities check
        capabilities = await system_checker.check_realtime_capabilities()
        
        self.assertIn('websocket_connection', capabilities)
        self.assertIn('real_time_updates', capabilities)
        self.assertIn('live_notifications', capabilities)
        self.assertIn('gps_tracking', capabilities)
    
    async def test_feature_connections_check(self):
        """Test feature connections check."""
        # Test feature connections check
        connections = await system_checker.check_feature_connections()
        
        self.assertIn('tickets_to_work_orders', connections)
        self.assertIn('tickets_to_knowledge_base', connections)
        self.assertIn('tickets_to_automation', connections)
        self.assertIn('work_orders_to_technicians', connections)
        self.assertIn('analytics_to_all_features', connections)


class RealTimeIntegrationTest(TestCase):
    """Test real-time integration service."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.ticket = TestDataFactory.create_ticket(self.organization, self.user)
    
    def test_realtime_update_sending(self):
        """Test real-time update sending."""
        # Test ticket update
        realtime_integration.send_ticket_update(
            ticket_id=self.ticket.id,
            action='status_changed',
            data={'status': 'in_progress', 'assigned_agent': self.user.id},
            organization_id=self.organization.id,
            user_id=self.user.id
        )
        
        # Test work order update
        work_order = TestDataFactory.create_work_order(self.organization, self.user)
        realtime_integration.send_work_order_update(
            work_order_id=work_order.id,
            action='assigned',
            data={'technician_id': 1, 'assigned_at': timezone.now().isoformat()},
            organization_id=self.organization.id,
            user_id=self.user.id
        )
        
        # Test notification
        realtime_integration.send_notification(
            notification_type='ticket_assigned',
            message='You have been assigned a new ticket',
            user_id=self.user.id,
            organization_id=self.organization.id,
            data={'ticket_id': self.ticket.id}
        )
        
        # Test system status update
        realtime_integration.send_system_status_update(
            status='healthy',
            details={'uptime': '99.9%', 'services': 6},
            organization_id=self.organization.id
        )
        
        # Test feature status update
        realtime_integration.send_feature_status_update(
            feature_name='tickets',
            status='active',
            details={'endpoints': 5, 'operations': 10},
            organization_id=self.organization.id
        )
    
    def test_websocket_connection_management(self):
        """Test WebSocket connection management."""
        # Test user connection
        realtime_integration.connect_user(
            user_id=self.user.id,
            organization_id=self.organization.id,
            websocket_channel='test_channel'
        )
        
        # Test user disconnection
        realtime_integration.disconnect_user(
            user_id=self.user.id,
            organization_id=self.organization.id,
            websocket_channel='test_channel'
        )
    
    def test_realtime_stats(self):
        """Test real-time statistics."""
        # Test getting real-time stats
        stats = realtime_integration.get_realtime_stats()
        
        self.assertIn('connection_count', stats)
        self.assertIn('recent_activity', stats)
        self.assertIn('feature_usage', stats)
        self.assertIn('timestamp', stats)
    
    def test_feature_health_monitoring(self):
        """Test feature health monitoring."""
        # Test getting feature health
        health = realtime_integration.get_feature_health('tickets')
        
        self.assertIn('feature', health)
        self.assertIn('is_active', health)
        self.assertIn('recent_activity', health)
        self.assertIn('error_count', health)
        self.assertIn('timestamp', health)
    
    def test_external_service_sync(self):
        """Test external service synchronization."""
        # Test AI service sync
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {'success': True}
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async def test_ai_sync():
                return await realtime_integration.sync_with_ai_service(
                    'ticket_created',
                    {'ticket_id': self.ticket.id}
                )
            
            result = asyncio.run(test_ai_sync())
            self.assertIsNotNone(result)
        
        # Test real-time service sync
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {'success': True}
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async def test_realtime_sync():
                return await realtime_integration.sync_with_realtime_service(
                    'ticket_updated',
                    {'ticket_id': self.ticket.id}
                )
            
            result = asyncio.run(test_realtime_sync())
            self.assertIsNotNone(result)


class ServiceIntegrationTest(TransactionTestCase):
    """Test service integrations and end-to-end scenarios."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.customer = TestDataFactory.create_user(self.organization, "customer@example.com", "customer")
        self.agent = TestDataFactory.create_user(self.organization, "agent@example.com", "agent")
        self.technician = TestDataFactory.create_technician(
            self.organization,
            TestDataFactory.create_user(self.organization, "tech@example.com", "technician")
        )
    
    def test_ticket_to_work_order_flow(self):
        """Test ticket to work order conversion flow."""
        # Create ticket
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        
        # Test ticket escalation to work order
        from apps.tickets.services import TicketService
        ticket_service = TicketService()
        
        work_order = ticket_service.escalate_to_work_order(
            ticket=ticket,
            work_order_data={
                'title': f'Work Order for {ticket.subject}',
                'description': ticket.description,
                'scheduled_start': timezone.now() + timedelta(hours=1),
                'scheduled_end': timezone.now() + timedelta(hours=2),
                'location': {
                    'address': '123 Test St',
                    'city': 'Test City',
                    'coordinates': [40.7128, -74.0060]
                }
            }
        )
        
        self.assertIsNotNone(work_order)
        self.assertEqual(work_order.related_ticket, ticket)
        self.assertEqual(work_order.status, 'scheduled')
    
    def test_automation_rule_execution(self):
        """Test automation rule execution."""
        # Create automation rule
        rule = TestDataFactory.create_automation_rule(self.organization)
        
        # Create ticket that should trigger rule
        ticket = TestDataFactory.create_ticket(
            self.organization, 
            self.customer, 
            priority="high"
        )
        
        # Test rule execution
        from apps.automation.services import AutomationService
        automation_service = AutomationService()
        
        result = automation_service.execute_rule(rule, ticket)
        
        self.assertTrue(result['success'])
        self.assertIn('actions_executed', result)
        self.assertIn('execution_time', result)
    
    def test_sla_policy_application(self):
        """Test SLA policy application."""
        # Create SLA policy
        sla_policy = TestDataFactory.create_sla_policy(self.organization)
        
        # Create ticket
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        
        # Test SLA policy application
        from apps.automation.services import SLAService
        sla_service = SLAService()
        
        result = sla_service.apply_sla_policy(ticket, sla_policy)
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['due_date'])
        self.assertIn('sla_breach_time', result)
    
    def test_webhook_integration_flow(self):
        """Test webhook integration flow."""
        # Create webhook
        webhook = TestDataFactory.create_webhook(self.organization)
        
        # Create ticket
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        
        # Test webhook triggering
        from apps.integrations.services import WebhookService
        webhook_service = WebhookService()
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'success': True}
            mock_post.return_value = mock_response
            
            result = webhook_service.trigger_webhook(
                webhook=webhook,
                event_type='ticket_created',
                payload={'ticket_id': ticket.id, 'ticket_number': ticket.number}
            )
            
            self.assertTrue(result['success'])
            self.assertEqual(result['status_code'], 200)
    
    def test_notification_flow(self):
        """Test notification flow."""
        # Create ticket
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        
        # Test notification sending
        from apps.notifications.services import NotificationService
        notification_service = NotificationService()
        
        with patch('apps.notifications.tasks.send_notification.delay') as mock_send:
            result = notification_service.send_notification(
                user=self.agent,
                notification_type='ticket_assigned',
                message='You have been assigned a new ticket',
                priority='high',
                data={'ticket_id': ticket.id}
            )
            
            self.assertTrue(result['success'])
            self.assertIn('notification_id', result)
            
            # Verify task was queued
            mock_send.assert_called_once()
    
    def test_analytics_data_collection(self):
        """Test analytics data collection."""
        # Create ticket
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        
        # Test analytics data collection
        from apps.analytics.services import AnalyticsService
        analytics_service = AnalyticsService()
        
        result = analytics_service.collect_ticket_metrics(ticket)
        
        self.assertTrue(result['success'])
        self.assertIn('metrics_collected', result)
        self.assertIn('data_points', result)
    
    def test_end_to_end_ticket_flow(self):
        """Test end-to-end ticket flow."""
        # Create ticket
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        
        # Test ticket assignment
        ticket.assigned_agent = self.agent
        ticket.status = 'in_progress'
        ticket.save()
        
        # Test ticket resolution
        ticket.status = 'resolved'
        ticket.resolved_at = timezone.now()
        ticket.save()
        
        # Test ticket closure
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()
        
        # Verify ticket flow
        self.assertEqual(ticket.assigned_agent, self.agent)
        self.assertEqual(ticket.status, 'closed')
        self.assertIsNotNone(ticket.resolved_at)
        self.assertIsNotNone(ticket.closed_at)
    
    def test_end_to_end_work_order_flow(self):
        """Test end-to-end work order flow."""
        # Create work order
        work_order = TestDataFactory.create_work_order(self.organization, self.customer)
        
        # Test work order assignment
        from apps.field_service.services import WorkOrderService
        work_order_service = WorkOrderService()
        
        assignment = work_order_service.assign_technician(
            work_order=work_order,
            technician=self.technician,
            assigned_at=timezone.now()
        )
        
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.technician, self.technician)
        
        # Test work order completion
        work_order.status = 'completed'
        work_order.completed_at = timezone.now()
        work_order.save()
        
        # Verify work order flow
        self.assertEqual(work_order.status, 'completed')
        self.assertIsNotNone(work_order.completed_at)
        self.assertIsNotNone(assignment)
    
    def test_system_health_monitoring(self):
        """Test system health monitoring."""
        # Test system health check
        from apps.api.services import SystemHealthService
        health_service = SystemHealthService()
        
        health_report = health_service.get_system_health()
        
        self.assertIn('overall_status', health_report)
        self.assertIn('services', health_report)
        self.assertIn('features', health_report)
        self.assertIn('connections', health_report)
        self.assertIn('timestamp', health_report)
        
        # Test individual service health
        for service_name, service_data in health_report['services'].items():
            self.assertIn('status', service_data)
            self.assertIn('timestamp', service_data)
        
        # Test feature health
        for feature_name, feature_data in health_report['features'].items():
            self.assertIn('status', feature_data)
            self.assertIn('operations', feature_data)
            self.assertIn('timestamp', feature_data)
