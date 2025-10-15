# 🚀 **Deployment Documentation**

**Version:** 1.0.0  
**Last Updated:** October 13, 2025

---

## 📋 **Table of Contents**

- [Deployment Overview](#deployment-overview)
- [Environment Preparation](#environment-preparation)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Database Deployment](#database-deployment)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring Setup](#monitoring-setup)
- [Backup and Recovery](#backup-and-recovery)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

---

## 🎯 **Deployment Overview**

This document provides comprehensive deployment instructions for the Helpdesk Platform across different environments and platforms.

### **Deployment Options**
- **Docker**: Local and containerized deployment
- **Cloud Platforms**: AWS, Digital Ocean, Google Cloud
- **Traditional Servers**: Ubuntu, CentOS, Windows Server
- **Kubernetes**: Container orchestration

### **Environment Types**
- **Development**: Local development environment
- **Staging**: Pre-production testing environment
- **Production**: Live production environment

---

## 🛠️ **Environment Preparation**

### **System Requirements**

#### **Minimum Requirements**
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: 100 Mbps

#### **Recommended Requirements**
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Network**: 1 Gbps

#### **Production Requirements**
- **CPU**: 8 cores
- **RAM**: 16GB
- **Storage**: 100GB SSD
- **Network**: 10 Gbps

### **Software Requirements**

#### **Operating System**
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+
- **Windows**: Windows Server 2019+
- **macOS**: macOS 10.15+ (development only)

#### **Required Software**
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Python**: 3.11+ (if not using Docker)
- **Node.js**: 18+ (if not using Docker)

### **Network Configuration**

#### **Port Requirements**
- **80**: HTTP (redirects to HTTPS)
- **443**: HTTPS
- **8000**: Django API (internal)
- **3000**: React Frontend (internal)
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)

#### **Firewall Configuration**
```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## 🐳 **Docker Deployment**

### **Local Development Deployment**

#### **1. Clone Repository**
```bash
git clone https://github.com/your-username/helpdesk-platform.git
cd helpdesk-platform
```

#### **2. Environment Setup**
```bash
# Copy environment file
cp env.example .env

# Edit environment variables
nano .env
```

#### **3. Start Services**
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### **4. Initialize Database**
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec web python manage.py loaddata fixtures/sample_data.json
```

#### **5. Verify Deployment**
```bash
# Check API health
curl http://localhost:8000/health/

# Check frontend
curl http://localhost:3000

# Check database
docker-compose exec db psql -U helpdesk_user -d helpdesk -c "SELECT version();"
```

### **Production Docker Deployment**

#### **1. Production Environment File**
```bash
# Create production environment file
cp env.example .env.production

# Edit production variables
nano .env.production
```

**Production Environment Variables:**
```bash
# Django Settings
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database
DB_HOST=your-db-host
DB_NAME=helpdesk_production
DB_USER=helpdesk_user
DB_PASSWORD=your-secure-password
DB_PORT=5432

# Redis
REDIS_URL=redis://your-redis-host:6379/0

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# External Services
OPENAI_API_KEY=your-openai-key
GOOGLE_MAPS_API_KEY=your-maps-key
TWILIO_ACCOUNT_SID=your-twilio-sid
SENDGRID_API_KEY=your-sendgrid-key
```

#### **2. Production Docker Compose**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    build:
      context: ./core
      dockerfile: Dockerfile
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
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
    restart: unless-stopped

  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: helpdesk_production
      POSTGRES_USER: helpdesk_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

#### **3. Deploy Production**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Check deployment
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

---

## ☁️ **Cloud Deployment**

### **AWS Deployment**

#### **1. AWS ECS Deployment**

**Create ECS Cluster:**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name helpdesk-platform

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster helpdesk-platform \
  --service-name helpdesk-web \
  --task-definition helpdesk-platform:1 \
  --desired-count 2
```

**Task Definition (task-definition.json):**
```json
{
  "family": "helpdesk-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "django-app",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/helpdesk-django:latest",
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
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "django"
        }
      }
    }
  ]
}
```

#### **2. AWS RDS Database**
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier helpdesk-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username helpdesk_user \
  --master-user-password your-secure-password \
  --allocated-storage 20 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-12345678 \
  --db-subnet-group-name helpdesk-subnet-group
```

#### **3. AWS ElastiCache Redis**
```bash
# Create ElastiCache cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id helpdesk-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --vpc-security-group-ids sg-12345678
```

### **Digital Ocean Deployment**

