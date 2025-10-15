"""
Comprehensive test suite for Enhanced SLA Management System
Tests all SLA management functionality with comprehensive coverage
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.tickets.sla import SLAManager, SLAPolicy, SLAPolicyNotFound
from apps.tickets.models import Ticket
from apps.accounts.models import User
from apps.organizations.models import Organization


class TestSLAManager(TestCase):
    """Test suite for SLA Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org",
            timezone="UTC"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            organization=self.organization
        )
        self.sla_manager = SLAManager(organization_id=self.organization.id)
        
        # Create test SLA policy
        self.sla_policy = SLAPolicy.objects.create(
            name="High Priority SLA",
            description="SLA for high priority tickets",
            organization=self.organization,
            response_time=60,  # 60 minutes
            resolution_time=240,  # 240 minutes (4 hours)
            conditions=[
                {"field": "priority", "operator": "equals", "value": "high"}
            ],
            is_active=True
        )
        
        # Create test ticket
        self.ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Test Ticket",
            description="This is a test ticket",
            priority="high",
            status="open",
            created_at=timezone.now() - timedelta(minutes=30)  # Created 30 mins ago
        )
    
    def test_sla_manager_initialization(self):
        """Test SLA Manager initialization"""
        self.assertEqual(self.sla_manager.organization_id, self.organization.id)
        self.assertIsNotNone(self.sla_manager.business_hours)
        self.assertIsNotNone(self.sla_manager.timezone)
    
    def test_get_applicable_policy_org_specific(self):
        """Test getting organization-specific SLA policy"""
        policy = self.sla_manager.get_applicable_policy(self.ticket)
        
        self.assertEqual(policy, self.sla_policy)
        self.assertEqual(policy.name, "High Priority SLA")
        self.assertEqual(policy.response_time, 60)
        self.assertEqual(policy.resolution_time, 240)
    
    def test_get_applicable_policy_global_fallback(self):
        """Test getting global SLA policy as fallback"""
        # Deactivate org-specific policy
        self.sla_policy.is_active = False
        self.sla_policy.save()
        
        # Create global policy
        global_policy = SLAPolicy.objects.create(
            name="Global Default SLA",
            description="Default SLA for all organizations",
            response_time=120,
            resolution_time=480,
            is_active=True,
            is_global=True,
            conditions=[]
        )
        
        policy = self.sla_manager.get_applicable_policy(self.ticket)
        
        self.assertEqual(policy, global_policy)
        self.assertEqual(policy.name, "Global Default SLA")
        self.assertTrue(policy.is_global)
    
    def test_get_applicable_policy_not_found(self):
        """Test when no applicable SLA policy is found"""
        # Deactivate all policies
        SLAPolicy.objects.all().update(is_active=False)
        
        with self.assertRaises(SLAPolicyNotFound):
            self.sla_manager.get_applicable_policy(self.ticket)
    
    def test_evaluate_conditions_true(self):
        """Test condition evaluation when conditions are met"""
        conditions = [{"field": "priority", "operator": "equals", "value": "high"}]
        result = self.sla_manager.evaluate_conditions(self.ticket, conditions)
        
        self.assertTrue(result)
    
    def test_evaluate_conditions_false(self):
        """Test condition evaluation when conditions are not met"""
        conditions = [{"field": "priority", "operator": "equals", "value": "low"}]
        result = self.sla_manager.evaluate_conditions(self.ticket, conditions)
        
        self.assertFalse(result)
    
    def test_evaluate_conditions_multiple(self):
        """Test condition evaluation with multiple conditions"""
        conditions = [
            {"field": "priority", "operator": "equals", "value": "high"},
            {"field": "status", "operator": "equals", "value": "open"}
        ]
        result = self.sla_manager.evaluate_conditions(self.ticket, conditions)
        
        self.assertTrue(result)
    
    def test_evaluate_conditions_complex(self):
        """Test condition evaluation with complex conditions"""
        conditions = [
            {"field": "priority", "operator": "in", "value": ["high", "urgent"]},
            {"field": "status", "operator": "not_equals", "value": "closed"}
        ]
        result = self.sla_manager.evaluate_conditions(self.ticket, conditions)
        
        self.assertTrue(result)
    
    def test_calculate_due_date_response_time(self):
        """Test due date calculation for response time"""
        due_date = self.sla_manager.calculate_due_date(self.ticket, self.sla_policy)
        
        # Ticket created 30 mins ago, response time 60 mins
        # Due date should be 30 minutes from now
        expected_due_date = self.ticket.created_at + timedelta(minutes=self.sla_policy.response_time)
        
        # Allow for small time differences
        time_diff = abs((due_date - expected_due_date).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute
    
    def test_calculate_due_date_resolution_time(self):
        """Test due date calculation for resolution time"""
        due_date = self.sla_manager.calculate_due_date(self.ticket, self.sla_policy, sla_type="resolution")
        
        # Ticket created 30 mins ago, resolution time 240 mins
        # Due date should be 210 minutes from now
        expected_due_date = self.ticket.created_at + timedelta(minutes=self.sla_policy.resolution_time)
        
        # Allow for small time differences
        time_diff = abs((due_date - expected_due_date).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute
    
    def test_calculate_due_date_business_hours(self):
        """Test due date calculation with business hours"""
        # Mock business hours (9 AM - 5 PM, Monday-Friday)
        with patch.object(self.sla_manager, '_get_business_hours') as mock_business_hours:
            mock_business_hours.return_value = {
                "start": "09:00",
                "end": "17:00",
                "days": [1, 2, 3, 4, 5]  # Monday-Friday
            }
            
            due_date = self.sla_manager.calculate_due_date(self.ticket, self.sla_policy)
            
            self.assertIsInstance(due_date, datetime)
            self.assertGreater(due_date, timezone.now())
    
    def test_check_breach_not_breached(self):
        """Test SLA breach check when not breached"""
        is_breached, details = self.sla_manager.check_breach(self.ticket)
        
        self.assertFalse(is_breached)
        self.assertEqual(details["reason"], "SLA not breached")
        self.assertIn("time_remaining", details)
        self.assertGreater(details["time_remaining"], 0)
    
    def test_check_breach_response_time_breached(self):
        """Test SLA breach check when response time is breached"""
        # Simulate ticket created long ago to breach response time
        self.ticket.created_at = timezone.now() - timedelta(minutes=self.sla_policy.response_time + 1)
        self.ticket.save()
        
        is_breached, details = self.sla_manager.check_breach(self.ticket)
        
        self.assertTrue(is_breached)
        self.assertEqual(details["reason"], "SLA deadline exceeded")
        self.assertEqual(details["sla_policy"], self.sla_policy.name)
        self.assertIn("breach_time", details)
    
    def test_check_breach_resolution_time_breached(self):
        """Test SLA breach check when resolution time is breached"""
        # Simulate ticket created long ago to breach resolution time
        self.ticket.created_at = timezone.now() - timedelta(minutes=self.sla_policy.resolution_time + 1)
        self.ticket.save()
        
        is_breached, details = self.sla_manager.check_breach(self.ticket, sla_type="resolution")
        
        self.assertTrue(is_breached)
        self.assertEqual(details["reason"], "SLA deadline exceeded")
        self.assertEqual(details["sla_policy"], self.sla_policy.name)
    
    def test_get_sla_status_not_breached(self):
        """Test getting SLA status when not breached"""
        status_info = self.sla_manager.get_sla_status(self.ticket)
        
        self.assertFalse(status_info["is_breached"])
        self.assertEqual(status_info["status"], "Within SLA")
        self.assertIn("time_remaining", status_info)
        self.assertGreater(status_info["time_remaining"], 0)
    
    def test_get_sla_status_breached(self):
        """Test getting SLA status when breached"""
        # Simulate ticket created long ago to breach SLA
        self.ticket.created_at = timezone.now() - timedelta(minutes=self.sla_policy.response_time + 1)
        self.ticket.save()
        
        status_info = self.sla_manager.get_sla_status(self.ticket)
        
        self.assertTrue(status_info["is_breached"])
        self.assertEqual(status_info["status"], "SLA Breached")
        self.assertEqual(status_info["breach_reason"], "SLA deadline exceeded")
        self.assertIn("breach_time", status_info)
    
    def test_get_sla_status_no_policy(self):
        """Test getting SLA status when no policy is found"""
        # Deactivate all policies
        SLAPolicy.objects.all().update(is_active=False)
        
        status_info = self.sla_manager.get_sla_status(self.ticket)
        
        self.assertFalse(status_info["is_breached"])
        self.assertEqual(status_info["status"], "No SLA Policy")
        self.assertIsNone(status_info.get("time_remaining"))
    
    def test_calculate_response_time(self):
        """Test response time calculation"""
        response_time = self.sla_manager._calculate_response_time(self.sla_policy, self.ticket)
        
        self.assertEqual(response_time, self.sla_policy.response_time)
    
    def test_calculate_resolution_time(self):
        """Test resolution time calculation"""
        resolution_time = self.sla_manager._calculate_resolution_time(self.sla_policy, self.ticket)
        
        self.assertEqual(resolution_time, self.sla_policy.resolution_time)
    
    def test_get_business_hours(self):
        """Test business hours retrieval"""
        business_hours = self.sla_manager._get_business_hours()
        
        self.assertIsInstance(business_hours, dict)
        self.assertIn("start", business_hours)
        self.assertIn("end", business_hours)
        self.assertIn("days", business_hours)
    
    def test_get_organization_timezone(self):
        """Test organization timezone retrieval"""
        timezone = self.sla_manager._get_organization_timezone()
        
        self.assertIsInstance(timezone, str)
        self.assertEqual(timezone, "UTC")
    
    def test_sla_manager_without_organization(self):
        """Test SLA Manager without organization"""
        manager = SLAManager(organization_id=None)
        
        self.assertIsNone(manager.organization_id)
        self.assertIsNotNone(manager.business_hours)
        self.assertIsNotNone(manager.timezone)


class TestSLAPolicy(TestCase):
    """Test suite for SLA Policy Model"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
    
    def test_sla_policy_creation(self):
        """Test SLA Policy creation"""
        policy = SLAPolicy.objects.create(
            name="Test SLA Policy",
            description="Test SLA policy description",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            conditions=[
                {"field": "priority", "operator": "equals", "value": "high"}
            ],
            is_active=True
        )
        
        self.assertEqual(policy.name, "Test SLA Policy")
        self.assertEqual(policy.organization, self.organization)
        self.assertEqual(policy.response_time, 60)
        self.assertEqual(policy.resolution_time, 240)
        self.assertTrue(policy.is_active)
        self.assertIsInstance(policy.conditions, list)
        self.assertEqual(len(policy.conditions), 1)
    
    def test_sla_policy_global(self):
        """Test global SLA Policy creation"""
        policy = SLAPolicy.objects.create(
            name="Global SLA Policy",
            description="Global SLA policy description",
            response_time=120,
            resolution_time=480,
            is_global=True,
            is_active=True,
            conditions=[]
        )
        
        self.assertTrue(policy.is_global)
        self.assertIsNone(policy.organization)
        self.assertEqual(policy.response_time, 120)
        self.assertEqual(policy.resolution_time, 480)
    
    def test_sla_policy_string_representation(self):
        """Test SLA Policy string representation"""
        policy = SLAPolicy.objects.create(
            name="Test SLA Policy",
            description="Test SLA policy description",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            is_active=True
        )
        
        expected_str = f"Test SLA Policy ({self.organization.name})"
        self.assertEqual(str(policy), expected_str)
    
    def test_sla_policy_global_string_representation(self):
        """Test global SLA Policy string representation"""
        policy = SLAPolicy.objects.create(
            name="Global SLA Policy",
            description="Global SLA policy description",
            response_time=120,
            resolution_time=480,
            is_global=True,
            is_active=True
        )
        
        expected_str = "Global SLA Policy (Global)"
        self.assertEqual(str(policy), expected_str)
    
    def test_sla_policy_validation(self):
        """Test SLA Policy validation"""
        # Test valid policy
        policy = SLAPolicy(
            name="Valid Policy",
            description="Valid policy description",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            is_active=True
        )
        
        self.assertTrue(policy.full_clean())
    
    def test_sla_policy_conditions_validation(self):
        """Test SLA Policy conditions validation"""
        # Test valid conditions
        valid_conditions = [
            {"field": "priority", "operator": "equals", "value": "high"},
            {"field": "status", "operator": "not_equals", "value": "closed"}
        ]
        
        policy = SLAPolicy(
            name="Test Policy",
            description="Test policy description",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            conditions=valid_conditions,
            is_active=True
        )
        
        self.assertTrue(policy.full_clean())
    
    def test_sla_policy_ordering(self):
        """Test SLA Policy ordering"""
        policy1 = SLAPolicy.objects.create(
            name="B Policy",
            description="B policy description",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            is_active=True
        )
        
        policy2 = SLAPolicy.objects.create(
            name="A Policy",
            description="A policy description",
            organization=self.organization,
            response_time=120,
            resolution_time=480,
            is_active=True
        )
        
        policies = list(SLAPolicy.objects.all())
        self.assertEqual(policies[0], policy2)  # A Policy should come first
        self.assertEqual(policies[1], policy1)  # B Policy should come second


class TestSLAEdgeCases(TestCase):
    """Test suite for SLA edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            organization=self.organization
        )
        self.sla_manager = SLAManager(organization_id=self.organization.id)
    
    def test_ticket_without_sla_policy(self):
        """Test ticket without applicable SLA policy"""
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Test Ticket",
            description="This is a test ticket",
            priority="low",
            status="open"
        )
        
        # No SLA policy matches this ticket
        with self.assertRaises(SLAPolicyNotFound):
            self.sla_manager.get_applicable_policy(ticket)
    
    def test_ticket_with_multiple_matching_policies(self):
        """Test ticket with multiple matching SLA policies"""
        # Create multiple policies that could match
        policy1 = SLAPolicy.objects.create(
            name="General Policy",
            description="General policy",
            organization=self.organization,
            response_time=120,
            resolution_time=480,
            conditions=[{"field": "priority", "operator": "in", "value": ["low", "medium"]}],
            is_active=True
        )
        
        policy2 = SLAPolicy.objects.create(
            name="Specific Policy",
            description="Specific policy",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            conditions=[
                {"field": "priority", "operator": "equals", "value": "low"},
                {"field": "status", "operator": "equals", "value": "open"}
            ],
            is_active=True
        )
        
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Test Ticket",
            description="This is a test ticket",
            priority="low",
            status="open"
        )
        
        # Should return the most specific policy
        policy = self.sla_manager.get_applicable_policy(ticket)
        self.assertEqual(policy, policy2)  # More specific policy
    
    def test_ticket_created_outside_business_hours(self):
        """Test ticket created outside business hours"""
        # Create ticket on weekend (outside business hours)
        weekend_time = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        # Find the next Saturday
        days_ahead = 5 - weekend_time.weekday()  # Saturday is 5
        if days_ahead <= 0:
            days_ahead += 7
        weekend_time += timedelta(days=days_ahead)
        
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Weekend Ticket",
            description="This ticket was created on weekend",
            priority="high",
            status="open",
            created_at=weekend_time
        )
        
        sla_policy = SLAPolicy.objects.create(
            name="Weekend Policy",
            description="Policy for weekend tickets",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            conditions=[{"field": "priority", "operator": "equals", "value": "high"}],
            is_active=True
        )
        
        # Should still be able to calculate due date
        due_date = self.sla_manager.calculate_due_date(ticket, sla_policy)
        self.assertIsInstance(due_date, datetime)
        self.assertGreater(due_date, timezone.now())
    
    def test_ticket_with_complex_conditions(self):
        """Test ticket with complex SLA conditions"""
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Complex Ticket",
            description="This ticket has complex conditions",
            priority="urgent",
            status="open"
        )
        
        sla_policy = SLAPolicy.objects.create(
            name="Complex Policy",
            description="Policy with complex conditions",
            organization=self.organization,
            response_time=30,  # 30 minutes for urgent
            resolution_time=120,  # 2 hours for urgent
            conditions=[
                {"field": "priority", "operator": "in", "value": ["urgent", "high"]},
                {"field": "status", "operator": "not_equals", "value": "closed"},
                {"field": "subject", "operator": "contains", "value": "Complex"}
            ],
            is_active=True
        )
        
        # Should match the complex conditions
        policy = self.sla_manager.get_applicable_policy(ticket)
        self.assertEqual(policy, sla_policy)
    
    def test_sla_breach_at_exact_time(self):
        """Test SLA breach at exact deadline time"""
        sla_policy = SLAPolicy.objects.create(
            name="Exact Time Policy",
            description="Policy for exact time testing",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            conditions=[{"field": "priority", "operator": "equals", "value": "high"}],
            is_active=True
        )
        
        # Create ticket exactly at the deadline
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Exact Time Ticket",
            description="This ticket is at exact deadline",
            priority="high",
            status="open",
            created_at=timezone.now() - timedelta(minutes=60)  # Exactly at deadline
        )
        
        is_breached, details = self.sla_manager.check_breach(ticket)
        
        # Should not be breached at exact time (within tolerance)
        self.assertFalse(is_breached)
        self.assertEqual(details["reason"], "SLA not breached")
    
    def test_sla_breach_just_past_deadline(self):
        """Test SLA breach just past deadline"""
        sla_policy = SLAPolicy.objects.create(
            name="Just Past Policy",
            description="Policy for just past deadline testing",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            conditions=[{"field": "priority", "operator": "equals", "value": "high"}],
            is_active=True
        )
        
        # Create ticket just past the deadline
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Just Past Ticket",
            description="This ticket is just past deadline",
            priority="high",
            status="open",
            created_at=timezone.now() - timedelta(minutes=61)  # Just past deadline
        )
        
        is_breached, details = self.sla_manager.check_breach(ticket)
        
        # Should be breached just past deadline
        self.assertTrue(is_breached)
        self.assertEqual(details["reason"], "SLA deadline exceeded")


