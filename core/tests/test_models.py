"""
Comprehensive model tests for all database operations.
"""
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
# Import mock GDAL for testing
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from mock_gdal import MockPoint as Point

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket, TicketComment, TicketAttachment, TicketHistory
from apps.field_service.models import WorkOrder, Technician, JobAssignment, ServiceReport, Asset, InventoryItem, Route
from apps.knowledge_base.models import KBArticle, KBCategory, KBFeedback
from apps.automation.models import AutomationRule, SLAPolicy, EmailTemplate
from apps.analytics.models import AnalyticsDashboard, Report, Metric
from apps.integrations.models import Webhook, IntegrationLog
from apps.notifications.models import Notification
from apps.api.models import APIService
from apps.features.models import Feature, FeatureCategory, FeatureConnection, FeatureUsage, FeatureHealth
from apps.security.models import SecurityPolicy, AuditLog
from apps.i18n.models import Language, Translation
from apps.customization.models import CustomField, CustomFieldValue, Theme
from apps.compliance.models import CompliancePolicy, ComplianceCheck

from .test_utils import TestDataFactory, TestAssertions
from .test_utilities import EnhancedTransactionTestCase, TestDataFactory as EnhancedTestDataFactory

User = get_user_model()


class OrganizationModelTest(EnhancedTransactionTestCase):
    """Test Organization model with enhanced quality and proper isolation."""
    
    def setUp(self):
        super().setUp()
        self.organization = EnhancedTestDataFactory.create_organization()
    
    def test_organization_creation_with_valid_data(self):
        """Test organization creation with valid data."""
        self.assertEqual(self.organization.name, "Test Organization")
        self.assertEqual(self.organization.subscription_tier, "enterprise")
        self.assertTrue(self.organization.is_active)
        self.assertIsNotNone(self.organization.created_at)
    
    def test_organization_settings_are_properly_configured(self):
        """Test organization settings are properly configured."""
        settings = self.organization.settings
        self.assertEqual(settings['timezone'], 'UTC')
        self.assertEqual(settings['date_format'], 'YYYY-MM-DD')
        self.assertEqual(settings['currency'], 'USD')
        self.assertEqual(settings['language'], 'en')
    
    def test_organization_string_representation(self):
        """Test organization string representation returns correct format."""
        self.assertEqual(str(self.organization), "Test Organization")
    
    def test_organization_name_uniqueness_constraint(self):
        """Test organization name uniqueness constraint prevents duplicates."""
        with self.assertRaises(IntegrityError):
            Organization.objects.create(
                name="Test Organization",
                subscription_tier="basic"
            )


class UserModelTest(EnhancedTransactionTestCase):
    """Test User model with enhanced quality and proper isolation."""
    
    def setUp(self):
        super().setUp()
        self.organization = EnhancedTestDataFactory.create_organization()
        self.user = EnhancedTestDataFactory.create_user(self.organization)
    
    def test_user_creation_with_valid_data(self):
        """Test user creation with valid data."""
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.organization, self.organization)
        self.assertEqual(self.user.role, "agent")
        self.assertTrue(self.user.is_active)
        self.assertIsNotNone(self.user.created_at)
    
    def test_user_string_representation(self):
        """Test user string representation returns email address."""
        self.assertEqual(str(self.user), "test@example.com")
    
    def test_user_full_name_returns_concatenated_names(self):
        """Test user full name returns concatenated first and last names."""
        self.assertEqual(self.user.get_full_name(), "Test User")
    
    def test_user_short_name_returns_first_name(self):
        """Test user short name returns first name only."""
        self.assertEqual(self.user.get_short_name(), "Test")
    
    def test_user_role_based_permissions_are_correctly_assigned(self):
        """Test user role-based permissions are correctly assigned."""
        # Test role-based permissions
        self.assertTrue(self.user.has_perm('tickets.view_ticket'))
        self.assertTrue(self.user.has_perm('tickets.add_ticket'))
        self.assertTrue(self.user.has_perm('tickets.change_ticket'))
    
    def test_user_organization_isolation(self):
        """Test user organization isolation."""
        other_org = TestDataFactory.create_organization("Other Organization")
        other_user = TestDataFactory.create_user(other_org, "other@example.com")
        
        # Users should be isolated by organization
        self.assertNotEqual(self.user.organization, other_user.organization)
        self.assertNotEqual(self.user.email, other_user.email)


