"""
Comprehensive Security Monitoring Tests
Tests critical security monitoring logic including threat detection, log analysis, and security alerts.
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
from apps.security_compliance.models import SecurityPolicy, AuditLog, ComplianceCheck, IncidentResponse, PenetrationTest
from apps.security.monitoring import SecurityMonitor
from apps.monitoring.models import Alert
from apps.tickets.models import Ticket

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class SecurityMonitorTest(EnhancedTransactionTestCase):
    """Test Security Monitor with comprehensive security monitoring coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.security_monitor = SecurityMonitor()
        
        # Create security policy
        self.security_policy = SecurityPolicy.objects.create(
            organization=self.organization,
            name="Test Security Policy",
            policy_type="access_control",
            is_active=True,
            rules={
                'max_login_attempts': 5,
                'session_timeout': 3600,
                'password_complexity': True
            }
        )
    
    def test_detect_threats_success(self):
        """Test successful threat detection."""
        with patch.object(self.security_monitor, '_analyze_security_logs') as mock_analyze:
            mock_analyze.return_value = {'threats_detected': 0, 'risk_level': 'low'}
            
            with patch.object(self.security_monitor, '_check_suspicious_activities') as mock_check:
                mock_check.return_value = {'suspicious_activities': 0, 'risk_level': 'low'}
                
                result = self.security_monitor.detect_threats()
                
                self.assertEqual(result['overall_risk_level'], 'low')
                self.assertIn('threats_detected', result)
                self.assertIn('suspicious_activities', result)
                self.assertEqual(result['threats_detected'], 0)
                self.assertEqual(result['suspicious_activities'], 0)
    
    def test_detect_threats_high_risk(self):
        """Test threat detection with high risk threats."""
        with patch.object(self.security_monitor, '_analyze_security_logs') as mock_analyze:
            mock_analyze.return_value = {
                'threats_detected': 3,
                'risk_level': 'high',
                'threats': [
                    {'type': 'brute_force', 'severity': 'high'},
                    {'type': 'sql_injection', 'severity': 'critical'},
                    {'type': 'xss_attempt', 'severity': 'medium'}
                ]
            }
            
            with patch.object(self.security_monitor, '_check_suspicious_activities') as mock_check:
                mock_check.return_value = {'suspicious_activities': 2, 'risk_level': 'medium'}
                
                result = self.security_monitor.detect_threats()
                
                self.assertEqual(result['overall_risk_level'], 'high')
                self.assertEqual(result['threats_detected'], 3)
                self.assertEqual(result['suspicious_activities'], 2)
                self.assertIn('threats', result)
                self.assertEqual(len(result['threats']), 3)
    
    def test_detect_threats_critical_risk(self):
        """Test threat detection with critical risk threats."""
        with patch.object(self.security_monitor, '_analyze_security_logs') as mock_analyze:
            mock_analyze.return_value = {
                'threats_detected': 5,
                'risk_level': 'critical',
                'threats': [
                    {'type': 'data_breach', 'severity': 'critical'},
                    {'type': 'privilege_escalation', 'severity': 'critical'},
                    {'type': 'malware_detected', 'severity': 'critical'}
                ]
            }
            
            with patch.object(self.security_monitor, '_check_suspicious_activities') as mock_check:
                mock_check.return_value = {'suspicious_activities': 3, 'risk_level': 'high'}
                
                result = self.security_monitor.detect_threats()
                
                self.assertEqual(result['overall_risk_level'], 'critical')
                self.assertEqual(result['threats_detected'], 5)
                self.assertEqual(result['suspicious_activities'], 3)
                self.assertIn('critical_threats', result)
                self.assertEqual(len(result['critical_threats']), 3)
    
    def test_detect_threats_error(self):
        """Test threat detection with error."""
        with patch.object(self.security_monitor, '_analyze_security_logs') as mock_analyze:
            mock_analyze.side_effect = Exception("Security log analysis failed")
            
            result = self.security_monitor.detect_threats()
            
            self.assertEqual(result['overall_risk_level'], 'unknown')
            self.assertIn('error', result)
            self.assertIn('Security log analysis failed', result['error'])
    
    def test_analyze_security_logs_success(self):
        """Test successful security log analysis."""
        with patch.object(self.security_monitor, '_get_security_logs') as mock_get_logs:
            mock_get_logs.return_value = [
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
                {'event': 'login', 'user': 'user2', 'ip': '192.168.1.2', 'timestamp': timezone.now()}
            ]
            
            with patch.object(self.security_monitor, '_detect_brute_force') as mock_brute_force:
                mock_brute_force.return_value = {'detected': False, 'attempts': 0}
                
                with patch.object(self.security_monitor, '_detect_sql_injection') as mock_sql_injection:
                    mock_sql_injection.return_value = {'detected': False, 'attempts': 0}
                    
                    result = self.security_monitor._analyze_security_logs()
                    
                    self.assertEqual(result['threats_detected'], 0)
                    self.assertEqual(result['risk_level'], 'low')
                    self.assertEqual(len(result['threats']), 0)
    
    def test_analyze_security_logs_threats_detected(self):
        """Test security log analysis with threats detected."""
        with patch.object(self.security_monitor, '_get_security_logs') as mock_get_logs:
            mock_get_logs.return_value = [
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()}
            ]
            
            with patch.object(self.security_monitor, '_detect_brute_force') as mock_brute_force:
                mock_brute_force.return_value = {
                    'detected': True,
                    'attempts': 6,
                    'user': 'user1',
                    'ip': '192.168.1.1'
                }
                
                with patch.object(self.security_monitor, '_detect_sql_injection') as mock_sql_injection:
                    mock_sql_injection.return_value = {'detected': False, 'attempts': 0}
                    
                    result = self.security_monitor._analyze_security_logs()
                    
                    self.assertEqual(result['threats_detected'], 1)
                    self.assertEqual(result['risk_level'], 'high')
                    self.assertEqual(len(result['threats']), 1)
                    self.assertEqual(result['threats'][0]['type'], 'brute_force')
    
    def test_analyze_security_logs_error(self):
        """Test security log analysis with error."""
        with patch.object(self.security_monitor, '_get_security_logs') as mock_get_logs:
            mock_get_logs.side_effect = Exception("Failed to retrieve security logs")
            
            with self.assertRaises(Exception):
                self.security_monitor._analyze_security_logs()
    
    def test_check_suspicious_activities_success(self):
        """Test successful suspicious activities check."""
        with patch.object(self.security_monitor, '_check_unusual_login_patterns') as mock_login:
            mock_login.return_value = {'suspicious': False, 'activities': 0}
            
            with patch.object(self.security_monitor, '_check_privilege_escalation') as mock_privilege:
                mock_privilege.return_value = {'suspicious': False, 'activities': 0}
                
                with patch.object(self.security_monitor, '_check_data_access_patterns') as mock_data:
                    mock_data.return_value = {'suspicious': False, 'activities': 0}
                    
                    result = self.security_monitor._check_suspicious_activities()
                    
                    self.assertEqual(result['suspicious_activities'], 0)
                    self.assertEqual(result['risk_level'], 'low')
    
    def test_check_suspicious_activities_detected(self):
        """Test suspicious activities check with activities detected."""
        with patch.object(self.security_monitor, '_check_unusual_login_patterns') as mock_login:
            mock_login.return_value = {
                'suspicious': True,
                'activities': 2,
                'details': [
                    {'type': 'unusual_time', 'user': 'user1', 'time': '03:00'},
                    {'type': 'unusual_location', 'user': 'user2', 'location': 'Unknown'}
                ]
            }
            
            with patch.object(self.security_monitor, '_check_privilege_escalation') as mock_privilege:
                mock_privilege.return_value = {'suspicious': False, 'activities': 0}
                
                with patch.object(self.security_monitor, '_check_data_access_patterns') as mock_data:
                    mock_data.return_value = {'suspicious': False, 'activities': 0}
                    
                    result = self.security_monitor._check_suspicious_activities()
                    
                    self.assertEqual(result['suspicious_activities'], 2)
                    self.assertEqual(result['risk_level'], 'medium')
                    self.assertIn('details', result)
                    self.assertEqual(len(result['details']), 2)
    
    def test_check_suspicious_activities_error(self):
        """Test suspicious activities check with error."""
        with patch.object(self.security_monitor, '_check_unusual_login_patterns') as mock_login:
            mock_login.side_effect = Exception("Login pattern analysis failed")
            
            with self.assertRaises(Exception):
                self.security_monitor._check_suspicious_activities()
    
    def test_detect_brute_force_success(self):
        """Test successful brute force detection."""
        logs = [
            {'event': 'login_failed', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
            {'event': 'login_failed', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
            {'event': 'login_failed', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
            {'event': 'login_failed', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
            {'event': 'login_failed', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
            {'event': 'login_failed', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._detect_brute_force(logs)
        
        self.assertTrue(result['detected'])
        self.assertEqual(result['attempts'], 6)
        self.assertEqual(result['user'], 'user1')
        self.assertEqual(result['ip'], '192.168.1.1')
    
    def test_detect_brute_force_not_detected(self):
        """Test brute force detection with no brute force attempts."""
        logs = [
            {'event': 'login_failed', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
            {'event': 'login_failed', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._detect_brute_force(logs)
        
        self.assertFalse(result['detected'])
        self.assertEqual(result['attempts'], 2)
    
    def test_detect_sql_injection_success(self):
        """Test successful SQL injection detection."""
        logs = [
            {'event': 'query', 'sql': "SELECT * FROM users WHERE id = 1 OR 1=1", 'user': 'user1', 'timestamp': timezone.now()},
            {'event': 'query', 'sql': "SELECT * FROM users WHERE name = 'admin'--", 'user': 'user1', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._detect_sql_injection(logs)
        
        self.assertTrue(result['detected'])
        self.assertEqual(result['attempts'], 2)
        self.assertEqual(result['user'], 'user1')
        self.assertIn('sql_injection_patterns', result)
    
    def test_detect_sql_injection_not_detected(self):
        """Test SQL injection detection with no SQL injection attempts."""
        logs = [
            {'event': 'query', 'sql': "SELECT * FROM users WHERE id = 1", 'user': 'user1', 'timestamp': timezone.now()},
            {'event': 'query', 'sql': "SELECT * FROM users WHERE name = 'admin'", 'user': 'user1', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._detect_sql_injection(logs)
        
        self.assertFalse(result['detected'])
        self.assertEqual(result['attempts'], 0)
    
    def test_detect_xss_attempts_success(self):
        """Test successful XSS attempt detection."""
        logs = [
            {'event': 'request', 'url': '/search?q=<script>alert(1)</script>', 'user': 'user1', 'timestamp': timezone.now()},
            {'event': 'request', 'url': '/comment?text=<img src=x onerror=alert(1)>', 'user': 'user1', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._detect_xss_attempts(logs)
        
        self.assertTrue(result['detected'])
        self.assertEqual(result['attempts'], 2)
        self.assertEqual(result['user'], 'user1')
        self.assertIn('xss_patterns', result)
    
    def test_detect_xss_attempts_not_detected(self):
        """Test XSS attempt detection with no XSS attempts."""
        logs = [
            {'event': 'request', 'url': '/search?q=normal_search', 'user': 'user1', 'timestamp': timezone.now()},
            {'event': 'request', 'url': '/comment?text=normal_comment', 'user': 'user1', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._detect_xss_attempts(logs)
        
        self.assertFalse(result['detected'])
        self.assertEqual(result['attempts'], 0)
    
    def test_analyze_logs_success(self):
        """Test successful log analysis."""
        with patch.object(self.security_monitor, '_get_security_logs') as mock_get_logs:
            mock_get_logs.return_value = [
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
                {'event': 'login', 'user': 'user2', 'ip': '192.168.1.2', 'timestamp': timezone.now()}
            ]
            
            with patch.object(self.security_monitor, '_parse_log_entry') as mock_parse:
                mock_parse.return_value = {'parsed': True, 'event_type': 'login'}
                
                result = self.security_monitor.analyze_logs()
                
                self.assertIn('logs_analyzed', result)
                self.assertIn('analysis_summary', result)
                self.assertEqual(result['logs_analyzed'], 2)
    
    def test_analyze_logs_error(self):
        """Test log analysis with error."""
        with patch.object(self.security_monitor, '_get_security_logs') as mock_get_logs:
            mock_get_logs.side_effect = Exception("Log retrieval failed")
            
            result = self.security_monitor.analyze_logs()
            
            self.assertIn('error', result)
            self.assertIn('Log retrieval failed', result['error'])
    
    def test_generate_alerts_success(self):
        """Test successful security alert generation."""
        threat_data = {
            'threats_detected': 2,
            'risk_level': 'high',
            'threats': [
                {'type': 'brute_force', 'severity': 'high', 'user': 'user1'},
                {'type': 'sql_injection', 'severity': 'critical', 'user': 'user2'}
            ]
        }
        
        with patch.object(self.security_monitor, '_create_security_alert') as mock_create:
            mock_create.return_value = {'alert_id': 'alert_123', 'created': True}
            
            result = self.security_monitor.generate_alerts(threat_data)
            
            self.assertIn('alerts_generated', result)
            self.assertIn('alert_ids', result)
            self.assertEqual(result['alerts_generated'], 2)
            self.assertEqual(len(result['alert_ids']), 2)
    
    def test_generate_alerts_error(self):
        """Test security alert generation with error."""
        threat_data = {
            'threats_detected': 1,
            'risk_level': 'high',
            'threats': [{'type': 'brute_force', 'severity': 'high'}]
        }
        
        with patch.object(self.security_monitor, '_create_security_alert') as mock_create:
            mock_create.side_effect = Exception("Alert creation failed")
            
            result = self.security_monitor.generate_alerts(threat_data)
            
            self.assertIn('error', result)
            self.assertIn('Alert creation failed', result['error'])
    
    def test_create_security_alert_success(self):
        """Test successful security alert creation."""
        threat = {
            'type': 'brute_force',
            'severity': 'high',
            'user': 'user1',
            'ip': '192.168.1.1'
        }
        
        result = self.security_monitor._create_security_alert(threat)
        
        self.assertTrue(result['created'])
        self.assertIn('alert_id', result)
        
        # Verify alert was created in database
        alert = Alert.objects.get(id=result['alert_id'])
        self.assertEqual(alert.alert_type, 'security_threat')
        self.assertEqual(alert.severity, 'high')
        self.assertIn('brute_force', alert.message)
    
    def test_create_security_alert_error(self):
        """Test security alert creation with error."""
        threat = {
            'type': 'invalid_threat',
            'severity': 'invalid_severity'
        }
        
        with self.assertRaises(ValueError):
            self.security_monitor._create_security_alert(threat)
    
    def test_check_unusual_login_patterns_success(self):
        """Test successful unusual login pattern detection."""
        logs = [
            {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
            {'event': 'login', 'user': 'user1', 'ip': '10.0.0.1', 'timestamp': timezone.now()},  # Different IP
            {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now() - timedelta(hours=3)}  # Unusual time
        ]
        
        result = self.security_monitor._check_unusual_login_patterns(logs)
        
        self.assertTrue(result['suspicious'])
        self.assertGreater(result['activities'], 0)
        self.assertIn('details', result)
    
    def test_check_unusual_login_patterns_not_suspicious(self):
        """Test unusual login pattern detection with normal patterns."""
        logs = [
            {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
            {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now() - timedelta(hours=1)}
        ]
        
        result = self.security_monitor._check_unusual_login_patterns(logs)
        
        self.assertFalse(result['suspicious'])
        self.assertEqual(result['activities'], 0)
    
    def test_check_privilege_escalation_success(self):
        """Test successful privilege escalation detection."""
        logs = [
            {'event': 'permission_granted', 'user': 'user1', 'permission': 'admin', 'timestamp': timezone.now()},
            {'event': 'permission_granted', 'user': 'user1', 'permission': 'superuser', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._check_privilege_escalation(logs)
        
        self.assertTrue(result['suspicious'])
        self.assertGreater(result['activities'], 0)
        self.assertIn('details', result)
    
    def test_check_privilege_escalation_not_suspicious(self):
        """Test privilege escalation detection with normal permissions."""
        logs = [
            {'event': 'permission_granted', 'user': 'user1', 'permission': 'read', 'timestamp': timezone.now()},
            {'event': 'permission_granted', 'user': 'user1', 'permission': 'write', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._check_privilege_escalation(logs)
        
        self.assertFalse(result['suspicious'])
        self.assertEqual(result['activities'], 0)
    
    def test_check_data_access_patterns_success(self):
        """Test successful data access pattern detection."""
        logs = [
            {'event': 'data_access', 'user': 'user1', 'table': 'users', 'action': 'select', 'timestamp': timezone.now()},
            {'event': 'data_access', 'user': 'user1', 'table': 'users', 'action': 'select', 'timestamp': timezone.now()},
            {'event': 'data_access', 'user': 'user1', 'table': 'users', 'action': 'select', 'timestamp': timezone.now()},
            {'event': 'data_access', 'user': 'user1', 'table': 'users', 'action': 'select', 'timestamp': timezone.now()},
            {'event': 'data_access', 'user': 'user1', 'table': 'users', 'action': 'select', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._check_data_access_patterns(logs)
        
        self.assertTrue(result['suspicious'])
        self.assertGreater(result['activities'], 0)
        self.assertIn('details', result)
    
    def test_check_data_access_patterns_not_suspicious(self):
        """Test data access pattern detection with normal patterns."""
        logs = [
            {'event': 'data_access', 'user': 'user1', 'table': 'users', 'action': 'select', 'timestamp': timezone.now()},
            {'event': 'data_access', 'user': 'user1', 'table': 'users', 'action': 'select', 'timestamp': timezone.now()}
        ]
        
        result = self.security_monitor._check_data_access_patterns(logs)
        
        self.assertFalse(result['suspicious'])
        self.assertEqual(result['activities'], 0)
    
    def test_get_security_logs_success(self):
        """Test successful security log retrieval."""
        with patch('apps.security.monitoring.AuditLog.objects.filter') as mock_filter:
            mock_logs = [
                {'event': 'login', 'user': 'user1', 'ip': '192.168.1.1', 'timestamp': timezone.now()},
                {'event': 'login', 'user': 'user2', 'ip': '192.168.1.2', 'timestamp': timezone.now()}
            ]
            mock_filter.return_value.values.return_value = mock_logs
            
            result = self.security_monitor._get_security_logs()
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['event'], 'login')
            self.assertEqual(result[1]['event'], 'login')
    
    def test_get_security_logs_error(self):
        """Test security log retrieval with error."""
        with patch('apps.security.monitoring.AuditLog.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database connection failed")
            
            with self.assertRaises(Exception):
                self.security_monitor._get_security_logs()
    
    def test_parse_log_entry_success(self):
        """Test successful log entry parsing."""
        log_entry = {
            'event': 'login',
            'user': 'user1',
            'ip': '192.168.1.1',
            'timestamp': timezone.now(),
            'details': {'success': True, 'method': 'password'}
        }
        
        result = self.security_monitor._parse_log_entry(log_entry)
        
        self.assertTrue(result['parsed'])
        self.assertEqual(result['event_type'], 'login')
        self.assertEqual(result['user'], 'user1')
        self.assertEqual(result['ip'], '192.168.1.1')
    
    def test_parse_log_entry_error(self):
        """Test log entry parsing with error."""
        log_entry = {
            'invalid': 'data'
        }
        
        result = self.security_monitor._parse_log_entry(log_entry)
        
        self.assertFalse(result['parsed'])
        self.assertIn('error', result)
    
    def test_generate_security_report_success(self):
        """Test successful security report generation."""
        with patch.object(self.security_monitor, 'detect_threats') as mock_detect:
            mock_detect.return_value = {
                'overall_risk_level': 'medium',
                'threats_detected': 2,
                'suspicious_activities': 1
            }
            
            with patch.object(self.security_monitor, 'analyze_logs') as mock_analyze:
                mock_analyze.return_value = {
                    'logs_analyzed': 100,
                    'analysis_summary': 'Normal activity detected'
                }
                
                result = self.security_monitor.generate_security_report()
                
                self.assertIn('report_id', result)
                self.assertIn('generated_at', result)
                self.assertIn('overall_risk_level', result)
                self.assertIn('threats_detected', result)
                self.assertIn('suspicious_activities', result)
                self.assertIn('logs_analyzed', result)
    
    def test_generate_security_report_error(self):
        """Test security report generation with error."""
        with patch.object(self.security_monitor, 'detect_threats') as mock_detect:
            mock_detect.side_effect = Exception("Threat detection failed")
            
            result = self.security_monitor.generate_security_report()
            
            self.assertIn('error', result)
            self.assertIn('Threat detection failed', result['error'])


# Export test classes
__all__ = [
    'SecurityMonitorTest'
]
