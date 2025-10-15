"""
Test cases for SLA Management System
Critical business logic that was previously untested
"""

import pytest
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock

from apps.tickets.sla import SLAManager, SLAPolicy, SLAPolicyNotFound
from apps.tickets.models import Ticket
from apps.organizations.models import Organization


class TestSLAManager(TestCase):
    """Test cases for SLA Manager functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Organization",
            domain="test.com"
        )
        
        self.sla_policy = SLAPolicy.objects.create(
            name="Standard SLA",
            description="Standard service level agreement",
            organization=self.organization,
            response_time=60,  # 1 hour
            resolution_time=480,  # 8 hours
            conditions=[
                {"field": "priority", "operator": "equals", "value": "high"}
            ],
            is_active=True
        )
        
        self.sla_manager = SLAManager(organization_id=self.organization.id)
    
    def test_calculate_due_date_high_priority(self):
        """Test SLA due date calculation for high priority tickets"""
        # Create a high priority ticket
        ticket = Ticket.objects.create(
            subject="Test Ticket",
            description="Test Description",
            priority="high",
            organization=self.organization
        )
        
        # Calculate due date
        due_date = self.sla_manager.calculate_due_date(ticket, self.sla_policy)
        
        # Verify due date is calculated correctly
        expected_due_date = ticket.created_at + timedelta(minutes=60)
        self.assertEqual(due_date, expected_due_date)
    
    def test_calculate_due_date_business_hours(self):
        """Test SLA calculation with business hours"""
        # Mock business hours (9 AM - 5 PM, Monday-Friday)
        with patch.object(self.sla_manager, '_get_business_hours') as mock_business_hours:
            mock_business_hours.return_value = {
                'monday': {'start': '09:00', 'end': '17:00'},
                'tuesday': {'start': '09:00', 'end': '17:00'},
                'wednesday': {'start': '09:00', 'end': '17:00'},
                'thursday': {'start': '09:00', 'end': '17:00'},
                'friday': {'start': '09:00', 'end': '17:00'},
                'saturday': None,
                'sunday': None
            }
            
            # Create ticket on Friday at 4 PM
            friday_4pm = timezone.now().replace(hour=16, minute=0, second=0, microsecond=0)
            ticket = Ticket.objects.create(
                subject="Test Ticket",
                description="Test Description",
                priority="high",
                organization=self.organization,
                created_at=friday_4pm
            )
            
            due_date = self.sla_manager.calculate_due_date(ticket, self.sla_policy)
            
            # Should be due on Monday at 5 PM (1 hour into business hours)
            expected_due_date = friday_4pm + timedelta(days=3, hours=1)
            self.assertEqual(due_date, expected_due_date)
    
    def test_get_applicable_policy(self):
        """Test getting applicable SLA policy"""
        ticket = Ticket.objects.create(
            subject="Test Ticket",
            description="Test Description",
            priority="high",
            organization=self.organization
        )
        
        policy = self.sla_manager.get_applicable_policy(ticket)
        
        self.assertIsNotNone(policy)
        self.assertEqual(policy.name, "Standard SLA")
    
    def test_get_applicable_policy_no_match(self):
        """Test when no SLA policy matches"""
        ticket = Ticket.objects.create(
            subject="Test Ticket",
            description="Test Description",
            priority="low",  # Doesn't match high priority condition
            organization=self.organization
        )
        
        with self.assertRaises(SLAPolicyNotFound):
            self.sla_manager.get_applicable_policy(ticket)
    
    def test_evaluate_conditions(self):
        """Test SLA condition evaluation"""
        ticket = Ticket.objects.create(
            subject="Test Ticket",
            description="Test Description",
            priority="high",
            organization=self.organization
        )
        
        conditions = [
            {"field": "priority", "operator": "equals", "value": "high"}
        ]
        
        result = self.sla_manager.evaluate_conditions(ticket, conditions)
        self.assertTrue(result)
        
        # Test with non-matching condition
        conditions = [
            {"field": "priority", "operator": "equals", "value": "low"}
        ]
        
        result = self.sla_manager.evaluate_conditions(ticket, conditions)
        self.assertFalse(result)
    
    def test_check_breach_no_breach(self):
        """Test SLA breach check when no breach occurs"""
        ticket = Ticket.objects.create(
            subject="Test Ticket",
            description="Test Description",
            priority="high",
            organization=self.organization
        )
        
        is_breached, details = self.sla_manager.check_breach(ticket)
        
        self.assertFalse(is_breached)
        self.assertEqual(details["reason"], "SLA not breached")
    
    def test_check_breach_breach_occurred(self):
        """Test SLA breach check when breach occurs"""
        # Create ticket 2 hours ago (beyond 1 hour SLA)
        two_hours_ago = timezone.now() - timedelta(hours=2)
        
        ticket = Ticket.objects.create(
            subject="Test Ticket",
            description="Test Description",
            priority="high",
            organization=self.organization,
            created_at=two_hours_ago
        )
        
        is_breached, details = self.sla_manager.check_breach(ticket)
        
        self.assertTrue(is_breached)
        self.assertEqual(details["reason"], "SLA deadline exceeded")
        self.assertIn("overdue_minutes", details)
        self.assertGreater(details["overdue_minutes"], 0)
    
    def test_get_sla_status(self):
        """Test getting SLA status for a ticket"""
        ticket = Ticket.objects.create(
            subject="Test Ticket",
            description="Test Description",
            priority="high",
            organization=self.organization
        )
        
        status = self.sla_manager.get_sla_status(ticket)
        
        self.assertIn("policy_name", status)
        self.assertIn("due_date", status)
        self.assertIn("time_remaining", status)
        self.assertIn("is_breached", status)
        self.assertEqual(status["policy_name"], "Standard SLA")
    
    def test_sla_manager_without_organization(self):
        """Test SLA manager without organization context"""
        sla_manager = SLAManager()
        
        # Should still work but with global policies
        self.assertIsNotNone(sla_manager)
    
    def test_business_hours_calculation(self):
        """Test business hours calculation"""
        business_hours = self.sla_manager._get_business_hours()
        
        # Should return a dictionary with day configurations
        self.assertIsInstance(business_hours, dict)
        self.assertIn('monday', business_hours)
    
    def test_organization_timezone(self):
        """Test organization timezone retrieval"""
        timezone_str = self.sla_manager._get_organization_timezone()
        
        # Should return a valid timezone string
        self.assertIsInstance(timezone_str, str)
        self.assertEqual(timezone_str, "UTC")  # Default timezone


class TestSLAPolicy(TestCase):
    """Test cases for SLA Policy model"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Organization",
            domain="test.com"
        )
    
    def test_sla_policy_creation(self):
        """Test SLA policy creation"""
        policy = SLAPolicy.objects.create(
            name="Test Policy",
            description="Test Description",
            organization=self.organization,
            response_time=120,
            resolution_time=960,
            conditions=[
                {"field": "priority", "operator": "equals", "value": "medium"}
            ]
        )
        
        self.assertEqual(policy.name, "Test Policy")
        self.assertEqual(policy.response_time, 120)
        self.assertEqual(policy.resolution_time, 960)
        self.assertTrue(policy.is_active)
    
    def test_sla_policy_string_representation(self):
        """Test SLA policy string representation"""
        policy = SLAPolicy.objects.create(
            name="Test Policy",
            description="Test Description",
            organization=self.organization,
            response_time=60,
            resolution_time=480
        )
        
        expected_string = f"Test Policy ({self.organization.name})"
        self.assertEqual(str(policy), expected_string)
    
    def test_global_sla_policy(self):
        """Test global SLA policy (no organization)"""
        policy = SLAPolicy.objects.create(
            name="Global Policy",
            description="Global Description",
            organization=None,
            response_time=180,
            resolution_time=1440
        )
        
        self.assertIsNone(policy.organization)
        expected_string = "Global Policy (Global)"
        self.assertEqual(str(policy), expected_string)


