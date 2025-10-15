"""
Enhanced test utilities for improved test quality and reduced duplication.
"""

import json
import time
import uuid
import logging
from datetime import datetime, timedelta
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
logger = logging.getLogger(__name__)


class TestIsolationMixin:
    """Mixin for proper test isolation and cleanup."""
    
    def setUp(self):
        super().setUp()
        self._cleanup_data()
    
    def tearDown(self):
        self._cleanup_data()
        super().tearDown()
    
    def _cleanup_data(self):
        """Clean up all test data to prevent isolation issues."""
        try:
            # Clean up in reverse dependency order
            TicketAttachment.objects.all().delete()
            TicketComment.objects.all().delete()
            Ticket.objects.all().delete()
            WorkOrder.objects.all().delete()
            Technician.objects.all().delete()
            JobAssignment.objects.all().delete()
            ServiceReport.objects.all().delete()
            Asset.objects.all().delete()
            InventoryItem.objects.all().delete()
            Route.objects.all().delete()
            KBArticle.objects.all().delete()
            KBCategory.objects.all().delete()
            KBFeedback.objects.all().delete()
            AutomationRule.objects.all().delete()
            SLAPolicy.objects.all().delete()
            EmailTemplate.objects.all().delete()
            AnalyticsDashboard.objects.all().delete()
            Report.objects.all().delete()
            Metric.objects.all().delete()
            Webhook.objects.all().delete()
            IntegrationLog.objects.all().delete()
            Notification.objects.all().delete()
            APIService.objects.all().delete()
            Feature.objects.all().delete()
            FeatureCategory.objects.all().delete()
            FeatureConnection.objects.all().delete()
            FeatureUsage.objects.all().delete()
            FeatureHealth.objects.all().delete()
            SecurityPolicy.objects.all().delete()
            AuditLog.objects.all().delete()
            Language.objects.all().delete()
            Translation.objects.all().delete()
            CustomField.objects.all().delete()
            CustomFieldValue.objects.all().delete()
            Theme.objects.all().delete()
            CompliancePolicy.objects.all().delete()
            ComplianceCheck.objects.all().delete()
            User.objects.all().delete()
            Organization.objects.all().delete()
        except Exception as e:
            logger.warning(f"Error during test cleanup: {e}")


class TestAsyncMixin:
    """Mixin for proper async test handling."""
    
    def setUp(self):
        super().setUp()
        self._setup_async_environment()
    
    def tearDown(self):
        self._cleanup_async_environment()
        super().tearDown()
    
    def _setup_async_environment(self):
        """Setup async test environment."""
        # Setup async test environment if needed
        pass
    
    def _cleanup_async_environment(self):
        """Cleanup async test environment."""
        # Cleanup async test environment if needed
        pass
    
    async def run_async_test(self, test_func, *args, **kwargs):
        """Run async test with proper error handling."""
        try:
            return await test_func(*args, **kwargs)
        except Exception as e:
            self.fail(f"Async test failed: {e}")


class TestMockMixin:
    """Mixin for proper mock management."""
    
    def setUp(self):
        super().setUp()
        self._setup_mocks()
    
    def tearDown(self):
        self._cleanup_mocks()
        super().tearDown()
    
    def _setup_mocks(self):
        """Setup mocks for test."""
        self.mocks = {}
    
    def _cleanup_mocks(self):
        """Cleanup mocks after test."""
        for mock_name, mock_obj in self.mocks.items():
            if hasattr(mock_obj, 'reset_mock'):
                mock_obj.reset_mock()
        self.mocks.clear()
    
    def create_mock(self, name, **kwargs):
        """Create a mock with proper configuration."""
        mock_obj = Mock(**kwargs)
        self.mocks[name] = mock_obj
        return mock_obj


