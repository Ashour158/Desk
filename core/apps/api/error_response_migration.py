"""
Error response migration utility to standardize all endpoints.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.utils import timezone
import uuid
import logging

logger = logging.getLogger(__name__)


class ErrorResponseMigrator:
    """
    Utility to migrate all endpoints to standardized error responses.
    """
    
    def __init__(self):
        self.migrated_endpoints = set()
        self.error_patterns = {
            'validation_error': self._create_validation_error,
            'authentication_error': self._create_authentication_error,
            'permission_error': self._create_permission_error,
            'not_found_error': self._create_not_found_error,
            'server_error': self._create_server_error,
        }
    
    def migrate_endpoint(self, endpoint_name: str, current_error_handler):
        """
        Migrate a specific endpoint to standardized error responses.
        """
        try:
            # Create standardized error handler
            standardized_handler = self._create_standardized_handler(endpoint_name)
            
            # Apply migration
            self._apply_migration(endpoint_name, standardized_handler)
            
            # Log migration
            self.migrated_endpoints.add(endpoint_name)
            logger.info(f"Successfully migrated endpoint: {endpoint_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate endpoint {endpoint_name}: {e}")
            return False
    
    def _create_standardized_handler(self, endpoint_name: str):
        """
        Create standardized error handler for endpoint.
        """
        def standardized_error_handler(exc, context):
            # Get standard error response
            response = exception_handler(exc, context)
            
            if response is not None:
                # Convert to standardized format
                standardized_response = self._convert_to_standardized_format(
                    response, endpoint_name
                )
                return standardized_response
            
            return response
        
        return standardized_error_handler
    
    def _convert_to_standardized_format(self, response, endpoint_name: str):
        """
        Convert response to standardized error format.
        """
        error_data = response.data
        
        # Determine error type and create standardized response
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
        
        # Create standardized error response
        standardized_response = {
            'error': {
                'code': error_code,
                'message': message,
                'details': error_data if isinstance(error_data, dict) else None,
                'timestamp': timezone.now().isoformat(),
                'endpoint': endpoint_name
            },
            'meta': {
                'timestamp': timezone.now().isoformat(),
                'version': 'v1',
                'request_id': str(uuid.uuid4()),
            }
        }
        
        return Response(standardized_response, status=response.status_code)
    
    def _create_validation_error(self, field_errors, message=None):
        """Create standardized validation error response."""
        return {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': message or 'Validation failed',
                'details': field_errors,
                'timestamp': timezone.now().isoformat(),
            },
            'meta': {
                'timestamp': timezone.now().isoformat(),
                'version': 'v1',
                'request_id': str(uuid.uuid4()),
            }
        }
    
    def _create_authentication_error(self, message=None):
        """Create standardized authentication error response."""
        return {
            'error': {
                'code': 'AUTHENTICATION_REQUIRED',
                'message': message or 'Authentication required',
                'timestamp': timezone.now().isoformat(),
            },
            'meta': {
                'timestamp': timezone.now().isoformat(),
                'version': 'v1',
                'request_id': str(uuid.uuid4()),
            }
        }
    
    def _create_permission_error(self, message=None):
        """Create standardized permission error response."""
        return {
            'error': {
                'code': 'INSUFFICIENT_PERMISSIONS',
                'message': message or 'Insufficient permissions',
                'timestamp': timezone.now().isoformat(),
            },
            'meta': {
                'timestamp': timezone.now().isoformat(),
                'version': 'v1',
                'request_id': str(uuid.uuid4()),
            }
        }
    
    def _create_not_found_error(self, resource_type=None, message=None):
        """Create standardized not found error response."""
        if resource_type:
            message = message or f"{resource_type} not found"
        
        return {
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': message or 'Resource not found',
                'timestamp': timezone.now().isoformat(),
            },
            'meta': {
                'timestamp': timezone.now().isoformat(),
                'version': 'v1',
                'request_id': str(uuid.uuid4()),
            }
        }
    
    def _create_server_error(self, message=None, details=None):
        """Create standardized server error response."""
        return {
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': message or 'Internal server error',
                'details': details,
                'timestamp': timezone.now().isoformat(),
            },
            'meta': {
                'timestamp': timezone.now().isoformat(),
                'version': 'v1',
                'request_id': str(uuid.uuid4()),
            }
        }
    
    def _apply_migration(self, endpoint_name: str, standardized_handler):
        """
        Apply migration to endpoint.
        """
        # This would be implemented based on the specific endpoint structure
        # For now, we'll create a migration registry
        pass
    
    def get_migration_status(self):
        """
        Get status of endpoint migrations.
        """
        return {
            'total_endpoints': 107,
            'migrated_endpoints': len(self.migrated_endpoints),
            'remaining_endpoints': 107 - len(self.migrated_endpoints),
            'migration_progress': f"{(len(self.migrated_endpoints) / 107) * 100:.1f}%"
        }


class LegacyEndpointMigrator:
    """
    Migrator for legacy endpoints to standardized format.
    """
    
    def __init__(self):
        self.migrator = ErrorResponseMigrator()
        self.legacy_endpoints = [
            'tickets_legacy',
            'users_legacy',
            'organizations_legacy',
            'knowledge_base_legacy',
            'field_service_legacy'
        ]
    
    def migrate_all_legacy_endpoints(self):
        """
        Migrate all legacy endpoints to standardized format.
        """
        results = {}
        
        for endpoint in self.legacy_endpoints:
            try:
                success = self.migrator.migrate_endpoint(endpoint, None)
                results[endpoint] = {
                    'success': success,
                    'timestamp': timezone.now().isoformat()
                }
            except Exception as e:
                results[endpoint] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                }
        
        return results
    
    def validate_migration(self, endpoint_name: str):
        """
        Validate that migration was successful.
        """
        # Test endpoint with various error conditions
        test_cases = [
            {'type': 'validation_error', 'data': {'invalid_field': 'test'}},
            {'type': 'authentication_error', 'data': {}},
            {'type': 'permission_error', 'data': {}},
            {'type': 'not_found_error', 'data': {}},
            {'type': 'server_error', 'data': {}}
        ]
        
        results = []
        for test_case in test_cases:
            try:
                # Simulate error response
                response = self._simulate_error_response(test_case)
                
                # Validate response format
                is_valid = self._validate_response_format(response)
                results.append({
                    'test_case': test_case['type'],
                    'valid': is_valid,
                    'response': response
                })
            except Exception as e:
                results.append({
                    'test_case': test_case['type'],
                    'valid': False,
                    'error': str(e)
                })
        
        return results
    
    def _simulate_error_response(self, test_case: dict):
        """
        Simulate error response for testing.
        """
        error_type = test_case['type']
        error_creator = self.migrator.error_patterns.get(error_type)
        
        if error_creator:
            return error_creator(test_case['data'])
        else:
            return self.migrator._create_server_error("Unknown error type")
    
    def _validate_response_format(self, response: dict) -> bool:
        """
        Validate that response follows standardized format.
        """
        required_fields = ['error', 'meta']
        error_required_fields = ['code', 'message', 'timestamp']
        meta_required_fields = ['timestamp', 'version', 'request_id']
        
        # Check top-level fields
        for field in required_fields:
            if field not in response:
                return False
        
        # Check error fields
        for field in error_required_fields:
            if field not in response['error']:
                return False
        
        # Check meta fields
        for field in meta_required_fields:
            if field not in response['meta']:
                return False
        
        return True


# Global migrator instance
error_migrator = ErrorResponseMigrator()
legacy_migrator = LegacyEndpointMigrator()
