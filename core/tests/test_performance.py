"""
Comprehensive performance tests for all functionalities.
"""
import time
import asyncio
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.db import connection
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from unittest.mock import patch, Mock, MagicMock
import concurrent.futures
import threading

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket, TicketComment
from apps.field_service.models import WorkOrder, Technician
from apps.knowledge_base.models import KBArticle
from apps.automation.models import AutomationRule, SLAPolicy
from apps.analytics.models import AnalyticsDashboard, Report
from apps.integrations.models import Webhook, IntegrationLog
from apps.notifications.models import Notification
from apps.api.models import APIService
from apps.features.models import Feature, FeatureUsage

from .test_utils import (
    TestDataFactory, TestClientFactory, TestAssertions, 
    TestMocks, TestPerformance, TestSecurity, TestIntegration
)

User = get_user_model()


class DatabasePerformanceTest(TestCase):
    """Test database performance and query optimization."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.users = []
        self.tickets = []
        self.work_orders = []
        
        # Create test data
        for i in range(100):
            user = TestDataFactory.create_user(
                self.organization, 
                f"user{i}@example.com", 
                "customer"
            )
            self.users.append(user)
            
            ticket = TestDataFactory.create_ticket(
                self.organization, 
                user, 
                f"Ticket {i}"
            )
            self.tickets.append(ticket)
            
            work_order = TestDataFactory.create_work_order(
                self.organization, 
                user, 
                f"Work Order {i}"
            )
            self.work_orders.append(work_order)
    
    def test_ticket_list_performance(self):
        """Test ticket list query performance."""
        start_time = time.time()
        
        # Test with select_related for foreign keys
        tickets = Ticket.objects.select_related(
            'customer', 'assigned_agent', 'organization'
        ).filter(organization=self.organization)
        
        ticket_list = list(tickets)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        TestPerformance.assert_response_time(None, max_time=0.5)
        self.assertLess(execution_time, 0.5)
        self.assertEqual(len(ticket_list), 100)
        
        # Test query count
        with self.assertNumQueries(1):
            tickets = Ticket.objects.select_related(
                'customer', 'assigned_agent', 'organization'
            ).filter(organization=self.organization)
            list(tickets)
    
    def test_ticket_search_performance(self):
        """Test ticket search performance."""
        start_time = time.time()
        
        # Test full-text search
        tickets = Ticket.objects.filter(
            organization=self.organization,
            subject__icontains='Ticket'
        ).select_related('customer', 'assigned_agent')
        
        ticket_list = list(tickets)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.3)
        self.assertEqual(len(ticket_list), 100)
    
    def test_ticket_comment_performance(self):
        """Test ticket comment performance."""
        # Create comments for tickets
        for ticket in self.tickets[:50]:
            for i in range(5):
                TicketComment.objects.create(
                    organization=self.organization,
                    ticket=ticket,
                    user=self.users[0],
                    content=f"Comment {i} for ticket {ticket.id}",
                    is_public=True
                )
        
        start_time = time.time()
        
        # Test comment query with prefetch_related
        tickets = Ticket.objects.prefetch_related('comments').filter(
            organization=self.organization
        )
        
        ticket_list = list(tickets)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.8)
        self.assertEqual(len(ticket_list), 100)
        
        # Test query count
        with self.assertNumQueries(2):  # 1 for tickets, 1 for comments
            tickets = Ticket.objects.prefetch_related('comments').filter(
                organization=self.organization
            )
            list(tickets)
    
    def test_work_order_optimization_performance(self):
        """Test work order optimization performance."""
        start_time = time.time()
        
        # Test work order query with location data
        work_orders = WorkOrder.objects.filter(
            organization=self.organization,
            status='scheduled'
        ).select_related('customer', 'assigned_technician')
        
        work_order_list = list(work_orders)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.4)
        self.assertEqual(len(work_order_list), 100)
    
    def test_analytics_query_performance(self):
        """Test analytics query performance."""
        start_time = time.time()
        
        # Test analytics aggregation
        from django.db.models import Count, Avg, Sum
        from django.db.models.functions import TruncDate
        
        ticket_metrics = Ticket.objects.filter(
            organization=self.organization
        ).aggregate(
            total_tickets=Count('id'),
            avg_resolution_time=Avg('resolution_time'),
            total_comments=Sum('comments__count')
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.2)
        self.assertIn('total_tickets', ticket_metrics)
        self.assertIn('avg_resolution_time', ticket_metrics)
    
    def test_bulk_operations_performance(self):
        """Test bulk operations performance."""
        start_time = time.time()
        
        # Test bulk ticket creation
        tickets_to_create = []
        for i in range(50):
            ticket = Ticket(
                organization=self.organization,
                customer=self.users[0],
                subject=f"Bulk Ticket {i}",
                description=f"Bulk ticket description {i}",
                status='open',
                priority='medium',
                channel='web'
            )
            tickets_to_create.append(ticket)
        
        Ticket.objects.bulk_create(tickets_to_create)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 1.0)
        
        # Verify tickets were created
        ticket_count = Ticket.objects.filter(
            organization=self.organization,
            subject__startswith='Bulk Ticket'
        ).count()
        self.assertEqual(ticket_count, 50)
    
    def test_database_connection_pooling(self):
        """Test database connection pooling."""
        start_time = time.time()
        
        # Test concurrent database operations
        def db_operation():
            tickets = Ticket.objects.filter(organization=self.organization)
            return list(tickets)
        
        # Run concurrent operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(db_operation) for _ in range(20)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 2.0)
        self.assertEqual(len(results), 20)
        
        # Verify all operations succeeded
        for result in results:
            self.assertGreater(len(result), 0)


class APIPerformanceTest(APITestCase):
    """Test API performance and response times."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.client = TestClientFactory.create_authenticated_client(self.user)
        
        # Create test data
        for i in range(50):
            customer = TestDataFactory.create_user(
                self.organization, 
                f"customer{i}@example.com", 
                "customer"
            )
            TestDataFactory.create_ticket(self.organization, customer, f"Ticket {i}")
    
    def test_ticket_list_api_performance(self):
        """Test ticket list API performance."""
        start_time = time.time()
        
        url = reverse('api:ticket-list')
        response = self.client.get(url)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        TestAssertions.assert_response_success(response)
        self.assertLess(execution_time, 1.0)
        
        # Verify response data
        tickets = response.data['results']
        self.assertGreater(len(tickets), 0)
    
    def test_ticket_search_api_performance(self):
        """Test ticket search API performance."""
        start_time = time.time()
        
        url = reverse('api:ticket-list')
        response = self.client.get(url, {'search': 'Ticket'})
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        TestAssertions.assert_response_success(response)
        self.assertLess(execution_time, 0.8)
        
        # Verify search results
        tickets = response.data['results']
        self.assertGreater(len(tickets), 0)
    
    def test_ticket_filter_api_performance(self):
        """Test ticket filter API performance."""
        start_time = time.time()
        
        url = reverse('api:ticket-list')
        response = self.client.get(url, {
            'status': 'open',
            'priority': 'high',
            'created_after': (timezone.now() - timedelta(days=7)).isoformat()
        })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        TestAssertions.assert_response_success(response)
        self.assertLess(execution_time, 0.6)
        
        # Verify filter results
        tickets = response.data['results']
        self.assertIsInstance(tickets, list)
    
    def test_ticket_create_api_performance(self):
        """Test ticket create API performance."""
        start_time = time.time()
        
        url = reverse('api:ticket-list')
        data = {
            'subject': 'Performance Test Ticket',
            'description': 'Testing ticket creation performance',
            'priority': 'medium',
            'channel': 'web',
            'customer': self.user.id
        }
        
        response = self.client.post(url, data, format='json')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        TestAssertions.assert_response_success(response, status.HTTP_201_CREATED)
        self.assertLess(execution_time, 0.5)
        
        # Verify ticket was created
        TestAssertions.assert_ticket_created(data, self.organization)
    
    def test_ticket_bulk_operations_performance(self):
        """Test ticket bulk operations performance."""
        start_time = time.time()
        
        # Create multiple tickets for bulk operations
        ticket_ids = []
        for i in range(10):
            customer = TestDataFactory.create_user(
                self.organization, 
                f"bulk_customer{i}@example.com", 
                "customer"
            )
            ticket = TestDataFactory.create_ticket(
                self.organization, 
                customer, 
                f"Bulk Ticket {i}"
            )
            ticket_ids.append(ticket.id)
        
        # Test bulk update
        url = reverse('api:ticket-bulk-update')
        data = {
            'ticket_ids': ticket_ids,
            'updates': {
                'status': 'in_progress',
                'priority': 'high'
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        TestAssertions.assert_response_success(response)
        self.assertLess(execution_time, 1.0)
        
        # Verify bulk update
        updated_tickets = Ticket.objects.filter(id__in=ticket_ids)
        for ticket in updated_tickets:
            self.assertEqual(ticket.status, 'in_progress')
            self.assertEqual(ticket.priority, 'high')
    
    def test_concurrent_api_requests(self):
        """Test concurrent API requests performance."""
        start_time = time.time()
        
        def make_request():
            url = reverse('api:ticket-list')
            response = self.client.get(url)
            return response.status_code == 200
        
        # Run concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 3.0)
        self.assertEqual(len(results), 20)
        
        # Verify all requests succeeded
        self.assertTrue(all(results))
    
    def test_api_response_size(self):
        """Test API response size optimization."""
        # Test ticket list with field selection
        url = reverse('api:ticket-list')
        response = self.client.get(url, {'fields': 'id,subject,status,priority'})
        
        TestAssertions.assert_response_success(response)
        
        # Verify response size
        response_size = len(response.content)
        self.assertLess(response_size, 50000)  # Less than 50KB
        
        # Verify field selection
        tickets = response.data['results']
        if tickets:
            ticket = tickets[0]
            self.assertIn('id', ticket)
            self.assertIn('subject', ticket)
            self.assertIn('status', ticket)
            self.assertIn('priority', ticket)
            self.assertNotIn('description', ticket)


class CachePerformanceTest(TestCase):
    """Test cache performance and optimization."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        
        # Clear cache
        cache.clear()
    
    def test_cache_set_performance(self):
        """Test cache set performance."""
        start_time = time.time()
        
        # Test cache set operations
        for i in range(100):
            cache.set(f'test_key_{i}', f'test_value_{i}', 300)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.5)
    
    def test_cache_get_performance(self):
        """Test cache get performance."""
        # Set cache values
        for i in range(100):
            cache.set(f'test_key_{i}', f'test_value_{i}', 300)
        
        start_time = time.time()
        
        # Test cache get operations
        for i in range(100):
            value = cache.get(f'test_key_{i}')
            self.assertEqual(value, f'test_value_{i}')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.3)
    
    def test_cache_miss_performance(self):
        """Test cache miss performance."""
        start_time = time.time()
        
        # Test cache miss operations
        for i in range(100):
            value = cache.get(f'nonexistent_key_{i}')
            self.assertIsNone(value)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.2)
    
    def test_cache_invalidation_performance(self):
        """Test cache invalidation performance."""
        # Set cache values
        for i in range(100):
            cache.set(f'test_key_{i}', f'test_value_{i}', 300)
        
        start_time = time.time()
        
        # Test cache invalidation
        for i in range(100):
            cache.delete(f'test_key_{i}')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.4)
        
        # Verify cache was cleared
        for i in range(100):
            value = cache.get(f'test_key_{i}')
            self.assertIsNone(value)
    
    def test_cache_pattern_performance(self):
        """Test cache pattern performance."""
        start_time = time.time()
        
        # Test cache pattern operations
        cache.set('user:1:profile', {'name': 'John', 'email': 'john@example.com'}, 300)
        cache.set('user:1:permissions', ['read', 'write'], 300)
        cache.set('user:1:settings', {'theme': 'dark', 'language': 'en'}, 300)
        
        # Test cache pattern retrieval
        profile = cache.get('user:1:profile')
        permissions = cache.get('user:1:permissions')
        settings = cache.get('user:1:settings')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.1)
        
        # Verify cache values
        self.assertEqual(profile['name'], 'John')
        self.assertEqual(permissions, ['read', 'write'])
        self.assertEqual(settings['theme'], 'dark')


class RealTimePerformanceTest(TestCase):
    """Test real-time performance and WebSocket optimization."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.ticket = TestDataFactory.create_ticket(self.organization, self.user)
    
    async def test_websocket_connection_performance(self):
        """Test WebSocket connection performance."""
        start_time = time.time()
        
        from apps.api.consumers import TicketConsumer
        
        communicator = WebsocketCommunicator(
            TicketConsumer,
            f"/ws/tickets/?org={self.organization.id}&user={self.user.id}"
        )
        
        connected, subprotocol = await communicator.connect()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertTrue(connected)
        self.assertLess(execution_time, 0.5)
        
        await communicator.disconnect()
    
    async def test_websocket_message_performance(self):
        """Test WebSocket message performance."""
        from apps.api.consumers import TicketConsumer
        
        communicator = WebsocketCommunicator(
            TicketConsumer,
            f"/ws/tickets/?org={self.organization.id}&user={self.user.id}"
        )
        
        await communicator.connect()
        
        start_time = time.time()
        
        # Test message sending
        for i in range(10):
            await communicator.send_json_to({
                'type': 'ticket_message',
                'ticket_id': self.ticket.id,
                'message': f'Test message {i}',
                'user_id': self.user.id
            })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.3)
        
        await communicator.disconnect()
    
    def test_realtime_update_performance(self):
        """Test real-time update performance."""
        from apps.api.real_time_integration import realtime_integration
        
        start_time = time.time()
        
        # Test real-time updates
        for i in range(50):
            realtime_integration.send_ticket_update(
                ticket_id=self.ticket.id,
                action='status_changed',
                data={'status': 'in_progress', 'timestamp': timezone.now().isoformat()},
                organization_id=self.organization.id,
                user_id=self.user.id
            )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 1.0)
    
    def test_concurrent_websocket_connections(self):
        """Test concurrent WebSocket connections."""
        start_time = time.time()
        
        async def create_connection():
            from apps.api.consumers import TicketConsumer
            
            communicator = WebsocketCommunicator(
                TicketConsumer,
                f"/ws/tickets/?org={self.organization.id}&user={self.user.id}"
            )
            
            connected, subprotocol = await communicator.connect()
            await communicator.disconnect()
            
            return connected
        
        # Run concurrent connections
        async def test_concurrent_connections():
            tasks = [create_connection() for _ in range(10)]
            results = await asyncio.gather(*tasks)
            return results
        
        results = asyncio.run(test_concurrent_connections())
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 2.0)
        self.assertEqual(len(results), 10)
        
        # Verify all connections succeeded
        self.assertTrue(all(results))


