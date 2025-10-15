# Rollback Procedures

**Date:** October 13, 2025  
**Version:** 1.0.0  
**Platform:** Helpdesk Platform

## 📋 Table of Contents

1. [Overview](#overview)
2. [Configuration Rollback](#configuration-rollback)
3. [Database Migration Rollback](#database-migration-rollback)
4. [Environment Rollback](#environment-rollback)
5. [Secrets Management Rollback](#secrets-management-rollback)
6. [Feature Flags Rollback](#feature-flags-rollback)
7. [Deployment Rollback](#deployment-rollback)
8. [Nginx Configuration Rollback](#nginx-configuration-rollback)
9. [Emergency Rollback](#emergency-rollback)
10. [Testing Rollback Procedures](#testing-rollback-procedures)

## 🔄 Overview

This document outlines the rollback procedures for the Helpdesk Platform. Rollback procedures are essential for maintaining system stability and quickly recovering from failed deployments or configuration changes.

### Rollback Types

1. **Configuration Rollback** - Reverting configuration file changes
2. **Database Migration Rollback** - Reverting database schema changes
3. **Environment Rollback** - Reverting environment variable changes
4. **Secrets Management Rollback** - Reverting secrets management changes
5. **Feature Flags Rollback** - Reverting feature flag changes
6. **Deployment Rollback** - Reverting deployment changes
7. **Nginx Configuration Rollback** - Reverting Nginx configuration changes

## ⚙️ Configuration Rollback

### Files to Backup

```bash
# Core configuration files
core/config/settings/development.py
core/config/settings/staging.py
core/config/settings/production.py
core/config/settings/base.py

# Infrastructure configuration
nginx/nginx.conf
docker-compose.yml
docker-compose.staging.yml
docker-compose.production.yml

# Deployment configuration
deploy/aws/cloudformation.yaml
deploy/aws/ecs-task-definition.json
deploy/render/render.yaml
```

### Rollback Procedure

#### 1. Create Backup

```bash
# Create configuration backup
mkdir -p backups/config_$(date +%Y%m%d_%H%M%S)
cp -r core/config/settings/ backups/config_$(date +%Y%m%d_%H%M%S)/
cp nginx/nginx.conf backups/config_$(date +%Y%m%d_%H%M%S)/
cp docker-compose*.yml backups/config_$(date +%Y%m%d_%H%M%S)/
```

#### 2. Restore Configuration

```bash
# Restore from backup
cp -r backups/config_YYYYMMDD_HHMMSS/settings/ core/config/
cp backups/config_YYYYMMDD_HHMMSS/nginx.conf nginx/
cp backups/config_YYYYMMDD_HHMMSS/docker-compose*.yml ./
```

#### 3. Verify Rollback

```bash
# Check configuration files
ls -la core/config/settings/
ls -la nginx/
ls -la docker-compose*.yml

# Test configuration
python manage.py check --deploy
```

### Automated Rollback Script

```bash
#!/bin/bash
# config_rollback.sh

BACKUP_DIR="backups/config_$1"
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory $BACKUP_DIR not found"
    exit 1
fi

echo "Rolling back configuration from $BACKUP_DIR..."

# Restore configuration files
cp -r "$BACKUP_DIR/settings/" core/config/
cp "$BACKUP_DIR/nginx.conf" nginx/
cp "$BACKUP_DIR/docker-compose"*.yml ./

echo "Configuration rollback completed"
```

## 🗄️ Database Migration Rollback

### Rollback Procedure

#### 1. Check Current Migration State

```bash
# Show current migrations
python manage.py showmigrations

# Show migration history
python manage.py showmigrations --plan
```

#### 2. Rollback to Specific Migration

```bash
# Rollback to specific migration
python manage.py migrate app_name migration_number

# Rollback all migrations for an app
python manage.py migrate app_name zero

# Rollback to previous migration
python manage.py migrate app_name --fake-initial
```

#### 3. Rollback All Migrations

```bash
# Rollback all migrations
python manage.py migrate zero

# Reapply migrations
python manage.py migrate
```

### Migration Rollback Script

```bash
#!/bin/bash
# migration_rollback.sh

APP_NAME=$1
MIGRATION_NUMBER=$2

if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <app_name> [migration_number]"
    exit 1
fi

echo "Rolling back migrations for $APP_NAME..."

if [ -z "$MIGRATION_NUMBER" ]; then
    # Rollback to zero
    python manage.py migrate $APP_NAME zero
else
    # Rollback to specific migration
    python manage.py migrate $APP_NAME $MIGRATION_NUMBER
fi

echo "Migration rollback completed"
```

## 🌍 Environment Rollback

### Environment Variables to Backup

```bash
# Core environment variables
DJANGO_SETTINGS_MODULE
SECRET_KEY
DEBUG
ALLOWED_HOSTS

# Database environment variables
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
DATABASE_URL

# Cache environment variables
REDIS_URL
REDIS_PASSWORD

# Email environment variables
EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL

# Third-party service environment variables
OPENAI_API_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
SENDGRID_API_KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
SENTRY_DSN

# CORS environment variables
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
```

### Rollback Procedure

#### 1. Backup Environment Variables

```bash
# Create environment backup
env > backups/env_$(date +%Y%m%d_%H%M%S).env
```

#### 2. Restore Environment Variables

```bash
# Restore from backup
source backups/env_YYYYMMDD_HHMMSS.env
```

#### 3. Verify Environment

```bash
# Check environment variables
echo $DJANGO_SETTINGS_MODULE
echo $DB_HOST
echo $REDIS_URL

# Test Django configuration
python manage.py check
```

### Environment Rollback Script

```bash
#!/bin/bash
# env_rollback.sh

BACKUP_FILE="backups/env_$1.env"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file $BACKUP_FILE not found"
    exit 1
fi

echo "Rolling back environment from $BACKUP_FILE..."

# Restore environment variables
source "$BACKUP_FILE"

echo "Environment rollback completed"
```

## 🔐 Secrets Management Rollback

### Rollback Procedure

#### 1. AWS Secrets Manager Rollback

```bash
# List secrets
aws secretsmanager list-secrets

# Get secret value
aws secretsmanager get-secret-value --secret-id helpdesk/DB_PASSWORD

# Update secret to previous value
aws secretsmanager update-secret --secret-id helpdesk/DB_PASSWORD --secret-string "previous_value"
```

#### 2. HashiCorp Vault Rollback

```bash
# List secrets
vault kv list secret/helpdesk

# Get secret value
vault kv get secret/helpdesk/DB_PASSWORD

# Update secret to previous value
vault kv put secret/helpdesk/DB_PASSWORD value="previous_value"
```

#### 3. Environment Variables Rollback

```bash
# Restore from backup
export DB_PASSWORD="previous_value"
export REDIS_PASSWORD="previous_value"
export EMAIL_HOST_PASSWORD="previous_value"
```

### Secrets Rollback Script

```bash
#!/bin/bash
# secrets_rollback.sh

SECRET_BACKEND=$1
SECRET_NAME=$2
PREVIOUS_VALUE=$3

if [ -z "$SECRET_BACKEND" ] || [ -z "$SECRET_NAME" ] || [ -z "$PREVIOUS_VALUE" ]; then
    echo "Usage: $0 <backend> <secret_name> <previous_value>"
    exit 1
fi

echo "Rolling back secret $SECRET_NAME to previous value..."

case $SECRET_BACKEND in
    "aws")
        aws secretsmanager update-secret --secret-id "helpdesk/$SECRET_NAME" --secret-string "$PREVIOUS_VALUE"
        ;;
    "vault")
        vault kv put "secret/helpdesk/$SECRET_NAME" value="$PREVIOUS_VALUE"
        ;;
    "env")
        export "$SECRET_NAME=$PREVIOUS_VALUE"
        ;;
    *)
        echo "Unknown backend: $SECRET_BACKEND"
        exit 1
        ;;
esac

echo "Secrets rollback completed"
```

## 🚩 Feature Flags Rollback

### Rollback Procedure

#### 1. Database Feature Flags Rollback

```bash
# Connect to database
python manage.py shell

# Rollback feature flags
from apps.features.models import Feature
Feature.objects.filter(name='FEATURE_NAME').update(status='inactive')
```

#### 2. Environment Feature Flags Rollback

```bash
# Restore from backup
cp backups/feature_flags_YYYYMMDD_HHMMSS.py core/config/settings/
```

#### 3. API Feature Flags Rollback

```bash
# Update feature flag via API
curl -X POST "https://api.helpdesk.com/api/v1/features/flags/FEATURE_NAME/update/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": false}'
```

### Feature Flags Rollback Script

```bash
#!/bin/bash
# feature_flags_rollback.sh

FEATURE_NAME=$1
FEATURE_VALUE=$2

if [ -z "$FEATURE_NAME" ] || [ -z "$FEATURE_VALUE" ]; then
    echo "Usage: $0 <feature_name> <feature_value>"
    exit 1
fi

echo "Rolling back feature flag $FEATURE_NAME to $FEATURE_VALUE..."

# Update feature flag
python manage.py shell << EOF
from apps.features.models import Feature
Feature.objects.filter(name='$FEATURE_NAME').update(status='$FEATURE_VALUE')
EOF

echo "Feature flags rollback completed"
```

## 🚀 Deployment Rollback

### Rollback Procedure

#### 1. Docker Deployment Rollback

```bash
# Stop current containers
docker-compose down

# Restore from backup
cp backups/docker-compose_YYYYMMDD_HHMMSS.yml docker-compose.yml

# Start with previous configuration
docker-compose up -d
```

#### 2. AWS ECS Deployment Rollback

```bash
# List task definitions
aws ecs list-task-definitions

# Rollback to previous task definition
aws ecs update-service --cluster helpdesk-cluster --service helpdesk-service --task-definition helpdesk-task:previous
```

#### 3. Render Deployment Rollback

```bash
# List deployments
render deployments list

# Rollback to previous deployment
render deployments rollback <deployment_id>
```

### Deployment Rollback Script

```bash
#!/bin/bash
# deployment_rollback.sh

DEPLOYMENT_TYPE=$1
BACKUP_FILE=$2

if [ -z "$DEPLOYMENT_TYPE" ] || [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <deployment_type> <backup_file>"
    exit 1
fi

echo "Rolling back $DEPLOYMENT_TYPE deployment from $BACKUP_FILE..."

case $DEPLOYMENT_TYPE in
    "docker")
        docker-compose down
        cp "$BACKUP_FILE" docker-compose.yml
        docker-compose up -d
        ;;
    "aws")
        aws ecs update-service --cluster helpdesk-cluster --service helpdesk-service --task-definition "$BACKUP_FILE"
        ;;
    "render")
        render deployments rollback "$BACKUP_FILE"
        ;;
    *)
        echo "Unknown deployment type: $DEPLOYMENT_TYPE"
        exit 1
        ;;
esac

echo "Deployment rollback completed"
```

## 🌐 Nginx Configuration Rollback

### Rollback Procedure

#### 1. Backup Nginx Configuration

```bash
# Create Nginx backup
mkdir -p backups/nginx_$(date +%Y%m%d_%H%M%S)
cp nginx/nginx.conf backups/nginx_$(date +%Y%m%d_%H%M%S)/
cp -r nginx/ssl/ backups/nginx_$(date +%Y%m%d_%H%M%S)/
```

#### 2. Restore Nginx Configuration

```bash
# Restore from backup
cp backups/nginx_YYYYMMDD_HHMMSS/nginx.conf nginx/
cp -r backups/nginx_YYYYMMDD_HHMMSS/ssl/ nginx/
```

#### 3. Reload Nginx

```bash
# Test configuration
nginx -t

# Reload Nginx
nginx -s reload
```

### Nginx Rollback Script

```bash
#!/bin/bash
# nginx_rollback.sh

BACKUP_DIR="backups/nginx_$1"
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory $BACKUP_DIR not found"
    exit 1
fi

echo "Rolling back Nginx configuration from $BACKUP_DIR..."

# Restore Nginx configuration
cp "$BACKUP_DIR/nginx.conf" nginx/
cp -r "$BACKUP_DIR/ssl/" nginx/

# Test and reload Nginx
nginx -t && nginx -s reload

echo "Nginx rollback completed"
```

## 🚨 Emergency Rollback

### Emergency Rollback Procedure

#### 1. Immediate Actions

```bash
# Stop all services
docker-compose down
systemctl stop nginx
systemctl stop redis
systemctl stop postgresql

# Restore from latest backup
cp -r backups/latest/* ./

# Restart services
systemctl start postgresql
systemctl start redis
systemctl start nginx
docker-compose up -d
```

#### 2. Verify System Health

```bash
# Check service status
systemctl status nginx
systemctl status redis
systemctl status postgresql
docker-compose ps

# Test application
curl -f http://localhost:8000/health/
```

#### 3. Notify Team

```bash
# Send notification
curl -X POST "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{"text": "Emergency rollback completed for Helpdesk Platform"}'
```

### Emergency Rollback Script

```bash
#!/bin/bash
# emergency_rollback.sh

echo "🚨 EMERGENCY ROLLBACK INITIATED 🚨"

# Stop all services
echo "Stopping all services..."
docker-compose down
systemctl stop nginx
systemctl stop redis
systemctl stop postgresql

# Restore from latest backup
echo "Restoring from latest backup..."
cp -r backups/latest/* ./

# Restart services
echo "Restarting services..."
systemctl start postgresql
systemctl start redis
systemctl start nginx
docker-compose up -d

# Verify system health
echo "Verifying system health..."
sleep 30
curl -f http://localhost:8000/health/ && echo "✅ System healthy" || echo "❌ System unhealthy"

echo "🚨 EMERGENCY ROLLBACK COMPLETED 🚨"
```

## 🧪 Testing Rollback Procedures

### Automated Testing

```bash
# Run rollback tests
python scripts/test_rollback_procedures.py

# Test specific rollback
python scripts/test_rollback_procedures.py --test configuration_rollback
python scripts/test_rollback_procedures.py --test database_migration_rollback
python scripts/test_rollback_procedures.py --test environment_rollback
python scripts/test_rollback_procedures.py --test secrets_rollback
python scripts/test_rollback_procedures.py --test feature_flags_rollback
python scripts/test_rollback_procedures.py --test deployment_rollback
python scripts/test_rollback_procedures.py --test nginx_rollback
```

### Manual Testing

#### 1. Configuration Rollback Test

```bash
# Create test configuration
echo "# TEST CONFIGURATION" >> core/config/settings/development.py

# Create backup
mkdir -p backups/test_config_$(date +%Y%m%d_%H%M%S)
cp core/config/settings/development.py backups/test_config_$(date +%Y%m%d_%H%M%S)/

# Modify configuration
echo "# MODIFIED CONFIGURATION" >> core/config/settings/development.py

# Test rollback
cp backups/test_config_YYYYMMDD_HHMMSS/development.py core/config/settings/
```

#### 2. Database Migration Rollback Test

```bash
# Create test migration
python manage.py makemigrations --empty test_app

# Apply migration
python manage.py migrate

# Test rollback
python manage.py migrate test_app zero
```

#### 3. Environment Rollback Test

```bash
# Set test environment variable
export TEST_VAR="original_value"

# Create backup
env > backups/test_env_$(date +%Y%m%d_%H%M%S).env

# Modify environment
export TEST_VAR="modified_value"

# Test rollback
source backups/test_env_YYYYMMDD_HHMMSS.env
echo $TEST_VAR  # Should be "original_value"
```

### Test Results

```bash
# Generate test report
python scripts/test_rollback_procedures.py --report

# View test results
cat rollback_procedures_test_report.json
```

## 📊 Rollback Monitoring

### Monitoring Rollback Success

```bash
# Check service status
systemctl status nginx redis postgresql
docker-compose ps

# Check application health
curl -f http://localhost:8000/health/

# Check database connectivity
python manage.py dbshell

# Check cache connectivity
python manage.py shell -c "from django.core.cache import cache; cache.set('test', 'value'); print(cache.get('test'))"
```

### Rollback Metrics

```bash
# Track rollback frequency
grep "ROLLBACK" logs/django.log | wc -l

# Track rollback success rate
grep "ROLLBACK SUCCESS" logs/django.log | wc -l
grep "ROLLBACK FAILED" logs/django.log | wc -l
```

## 📞 Support

For rollback issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Verify backup files exist and are accessible
4. Test rollback procedures in a staging environment
5. Contact the development team if issues persist

## 🔄 Updates

This document is updated regularly. Last updated: October 13, 2025

For the latest version, check the repository or contact the development team.