#### **1. App Platform Deployment**

**Create App Spec (app.yaml):**
```yaml
name: helpdesk-platform
services:
- name: django
  source_dir: /core
  github:
    repo: your-username/helpdesk-platform
    branch: main
  run_command: gunicorn config.wsgi:application --bind 0.0.0.0:8080
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  envs:
  - key: DJANGO_SETTINGS_MODULE
    value: config.settings.production
  - key: SECRET_KEY
    value: your-secret-key
  - key: DATABASE_URL
    value: postgresql://user:pass@host:port/db
  - key: REDIS_URL
    value: redis://host:port/0
  - key: ALLOWED_HOSTS
    value: your-domain.com,api.your-domain.com

- name: frontend
  source_dir: /customer-portal
  github:
    repo: your-username/helpdesk-platform
    branch: main
  run_command: npm run build && npm run start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: NODE_ENV
    value: production
  - key: REACT_APP_API_URL
    value: https://api.your-domain.com

databases:
- name: helpdesk-postgres
  engine: PG
  version: "15"
  size: db-s-1vcpu-1gb
  num_nodes: 1

- name: helpdesk-redis
  engine: REDIS
  version: "7"
  size: db-s-1vcpu-1gb
  num_nodes: 1
```

#### **2. Deploy to Digital Ocean**
```bash
# Install doctl
snap install doctl

# Authenticate
doctl auth init

# Create app
doctl apps create --spec app.yaml

# Get app status
doctl apps get APP_ID
```

### **Google Cloud Deployment**

#### **1. Cloud Run Deployment**

**Create Cloud Run Service:**
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/helpdesk-platform

# Deploy to Cloud Run
gcloud run deploy helpdesk-platform \
  --image gcr.io/PROJECT_ID/helpdesk-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DJANGO_SETTINGS_MODULE=config.settings.production
```

#### **2. Cloud SQL Database**
```bash
# Create Cloud SQL instance
gcloud sql instances create helpdesk-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create helpdesk --instance=helpdesk-db

# Create user
gcloud sql users create helpdesk_user --instance=helpdesk-db --password=your-password
```

---

## 🗄️ **Database Deployment**

### **PostgreSQL Setup**

#### **1. Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib postgis

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib postgis
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

#### **2. Configure Database**
```bash
# Create database
sudo -u postgres psql
CREATE DATABASE helpdesk;
CREATE USER helpdesk_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE helpdesk TO helpdesk_user;
\q

# Enable PostGIS
sudo -u postgres psql -d helpdesk -c "CREATE EXTENSION postgis;"
```

#### **3. Database Migrations**
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data
python manage.py loaddata fixtures/initial_data.json
```

### **Redis Setup**

#### **1. Install Redis**
```bash
# Ubuntu/Debian
sudo apt install redis-server

# CentOS/RHEL
sudo yum install redis
sudo systemctl enable redis
sudo systemctl start redis
```

#### **2. Configure Redis**
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Set password
requirepass your-redis-password

# Restart Redis
sudo systemctl restart redis
```

---

## 🔒 **SSL/TLS Configuration**

### **Let's Encrypt SSL**

#### **1. Install Certbot**
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

#### **2. Obtain SSL Certificate**
```bash
# Get certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Test renewal
sudo certbot renew --dry-run
```

#### **3. Auto-renewal**
```bash
# Add to crontab
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

### **Nginx SSL Configuration**

#### **1. SSL Configuration**
```nginx
# /etc/nginx/sites-available/helpdesk-platform
server {
    listen 80;
    server_name your-domain.com api.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com api.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 **Monitoring Setup**

### **Application Monitoring**

#### **1. Health Checks**
```python
# Add to Django settings
HEALTH_CHECK_ENABLED = True
HEALTH_CHECK_URL = '/health/'

# Create health check endpoint
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
```

#### **2. Logging Configuration**
```python
# Add to Django settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/helpdesk/django.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### **System Monitoring**

#### **1. Prometheus Setup**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'helpdesk-platform'
    static_configs:
      - targets: ['localhost:8000']
```

#### **2. Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "Helpdesk Platform",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## 💾 **Backup and Recovery**

### **Database Backup**

#### **1. Automated Backup Script**
```bash
#!/bin/bash
# backup.sh

