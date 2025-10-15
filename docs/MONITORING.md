# 📊 **Monitoring Setup Guide**

**Version:** 1.0.0  
**Last Updated:** October 13, 2025

---

## 📋 **Table of Contents**

- [Monitoring Overview](#monitoring-overview)
- [Application Monitoring](#application-monitoring)
- [Infrastructure Monitoring](#infrastructure-monitoring)
- [Log Management](#log-management)
- [Alerting](#alerting)
- [Performance Monitoring](#performance-monitoring)
- [Security Monitoring](#security-monitoring)
- [Dashboard Setup](#dashboard-setup)
- [Monitoring Tools](#monitoring-tools)
- [Best Practices](#best-practices)

---

## 🎯 **Monitoring Overview**

This guide provides comprehensive monitoring setup for the Helpdesk Platform to ensure optimal performance, reliability, and security.

### **Monitoring Objectives**
- **Availability**: Ensure 99.9% uptime
- **Performance**: Monitor response times and throughput
- **Security**: Detect and prevent security threats
- **Capacity**: Plan for growth and scaling
- **Compliance**: Meet regulatory requirements

### **Monitoring Layers**
- **Application Layer**: Django, React, API performance
- **Infrastructure Layer**: Servers, databases, networks
- **Business Layer**: User metrics, feature usage
- **Security Layer**: Threats, vulnerabilities, access

---

## 🔍 **Application Monitoring**

### **Django Application Monitoring**

#### **1. Health Checks**
```python
# apps/api/views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import time

def health_check(request):
    """Comprehensive health check endpoint."""
    start_time = time.time()
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        cache_status = "healthy" if cache.get('health_check') == 'ok' else "unhealthy"
    except Exception as e:
        cache_status = f"unhealthy: {str(e)}"
    
    # Check response time
    response_time = (time.time() - start_time) * 1000
    
    return JsonResponse({
        'status': 'healthy' if db_status == 'healthy' and cache_status == 'healthy' else 'unhealthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'checks': {
            'database': db_status,
            'cache': cache_status,
            'response_time_ms': response_time
        }
    })
```

#### **2. Performance Metrics**
```python
# apps/api/middleware.py
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class PerformanceMiddleware(MiddlewareMixin):
    """Middleware to track performance metrics."""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log slow requests
            if duration > 1.0:  # 1 second threshold
                logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
            
            # Add performance headers
            response['X-Response-Time'] = f"{duration:.3f}s"
            
        return response
```

#### **3. Database Monitoring**
```python
# apps/api/monitoring.py
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class DatabaseMonitor:
    """Monitor database performance and health."""
    
    @staticmethod
    def get_connection_count():
        """Get current database connections."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """)
            return cursor.fetchone()[0]
    
    @staticmethod
    def get_slow_queries():
        """Get slow queries from PostgreSQL."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT query, mean_time, calls
                FROM pg_stat_statements
                WHERE mean_time > 1000  -- 1 second threshold
                ORDER BY mean_time DESC
                LIMIT 10
            """)
            return cursor.fetchall()
    
    @staticmethod
    def get_database_size():
        """Get database size."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            return cursor.fetchone()[0]
```

### **React Frontend Monitoring**

#### **1. Error Tracking**
```typescript
// src/utils/errorTracking.ts
import { captureException, captureMessage } from '@sentry/react';

export const trackError = (error: Error, context?: any) => {
  console.error('Application Error:', error);
  captureException(error, { extra: context });
};

export const trackMessage = (message: string, level: 'info' | 'warning' | 'error' = 'info') => {
  console.log(`[${level.toUpperCase()}] ${message}`);
  captureMessage(message, level);
};

// Global error handler
window.addEventListener('error', (event) => {
  trackError(event.error, {
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
  });
});

window.addEventListener('unhandledrejection', (event) => {
  trackError(new Error(event.reason), {
    type: 'unhandledrejection',
  });
});
```

#### **2. Performance Monitoring**
```typescript
// src/utils/performanceMonitoring.ts
export const trackPageLoad = () => {
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  
  const metrics = {
    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
    loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
    totalTime: navigation.loadEventEnd - navigation.fetchStart,
  };
  
  console.log('Page Load Metrics:', metrics);
  
  // Send to monitoring service
  fetch('/api/v1/analytics/performance/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(metrics),
  });
};

export const trackUserInteraction = (action: string, duration: number) => {
  console.log(`User Action: ${action} took ${duration}ms`);
  
  // Send to analytics
  fetch('/api/v1/analytics/interactions/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, duration }),
  });
};
```

---

## 🖥️ **Infrastructure Monitoring**

### **System Metrics**

#### **1. CPU Monitoring**
```bash
#!/bin/bash
# monitor_cpu.sh

# Get CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

# Alert if CPU usage > 80%
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "ALERT: High CPU usage: ${CPU_USAGE}%"
    # Send alert notification
fi

# Log CPU usage
echo "$(date): CPU Usage: ${CPU_USAGE}%" >> /var/log/monitoring/cpu.log
```

#### **2. Memory Monitoring**
```bash
#!/bin/bash
# monitor_memory.sh

# Get memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')

# Alert if memory usage > 85%
if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
    echo "ALERT: High memory usage: ${MEMORY_USAGE}%"
    # Send alert notification
fi

# Log memory usage
echo "$(date): Memory Usage: ${MEMORY_USAGE}%" >> /var/log/monitoring/memory.log
```

#### **3. Disk Monitoring**
```bash
#!/bin/bash
# monitor_disk.sh

# Get disk usage
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)

# Alert if disk usage > 90%
if [ $DISK_USAGE -gt 90 ]; then
    echo "ALERT: High disk usage: ${DISK_USAGE}%"
    # Send alert notification
fi

# Log disk usage
echo "$(date): Disk Usage: ${DISK_USAGE}%" >> /var/log/monitoring/disk.log
```

### **Docker Monitoring**

#### **1. Container Health Checks**
```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: ./core
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
  db:
    image: postgis/postgis:15-3.3
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U helpdesk_user -d helpdesk"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### **2. Container Metrics**
```bash
#!/bin/bash
# monitor_containers.sh

# Get container stats
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" > /tmp/container_stats.txt

# Check for unhealthy containers
UNHEALTHY=$(docker ps --filter "health=unhealthy" --format "{{.Names}}")

if [ ! -z "$UNHEALTHY" ]; then
    echo "ALERT: Unhealthy containers: $UNHEALTHY"
    # Send alert notification
fi

# Log container stats
cat /tmp/container_stats.txt >> /var/log/monitoring/containers.log
```

---

## 📝 **Log Management**

### **Centralized Logging**

#### **1. ELK Stack Setup**
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    ports:
      - "5044:5044"
    volumes:
      - ./logstash/config/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

#### **2. Logstash Configuration**
```ruby
# logstash/config/logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "helpdesk-web" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }
  
  if [fields][service] == "helpdesk-db" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "helpdesk-logs-%{+YYYY.MM.dd}"
  }
}
```

#### **3. Filebeat Configuration**
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/helpdesk/*.log
  fields:
    service: helpdesk-web
  fields_under_root: true

output.logstash:
  hosts: ["logstash:5044"]

processors:
- add_host_metadata:
    when.not.contains.tags: forwarded
```

### **Application Logging**

#### **1. Django Logging Configuration**
```python
# config/settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/helpdesk/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/helpdesk/error.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
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

---

## 🚨 **Alerting**

### **Alert Rules**

#### **1. Prometheus Alert Rules**
```yaml
# prometheus/alerts.yml
groups:
- name: helpdesk-platform
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"

  - alert: DatabaseDown
    expr: up{job="postgresql"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database is down"
      description: "PostgreSQL database is not responding"

  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage"
      description: "CPU usage is {{ $value }}%"

  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value }}%"
```

#### **2. Alertmanager Configuration**
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@helpdesk-platform.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://localhost:5001/'

- name: 'email'
  email_configs:
  - to: 'admin@helpdesk-platform.com'
    subject: 'Helpdesk Platform Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
```

### **Notification Channels**

#### **1. Slack Integration**
```python
# apps/monitoring/notifications.py
import requests
import json

class SlackNotifier:
    """Send alerts to Slack."""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_alert(self, title, message, severity='warning'):
        """Send alert to Slack."""
        color = {
            'info': '#36a64f',
            'warning': '#ff9500',
            'error': '#ff0000',
            'critical': '#8b0000'
        }.get(severity, '#ff9500')
        
        payload = {
            'attachments': [{
                'color': color,
                'title': title,
                'text': message,
                'timestamp': int(time.time())
            }]
        }
        
        response = requests.post(self.webhook_url, json=payload)
        return response.status_code == 200
```

#### **2. Email Notifications**
```python
# apps/monitoring/email.py
from django.core.mail import send_mail
from django.conf import settings

class EmailNotifier:
    """Send email notifications."""
    
    @staticmethod
    def send_alert(subject, message, recipients=None):
        """Send alert email."""
        if recipients is None:
            recipients = ['admin@helpdesk-platform.com']
        
        send_mail(
            subject=f'[ALERT] {subject}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
```

---

## 📈 **Performance Monitoring**

### **Application Performance**

#### **1. APM Setup**
```python
# config/settings/production.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_celery_beat',
    'django_celery_results',
    'django_ratelimit',
    'django_cryptography',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'drf_spectacular',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    'debug_toolbar',  # For development
    'django_prometheus',  # For metrics
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'apps.organizations.middleware.TenantMiddleware',
    'apps.security.network_security.SecurityMiddleware',
    'apps.api.global_error_handler.GlobalErrorMiddleware',
    'apps.features.middleware.FeatureFlagMiddleware',
    'apps.features.middleware.FeatureUsageMiddleware',
    'apps.features.middleware.FeatureHealthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

#### **2. Custom Metrics**
```python
# apps/monitoring/metrics.py
from django_prometheus.models import MetricsModelMixin
from django.db import models

class TicketMetrics(MetricsModelMixin, models.Model):
    """Track ticket-related metrics."""
    
    total_tickets = models.PositiveIntegerField(default=0)
    open_tickets = models.PositiveIntegerField(default=0)
    closed_tickets = models.PositiveIntegerField(default=0)
    avg_resolution_time = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'ticket_metrics'

# Custom metrics
from django_prometheus.models import MetricsModelMixin
from django.db import models

class CustomMetrics(MetricsModelMixin, models.Model):
    """Custom application metrics."""
    
    # API metrics
    api_requests_total = models.PositiveIntegerField(default=0)
    api_errors_total = models.PositiveIntegerField(default=0)
    api_response_time_seconds = models.FloatField(default=0.0)
    
    # User metrics
    active_users_total = models.PositiveIntegerField(default=0)
    new_users_total = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'custom_metrics'
```

### **Database Performance**

#### **1. Query Monitoring**
```python
# apps/monitoring/database.py
from django.db import connection
from django.core.cache import cache
import time

class DatabaseMonitor:
    """Monitor database performance."""
    
    @staticmethod
    def get_slow_queries():
        """Get slow queries from PostgreSQL."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT query, mean_time, calls, total_time
                FROM pg_stat_statements
                WHERE mean_time > 1000  -- 1 second threshold
                ORDER BY mean_time DESC
                LIMIT 10
            """)
            return cursor.fetchall()
    
    @staticmethod
    def get_connection_stats():
        """Get database connection statistics."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity
            """)
            return cursor.fetchone()
    
    @staticmethod
    def get_table_sizes():
        """Get table sizes."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10
            """)
            return cursor.fetchall()
```

---

## 🔒 **Security Monitoring**

### **Security Events**

#### **1. Failed Login Attempts**
```python
# apps/security/monitoring.py
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')
    
    logger.warning(f"Failed login attempt for {credentials.get('email')} from {ip_address}")
    
    # Check for brute force attempts
    failed_attempts = cache.get(f'failed_login_{ip_address}', 0)
    failed_attempts += 1
    cache.set(f'failed_login_{ip_address}', failed_attempts, 300)  # 5 minutes
    
    if failed_attempts >= 5:
        logger.error(f"Potential brute force attack from {ip_address}")
        # Send security alert
        send_security_alert('Brute Force Attack', f"IP {ip_address} has {failed_attempts} failed login attempts")
```

#### **2. Suspicious Activity**
```python
# apps/security/monitoring.py
class SecurityMonitor:
    """Monitor security events."""
    
    @staticmethod
    def detect_suspicious_activity(request):
        """Detect suspicious activity patterns."""
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        
        # Check for unusual user agents
        suspicious_agents = ['curl', 'wget', 'python-requests']
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            logger.warning(f"Suspicious user agent: {user_agent} from {ip_address}")
        
        # Check for rapid requests
        request_count = cache.get(f'requests_{ip_address}', 0)
        request_count += 1
        cache.set(f'requests_{ip_address}', request_count, 60)  # 1 minute
        
        if request_count > 100:  # 100 requests per minute
            logger.error(f"Potential DDoS attack from {ip_address}")
            send_security_alert('DDoS Attack', f"IP {ip_address} made {request_count} requests in 1 minute")
```

### **Vulnerability Scanning**

#### **1. Dependency Scanning**
```bash
#!/bin/bash
# security_scan.sh

# Scan Python dependencies
pip install safety
safety check --json > security_report.json

# Scan Node.js dependencies
npm audit --json > npm_audit.json

# Scan Docker images
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image helpdesk-platform:latest

# Send report
curl -X POST "https://api.helpdesk-platform.com/security/report" \
  -H "Content-Type: application/json" \
  -d @security_report.json
```

#### **2. Network Security**
```bash
#!/bin/bash
# network_scan.sh

# Check open ports
nmap -sT -O localhost

# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Check for vulnerabilities
nikto -h your-domain.com
```

---

## 📊 **Dashboard Setup**

### **Grafana Dashboard**

#### **1. Grafana Configuration**
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'

volumes:
  grafana_data:
  prometheus_data:
```

#### **2. Dashboard JSON**
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
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_activity_count",
            "legendFormat": "Active connections"
          }
        ]
      }
    ]
  }
}
```

---

## 🛠️ **Monitoring Tools**

### **Open Source Tools**

#### **1. Prometheus + Grafana**
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notification

#### **2. ELK Stack**
- **Elasticsearch**: Log storage and search
- **Logstash**: Log processing and transformation
- **Kibana**: Log visualization and analysis

#### **3. Jaeger**
- **Distributed Tracing**: Request tracing across services
- **Performance Analysis**: Identify bottlenecks
- **Dependency Mapping**: Service dependency visualization

### **Commercial Tools**

#### **1. DataDog**
- **APM**: Application performance monitoring
- **Infrastructure**: Server and container monitoring
- **Logs**: Centralized log management
- **Synthetics**: Uptime monitoring

#### **2. New Relic**
- **APM**: Application performance monitoring
- **Infrastructure**: Server monitoring
- **Browser**: Frontend performance monitoring
- **Mobile**: Mobile app monitoring

#### **3. Sentry**
- **Error Tracking**: Real-time error monitoring
- **Performance**: Application performance monitoring
- **Release Tracking**: Deployment monitoring
- **User Feedback**: User experience monitoring

---

## 📚 **Best Practices**

### **Monitoring Strategy**

#### **1. SLI/SLO Definition**
```yaml
# Service Level Objectives
slo:
  availability: 99.9%
  latency_p99: 500ms
  error_rate: 0.1%
  throughput: 1000 rps

