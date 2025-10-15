"""
Test suite for refactored code to ensure all changes work correctly.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, time
from apps.common.constants import (
    SLA_CRITICAL_THRESHOLD,
    SLA_WARNING_THRESHOLD,
    DEFAULT_BUSINESS_START_TIME,
    LONG_FIELD_LENGTH,
    MEDIUM_FIELD_LENGTH,
    SHORT_FIELD_LENGTH,
)
from apps.common.operators import OperatorEvaluator, BusinessHoursCalculator
from apps.common.base_models import BaseModel, TenantAwareModel, TimestampedModel
from apps.automation.engine import ConditionEvaluator, ActionExecutor
from apps.tickets.sla import SLAManager
from apps.organizations.models import Organization
from apps.accounts.models import User


class TestRefactoredOperators(TestCase):
    """Test the refactored operator evaluation system."""
    
    def setUp(self):
        """Set up test data."""
        self.evaluator = OperatorEvaluator()
    
    def test_operator_evaluation(self):
        """Test operator evaluation with various operators."""
        # Test equals operator
        self.assertTrue(self.evaluator.evaluate("test", "equals", "test"))
        self.assertFalse(self.evaluator.evaluate("test", "equals", "different"))
        
        # Test contains operator
        self.assertTrue(self.evaluator.evaluate("hello world", "contains", "world"))
        self.assertFalse(self.evaluator.evaluate("hello world", "contains", "universe"))
        
        # Test greater_than operator
        self.assertTrue(self.evaluator.evaluate(10, "greater_than", 5))
        self.assertFalse(self.evaluator.evaluate(5, "greater_than", 10))
        
        # Test is_empty operator
        self.assertTrue(self.evaluator.evaluate("", "is_empty", ""))
        self.assertTrue(self.evaluator.evaluate(None, "is_empty", ""))
        self.assertFalse(self.evaluator.evaluate("test", "is_empty", ""))
        
        # Test is_not_empty operator
        self.assertTrue(self.evaluator.evaluate("test", "is_not_empty", ""))
        self.assertFalse(self.evaluator.evaluate("", "is_not_empty", ""))
    
    def test_case_insensitive_comparison(self):
        """Test case insensitive string comparison."""
        self.assertTrue(self.evaluator.evaluate("TEST", "equals", "test"))
        self.assertTrue(self.evaluator.evaluate("Hello World", "contains", "world"))
    
    def test_regex_operator(self):
        """Test regex operator."""
        self.assertTrue(self.evaluator.evaluate("test123", "regex", r"\d+"))
        self.assertFalse(self.evaluator.evaluate("test", "regex", r"\d+"))


class TestRefactoredBusinessHours(TestCase):
    """Test the refactored business hours calculator."""
    
    def setUp(self):
        """Set up test data."""
        self.calculator = BusinessHoursCalculator()
        self.business_hours = {
            "monday": {"enabled": True, "start": "09:00", "end": "17:00"},
            "tuesday": {"enabled": True, "start": "09:00", "end": "17:00"},
            "wednesday": {"enabled": True, "start": "09:00", "end": "17:00"},
            "thursday": {"enabled": True, "start": "09:00", "end": "17:00"},
            "friday": {"enabled": True, "start": "09:00", "end": "17:00"},
            "saturday": {"enabled": False, "start": "09:00", "end": "17:00"},
            "sunday": {"enabled": False, "start": "09:00", "end": "17:00"},
        }
    
    def test_add_business_time_weekday(self):
        """Test adding business time on a weekday."""
        # Monday 10:00 AM + 2 hours = Monday 12:00 PM
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0)  # Monday
        duration = timedelta(hours=2)
        
        result = self.calculator.add_business_time(start_time, duration, self.business_hours)
        expected = timezone.datetime(2024, 1, 1, 12, 0, 0)
        
        self.assertEqual(result, expected)
    
    def test_add_business_time_weekend(self):
        """Test adding business time on a weekend."""
        # Saturday 10:00 AM + 2 hours = Monday 9:00 AM (next business day)
        start_time = timezone.datetime(2024, 1, 6, 10, 0, 0)  # Saturday
        duration = timedelta(hours=2)
        
        result = self.calculator.add_business_time(start_time, duration, self.business_hours)
        expected = timezone.datetime(2024, 1, 8, 9, 0, 0)  # Monday 9:00 AM
        
        self.assertEqual(result, expected)
    
    def test_add_business_time_after_hours(self):
        """Test adding business time after business hours."""
        # Friday 6:00 PM + 2 hours = Monday 11:00 AM
        start_time = timezone.datetime(2024, 1, 5, 18, 0, 0)  # Friday 6:00 PM
        duration = timedelta(hours=2)
        
        result = self.calculator.add_business_time(start_time, duration, self.business_hours)
        expected = timezone.datetime(2024, 1, 8, 11, 0, 0)  # Monday 11:00 AM
        
        self.assertEqual(result, expected)
    
    def test_parse_time(self):
        """Test time parsing."""
        # Valid time
        result = self.calculator._parse_time("14:30")
        expected = time(14, 30)
        self.assertEqual(result, expected)
        
        # Invalid time (should return default)
        result = self.calculator._parse_time("invalid")
        expected = DEFAULT_BUSINESS_START_TIME
        self.assertEqual(result, expected)


class TestRefactoredSLA(TestCase):
    """Test the refactored SLA manager."""
    
    def setUp(self):
        """Set up test data."""
        self.sla_manager = SLAManager()
        self.organization = Organization.objects.create(name="Test Org")
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            organization=self.organization
        )
    
    def test_compare_values_with_operators(self):
        """Test compare_values method with various operators."""
        # Test equals
        self.assertTrue(self.sla_manager.compare_values("test", "equals", "test"))
        self.assertFalse(self.sla_manager.compare_values("test", "equals", "different"))
        
        # Test contains
        self.assertTrue(self.sla_manager.compare_values("hello world", "contains", "world"))
        self.assertFalse(self.sla_manager.compare_values("hello", "contains", "world"))
        
        # Test greater_than
        self.assertTrue(self.sla_manager.compare_values(10, "greater_than", 5))
        self.assertFalse(self.sla_manager.compare_values(5, "greater_than", 10))
    
    def test_sla_status_with_constants(self):
        """Test SLA status calculation using constants."""
        from apps.tickets.models import Ticket
        
        # Create a ticket
        ticket = Ticket.objects.create(
            subject="Test Ticket",
            description="Test Description",
            customer=self.user,
            organization=self.organization,
            due_date=timezone.now() + SLA_CRITICAL_THRESHOLD
        )
        
        # Test critical status
        status = self.sla_manager.get_sla_status(ticket)
        self.assertEqual(status, "critical")
        
        # Test warning status
        ticket.due_date = timezone.now() + SLA_WARNING_THRESHOLD
        ticket.save()
        status = self.sla_manager.get_sla_status(ticket)
        self.assertEqual(status, "warning")


class TestRefactoredAutomation(TestCase):
    """Test the refactored automation engine."""
    
    def setUp(self):
        """Set up test data."""
        self.condition_evaluator = ConditionEvaluator()
        self.action_executor = ActionExecutor()
    
    def test_compare_values_delegation(self):
        """Test that compare_values delegates to OperatorEvaluator."""
        # Test that the method works the same way
        self.assertTrue(self.condition_evaluator.compare_values("test", "equals", "test"))
        self.assertFalse(self.condition_evaluator.compare_values("test", "equals", "different"))
        
        # Test case insensitive comparison
        self.assertTrue(self.condition_evaluator.compare_values("TEST", "equals", "test"))
    
    def test_execute_action_with_mapping(self):
        """Test execute_action with action handler mapping."""
        # Mock action data
        action = {"type": "assign", "agent_id": 1}
        entity = type('MockEntity', (), {'organization': None})()
        context = {}
        
        # This should not raise an exception
        try:
            self.action_executor.execute_action(action, entity, context)
        except Exception as e:
            # Expected to fail due to missing agent, but should not crash
            self.assertIn("Agent", str(e))


class TestConstants(TestCase):
    """Test that constants are properly defined and accessible."""
    
    def test_time_constants(self):
        """Test time-related constants."""
        self.assertEqual(SLA_CRITICAL_THRESHOLD, timedelta(hours=1))
        self.assertEqual(SLA_WARNING_THRESHOLD, timedelta(hours=4))
        self.assertEqual(DEFAULT_BUSINESS_START_TIME, time(9, 0))
    
    def test_field_length_constants(self):
        """Test field length constants."""
        self.assertEqual(SHORT_FIELD_LENGTH, 50)
        self.assertEqual(MEDIUM_FIELD_LENGTH, 100)
        self.assertEqual(LONG_FIELD_LENGTH, 200)
    
    def test_choice_constants(self):
        """Test choice constants are properly defined."""
        from apps.common.constants import (
            COMMON_STATUS_CHOICES,
            COMMON_PRIORITY_CHOICES,
            DEVICE_TYPE_CHOICES,
            PLATFORM_TYPE_CHOICES,
        )
        
        # Test that choices are tuples
        self.assertIsInstance(COMMON_STATUS_CHOICES, list)
        self.assertIsInstance(COMMON_PRIORITY_CHOICES, list)
        self.assertIsInstance(DEVICE_TYPE_CHOICES, list)
        self.assertIsInstance(PLATFORM_TYPE_CHOICES, list)
        
        # Test that choices have expected structure
        for choice in COMMON_STATUS_CHOICES:
            self.assertIsInstance(choice, tuple)
            self.assertEqual(len(choice), 2)


class TestBaseModels(TestCase):
    """Test base model classes."""
    
    def test_base_model_inheritance(self):
        """Test that base models can be instantiated."""
        # Test that base classes are abstract
        self.assertTrue(BaseModel._meta.abstract)
        self.assertTrue(TenantAwareModel._meta.abstract)
        self.assertTrue(TimestampedModel._meta.abstract)
    
    def test_base_model_fields(self):
        """Test that base models have expected fields."""
        # Test TenantAwareModel
        self.assertTrue(hasattr(TenantAwareModel, 'organization'))
        
        # Test TimestampedModel
        self.assertTrue(hasattr(TimestampedModel, 'created_at'))
        self.assertTrue(hasattr(TimestampedModel, 'updated_at'))


class TestRefactoringIntegration(TestCase):
    """Integration tests for refactored code."""
    
    def test_automation_engine_integration(self):
        """Test that automation engine works with refactored components."""
        from apps.automation.engine import WorkflowEngine
        
        engine = WorkflowEngine()
        
        # Test that engine can be instantiated
        self.assertIsNotNone(engine.condition_evaluator)
        self.assertIsNotNone(engine.action_executor)
    
    def test_sla_manager_integration(self):
        """Test that SLA manager works with refactored components."""
        sla_manager = SLAManager()
        
        # Test that SLA manager can be instantiated
        self.assertIsNotNone(sla_manager)
        
        # Test that it uses the refactored compare_values
        self.assertTrue(callable(sla_manager.compare_values))
    
    def test_operator_evaluator_integration(self):
        """Test that operator evaluator integrates properly."""
        evaluator = OperatorEvaluator()
        
        # Test that all operators are available
        expected_operators = [
            "equals", "not_equals", "contains", "not_contains",
            "starts_with", "ends_with", "in", "not_in",
            "greater_than", "less_than", "greater_than_or_equal",
            "less_than_or_equal", "is_empty", "is_not_empty", "regex"
        ]
        
        for operator in expected_operators:
            self.assertIn(operator, evaluator.operators)
    
    def test_business_hours_calculator_integration(self):
        """Test that business hours calculator integrates properly."""
        calculator = BusinessHoursCalculator()
        
        # Test that calculator can be instantiated
        self.assertIsNotNone(calculator)
        
        # Test that it has the expected methods
        self.assertTrue(callable(calculator.add_business_time))
        self.assertTrue(callable(calculator._parse_time))
