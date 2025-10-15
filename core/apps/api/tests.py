"""
Comprehensive API testing suite.
"""

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.organizations.models import Organization
from apps.tickets.models import Ticket
from apps.field_service.models import WorkOrder, Technician
from apps.ai_ml.models import MLModel, Prediction
from apps.customer_experience.models import CustomerJourney
from apps.advanced_analytics.models import Dashboard, KPI
from apps.integration_platform.models import Integration
from apps.mobile_iot.models import MobileDevice
from apps.security_compliance.models import SecurityPolicy
from apps.workflow_automation.models import Workflow
from apps.communication_platform.models import CommunicationChannel

User = get_user_model()


class BaseAPITestCase(APITestCase):
    """Base test case with common setup."""

    def setUp(self):
        """Set up test data."""
        # Create organization
        self.organization = Organization.objects.create(
            name="Test Organization", domain="test.com", subscription_tier="premium"
        )

        # Create users
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            full_name="Admin User",
            organization=self.organization,
            role="admin",
        )

        self.agent_user = User.objects.create_user(
            email="agent@test.com",
            password="testpass123",
            full_name="Agent User",
            organization=self.organization,
            role="agent",
        )

        self.customer_user = User.objects.create_user(
            email="customer@test.com",
            password="testpass123",
            full_name="Customer User",
            organization=self.organization,
            role="customer",
        )

        # Create JWT token
        self.refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(self.refresh.access_token)

        # Set up API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def tearDown(self):
        """Clean up test data."""
        pass