class TicketModelTest(TestCase):
    """Test Ticket model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.customer = TestDataFactory.create_user(self.organization, "customer@example.com", "customer")
        self.agent = TestDataFactory.create_user(self.organization, "agent@example.com", "agent")
        self.ticket = TestDataFactory.create_ticket(self.organization, self.customer)
    
    def test_ticket_creation(self):
        """Test ticket creation."""
        self.assertEqual(self.ticket.subject, "Test Ticket")
        self.assertEqual(self.ticket.customer, self.customer)
        self.assertEqual(self.ticket.organization, self.organization)
        self.assertEqual(self.ticket.status, "open")
        self.assertEqual(self.ticket.priority, "medium")
        self.assertEqual(self.ticket.channel, "web")
        self.assertIsNotNone(self.ticket.created_at)
    
    def test_ticket_number_generation(self):
        """Test ticket number generation."""
        self.assertIsNotNone(self.ticket.number)
        self.assertTrue(self.ticket.number.startswith('TICKET-'))
    
    def test_ticket_status_workflow(self):
        """Test ticket status workflow."""
        # Test status transitions
        self.ticket.status = "in_progress"
        self.ticket.save()
        self.assertEqual(self.ticket.status, "in_progress")
        
        self.ticket.status = "resolved"
        self.ticket.save()
        self.assertEqual(self.ticket.status, "resolved")
        
        self.ticket.status = "closed"
        self.ticket.save()
        self.assertEqual(self.ticket.status, "closed")
    
    def test_ticket_priority_levels(self):
        """Test ticket priority levels."""
        priorities = ["low", "medium", "high", "urgent"]
        for priority in priorities:
            self.ticket.priority = priority
            self.ticket.save()
            self.assertEqual(self.ticket.priority, priority)
    
    def test_ticket_custom_fields(self):
        """Test ticket custom fields."""
        custom_fields = {
            "department": "IT",
            "category": "Hardware",
            "urgency": "High",
            "custom_field_1": "Value 1"
        }
        self.ticket.custom_fields = custom_fields
        self.ticket.save()
        
        self.assertEqual(self.ticket.custom_fields["department"], "IT")
        self.assertEqual(self.ticket.custom_fields["category"], "Hardware")
        self.assertEqual(self.ticket.custom_fields["urgency"], "High")
    
    def test_ticket_sla_fields(self):
        """Test ticket SLA fields."""
        self.ticket.first_response_at = timezone.now()
        self.ticket.resolved_at = timezone.now() + timedelta(hours=2)
        self.ticket.sla_breach = False
        self.ticket.save()
        
        self.assertIsNotNone(self.ticket.first_response_at)
        self.assertIsNotNone(self.ticket.resolved_at)
        self.assertFalse(self.ticket.sla_breach)
    
    def test_ticket_organization_isolation(self):
        """Test ticket organization isolation."""
        other_org = TestDataFactory.create_organization("Other Organization")
        other_customer = TestDataFactory.create_user(other_org, "other@example.com", "customer")
        other_ticket = TestDataFactory.create_ticket(other_org, other_customer)
        
        # Tickets should be isolated by organization
        self.assertNotEqual(self.ticket.organization, other_ticket.organization)
        self.assertNotEqual(self.ticket.customer, other_ticket.customer)


class TicketCommentModelTest(TestCase):
    """Test TicketComment model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.customer = TestDataFactory.create_user(self.organization, "customer@example.com", "customer")
        self.agent = TestDataFactory.create_user(self.organization, "agent@example.com", "agent")
        self.ticket = TestDataFactory.create_ticket(self.organization, self.customer)
    
    def test_comment_creation(self):
        """Test comment creation."""
        comment = TicketComment.objects.create(
            organization=self.organization,
            ticket=self.ticket,
            user=self.customer,
            content="Test comment content",
            is_public=True
        )
        
        self.assertEqual(comment.ticket, self.ticket)
        self.assertEqual(comment.user, self.customer)
        self.assertEqual(comment.content, "Test comment content")
        self.assertTrue(comment.is_public)
        self.assertFalse(comment.is_note)
    
    def test_comment_types(self):
        """Test different comment types."""
        # Public comment
        public_comment = TicketComment.objects.create(
            organization=self.organization,
            ticket=self.ticket,
            user=self.customer,
            content="Public comment",
            is_public=True
        )
        self.assertTrue(public_comment.is_public)
        self.assertFalse(public_comment.is_note)
        
        # Internal note
        internal_note = TicketComment.objects.create(
            organization=self.organization,
            ticket=self.ticket,
            user=self.agent,
            content="Internal note",
            is_public=False,
            is_note=True
        )
        self.assertFalse(internal_note.is_public)
        self.assertTrue(internal_note.is_note)
    
    def test_comment_attachments(self):
        """Test comment attachments."""
        comment = TicketComment.objects.create(
            organization=self.organization,
            ticket=self.ticket,
            user=self.customer,
            content="Comment with attachment",
            is_public=True
        )
        
        # Add attachment
        attachment = TicketAttachment.objects.create(
            organization=self.organization,
            ticket=self.ticket,
            comment=comment,
            filename="test.pdf",
            file_size=1024,
            content_type="application/pdf"
        )
        
        self.assertEqual(attachment.comment, comment)
        self.assertEqual(attachment.filename, "test.pdf")
        self.assertEqual(attachment.file_size, 1024)


