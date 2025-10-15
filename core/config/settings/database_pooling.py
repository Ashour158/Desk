"""
Database connection pooling configuration for production environments.
"""

import os
from .base import *

# Database connection pooling configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'helpdesk_db'),
        'USER': os.environ.get('DB_USER', 'helpdesk_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            # Connection pooling settings
            'MAX_CONNS': int(os.environ.get('DB_MAX_CONNS', '20')),
            'MIN_CONNS': int(os.environ.get('DB_MIN_CONNS', '5')),
            'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '600')),  # 10 minutes
            
            # Connection timeout settings
            'connect_timeout': int(os.environ.get('DB_CONNECT_TIMEOUT', '10')),
            'options': '-c default_transaction_isolation=read committed',
            
            # SSL settings for production
            'sslmode': os.environ.get('DB_SSL_MODE', 'prefer'),
            
            # Connection health check
            'application_name': 'helpdesk_platform',
        },
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '600')),
        'ATOMIC_REQUESTS': True,
    }
}

# Database connection pooling middleware
MIDDLEWARE += [
    'apps.caching.middleware.DatabaseConnectionMiddleware',
]

# Database query optimization settings
DATABASE_ROUTERS = [
    'apps.caching.routers.DatabaseRouter',
]

# Connection pooling monitoring
DATABASE_POOLING = {
    'ENABLED': True,
    'MAX_CONNECTIONS': int(os.environ.get('DB_MAX_CONNS', '20')),
    'MIN_CONNECTIONS': int(os.environ.get('DB_MIN_CONNS', '5')),
    'CONNECTION_TIMEOUT': int(os.environ.get('DB_CONNECT_TIMEOUT', '10')),
    'IDLE_TIMEOUT': int(os.environ.get('DB_IDLE_TIMEOUT', '300')),  # 5 minutes
    'MAX_LIFETIME': int(os.environ.get('DB_MAX_LIFETIME', '3600')),  # 1 hour
    'RETRY_ATTEMPTS': int(os.environ.get('DB_RETRY_ATTEMPTS', '3')),
    'RETRY_DELAY': int(os.environ.get('DB_RETRY_DELAY', '1')),
}

# Database performance monitoring
DATABASE_MONITORING = {
    'ENABLED': True,
    'SLOW_QUERY_THRESHOLD': float(os.environ.get('DB_SLOW_QUERY_THRESHOLD', '1.0')),  # 1 second
    'LOG_SLOW_QUERIES': True,
    'LOG_QUERY_PLANS': False,
    'LOG_CONNECTION_POOL_STATS': True,
}

# Redis connection pooling for caching
REDIS_POOL = {
    'ENABLED': True,
    'MAX_CONNECTIONS': int(os.environ.get('REDIS_MAX_CONNS', '50')),
    'MIN_CONNECTIONS': int(os.environ.get('REDIS_MIN_CONNS', '5')),
    'CONNECTION_TIMEOUT': int(os.environ.get('REDIS_CONNECT_TIMEOUT', '5')),
    'IDLE_TIMEOUT': int(os.environ.get('REDIS_IDLE_TIMEOUT', '300')),  # 5 minutes
    'MAX_LIFETIME': int(os.environ.get('REDIS_MAX_LIFETIME', '3600')),  # 1 hour
    'RETRY_ATTEMPTS': int(os.environ.get('REDIS_RETRY_ATTEMPTS', '3')),
    'RETRY_DELAY': int(os.environ.get('REDIS_RETRY_DELAY', '1')),
}

# Update cache configuration with connection pooling
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': int(os.environ.get('REDIS_MAX_CONNS', '50')),
                'retry_on_timeout': True,
                'socket_keepalive': True,
                'socket_keepalive_options': {},
                'health_check_interval': 30,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        }
    }
}

# Celery configuration with connection pooling
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Celery connection pooling
CELERY_BROKER_POOL_LIMIT = int(os.environ.get('CELERY_BROKER_POOL_LIMIT', '10'))
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10

# Database connection health check
DATABASE_HEALTH_CHECK = {
    'ENABLED': True,
    'INTERVAL': int(os.environ.get('DB_HEALTH_CHECK_INTERVAL', '30')),  # 30 seconds
    'TIMEOUT': int(os.environ.get('DB_HEALTH_CHECK_TIMEOUT', '5')),  # 5 seconds
    'QUERY': 'SELECT 1',
}

# Connection pool statistics
DATABASE_POOL_STATS = {
    'ENABLED': True,
    'LOG_INTERVAL': int(os.environ.get('DB_POOL_STATS_INTERVAL', '300')),  # 5 minutes
    'METRICS': [
        'active_connections',
        'idle_connections',
        'total_connections',
        'connection_errors',
        'connection_timeouts',
        'query_execution_time',
        'slow_queries',
    ]
}

# Production database settings
if os.environ.get('ENVIRONMENT') == 'production':
    # Enable connection pooling
    DATABASES['default']['OPTIONS'].update({
        'MAX_CONNS': 50,
        'MIN_CONNS': 10,
        'CONN_MAX_AGE': 1800,  # 30 minutes
        'sslmode': 'require',
        'sslcert': os.environ.get('DB_SSL_CERT', ''),
        'sslkey': os.environ.get('DB_SSL_KEY', ''),
        'sslrootcert': os.environ.get('DB_SSL_ROOT_CERT', ''),
    })
    
    # Production Redis settings
    CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS'].update({
        'max_connections': 100,
        'socket_keepalive': True,
        'socket_keepalive_options': {
            1: 1,  # TCP_KEEPIDLE
            2: 3,  # TCP_KEEPINTVL
            3: 5,  # TCP_KEEPCNT
        },
    })
    
    # Production Celery settings
    CELERY_BROKER_POOL_LIMIT = 20
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
    CELERY_BROKER_CONNECTION_RETRY = True
    CELERY_BROKER_CONNECTION_MAX_RETRIES = 20

# Development database settings
if os.environ.get('ENVIRONMENT') == 'development':
    # Disable connection pooling for development
    DATABASES['default']['OPTIONS'].update({
        'MAX_CONNS': 5,
        'MIN_CONNS': 1,
        'CONN_MAX_AGE': 0,  # No connection reuse
    })
    
    # Development Redis settings
    CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS'].update({
        'max_connections': 10,
    })
    
    # Development Celery settings
    CELERY_BROKER_POOL_LIMIT = 5

# Test database settings
if os.environ.get('ENVIRONMENT') == 'test':
    # Use in-memory database for tests
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }
    
    # Disable connection pooling for tests
    DATABASE_POOLING['ENABLED'] = False
    DATABASE_MONITORING['ENABLED'] = False
