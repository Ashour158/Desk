# 🚀 **Deployment Process Documentation**

**Version:** 1.0.0  
**Last Updated:** October 13, 2025

## 📋 **Table of Contents**

- [Deployment Overview](#deployment-overview)
- [Environment Setup](#environment-setup)
- [Build Process](#build-process)
- [Deployment Strategies](#deployment-strategies)
- [Platform-Specific Deployments](#platform-specific-deployments)
- [Database Migrations](#database-migrations)
- [Environment Configuration](#environment-configuration)
- [Health Checks](#health-checks)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## 🎯 **Deployment Overview**

The Helpdesk Platform supports multiple deployment strategies across different environments and platforms. The deployment process is designed to be reliable, secure, and maintainable with comprehensive automation and monitoring.

### **Deployment Architecture**

```mermaid
graph TB
    subgraph "Development"
        DEV[Development Environment]
        DEV_DB[(SQLite Database)]
        DEV_CACHE[(Redis Cache)]
    end
    
    subgraph "Staging"
        STAGE[Staging Environment]
        STAGE_DB[(PostgreSQL)]
        STAGE_CACHE[(Redis Cache)]
        STAGE_CDN[CDN]
    end
    
    subgraph "Production"
        PROD[Production Environment]
        PROD_DB[(Aurora PostgreSQL)]
        PROD_CACHE[(ElastiCache Redis)]
        PROD_CDN[CloudFront CDN]
        PROD_LB[Load Balancer]
    end
    
    subgraph "CI/CD Pipeline"
        GIT[Git Repository]
        CI[CI/CD Pipeline]
        REGISTRY[Container Registry]
        MONITOR[Monitoring]
    end
    
    GIT --> CI
    CI --> REGISTRY
    REGISTRY --> DEV
    REGISTRY --> STAGE
    REGISTRY --> PROD
    
    DEV --> DEV_DB
    DEV --> DEV_CACHE
    
    STAGE --> STAGE_DB
    STAGE --> STAGE_CACHE
    STAGE --> STAGE_CDN
    
    PROD --> PROD_DB
    PROD --> PROD_CACHE
    PROD --> PROD_CDN
    PROD --> PROD_LB
    
    CI --> MONITOR
    PROD --> MONITOR
```

### **Deployment Principles**

- **Zero-Downtime Deployments**: Blue-green and rolling deployments
- **Infrastructure as Code**: All infrastructure defined in code
- **Automated Testing**: Comprehensive test suites before deployment
- **Environment Parity**: Consistent environments across stages
- **Security First**: Security scanning and validation at every stage
- **Monitoring**: Real-time monitoring and alerting
- **Rollback Ready**: Quick rollback capabilities for issues

---

## 🏗️ **Environment Setup**

### **Environment Requirements**

#### **Development Environment**
```yaml
# docker-compose.dev.yml
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
      - /app/staticfiles
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=helpdesk_dev
      - POSTGRES_USER=helpdesk
      - POSTGRES_PASSWORD=dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.dev.conf:/etc/nginx/nginx.conf
    depends_on:
      - web

volumes:
  postgres_data:
```

#### **Staging Environment**
```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  web:
    build: .
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.staging
      - DEBUG=False
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=helpdesk_staging
      - POSTGRES_USER=helpdesk
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

  redis:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.staging.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
```

#### **Production Environment**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  web:
    build: .
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DEBUG=False
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=helpdesk_production
      - POSTGRES_USER=helpdesk
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G

  redis:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
```

---

## 🔨 **Build Process**

### **Docker Build Process**

#### **Multi-Stage Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy project
COPY . /app/

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### **Frontend Build Process**
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine as base

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=base /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### **Build Scripts**

#### **Build Script**
```bash
#!/bin/bash
# scripts/build.sh

set -e

# Configuration
REGISTRY="your-registry.com"
IMAGE_NAME="helpdesk-platform"
VERSION=${1:-latest}
ENVIRONMENT=${2:-production}

echo "Building $IMAGE_NAME:$VERSION for $ENVIRONMENT environment"

# Build backend
echo "Building backend..."
docker build -t $REGISTRY/$IMAGE_NAME-backend:$VERSION -f Dockerfile .

# Build frontend
echo "Building frontend..."
docker build -t $REGISTRY/$IMAGE_NAME-frontend:$VERSION -f Dockerfile.frontend ./customer-portal

# Build AI service
echo "Building AI service..."
docker build -t $REGISTRY/$IMAGE_NAME-ai:$VERSION -f ai-service/Dockerfile ./ai-service

# Build realtime service
echo "Building realtime service..."
docker build -t $REGISTRY/$IMAGE_NAME-realtime:$VERSION -f realtime-service/Dockerfile ./realtime-service

# Security scanning
echo "Running security scan..."
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image $REGISTRY/$IMAGE_NAME-backend:$VERSION

# Push to registry
echo "Pushing images to registry..."
docker push $REGISTRY/$IMAGE_NAME-backend:$VERSION
docker push $REGISTRY/$IMAGE_NAME-frontend:$VERSION
docker push $REGISTRY/$IMAGE_NAME-ai:$VERSION
docker push $REGISTRY/$IMAGE_NAME-realtime:$VERSION

echo "Build completed successfully!"
```

#### **Build Configuration**
```yaml
# .github/workflows/build.yml
name: Build and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.REGISTRY_URL }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Build and push backend
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/helpdesk-backend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build and push frontend
      uses: docker/build-push-action@v4
      with:
        context: ./customer-portal
        push: true
        tags: ${{ secrets.REGISTRY_URL }}/helpdesk-frontend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Security scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ secrets.REGISTRY_URL }}/helpdesk-backend:${{ github.sha }}
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

---

## 🚀 **Deployment Strategies**

### **1. Blue-Green Deployment**

#### **Blue-Green Setup**
```yaml
# blue-green-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: helpdesk-blue
  labels:
    app: helpdesk
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: helpdesk
      version: blue
  template:
    metadata:
      labels:
        app: helpdesk
        version: blue
    spec:
      containers:
      - name: helpdesk
        image: helpdesk-backend:blue
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: helpdesk-green
  labels:
    app: helpdesk
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: helpdesk
      version: green
  template:
    metadata:
      labels:
        app: helpdesk
        version: green
    spec:
      containers:
      - name: helpdesk
        image: helpdesk-backend:green
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: helpdesk-service
spec:
  selector:
    app: helpdesk
    version: blue  # Switch between blue and green
  ports:
  - port: 80
    targetPort: 8000
```

#### **Blue-Green Switch Script**
```bash
#!/bin/bash
# scripts/blue-green-switch.sh

CURRENT_VERSION=$(kubectl get service helpdesk-service -o jsonpath='{.spec.selector.version}')
NEW_VERSION=""

if [ "$CURRENT_VERSION" = "blue" ]; then
    NEW_VERSION="green"
else
    NEW_VERSION="blue"
fi

echo "Switching from $CURRENT_VERSION to $NEW_VERSION"

# Update service selector
kubectl patch service helpdesk-service -p '{"spec":{"selector":{"version":"'$NEW_VERSION'"}}}'

# Wait for rollout
kubectl rollout status deployment/helpdesk-$NEW_VERSION

# Verify health
kubectl get pods -l app=helpdesk,version=$NEW_VERSION

echo "Switch completed successfully!"
```

### **2. Rolling Deployment**

#### **Rolling Update Configuration**
```yaml
# rolling-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: helpdesk-deployment
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: helpdesk
  template:
    metadata:
      labels:
        app: helpdesk
    spec:
      containers:
      - name: helpdesk
        image: helpdesk-backend:latest
        ports:
        - containerPort: 8000
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
```

#### **Rolling Update Script**
```bash
#!/bin/bash
# scripts/rolling-update.sh

IMAGE_TAG=${1:-latest}
NAMESPACE=${2:-default}

echo "Starting rolling update to $IMAGE_TAG"

# Update deployment
kubectl set image deployment/helpdesk-deployment \
  helpdesk=helpdesk-backend:$IMAGE_TAG \
  -n $NAMESPACE

# Wait for rollout
kubectl rollout status deployment/helpdesk-deployment -n $NAMESPACE

# Verify deployment
kubectl get pods -l app=helpdesk -n $NAMESPACE

echo "Rolling update completed successfully!"
```

### **3. Canary Deployment**

#### **Canary Setup**
```yaml
# canary-deployment.yml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: helpdesk-rollout
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 40
      - pause: {duration: 10m}
      - setWeight: 60
      - pause: {duration: 10m}
      - setWeight: 80
      - pause: {duration: 10m}
  selector:
    matchLabels:
      app: helpdesk
  template:
    metadata:
      labels:
        app: helpdesk
    spec:
      containers:
      - name: helpdesk
        image: helpdesk-backend:latest
        ports:
        - containerPort: 8000
```

#### **Canary Analysis**
```bash
#!/bin/bash
# scripts/canary-analysis.sh

# Get canary metrics
kubectl get rollout helpdesk-rollout -o jsonpath='{.status.conditions}'

# Check error rates
kubectl logs -l app=helpdesk,version=canary --tail=100 | grep ERROR | wc -l

# Check response times
kubectl top pods -l app=helpdesk

# Promote or rollback based on metrics
if [ $ERROR_RATE -lt 5 ] && [ $RESPONSE_TIME -lt 1000 ]; then
    echo "Promoting canary"
    kubectl argo rollouts promote helpdesk-rollout
else
    echo "Rolling back canary"
    kubectl argo rollouts abort helpdesk-rollout
fi
```

---

## 🌐 **Platform-Specific Deployments**

### **1. AWS ECS Deployment**

#### **ECS Task Definition**
```json
{
  "family": "helpdesk-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "helpdesk-backend",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/helpdesk-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DJANGO_SETTINGS_MODULE",
          "value": "config.settings.production"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@aurora-cluster:5432/helpdesk"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:helpdesk/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/helpdesk-platform",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "backend"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### **ECS Service Configuration**
```yaml
# ecs-service.yml
apiVersion: v1
kind: Service
metadata:
  name: helpdesk-service
spec:
  type: LoadBalancer
  selector:
    app: helpdesk
  ports:
  - port: 80
    targetPort: 8000
  loadBalancerSourceRanges:
  - 0.0.0.0/0
```

### **2. Kubernetes Deployment**

#### **Kubernetes Manifests**
```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: helpdesk-backend
  labels:
    app: helpdesk
    component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: helpdesk
      component: backend
  template:
    metadata:
      labels:
        app: helpdesk
        component: backend
    spec:
      containers:
      - name: helpdesk-backend
        image: helpdesk-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "config.settings.production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: helpdesk-backend-service
spec:
  selector:
    app: helpdesk
    component: backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: helpdesk-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.helpdesk.com
    secretName: helpdesk-tls
  rules:
  - host: api.helpdesk.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: helpdesk-backend-service
            port:
              number: 80
```

### **3. Render Deployment**

#### **Render Configuration**
```yaml
# render.yaml
services:
  # Backend API
  - type: web
    name: helpdesk-backend
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - key: SECRET_KEY
        fromService:
          type: web
          name: helpdesk-backend
          envVarKey: SECRET_KEY
      - key: DATABASE_URL
        fromDatabase:
          name: helpdesk-postgres
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: helpdesk-redis
          property: connectionString
    healthCheckPath: /health/
    autoDeploy: true

  # Frontend
  - type: web
    name: helpdesk-frontend
    env: static
    buildCommand: npm ci && npm run build
    staticPublishPath: ./dist
    envVars:
      - key: REACT_APP_API_URL
        value: https://helpdesk-backend.onrender.com
    autoDeploy: true

  # Celery Worker
  - type: worker
    name: helpdesk-celery
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A config worker -l info
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - key: CELERY_BROKER_URL
        fromService:
          type: redis
          name: helpdesk-redis
          property: connectionString

databases:
  - name: helpdesk-postgres
    plan: starter
    databaseName: helpdesk
    user: helpdesk_user

  - name: helpdesk-redis
    plan: starter
```

### **4. Docker Compose Deployment**

#### **Production Docker Compose**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    build: .
    restart: unless-stopped
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
    env_file:
      - .env.production
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - web
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

---

## 🗄️ **Database Migrations**

### **Migration Strategy**

#### **Migration Script**
```bash
#!/bin/bash
# scripts/migrate.sh

set -e

ENVIRONMENT=${1:-production}
BACKUP_ENABLED=${2:-true}

echo "Running migrations for $ENVIRONMENT environment"

# Backup database if enabled
if [ "$BACKUP_ENABLED" = "true" ]; then
    echo "Creating database backup..."
    ./scripts/backup-db.sh $ENVIRONMENT
fi

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --settings=config.settings.$ENVIRONMENT

# Run data migrations
echo "Running data migrations..."
python manage.py migrate --settings=config.settings.$ENVIRONMENT --run-syncdb

# Verify migrations
echo "Verifying migrations..."
python manage.py showmigrations --settings=config.settings.$ENVIRONMENT

echo "Migrations completed successfully!"
```

#### **Migration Validation**
```python
# scripts/validate_migrations.py
import os
import sys
import django
from django.core.management import execute_from_command_line

def validate_migrations():
    """Validate that all migrations are applied correctly"""
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    django.setup()
    
    from django.db import connection
    from django.core.management import call_command
    
    # Check for unapplied migrations
    try:
        call_command('migrate', '--check', verbosity=0)
        print("✅ All migrations are applied")
        return True
    except SystemExit:
        print("❌ Unapplied migrations found")
        return False

def check_database_health():
    """Check database connection and basic health"""
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result[0] == 1:
            print("✅ Database connection healthy")
            return True
        else:
            print("❌ Database health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_migrations() and check_database_health()
    sys.exit(0 if success else 1)
```

### **Data Migration Examples**

#### **User Data Migration**
```python
# migrations/0001_initial_data.py
from django.db import migrations
from django.contrib.auth import get_user_model

User = get_user_model()

def create_initial_data(apps, schema_editor):
    """Create initial data for the application"""
    
    # Create superuser
    if not User.objects.filter(email='admin@helpdesk.com').exists():
        User.objects.create_superuser(
            email='admin@helpdesk.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
    
    # Create default organization
    Organization = apps.get_model('organizations', 'Organization')
    if not Organization.objects.filter(slug='default').exists():
        Organization.objects.create(
            name='Default Organization',
            slug='default',
            description='Default organization for the helpdesk platform'
        )

def reverse_initial_data(apps, schema_editor):
    """Reverse the initial data creation"""
    User.objects.filter(email='admin@helpdesk.com').delete()
    Organization.objects.filter(slug='default').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0001_initial'),
        ('users', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(create_initial_data, reverse_initial_data),
    ]
```

#### **Feature Flag Migration**
```python
# migrations/0002_feature_flags.py
from django.db import migrations

def create_feature_flags(apps, schema_editor):
    """Create default feature flags"""
    
    Feature = apps.get_model('features', 'Feature')
    FeatureCategory = apps.get_model('features', 'FeatureCategory')
    
    # Create categories
    categories = [
        ('AI', 'AI and Machine Learning'),
        ('Analytics', 'Analytics and Reporting'),
        ('Communication', 'Communication Features'),
        ('Security', 'Security Features'),
    ]
    
    for slug, name in categories:
        FeatureCategory.objects.get_or_create(
            slug=slug,
            defaults={'name': name}
        )
    
    # Create features
    features = [
        ('AI_ML_FEATURES', 'AI/ML Features', 'AI', True),
        ('ADVANCED_ANALYTICS', 'Advanced Analytics', 'Analytics', True),
        ('REAL_TIME_NOTIFICATIONS', 'Real-time Notifications', 'Communication', True),
        ('ADVANCED_SECURITY', 'Advanced Security', 'Security', True),
    ]
    
    for slug, name, category_slug, is_active in features:
        category = FeatureCategory.objects.get(slug=category_slug)
        Feature.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'category': category,
                'is_active': is_active
            }
        )

class Migration(migrations.Migration):
    dependencies = [
        ('features', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(create_feature_flags),
    ]
```

---

## ⚙️ **Environment Configuration**

### **Environment Variables**

#### **Production Environment**
```bash
# .env.production
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DB_NAME=helpdesk_production
DB_USER=helpdesk_user
DB_PASSWORD=secure-password
DB_HOST=aurora-cluster.amazonaws.com
DB_PORT=5432

# Redis
REDIS_URL=redis://redis-cluster:6379/0
CELERY_BROKER_URL=redis://redis-cluster:6379/0
CELERY_RESULT_BACKEND=redis://redis-cluster:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@helpdesk.com
EMAIL_HOST_PASSWORD=email-password

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=helpdesk-storage
AWS_REGION=us-west-2

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO

# Feature Flags
FEATURE_FLAGS_AI_ML_FEATURES=True
FEATURE_FLAGS_ADVANCED_ANALYTICS=True
FEATURE_FLAGS_REAL_TIME_NOTIFICATIONS=True
```

#### **Staging Environment**
```bash
# .env.staging
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.staging
DEBUG=False
SECRET_KEY=staging-secret-key

# Database
DATABASE_URL=postgresql://user:pass@staging-host:5432/dbname
DB_NAME=helpdesk_staging
DB_USER=helpdesk_user
DB_PASSWORD=staging-password
DB_HOST=staging-db.amazonaws.com
DB_PORT=5432

# Redis
REDIS_URL=redis://staging-redis:6379/0
CELERY_BROKER_URL=redis://staging-redis:6379/0
CELERY_RESULT_BACKEND=redis://staging-redis:6379/0

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=sendgrid-api-key

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Feature Flags
FEATURE_FLAGS_AI_ML_FEATURES=True
FEATURE_FLAGS_ADVANCED_ANALYTICS=True
FEATURE_FLAGS_REAL_TIME_NOTIFICATIONS=True
FEATURE_FLAGS_IOT_INTEGRATION=False  # Disabled in staging
```

### **Configuration Management**

#### **ConfigMap for Kubernetes**
```yaml
# configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DJANGO_SETTINGS_MODULE: "config.settings.production"
  DEBUG: "False"
  LOG_LEVEL: "INFO"
  REDIS_URL: "redis://redis-service:6379/0"
  CELERY_BROKER_URL: "redis://redis-service:6379/0"
  CELERY_RESULT_BACKEND: "redis://redis-service:6379/0"
  EMAIL_HOST: "smtp.gmail.com"
  EMAIL_PORT: "587"
  EMAIL_USE_TLS: "True"
  SECURE_SSL_REDIRECT: "True"
  SECURE_HSTS_SECONDS: "31536000"
  SESSION_COOKIE_SECURE: "True"
  CSRF_COOKIE_SECURE: "True"
  FEATURE_FLAGS_AI_ML_FEATURES: "True"
  FEATURE_FLAGS_ADVANCED_ANALYTICS: "True"
  FEATURE_FLAGS_REAL_TIME_NOTIFICATIONS: "True"
```

#### **Secrets for Kubernetes**
```yaml
# secrets.yml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret-key>
  DB_PASSWORD: <base64-encoded-db-password>
  EMAIL_HOST_PASSWORD: <base64-encoded-email-password>
  AWS_ACCESS_KEY_ID: <base64-encoded-aws-access-key>
  AWS_SECRET_ACCESS_KEY: <base64-encoded-aws-secret-key>
  SENTRY_DSN: <base64-encoded-sentry-dsn>
```

---

## 🏥 **Health Checks**

### **Health Check Endpoints**

#### **Django Health Check**
```python
# apps/core/views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import time

def health_check(request):
    """Comprehensive health check endpoint"""
    
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        health_status['checks']['database'] = {
            'status': 'healthy',
            'response_time': time.time() - time.time()
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Cache check
    try:
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        
        health_status['checks']['cache'] = {
            'status': 'healthy' if cache_result == 'ok' else 'unhealthy'
        }
    except Exception as e:
        health_status['checks']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Redis check
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        
        health_status['checks']['redis'] = {
            'status': 'healthy'
        }
    except Exception as e:
        health_status['checks']['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)
```

#### **Health Check Configuration**
```yaml
# health-check.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: health-check-config
data:
  health-check.sh: |
    #!/bin/bash
    set -e
    
    # Check if application is responding
    curl -f http://localhost:8000/health/ || exit 1
    
    # Check database connectivity
    python manage.py dbshell -c "SELECT 1" || exit 1
    
    # Check cache connectivity
    python manage.py shell -c "from django.core.cache import cache; cache.get('test')" || exit 1
    
    echo "Health check passed"
```

### **Monitoring Integration**

#### **Prometheus Metrics**
```python
# apps/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

# Database metrics
DB_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
DB_QUERY_DURATION = Histogram('database_query_duration_seconds', 'Database query duration')

# Cache metrics
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['cache_name'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['cache_name'])

# Custom metrics
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
TICKETS_OPEN = Gauge('tickets_open_total', 'Number of open tickets')
```

#### **Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "Helpdesk Platform Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "singlestat",
        "targets": [
          {
            "expr": "database_connections_active",
            "legendFormat": "Active Connections"
          }
        ]
      }
    ]
  }
}
```

---

## 🔄 **Rollback Procedures**

### **Rollback Strategies**

#### **Database Rollback**
```bash
#!/bin/bash
# scripts/rollback-db.sh

MIGRATION_TARGET=${1:-previous}
ENVIRONMENT=${2:-production}

echo "Rolling back database to $MIGRATION_TARGET for $ENVIRONMENT"

# Create backup before rollback
./scripts/backup-db.sh $ENVIRONMENT

# Rollback migrations
python manage.py migrate $MIGRATION_TARGET --settings=config.settings.$ENVIRONMENT

# Verify rollback
python manage.py showmigrations --settings=config.settings.$ENVIRONMENT

echo "Database rollback completed"
```

#### **Application Rollback**
```bash
#!/bin/bash
# scripts/rollback-app.sh

PREVIOUS_VERSION=${1:-previous}
NAMESPACE=${2:-default}

echo "Rolling back application to $PREVIOUS_VERSION"

# Get previous deployment
PREVIOUS_DEPLOYMENT=$(kubectl get deployment helpdesk-deployment -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}')

# Rollback deployment
kubectl rollout undo deployment/helpdesk-deployment -n $NAMESPACE

# Wait for rollout
kubectl rollout status deployment/helpdesk-deployment -n $NAMESPACE

# Verify rollback
kubectl get pods -l app=helpdesk -n $NAMESPACE

echo "Application rollback completed"
```

#### **Blue-Green Rollback**
```bash
#!/bin/bash
# scripts/blue-green-rollback.sh

echo "Rolling back blue-green deployment"

# Get current version
CURRENT_VERSION=$(kubectl get service helpdesk-service -o jsonpath='{.spec.selector.version}')

# Switch back to previous version
if [ "$CURRENT_VERSION" = "blue" ]; then
    kubectl patch service helpdesk-service -p '{"spec":{"selector":{"version":"green"}}}'
else
    kubectl patch service helpdesk-service -p '{"spec":{"selector":{"version":"blue"}}}'
fi

# Wait for switch
sleep 30

# Verify rollback
kubectl get pods -l app=helpdesk

echo "Blue-green rollback completed"
```

### **Automated Rollback**

#### **Rollback Conditions**
```yaml
# rollback-conditions.yml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: helpdesk-rollout
spec:
  strategy:
    canary:
      analysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: helpdesk-service
        - name: error-rate-threshold
          value: "5"
        - name: response-time-threshold
          value: "1000"
      steps:
      - setWeight: 20
      - analysis:
          templates:
          - templateName: success-rate
          args:
          - name: service-name
            value: helpdesk-service
      - setWeight: 40
      - analysis:
          templates:
          - templateName: success-rate
      - setWeight: 60
      - analysis:
          templates:
          - templateName: success-rate
      - setWeight: 80
      - analysis:
          templates:
          - templateName: success-rate
```

#### **Rollback Triggers**
```python
# scripts/rollback-triggers.py
import requests
import time
import os

class RollbackTrigger:
    def __init__(self):
        self.error_threshold = 5  # 5% error rate
        self.response_time_threshold = 1000  # 1 second
        self.check_interval = 60  # 1 minute
    
    def check_metrics(self):
        """Check application metrics for rollback conditions"""
        
        # Get error rate
        error_rate = self.get_error_rate()
        
        # Get response time
        response_time = self.get_response_time()
        
        # Check if rollback is needed
        if error_rate > self.error_threshold:
            print(f"Error rate {error_rate}% exceeds threshold {self.error_threshold}%")
            return True
        
        if response_time > self.response_time_threshold:
            print(f"Response time {response_time}ms exceeds threshold {self.response_time_threshold}ms")
            return True
        
        return False
    
    def get_error_rate(self):
        """Get current error rate from monitoring system"""
        # Implementation depends on monitoring system
        # This is a placeholder
        return 2.5
    
    def get_response_time(self):
        """Get current response time from monitoring system"""
        # Implementation depends on monitoring system
        # This is a placeholder
        return 500
    
    def trigger_rollback(self):
        """Trigger application rollback"""
        print("Triggering rollback...")
        
        # Execute rollback script
        os.system("./scripts/rollback-app.sh")
        
        print("Rollback triggered successfully")
    
    def run(self):
        """Run continuous monitoring"""
        while True:
            if self.check_metrics():
                self.trigger_rollback()
                break
            
            time.sleep(self.check_interval)

if __name__ == "__main__":
    trigger = RollbackTrigger()
    trigger.run()
```

---

## 📊 **Monitoring and Logging**

### **Logging Configuration**

#### **Structured Logging**
```python
# apps/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'organization_id'):
            log_entry['organization_id'] = record.organization_id
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

# Configure logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': JSONFormatter,
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/error.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
            'level': 'ERROR',
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
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'helpdesk': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

#### **Application Metrics**
```python
# apps/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from django.http import HttpResponse
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
TICKETS_CREATED = Counter('tickets_created_total', 'Total tickets created')
TICKETS_RESOLVED = Counter('tickets_resolved_total', 'Total tickets resolved')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
OPEN_TICKETS = Gauge('tickets_open_total', 'Number of open tickets')

# Database metrics
DB_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
DB_QUERY_DURATION = Histogram('database_query_duration_seconds', 'Database query duration')

# Cache metrics
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['cache_name'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['cache_name'])

def metrics_view(request):
    """Prometheus metrics endpoint"""
    return HttpResponse(generate_latest(), content_type='text/plain')
```

### **Alerting Configuration**

#### **Alert Rules**
```yaml
# alert-rules.yml
groups:
- name: helpdesk-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"
  
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"
  
  - alert: DatabaseConnectionsHigh
    expr: database_connections_active > 80
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "High database connection count"
      description: "Database connections: {{ $value }}"
  
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "Service {{ $labels.instance }} is down"
```

#### **Notification Channels**
```yaml
# notification-channels.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
data:
  alertmanager.yml: |
    global:
      smtp_smarthost: 'smtp.gmail.com:587'
      smtp_from: 'alerts@helpdesk.com'
    
    route:
      group_by: ['alertname']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'web.hook'
      routes:
      - match:
          severity: critical
        receiver: 'critical-alerts'
      - match:
          severity: warning
        receiver: 'warning-alerts'
    
    receivers:
    - name: 'web.hook'
      webhook_configs:
      - url: 'http://webhook:5001/'
    
    - name: 'critical-alerts'
      email_configs:
      - to: 'admin@helpdesk.com'
        subject: 'Critical Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
      slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        title: 'Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    
    - name: 'warning-alerts'
      email_configs:
      - to: 'team@helpdesk.com'
        subject: 'Warning Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

---

## 🔒 **Security Considerations**

### **Security Scanning**

#### **Container Security**
```bash
#!/bin/bash
# scripts/security-scan.sh

set -e

IMAGE_NAME=${1:-helpdesk-backend}
IMAGE_TAG=${2:-latest}
FULL_IMAGE="$IMAGE_NAME:$IMAGE_TAG"

echo "Running security scan for $FULL_IMAGE"

# Trivy vulnerability scan
echo "Running Trivy vulnerability scan..."
trivy image --severity HIGH,CRITICAL --format json --output trivy-report.json $FULL_IMAGE

# Trivy secret scan
echo "Running Trivy secret scan..."
trivy image --scanners secret --format json --output trivy-secrets.json $FULL_IMAGE

# Docker Bench Security
echo "Running Docker Bench Security..."
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /etc:/etc:ro \
  -v /usr/bin/containerd:/usr/bin/containerd:ro \
  -v /usr/bin/runc:/usr/bin/runc:ro \
  -v /usr/lib/systemd:/usr/lib/systemd:ro \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --label docker_bench_security \
  docker/docker-bench-security

# Check for security issues
if [ -f trivy-report.json ]; then
    HIGH_VULNS=$(jq '.Results[].Vulnerabilities[] | select(.Severity == "HIGH") | .VulnerabilityID' trivy-report.json | wc -l)
    CRITICAL_VULNS=$(jq '.Results[].Vulnerabilities[] | select(.Severity == "CRITICAL") | .VulnerabilityID' trivy-report.json | wc -l)
    
    if [ $CRITICAL_VULNS -gt 0 ]; then
        echo "❌ Critical vulnerabilities found: $CRITICAL_VULNS"
        exit 1
    elif [ $HIGH_VULNS -gt 5 ]; then
        echo "⚠️ High vulnerabilities found: $HIGH_VULNS"
        exit 1
    else
        echo "✅ Security scan passed"
    fi
fi

echo "Security scan completed"
```

#### **Dependency Scanning**
```bash
#!/bin/bash
# scripts/dependency-scan.sh

set -e

echo "Running dependency security scan"

# Python dependencies
echo "Scanning Python dependencies..."
safety check --json --output safety-report.json

# Node.js dependencies
echo "Scanning Node.js dependencies..."
cd customer-portal
npm audit --json > ../npm-audit-report.json
cd ..

# Check for high/critical vulnerabilities
PYTHON_VULNS=$(jq '.vulnerabilities | length' safety-report.json)
NODE_VULNS=$(jq '.vulnerabilities | length' npm-audit-report.json)

if [ $PYTHON_VULNS -gt 0 ]; then
    echo "❌ Python vulnerabilities found: $PYTHON_VULNS"
    exit 1
fi

if [ $NODE_VULNS -gt 0 ]; then
    echo "❌ Node.js vulnerabilities found: $NODE_VULNS"
    exit 1
fi

echo "✅ Dependency scan passed"
```

### **Security Hardening**

#### **Container Security**
```dockerfile
# Security-hardened Dockerfile
FROM python:3.11-slim as base

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set security options
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy application
COPY --chown=appuser:appuser . /app/

# Create directories with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### **Network Security**
```yaml
# network-policy.yml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: helpdesk-network-policy
spec:
  podSelector:
    matchLabels:
      app: helpdesk
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector:
        matchLabels:
          name: cache
    ports:
    - protocol: TCP
      port: 6379
```

---

## 🔧 **Troubleshooting**

### **Common Deployment Issues**

#### **Issue 1: Database Connection Failed**
```bash
# Check database connectivity
kubectl exec -it deployment/helpdesk-backend -- python manage.py dbshell

# Check database credentials
kubectl get secret db-secret -o yaml

# Check database service
kubectl get service database-service

# Check database pods
kubectl get pods -l app=database
```

#### **Issue 2: Application Not Starting**
```bash
# Check application logs
kubectl logs deployment/helpdesk-backend

# Check application status
kubectl get pods -l app=helpdesk

# Check application events
kubectl describe pod <pod-name>

# Check resource usage
kubectl top pods -l app=helpdesk
```

#### **Issue 3: Health Check Failing**
```bash
# Check health endpoint
kubectl exec -it deployment/helpdesk-backend -- curl http://localhost:8000/health/

# Check health check configuration
kubectl get deployment helpdesk-backend -o yaml

# Check application readiness
kubectl get pods -l app=helpdesk -o wide
```

### **Debugging Scripts**

#### **Debug Script**
```bash
#!/bin/bash
# scripts/debug.sh

NAMESPACE=${1:-default}
POD_NAME=${2:-}

echo "Debugging helpdesk deployment in namespace $NAMESPACE"

# Get pod information
if [ -z "$POD_NAME" ]; then
    POD_NAME=$(kubectl get pods -l app=helpdesk -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}')
fi

echo "Debugging pod: $POD_NAME"

# Check pod status
echo "=== Pod Status ==="
kubectl get pod $POD_NAME -n $NAMESPACE -o wide

# Check pod events
echo "=== Pod Events ==="
kubectl describe pod $POD_NAME -n $NAMESPACE

# Check application logs
echo "=== Application Logs ==="
kubectl logs $POD_NAME -n $NAMESPACE --tail=100

# Check resource usage
echo "=== Resource Usage ==="
kubectl top pod $POD_NAME -n $NAMESPACE

# Check environment variables
echo "=== Environment Variables ==="
kubectl exec $POD_NAME -n $NAMESPACE -- env | grep -E "(DJANGO|DATABASE|REDIS)"

# Check database connectivity
echo "=== Database Connectivity ==="
kubectl exec $POD_NAME -n $NAMESPACE -- python manage.py dbshell -c "SELECT 1"

# Check cache connectivity
echo "=== Cache Connectivity ==="
kubectl exec $POD_NAME -n $NAMESPACE -- python manage.py shell -c "from django.core.cache import cache; cache.get('test')"

echo "Debug completed"
```

#### **Performance Debug Script**
```bash
#!/bin/bash
# scripts/performance-debug.sh

NAMESPACE=${1:-default}

echo "Performance debugging for helpdesk deployment"

# Check resource usage
echo "=== Resource Usage ==="
kubectl top pods -l app=helpdesk -n $NAMESPACE

# Check resource limits
echo "=== Resource Limits ==="
kubectl get deployment helpdesk-backend -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].resources}'

# Check application metrics
echo "=== Application Metrics ==="
kubectl port-forward deployment/helpdesk-backend 8000:8000 -n $NAMESPACE &
PF_PID=$!

sleep 5
curl -s http://localhost:8000/metrics/ | grep -E "(http_requests_total|http_request_duration_seconds)"

kill $PF_PID

# Check database performance
echo "=== Database Performance ==="
kubectl exec deployment/helpdesk-backend -n $NAMESPACE -- python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT * FROM pg_stat_activity WHERE state = \\'active\\'')
    print('Active connections:', cursor.rowcount)
"

echo "Performance debug completed"
```

### **Recovery Procedures**

#### **Database Recovery**
```bash
#!/bin/bash
# scripts/database-recovery.sh

BACKUP_FILE=${1:-latest}
ENVIRONMENT=${2:-production}

echo "Recovering database from backup: $BACKUP_FILE"

# Stop application
kubectl scale deployment helpdesk-backend --replicas=0

# Restore database
kubectl exec -it deployment/database -- pg_restore -U helpdesk_user -d helpdesk_production /backups/$BACKUP_FILE

# Run migrations
kubectl exec -it deployment/helpdesk-backend -- python manage.py migrate

# Start application
kubectl scale deployment helpdesk-backend --replicas=3

echo "Database recovery completed"
```

#### **Application Recovery**
```bash
#!/bin/bash
# scripts/application-recovery.sh

NAMESPACE=${1:-default}

echo "Recovering helpdesk application"

# Delete problematic pods
kubectl delete pods -l app=helpdesk -n $NAMESPACE

# Wait for pods to restart
kubectl wait --for=condition=ready pod -l app=helpdesk -n $NAMESPACE --timeout=300s

# Check application health
kubectl get pods -l app=helpdesk -n $NAMESPACE

# Verify application is responding
kubectl exec -it deployment/helpdesk-backend -n $NAMESPACE -- curl http://localhost:8000/health/

echo "Application recovery completed"
```

---

## 📚 **Best Practices**

### **1. Deployment Best Practices**

#### **Pre-Deployment Checklist**
- [ ] All tests passing
- [ ] Security scans completed
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Health checks implemented
- [ ] Monitoring configured
- [ ] Rollback plan ready
- [ ] Team notified

#### **Post-Deployment Checklist**
- [ ] Application responding
- [ ] Health checks passing
- [ ] Metrics being collected
- [ ] Logs being generated
- [ ] Alerts configured
- [ ] Performance acceptable
- [ ] User acceptance testing
- [ ] Documentation updated

### **2. Security Best Practices**

#### **Container Security**
- Use minimal base images
- Run as non-root user
- Scan for vulnerabilities
- Keep images updated
- Use multi-stage builds
- Implement security policies

#### **Network Security**
- Use network policies
- Encrypt traffic
- Implement firewalls
- Monitor network traffic
- Use secure protocols
- Implement rate limiting

### **3. Monitoring Best Practices**

#### **Metrics Collection**
- Collect business metrics
- Monitor system resources
- Track application performance
- Monitor security events
- Implement alerting
- Use dashboards

#### **Logging**
- Use structured logging
- Include correlation IDs
- Log security events
- Implement log rotation
- Use centralized logging
- Monitor log quality

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: DevOps Team
