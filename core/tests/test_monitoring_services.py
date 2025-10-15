"""
Comprehensive Monitoring Services Tests
Tests critical monitoring service logic including health checking, metrics collection, and alert generation.
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
from apps.tickets.models import Ticket
from apps.field_service.models import WorkOrder, Technician

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class SystemMetricsCollectorTest(EnhancedTransactionTestCase):
    """Test System Metrics Collector with comprehensive monitoring coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.metrics_collector = SystemMetricsCollector()
        
        # Create monitoring configuration
        self.monitoring_config = MonitoringConfiguration.objects.create(
            organization=self.organization,
            name="Test Monitoring Config",
            is_active=True,
            collection_interval=60,  # 1 minute
            retention_days=30
        )
    
    def test_collect_system_metrics_success(self):
        """Test successful system metrics collection."""
        with patch.object(self.metrics_collector, '_collect_cpu_metrics') as mock_cpu:
            mock_cpu.return_value = {'cpu_usage': 45.5, 'cpu_cores': 4}
            
            with patch.object(self.metrics_collector, '_collect_memory_metrics') as mock_memory:
                mock_memory.return_value = {'memory_usage': 60.2, 'memory_total': 8192}
                
                with patch.object(self.metrics_collector, '_collect_disk_metrics') as mock_disk:
                    mock_disk.return_value = {'disk_usage': 75.8, 'disk_total': 1000}
                    
                    result = self.metrics_collector.collect_system_metrics()
                    
                    self.assertIn('cpu_usage', result)
                    self.assertIn('memory_usage', result)
                    self.assertIn('disk_usage', result)
                    self.assertEqual(result['cpu_usage'], 45.5)
                    self.assertEqual(result['memory_usage'], 60.2)
                    self.assertEqual(result['disk_usage'], 75.8)
    
    def test_collect_system_metrics_partial_failure(self):
        """Test system metrics collection with partial failure."""
        with patch.object(self.metrics_collector, '_collect_cpu_metrics') as mock_cpu:
            mock_cpu.return_value = {'cpu_usage': 45.5, 'cpu_cores': 4}
            
            with patch.object(self.metrics_collector, '_collect_memory_metrics') as mock_memory:
                mock_memory.side_effect = Exception("Memory collection failed")
                
                with patch.object(self.metrics_collector, '_collect_disk_metrics') as mock_disk:
                    mock_disk.return_value = {'disk_usage': 75.8, 'disk_total': 1000}
                    
                    result = self.metrics_collector.collect_system_metrics()
                    
                    self.assertIn('cpu_usage', result)
                    self.assertIn('disk_usage', result)
                    self.assertIn('errors', result)
                    self.assertIn('Memory collection failed', result['errors'])
    
    def test_collect_cpu_metrics_success(self):
        """Test successful CPU metrics collection."""
        with patch('psutil.cpu_percent') as mock_cpu_percent:
            mock_cpu_percent.return_value = 45.5
            
            with patch('psutil.cpu_count') as mock_cpu_count:
                mock_cpu_count.return_value = 4
                
                result = self.metrics_collector._collect_cpu_metrics()
                
                self.assertEqual(result['cpu_usage'], 45.5)
                self.assertEqual(result['cpu_cores'], 4)
    
    def test_collect_cpu_metrics_error(self):
        """Test CPU metrics collection with error."""
        with patch('psutil.cpu_percent') as mock_cpu_percent:
            mock_cpu_percent.side_effect = Exception("CPU metrics unavailable")
            
            with self.assertRaises(Exception):
                self.metrics_collector._collect_cpu_metrics()
    
    def test_collect_memory_metrics_success(self):
        """Test successful memory metrics collection."""
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value = Mock(
                percent=60.2,
                total=8192 * 1024 * 1024,  # 8GB in bytes
                available=3276 * 1024 * 1024  # 3.2GB in bytes
            )
            
            result = self.metrics_collector._collect_memory_metrics()
            
            self.assertEqual(result['memory_usage'], 60.2)
            self.assertEqual(result['memory_total'], 8192)
            self.assertEqual(result['memory_available'], 3276)
    
    def test_collect_memory_metrics_error(self):
        """Test memory metrics collection with error."""
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.side_effect = Exception("Memory metrics unavailable")
            
            with self.assertRaises(Exception):
                self.metrics_collector._collect_memory_metrics()
    
    def test_collect_disk_metrics_success(self):
        """Test successful disk metrics collection."""
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk.return_value = Mock(
                percent=75.8,
                total=1000 * 1024 * 1024 * 1024,  # 1TB in bytes
                free=250 * 1024 * 1024 * 1024  # 250GB in bytes
            )
            
            result = self.metrics_collector._collect_disk_metrics()
            
            self.assertEqual(result['disk_usage'], 75.8)
            self.assertEqual(result['disk_total'], 1000)
            self.assertEqual(result['disk_free'], 250)
    
    def test_collect_disk_metrics_error(self):
        """Test disk metrics collection with error."""
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk.side_effect = Exception("Disk metrics unavailable")
            
            with self.assertRaises(Exception):
                self.metrics_collector._collect_disk_metrics()
    
    def test_collect_application_metrics_success(self):
        """Test successful application metrics collection."""
        # Create test data
        Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Test Ticket",
            description="Test description"
        )
        
        result = self.metrics_collector.collect_application_metrics()
        
        self.assertIn('tickets_count', result)
        self.assertIn('users_count', result)
        self.assertIn('organizations_count', result)
        self.assertEqual(result['tickets_count'], 1)
        self.assertEqual(result['users_count'], 1)
        self.assertEqual(result['organizations_count'], 1)
    
    def test_collect_application_metrics_error(self):
        """Test application metrics collection with error."""
        with patch('apps.monitoring.services.Ticket.objects.count') as mock_count:
            mock_count.side_effect = Exception("Database error")
            
            with self.assertRaises(Exception):
                self.metrics_collector.collect_application_metrics()
    
    def test_store_metrics_success(self):
        """Test successful metrics storage."""
        metrics_data = {
            'cpu_usage': 45.5,
            'memory_usage': 60.2,
            'disk_usage': 75.8
        }
        
        result = self.metrics_collector.store_metrics(metrics_data)
        
        self.assertTrue(result['stored'])
        self.assertIn('metric_id', result)
        
        # Verify metric was stored
        metric = SystemMetric.objects.get(id=result['metric_id'])
        self.assertEqual(metric.cpu_usage, 45.5)
        self.assertEqual(metric.memory_usage, 60.2)
        self.assertEqual(metric.disk_usage, 75.8)
    
    def test_store_metrics_error(self):
        """Test metrics storage with error."""
        metrics_data = {
            'cpu_usage': 'invalid',  # Invalid data type
            'memory_usage': 60.2,
            'disk_usage': 75.8
        }
        
        with self.assertRaises(ValueError):
            self.metrics_collector.store_metrics(metrics_data)
    
    def test_get_metrics_history_success(self):
        """Test successful metrics history retrieval."""
        # Create test metrics
        SystemMetric.objects.create(
            organization=self.organization,
            cpu_usage=45.5,
            memory_usage=60.2,
            disk_usage=75.8,
            timestamp=timezone.now()
        )
        
        result = self.metrics_collector.get_metrics_history(hours=24)
        
        self.assertIn('metrics', result)
        self.assertEqual(len(result['metrics']), 1)
        self.assertEqual(result['metrics'][0]['cpu_usage'], 45.5)
    
    def test_get_metrics_history_error(self):
        """Test metrics history retrieval with error."""
        with patch('apps.monitoring.services.SystemMetric.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")
            
            with self.assertRaises(Exception):
                self.metrics_collector.get_metrics_history(hours=24)


class AlertManagerTest(EnhancedTransactionTestCase):
    """Test Alert Manager with comprehensive alerting coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.alert_manager = AlertManager()
        
        # Create monitoring configuration
        self.monitoring_config = MonitoringConfiguration.objects.create(
            organization=self.organization,
            name="Test Monitoring Config",
            is_active=True,
            alert_thresholds={
                'cpu_usage': 80.0,
                'memory_usage': 85.0,
                'disk_usage': 90.0
            }
        )
    
    def test_check_metrics_alerts_success(self):
        """Test successful metrics alert checking."""
        metrics_data = {
            'cpu_usage': 85.0,  # Above threshold
            'memory_usage': 60.0,  # Below threshold
            'disk_usage': 95.0  # Above threshold
        }
        
        with patch.object(self.alert_manager, '_create_alert') as mock_create:
            mock_create.return_value = {'alert_id': 'alert_123'}
            
            result = self.alert_manager.check_metrics_alerts(metrics_data)
            
            self.assertIn('alerts_created', result)
            self.assertEqual(result['alerts_created'], 2)  # CPU and disk alerts
            self.assertEqual(mock_create.call_count, 2)
    
    def test_check_metrics_alerts_no_alerts(self):
        """Test metrics alert checking with no alerts."""
        metrics_data = {
            'cpu_usage': 50.0,  # Below threshold
            'memory_usage': 60.0,  # Below threshold
            'disk_usage': 70.0  # Below threshold
        }
        
        result = self.alert_manager.check_metrics_alerts(metrics_data)
        
        self.assertIn('alerts_created', result)
        self.assertEqual(result['alerts_created'], 0)
    
    def test_create_alert_success(self):
        """Test successful alert creation."""
        alert_data = {
            'type': 'cpu_usage_high',
            'severity': 'warning',
            'message': 'CPU usage is above threshold',
            'value': 85.0,
            'threshold': 80.0
        }
        
        result = self.alert_manager._create_alert(alert_data)
        
        self.assertIn('alert_id', result)
        self.assertTrue(result['created'])
        
        # Verify alert was created
        alert = Alert.objects.get(id=result['alert_id'])
        self.assertEqual(alert.alert_type, 'cpu_usage_high')
        self.assertEqual(alert.severity, 'warning')
        self.assertEqual(alert.message, 'CPU usage is above threshold')
    
    def test_create_alert_error(self):
        """Test alert creation with error."""
        alert_data = {
            'type': 'invalid_type',
            'severity': 'invalid_severity',
            'message': 'Test alert',
            'value': 85.0,
            'threshold': 80.0
        }
        
        with self.assertRaises(ValueError):
            self.alert_manager._create_alert(alert_data)
    
    def test_send_alert_notification_success(self):
        """Test successful alert notification sending."""
        alert = Alert.objects.create(
            organization=self.organization,
            alert_type='cpu_usage_high',
            severity='warning',
            message='CPU usage is above threshold',
            is_active=True
        )
        
        with patch.object(self.alert_manager, '_send_email_alert') as mock_email:
            mock_email.return_value = {'sent': True}
            
            with patch.object(self.alert_manager, '_send_slack_alert') as mock_slack:
                mock_slack.return_value = {'sent': True}
                
                result = self.alert_manager.send_alert_notification(alert)
                
                self.assertTrue(result['sent'])
                self.assertIn('email_sent', result)
                self.assertIn('slack_sent', result)
                mock_email.assert_called_once_with(alert)
                mock_slack.assert_called_once_with(alert)
    
    def test_send_alert_notification_error(self):
        """Test alert notification sending with error."""
        alert = Alert.objects.create(
            organization=self.organization,
            alert_type='cpu_usage_high',
            severity='warning',
            message='CPU usage is above threshold',
            is_active=True
        )
        
        with patch.object(self.alert_manager, '_send_email_alert') as mock_email:
            mock_email.side_effect = Exception("Email service unavailable")
            
            result = self.alert_manager.send_alert_notification(alert)
            
            self.assertFalse(result['sent'])
            self.assertIn('error', result)
            self.assertIn('Email service unavailable', result['error'])
    
    def test_resolve_alert_success(self):
        """Test successful alert resolution."""
        alert = Alert.objects.create(
            organization=self.organization,
            alert_type='cpu_usage_high',
            severity='warning',
            message='CPU usage is above threshold',
            is_active=True
        )
        
        result = self.alert_manager.resolve_alert(alert, 'CPU usage normalized')
        
        self.assertTrue(result['resolved'])
        alert.refresh_from_db()
        self.assertFalse(alert.is_active)
        self.assertEqual(alert.resolution, 'CPU usage normalized')
    
    def test_resolve_alert_error(self):
        """Test alert resolution with error."""
        alert = Alert.objects.create(
            organization=self.organization,
            alert_type='cpu_usage_high',
            severity='warning',
            message='CPU usage is above threshold',
            is_active=False  # Already resolved
        )
        
        with self.assertRaises(ValueError):
            self.alert_manager.resolve_alert(alert, 'Test resolution')
    
    def test_get_active_alerts_success(self):
        """Test successful active alerts retrieval."""
        # Create test alerts
        Alert.objects.create(
            organization=self.organization,
            alert_type='cpu_usage_high',
            severity='warning',
            message='CPU usage is above threshold',
            is_active=True
        )
        
        Alert.objects.create(
            organization=self.organization,
            alert_type='memory_usage_high',
            severity='critical',
            message='Memory usage is above threshold',
            is_active=True
        )
        
        result = self.alert_manager.get_active_alerts()
        
        self.assertIn('alerts', result)
        self.assertEqual(len(result['alerts']), 2)
    
    def test_get_active_alerts_error(self):
        """Test active alerts retrieval with error."""
        with patch('apps.monitoring.services.Alert.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")
            
            with self.assertRaises(Exception):
                self.alert_manager.get_active_alerts()


class HealthCheckerTest(EnhancedTransactionTestCase):
    """Test Health Checker with comprehensive health checking coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.health_checker = HealthChecker()
    
    def test_check_health_success(self):
        """Test successful health checking."""
        with patch.object(self.health_checker, '_check_database_health') as mock_db:
            mock_db.return_value = {'status': 'healthy', 'response_time': 50}
            
            with patch.object(self.health_checker, '_check_redis_health') as mock_redis:
                mock_redis.return_value = {'status': 'healthy', 'response_time': 10}
                
                with patch.object(self.health_checker, '_check_api_health') as mock_api:
                    mock_api.return_value = {'status': 'healthy', 'response_time': 100}
                    
                    result = self.health_checker.check_health()
                    
                    self.assertIn('overall_status', result)
                    self.assertIn('services', result)
                    self.assertEqual(result['overall_status'], 'healthy')
                    self.assertEqual(len(result['services']), 3)
    
    def test_check_health_partial_failure(self):
        """Test health checking with partial failure."""
        with patch.object(self.health_checker, '_check_database_health') as mock_db:
            mock_db.return_value = {'status': 'healthy', 'response_time': 50}
            
            with patch.object(self.health_checker, '_check_redis_health') as mock_redis:
                mock_redis.return_value = {'status': 'unhealthy', 'error': 'Connection failed'}
                
                with patch.object(self.health_checker, '_check_api_health') as mock_api:
                    mock_api.return_value = {'status': 'healthy', 'response_time': 100}
                    
                    result = self.health_checker.check_health()
                    
                    self.assertEqual(result['overall_status'], 'degraded')
                    self.assertEqual(len(result['services']), 3)
    
    def test_check_health_critical_failure(self):
        """Test health checking with critical failure."""
        with patch.object(self.health_checker, '_check_database_health') as mock_db:
            mock_db.return_value = {'status': 'unhealthy', 'error': 'Database unavailable'}
            
            with patch.object(self.health_checker, '_check_redis_health') as mock_redis:
                mock_redis.return_value = {'status': 'unhealthy', 'error': 'Redis unavailable'}
                
                with patch.object(self.health_checker, '_check_api_health') as mock_api:
                    mock_api.return_value = {'status': 'unhealthy', 'error': 'API unavailable'}
                    
                    result = self.health_checker.check_health()
                    
                    self.assertEqual(result['overall_status'], 'unhealthy')
                    self.assertEqual(len(result['services']), 3)
    
    def test_check_database_health_success(self):
        """Test successful database health check."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.05]  # 50ms response time
                
                result = self.health_checker._check_database_health()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 50)
    
    def test_check_database_health_failure(self):
        """Test database health check with failure."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.side_effect = Exception("Database connection failed")
            
            result = self.health_checker._check_database_health()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('Database connection failed', result['error'])
    
    def test_check_redis_health_success(self):
        """Test successful Redis health check."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.return_value = True
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.01]  # 10ms response time
                
                result = self.health_checker._check_redis_health()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 10)
    
    def test_check_redis_health_failure(self):
        """Test Redis health check with failure."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis connection failed")
            
            result = self.health_checker._check_redis_health()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('Redis connection failed', result['error'])
    
    def test_check_api_health_success(self):
        """Test successful API health check."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'status': 'healthy'}
            mock_get.return_value = mock_response
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.1]  # 100ms response time
                
                result = self.health_checker._check_api_health()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 100)
    
    def test_check_api_health_failure(self):
        """Test API health check with failure."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API connection failed")
            
            result = self.health_checker._check_api_health()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('API connection failed', result['error'])


