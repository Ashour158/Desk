"""
Enhanced Logging System for Django Backend
Comprehensive logging with data sanitization, structured logging, and external service integration
"""

import json
import logging
import logging.handlers
import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone as django_timezone
from django.core.cache import cache
import uuid


class SensitiveDataFilter(logging.Filter):
    """
    Filter to sanitize sensitive data from log records
    """
    
    # Sensitive field patterns
    SENSITIVE_PATTERNS = [
        r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'secret["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'key["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'authorization["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'api_key["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'access_token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'refresh_token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'session_id["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
        r'csrf_token["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
    ]
    
    # Credit card patterns
    CREDIT_CARD_PATTERNS = [
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        r'\b\d{13,19}\b',
    ]
    
    # SSN patterns
    SSN_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',
        r'\b\d{9}\b',
    ]
    
    def filter(self, record):
        """Filter and sanitize log record"""
        if hasattr(record, 'msg'):
            record.msg = self.sanitize_data(str(record.msg))
        
        if hasattr(record, 'args'):
            record.args = tuple(self.sanitize_data(str(arg)) for arg in record.args)
        
        return True
    
    def sanitize_data(self, data: str) -> str:
        """Sanitize sensitive data from string"""
        if not isinstance(data, str):
            return data
        
        # Replace sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            data = re.sub(pattern, r'\1=***REDACTED***', data, flags=re.IGNORECASE)
        
        # Replace credit card numbers
        for pattern in self.CREDIT_CARD_PATTERNS:
            data = re.sub(pattern, '***REDACTED***', data)
        
        # Replace SSNs
        for pattern in self.SSN_PATTERNS:
            data = re.sub(pattern, '***REDACTED***', data)
        
        return data


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    """
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread,
            'request_id': getattr(record, 'request_id', None),
            'user_id': getattr(record, 'user_id', None),
            'session_id': getattr(record, 'session_id', None),
            'ip_address': getattr(record, 'ip_address', None),
            'user_agent': getattr(record, 'user_agent', None),
            'url': getattr(record, 'url', None),
            'method': getattr(record, 'method', None),
            'status_code': getattr(record, 'status_code', None),
            'duration': getattr(record, 'duration', None),
            'context': getattr(record, 'context', {}),
            'exception': self.format_exception(record) if record.exc_info else None,
        }
        
        # Add custom fields
        for key, value in record.__dict__.items():
            if key not in log_entry and not key.startswith('_'):
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)
    
    def format_exception(self, record):
        """Format exception information"""
        if record.exc_info:
            return {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        return None


class EnhancedLoggingHandler(logging.Handler):
    """
    Enhanced logging handler with external service integration
    """
    
    def __init__(self, external_service=None):
        super().__init__()
        self.external_service = external_service
        self.log_buffer = []
        self.buffer_size = 100
        self.flush_interval = 30  # seconds
    
    def emit(self, record):
        """Emit log record"""
        try:
            # Add to buffer
            self.log_buffer.append(self.format(record))
            
            # Flush if buffer is full
            if len(self.log_buffer) >= self.buffer_size:
                self.flush()
            
            # Send to external service for critical errors
            if record.levelno >= logging.ERROR:
                self.send_to_external_service(record)
                
        except Exception as e:
            # Fallback to console if logging fails
            print(f"Logging error: {e}")
    
    def flush(self):
        """Flush log buffer"""
        if self.log_buffer:
            # Send to external service
            if self.external_service:
                self.external_service.send_logs(self.log_buffer)
            
            # Clear buffer
            self.log_buffer.clear()
    
    def send_to_external_service(self, record):
        """Send critical logs to external service"""
        if not self.external_service:
            return
        
        try:
            log_data = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'message': record.getMessage(),
                'context': getattr(record, 'context', {}),
                'exception': self.format_exception(record) if record.exc_info else None,
            }
            
            self.external_service.send_critical_log(log_data)
        except Exception as e:
            print(f"External service error: {e}")


class PerformanceLogger:
    """
    Performance logging utility
    """
    
    def __init__(self, logger_name='performance'):
        self.logger = logging.getLogger(logger_name)
    
    def log_request(self, request, response, duration):
        """Log HTTP request performance"""
        self.logger.info(
            f"Request completed: {request.method} {request.path}",
            extra={
                'request_id': getattr(request, 'request_id', None),
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'url': request.get_full_path(),
                'method': request.method,
                'status_code': response.status_code,
                'duration': duration,
                'context': {
                    'request_size': len(request.body) if hasattr(request, 'body') else 0,
                    'response_size': len(response.content) if hasattr(response, 'content') else 0,
                }
            }
        )
    
    def log_database_query(self, query, duration, params=None):
        """Log database query performance"""
        self.logger.info(
            f"Database query executed: {query[:100]}...",
            extra={
                'query': query,
                'duration': duration,
                'params': params,
                'context': {
                    'query_type': self.get_query_type(query),
                    'table_name': self.get_table_name(query),
                }
            }
        )
    
    def log_api_call(self, url, method, status_code, duration, response_size=None):
        """Log external API call performance"""
        self.logger.info(
            f"API call completed: {method} {url}",
            extra={
                'url': url,
                'method': method,
                'status_code': status_code,
                'duration': duration,
                'response_size': response_size,
                'context': {
                    'api_type': 'external',
                    'success': 200 <= status_code < 300,
                }
            }
        )
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def get_query_type(self, query):
        """Get SQL query type"""
        query_upper = query.upper().strip()
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        return 'OTHER'
    
    def get_table_name(self, query):
        """Extract table name from query"""
        # Simple regex to extract table name
        match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if match:
            return match.group(1)
        return None


class SecurityLogger:
    """
    Security event logging utility
    """
    
    def __init__(self, logger_name='security'):
        self.logger = logging.getLogger(logger_name)
    
    def log_authentication(self, user, success, ip_address, user_agent, context=None):
        """Log authentication events"""
        self.logger.info(
            f"Authentication {'successful' if success else 'failed'}: {user}",
            extra={
                'user_id': getattr(user, 'id', None) if user else None,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'success': success,
                'context': context or {},
                'event_type': 'authentication',
            }
        )
    
    def log_authorization(self, user, resource, action, success, ip_address, context=None):
        """Log authorization events"""
        self.logger.info(
            f"Authorization {'granted' if success else 'denied'}: {user} -> {action} on {resource}",
            extra={
                'user_id': getattr(user, 'id', None) if user else None,
                'resource': resource,
                'action': action,
                'success': success,
                'ip_address': ip_address,
                'context': context or {},
                'event_type': 'authorization',
            }
        )
    
    def log_security_event(self, event_type, description, severity, ip_address, user=None, context=None):
        """Log security events"""
        self.logger.warning(
            f"Security event: {event_type} - {description}",
            extra={
                'user_id': getattr(user, 'id', None) if user else None,
                'ip_address': ip_address,
                'event_type': event_type,
                'description': description,
                'severity': severity,
                'context': context or {},
            }
        )
    
    def log_threat_detection(self, threat_type, description, ip_address, user_agent, context=None):
        """Log threat detection events"""
        self.logger.error(
            f"Threat detected: {threat_type} - {description}",
            extra={
                'ip_address': ip_address,
                'user_agent': user_agent,
                'threat_type': threat_type,
                'description': description,
                'context': context or {},
                'event_type': 'threat_detection',
            }
        )


class ComplianceLogger:
    """
    Compliance logging utility for audit trails
    """
    
    def __init__(self, logger_name='compliance'):
        self.logger = logging.getLogger(logger_name)
    
    def log_data_access(self, user, data_type, action, record_id, ip_address, context=None):
        """Log data access for compliance"""
        self.logger.info(
            f"Data access: {user} {action} {data_type} record {record_id}",
            extra={
                'user_id': getattr(user, 'id', None) if user else None,
                'data_type': data_type,
                'action': action,
                'record_id': record_id,
                'ip_address': ip_address,
                'context': context or {},
                'event_type': 'data_access',
                'compliance_required': True,
            }
        )
    
    def log_data_modification(self, user, data_type, action, record_id, old_values, new_values, ip_address, context=None):
        """Log data modifications for compliance"""
        self.logger.info(
            f"Data modification: {user} {action} {data_type} record {record_id}",
            extra={
                'user_id': getattr(user, 'id', None) if user else None,
                'data_type': data_type,
                'action': action,
                'record_id': record_id,
                'old_values': old_values,
                'new_values': new_values,
                'ip_address': ip_address,
                'context': context or {},
                'event_type': 'data_modification',
                'compliance_required': True,
            }
        )
    
    def log_user_activity(self, user, activity, ip_address, user_agent, context=None):
        """Log user activities for compliance"""
        self.logger.info(
            f"User activity: {user} {activity}",
            extra={
                'user_id': getattr(user, 'id', None) if user else None,
                'activity': activity,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'context': context or {},
                'event_type': 'user_activity',
                'compliance_required': True,
            }
        )


class LoggingConfiguration:
    """
    Enhanced logging configuration
    """
    
    @staticmethod
    def get_enhanced_logging_config():
        """Get enhanced logging configuration"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                    'style': '{',
                },
                'json': {
                    '()': JSONFormatter,
                },
                'simple': {
                    'format': '{levelname} {message}',
                    'style': '{',
                },
            },
            'filters': {
                'sensitive_data': {
                    '()': SensitiveDataFilter,
                },
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                    'filters': ['sensitive_data'],
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/django.log',
                    'maxBytes': 50 * 1024 * 1024,  # 50MB
                    'backupCount': 20,
                    'formatter': 'json',
                    'filters': ['sensitive_data'],
                },
                'error_file': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/error.log',
                    'maxBytes': 50 * 1024 * 1024,  # 50MB
                    'backupCount': 20,
                    'formatter': 'json',
                    'filters': ['sensitive_data'],
                },
                'security_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/security.log',
                    'maxBytes': 50 * 1024 * 1024,  # 50MB
                    'backupCount': 20,
                    'formatter': 'json',
                    'filters': ['sensitive_data'],
                },
                'performance_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/performance.log',
                    'maxBytes': 50 * 1024 * 1024,  # 50MB
                    'backupCount': 20,
                    'formatter': 'json',
                    'filters': ['sensitive_data'],
                },
                'compliance_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/compliance.log',
                    'maxBytes': 50 * 1024 * 1024,  # 50MB
                    'backupCount': 20,
                    'formatter': 'json',
                    'filters': ['sensitive_data'],
                },
            },
            'root': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
            'loggers': {
                'django': {
                    'handlers': ['console', 'file'],
                    'level': 'INFO',
                    'propagate': False,
                },
                'apps': {
                    'handlers': ['console', 'file'],
                    'level': 'DEBUG',
                    'propagate': False,
                },
                'security': {
                    'handlers': ['console', 'security_file'],
                    'level': 'INFO',
                    'propagate': False,
                },
                'performance': {
                    'handlers': ['console', 'performance_file'],
                    'level': 'INFO',
                    'propagate': False,
                },
                'compliance': {
                    'handlers': ['console', 'compliance_file'],
                    'level': 'INFO',
                    'propagate': False,
                },
            },
        }


# Global logger instances
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()
compliance_logger = ComplianceLogger()

# Export utilities
__all__ = [
    'SensitiveDataFilter',
    'JSONFormatter',
    'EnhancedLoggingHandler',
    'PerformanceLogger',
    'SecurityLogger',
    'ComplianceLogger',
    'LoggingConfiguration',
    'performance_logger',
    'security_logger',
    'compliance_logger',
]