class TestSLAIntegration(TestCase):
    """Test suite for SLA integration scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            organization=self.organization
        )
        self.sla_manager = SLAManager(organization_id=self.organization.id)
    
    def test_sla_workflow_integration(self):
        """Test complete SLA workflow integration"""
        # Create SLA policy
        sla_policy = SLAPolicy.objects.create(
            name="Workflow Policy",
            description="Policy for workflow testing",
            organization=self.organization,
            response_time=60,
            resolution_time=240,
            conditions=[{"field": "priority", "operator": "equals", "value": "high"}],
            is_active=True
        )
        
        # Create ticket
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Workflow Ticket",
            description="This ticket tests the complete workflow",
            priority="high",
            status="open"
        )
        
        # Test complete workflow
        # 1. Get applicable policy
        policy = self.sla_manager.get_applicable_policy(ticket)
        self.assertEqual(policy, sla_policy)
        
        # 2. Calculate due date
        due_date = self.sla_manager.calculate_due_date(ticket, policy)
        self.assertIsInstance(due_date, datetime)
        
        # 3. Check breach status
        is_breached, details = self.sla_manager.check_breach(ticket)
        self.assertFalse(is_breached)
        
        # 4. Get SLA status
        status_info = self.sla_manager.get_sla_status(ticket)
        self.assertFalse(status_info["is_breached"])
        self.assertEqual(status_info["status"], "Within SLA")
    
    def test_sla_multi_tenant_isolation(self):
        """Test SLA multi-tenant isolation"""
        # Create another organization
        other_org = Organization.objects.create(
            name="Other Organization",
            slug="other-org"
        )
        
        # Create SLA policy for other organization
        other_policy = SLAPolicy.objects.create(
            name="Other Policy",
            description="Policy for other organization",
            organization=other_org,
            response_time=120,
            resolution_time=480,
            conditions=[{"field": "priority", "operator": "equals", "value": "high"}],
            is_active=True
        )
        
        # Create ticket for our organization
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Isolation Ticket",
            description="This ticket tests multi-tenant isolation",
            priority="high",
            status="open"
        )
        
        # Should not get the other organization's policy
        with self.assertRaises(SLAPolicyNotFound):
            self.sla_manager.get_applicable_policy(ticket)
    
    def test_sla_global_policy_fallback(self):
        """Test global SLA policy fallback"""
        # Create global policy
        global_policy = SLAPolicy.objects.create(
            name="Global Fallback Policy",
            description="Global policy for fallback testing",
            response_time=180,
            resolution_time=720,
            is_global=True,
            is_active=True,
            conditions=[]
        )
        
        # Create ticket
        ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Fallback Ticket",
            description="This ticket tests global policy fallback",
            priority="low",
            status="open"
        )
        
        # Should get the global policy as fallback
        policy = self.sla_manager.get_applicable_policy(ticket)
        self.assertEqual(policy, global_policy)
        self.assertTrue(policy.is_global)
    
    def test_sla_performance_under_load(self):
        """Test SLA performance under load"""
        # Create multiple policies
        for i in range(10):
            SLAPolicy.objects.create(
                name=f"Policy {i}",
                description=f"Policy {i} description",
                organization=self.organization,
                response_time=60 + i * 10,
                resolution_time=240 + i * 20,
                conditions=[{"field": "priority", "operator": "equals", "value": "high"}],
                is_active=True
            )
        
        # Create multiple tickets
        tickets = []
        for i in range(100):
            ticket = Ticket.objects.create(
                organization=self.organization,
                customer=self.user,
                subject=f"Load Test Ticket {i}",
                description=f"This ticket {i} tests performance under load",
                priority="high",
                status="open"
            )
            tickets.append(ticket)
        
        # Test performance
        start_time = timezone.now()
        
        for ticket in tickets:
            policy = self.sla_manager.get_applicable_policy(ticket)
            due_date = self.sla_manager.calculate_due_date(ticket, policy)
            is_breached, details = self.sla_manager.check_breach(ticket)
            status_info = self.sla_manager.get_sla_status(ticket)
        
        end_time = timezone.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should process 100 tickets in reasonable time (less than 5 seconds)
        self.assertLess(processing_time, 5.0)
