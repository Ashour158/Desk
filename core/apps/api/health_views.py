"""
Health Check API Views
Comprehensive health check endpoints for monitoring and diagnostics
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from django.utils import timezone
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import logging
import psutil
import requests
import time

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check endpoint
    Returns system status and basic information
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {e}")

    # Check cache connectivity
    try:
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        cache_status = "healthy" if cache_result == 'ok' else "unhealthy"
    except Exception as e:
        cache_status = f"unhealthy: {str(e)}"
        logger.error(f"Cache health check failed: {e}")

    # Check system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_status = "healthy"
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 95:
            system_status = "degraded"
    except Exception as e:
        system_status = f"unhealthy: {str(e)}"
        logger.error(f"System health check failed: {e}")

    # Overall status
    overall_status = "healthy"
    if "unhealthy" in db_status or "unhealthy" in cache_status or "unhealthy" in system_status:
        overall_status = "unhealthy"
    elif "degraded" in system_status:
        overall_status = "degraded"

    response_data = {
        'status': overall_status,
        'timestamp': timezone.now().isoformat(),
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': getattr(settings, 'ENVIRONMENT', 'development'),
        'services': {
            'database': db_status,
            'cache': cache_status,
            'system': system_status
        }
    }

    status_code = 200 if overall_status == "healthy" else 503
    return Response(response_data, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def detailed_health_check(request):
    """
    Detailed health check endpoint
    Returns comprehensive system information
    """
    try:
        # Database health
        db_health = check_database_health()
        
        # Cache health
        cache_health = check_cache_health()
        
        # System health
        system_health = check_system_health()
        
        # External services health
        external_health = check_external_services_health()
        
        # Overall health assessment
        overall_health = assess_overall_health({
            'database': db_health,
            'cache': cache_health,
            'system': system_health,
            'external': external_health
        })
        
        response_data = {
            'status': overall_health['status'],
            'timestamp': timezone.now().isoformat(),
            'version': getattr(settings, 'VERSION', '1.0.0'),
            'environment': getattr(settings, 'ENVIRONMENT', 'development'),
            'services': {
                'database': db_health,
                'cache': cache_health,
                'system': system_health,
                'external': external_health
            },
            'metrics': {
                'response_time': time.time(),
                'uptime': get_system_uptime()
            }
        }
        
        status_code = 200 if overall_health['status'] == "healthy" else 503
        return Response(response_data, status=status_code)
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


def check_database_health():
    """Check database connectivity and performance"""
    try:
        start_time = time.time()
        
        with connection.cursor() as cursor:
            # Test basic connectivity
            cursor.execute("SELECT 1")
            
            # Test query performance
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
            
            # Test transaction capability
            cursor.execute("BEGIN")
            cursor.execute("SELECT 1")
            cursor.execute("ROLLBACK")
        
        response_time = (time.time() - start_time) * 1000  # milliseconds
        
        return {
            'status': 'healthy',
            'response_time': response_time,
            'migration_count': migration_count,
            'connection_pool': getattr(connection, 'pool', 'unknown')
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'response_time': 0
        }


def check_cache_health():
    """Check cache connectivity and performance"""
    try:
        start_time = time.time()
        
        # Test cache operations
        test_key = 'health_check_cache'
        test_value = f'test_{time.time()}'
        
        cache.set(test_key, test_value, 10)
        retrieved_value = cache.get(test_key)
        cache.delete(test_key)
        
        response_time = (time.time() - start_time) * 1000  # milliseconds
        
        if retrieved_value == test_value:
            return {
                'status': 'healthy',
                'response_time': response_time,
                'backend': cache.__class__.__name__
            }
        else:
            return {
                'status': 'unhealthy',
                'error': 'Cache read/write test failed',
                'response_time': response_time
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'response_time': 0
        }


def check_system_health():
    """Check system resources and performance"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / (1024**3)  # GB
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free = disk.free / (1024**3)  # GB
        
        # Network I/O
        network = psutil.net_io_counters()
        
        # Process count
        process_count = len(psutil.pids())
        
        # Determine overall system status
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 95:
            status = "degraded"
        elif cpu_percent > 80 or memory_percent > 85 or disk_percent > 90:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            'status': status,
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memory': {
                'percent': memory_percent,
                'available_gb': memory_available
            },
            'disk': {
                'percent': disk_percent,
                'free_gb': disk_free
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            },
            'processes': {
                'count': process_count
            }
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_external_services_health():
    """Check external services connectivity"""
    services = {
        'ai_service': {
            'url': getattr(settings, 'AI_SERVICE_URL', 'http://localhost:8001/health/'),
            'timeout': 5
        },
        'realtime_service': {
            'url': getattr(settings, 'REALTIME_SERVICE_URL', 'http://localhost:3000/health/'),
            'timeout': 5
        }
    }
    
    results = {}
    
    for service_name, config in services.items():
        try:
            start_time = time.time()
            response = requests.get(config['url'], timeout=config['timeout'])
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                results[service_name] = {
                    'status': 'healthy',
                    'response_time': response_time,
                    'status_code': response.status_code
                }
            else:
                results[service_name] = {
                    'status': 'unhealthy',
                    'response_time': response_time,
                    'status_code': response.status_code
                }
        except requests.exceptions.Timeout:
            results[service_name] = {
                'status': 'timeout',
                'response_time': config['timeout'] * 1000,
                'error': 'Request timeout'
            }
        except Exception as e:
            results[service_name] = {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': 0
            }
    
    return results


def assess_overall_health(health_data):
    """Assess overall system health based on individual service health"""
    unhealthy_services = []
    degraded_services = []
    
    for service_name, service_data in health_data.items():
        if service_data.get('status') == 'unhealthy':
            unhealthy_services.append(service_name)
        elif service_data.get('status') == 'degraded':
            degraded_services.append(service_name)
    
    if unhealthy_services:
        return {
            'status': 'unhealthy',
            'unhealthy_services': unhealthy_services,
            'degraded_services': degraded_services
        }
    elif degraded_services:
        return {
            'status': 'degraded',
            'unhealthy_services': unhealthy_services,
            'degraded_services': degraded_services
        }
    else:
        return {
            'status': 'healthy',
            'unhealthy_services': unhealthy_services,
            'degraded_services': degraded_services
        }


def get_system_uptime():
    """Get system uptime in seconds"""
    try:
        return time.time() - psutil.boot_time()
    except:
        return 0


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Kubernetes readiness probe endpoint
    Checks if the application is ready to receive traffic
    """
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check cache
        cache.set('readiness_check', 'ok', 10)
        cache.get('readiness_check')
        
        return Response({'status': 'ready'}, status=200)
    except Exception as e:
        return Response({
            'status': 'not_ready',
            'error': str(e)
        }, status=503)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Kubernetes liveness probe endpoint
    Checks if the application is alive and should be restarted
    """
    try:
        # Basic liveness check
        return Response({'status': 'alive'}, status=200)
    except Exception as e:
        return Response({
            'status': 'dead',
            'error': str(e)
        }, status=500)