# Service Level Indicators
sli:
  availability: "uptime / total_time"
  latency: "response_time_p99"
  error_rate: "errors / total_requests"
  throughput: "requests_per_second"
```

#### **2. Alert Fatigue Prevention**
- **Threshold-based**: Set appropriate thresholds
- **Escalation**: Implement escalation policies
- **Grouping**: Group related alerts
- **Suppression**: Suppress duplicate alerts

#### **3. Monitoring Coverage**
- **Application**: All critical paths
- **Infrastructure**: All components
- **Business**: Key business metrics
- **Security**: All security events

### **Performance Optimization**

#### **1. Metric Collection**
- **Minimal Overhead**: Keep collection overhead low
- **Sampling**: Use sampling for high-volume metrics
- **Aggregation**: Aggregate metrics appropriately
- **Retention**: Set appropriate retention periods

#### **2. Dashboard Design**
- **Relevant Metrics**: Show only relevant metrics
- **Visual Hierarchy**: Use proper visual hierarchy
- **Color Coding**: Use consistent color coding
- **Responsive**: Make dashboards responsive

---

## 📚 **Additional Resources**

### **Documentation**
- [README.md](../README.md) - Project overview
- [Architecture](ARCHITECTURE.md) - System architecture
- [Deployment](DEPLOYMENT.md) - Deployment guide
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues

### **External Resources**
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [ELK Stack Documentation](https://www.elastic.co/guide/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)

### **Tools**
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Log management
- **Jaeger**: Distributed tracing
- **DataDog**: Commercial monitoring
- **New Relic**: Commercial APM
- **Sentry**: Error tracking

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: DevOps Team