# Set variables
DB_NAME="helpdesk"
DB_USER="helpdesk_user"
BACKUP_DIR="/var/backups/helpdesk"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
pg_dump -h localhost -U $DB_USER $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove old backups (keep 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/
```

#### **2. Backup Schedule**
```bash
# Add to crontab
sudo crontab -e
# Add this line:
0 2 * * * /path/to/backup.sh
```

### **File Backup**

#### **1. Media Files Backup**
```bash
#!/bin/bash
# media-backup.sh

# Set variables
MEDIA_DIR="/var/www/helpdesk/media"
BACKUP_DIR="/var/backups/helpdesk/media"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $MEDIA_DIR .

# Upload to S3
aws s3 cp $BACKUP_DIR/media_$DATE.tar.gz s3://your-backup-bucket/media/
```

### **Recovery Procedures**

#### **1. Database Recovery**
```bash
# Stop application
docker-compose down

# Restore database
gunzip backup_20240101_020000.sql.gz
psql -h localhost -U helpdesk_user -d helpdesk < backup_20240101_020000.sql

# Start application
docker-compose up -d
```

#### **2. Full System Recovery**
```bash
# Restore from backup
aws s3 cp s3://your-backup-bucket/backup_20240101_020000.sql.gz ./
gunzip backup_20240101_020000.sql.gz
psql -h localhost -U helpdesk_user -d helpdesk < backup_20240101_020000.sql

# Restore media files
aws s3 cp s3://your-backup-bucket/media/media_20240101_020000.tar.gz ./
tar -xzf media_20240101_020000.tar.gz -C /var/www/helpdesk/media/
```

---

## 🔄 **Rollback Procedures**

### **Application Rollback**

#### **1. Docker Rollback**
```bash
# Stop current version
docker-compose down

# Rollback to previous version
git checkout v1.0.0
docker-compose up -d

# Verify rollback
curl http://localhost:8000/health/
```

#### **2. Database Rollback**
```bash
# Rollback migrations
python manage.py migrate 1.0.0

# Or restore from backup
gunzip backup_20240101_020000.sql.gz
psql -h localhost -U helpdesk_user -d helpdesk < backup_20240101_020000.sql
```

### **Emergency Procedures**

#### **1. Emergency Rollback Script**
```bash
#!/bin/bash
# emergency-rollback.sh

echo "Starting emergency rollback..."

# Stop all services
docker-compose down

# Rollback to last known good version
git checkout HEAD~1

# Restore database from backup
gunzip /var/backups/helpdesk/backup_latest.sql.gz
psql -h localhost -U helpdesk_user -d helpdesk < /var/backups/helpdesk/backup_latest.sql

# Start services
docker-compose up -d

# Verify rollback
curl http://localhost:8000/health/

echo "Emergency rollback completed."
```

---

## 🐛 **Troubleshooting**

### **Common Deployment Issues**

#### **1. Service Won't Start**
```bash
# Check logs
docker-compose logs web
docker-compose logs db
docker-compose logs redis

# Check service status
docker-compose ps

# Check resource usage
docker stats
```

#### **2. Database Connection Issues**
```bash
# Test database connection
docker-compose exec web python manage.py dbshell

# Check database logs
docker-compose logs db

# Test connection string
python -c "import psycopg2; psycopg2.connect('postgresql://user:pass@host:port/db')"
```

#### **3. SSL Certificate Issues**
```bash
# Check certificate
openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout

# Test SSL
curl -I https://your-domain.com

# Renew certificate
sudo certbot renew
```

### **Performance Issues**

#### **1. Slow Response Times**
```bash
# Check database performance
docker-compose exec db psql -U helpdesk_user -d helpdesk -c "SELECT * FROM pg_stat_activity;"

# Check Redis performance
docker-compose exec redis redis-cli info stats

# Check application logs
docker-compose logs web | grep -i error
```

#### **2. Memory Issues**
```bash
# Check memory usage
docker stats

# Check system memory
free -h

# Check swap usage
swapon -s
```

---

## 📚 **Additional Resources**

### **Documentation**
- [README.md](../README.md) - Project overview
- [Architecture](ARCHITECTURE.md) - System architecture
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
- [Monitoring](MONITORING.md) - Monitoring setup

### **External Resources**
- [Docker Documentation](https://docs.docker.com/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Digital Ocean Documentation](https://docs.digitalocean.com/)
- [Google Cloud Documentation](https://cloud.google.com/docs)

### **Tools**
- **Docker**: Container management
- **Kubernetes**: Container orchestration
- **Terraform**: Infrastructure as code
- **Ansible**: Configuration management
- **Prometheus**: Monitoring
- **Grafana**: Visualization

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: DevOps Team