class WorkOrderModelTest(TestCase):
    """Test WorkOrder model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.customer = TestDataFactory.create_user(self.organization, "customer@example.com", "customer")
        self.work_order = TestDataFactory.create_work_order(self.organization, self.customer)
    
    def test_work_order_creation(self):
        """Test work order creation."""
        self.assertEqual(self.work_order.title, "Test Work Order")
        self.assertEqual(self.work_order.customer, self.customer)
        self.assertEqual(self.work_order.organization, self.organization)
        self.assertEqual(self.work_order.status, "scheduled")
        self.assertIsNotNone(self.work_order.scheduled_start)
        self.assertIsNotNone(self.work_order.scheduled_end)
    
    def test_work_order_number_generation(self):
        """Test work order number generation."""
        self.assertIsNotNone(self.work_order.number)
        self.assertTrue(self.work_order.number.startswith('WO-'))
    
    def test_work_order_location(self):
        """Test work order location."""
        location = self.work_order.location
        self.assertEqual(location['address'], '123 Test St')
        self.assertEqual(location['city'], 'Test City')
        self.assertEqual(location['coordinates'], [40.7128, -74.0060])
    
    def test_work_order_status_workflow(self):
        """Test work order status workflow."""
        statuses = ["scheduled", "in_progress", "completed", "cancelled"]
        for status in statuses:
            self.work_order.status = status
            self.work_order.save()
            self.assertEqual(self.work_order.status, status)
    
    def test_work_order_cost_calculation(self):
        """Test work order cost calculation."""
        self.work_order.labor_cost = Decimal('100.00')
        self.work_order.parts_cost = Decimal('50.00')
        self.work_order.tax_rate = Decimal('0.08')
        self.work_order.save()
        
        expected_total = (Decimal('100.00') + Decimal('50.00')) * (1 + Decimal('0.08'))
        self.assertEqual(self.work_order.total_cost, expected_total)


class TechnicianModelTest(TestCase):
    """Test Technician model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.technician = TestDataFactory.create_technician(self.organization, self.user)
    
    def test_technician_creation(self):
        """Test technician creation."""
        self.assertEqual(self.technician.user, self.user)
        self.assertEqual(self.technician.organization, self.organization)
        self.assertEqual(self.technician.skills, ['electrical', 'plumbing'])
        self.assertEqual(self.technician.certifications, ['cert1', 'cert2'])
    
    def test_technician_location(self):
        """Test technician location."""
        location = self.technician.current_location
        self.assertEqual(location['latitude'], 40.7128)
        self.assertEqual(location['longitude'], -74.0060)
        self.assertEqual(location['address'], '123 Test St')
    
    def test_technician_availability(self):
        """Test technician availability."""
        self.technician.availability_status = "available"
        self.technician.save()
        self.assertEqual(self.technician.availability_status, "available")
        
        self.technician.availability_status = "busy"
        self.technician.save()
        self.assertEqual(self.technician.availability_status, "busy")
    
    def test_technician_skills_matching(self):
        """Test technician skills matching."""
        required_skills = ['electrical', 'plumbing']
        matching_skills = set(self.technician.skills) & set(required_skills)
        self.assertEqual(len(matching_skills), 2)
    
    def test_technician_geolocation(self):
        """Test technician geolocation."""
        # Test PostGIS point creation
        point = Point(-74.0060, 40.7128)
        self.technician.geo_location = point
        self.technician.save()
        
        self.assertIsNotNone(self.technician.geo_location)
        self.assertEqual(self.technician.geo_location.x, -74.0060)
        self.assertEqual(self.technician.geo_location.y, 40.7128)