class MonitoringServiceTest(EnhancedTransactionTestCase):
    """Test Monitoring Service with comprehensive monitoring coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.monitoring_service = MonitoringService()
    
    def test_start_monitoring_success(self):
        """Test successful monitoring start."""
        with patch.object(self.monitoring_service, '_start_metrics_collection') as mock_metrics:
            mock_metrics.return_value = {'started': True}
            
            with patch.object(self.monitoring_service, '_start_health_checking') as mock_health:
                mock_health.return_value = {'started': True}
                
                with patch.object(self.monitoring_service, '_start_alert_monitoring') as mock_alerts:
                    mock_alerts.return_value = {'started': True}
                    
                    result = self.monitoring_service.start_monitoring()
                    
                    self.assertTrue(result['started'])
                    self.assertIn('metrics_started', result)
                    self.assertIn('health_started', result)
                    self.assertIn('alerts_started', result)
    
    def test_start_monitoring_error(self):
        """Test monitoring start with error."""
        with patch.object(self.monitoring_service, '_start_metrics_collection') as mock_metrics:
            mock_metrics.side_effect = Exception("Metrics collection failed")
            
            result = self.monitoring_service.start_monitoring()
            
            self.assertFalse(result['started'])
            self.assertIn('error', result)
            self.assertIn('Metrics collection failed', result['error'])
    
    def test_stop_monitoring_success(self):
        """Test successful monitoring stop."""
        with patch.object(self.monitoring_service, '_stop_metrics_collection') as mock_metrics:
            mock_metrics.return_value = {'stopped': True}
            
            with patch.object(self.monitoring_service, '_stop_health_checking') as mock_health:
                mock_health.return_value = {'stopped': True}
                
                with patch.object(self.monitoring_service, '_stop_alert_monitoring') as mock_alerts:
                    mock_alerts.return_value = {'stopped': True}
                    
                    result = self.monitoring_service.stop_monitoring()
                    
                    self.assertTrue(result['stopped'])
                    self.assertIn('metrics_stopped', result)
                    self.assertIn('health_stopped', result)
                    self.assertIn('alerts_stopped', result)
    
    def test_stop_monitoring_error(self):
        """Test monitoring stop with error."""
        with patch.object(self.monitoring_service, '_stop_metrics_collection') as mock_metrics:
            mock_metrics.side_effect = Exception("Metrics collection stop failed")
            
            result = self.monitoring_service.stop_monitoring()
            
            self.assertFalse(result['stopped'])
            self.assertIn('error', result)
            self.assertIn('Metrics collection stop failed', result['error'])
    
    def test_get_monitoring_status_success(self):
        """Test successful monitoring status retrieval."""
        with patch.object(self.monitoring_service, '_get_metrics_status') as mock_metrics:
            mock_metrics.return_value = {'status': 'running', 'last_collection': timezone.now()}
            
            with patch.object(self.monitoring_service, '_get_health_status') as mock_health:
                mock_health.return_value = {'status': 'running', 'last_check': timezone.now()}
                
                with patch.object(self.monitoring_service, '_get_alerts_status') as mock_alerts:
                    mock_alerts.return_value = {'status': 'running', 'active_alerts': 2}
                    
                    result = self.monitoring_service.get_monitoring_status()
                    
                    self.assertIn('overall_status', result)
                    self.assertIn('metrics_status', result)
                    self.assertIn('health_status', result)
                    self.assertIn('alerts_status', result)
                    self.assertEqual(result['overall_status'], 'running')
    
    def test_get_monitoring_status_error(self):
        """Test monitoring status retrieval with error."""
        with patch.object(self.monitoring_service, '_get_metrics_status') as mock_metrics:
            mock_metrics.side_effect = Exception("Status retrieval failed")
            
            result = self.monitoring_service.get_monitoring_status()
            
            self.assertIn('error', result)
            self.assertIn('Status retrieval failed', result['error'])
    
    def test_generate_monitoring_report_success(self):
        """Test successful monitoring report generation."""
        # Create test data
        SystemMetric.objects.create(
            organization=self.organization,
            cpu_usage=45.5,
            memory_usage=60.2,
            disk_usage=75.8,
            timestamp=timezone.now()
        )
        
        Alert.objects.create(
            organization=self.organization,
            alert_type='cpu_usage_high',
            severity='warning',
            message='CPU usage is above threshold',
            is_active=True
        )
        
        result = self.monitoring_service.generate_monitoring_report()
        
        self.assertIn('report_id', result)
        self.assertIn('generated_at', result)
        self.assertIn('metrics_summary', result)
        self.assertIn('alerts_summary', result)
    
    def test_generate_monitoring_report_error(self):
        """Test monitoring report generation with error."""
        with patch('apps.monitoring.services.SystemMetric.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")
            
            with self.assertRaises(Exception):
                self.monitoring_service.generate_monitoring_report()


# Export test classes
__all__ = [
    'SystemMetricsCollectorTest',
    'AlertManagerTest',
    'HealthCheckerTest',
    'MonitoringServiceTest'
]
