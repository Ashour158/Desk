"""
Comprehensive API Enhanced Services Tests
Tests critical API enhanced service logic including logging, validation, and system checking.
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
from apps.api.enhanced_logging import LoggingConfiguration
from apps.api.system_checker import SystemChecker
from apps.api.ai_powered_validation import AIPoweredValidator
from apps.api.enhanced_validation import EnhancedValidator
from apps.tickets.models import Ticket
from apps.field_service.models import WorkOrder, Technician

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class LoggingConfigurationTest(EnhancedTransactionTestCase):
    """Test Logging Configuration with comprehensive logging coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.logging_config = LoggingConfiguration()
    
    def test_setup_logging_success(self):
        """Test successful logging setup."""
        with patch.object(self.logging_config, '_configure_loggers') as mock_configure:
            mock_configure.return_value = {'configured': True}
            
            with patch.object(self.logging_config, '_setup_handlers') as mock_handlers:
                mock_handlers.return_value = {'handlers_setup': True}
                
                with patch.object(self.logging_config, '_setup_formatters') as mock_formatters:
                    mock_formatters.return_value = {'formatters_setup': True}
                    
                    result = self.logging_config.setup_logging()
                    
                    self.assertTrue(result['setup'])
                    self.assertIn('loggers_configured', result)
                    self.assertIn('handlers_setup', result)
                    self.assertIn('formatters_setup', result)
    
    def test_setup_logging_error(self):
        """Test logging setup with error."""
        with patch.object(self.logging_config, '_configure_loggers') as mock_configure:
            mock_configure.side_effect = Exception("Logger configuration failed")
            
            result = self.logging_config.setup_logging()
            
            self.assertFalse(result['setup'])
            self.assertIn('error', result)
            self.assertIn('Logger configuration failed', result['error'])
    
    def test_configure_loggers_success(self):
        """Test successful logger configuration."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            result = self.logging_config._configure_loggers()
            
            self.assertTrue(result['configured'])
            self.assertGreater(mock_get_logger.call_count, 0)
    
    def test_configure_loggers_error(self):
        """Test logger configuration with error."""
        with patch('logging.getLogger') as mock_get_logger:
            mock_get_logger.side_effect = Exception("Logger creation failed")
            
            with self.assertRaises(Exception):
                self.logging_config._configure_loggers()
    
    def test_setup_handlers_success(self):
        """Test successful handler setup."""
        with patch('logging.StreamHandler') as mock_stream:
            mock_handler = Mock()
            mock_stream.return_value = mock_handler
            
            with patch('logging.FileHandler') as mock_file:
                mock_file_handler = Mock()
                mock_file.return_value = mock_file_handler
                
                result = self.logging_config._setup_handlers()
                
                self.assertTrue(result['handlers_setup'])
                self.assertGreater(mock_stream.call_count, 0)
                self.assertGreater(mock_file.call_count, 0)
    
    def test_setup_handlers_error(self):
        """Test handler setup with error."""
        with patch('logging.StreamHandler') as mock_stream:
            mock_stream.side_effect = Exception("Handler creation failed")
            
            with self.assertRaises(Exception):
                self.logging_config._setup_handlers()
    
    def test_setup_formatters_success(self):
        """Test successful formatter setup."""
        with patch('logging.Formatter') as mock_formatter:
            mock_formatter_instance = Mock()
            mock_formatter.return_value = mock_formatter_instance
            
            result = self.logging_config._setup_formatters()
            
            self.assertTrue(result['formatters_setup'])
            self.assertGreater(mock_formatter.call_count, 0)
    
    def test_setup_formatters_error(self):
        """Test formatter setup with error."""
        with patch('logging.Formatter') as mock_formatter:
            mock_formatter.side_effect = Exception("Formatter creation failed")
            
            with self.assertRaises(Exception):
                self.logging_config._setup_formatters()
    
    def test_configure_structured_logging_success(self):
        """Test successful structured logging configuration."""
        with patch.object(self.logging_config, '_setup_json_formatter') as mock_json:
            mock_json.return_value = {'json_formatter_setup': True}
            
            with patch.object(self.logging_config, '_setup_log_rotation') as mock_rotation:
                mock_rotation.return_value = {'rotation_setup': True}
                
                result = self.logging_config.configure_structured_logging()
                
                self.assertTrue(result['structured_logging_setup'])
                self.assertIn('json_formatter_setup', result)
                self.assertIn('rotation_setup', result)
    
    def test_configure_structured_logging_error(self):
        """Test structured logging configuration with error."""
        with patch.object(self.logging_config, '_setup_json_formatter') as mock_json:
            mock_json.side_effect = Exception("JSON formatter setup failed")
            
            result = self.logging_config.configure_structured_logging()
            
            self.assertFalse(result['structured_logging_setup'])
            self.assertIn('error', result)
            self.assertIn('JSON formatter setup failed', result['error'])
    
    def test_setup_json_formatter_success(self):
        """Test successful JSON formatter setup."""
        with patch('logging.Formatter') as mock_formatter:
            mock_formatter_instance = Mock()
            mock_formatter.return_value = mock_formatter_instance
            
            result = self.logging_config._setup_json_formatter()
            
            self.assertTrue(result['json_formatter_setup'])
            mock_formatter.assert_called_once()
    
    def test_setup_json_formatter_error(self):
        """Test JSON formatter setup with error."""
        with patch('logging.Formatter') as mock_formatter:
            mock_formatter.side_effect = Exception("JSON formatter creation failed")
            
            with self.assertRaises(Exception):
                self.logging_config._setup_json_formatter()
    
    def test_setup_log_rotation_success(self):
        """Test successful log rotation setup."""
        with patch('logging.handlers.RotatingFileHandler') as mock_rotating:
            mock_handler = Mock()
            mock_rotating.return_value = mock_handler
            
            result = self.logging_config._setup_log_rotation()
            
            self.assertTrue(result['rotation_setup'])
            mock_rotating.assert_called_once()
    
    def test_setup_log_rotation_error(self):
        """Test log rotation setup with error."""
        with patch('logging.handlers.RotatingFileHandler') as mock_rotating:
            mock_rotating.side_effect = Exception("Log rotation setup failed")
            
            with self.assertRaises(Exception):
                self.logging_config._setup_log_rotation()
    
    def test_configure_sensitive_data_sanitization_success(self):
        """Test successful sensitive data sanitization configuration."""
        with patch.object(self.logging_config, '_setup_sanitization_filters') as mock_filters:
            mock_filters.return_value = {'sanitization_setup': True}
            
            result = self.logging_config.configure_sensitive_data_sanitization()
            
            self.assertTrue(result['sanitization_configured'])
            self.assertIn('sanitization_setup', result)
    
    def test_configure_sensitive_data_sanitization_error(self):
        """Test sensitive data sanitization configuration with error."""
        with patch.object(self.logging_config, '_setup_sanitization_filters') as mock_filters:
            mock_filters.side_effect = Exception("Sanitization setup failed")
            
            result = self.logging_config.configure_sensitive_data_sanitization()
            
            self.assertFalse(result['sanitization_configured'])
            self.assertIn('error', result)
            self.assertIn('Sanitization setup failed', result['error'])
    
    def test_setup_sanitization_filters_success(self):
        """Test successful sanitization filters setup."""
        with patch('apps.api.enhanced_logging.SensitiveDataFilter') as mock_filter:
            mock_filter_instance = Mock()
            mock_filter.return_value = mock_filter_instance
            
            result = self.logging_config._setup_sanitization_filters()
            
            self.assertTrue(result['sanitization_setup'])
            mock_filter.assert_called_once()
    
    def test_setup_sanitization_filters_error(self):
        """Test sanitization filters setup with error."""
        with patch('apps.api.enhanced_logging.SensitiveDataFilter') as mock_filter:
            mock_filter.side_effect = Exception("Filter creation failed")
            
            with self.assertRaises(Exception):
                self.logging_config._setup_sanitization_filters()


class SystemCheckerTest(EnhancedTransactionTestCase):
    """Test System Checker with comprehensive system health checking coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.system_checker = SystemChecker()
    
    def test_check_all_services_success(self):
        """Test successful all services health check."""
        with patch.object(self.system_checker, '_check_database_service') as mock_db:
            mock_db.return_value = {'status': 'healthy', 'response_time': 50}
            
            with patch.object(self.system_checker, '_check_redis_service') as mock_redis:
                mock_redis.return_value = {'status': 'healthy', 'response_time': 10}
                
                with patch.object(self.system_checker, '_check_api_service') as mock_api:
                    mock_api.return_value = {'status': 'healthy', 'response_time': 100}
                    
                    result = self.system_checker.check_all_services()
                    
                    self.assertIn('overall_status', result)
                    self.assertIn('services', result)
                    self.assertEqual(result['overall_status'], 'healthy')
                    self.assertEqual(len(result['services']), 3)
    
    def test_check_all_services_partial_failure(self):
        """Test all services health check with partial failure."""
        with patch.object(self.system_checker, '_check_database_service') as mock_db:
            mock_db.return_value = {'status': 'healthy', 'response_time': 50}
            
            with patch.object(self.system_checker, '_check_redis_service') as mock_redis:
                mock_redis.return_value = {'status': 'unhealthy', 'error': 'Connection failed'}
                
                with patch.object(self.system_checker, '_check_api_service') as mock_api:
                    mock_api.return_value = {'status': 'healthy', 'response_time': 100}
                    
                    result = self.system_checker.check_all_services()
                    
                    self.assertEqual(result['overall_status'], 'degraded')
                    self.assertEqual(len(result['services']), 3)
    
    def test_check_all_services_critical_failure(self):
        """Test all services health check with critical failure."""
        with patch.object(self.system_checker, '_check_database_service') as mock_db:
            mock_db.return_value = {'status': 'unhealthy', 'error': 'Database unavailable'}
            
            with patch.object(self.system_checker, '_check_redis_service') as mock_redis:
                mock_redis.return_value = {'status': 'unhealthy', 'error': 'Redis unavailable'}
                
                with patch.object(self.system_checker, '_check_api_service') as mock_api:
                    mock_api.return_value = {'status': 'unhealthy', 'error': 'API unavailable'}
                    
                    result = self.system_checker.check_all_services()
                    
                    self.assertEqual(result['overall_status'], 'unhealthy')
                    self.assertEqual(len(result['services']), 3)
    
    def test_check_database_service_success(self):
        """Test successful database service health check."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.return_value = None
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.05]  # 50ms response time
                
                result = self.system_checker._check_database_service()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 50)
    
    def test_check_database_service_failure(self):
        """Test database service health check with failure."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.return_value.execute.side_effect = Exception("Database connection failed")
            
            result = self.system_checker._check_database_service()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('Database connection failed', result['error'])
    
    def test_check_redis_service_success(self):
        """Test successful Redis service health check."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.return_value = True
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.01]  # 10ms response time
                
                result = self.system_checker._check_redis_service()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 10)
    
    def test_check_redis_service_failure(self):
        """Test Redis service health check with failure."""
        with patch('redis.Redis') as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis connection failed")
            
            result = self.system_checker._check_redis_service()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('Redis connection failed', result['error'])
    
    def test_check_api_service_success(self):
        """Test successful API service health check."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'status': 'healthy'}
            mock_get.return_value = mock_response
            
            with patch('time.time') as mock_time:
                mock_time.side_effect = [1000, 1000.1]  # 100ms response time
                
                result = self.system_checker._check_api_service()
                
                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['response_time'], 100)
    
    def test_check_api_service_failure(self):
        """Test API service health check with failure."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API connection failed")
            
            result = self.system_checker._check_api_service()
            
            self.assertEqual(result['status'], 'unhealthy')
            self.assertIn('error', result)
            self.assertIn('API connection failed', result['error'])
    
    def test_check_features_success(self):
        """Test successful features availability check."""
        with patch.object(self.system_checker, '_check_tickets_feature') as mock_tickets:
            mock_tickets.return_value = {'available': True, 'features': ['create', 'read', 'update']}
            
            with patch.object(self.system_checker, '_check_work_orders_feature') as mock_work_orders:
                mock_work_orders.return_value = {'available': True, 'features': ['create', 'schedule']}
                
                result = self.system_checker.check_features()
                
                self.assertIn('tickets', result)
                self.assertIn('work_orders', result)
                self.assertTrue(result['tickets']['available'])
                self.assertTrue(result['work_orders']['available'])
    
    def test_check_features_partial_failure(self):
        """Test features availability check with partial failure."""
        with patch.object(self.system_checker, '_check_tickets_feature') as mock_tickets:
            mock_tickets.return_value = {'available': True, 'features': ['create', 'read', 'update']}
            
            with patch.object(self.system_checker, '_check_work_orders_feature') as mock_work_orders:
                mock_work_orders.return_value = {'available': False, 'error': 'Work orders service unavailable'}
                
                result = self.system_checker.check_features()
                
                self.assertTrue(result['tickets']['available'])
                self.assertFalse(result['work_orders']['available'])
    
    def test_check_tickets_feature_success(self):
        """Test successful tickets feature check."""
        # Create test ticket
        Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Test Ticket",
            description="Test description"
        )
        
        result = self.system_checker._check_tickets_feature()
        
        self.assertTrue(result['available'])
        self.assertIn('features', result)
        self.assertIn('create', result['features'])
        self.assertIn('read', result['features'])
    
    def test_check_tickets_feature_failure(self):
        """Test tickets feature check with failure."""
        with patch('apps.tickets.models.Ticket.objects.create') as mock_create:
            mock_create.side_effect = Exception("Tickets service unavailable")
            
            result = self.system_checker._check_tickets_feature()
            
            self.assertFalse(result['available'])
            self.assertIn('error', result)
            self.assertIn('Tickets service unavailable', result['error'])
    
    def test_check_work_orders_feature_success(self):
        """Test successful work orders feature check."""
        # Create test work order
        technician = Technician.objects.create(
            organization=self.organization,
            user=self.user,
            name="Test Technician",
            skills=["technical"],
            is_active=True
        )
        
        WorkOrder.objects.create(
            organization=self.organization,
            technician=technician,
            subject="Test Work Order",
            description="Test description"
        )
        
        result = self.system_checker._check_work_orders_feature()
        
        self.assertTrue(result['available'])
        self.assertIn('features', result)
        self.assertIn('create', result['features'])
        self.assertIn('schedule', result['features'])
    
    def test_check_work_orders_feature_failure(self):
        """Test work orders feature check with failure."""
        with patch('apps.field_service.models.WorkOrder.objects.create') as mock_create:
            mock_create.side_effect = Exception("Work orders service unavailable")
            
            result = self.system_checker._check_work_orders_feature()
            
            self.assertFalse(result['available'])
            self.assertIn('error', result)
            self.assertIn('Work orders service unavailable', result['error'])
    
    def test_generate_report_success(self):
        """Test successful system status report generation."""
        with patch.object(self.system_checker, 'check_all_services') as mock_services:
            mock_services.return_value = {
                'overall_status': 'healthy',
                'services': [
                    {'name': 'database', 'status': 'healthy'},
                    {'name': 'redis', 'status': 'healthy'},
                    {'name': 'api', 'status': 'healthy'}
                ]
            }
            
            with patch.object(self.system_checker, 'check_features') as mock_features:
                mock_features.return_value = {
                    'tickets': {'available': True},
                    'work_orders': {'available': True}
                }
                
                result = self.system_checker.generate_report()
                
                self.assertIn('report_id', result)
                self.assertIn('generated_at', result)
                self.assertIn('overall_status', result)
                self.assertIn('services_status', result)
                self.assertIn('features_status', result)
    
    def test_generate_report_error(self):
        """Test system status report generation with error."""
        with patch.object(self.system_checker, 'check_all_services') as mock_services:
            mock_services.side_effect = Exception("Service check failed")
            
            result = self.system_checker.generate_report()
            
            self.assertIn('error', result)
            self.assertIn('Service check failed', result['error'])


class AIPoweredValidatorTest(EnhancedTransactionTestCase):
    """Test AI Powered Validator with comprehensive validation coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.ai_validator = AIPoweredValidator()
    
    def test_validate_data_success(self):
        """Test successful AI-powered data validation."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical'
        }
        
        with patch.object(self.ai_validator, '_analyze_data_quality') as mock_analyze:
            mock_analyze.return_value = {'quality_score': 0.95, 'issues': []}
            
            with patch.object(self.ai_validator, '_detect_anomalies') as mock_detect:
                mock_detect.return_value = {'anomalies': [], 'risk_score': 0.1}
                
                result = self.ai_validator.validate_data(data)
                
                self.assertTrue(result['is_valid'])
                self.assertEqual(result['quality_score'], 0.95)
                self.assertEqual(result['risk_score'], 0.1)
                self.assertEqual(len(result['issues']), 0)
    
    def test_validate_data_quality_issues(self):
        """Test AI-powered data validation with quality issues."""
        data = {
            'subject': '',  # Empty subject
            'description': 'Short',  # Too short description
            'priority': 'invalid',  # Invalid priority
            'category': 'technical'
        }
        
        with patch.object(self.ai_validator, '_analyze_data_quality') as mock_analyze:
            mock_analyze.return_value = {
                'quality_score': 0.3,
                'issues': ['Empty subject', 'Description too short', 'Invalid priority']
            }
            
            with patch.object(self.ai_validator, '_detect_anomalies') as mock_detect:
                mock_detect.return_value = {'anomalies': [], 'risk_score': 0.1}
                
                result = self.ai_validator.validate_data(data)
                
                self.assertFalse(result['is_valid'])
                self.assertEqual(result['quality_score'], 0.3)
                self.assertEqual(len(result['issues']), 3)
    
    def test_validate_data_anomalies_detected(self):
        """Test AI-powered data validation with anomalies detected."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical'
        }
        
        with patch.object(self.ai_validator, '_analyze_data_quality') as mock_analyze:
            mock_analyze.return_value = {'quality_score': 0.95, 'issues': []}
            
            with patch.object(self.ai_validator, '_detect_anomalies') as mock_detect:
                mock_detect.return_value = {
                    'anomalies': ['Suspicious pattern detected'],
                    'risk_score': 0.8
                }
                
                result = self.ai_validator.validate_data(data)
                
                self.assertFalse(result['is_valid'])
                self.assertEqual(result['risk_score'], 0.8)
                self.assertIn('Suspicious pattern detected', result['anomalies'])
    
    def test_analyze_data_quality_success(self):
        """Test successful data quality analysis."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a comprehensive ticket description with sufficient detail',
            'priority': 'high',
            'category': 'technical'
        }
        
        with patch.object(self.ai_validator, '_check_completeness') as mock_completeness:
            mock_completeness.return_value = 1.0
            
            with patch.object(self.ai_validator, '_check_consistency') as mock_consistency:
                mock_consistency.return_value = 0.9
                
                with patch.object(self.ai_validator, '_check_relevance') as mock_relevance:
                    mock_relevance.return_value = 0.95
                    
                    result = self.ai_validator._analyze_data_quality(data)
                    
                    self.assertIn('quality_score', result)
                    self.assertIn('issues', result)
                    self.assertGreater(result['quality_score'], 0.8)
    
    def test_analyze_data_quality_error(self):
        """Test data quality analysis with error."""
        data = {'invalid': 'data'}
        
        with patch.object(self.ai_validator, '_check_completeness') as mock_completeness:
            mock_completeness.side_effect = Exception("Quality analysis failed")
            
            with self.assertRaises(Exception):
                self.ai_validator._analyze_data_quality(data)
    
    def test_detect_anomalies_success(self):
        """Test successful anomaly detection."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical'
        }
        
        with patch.object(self.ai_validator, '_check_patterns') as mock_patterns:
            mock_patterns.return_value = {'suspicious_patterns': []}
            
            with patch.object(self.ai_validator, '_check_frequency') as mock_frequency:
                mock_frequency.return_value = {'frequency_anomalies': []}
                
                result = self.ai_validator._detect_anomalies(data)
                
                self.assertIn('anomalies', result)
                self.assertIn('risk_score', result)
                self.assertEqual(len(result['anomalies']), 0)
    
    def test_detect_anomalies_suspicious_patterns(self):
        """Test anomaly detection with suspicious patterns."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical'
        }
        
        with patch.object(self.ai_validator, '_check_patterns') as mock_patterns:
            mock_patterns.return_value = {'suspicious_patterns': ['Repeated content']}
            
            with patch.object(self.ai_validator, '_check_frequency') as mock_frequency:
                mock_frequency.return_value = {'frequency_anomalies': []}
                
                result = self.ai_validator._detect_anomalies(data)
                
                self.assertIn('anomalies', result)
                self.assertIn('risk_score', result)
                self.assertIn('Repeated content', result['anomalies'])
    
    def test_detect_anomalies_error(self):
        """Test anomaly detection with error."""
        data = {'invalid': 'data'}
        
        with patch.object(self.ai_validator, '_check_patterns') as mock_patterns:
            mock_patterns.side_effect = Exception("Anomaly detection failed")
            
            with self.assertRaises(Exception):
                self.ai_validator._detect_anomalies(data)
    
    def test_check_completeness_success(self):
        """Test successful completeness check."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical'
        }
        
        result = self.ai_validator._check_completeness(data)
        
        self.assertEqual(result, 1.0)  # All required fields present
    
    def test_check_completeness_missing_fields(self):
        """Test completeness check with missing fields."""
        data = {
            'subject': 'Test Ticket',
            'description': '',  # Missing description
            'priority': 'high'
            # Missing category
        }
        
        result = self.ai_validator._check_completeness(data)
        
        self.assertLess(result, 1.0)  # Not all required fields present
    
    def test_check_consistency_success(self):
        """Test successful consistency check."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical'
        }
        
        result = self.ai_validator._check_consistency(data)
        
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)
    
    def test_check_consistency_inconsistent(self):
        """Test consistency check with inconsistent data."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'billing'  # Inconsistent with technical priority
        }
        
        result = self.ai_validator._check_consistency(data)
        
        self.assertLess(result, 1.0)  # Inconsistent data
    
    def test_check_relevance_success(self):
        """Test successful relevance check."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical'
        }
        
        result = self.ai_validator._check_relevance(data)
        
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)
    
    def test_check_relevance_irrelevant(self):
        """Test relevance check with irrelevant data."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical',
            'unrelated_field': 'This field is not relevant to tickets'
        }
        
        result = self.ai_validator._check_relevance(data)
        
        self.assertLess(result, 1.0)  # Contains irrelevant data