class LoadTest(TransactionTestCase):
    """Test system load and stress testing."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.client = TestClientFactory.create_authenticated_client(self.user)
    
    def test_high_volume_ticket_creation(self):
        """Test high volume ticket creation."""
        start_time = time.time()
        
        # Create high volume of tickets
        tickets_created = 0
        for i in range(1000):
            try:
                customer = TestDataFactory.create_user(
                    self.organization, 
                    f"load_customer{i}@example.com", 
                    "customer"
                )
                ticket = TestDataFactory.create_ticket(
                    self.organization, 
                    customer, 
                    f"Load Test Ticket {i}"
                )
                tickets_created += 1
            except Exception as e:
                logger.error(f"Error creating ticket {i}: {e}")
                break
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 30.0)  # Less than 30 seconds
        self.assertGreater(tickets_created, 500)  # At least 500 tickets created
        
        # Verify tickets were created
        ticket_count = Ticket.objects.filter(
            organization=self.organization,
            subject__startswith='Load Test Ticket'
        ).count()
        self.assertEqual(ticket_count, tickets_created)
    
    def test_concurrent_api_requests(self):
        """Test concurrent API requests."""
        start_time = time.time()
        
        def make_api_request():
            url = reverse('api:ticket-list')
            response = self.client.get(url)
            return response.status_code == 200
        
        # Run concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_api_request) for _ in range(100)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 10.0)  # Less than 10 seconds
        self.assertEqual(len(results), 100)
        
        # Verify success rate
        success_rate = sum(results) / len(results)
        self.assertGreater(success_rate, 0.95)  # At least 95% success rate
    
    def test_database_connection_stress(self):
        """Test database connection stress."""
        start_time = time.time()
        
        def db_stress_operation():
            # Perform database operations
            tickets = Ticket.objects.filter(organization=self.organization)
            ticket_count = tickets.count()
            
            # Create new ticket
            customer = TestDataFactory.create_user(
                self.organization, 
                f"stress_customer_{threading.current_thread().ident}@example.com", 
                "customer"
            )
            ticket = TestDataFactory.create_ticket(
                self.organization, 
                customer, 
                f"Stress Test Ticket {threading.current_thread().ident}"
            )
            
            return ticket_count + 1
        
        # Run concurrent database operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(db_stress_operation) for _ in range(50)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 15.0)  # Less than 15 seconds
        self.assertEqual(len(results), 50)
        
        # Verify all operations succeeded
        self.assertTrue(all(results))
    
    def test_memory_usage_optimization(self):
        """Test memory usage optimization."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        tickets = []
        for i in range(1000):
            customer = TestDataFactory.create_user(
                self.organization, 
                f"memory_customer{i}@example.com", 
                "customer"
            )
            ticket = TestDataFactory.create_ticket(
                self.organization, 
                customer, 
                f"Memory Test Ticket {i}"
            )
            tickets.append(ticket)
        
        # Test memory usage
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        # Verify memory usage
        self.assertLess(memory_increase, 100.0)  # Less than 100MB increase
        
        # Clean up
        del tickets
    
    def test_cache_memory_usage(self):
        """Test cache memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Test cache memory usage
        for i in range(10000):
            cache.set(f'load_test_key_{i}', f'load_test_value_{i}', 300)
        
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        # Verify memory usage
        self.assertLess(memory_increase, 50.0)  # Less than 50MB increase
        
        # Clean up
        cache.clear()
    
    def test_system_resilience(self):
        """Test system resilience under load."""
        start_time = time.time()
        
        def resilient_operation():
            try:
                # Perform operation that might fail
                customer = TestDataFactory.create_user(
                    self.organization, 
                    f"resilience_customer_{threading.current_thread().ident}@example.com", 
                    "customer"
                )
                ticket = TestDataFactory.create_ticket(
                    self.organization, 
                    customer, 
                    f"Resilience Test Ticket {threading.current_thread().ident}"
                )
                return True
            except Exception as e:
                logger.error(f"Resilience test error: {e}")
                return False
        
        # Run resilient operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(resilient_operation) for _ in range(100)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 20.0)  # Less than 20 seconds
        
        # Verify resilience
        success_rate = sum(results) / len(results)
        self.assertGreater(success_rate, 0.90)  # At least 90% success rate


class PerformanceMonitoringTest(TestCase):
    """Test performance monitoring and metrics."""
    
    def setUp(self):
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
    
    def test_query_performance_monitoring(self):
        """Test query performance monitoring."""
        from django.db import connection
        
        # Clear query log
        connection.queries_log.clear()
        
        # Perform database operations
        tickets = Ticket.objects.filter(organization=self.organization)
        ticket_list = list(tickets)
        
        # Check query performance
        queries = connection.queries
        self.assertGreater(len(queries), 0)
        
        # Check query execution time
        total_time = sum(float(query['time']) for query in queries)
        self.assertLess(total_time, 1.0)  # Less than 1 second total
        
        # Check individual query performance
        for query in queries:
            execution_time = float(query['time'])
            self.assertLess(execution_time, 0.5)  # Less than 0.5 seconds per query
    
    def test_api_performance_monitoring(self):
        """Test API performance monitoring."""
        client = TestClientFactory.create_authenticated_client(self.user)
        
        # Test API performance
        start_time = time.time()
        
        url = reverse('api:ticket-list')
        response = client.get(url)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        TestAssertions.assert_response_success(response)
        self.assertLess(execution_time, 1.0)
        
        # Check response headers for performance info
        self.assertIn('Content-Type', response)
        self.assertIn('application/json', response['Content-Type'])
    
    def test_cache_performance_monitoring(self):
        """Test cache performance monitoring."""
        # Test cache performance
        start_time = time.time()
        
        # Set cache values
        for i in range(100):
            cache.set(f'perf_test_key_{i}', f'perf_test_value_{i}', 300)
        
        # Get cache values
        for i in range(100):
            value = cache.get(f'perf_test_key_{i}')
            self.assertEqual(value, f'perf_test_value_{i}')
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance
        self.assertLess(execution_time, 0.5)
    
    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        tickets = []
        for i in range(100):
            customer = TestDataFactory.create_user(
                self.organization, 
                f"memory_monitor_customer{i}@example.com", 
                "customer"
            )
            ticket = TestDataFactory.create_ticket(
                self.organization, 
                customer, 
                f"Memory Monitor Ticket {i}"
            )
            tickets.append(ticket)
        
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        # Verify memory usage
        self.assertLess(memory_increase, 20.0)  # Less than 20MB increase
        
        # Clean up
        del tickets
    
    def test_system_metrics_collection(self):
        """Test system metrics collection."""
        from apps.analytics.services import MetricsService
        
        # Test metrics collection
        metrics = MetricsService.collect_system_metrics()
        
        # Verify metrics
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertIn('disk_usage', metrics)
        self.assertIn('database_connections', metrics)
        self.assertIn('cache_hit_rate', metrics)
        self.assertIn('response_times', metrics)
        
        # Verify metric values
        self.assertIsInstance(metrics['cpu_usage'], (int, float))
        self.assertIsInstance(metrics['memory_usage'], (int, float))
        self.assertIsInstance(metrics['disk_usage'], (int, float))
        self.assertIsInstance(metrics['database_connections'], int)
        self.assertIsInstance(metrics['cache_hit_rate'], (int, float))
        self.assertIsInstance(metrics['response_times'], dict)
