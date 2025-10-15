"""
Fixed development settings for helpdesk platform.
"""

# Import specific settings instead of wildcard
from .base import (
    BASE_DIR, SECRET_KEY, DEBUG, ALLOWED_HOSTS, INSTALLED_APPS, MIDDLEWARE,
    TEMPLATES, DATABASES, AUTH_PASSWORD_VALIDATORS, LANGUAGE_CODE, TIME_ZONE,
    USE_I18N, USE_TZ, STATIC_URL, STATIC_ROOT, DEFAULT_AUTO_FIELD, REST_FRAMEWORK,
    CORS_ALLOWED_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_ALL_ORIGINS,
    CORS_ALLOWED_HEADERS, CORS_ALLOWED_METHODS, CELERY_BROKER_URL, CELERY_RESULT_BACKEND,
    CELERY_ACCEPT_CONTENT, CELERY_TASK_SERIALIZER, CELERY_RESULT_SERIALIZER,
    CELERY_TIMEZONE, CELERY_BEAT_SCHEDULER, CELERY_BEAT_SCHEDULE, CACHE_TTL,
    SESSION_CACHE_ALIAS
)

# Development-specific overrides
DEBUG = True
ALLOWED_HOSTS = ['*']

# Database configuration for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache configuration for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files configuration
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files configuration
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Security settings for development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
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
    },
}

# Celery configuration for development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Development-specific apps
if DEBUG:
    INSTALLED_APPS += [
        'django_extensions',
        'debug_toolbar',
    ]
    
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    
    # Debug toolbar configuration
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]