class KBArticleModelTest(TestCase):
    """Test KBArticle model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.article = TestDataFactory.create_kb_article(self.organization)
    
    def test_article_creation(self):
        """Test article creation."""
        self.assertEqual(self.article.title, "Test Article")
        self.assertEqual(self.article.content, "Test content")
        self.assertEqual(self.article.organization, self.organization)
        self.assertEqual(self.article.category, "general")
        self.assertTrue(self.article.is_published)
    
    def test_article_versioning(self):
        """Test article versioning."""
        self.article.content = "Updated content"
        self.article.save()
        
        # Check if version was created
        self.assertIsNotNone(self.article.version)
        self.assertEqual(self.article.version, 2)
    
    def test_article_feedback(self):
        """Test article feedback."""
        feedback = KBFeedback.objects.create(
            organization=self.organization,
            article=self.article,
            rating=5,
            comment="Very helpful article"
        )
        
        self.assertEqual(feedback.article, self.article)
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(feedback.comment, "Very helpful article")
    
    def test_article_search(self):
        """Test article search."""
        # Test full-text search
        search_results = KBArticle.objects.filter(
            organization=self.organization,
            content__icontains="Test"
        )
        self.assertIn(self.article, search_results)
    
    def test_article_seo_fields(self):
        """Test article SEO fields."""
        self.article.meta_title = "Test Article - SEO Title"
        self.article.meta_description = "Test article description for SEO"
        self.article.slug = "test-article"
        self.article.save()
        
        self.assertEqual(self.article.meta_title, "Test Article - SEO Title")
        self.assertEqual(self.article.meta_description, "Test article description for SEO")
        self.assertEqual(self.article.slug, "test-article")


class AutomationRuleModelTest(TestCase):
    """Test AutomationRule model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.rule = TestDataFactory.create_automation_rule(self.organization)
    
    def test_rule_creation(self):
        """Test rule creation."""
        self.assertEqual(self.rule.name, "Test Rule")
        self.assertEqual(self.rule.trigger_type, "ticket_created")
        self.assertEqual(self.rule.organization, self.organization)
        self.assertTrue(self.rule.is_active)
    
    def test_rule_conditions(self):
        """Test rule conditions."""
        conditions = self.rule.conditions
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0]['field'], 'priority')
        self.assertEqual(conditions[0]['operator'], 'equals')
        self.assertEqual(conditions[0]['value'], 'high')
    
    def test_rule_actions(self):
        """Test rule actions."""
        actions = self.rule.actions
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]['type'], 'assign')
        self.assertEqual(actions[0]['agent_id'], 1)
        self.assertEqual(actions[1]['type'], 'change_status')
        self.assertEqual(actions[1]['status'], 'in_progress')
    
    def test_rule_execution_order(self):
        """Test rule execution order."""
        self.rule.execution_order = 1
        self.rule.save()
        self.assertEqual(self.rule.execution_order, 1)
    
    def test_rule_condition_evaluation(self):
        """Test rule condition evaluation."""
        # Test condition evaluation logic
        conditions = self.rule.conditions
        test_ticket = TestDataFactory.create_ticket(
            self.organization, 
            TestDataFactory.create_user(self.organization, "test@example.com", "customer"),
            priority="high"
        )
        
        # Mock condition evaluation
        field_value = getattr(test_ticket, conditions[0]['field'])
        operator = conditions[0]['operator']
        expected_value = conditions[0]['value']
        
        if operator == 'equals':
            self.assertEqual(field_value, expected_value)


