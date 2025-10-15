"""
Staging settings for helpdesk platform.
"""

import os
from .base import *

# Staging-specific overrides
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'staging.helpdesk.com,staging-api.helpdesk.com').split(',')

# Database configuration for staging
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME', 'helpdesk_staging'),
        'USER': os.environ.get('DB_USER', 'helpdesk_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'prefer',
            'MAX_CONNS': 10,
            'MIN_CONNS': 2,
            'CONN_MAX_AGE': 300,
            'CONN_HEALTH_CHECKS': True,
        },
        'CONN_MAX_AGE': 300,  # Connection pooling
        'CONN_HEALTH_CHECKS': True,
    }
}

# Cache configuration for staging
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'MAX_CONNECTIONS': 10,
            'RETRY_ON_TIMEOUT': True,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 10,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'helpdesk_staging',
        'TIMEOUT': 300,
        'VERSION': 1,
    }
}

# Email configuration for staging
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@staging.helpdesk.com')

# Security settings for staging
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Static files configuration for staging
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files configuration for staging
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Logging configuration for staging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
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
        'helpdesk': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Celery configuration for staging
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# CORS settings for staging
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'https://staging.helpdesk.com,https://staging-api.helpdesk.com').split(',')
CORS_ALLOW_CREDENTIALS = True

# Session configuration for staging
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# CSRF configuration for staging
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://staging.helpdesk.com,https://staging-api.helpdesk.com').split(',')

# Performance optimizations
CONN_MAX_AGE = 300  # Connection pooling
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

# Monitoring and health checks
HEALTH_CHECK_ENABLED = True
HEALTH_CHECK_URL = '/health/'

# Feature flags for staging
FEATURE_FLAGS = {
    'AI_ML_FEATURES': True,
    'ADVANCED_ANALYTICS': True,
    'REAL_TIME_NOTIFICATIONS': True,
    'MOBILE_APP': True,
    'IOT_INTEGRATION': False,  # Disabled in staging
    'ADVANCED_SECURITY': True,
    'WORKFLOW_AUTOMATION': True,
    'CUSTOMER_EXPERIENCE': True,
    'INTEGRATION_PLATFORM': True,
    'ADVANCED_COMMUNICATION': True,
}

# API endpoints for staging
API_ENDPOINTS = {
    'BASE_URL': 'https://staging-api.helpdesk.com',
    'TICKETS': '/api/v1/tickets/',
    'WORK_ORDERS': '/api/v1/work-orders/',
    'TECHNICIANS': '/api/v1/technicians/',
    'KNOWLEDGE_BASE': '/api/v1/knowledge-base/',
    'AUTOMATION': '/api/v1/automation/',
    'ANALYTICS': '/api/v1/analytics/',
    'INTEGRATIONS': '/api/v1/integrations/',
    'NOTIFICATIONS': '/api/v1/notifications/',
    'AI_ML': '/api/v1/ai-ml/',
    'CUSTOMER_EXPERIENCE': '/api/v1/customer-experience/',
    'ADVANCED_ANALYTICS': '/api/v1/advanced-analytics/',
    'INTEGRATION_PLATFORM': '/api/v1/integration-platform/',
    'MOBILE_IOT': '/api/v1/mobile-iot/',
    'ADVANCED_SECURITY': '/api/v1/advanced-security/',
    'ADVANCED_WORKFLOW': '/api/v1/advanced-workflow/',
    'ADVANCED_COMMUNICATION': '/api/v1/advanced-communication/',
}

# Third-party service credentials for staging
THIRD_PARTY_SERVICES = {
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
    'TWILIO_ACCOUNT_SID': os.environ.get('TWILIO_ACCOUNT_SID', ''),
    'TWILIO_AUTH_TOKEN': os.environ.get('TWILIO_AUTH_TOKEN', ''),
    'SENDGRID_API_KEY': os.environ.get('SENDGRID_API_KEY', ''),
    'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID', ''),
    'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
    'SENTRY_DSN': os.environ.get('SENTRY_DSN', ''),
}