class EnhancedValidatorTest(EnhancedTransactionTestCase):
    """Test Enhanced Validator with comprehensive validation coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.enhanced_validator = EnhancedValidator()
    
    def test_validate_ticket_data_success(self):
        """Test successful ticket data validation."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high',
            'category': 'technical'
        }
        
        result = self.enhanced_validator.validate_ticket_data(data)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_ticket_data_validation_errors(self):
        """Test ticket data validation with errors."""
        data = {
            'subject': '',  # Empty subject
            'description': 'Short',  # Too short description
            'priority': 'invalid',  # Invalid priority
            'category': 'technical'
        }
        
        result = self.enhanced_validator.validate_ticket_data(data)
        
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn('Subject is required', result['errors'])
        self.assertIn('Description is too short', result['errors'])
        self.assertIn('Invalid priority', result['errors'])
    
    def test_validate_work_order_data_success(self):
        """Test successful work order data validation."""
        data = {
            'subject': 'Test Work Order',
            'description': 'This is a valid work order description',
            'priority': 'medium',
            'technician_id': 1
        }
        
        result = self.enhanced_validator.validate_work_order_data(data)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_work_order_data_validation_errors(self):
        """Test work order data validation with errors."""
        data = {
            'subject': '',  # Empty subject
            'description': 'Short',  # Too short description
            'priority': 'invalid',  # Invalid priority
            'technician_id': None  # Missing technician
        }
        
        result = self.enhanced_validator.validate_work_order_data(data)
        
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn('Subject is required', result['errors'])
        self.assertIn('Description is too short', result['errors'])
        self.assertIn('Invalid priority', result['errors'])
        self.assertIn('Technician is required', result['errors'])
    
    def test_validate_user_data_success(self):
        """Test successful user data validation."""
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'agent'
        }
        
        result = self.enhanced_validator.validate_user_data(data)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_user_data_validation_errors(self):
        """Test user data validation with errors."""
        data = {
            'email': 'invalid-email',  # Invalid email
            'first_name': '',  # Empty first name
            'last_name': '',  # Empty last name
            'role': 'invalid'  # Invalid role
        }
        
        result = self.enhanced_validator.validate_user_data(data)
        
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn('Invalid email format', result['errors'])
        self.assertIn('First name is required', result['errors'])
        self.assertIn('Last name is required', result['errors'])
        self.assertIn('Invalid role', result['errors'])
    
    def test_validate_email_format_success(self):
        """Test successful email format validation."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'test+tag@example.org'
        ]
        
        for email in valid_emails:
            result = self.enhanced_validator._validate_email_format(email)
            self.assertTrue(result)
    
    def test_validate_email_format_invalid(self):
        """Test email format validation with invalid emails."""
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'test@',
            'test.example.com'
        ]
        
        for email in invalid_emails:
            result = self.enhanced_validator._validate_email_format(email)
            self.assertFalse(result)
    
    def test_validate_priority_success(self):
        """Test successful priority validation."""
        valid_priorities = ['low', 'medium', 'high', 'critical']
        
        for priority in valid_priorities:
            result = self.enhanced_validator._validate_priority(priority)
            self.assertTrue(result)
    
    def test_validate_priority_invalid(self):
        """Test priority validation with invalid priorities."""
        invalid_priorities = ['invalid', 'urgent', 'normal', '']
        
        for priority in invalid_priorities:
            result = self.enhanced_validator._validate_priority(priority)
            self.assertFalse(result)
    
    def test_validate_category_success(self):
        """Test successful category validation."""
        valid_categories = ['technical', 'billing', 'general', 'support']
        
        for category in valid_categories:
            result = self.enhanced_validator._validate_category(category)
            self.assertTrue(result)
    
    def test_validate_category_invalid(self):
        """Test category validation with invalid categories."""
        invalid_categories = ['invalid', 'sales', 'marketing', '']
        
        for category in invalid_categories:
            result = self.enhanced_validator._validate_category(category)
            self.assertFalse(result)
    
    def test_validate_role_success(self):
        """Test successful role validation."""
        valid_roles = ['admin', 'agent', 'customer', 'manager']
        
        for role in valid_roles:
            result = self.enhanced_validator._validate_role(role)
            self.assertTrue(result)
    
    def test_validate_role_invalid(self):
        """Test role validation with invalid roles."""
        invalid_roles = ['invalid', 'user', 'staff', '']
        
        for role in invalid_roles:
            result = self.enhanced_validator._validate_role(role)
            self.assertFalse(result)
    
    def test_validate_required_fields_success(self):
        """Test successful required fields validation."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description',
            'priority': 'high'
        }
        
        required_fields = ['subject', 'description', 'priority']
        
        result = self.enhanced_validator._validate_required_fields(data, required_fields)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_required_fields_missing(self):
        """Test required fields validation with missing fields."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description'
            # Missing priority
        }
        
        required_fields = ['subject', 'description', 'priority']
        
        result = self.enhanced_validator._validate_required_fields(data, required_fields)
        
        self.assertFalse(result['is_valid'])
        self.assertIn('Priority is required', result['errors'])
    
    def test_validate_field_length_success(self):
        """Test successful field length validation."""
        data = {
            'subject': 'Test Ticket',
            'description': 'This is a valid ticket description with sufficient length'
        }
        
        field_lengths = {
            'subject': {'min': 5, 'max': 100},
            'description': {'min': 20, 'max': 1000}
        }
        
        result = self.enhanced_validator._validate_field_lengths(data, field_lengths)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_field_length_invalid(self):
        """Test field length validation with invalid lengths."""
        data = {
            'subject': 'Test',  # Too short
            'description': 'Short'  # Too short
        }
        
        field_lengths = {
            'subject': {'min': 5, 'max': 100},
            'description': {'min': 20, 'max': 1000}
        }
        
        result = self.enhanced_validator._validate_field_lengths(data, field_lengths)
        
        self.assertFalse(result['is_valid'])
        self.assertIn('Subject is too short', result['errors'])
        self.assertIn('Description is too short', result['errors'])


# Export test classes
__all__ = [
    'LoggingConfigurationTest',
    'SystemCheckerTest',
    'AIPoweredValidatorTest',
    'EnhancedValidatorTest'
]