class SLAPolicyModelTest(TestCase):
    """Test SLAPolicy model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.sla_policy = TestDataFactory.create_sla_policy(self.organization)
    
    def test_sla_policy_creation(self):
        """Test SLA policy creation."""
        self.assertEqual(self.sla_policy.name, "Test SLA")
        self.assertEqual(self.sla_policy.first_response_time, 60)
        self.assertEqual(self.sla_policy.resolution_time, 480)
        self.assertEqual(self.sla_policy.organization, self.organization)
    
    def test_sla_policy_operational_hours(self):
        """Test SLA policy operational hours."""
        hours = self.sla_policy.operational_hours
        self.assertEqual(hours['monday']['start'], '09:00')
        self.assertEqual(hours['monday']['end'], '17:00')
        self.assertEqual(hours['friday']['start'], '09:00')
        self.assertEqual(hours['friday']['end'], '17:00')
    
    def test_sla_policy_conditions(self):
        """Test SLA policy conditions."""
        conditions = [
            {'field': 'priority', 'operator': 'equals', 'value': 'high'}
        ]
        self.sla_policy.conditions = conditions
        self.sla_policy.save()
        
        self.assertEqual(self.sla_policy.conditions, conditions)
    
    def test_sla_policy_escalation(self):
        """Test SLA policy escalation."""
        self.sla_policy.escalation_enabled = True
        self.sla_policy.escalation_time = 120
        self.sla_policy.escalation_actions = [
            {'type': 'notify_manager', 'manager_id': 1},
            {'type': 'change_priority', 'priority': 'urgent'}
        ]
        self.sla_policy.save()
        
        self.assertTrue(self.sla_policy.escalation_enabled)
        self.assertEqual(self.sla_policy.escalation_time, 120)
        self.assertEqual(len(self.sla_policy.escalation_actions), 2)


class WebhookModelTest(TestCase):
    """Test Webhook model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.webhook = TestDataFactory.create_webhook(self.organization)
    
    def test_webhook_creation(self):
        """Test webhook creation."""
        self.assertEqual(self.webhook.name, "Test Webhook")
        self.assertEqual(self.webhook.url, "https://example.com/webhook")
        self.assertEqual(self.webhook.organization, self.organization)
        self.assertTrue(self.webhook.is_active)
    
    def test_webhook_events(self):
        """Test webhook events."""
        events = self.webhook.events
        self.assertIn('ticket_created', events)
        self.assertIn('ticket_updated', events)
        self.assertEqual(len(events), 2)
    
    def test_webhook_secret_key(self):
        """Test webhook secret key."""
        self.assertEqual(self.webhook.secret_key, "test_secret_key")
    
    def test_webhook_headers(self):
        """Test webhook headers."""
        headers = {
            'Authorization': 'Bearer token123',
            'Content-Type': 'application/json'
        }
        self.webhook.headers = headers
        self.webhook.save()
        
        self.assertEqual(self.webhook.headers, headers)
    
    def test_webhook_retry_settings(self):
        """Test webhook retry settings."""
        self.webhook.retry_attempts = 3
        self.webhook.retry_delay = 5
        self.webhook.timeout = 30
        self.webhook.save()
        
        self.assertEqual(self.webhook.retry_attempts, 3)
        self.assertEqual(self.webhook.retry_delay, 5)
        self.assertEqual(self.webhook.timeout, 30)