class TestSLAIntegration(TestCase):
    """Integration tests for SLA system"""
    
    def setUp(self):
        """Set up test data"""
        self.organization = Organization.objects.create(
            name="Test Organization",
            domain="test.com"
        )
        
        # Create multiple SLA policies
        self.high_priority_policy = SLAPolicy.objects.create(
            name="High Priority SLA",
            organization=self.organization,
            response_time=30,  # 30 minutes
            resolution_time=240,  # 4 hours
            conditions=[
                {"field": "priority", "operator": "equals", "value": "high"}
            ]
        )
        
        self.medium_priority_policy = SLAPolicy.objects.create(
            name="Medium Priority SLA",
            organization=self.organization,
            response_time=120,  # 2 hours
            resolution_time=960,  # 16 hours
            conditions=[
                {"field": "priority", "operator": "equals", "value": "medium"}
            ]
        )
    
    def test_multiple_policies_priority_matching(self):
        """Test that correct policy is selected based on priority"""
        sla_manager = SLAManager(organization_id=self.organization.id)
        
        # Test high priority ticket
        high_priority_ticket = Ticket.objects.create(
            subject="High Priority Ticket",
            priority="high",
            organization=self.organization
        )
        
        high_policy = sla_manager.get_applicable_policy(high_priority_ticket)
        self.assertEqual(high_policy.name, "High Priority SLA")
        
        # Test medium priority ticket
        medium_priority_ticket = Ticket.objects.create(
            subject="Medium Priority Ticket",
            priority="medium",
            organization=self.organization
        )
        
        medium_policy = sla_manager.get_applicable_policy(medium_priority_ticket)
        self.assertEqual(medium_policy.name, "Medium Priority SLA")
    
    def test_sla_breach_escalation(self):
        """Test SLA breach escalation workflow"""
        # Create ticket that will breach SLA
        ticket = Ticket.objects.create(
            subject="Breach Test Ticket",
            priority="high",
            organization=self.organization,
            created_at=timezone.now() - timedelta(hours=1)  # 1 hour ago
        )
        
        sla_manager = SLAManager(organization_id=self.organization.id)
        is_breached, details = sla_manager.check_breach(ticket)
        
        self.assertTrue(is_breached)
        self.assertIn("overdue_minutes", details)
        self.assertGreater(details["overdue_minutes"], 0)
    
    def test_sla_status_tracking(self):
        """Test SLA status tracking over time"""
        ticket = Ticket.objects.create(
            subject="Status Test Ticket",
            priority="high",
            organization=self.organization
        )
        
        sla_manager = SLAManager(organization_id=self.organization.id)
        
        # Check initial status
        initial_status = sla_manager.get_sla_status(ticket)
        self.assertFalse(initial_status["is_breached"])
        self.assertGreater(initial_status["time_remaining"], 0)
        
        # Simulate time passing
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = timezone.now() + timedelta(hours=2)
            
            # Check status after time has passed
            updated_status = sla_manager.get_sla_status(ticket)
            self.assertTrue(updated_status["is_breached"])


if __name__ == '__main__':
    pytest.main([__file__])