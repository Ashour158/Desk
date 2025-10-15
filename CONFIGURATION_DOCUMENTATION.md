# Configuration Documentation

**Date:** October 13, 2025  
**Version:** 1.0.0  
**Platform:** Helpdesk Platform

## 📋 Table of Contents

1. [Environment Configuration](#environment-configuration)
2. [Database Configuration](#database-configuration)
3. [Cache Configuration](#cache-configuration)
4. [Security Configuration](#security-configuration)
5. [Feature Flags](#feature-flags)
6. [Secrets Management](#secrets-management)
7. [API Configuration](#api-configuration)
8. [Monitoring Configuration](#monitoring-configuration)
9. [Deployment Configuration](#deployment-configuration)
10. [Troubleshooting](#troubleshooting)

## 🌍 Environment Configuration

### Development Environment

**File:** `core/config/settings/development.py`

```python
# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Database: SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache: Local Memory
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email: Console Backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security: Relaxed for development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# CORS: Allow all origins
CORS_ALLOW_ALL_ORIGINS = True
```

### Staging Environment

**File:** `core/config/settings/staging.py`

```python
# Staging-specific settings
DEBUG = False
ALLOWED_HOSTS = ['staging.helpdesk.com', 'staging-api.helpdesk.com']

# Database: PostgreSQL with PostGIS
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
    }
}

# Cache: Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'MAX_CONNECTIONS': 10,
            'RETRY_ON_TIMEOUT': True,
        },
        'KEY_PREFIX': 'helpdesk_staging',
        'TIMEOUT': 300,
    }
}

# Security: Enhanced for staging
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS: Restricted to staging domains
CORS_ALLOWED_ORIGINS = [
    'https://staging.helpdesk.com',
    'https://staging-api.helpdesk.com'
]
```

### Production Environment

**File:** `core/config/settings/production.py`

```python
# Production-specific settings
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database: PostgreSQL with SSL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'helpdesk_production'),
        'USER': os.environ.get('DB_USER', 'helpdesk_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        },
    }
}

# Cache: Redis with connection pooling
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'MAX_CONNECTIONS': 20,
            'RETRY_ON_TIMEOUT': True,
        },
        'KEY_PREFIX': 'helpdesk',
        'TIMEOUT': 300,
    }
}

# Security: Maximum security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# CORS: Restricted to production domains
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
```

## 🗄️ Database Configuration

### Connection Settings

| Environment | Engine | SSL | Connection Pooling | Health Checks |
|-------------|--------|-----|-------------------|---------------|
| **Development** | SQLite | N/A | No | No |
| **Staging** | PostgreSQL + PostGIS | Prefer | Yes (2-10) | Yes |
| **Production** | PostgreSQL + PostGIS | Required | Yes (5-20) | Yes |

### Environment Variables

```bash
# Database Configuration
DB_NAME=helpdesk_production
DB_USER=helpdesk_user
DB_PASSWORD=your_secure_password
DB_HOST=your-db-host.com
DB_PORT=5432
DATABASE_URL=postgresql://user:password@host:port/database
```

### Connection Pooling

```python
# Staging Configuration
'OPTIONS': {
    'sslmode': 'prefer',
    'MAX_CONNS': 10,
    'MIN_CONNS': 2,
    'CONN_MAX_AGE': 300,
    'CONN_HEALTH_CHECKS': True,
}

# Production Configuration
'OPTIONS': {
    'sslmode': 'require',
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
    'CONN_MAX_AGE': 600,
    'CONN_HEALTH_CHECKS': True,
}
```

## 💾 Cache Configuration

### Redis Configuration

| Environment | Backend | Connection Pooling | Key Prefix | Timeout |
|-------------|---------|-------------------|------------|---------|
| **Development** | Local Memory | N/A | N/A | Default |
| **Staging** | Redis | Yes (10) | helpdesk_staging | 300s |
| **Production** | Redis | Yes (20) | helpdesk | 300s |

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/1
REDIS_PASSWORD=your_redis_password
```

### Cache Settings

```python
# Staging Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'MAX_CONNECTIONS': 10,
            'RETRY_ON_TIMEOUT': True,
        },
        'KEY_PREFIX': 'helpdesk_staging',
        'TIMEOUT': 300,
    }
}
```

## 🔒 Security Configuration

### SSL/TLS Settings

| Setting | Development | Staging | Production |
|---------|-------------|---------|------------|
| **SECURE_SSL_REDIRECT** | False | True | True |
| **SECURE_HSTS_SECONDS** | 0 | 31536000 | 31536000 |
| **SECURE_HSTS_INCLUDE_SUBDOMAINS** | False | True | True |
| **SECURE_HSTS_PRELOAD** | False | True | True |

### Security Headers

```python
# Production Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = 'require-corp'
```

### Content Security Policy

```python
# CSP Configuration
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_CONNECT_SRC = ("'self'", "ws:", "wss:")
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
```

### File Upload Security

```python
# File Upload Restrictions
FILE_UPLOAD_ALLOWED_EXTENSIONS = [
    'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx'
]
FILE_UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_DANGEROUS_EXTENSIONS = [
    'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar', 'php', 'asp', 'aspx'
]
```

## 🚩 Feature Flags

### Environment-Specific Feature Flags

```python
# Development Feature Flags
FEATURE_FLAGS = {
    'AI_ML_FEATURES': True,
    'ADVANCED_ANALYTICS': True,
    'REAL_TIME_NOTIFICATIONS': True,
    'MOBILE_APP': True,
    'IOT_INTEGRATION': True,
    'ADVANCED_SECURITY': True,
    'WORKFLOW_AUTOMATION': True,
    'CUSTOMER_EXPERIENCE': True,
    'INTEGRATION_PLATFORM': True,
    'ADVANCED_COMMUNICATION': True,
}

# Staging Feature Flags
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

# Production Feature Flags
FEATURE_FLAGS = {
    'AI_ML_FEATURES': True,
    'ADVANCED_ANALYTICS': True,
    'REAL_TIME_NOTIFICATIONS': True,
    'MOBILE_APP': True,
    'IOT_INTEGRATION': True,
    'ADVANCED_SECURITY': True,
    'WORKFLOW_AUTOMATION': True,
    'CUSTOMER_EXPERIENCE': True,
    'INTEGRATION_PLATFORM': True,
    'ADVANCED_COMMUNICATION': True,
}
```

### API Endpoints

```python
# Staging API Endpoints
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
```

## 🔐 Secrets Management

### Supported Backends

1. **Environment Variables** (Default)
2. **AWS Secrets Manager**
3. **HashiCorp Vault**

### Environment Variables Backend

```python
# Default backend
SECRET_BACKEND = 'environment'

# Secrets are stored in environment variables
DB_PASSWORD=your_db_password
REDIS_PASSWORD=your_redis_password
EMAIL_HOST_PASSWORD=your_email_password
OPENAI_API_KEY=your_openai_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
SENDGRID_API_KEY=your_sendgrid_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
SENTRY_DSN=your_sentry_dsn
```

### AWS Secrets Manager Backend

```python
# AWS Secrets Manager Configuration
SECRET_BACKEND = 'aws'
AWS_SECRETS_REGION = 'us-east-1'
AWS_SECRETS_PREFIX = 'helpdesk'
SECRET_CACHE_TTL = 300  # 5 minutes

# Required AWS credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### HashiCorp Vault Backend

```python
# Vault Configuration
SECRET_BACKEND = 'vault'
VAULT_URL = 'http://localhost:8200'
VAULT_TOKEN = 'your_vault_token'
VAULT_PATH = 'secret/helpdesk'
SECRET_CACHE_TTL = 300  # 5 minutes
```

### Secrets Usage

```python
# Using secrets in Django settings
from core.apps.secrets.management import get_secret

# Database password
DATABASES['default']['PASSWORD'] = get_secret('DB_PASSWORD', 'default_password')

# Redis password
REDIS_URL = f"redis://:{get_secret('REDIS_PASSWORD')}@localhost:6379/1"

# Email password
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')

# Third-party service credentials
OPENAI_API_KEY = get_secret('OPENAI_API_KEY')
TWILIO_ACCOUNT_SID = get_secret('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = get_secret('TWILIO_AUTH_TOKEN')
SENDGRID_API_KEY = get_secret('SENDGRID_API_KEY')
AWS_ACCESS_KEY_ID = get_secret('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_secret('AWS_SECRET_ACCESS_KEY')
SENTRY_DSN = get_secret('SENTRY_DSN')
```

## 🌐 API Configuration

### CORS Settings

```python
# Development CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Staging CORS
CORS_ALLOWED_ORIGINS = [
    'https://staging.helpdesk.com',
    'https://staging-api.helpdesk.com'
]
CORS_ALLOW_CREDENTIALS = True

# Production CORS
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True
```

### Session Configuration

```python
# Session Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
```

### CSRF Configuration

```python
# CSRF Settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
```

## 📊 Monitoring Configuration

### Logging Configuration

#### Development Logging

```python
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
}
```

#### Staging Logging

```python
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
}
```

#### Production Logging

```python
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
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
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
}
```

### Health Checks

```python
# Health Check Configuration
HEALTH_CHECK_ENABLED = True
HEALTH_CHECK_URL = '/health/'
```

## 🚀 Deployment Configuration

### Docker Configuration

#### Development

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - DEBUG=True
    volumes:
      - .:/app
```

#### Staging

```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.staging
      - DEBUG=False
      - DB_HOST=staging-db
      - REDIS_URL=redis://staging-redis:6379/1
    depends_on:
      - db
      - redis
```

#### Production

```yaml
# docker-compose.production.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DEBUG=False
      - DB_HOST=prod-db
      - REDIS_URL=redis://prod-redis:6379/1
    depends_on:
      - db
      - redis
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Environment Variables

#### Required Environment Variables

```bash
# Core Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database
DB_NAME=helpdesk_production
DB_USER=helpdesk_user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432
DATABASE_URL=postgresql://user:password@host:port/database

# Redis
REDIS_URL=redis://your-redis-host:6379/1
REDIS_PASSWORD=your-redis-password

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com

# Third-party Services
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
SENDGRID_API_KEY=your-sendgrid-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
SENTRY_DSN=your-sentry-dsn

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://api.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://api.your-domain.com
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Issues

**Error:** `django.db.utils.OperationalError: could not connect to server`

**Solution:**
```bash
# Check database connection
python manage.py dbshell

# Verify environment variables
echo $DB_HOST
echo $DB_PORT
echo $DB_NAME
echo $DB_USER
```

#### 2. Redis Connection Issues

**Error:** `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solution:**
```bash
# Check Redis connection
redis-cli ping

# Verify Redis URL
echo $REDIS_URL
```

#### 3. SSL Certificate Issues

**Error:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
```python
# For development only
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

#### 4. CORS Issues

**Error:** `Access to fetch at 'https://api.example.com' from origin 'https://example.com' has been blocked by CORS policy`

**Solution:**
```python
# Add origin to CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = [
    'https://example.com',
    'https://api.example.com'
]
```

#### 5. Secrets Management Issues

**Error:** `Secret not found`

**Solution:**
```bash
# Check secrets backend
echo $SECRET_BACKEND

# Verify secret exists
python manage.py shell
>>> from core.apps.secrets.management import get_secret
>>> get_secret('DB_PASSWORD')
```

### Debugging Commands

```bash
# Check Django settings
python manage.py diffsettings

# Check database connection
python manage.py dbshell

# Check cache connection
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')

# Check environment variables
python manage.py shell
>>> import os
>>> print(os.environ.get('DJANGO_SETTINGS_MODULE'))

# Test secrets management
python manage.py shell
>>> from core.apps.secrets.management import get_secret
>>> get_secret('DB_PASSWORD')
```

### Performance Monitoring

```bash
# Check database performance
python manage.py shell
>>> from django.db import connection
>>> connection.queries

# Check cache performance
python manage.py shell
>>> from django.core.cache import cache
>>> cache.get('test_key')

# Check memory usage
python manage.py shell
>>> import psutil
>>> psutil.virtual_memory()
```

### Log Analysis

```bash
# View Django logs
tail -f logs/django.log

# View error logs
tail -f logs/error.log

# Search for specific errors
grep "ERROR" logs/django.log
grep "CRITICAL" logs/django.log
```

## 📞 Support

For configuration issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Verify environment variables are set correctly
4. Test database and cache connections
5. Contact the development team if issues persist

## 🔄 Updates

This documentation is updated regularly. Last updated: October 13, 2025

For the latest version, check the repository or contact the development team.