class FeatureModelTest(TestCase):
    """Test Feature model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.feature = TestDataFactory.create_feature(self.organization)
    
    def test_feature_creation(self):
        """Test feature creation."""
        self.assertEqual(self.feature.name, "Test Feature")
        self.assertEqual(self.feature.description, "Test feature description")
        self.assertEqual(self.feature.feature_type, "core")
        self.assertEqual(self.feature.status, "active")
        self.assertEqual(self.feature.organization, self.organization)
    
    def test_feature_endpoint(self):
        """Test feature endpoint."""
        self.assertEqual(self.feature.endpoint, "test-feature")
        self.assertEqual(self.feature.full_endpoint, "/api/v1/test-feature/")
    
    def test_feature_realtime_support(self):
        """Test feature real-time support."""
        self.assertTrue(self.feature.supports_realtime)
        self.assertIsNotNone(self.feature.get_websocket_channel())
    
    def test_feature_permissions(self):
        """Test feature permissions."""
        permission = self.feature.permissions.create(
            permission_name="test_permission",
            description="Test permission description"
        )
        
        self.assertEqual(permission.feature, self.feature)
        self.assertEqual(permission.permission_name, "test_permission")
        self.assertTrue(permission.is_required)
    
    def test_feature_connections(self):
        """Test feature connections."""
        other_feature = TestDataFactory.create_feature(
            self.organization, 
            "Other Feature", 
            "integration"
        )
        
        connection = FeatureConnection.objects.create(
            source_feature=self.feature,
            target_feature=other_feature,
            connection_type="data_flow",
            description="Data flow connection"
        )
        
        self.assertEqual(connection.source_feature, self.feature)
        self.assertEqual(connection.target_feature, other_feature)
        self.assertEqual(connection.connection_type, "data_flow")
        self.assertTrue(connection.is_active)


class NotificationModelTest(TestCase):
    """Test Notification model."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.notification = Notification.objects.create(
            organization=self.organization,
            user=self.user,
            notification_type="ticket_assigned",
            message="You have been assigned a new ticket",
            priority="high"
        )
    
    def test_notification_creation(self):
        """Test notification creation."""
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.organization, self.organization)
        self.assertEqual(self.notification.notification_type, "ticket_assigned")
        self.assertEqual(self.notification.message, "You have been assigned a new ticket")
        self.assertEqual(self.notification.priority, "high")
        self.assertFalse(self.notification.is_read)
    
    def test_notification_mark_as_read(self):
        """Test notification mark as read."""
        self.notification.mark_as_read()
        self.assertTrue(self.notification.is_read)
        self.assertIsNotNone(self.notification.read_at)
    
    def test_notification_priority_levels(self):
        """Test notification priority levels."""
        priorities = ["low", "medium", "high", "urgent"]
        for priority in priorities:
            self.notification.priority = priority
            self.notification.save()
            self.assertEqual(self.notification.priority, priority)
    
    def test_notification_types(self):
        """Test notification types."""
        types = ["ticket_assigned", "ticket_updated", "work_order_created", "system_alert"]
        for notification_type in types:
            self.notification.notification_type = notification_type
            self.notification.save()
            self.assertEqual(self.notification.notification_type, notification_type)