class TestDataFactory:
    """Enhanced factory for creating test data with proper isolation."""
    
    @staticmethod
    def create_organization(name: str = "Test Organization", 
                          subscription_tier: str = "enterprise") -> Organization:
        """Create test organization with proper isolation."""
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
        """Create test user with proper isolation."""
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
        """Create test ticket with proper isolation."""
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
        """Create test work order with proper isolation."""
        return WorkOrder.objects.create(
            organization=organization,
            customer=customer,
            title=title,
            description="Test work order description",
            status=status,
            priority="medium",
            scheduled_date=timezone.now() + timedelta(days=1)
        )


class TestAssertions:
    """Enhanced assertions for better test quality."""
    
    @staticmethod
    def assert_response_success(response, expected_status=status.HTTP_200_OK):
        """Assert response is successful with proper error messages."""
        if response.status_code != expected_status:
            raise AssertionError(
                f"Expected status {expected_status}, got {response.status_code}. "
                f"Response: {response.content.decode()}"
            )
    
    @staticmethod
    def assert_response_error(response, expected_status=status.HTTP_400_BAD_REQUEST):
        """Assert response is an error with proper error messages."""
        if response.status_code != expected_status:
            raise AssertionError(
                f"Expected error status {expected_status}, got {response.status_code}. "
                f"Response: {response.content.decode()}"
            )
    
    @staticmethod
    def assert_model_created(model_class, **filters):
        """Assert model instance was created with proper error messages."""
        if not model_class.objects.filter(**filters).exists():
            raise AssertionError(
                f"Expected {model_class.__name__} instance with filters {filters} to exist"
            )
    
    @staticmethod
    def assert_model_not_created(model_class, **filters):
        """Assert model instance was not created with proper error messages."""
        if model_class.objects.filter(**filters).exists():
            raise AssertionError(
                f"Expected {model_class.__name__} instance with filters {filters} to not exist"
            )


class TestPerformanceMixin:
    """Mixin for performance testing utilities."""
    
    def assert_performance_within_limits(self, func, max_time_seconds=1.0, *args, **kwargs):
        """Assert function executes within time limits."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        if execution_time > max_time_seconds:
            self.fail(f"Function took {execution_time:.2f}s, expected < {max_time_seconds}s")
        
        return result


class TestSecurityMixin:
    """Mixin for security testing utilities."""
    
    def assert_no_sql_injection(self, endpoint, payloads):
        """Assert endpoint is protected against SQL injection."""
        for payload in payloads:
            response = self.client.post(endpoint, {'input': payload})
            # Should not execute SQL injection
            self.assertNotIn('error', response.content.decode().lower())
    
    def assert_no_xss_vulnerability(self, endpoint, payloads):
        """Assert endpoint is protected against XSS."""
        for payload in payloads:
            response = self.client.post(endpoint, {'input': payload})
            # Should sanitize XSS payloads
            self.assertNotIn('<script>', response.content.decode())
            self.assertNotIn('javascript:', response.content.decode())


class TestIntegrationMixin:
    """Mixin for integration testing utilities."""
    
    def assert_external_service_available(self, service_url, timeout=5):
        """Assert external service is available."""
        import requests
        try:
            response = requests.get(service_url, timeout=timeout)
            if response.status_code not in [200, 201]:
                self.fail(f"External service {service_url} returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.fail(f"External service {service_url} is not available: {e}")
    
    def assert_api_endpoint_accessible(self, endpoint, expected_status=200):
        """Assert API endpoint is accessible."""
        response = self.client.get(endpoint)
        if response.status_code != expected_status:
            self.fail(f"API endpoint {endpoint} returned status {response.status_code}")


class TestDataCleanupMixin:
    """Mixin for comprehensive test data cleanup."""
    
    def setUp(self):
        super().setUp()
        self._setup_cleanup_tracking()
    
    def tearDown(self):
        self._cleanup_all_test_data()
        super().tearDown()
    
    def _setup_cleanup_tracking(self):
        """Setup tracking for test data cleanup."""
        self.created_objects = []
    
    def _track_created_object(self, obj):
        """Track created object for cleanup."""
        self.created_objects.append(obj)
    
    def _cleanup_all_test_data(self):
        """Cleanup all tracked test data."""
        for obj in reversed(self.created_objects):
            try:
                if hasattr(obj, 'delete'):
                    obj.delete()
            except Exception as e:
                logger.warning(f"Error cleaning up object {obj}: {e}")
        self.created_objects.clear()


class TestErrorHandlingMixin:
    """Mixin for proper error handling in tests."""
    
    def assert_no_unhandled_exceptions(self, func, *args, **kwargs):
        """Assert function doesn't raise unhandled exceptions."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.fail(f"Function raised unhandled exception: {e}")
    
    def assert_graceful_error_handling(self, func, *args, **kwargs):
        """Assert function handles errors gracefully."""
        try:
            result = func(*args, **kwargs)
            # Function should return a result or handle error gracefully
            return result
        except Exception as e:
            # If exception is raised, it should be a known, expected exception
            if not isinstance(e, (ValueError, TypeError, AttributeError)):
                self.fail(f"Function raised unexpected exception: {e}")


