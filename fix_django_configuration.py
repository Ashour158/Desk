#!/usr/bin/env python3
"""
Script to fix Django configuration issues and install missing dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install missing Django dependencies."""
    print("Installing missing Django dependencies...")
    
    dependencies = [
        'django-celery-beat',
        'django-celery-results', 
        'django-cryptography',
        'django-otp',
        'django-ratelimit',
        'django-cors-headers',
        'django-filter',
        'psycopg2-binary',
        'django-extensions',
        'django-debug-toolbar'
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
            print(f"[OK] {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install {dep}: {e}")
            return False
    
    return True

def fix_development_settings():
    """Fix development settings configuration."""
    print("Fixing development settings...")
    
    development_settings_path = Path('config/settings/development.py')
    
    if not development_settings_path.exists():
        print("[ERROR] Development settings file not found")
        return False
    
    # Read current content
    with open(development_settings_path, 'r') as f:
        content = f.read()
    
    # Create fixed development settings
    fixed_content = '''"""
Development settings for helpdesk platform.
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
'''
    
    # Write fixed content
    with open(development_settings_path, 'w') as f:
        f.write(fixed_content)
    
    print("[OK] Development settings fixed")
    return True

def create_logs_directory():
    """Create logs directory for Django logging."""
    print("Creating logs directory...")
    
    logs_dir = Path('logs')
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create .gitkeep file
    (logs_dir / '.gitkeep').touch()
    
    print("[OK] Logs directory created")
    return True

def test_django_configuration():
    """Test Django configuration after fixes."""
    print("Testing Django configuration...")
    
    try:
        # Test Django settings
        result = subprocess.run([
            sys.executable, 'manage.py', 'check', '--settings=config.settings.development'
        ], capture_output=True, text=True, cwd='core')
        
        if result.returncode == 0:
            print("[OK] Django configuration test passed")
            return True
        else:
            print(f"[ERROR] Django configuration test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Django configuration test error: {e}")
        return False

def test_migrations():
    """Test Django migrations after fixes."""
    print("Testing Django migrations...")
    
    try:
        # Test showmigrations command
        result = subprocess.run([
            sys.executable, 'manage.py', 'showmigrations', '--settings=config.settings.development'
        ], capture_output=True, text=True, cwd='core')
        
        if result.returncode == 0:
            print("[OK] Django migrations test passed")
            return True
        else:
            print(f"[ERROR] Django migrations test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Django migrations test error: {e}")
        return False

def main():
    """Main function to fix Django configuration."""
    print("Fixing Django Configuration Issues")
    print("=" * 50)
    
    # Change to core directory
    os.chdir('core')
    
    # Install dependencies
    if not install_dependencies():
        print("[ERROR] Failed to install dependencies")
        return False
    
    # Fix development settings
    if not fix_development_settings():
        print("[ERROR] Failed to fix development settings")
        return False
    
    # Create logs directory
    if not create_logs_directory():
        print("[ERROR] Failed to create logs directory")
        return False
    
    # Test Django configuration
    if not test_django_configuration():
        print("[ERROR] Django configuration test failed")
        return False
    
    # Test migrations
    if not test_migrations():
        print("[ERROR] Django migrations test failed")
        return False
    
    print("\n[SUCCESS] Django configuration fixed successfully!")
    print("[OK] All dependencies installed")
    print("[OK] Development settings fixed")
    print("[OK] Logs directory created")
    print("[OK] Django configuration test passed")
    print("[OK] Django migrations test passed")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