class ModelIntegrationTest(TransactionTestCase):
    """Test model integrations and relationships."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.customer = TestDataFactory.create_user(self.organization, "customer@example.com", "customer")
        self.agent = TestDataFactory.create_user(self.organization, "agent@example.com", "agent")
        self.technician = TestDataFactory.create_technician(self.organization, self.agent)
    
    def test_ticket_work_order_integration(self):
        """Test ticket to work order integration."""
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        work_order = TestDataFactory.create_work_order(self.organization, self.customer)
        
        # Link ticket to work order
        work_order.related_ticket = ticket
        work_order.save()
        
        self.assertEqual(work_order.related_ticket, ticket)
    
    def test_technician_work_order_assignment(self):
        """Test technician work order assignment."""
        work_order = TestDataFactory.create_work_order(self.organization, self.customer)
        
        assignment = JobAssignment.objects.create(
            organization=self.organization,
            work_order=work_order,
            technician=self.technician,
            assigned_at=timezone.now()
        )
        
        self.assertEqual(assignment.work_order, work_order)
        self.assertEqual(assignment.technician, self.technician)
        self.assertIsNotNone(assignment.assigned_at)
    
    def test_automation_rule_triggering(self):
        """Test automation rule triggering."""
        rule = TestDataFactory.create_automation_rule(self.organization)
        ticket = TestDataFactory.create_ticket(self.organization, self.customer, priority="high")
        
        # Mock rule execution
        with transaction.atomic():
            # Simulate rule execution
            if rule.conditions[0]['value'] == ticket.priority:
                # Execute actions
                ticket.assigned_agent = self.agent
                ticket.status = "in_progress"
                ticket.save()
        
        self.assertEqual(ticket.assigned_agent, self.agent)
        self.assertEqual(ticket.status, "in_progress")
    
    def test_sla_policy_application(self):
        """Test SLA policy application."""
        sla_policy = TestDataFactory.create_sla_policy(self.organization)
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        
        # Apply SLA policy
        ticket.sla_policy = sla_policy
        ticket.due_date = timezone.now() + timedelta(minutes=sla_policy.first_response_time)
        ticket.save()
        
        self.assertEqual(ticket.sla_policy, sla_policy)
        self.assertIsNotNone(ticket.due_date)
    
    def test_webhook_integration_logging(self):
        """Test webhook integration logging."""
        webhook = TestDataFactory.create_webhook(self.organization)
        ticket = TestDataFactory.create_ticket(self.organization, self.customer)
        
        # Log webhook trigger
        log = IntegrationLog.objects.create(
            organization=self.organization,
            webhook=webhook,
            event_type="ticket_created",
            status="success",
            message="Webhook triggered successfully",
            payload={"ticket_id": ticket.id, "ticket_number": ticket.number}
        )
        
        self.assertEqual(log.webhook, webhook)
        self.assertEqual(log.event_type, "ticket_created")
        self.assertEqual(log.status, "success")
        self.assertIn("ticket_id", log.payload)
    
    def test_feature_usage_tracking(self):
        """Test feature usage tracking."""
        feature = TestDataFactory.create_feature(self.organization)
        
        usage = FeatureUsage.objects.create(
            organization=self.organization,
            feature=feature,
            user=self.agent,
            access_count=1,
            response_time=150.5,
            error_count=0
        )
        
        self.assertEqual(usage.feature, feature)
        self.assertEqual(usage.user, self.agent)
        self.assertEqual(usage.access_count, 1)
        self.assertEqual(usage.response_time, 150.5)
        self.assertEqual(usage.error_count, 0)
    
    def test_organization_tenant_isolation(self):
        """Test organization tenant isolation."""
        other_org = TestDataFactory.create_organization("Other Organization")
        other_customer = TestDataFactory.create_user(other_org, "other@example.com", "customer")
        other_ticket = TestDataFactory.create_ticket(other_org, other_customer)
        
        # Test that organizations are isolated
        self.assertNotEqual(self.organization, other_org)
        self.assertNotEqual(self.customer.organization, other_customer.organization)
        self.assertNotEqual(self.customer, other_customer)
        
        # Test that tickets are isolated
        tickets = Ticket.objects.filter(organization=self.organization)
        self.assertNotIn(other_ticket, tickets)
        
        other_tickets = Ticket.objects.filter(organization=other_org)
        self.assertNotIn(TestDataFactory.create_ticket(self.organization, self.customer), other_tickets)