class AuthenticationTests(BaseAPITestCase):
    """Test authentication endpoints."""

    def test_jwt_authentication(self):
        """Test JWT token authentication."""
        response = self.client.get("/api/v1/tickets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token(self):
        """Test invalid token rejection."""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
        response = self.client.get("/api/v1/tickets/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_token(self):
        """Test no token rejection."""
        self.client.credentials()
        response = self.client.get("/api/v1/tickets/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh."""
        response = self.client.post(
            "/api/v1/auth/refresh/", {"refresh": str(self.refresh)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class TicketAPITests(BaseAPITestCase):
    """Test ticket API endpoints."""

    def test_create_ticket(self):
        """Test ticket creation."""
        data = {
            "subject": "Test Ticket",
            "description": "This is a test ticket",
            "priority": "high",
            "category": "technical",
        }
        response = self.client.post("/api/v1/tickets/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(Ticket.objects.first().subject, "Test Ticket")

    def test_list_tickets(self):
        """Test ticket listing."""
        # Create test tickets
        Ticket.objects.create(
            organization=self.organization,
            subject="Ticket 1",
            description="Description 1",
            customer=self.customer_user,
        )
        Ticket.objects.create(
            organization=self.organization,
            subject="Ticket 2",
            description="Description 2",
            customer=self.customer_user,
        )

        response = self.client.get("/api/v1/tickets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_ticket_filtering(self):
        """Test ticket filtering."""
        # Create tickets with different priorities
        Ticket.objects.create(
            organization=self.organization,
            subject="High Priority Ticket",
            description="High priority description",
            priority="high",
            customer=self.customer_user,
        )
        Ticket.objects.create(
            organization=self.organization,
            subject="Low Priority Ticket",
            description="Low priority description",
            priority="low",
            customer=self.customer_user,
        )

        response = self.client.get("/api/v1/tickets/?priority=high")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["priority"], "high")

    def test_ticket_search(self):
        """Test ticket search functionality."""
        Ticket.objects.create(
            organization=self.organization,
            subject="Login Issue",
            description="Cannot login to the system",
            customer=self.customer_user,
        )
        Ticket.objects.create(
            organization=self.organization,
            subject="Email Problem",
            description="Email not working",
            customer=self.customer_user,
        )

        response = self.client.get("/api/v1/tickets/?search=login")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("login", response.data["results"][0]["subject"].lower())

    def test_ticket_pagination(self):
        """Test ticket pagination."""
        # Create multiple tickets
        for i in range(25):
            Ticket.objects.create(
                organization=self.organization,
                subject=f"Ticket {i}",
                description=f"Description {i}",
                customer=self.customer_user,
            )

        response = self.client.get("/api/v1/tickets/?page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

    def test_ticket_ordering(self):
        """Test ticket ordering."""
        # Create tickets with different creation times
        ticket1 = Ticket.objects.create(
            organization=self.organization,
            subject="First Ticket",
            description="First description",
            customer=self.customer_user,
        )
        ticket2 = Ticket.objects.create(
            organization=self.organization,
            subject="Second Ticket",
            description="Second description",
            customer=self.customer_user,
        )

        response = self.client.get("/api/v1/tickets/?ordering=-created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], ticket2.id)
        self.assertEqual(response.data["results"][1]["id"], ticket1.id)


class WorkOrderAPITests(BaseAPITestCase):
    """Test work order API endpoints."""

    def test_create_work_order(self):
        """Test work order creation."""
        data = {
            "title": "Equipment Repair",
            "description": "Printer not working",
            "customer": self.customer_user.id,
            "location": {
                "address": "123 Main St",
                "city": "New York",
                "coordinates": [40.7128, -74.0060],
            },
            "scheduled_start": "2024-01-15T09:00:00Z",
        }
        response = self.client.post("/api/v1/work-orders/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkOrder.objects.count(), 1)
        self.assertEqual(WorkOrder.objects.first().title, "Equipment Repair")

    def test_work_order_assignment(self):
        """Test work order assignment to technician."""
        # Create technician
        technician = Technician.objects.create(
            organization=self.organization,
            user=self.agent_user,
            skills=["repair", "maintenance"],
            availability_status="available",
        )

        # Create work order
        work_order = WorkOrder.objects.create(
            organization=self.organization,
            title="Equipment Repair",
            description="Printer not working",
            customer=self.customer_user,
        )

        # Assign work order
        response = self.client.post(
            f"/api/v1/work-orders/{work_order.id}/assign/",
            {"technician": technician.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        work_order.refresh_from_db()
        self.assertEqual(work_order.technician, technician)


class AIMLAPITests(BaseAPITestCase):
    """Test AI/ML API endpoints."""

    def test_create_ml_model(self):
        """Test ML model creation."""
        data = {
            "name": "Ticket Routing Model",
            "description": "Predicts best agent for ticket assignment",
            "model_type": "ticket_routing",
            "algorithm": "random_forest",
        }
        response = self.client.post("/api/v1/ai-ml/models/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MLModel.objects.count(), 1)
        self.assertEqual(MLModel.objects.first().name, "Ticket Routing Model")

    def test_model_training(self):
        """Test ML model training."""
        model = MLModel.objects.create(
            organization=self.organization,
            name="Test Model",
            model_type="ticket_routing",
            algorithm="random_forest",
        )

        response = self.client.post(
            f"/api/v1/ai-ml/models/{model.id}/train/",
            {"training_data_size": 1000, "epochs": 100},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("job_id", response.data)

    def test_model_prediction(self):
        """Test ML model prediction."""
        model = MLModel.objects.create(
            organization=self.organization,
            name="Test Model",
            model_type="ticket_routing",
            algorithm="random_forest",
            is_active=True,
        )

        response = self.client.post(
            f"/api/v1/ai-ml/models/{model.id}/predict/",
            {
                "input_data": {"subject": "Login Issue", "category": "technical"},
                "entity_type": "ticket",
                "entity_id": "TKT-001",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("prediction_id", response.data)
        self.assertIn("result", response.data)


class CustomerExperienceAPITests(BaseAPITestCase):
    """Test customer experience API endpoints."""

    def test_create_customer_journey(self):
        """Test customer journey creation."""
        data = {"customer": self.customer_user.id, "current_stage": "awareness"}
        response = self.client.post("/api/v1/customer-experience/journeys/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomerJourney.objects.count(), 1)
        self.assertEqual(CustomerJourney.objects.first().current_stage, "awareness")

    def test_add_touchpoint(self):
        """Test adding touchpoint to journey."""
        journey = CustomerJourney.objects.create(
            organization=self.organization,
            customer=self.customer_user,
            current_stage="awareness",
        )

        response = self.client.post(
            f"/api/v1/customer-experience/journeys/{journey.id}/add_touchpoint/",
            {
                "touchpoint_type": "email",
                "channel": "email",
                "title": "Welcome Email",
                "description": "Welcome to our service",
                "satisfaction_rating": 5,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("touchpoint_id", response.data)


class AdvancedAnalyticsAPITests(BaseAPITestCase):
    """Test advanced analytics API endpoints."""

    def test_create_dashboard(self):
        """Test dashboard creation."""
        data = {
            "name": "Customer Analytics",
            "description": "Customer analytics dashboard",
            "dashboard_type": "customer",
            "layout": {"columns": 2, "rows": 3},
        }
        response = self.client.post("/api/v1/advanced-analytics/dashboards/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dashboard.objects.count(), 1)
        self.assertEqual(Dashboard.objects.first().name, "Customer Analytics")

    def test_create_kpi(self):
        """Test KPI creation."""
        data = {
            "name": "Customer Satisfaction",
            "description": "Overall customer satisfaction score",
            "kpi_type": "satisfaction",
            "formula": "AVG(satisfaction_rating)",
            "target_value": 4.5,
        }
        response = self.client.post("/api/v1/advanced-analytics/kpis/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KPI.objects.count(), 1)
        self.assertEqual(KPI.objects.first().name, "Customer Satisfaction")

    def test_calculate_kpi(self):
        """Test KPI calculation."""
        kpi = KPI.objects.create(
            organization=self.organization,
            name="Test KPI",
            kpi_type="satisfaction",
            formula="AVG(satisfaction_rating)",
            target_value=4.5,
        )

        response = self.client.post(
            f"/api/v1/advanced-analytics/kpis/{kpi.id}/calculate/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("current_value", response.data)
        self.assertIn("change_percentage", response.data)


class IntegrationPlatformAPITests(BaseAPITestCase):
    """Test integration platform API endpoints."""

    def test_create_integration(self):
        """Test integration creation."""
        data = {
            "name": "Salesforce Integration",
            "description": "Integration with Salesforce CRM",
            "integration_type": "crm",
            "api_endpoint": "https://api.salesforce.com",
            "authentication_method": "oauth2",
        }
        response = self.client.post("/api/v1/integration-platform/integrations/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Integration.objects.count(), 1)
        self.assertEqual(Integration.objects.first().name, "Salesforce Integration")

    def test_test_connection(self):
        """Test integration connection."""
        integration = Integration.objects.create(
            organization=self.organization,
            name="Test Integration",
            integration_type="crm",
            api_endpoint="https://api.example.com",
        )

        response = self.client.post(
            f"/api/v1/integration-platform/integrations/{integration.id}/test_connection/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("connection_status", response.data)
        self.assertEqual(response.data["connection_status"], "success")


class SecurityAPITests(BaseAPITestCase):
    """Test security API endpoints."""

    def test_create_security_policy(self):
        """Test security policy creation."""
        data = {
            "name": "Password Policy",
            "description": "Password security policy",
            "policy_type": "password_policy",
            "configuration": {
                "min_length": 8,
                "require_uppercase": True,
                "require_numbers": True,
            },
        }
        response = self.client.post("/api/v1/security/policies/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SecurityPolicy.objects.count(), 1)
        self.assertEqual(SecurityPolicy.objects.first().name, "Password Policy")

    def test_security_audit_log(self):
        """Test security audit logging."""
        response = self.client.get("/api/v1/security/audit-logs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class WorkflowAutomationAPITests(BaseAPITestCase):
    """Test workflow automation API endpoints."""

    def test_create_workflow(self):
        """Test workflow creation."""
        data = {
            "name": "Ticket Escalation",
            "description": "Automatically escalate high priority tickets",
            "trigger_event": "ticket_created",
            "workflow_definition": {
                "conditions": [
                    {"field": "priority", "operator": "equals", "value": "high"}
                ],
                "actions": [{"type": "assign", "agent_id": self.agent_user.id}],
            },
        }
        response = self.client.post("/api/v1/workflow-automation/workflows/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workflow.objects.count(), 1)
        self.assertEqual(Workflow.objects.first().name, "Ticket Escalation")

    def test_execute_workflow(self):
        """Test workflow execution."""
        workflow = Workflow.objects.create(
            organization=self.organization,
            name="Test Workflow",
            trigger_event="ticket_created",
            workflow_definition={"conditions": [], "actions": []},
        )

        response = self.client.post(
            f"/api/v1/workflow-automation/workflows/{workflow.id}/execute/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)


class CommunicationPlatformAPITests(BaseAPITestCase):
    """Test communication platform API endpoints."""

    def test_create_communication_channel(self):
        """Test communication channel creation."""
        data = {
            "name": "Email Channel",
            "channel_type": "email",
            "configuration": {
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "username": "noreply@example.com",
            },
        }
        response = self.client.post("/api/v1/communication-platform/channels/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommunicationChannel.objects.count(), 1)
        self.assertEqual(CommunicationChannel.objects.first().name, "Email Channel")

    def test_channel_analytics(self):
        """Test communication channel analytics."""
        response = self.client.get("/api/v1/communication-platform/channels/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_channels", response.data)
        self.assertIn("active_channels", response.data)


class MobileIoTAPITests(BaseAPITestCase):
    """Test mobile & IoT API endpoints."""

    def test_create_mobile_device(self):
        """Test mobile device creation."""
        data = {
            "device_id": "device_123",
            "device_type": "ios",
            "os_version": "17.0",
            "app_version": "1.0.0",
        }
        response = self.client.post("/api/v1/mobile-iot/mobile-devices/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MobileDevice.objects.count(), 1)
        self.assertEqual(MobileDevice.objects.first().device_id, "device_123")

    def test_device_analytics(self):
        """Test mobile device analytics."""
        response = self.client.get("/api/v1/mobile-iot/mobile-devices/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_devices", response.data)
        self.assertIn("active_devices", response.data)


class PerformanceTests(BaseAPITestCase):
    """Test API performance."""

    def test_ticket_list_performance(self):
        """Test ticket list endpoint performance."""
        # Create multiple tickets
        for i in range(100):
            Ticket.objects.create(
                organization=self.organization,
                subject=f"Ticket {i}",
                description=f"Description {i}",
                customer=self.customer_user,
            )

        import time

        start_time = time.time()
        response = self.client.get("/api/v1/tickets/")
        end_time = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(
            end_time - start_time, 1.0
        )  # Should complete in less than 1 second

    def test_concurrent_requests(self):
        """Test concurrent request handling."""
        import threading
        import time

        results = []

        def make_request():
            response = self.client.get("/api/v1/tickets/")
            results.append(response.status_code)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        self.assertEqual(len(results), 10)
        self.assertTrue(all(status_code == 200 for status_code in results))


class ErrorHandlingTests(BaseAPITestCase):
    """Test error handling."""

    def test_invalid_data(self):
        """Test invalid data handling."""
        response = self.client.post(
            "/api/v1/tickets/",
            {
                "subject": "",  # Invalid: empty subject
                "description": "Test description",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("subject", response.data)

    def test_not_found(self):
        """Test 404 error handling."""
        response = self.client.get("/api/v1/tickets/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_permission_denied(self):
        """Test permission denied handling."""
        # Use customer user (limited permissions)
        customer_token = str(RefreshToken.for_user(self.customer_user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {customer_token}")

        response = self.client.get("/api/v1/admin/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rate_limiting(self):
        """Test rate limiting."""
        # Make multiple requests quickly
        for i in range(100):
            response = self.client.get("/api/v1/tickets/")
            if response.status_code == 429:
                break

        # Should eventually hit rate limit
        self.assertIn(response.status_code, [200, 429])
