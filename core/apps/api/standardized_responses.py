"""
Standardized error responses with meta information and response versioning.
"""

from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings
import uuid
import logging

logger = logging.getLogger(__name__)


class StandardizedResponse:
    """
    Standardized response format for all API endpoints.
    """
    
    def __init__(self, version='v1'):
        self.version = version
    
    def success_response(self, data=None, message=None, status_code=status.HTTP_200_OK, **kwargs):
        """
        Create standardized success response.
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            **kwargs: Additional response data
            
        Returns:
            Response: Standardized success response
        """
        response_data = {
            'data': data,
            'message': message,
            'meta': self._get_meta(),
            **kwargs
        }
        
        return Response(response_data, status=status_code)
    
    def error_response(self, error_code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
        """
        Create standardized error response.
        
        Args:
            error_code: Error code
            message: Error message
            details: Error details
            status_code: HTTP status code
            **kwargs: Additional response data
            
        Returns:
            Response: Standardized error response
        """
        response_data = {
            'error': {
                'code': error_code,
                'message': message,
                'details': details,
                'timestamp': timezone.now().isoformat(),
            },
            'meta': self._get_meta(),
            **kwargs
        }
        
        return Response(response_data, status=status_code)
    
    def paginated_response(self, data, pagination_info, message=None, **kwargs):
        """
        Create standardized paginated response.
        
        Args:
            data: Response data
            pagination_info: Pagination information
            message: Success message
            **kwargs: Additional response data
            
        Returns:
            Response: Standardized paginated response
        """
        response_data = {
            'data': data,
            'pagination': pagination_info,
            'message': message,
            'meta': self._get_meta(),
            **kwargs
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _get_meta(self):
        """
        Get standardized meta information.
        
        Returns:
            dict: Meta information
        """
        return {
            'timestamp': timezone.now().isoformat(),
            'version': self.version,
            'request_id': str(uuid.uuid4()),
            'api_version': getattr(settings, 'API_VERSION', 'v1'),
        }


class ErrorResponseManager:
    """
    Manager for standardized error responses.
    """
    
    # Standard error codes
    ERROR_CODES = {
        'VALIDATION_ERROR': 'VALIDATION_ERROR',
        'AUTHENTICATION_REQUIRED': 'AUTHENTICATION_REQUIRED',
        'INSUFFICIENT_PERMISSIONS': 'INSUFFICIENT_PERMISSIONS',
        'RESOURCE_NOT_FOUND': 'RESOURCE_NOT_FOUND',
        'RESOURCE_ALREADY_EXISTS': 'RESOURCE_ALREADY_EXISTS',
        'RATE_LIMIT_EXCEEDED': 'RATE_LIMIT_EXCEEDED',
        'FILE_UPLOAD_ERROR': 'FILE_UPLOAD_ERROR',
        'INTERNAL_SERVER_ERROR': 'INTERNAL_SERVER_ERROR',
        'SERVICE_UNAVAILABLE': 'SERVICE_UNAVAILABLE',
        'INVALID_REQUEST': 'INVALID_REQUEST',
        'CONFLICT': 'CONFLICT',
        'FORBIDDEN': 'FORBIDDEN',
        'METHOD_NOT_ALLOWED': 'METHOD_NOT_ALLOWED',
        'UNSUPPORTED_MEDIA_TYPE': 'UNSUPPORTED_MEDIA_TYPE',
        'REQUEST_ENTITY_TOO_LARGE': 'REQUEST_ENTITY_TOO_LARGE',
        'TOO_MANY_REQUESTS': 'TOO_MANY_REQUESTS',
    }
    
    # Error messages
    ERROR_MESSAGES = {
        'VALIDATION_ERROR': 'Validation failed',
        'AUTHENTICATION_REQUIRED': 'Authentication required',
        'INSUFFICIENT_PERMISSIONS': 'Insufficient permissions',
        'RESOURCE_NOT_FOUND': 'Resource not found',
        'RESOURCE_ALREADY_EXISTS': 'Resource already exists',
        'RATE_LIMIT_EXCEEDED': 'Rate limit exceeded',
        'FILE_UPLOAD_ERROR': 'File upload failed',
        'INTERNAL_SERVER_ERROR': 'Internal server error',
        'SERVICE_UNAVAILABLE': 'Service unavailable',
        'INVALID_REQUEST': 'Invalid request',
        'CONFLICT': 'Resource conflict',
        'FORBIDDEN': 'Access forbidden',
        'METHOD_NOT_ALLOWED': 'Method not allowed',
        'UNSUPPORTED_MEDIA_TYPE': 'Unsupported media type',
        'REQUEST_ENTITY_TOO_LARGE': 'Request entity too large',
        'TOO_MANY_REQUESTS': 'Too many requests',
    }
    
    # HTTP status code mapping
    STATUS_CODE_MAPPING = {
        'VALIDATION_ERROR': status.HTTP_400_BAD_REQUEST,
        'AUTHENTICATION_REQUIRED': status.HTTP_401_UNAUTHORIZED,
        'INSUFFICIENT_PERMISSIONS': status.HTTP_403_FORBIDDEN,
        'RESOURCE_NOT_FOUND': status.HTTP_404_NOT_FOUND,
        'RESOURCE_ALREADY_EXISTS': status.HTTP_409_CONFLICT,
        'RATE_LIMIT_EXCEEDED': status.HTTP_429_TOO_MANY_REQUESTS,
        'FILE_UPLOAD_ERROR': status.HTTP_400_BAD_REQUEST,
        'INTERNAL_SERVER_ERROR': status.HTTP_500_INTERNAL_SERVER_ERROR,
        'SERVICE_UNAVAILABLE': status.HTTP_503_SERVICE_UNAVAILABLE,
        'INVALID_REQUEST': status.HTTP_400_BAD_REQUEST,
        'CONFLICT': status.HTTP_409_CONFLICT,
        'FORBIDDEN': status.HTTP_403_FORBIDDEN,
        'METHOD_NOT_ALLOWED': status.HTTP_405_METHOD_NOT_ALLOWED,
        'UNSUPPORTED_MEDIA_TYPE': status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        'REQUEST_ENTITY_TOO_LARGE': status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        'TOO_MANY_REQUESTS': status.HTTP_429_TOO_MANY_REQUESTS,
    }
    
    def __init__(self):
        self.response_handler = StandardizedResponse()
    
    def validation_error(self, field_errors, message=None):
        """
        Create validation error response.
        
        Args:
            field_errors: Field-specific validation errors
            message: Custom error message
            
        Returns:
            Response: Validation error response
        """
        return self.response_handler.error_response(
            error_code=self.ERROR_CODES['VALIDATION_ERROR'],
            message=message or self.ERROR_MESSAGES['VALIDATION_ERROR'],
            details=field_errors,
            status_code=self.STATUS_CODE_MAPPING['VALIDATION_ERROR']
        )
    
    def authentication_required(self, message=None):
        """
        Create authentication required error response.
        
        Args:
            message: Custom error message
            
        Returns:
            Response: Authentication error response
        """
        return self.response_handler.error_response(
            error_code=self.ERROR_CODES['AUTHENTICATION_REQUIRED'],
            message=message or self.ERROR_MESSAGES['AUTHENTICATION_REQUIRED'],
            status_code=self.STATUS_CODE_MAPPING['AUTHENTICATION_REQUIRED']
        )
    
    def insufficient_permissions(self, message=None):
        """
        Create insufficient permissions error response.
        
        Args:
            message: Custom error message
            
        Returns:
            Response: Permission error response
        """
        return self.response_handler.error_response(
            error_code=self.ERROR_CODES['INSUFFICIENT_PERMISSIONS'],
            message=message or self.ERROR_MESSAGES['INSUFFICIENT_PERMISSIONS'],
            status_code=self.STATUS_CODE_MAPPING['INSUFFICIENT_PERMISSIONS']
        )
    
    def resource_not_found(self, resource_type=None, message=None):
        """
        Create resource not found error response.
        
        Args:
            resource_type: Type of resource not found
            message: Custom error message
            
        Returns:
            Response: Not found error response
        """
        if resource_type:
            message = message or f"{resource_type} not found"
        
        return self.response_handler.error_response(
            error_code=self.ERROR_CODES['RESOURCE_NOT_FOUND'],
            message=message or self.ERROR_MESSAGES['RESOURCE_NOT_FOUND'],
            status_code=self.STATUS_CODE_MAPPING['RESOURCE_NOT_FOUND']
        )
    
    def resource_already_exists(self, resource_type=None, message=None):
        """
        Create resource already exists error response.
        
        Args:
            resource_type: Type of resource that already exists
            message: Custom error message
            
        Returns:
            Response: Conflict error response
        """
        if resource_type:
            message = message or f"{resource_type} already exists"
        
        return self.response_handler.error_response(
            error_code=self.ERROR_CODES['RESOURCE_ALREADY_EXISTS'],
            message=message or self.ERROR_MESSAGES['RESOURCE_ALREADY_EXISTS'],
            status_code=self.STATUS_CODE_MAPPING['RESOURCE_ALREADY_EXISTS']
        )
    
    def rate_limit_exceeded(self, limit=None, reset_time=None, message=None):
        """
        Create rate limit exceeded error response.
        
        Args:
            limit: Rate limit value
            reset_time: Time when limit resets
            message: Custom error message
            
        Returns:
            Response: Rate limit error response
        """
        details = {}
        if limit:
            details['limit'] = limit
        if reset_time:
            details['reset_time'] = reset_time
        
        return self.response_handler.error_response(
            error_code=self.ERROR_CODES['RATE_LIMIT_EXCEEDED'],
            message=message or self.ERROR_MESSAGES['RATE_LIMIT_EXCEEDED'],
            details=details,
            status_code=self.STATUS_CODE_MAPPING['RATE_LIMIT_EXCEEDED']
        )
    
    def file_upload_error(self, file_errors, message=None):
        """
        Create file upload error response.
        
        Args:
            file_errors: File-specific errors
            message: Custom error message
            
        Returns:
            Response: File upload error response
        """
        return self.response_handler.error_response(
            error_code=self.ERROR_CODES['FILE_UPLOAD_ERROR'],
            message=message or self.ERROR_MESSAGES['FILE_UPLOAD_ERROR'],
            details=file_errors,
            status_code=self.STATUS_CODE_MAPPING['FILE_UPLOAD_ERROR']
        )
    
    def internal_server_error(self, message=None, details=None):
        """
        Create internal server error response.
        
        Args:
            message: Custom error message
            details: Error details
            
        Returns:
            Response: Internal server error response
        """
        return self.response_handler.error_response(
            error_code=self.ERROR_CODES['INTERNAL_SERVER_ERROR'],
            message=message or self.ERROR_MESSAGES['INTERNAL_SERVER_ERROR'],
            details=details,
            status_code=self.STATUS_CODE_MAPPING['INTERNAL_SERVER_ERROR']
        )
    
    def custom_error(self, error_code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Create custom error response.
        
        Args:
            error_code: Custom error code
            message: Error message
            details: Error details
            status_code: HTTP status code
            
        Returns:
            Response: Custom error response
        """
        return self.response_handler.error_response(
            error_code=error_code,
            message=message,
            details=details,
            status_code=status_code
        )


class ResponseVersioning:
    """
    Handle API response versioning.
    """
    
    def __init__(self, current_version='v1'):
        self.current_version = current_version
        self.supported_versions = ['v1']
    
    def get_version_from_request(self, request):
        """
        Get API version from request.
        
        Args:
            request: HTTP request
            
        Returns:
            str: API version
        """
        # Check Accept header
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'application/vnd.helpdesk.v' in accept_header:
            version = accept_header.split('application/vnd.helpdesk.v')[1].split('+')[0]
            if version in self.supported_versions:
                return version
        
        # Check query parameter
        version = request.GET.get('version')
        if version in self.supported_versions:
            return version
        
        # Default to current version
        return self.current_version
    
    def format_response_for_version(self, data, version):
        """
        Format response data for specific version.
        
        Args:
            data: Response data
            version: API version
            
        Returns:
            dict: Versioned response data
        """
        if version == 'v1':
            return self._format_v1_response(data)
        
        # Default to current version
        return self._format_v1_response(data)
    
    def _format_v1_response(self, data):
        """
        Format response for v1 API.
        
        Args:
            data: Response data
            
        Returns:
            dict: v1 formatted response
        """
        return {
            'data': data,
            'meta': {
                'version': 'v1',
                'timestamp': timezone.now().isoformat(),
            }
        }


class APIResponseMixin:
    """
    Mixin for views to provide standardized responses.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_handler = StandardizedResponse()
        self.error_manager = ErrorResponseManager()
        self.versioning = ResponseVersioning()
    
    def success_response(self, data=None, message=None, status_code=status.HTTP_200_OK, **kwargs):
        """
        Create standardized success response.
        """
        return self.response_handler.success_response(
            data=data,
            message=message,
            status_code=status_code,
            **kwargs
        )
    
    def error_response(self, error_code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
        """
        Create standardized error response.
        """
        return self.response_handler.error_response(
            error_code=error_code,
            message=message,
            details=details,
            status_code=status_code,
            **kwargs
        )
    
    def validation_error(self, field_errors, message=None):
        """
        Create validation error response.
        """
        return self.error_manager.validation_error(field_errors, message)
    
    def authentication_required(self, message=None):
        """
        Create authentication required error response.
        """
        return self.error_manager.authentication_required(message)
    
    def insufficient_permissions(self, message=None):
        """
        Create insufficient permissions error response.
        """
        return self.error_manager.insufficient_permissions(message)
    
    def resource_not_found(self, resource_type=None, message=None):
        """
        Create resource not found error response.
        """
        return self.error_manager.resource_not_found(resource_type, message)
    
    def resource_already_exists(self, resource_type=None, message=None):
        """
        Create resource already exists error response.
        """
        return self.error_manager.resource_already_exists(resource_type, message)
    
    def rate_limit_exceeded(self, limit=None, reset_time=None, message=None):
        """
        Create rate limit exceeded error response.
        """
        return self.error_manager.rate_limit_exceeded(limit, reset_time, message)
    
    def file_upload_error(self, file_errors, message=None):
        """
        Create file upload error response.
        """
        return self.error_manager.file_upload_error(file_errors, message)
    
    def internal_server_error(self, message=None, details=None):
        """
        Create internal server error response.
        """
        return self.error_manager.internal_server_error(message, details)


# Global error response manager instance
error_manager = ErrorResponseManager()

# Global response handler instance
response_handler = StandardizedResponse()


def custom_exception_handler(exc, context):
    """
    Custom exception handler for standardized error responses.
    """
    from rest_framework.views import exception_handler
    from rest_framework import status
    
    # Get the standard error response
    response = exception_handler(exc, context)
    
    if response is not None:
        # Create standardized error response
        error_data = response.data
        
        # Determine error code and message
        if isinstance(error_data, dict):
            if 'detail' in error_data:
                error_code = 'INVALID_REQUEST'
                message = str(error_data['detail'])
            elif 'non_field_errors' in error_data:
                error_code = 'VALIDATION_ERROR'
                message = str(error_data['non_field_errors'][0]) if error_data['non_field_errors'] else 'Validation failed'
            else:
                error_code = 'VALIDATION_ERROR'
                message = 'Validation failed'
        else:
            error_code = 'INVALID_REQUEST'
            message = str(error_data)
        
        # Create standardized response
        standardized_response = error_manager.custom_error(
            error_code=error_code,
            message=message,
            details=error_data if isinstance(error_data, dict) else None,
            status_code=response.status_code
        )
        
        return standardized_response
    
    return response
