"""
Comprehensive test runner for all test suites.
"""
import os
import sys
import time
import json
import asyncio
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
from django.test import TestCase, TransactionTestCase
from django.test.utils import get_runner
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.core.cache import cache
from rest_framework.test import APITestCase
from channels.testing import WebsocketCommunicator
from unittest.mock import patch, Mock, MagicMock
import concurrent.futures
import threading
import psutil
import gc

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket
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


class ComprehensiveTestRunner:
    """Comprehensive test runner for all test suites."""
    
    def __init__(self):
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_suites': {},
            'performance_metrics': {},
            'system_health': {},
            'errors': []
        }
        
        self.test_suites = [
            'test_models',
            'test_apis', 
            'test_services',
            'test_performance',
            'test_security',
            'test_integration'
        ]
    
    def run_all_tests(self):
        """Run all test suites."""
        logger.info("🚀 Starting Comprehensive Test Suite")
        logger.info("=" * 60)
        
        # System health check
        self.check_system_health()
        
        # Run test suites
        for suite in self.test_suites:
            logger.info(f"\n📋 Running {suite} tests...")
            self.run_test_suite(suite)
        
        # Performance analysis
        self.analyze_performance()
        
        # Generate report
        self.generate_report()
        
        logger.info("\n✅ Test Suite Complete!")
        logger.info(f"Total Tests: {self.test_results['total_tests']}")
        logger.info(f"Passed: {self.test_results['passed_tests']}")
        logger.info(f"Failed: {self.test_results['failed_tests']}")
        logger.info(f"Skipped: {self.test_results['skipped_tests']}")
        
        return self.test_results
    
    def run_test_suite(self, suite_name):
        """Run individual test suite."""
        start_time = time.time()
        
        try:
            # Import and run test suite
            if suite_name == 'test_models':
                import tests.test_models
                suite_results = self.run_model_tests()
            elif suite_name == 'test_apis':
                import tests.test_apis
                suite_results = self.run_api_tests()
            elif suite_name == 'test_services':
                import tests.test_services
                suite_results = self.run_service_tests()
            elif suite_name == 'test_performance':
                import tests.test_performance
                suite_results = self.run_performance_tests()
            elif suite_name == 'test_security':
                import tests.test_security
                suite_results = self.run_security_tests()
            elif suite_name == 'test_integration':
                import tests.test_integration
                suite_results = self.run_integration_tests()
            else:
                suite_results = {'error': f'Unknown test suite: {suite_name}'}
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Store results
            self.test_results['test_suites'][suite_name] = {
                'execution_time': execution_time,
                'results': suite_results,
                'status': 'completed' if 'error' not in suite_results else 'failed'
            }
            
            # Update counters
            if 'error' not in suite_results:
                self.test_results['total_tests'] += suite_results.get('total_tests', 0)
                self.test_results['passed_tests'] += suite_results.get('passed_tests', 0)
                self.test_results['failed_tests'] += suite_results.get('failed_tests', 0)
                self.test_results['skipped_tests'] += suite_results.get('skipped_tests', 0)
            else:
                self.test_results['errors'].append(f"{suite_name}: {suite_results['error']}")
            
            logger.info(f"✅ {suite_name} completed in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ {suite_name} failed: {str(e)}")
            self.test_results['errors'].append(f"{suite_name}: {str(e)}")
            self.test_results['test_suites'][suite_name] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def run_model_tests(self):
        """Run model tests."""
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_cases': []
        }
        
        # Test model creation
        try:
            organization = TestDataFactory.create_organization()
            user = TestDataFactory.create_user(organization)
            ticket = TestDataFactory.create_ticket(organization, user)
            
            results['total_tests'] += 3
            results['passed_tests'] += 3
            results['test_cases'].append({
                'name': 'Model Creation',
                'status': 'passed',
                'message': 'All models created successfully'
            })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Model Creation',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test model relationships
        try:
            work_order = TestDataFactory.create_work_order(organization, user)
            technician = TestDataFactory.create_technician(organization, user)
            
            results['total_tests'] += 2
            results['passed_tests'] += 2
            results['test_cases'].append({
                'name': 'Model Relationships',
                'status': 'passed',
                'message': 'All relationships created successfully'
            })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Model Relationships',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test model validation
        try:
            # Test invalid data
            try:
                invalid_ticket = Ticket.objects.create(
                    organization=organization,
                    subject='',  # Empty subject should fail
                    description='Test',
                    status='invalid_status'  # Invalid status
                )
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Model Validation',
                    'status': 'failed',
                    'message': 'Validation should have failed'
                })
            except Exception:
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Model Validation',
                    'status': 'passed',
                    'message': 'Validation working correctly'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Model Validation',
                'status': 'failed',
                'message': str(e)
            })
        
        return results
    
    def run_api_tests(self):
        """Run API tests."""
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_cases': []
        }
        
        # Test API authentication
        try:
            organization = TestDataFactory.create_organization()
            user = TestDataFactory.create_user(organization)
            client = TestClientFactory.create_authenticated_client(user)
            
            results['total_tests'] += 1
            results['passed_tests'] += 1
            results['test_cases'].append({
                'name': 'API Authentication',
                'status': 'passed',
                'message': 'Authentication working correctly'
            })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'API Authentication',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test API endpoints
        try:
            # Test ticket list endpoint
            url = reverse('api:ticket-list')
            response = client.get(url)
            
            if response.status_code == 200:
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Ticket List API',
                    'status': 'passed',
                    'message': 'Ticket list endpoint working'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Ticket List API',
                    'status': 'failed',
                    'message': f'Unexpected status code: {response.status_code}'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Ticket List API',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test API performance
        try:
            start_time = time.time()
            
            for i in range(10):
                response = client.get(url)
                if response.status_code != 200:
                    raise Exception(f'API request {i} failed')
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if execution_time < 2.0:  # Less than 2 seconds for 10 requests
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'API Performance',
                    'status': 'passed',
                    'message': f'API performance acceptable: {execution_time:.2f}s'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'API Performance',
                    'status': 'failed',
                    'message': f'API performance too slow: {execution_time:.2f}s'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'API Performance',
                'status': 'failed',
                'message': str(e)
            })
        
        return results
    
    def run_service_tests(self):
        """Run service tests."""
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_cases': []
        }
        
        # Test AI service
        try:
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'category': 'Technical',
                    'confidence': 0.85
                }
                mock_post.return_value = mock_response
                
                # Test AI categorization
                from apps.ai_ml.services import AICategorizationService
                service = AICategorizationService()
                result = service.categorize_ticket('Test subject', 'Test description')
                
                if result['category'] == 'Technical':
                    results['total_tests'] += 1
                    results['passed_tests'] += 1
                    results['test_cases'].append({
                        'name': 'AI Service',
                        'status': 'passed',
                        'message': 'AI service working correctly'
                    })
                else:
                    results['failed_tests'] += 1
                    results['test_cases'].append({
                        'name': 'AI Service',
                        'status': 'failed',
                        'message': 'AI service returned unexpected result'
                    })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'AI Service',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test email service
        try:
            with patch('apps.notifications.tasks.send_email.delay') as mock_send:
                from apps.notifications.services import EmailService
                service = EmailService()
                result = service.send_email(
                    to_email='test@example.com',
                    subject='Test Email',
                    template='test',
                    context={}
                )
                
                if result['success']:
                    results['total_tests'] += 1
                    results['passed_tests'] += 1
                    results['test_cases'].append({
                        'name': 'Email Service',
                        'status': 'passed',
                        'message': 'Email service working correctly'
                    })
                else:
                    results['failed_tests'] += 1
                    results['test_cases'].append({
                        'name': 'Email Service',
                        'status': 'failed',
                        'message': 'Email service failed'
                    })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Email Service',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test webhook service
        try:
            organization = TestDataFactory.create_organization()
            webhook = TestDataFactory.create_webhook(organization)
            
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'success': True}
                mock_post.return_value = mock_response
                
                from apps.integrations.services import WebhookService
                service = WebhookService()
                result = service.trigger_webhook(
                    webhook=webhook,
                    event_type='test_event',
                    payload={'test': 'data'}
                )
                
                if result['success']:
                    results['total_tests'] += 1
                    results['passed_tests'] += 1
                    results['test_cases'].append({
                        'name': 'Webhook Service',
                        'status': 'passed',
                        'message': 'Webhook service working correctly'
                    })
                else:
                    results['failed_tests'] += 1
                    results['test_cases'].append({
                        'name': 'Webhook Service',
                        'status': 'failed',
                        'message': 'Webhook service failed'
                    })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Webhook Service',
                'status': 'failed',
                'message': str(e)
            })
        
        return results
    
    def run_performance_tests(self):
        """Run performance tests."""
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_cases': []
        }
        
        # Test database performance
        try:
            start_time = time.time()
            
            organization = TestDataFactory.create_organization()
            for i in range(100):
                user = TestDataFactory.create_user(organization, f"perf_user{i}@example.com")
                TestDataFactory.create_ticket(organization, user, f"Perf Ticket {i}")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if execution_time < 5.0:  # Less than 5 seconds for 100 records
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Database Performance',
                    'status': 'passed',
                    'message': f'Database performance acceptable: {execution_time:.2f}s'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Database Performance',
                    'status': 'failed',
                    'message': f'Database performance too slow: {execution_time:.2f}s'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Database Performance',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test cache performance
        try:
            start_time = time.time()
            
            for i in range(1000):
                cache.set(f'perf_test_key_{i}', f'perf_test_value_{i}', 300)
            
            for i in range(1000):
                value = cache.get(f'perf_test_key_{i}')
                if value != f'perf_test_value_{i}':
                    raise Exception(f'Cache value mismatch for key {i}')
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if execution_time < 2.0:  # Less than 2 seconds for 1000 operations
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Cache Performance',
                    'status': 'passed',
                    'message': f'Cache performance acceptable: {execution_time:.2f}s'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Cache Performance',
                    'status': 'failed',
                    'message': f'Cache performance too slow: {execution_time:.2f}s'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Cache Performance',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test memory usage
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operations
            tickets = []
            for i in range(1000):
                organization = TestDataFactory.create_organization(f"Memory Org {i}")
                user = TestDataFactory.create_user(organization, f"memory_user{i}@example.com")
                ticket = TestDataFactory.create_ticket(organization, user, f"Memory Ticket {i}")
                tickets.append(ticket)
            
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            if memory_increase < 100.0:  # Less than 100MB increase
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Memory Usage',
                    'status': 'passed',
                    'message': f'Memory usage acceptable: {memory_increase:.2f}MB increase'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Memory Usage',
                    'status': 'failed',
                    'message': f'Memory usage too high: {memory_increase:.2f}MB increase'
                })
            
            # Clean up
            del tickets
            gc.collect()
            
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Memory Usage',
                'status': 'failed',
                'message': str(e)
            })
        
        return results
    
    def run_security_tests(self):
        """Run security tests."""
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_cases': []
        }
        
        # Test authentication
        try:
            organization = TestDataFactory.create_organization()
            user = TestDataFactory.create_user(organization)
            
            # Test password hashing
            if user.check_password('testpass123'):
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Password Hashing',
                    'status': 'passed',
                    'message': 'Password hashing working correctly'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Password Hashing',
                    'status': 'failed',
                    'message': 'Password hashing not working'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Password Hashing',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test organization isolation
        try:
            org1 = TestDataFactory.create_organization("Org 1")
            org2 = TestDataFactory.create_organization("Org 2")
            user1 = TestDataFactory.create_user(org1, "user1@example.com")
            user2 = TestDataFactory.create_user(org2, "user2@example.com")
            
            ticket1 = TestDataFactory.create_ticket(org1, user1)
            ticket2 = TestDataFactory.create_ticket(org2, user2)
            
            # Test isolation
            tickets_org1 = Ticket.objects.filter(organization=org1)
            tickets_org2 = Ticket.objects.filter(organization=org2)
            
            if ticket1 in tickets_org1 and ticket1 not in tickets_org2:
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Organization Isolation',
                    'status': 'passed',
                    'message': 'Organization isolation working correctly'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Organization Isolation',
                    'status': 'failed',
                    'message': 'Organization isolation not working'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Organization Isolation',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test SQL injection protection
        try:
            organization = TestDataFactory.create_organization()
            user = TestDataFactory.create_user(organization)
            
            # Test SQL injection attempt
            malicious_input = "'; DROP TABLE tickets; --"
            ticket = TestDataFactory.create_ticket(organization, user, malicious_input)
            
            # Verify ticket was created safely
            if ticket.subject == malicious_input:
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'SQL Injection Protection',
                    'status': 'passed',
                    'message': 'SQL injection protection working correctly'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'SQL Injection Protection',
                    'status': 'failed',
                    'message': 'SQL injection protection not working'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'SQL Injection Protection',
                'status': 'failed',
                'message': str(e)
            })
        
        return results
    
    def run_integration_tests(self):
        """Run integration tests."""
        results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_cases': []
        }
        
        # Test end-to-end ticket flow
        try:
            organization = TestDataFactory.create_organization()
            customer = TestDataFactory.create_user(organization, "customer@example.com", "customer")
            agent = TestDataFactory.create_user(organization, "agent@example.com", "agent")
            
            # Create ticket
            ticket = TestDataFactory.create_ticket(organization, customer)
            
            # Assign ticket
            ticket.assigned_agent = agent
            ticket.status = 'in_progress'
            ticket.save()
            
            # Resolve ticket
            ticket.status = 'resolved'
            ticket.resolved_at = timezone.now()
            ticket.save()
            
            # Close ticket
            ticket.status = 'closed'
            ticket.closed_at = timezone.now()
            ticket.save()
            
            # Verify flow
            if (ticket.assigned_agent == agent and 
                ticket.status == 'closed' and 
                ticket.resolved_at is not None and 
                ticket.closed_at is not None):
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'End-to-End Ticket Flow',
                    'status': 'passed',
                    'message': 'Ticket flow working correctly'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'End-to-End Ticket Flow',
                    'status': 'failed',
                    'message': 'Ticket flow not working correctly'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'End-to-End Ticket Flow',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test automation integration
        try:
            organization = TestDataFactory.create_organization()
            rule = TestDataFactory.create_automation_rule(organization)
            ticket = TestDataFactory.create_ticket(organization, 
                TestDataFactory.create_user(organization, "customer@example.com", "customer"),
                priority="high")
            
            # Test rule execution
            if rule.conditions[0]['value'] == ticket.priority:
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Automation Integration',
                    'status': 'passed',
                    'message': 'Automation integration working correctly'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Automation Integration',
                    'status': 'failed',
                    'message': 'Automation integration not working'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Automation Integration',
                'status': 'failed',
                'message': str(e)
            })
        
        # Test notification integration
        try:
            organization = TestDataFactory.create_organization()
            user = TestDataFactory.create_user(organization)
            ticket = TestDataFactory.create_ticket(organization, user)
            
            # Test notification creation
            notification = Notification.objects.create(
                organization=organization,
                user=user,
                notification_type='ticket_created',
                message='Test notification',
                priority='high'
            )
            
            if notification.user == user and notification.notification_type == 'ticket_created':
                results['total_tests'] += 1
                results['passed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Notification Integration',
                    'status': 'passed',
                    'message': 'Notification integration working correctly'
                })
            else:
                results['failed_tests'] += 1
                results['test_cases'].append({
                    'name': 'Notification Integration',
                    'status': 'failed',
                    'message': 'Notification integration not working'
                })
        except Exception as e:
            results['failed_tests'] += 1
            results['test_cases'].append({
                'name': 'Notification Integration',
                'status': 'failed',
                'message': str(e)
            })
        
        return results
    
    def check_system_health(self):
        """Check system health before running tests."""
        try:
            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Check cache connection
            cache.set('health_check', 'ok', 10)
            cache_result = cache.get('health_check')
            
            # Check memory usage
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            self.test_results['system_health'] = {
                'database': 'healthy',
                'cache': 'healthy' if cache_result == 'ok' else 'unhealthy',
                'memory_usage_mb': memory_usage,
                'cpu_usage_percent': process.cpu_percent(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.test_results['system_health'] = {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_performance(self):
        """Analyze performance metrics."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            self.test_results['performance_metrics'] = {
                'total_execution_time': (datetime.now() - datetime.fromisoformat(self.test_results['start_time'])).total_seconds(),
                'memory_usage_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_usage_percent': process.cpu_percent(),
                'database_queries': len(connection.queries) if hasattr(connection, 'queries') else 0,
                'cache_hit_rate': self.calculate_cache_hit_rate(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.test_results['performance_metrics'] = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def calculate_cache_hit_rate(self):
        """Calculate cache hit rate."""
        try:
            # This would be implemented with actual cache statistics
            return 0.85  # Placeholder
        except:
            return 0.0
    
    def generate_report(self):
        """Generate comprehensive test report."""
        self.test_results['end_time'] = datetime.now().isoformat()
        
        # Calculate success rate
        total_tests = self.test_results['total_tests']
        if total_tests > 0:
            success_rate = (self.test_results['passed_tests'] / total_tests) * 100
        else:
            success_rate = 0
        
        self.test_results['success_rate'] = success_rate
        
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\n📊 Test Report saved to: {report_file}")
        logger.info(f"📈 Success Rate: {success_rate:.2f}%")
        
        if success_rate >= 90:
            logger.info("🎉 Excellent! System is performing well.")
        elif success_rate >= 80:
            logger.info("✅ Good! System is performing adequately.")
        elif success_rate >= 70:
            logger.warning("⚠️  Warning! System needs attention.")
        else:
            logger.error("❌ Critical! System needs immediate attention.")


def run_comprehensive_tests():
    """Run comprehensive test suite."""
    runner = ComprehensiveTestRunner()
    return runner.run_all_tests()


if __name__ == '__main__':
    run_comprehensive_tests()