class TestQualityMixin:
    """Mixin for test quality improvements."""
    
    def setUp(self):
        super().setUp()
        self._setup_test_quality_checks()
    
    def tearDown(self):
        self._cleanup_test_quality_checks()
        super().tearDown()
    
    def _setup_test_quality_checks(self):
        """Setup test quality checks."""
        self.test_start_time = time.time()
        self.test_errors = []
    
    def _cleanup_test_quality_checks(self):
        """Cleanup test quality checks."""
        test_duration = time.time() - self.test_start_time
        if test_duration > 5.0:  # 5 seconds
            logger.warning(f"Test {self._testMethodName} took {test_duration:.2f}s")
        
        if self.test_errors:
            logger.warning(f"Test {self._testMethodName} had {len(self.test_errors)} errors")
    
    def add_test_error(self, error):
        """Add test error for quality tracking."""
        self.test_errors.append(error)
    
    def assert_test_quality_metrics(self, max_duration=5.0, max_errors=0):
        """Assert test quality metrics."""
        test_duration = time.time() - self.test_start_time
        if test_duration > max_duration:
            self.fail(f"Test took {test_duration:.2f}s, expected < {max_duration}s")
        
        if len(self.test_errors) > max_errors:
            self.fail(f"Test had {len(self.test_errors)} errors, expected < {max_errors}")


# Enhanced test base classes
class EnhancedTestCase(TestIsolationMixin, TestMockMixin, TestDataCleanupMixin, TestErrorHandlingMixin, TestQualityMixin, TestCase):
    """Enhanced TestCase with all quality improvements."""
    pass


class EnhancedTransactionTestCase(TestIsolationMixin, TestMockMixin, TestDataCleanupMixin, TestErrorHandlingMixin, TestQualityMixin, TransactionTestCase):
    """Enhanced TransactionTestCase with all quality improvements."""
    pass


class EnhancedAPITestCase(TestIsolationMixin, TestMockMixin, TestDataCleanupMixin, TestErrorHandlingMixin, TestQualityMixin, APITestCase):
    """Enhanced APITestCase with all quality improvements."""
    pass


class EnhancedAsyncTestCase(TestIsolationMixin, TestAsyncMixin, TestMockMixin, TestDataCleanupMixin, TestErrorHandlingMixin, TestQualityMixin, TestCase):
    """Enhanced TestCase with async support and all quality improvements."""
    pass


# Export all utilities
__all__ = [
    'TestIsolationMixin',
    'TestAsyncMixin', 
    'TestMockMixin',
    'TestDataFactory',
    'TestAssertions',
    'TestPerformanceMixin',
    'TestSecurityMixin',
    'TestIntegrationMixin',
    'TestDataCleanupMixin',
    'TestErrorHandlingMixin',
    'TestQualityMixin',
    'EnhancedTestCase',
    'EnhancedTransactionTestCase',
    'EnhancedAPITestCase',
    'EnhancedAsyncTestCase'
]
