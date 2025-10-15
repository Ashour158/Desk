"""
Global Error Handler Middleware
Comprehensive error handling for the entire application
"""

import logging
import traceback
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
import json

logger = logging.getLogger(__name__)


class GlobalErrorMiddleware:
    """
    Global error handling middleware
    Catches and handles all unhandled exceptions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return self.handle_exception(request, e)
    
    def handle_exception(self, request, exception):
        """Handle unhandled exceptions"""
        try:
            # Log the exception
            logger.error(f"Unhandled exception: {exception}", exc_info=True)
            
            # Get error details
            error_details = self.get_error_details(exception)
            
            # Create error response
            error_response = {
                'error': {
                    'type': error_details['type'],
                    'message': error_details['message'],
                    'code': error_details['code'],
                    'timestamp': timezone.now().isoformat(),
                    'request_id': getattr(request, 'request_id', None),
                    'path': request.path,
                    'method': request.method
                }
            }
            
            # Add debug information in development
            if settings.DEBUG:
                error_response['error']['debug'] = {
                    'exception': str(exception),
                    'traceback': traceback.format_exc()
                }
            
            # Return appropriate response
            return JsonResponse(
                error_response,
                status=error_details['status_code'],
                content_type='application/json'
            )
            
        except Exception as handler_error:
            # If error handling itself fails, return basic error
            logger.critical(f"Error handler failed: {handler_error}")
            return JsonResponse({
                'error': {
                    'type': 'InternalServerError',
                    'message': 'An internal server error occurred',
                    'code': 'HANDLER_ERROR',
                    'timestamp': timezone.now().isoformat()
                }
            }, status=500)
    
    def get_error_details(self, exception):
        """Get error details based on exception type"""
        error_mapping = {
            ValidationError: {
                'type': 'ValidationError',
                'message': 'Invalid data provided',
                'code': 'VALIDATION_ERROR',
                'status_code': 400
            },
            PermissionDenied: {
                'type': 'PermissionDenied',
                'message': 'You do not have permission to perform this action',
                'code': 'PERMISSION_DENIED',
                'status_code': 403
            },
            FileNotFoundError: {
                'type': 'FileNotFoundError',
                'message': 'Requested file not found',
                'code': 'FILE_NOT_FOUND',
                'status_code': 404
            },
            ConnectionError: {
                'type': 'ConnectionError',
                'message': 'Unable to connect to external service',
                'code': 'CONNECTION_ERROR',
                'status_code': 503
            },
            TimeoutError: {
                'type': 'TimeoutError',
                'message': 'Request timeout',
                'code': 'TIMEOUT_ERROR',
                'status_code': 504
            }
        }
        
        # Get error details from mapping
        error_details = error_mapping.get(type(exception), {
            'type': 'InternalServerError',
            'message': 'An internal server error occurred',
            'code': 'INTERNAL_ERROR',
            'status_code': 500
        })
        
        # Customize message if available
        if hasattr(exception, 'message'):
            error_details['message'] = str(exception.message)
        elif str(exception):
            error_details['message'] = str(exception)
        
        return error_details


def drf_exception_handler(exc, context):
    """
    Custom DRF exception handler
    Provides consistent error responses for DRF views
    """
    # Get default DRF response
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize error response
        custom_response_data = {
            'error': {
                'type': get_exception_type(exc),
                'message': get_exception_message(exc),
                'code': get_exception_code(exc),
                'timestamp': timezone.now().isoformat(),
                'path': context.get('request').path if context.get('request') else None,
                'method': context.get('request').method if context.get('request') else None
            }
        }
        
        # Add field errors if available
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            custom_response_data['error']['field_errors'] = exc.detail
        
        # Add debug information in development
        if settings.DEBUG:
            custom_response_data['error']['debug'] = {
                'exception': str(exc),
                'traceback': traceback.format_exc()
            }
        
        response.data = custom_response_data
    
    return response


def get_exception_type(exc):
    """Get exception type name"""
    return exc.__class__.__name__


def get_exception_message(exc):
    """Get exception message"""
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            return 'Validation error'
        return str(exc.detail)
    return str(exc)


def get_exception_code(exc):
    """Get exception code"""
    if hasattr(exc, 'default_code'):
        return exc.default_code
    return exc.__class__.__name__.upper()


class APIErrorResponse:
    """Standardized API error response"""
    
    @staticmethod
    def validation_error(message, field_errors=None):
        """Create validation error response"""
        return Response({
            'error': {
                'type': 'ValidationError',
                'message': message,
                'code': 'VALIDATION_ERROR',
                'field_errors': field_errors,
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def permission_denied(message="Permission denied"):
        """Create permission denied response"""
        return Response({
            'error': {
                'type': 'PermissionDenied',
                'message': message,
                'code': 'PERMISSION_DENIED',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def not_found(message="Resource not found"):
        """Create not found response"""
        return Response({
            'error': {
                'type': 'NotFound',
                'message': message,
                'code': 'NOT_FOUND',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def server_error(message="Internal server error"):
        """Create server error response"""
        return Response({
            'error': {
                'type': 'InternalServerError',
                'message': message,
                'code': 'INTERNAL_ERROR',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def service_unavailable(message="Service temporarily unavailable"):
        """Create service unavailable response"""
        return Response({
            'error': {
                'type': 'ServiceUnavailable',
                'message': message,
                'code': 'SERVICE_UNAVAILABLE',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class ErrorLogger:
    """Centralized error logging"""
    
    @staticmethod
    def log_error(error, request=None, context=None):
        """Log error with context"""
        error_data = {
            'error': str(error),
            'type': type(error).__name__,
            'timestamp': timezone.now().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        if request:
            error_data['request'] = {
                'path': request.path,
                'method': request.method,
                'user': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'ip': get_client_ip(request)
            }
        
        if context:
            error_data['context'] = context
        
        logger.error(f"Application error: {json.dumps(error_data, indent=2)}")
    
    @staticmethod
    def log_warning(message, request=None, context=None):
        """Log warning with context"""
        warning_data = {
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
        
        if request:
            warning_data['request'] = {
                'path': request.path,
                'method': request.method,
                'user': getattr(request.user, 'id', None) if hasattr(request, 'user') else None
            }
        
        if context:
            warning_data['context'] = context
        
        logger.warning(f"Application warning: {json.dumps(warning_data, indent=2)}")


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Export commonly used functions
__all__ = [
    'GlobalErrorMiddleware',
    'drf_exception_handler',
    'APIErrorResponse',
    'ErrorLogger'
]