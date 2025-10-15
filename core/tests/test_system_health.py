"""
Comprehensive System Health Tests
Tests critical system health checking logic including service health, database health, and system status.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from decimal import Decimal

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.monitoring.models import SystemMetric, Alert, HealthCheck, MonitoringConfiguration
from apps.monitoring.services import SystemMetricsCollector, AlertManager, HealthChecker, MonitoringService
from apps.api.system_checker import SystemChecker
from apps.tickets.models import Ticket
from apps.field_service.models import WorkOrder, Technician

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class SystemHealthTest(EnhancedTransactionTestCase):
    """Test System Health with comprehensive health checking coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.health_checker = HealthChecker()
        self.system_checker = SystemChecker()
    
    def test_comprehensive_health_check_success(self):
        """Test successful comprehensive health check."""
        with patch.object(self.health_checker, 'check_health') as mock_health:
            mock_health.return_value = {
                'overall_status': 'healthy',
                'services': [
                    {'name': 'database', 'status': 'healthy', 'response_time': 50},
                    {'name': 'redis', 'status': 'healthy', 'response_time': 10},
                    {'name': 'api', 'status': 'healthy', 'response_time': 100}
                ]
            }
            
            with patch.object(self.system_checker, 'check_all_services') as mock_services:
                mock_services.return_value = {
                    'overall_status': 'healthy',
                    'services': [
                        {'name': 'database', 'status': 'healthy'},
                        {'name': 'redis', 'status': 'healthy'},
                        {'name': 'api', 'status': 'healthy'}
                    ]
                }
                
                result = self._comprehensive_health_check()
                
                self.assertEqual(result['overall_status'], 'healthy')
                self.assertIn('health_checker_status', result)
                self.assertIn('system_checker_status', result)
    
    def test_comprehensive_health_check_degraded(self):
        """Test comprehensive health check with degraded status."""
        with patch.object(self.health_checker, 'check_health') as mock_health:
            mock_health.return_value = {
                'overall_status': 'degraded',
                'services': [
                    {'name': 'database', 'status': 'healthy', 'response_time': 50},
                    {'name': 'redis', 'status': 'unhealthy', 'error': 'Connection failed'},
                    {'name': 'api', 'status': 'healthy', 'response_time': 100}
                ]
            }
            
            with patch.object(self.system_checker, 'check_all_services') as mock_services:
                mock_services.return_value = {
                    'overall_status': 'degraded',
                    'services': [
                        {'name': 'database', 'status': 'healthy'},
                        {'name': 'redis', 'status': 'unhealthy'},
                        {'name': 'api', 'status': 'healthy'}
                    ]
                }
                
                result = self._comprehensive_health_check()
                
                self.assertEqual(result['overall_status'], 'degraded')
                self.assertIn('degraded_services', result)
    
    def test_comprehensive_health_check_unhealthy(self):
        """Test comprehensive health check with unhealthy status."""
        with patch.object(self.health_checker, 'check_health') as mock_health:
            mock_health.return_value = {
                'overall_status': 'unhealthy',
                'services': [
                    {'name': 'database', 'status': 'unhealthy', 'error': 'Database unavailable'},
                    {'name': 'redis', 'status': 'unhealthy', 'error': 'Redis unavailable'},
                    {'name': 'api', 'status': 'unhealthy', 'error': 'API unavailable'}
                ]
            }
            
            with patch.object(self.system_checker, 'check_all_services') as mock_services:
                mock_services.return_value = {
                    'overall_status': 'unhealthy',
                    'services': [
                        {'name': 'database', 'status': 'unhealthy'},
                        {'name': 'redis', 'status': 'unhealthy'},
                        {'name': 'api', 'status': 'unhealthy'}
                    ]
                }
                
                result = self._comprehensive_health_check()
                
                self.assertEqual(result['overall_status'], 'unhealthy')
                self.assertIn('critical_services_down', result)
    
    def test_database_health_check_success(self):
        """Test successful database health check."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.05]  # 50ms response time
                
                result = self._check_database_health()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 50)
                self.assertIn('connection_test', result)
                self.assertTrue(result['connection_test'])
    
    def test_database_health_check_failure(self):
        """Test database health check with failure."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.side_effect = Exception("Database connection failed")
            
            result = self._check_database_health()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('Database connection failed', result['error'])
            self.assertFalse(result['connection_test'])
    
    def test_redis_health_check_success(self):
        """Test successful Redis health check."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.return_value = True
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.01]  # 10ms response time
                
                result = self._check_redis_health()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 10)
                self.assertIn('ping_test', result)
                self.assertTrue(result['ping_test'])
    
    def test_redis_health_check_failure(self):
        """Test Redis health check with failure."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis connection failed")
            
            result = self._check_redis_health()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('Redis connection failed', result['error'])
            self.assertFalse(result['ping_test'])
    
    def test_api_health_check_success(self):
        """Test successful API health check."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'status': 'healthy'}
            mock_get.return_value = mock_response
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.1]  # 100ms response time
                
                result = self._check_api_health()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 100)
                self.assertIn('endpoint_test', result)
                self.assertTrue(result['endpoint_test'])
    
    def test_api_health_check_failure(self):
        """Test API health check with failure."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API connection failed")
            
            result = self._check_api_health()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('API connection failed', result['error'])
            self.assertFalse(result['endpoint_test'])
    
    def test_system_metrics_health_check_success(self):
        """Test successful system metrics health check."""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 45.5
            
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value = Mock(percent=60.2, total=8192*1024*1024)
                
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value = Mock(percent=75.8, total=1000*1024*1024*1024)
                    
                    result = self._check_system_metrics_health()
                    
                    self.assertEqual(result['status'], 'healthy')
                    self.assertIn('cpu_usage', result)
                    self.assertIn('memory_usage', result)
                    self.assertIn('disk_usage', result)
                    self.assertEqual(result['cpu_usage'], 45.5)
                    self.assertEqual(result['memory_usage'], 60.2)
                    self.assertEqual(result['disk_usage'], 75.8)
    
    def test_system_metrics_health_check_high_usage(self):
        """Test system metrics health check with high usage."""
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 95.0  # High CPU usage
            
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value = Mock(percent=90.0, total=8192*1024*1024)
                
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value = Mock(percent=95.0, total=1000*1024*1024*1024)
                    
                    result = self._check_system_metrics_health()
                    
                    self.assertEqual(result['status'], 'warning')
                    self.assertIn('high_cpu_usage', result)
                    self.assertIn('high_memory_usage', result)
                    self.assertIn('high_disk_usage', result)
    
    def test_application_health_check_success(self):
        """Test successful application health check."""
        # Create test data
        Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Test Ticket",
            description="Test description"
        )
        
        result = self._check_application_health()
        
        self.assertEqual(result['status'], 'healthy')
        self.assertIn('tickets_count', result)
        self.assertIn('users_count', result)
        self.assertIn('organizations_count', result)
        self.assertEqual(result['tickets_count'], 1)
        self.assertEqual(result['users_count'], 1)
        self.assertEqual(result['organizations_count'], 1)
    
    def test_application_health_check_error(self):
        """Test application health check with error."""
        with patch('apps.tickets.models.Ticket.objects.count') as mock_count:
            mock_count.side_effect = Exception("Database error")
            
            result = self._check_application_health()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('Database error', result['error'])
    
    def test_network_health_check_success(self):
        """Test successful network health check."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.05]  # 50ms response time
                
                result = self._check_network_health()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 50)
                self.assertIn('connectivity_test', result)
                self.assertTrue(result['connectivity_test'])
    
    def test_network_health_check_failure(self):
        """Test network health check with failure."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network connection failed")
            
            result = self._check_network_health()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('Network connection failed', result['error'])
            self.assertFalse(result['connectivity_test'])
    
    def test_generate_health_report_success(self):
        """Test successful health report generation."""
        with patch.object(self, '_comprehensive_health_check') as mock_health:
            mock_health.return_value = {
                'overall_status': 'healthy',
                'health_checker_status': 'healthy',
                'system_checker_status': 'healthy'
            }
            
            result = self._generate_health_report()
            
            self.assertIn('report_id', result)
            self.assertIn('generated_at', result)
            self.assertIn('overall_status', result)
            self.assertIn('health_summary', result)
            self.assertEqual(result['overall_status'], 'healthy')
    
    def test_generate_health_report_error(self):
        """Test health report generation with error."""
        with patch.object(self, '_comprehensive_health_check') as mock_health:
            mock_health.side_effect = Exception("Health check failed")
            
            result = self._generate_health_report()
            
            self.assertIn('error', result)
            self.assertIn('Health check failed', result['error'])
    
    def _comprehensive_health_check(self):
        """Comprehensive health check combining multiple services."""
        try:
            health_checker_result = self.health_checker.check_health()
            system_checker_result = self.system_checker.check_all_services()
            
            # Determine overall status
            overall_status = 'healthy'
            if (health_checker_result['overall_status'] == 'unhealthy' or 
                system_checker_result['overall_status'] == 'unhealthy'):
                overall_status = 'unhealthy'
            elif (health_checker_result['overall_status'] == 'degraded' or 
                  system_checker_result['overall_status'] == 'degraded'):
                overall_status = 'degraded'
            
            return {
                'overall_status': overall_status,
                'health_checker_status': health_checker_result['overall_status'],
                'system_checker_status': system_checker_result['overall_status'],
                'health_checker_services': health_checker_result.get('services', []),
                'system_checker_services': system_checker_result.get('services', [])
            }
        except Exception as e:
            return {
                'overall_status': 'unhealthy',
                'error': str(e)
            }
    
    def _check_database_health(self):
        """Check database health."""
        try:
            start_time = timezone.now()
            
            # Test database connection
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'connection_test': True
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection_test': False
            }
    
    def _check_redis_health(self):
        """Check Redis health."""
        try:
            start_time = timezone.now()
            
            # Test Redis connection
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'ping_test': True
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'ping_test': False
            }
    
    def _check_api_health(self):
        """Check API health."""
        try:
            start_time = timezone.now()
            
            # Test API endpoint
            import requests
            response = requests.get('http://localhost:8000/api/health/', timeout=5)
            response.raise_for_status()
            
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'endpoint_test': True
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'endpoint_test': False
            }
    
    def _check_system_metrics_health(self):
        """Check system metrics health."""
        try:
            import psutil
            
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Check for high usage
            warnings = []
            if cpu_usage > 80:
                warnings.append('high_cpu_usage')
            if memory.percent > 85:
                warnings.append('high_memory_usage')
            if disk.percent > 90:
                warnings.append('high_disk_usage')
            
            status = 'warning' if warnings else 'healthy'
            
            return {
                'status': status,
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'warnings': warnings
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _check_application_health(self):
        """Check application health."""
        try:
            # Check database connectivity and basic operations
            tickets_count = Ticket.objects.count()
            users_count = User.objects.count()
            organizations_count = Organization.objects.count()
            
            return {
                'status': 'healthy',
                'tickets_count': tickets_count,
                'users_count': users_count,
                'organizations_count': organizations_count
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _check_network_health(self):
        """Check network health."""
        try:
            start_time = timezone.now()
            
            # Test external connectivity
            import requests
            response = requests.get('https://www.google.com', timeout=5)
            response.raise_for_status()
            
            end_time = timezone.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'connectivity_test': True
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connectivity_test': False
            }
    
    def _generate_health_report(self):
        """Generate comprehensive health report."""
        try:
            health_data = self._comprehensive_health_check()
            
            report_id = f"health_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                'report_id': report_id,
                'generated_at': timezone.now(),
                'overall_status': health_data['overall_status'],
                'health_summary': health_data
            }
        except Exception as e:
            return {
                'error': str(e)
            }


# Export test classes
__all__ = [
    'SystemHealthTest'
]
