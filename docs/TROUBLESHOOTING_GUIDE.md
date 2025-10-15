# 🔧 **Troubleshooting Guide**

**Version:** 1.0.0  
**Last Updated:** October 13, 2025

## 📋 **Table of Contents**

- [Quick Reference](#quick-reference)
- [Common Issues](#common-issues)
- [Application Issues](#application-issues)
- [Database Issues](#database-issues)
- [Authentication Issues](#authentication-issues)
- [Performance Issues](#performance-issues)
- [Deployment Issues](#deployment-issues)
- [Monitoring and Logging](#monitoring-and-logging)
- [Debugging Tools](#debugging-tools)
- [Emergency Procedures](#emergency-procedures)
- [Prevention Strategies](#prevention-strategies)

---

## ⚡ **Quick Reference**

### **Emergency Contacts**
- **On-Call Engineer**: +1-555-HELPDESK
- **DevOps Team**: devops@helpdesk.com
- **Security Team**: security@helpdesk.com
- **Database Team**: dba@helpdesk.com

### **Critical Commands**
```bash
# Check application status
kubectl get pods -l app=helpdesk

# Check application logs
kubectl logs -f deployment/helpdesk-backend

# Check database connectivity
kubectl exec deployment/helpdesk-backend -- python manage.py dbshell

# Check health endpoint
curl http://localhost:8000/health/

# Restart application
kubectl rollout restart deployment/helpdesk-backend
```

### **Quick Diagnostics**
```bash
# Run comprehensive health check
./scripts/health-check.sh

# Check system resources
kubectl top pods -l app=helpdesk

# Check application metrics
curl http://localhost:8000/metrics/

# Check database status
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "from django.db import connection; connection.ensure_connection()"
```

---

## 🚨 **Common Issues**

### **Issue 1: Application Not Responding**

#### **Symptoms**
- HTTP 500/502/503 errors
- Application timeout
- Health check failures
- High error rates in logs

#### **Diagnosis Steps**
```bash
# 1. Check pod status
kubectl get pods -l app=helpdesk

# 2. Check pod events
kubectl describe pod <pod-name>

# 3. Check application logs
kubectl logs -f deployment/helpdesk-backend

# 4. Check resource usage
kubectl top pods -l app=helpdesk

# 5. Check health endpoint
kubectl exec deployment/helpdesk-backend -- curl http://localhost:8000/health/
```

#### **Common Causes**
- **Out of Memory**: Application consuming too much memory
- **Database Connection Issues**: Can't connect to database
- **Configuration Errors**: Wrong environment variables
- **Dependency Issues**: Missing or incompatible dependencies
- **Code Errors**: Application crashes due to bugs

#### **Solutions**
```bash
# Solution 1: Restart application
kubectl rollout restart deployment/helpdesk-backend

# Solution 2: Scale up resources
kubectl patch deployment helpdesk-backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"helpdesk-backend","resources":{"limits":{"memory":"2Gi"}}}]}}}}'

# Solution 3: Check and fix configuration
kubectl get configmap app-config -o yaml
kubectl get secret app-secrets -o yaml

# Solution 4: Rollback to previous version
kubectl rollout undo deployment/helpdesk-backend
```

### **Issue 2: Database Connection Failed**

#### **Symptoms**
- Database connection errors in logs
- Application can't start
- Database queries failing
- Connection timeout errors

#### **Diagnosis Steps**
```bash
# 1. Check database service
kubectl get service database-service

# 2. Check database pods
kubectl get pods -l app=database

# 3. Test database connectivity
kubectl exec deployment/helpdesk-backend -- python manage.py dbshell

# 4. Check database logs
kubectl logs -f deployment/database

# 5. Check network connectivity
kubectl exec deployment/helpdesk-backend -- nc -zv database-service 5432
```

#### **Common Causes**
- **Database Service Down**: Database pods not running
- **Network Issues**: Can't reach database service
- **Authentication Failed**: Wrong credentials
- **Database Full**: No disk space
- **Connection Pool Exhausted**: Too many connections

#### **Solutions**
```bash
# Solution 1: Restart database
kubectl rollout restart deployment/database

# Solution 2: Check database credentials
kubectl get secret db-secret -o yaml

# Solution 3: Check database disk space
kubectl exec deployment/database -- df -h

# Solution 4: Check connection limits
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "SELECT count(*) FROM pg_stat_activity;"

# Solution 5: Restart application
kubectl rollout restart deployment/helpdesk-backend
```

### **Issue 3: High Memory Usage**

#### **Symptoms**
- Application pods being killed (OOMKilled)
- High memory consumption
- Slow response times
- Memory leaks in logs

#### **Diagnosis Steps**
```bash
# 1. Check memory usage
kubectl top pods -l app=helpdesk

# 2. Check pod events
kubectl describe pod <pod-name>

# 3. Check application logs for memory issues
kubectl logs deployment/helpdesk-backend | grep -i memory

# 4. Check resource limits
kubectl get deployment helpdesk-backend -o jsonpath='{.spec.template.spec.containers[0].resources}'

# 5. Check for memory leaks
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "import psutil; print(psutil.virtual_memory())"
```

#### **Common Causes**
- **Memory Leaks**: Application not releasing memory
- **Large Data Processing**: Processing too much data at once
- **Inefficient Queries**: Database queries loading too much data
- **Caching Issues**: Cache consuming too much memory
- **Resource Limits Too Low**: Pod limits insufficient

#### **Solutions**
```bash
# Solution 1: Increase memory limits
kubectl patch deployment helpdesk-backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"helpdesk-backend","resources":{"limits":{"memory":"4Gi"}}}]}}}}'

# Solution 2: Restart application to clear memory
kubectl rollout restart deployment/helpdesk-backend

# Solution 3: Check for memory leaks in code
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import gc
gc.collect()
print('Memory after GC:', psutil.virtual_memory().used)
"

# Solution 4: Optimize database queries
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.db import connection
print('Query count:', len(connection.queries))
"

# Solution 5: Clear cache
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.core.cache import cache
cache.clear()
"
```

---

## 🏥 **Application Issues**

### **Django Application Issues**

#### **Issue: Django Application Crashes**

**Symptoms:**
- Application pods restarting frequently
- 500 Internal Server Error
- Application logs showing Python exceptions

**Diagnosis:**
```bash
# Check application logs
kubectl logs -f deployment/helpdesk-backend

# Check for Python exceptions
kubectl logs deployment/helpdesk-backend | grep -i exception

# Check Django settings
kubectl exec deployment/helpdesk-backend -- python manage.py check

# Check database migrations
kubectl exec deployment/helpdesk-backend -- python manage.py showmigrations
```

**Common Causes:**
- **Missing Environment Variables**: Required settings not configured
- **Database Migration Issues**: Unapplied migrations
- **Import Errors**: Missing Python packages
- **Configuration Errors**: Invalid Django settings
- **Permission Issues**: File system permissions

**Solutions:**
```bash
# Solution 1: Check environment variables
kubectl exec deployment/helpdesk-backend -- env | grep DJANGO

# Solution 2: Apply database migrations
kubectl exec deployment/helpdesk-backend -- python manage.py migrate

# Solution 3: Check Django configuration
kubectl exec deployment/helpdesk-backend -- python manage.py check --deploy

# Solution 4: Restart application
kubectl rollout restart deployment/helpdesk-backend

# Solution 5: Check file permissions
kubectl exec deployment/helpdesk-backend -- ls -la /app
```

#### **Issue: Static Files Not Loading**

**Symptoms:**
- CSS/JS files not loading
- 404 errors for static files
- Broken UI styling

**Diagnosis:**
```bash
# Check static files collection
kubectl exec deployment/helpdesk-backend -- python manage.py collectstatic --dry-run

# Check static files directory
kubectl exec deployment/helpdesk-backend -- ls -la /app/staticfiles

# Check nginx configuration
kubectl get configmap nginx-config -o yaml

# Check static files URL
curl -I http://localhost/static/css/main.css
```

**Solutions:**
```bash
# Solution 1: Collect static files
kubectl exec deployment/helpdesk-backend -- python manage.py collectstatic --noinput

# Solution 2: Check nginx configuration
kubectl exec deployment/nginx -- nginx -t

# Solution 3: Restart nginx
kubectl rollout restart deployment/nginx

# Solution 4: Check static files permissions
kubectl exec deployment/helpdesk-backend -- chmod -R 755 /app/staticfiles
```

### **Frontend Application Issues**

#### **Issue: React Application Not Loading**

**Symptoms:**
- Blank page in browser
- JavaScript errors in console
- API calls failing
- Build errors

**Diagnosis:**
```bash
# Check frontend build
kubectl logs deployment/helpdesk-frontend

# Check nginx configuration
kubectl get configmap nginx-config -o yaml

# Check API connectivity
curl -I http://localhost/api/health/

# Check browser console
# Open browser developer tools and check console for errors
```

**Common Causes:**
- **Build Failures**: Frontend build process failing
- **API Connection Issues**: Can't connect to backend API
- **Configuration Errors**: Wrong API endpoints
- **Nginx Issues**: Reverse proxy not configured correctly
- **CORS Issues**: Cross-origin requests blocked

**Solutions:**
```bash
# Solution 1: Rebuild frontend
kubectl exec deployment/helpdesk-frontend -- npm run build

# Solution 2: Check API configuration
kubectl get configmap app-config -o yaml | grep API

# Solution 3: Check CORS settings
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.conf import settings
print('CORS_ALLOWED_ORIGINS:', settings.CORS_ALLOWED_ORIGINS)
"

# Solution 4: Restart nginx
kubectl rollout restart deployment/nginx

# Solution 5: Check network connectivity
kubectl exec deployment/helpdesk-frontend -- curl http://helpdesk-backend:8000/health/
```

---

## 🗄️ **Database Issues**

### **PostgreSQL Issues**

#### **Issue: Database Connection Timeout**

**Symptoms:**
- Connection timeout errors
- Application can't connect to database
- Database queries hanging
- Connection pool exhausted

**Diagnosis:**
```bash
# Check database service
kubectl get service database-service

# Check database pods
kubectl get pods -l app=database

# Check database logs
kubectl logs -f deployment/database

# Check connection count
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';
"

# Check database locks
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
SELECT * FROM pg_locks WHERE NOT granted;
"
```

**Common Causes:**
- **Too Many Connections**: Connection pool exhausted
- **Long-Running Queries**: Queries blocking connections
- **Database Locks**: Deadlocks or long-running transactions
- **Network Issues**: Network connectivity problems
- **Database Overload**: Database under heavy load

**Solutions:**
```bash
# Solution 1: Check and kill long-running queries
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"

# Solution 2: Increase connection limits
kubectl patch deployment/database -p '{"spec":{"template":{"spec":{"containers":[{"name":"database","env":[{"name":"POSTGRES_MAX_CONNECTIONS","value":"200"}]}]}}}}'

# Solution 3: Restart database
kubectl rollout restart deployment/database

# Solution 4: Check for deadlocks
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
SELECT * FROM pg_stat_database WHERE datname = 'helpdesk';
"
```

#### **Issue: Database Disk Space Full**

**Symptoms:**
- Database write errors
- Application can't save data
- Database logs showing disk space errors
- Database pods failing

**Diagnosis:**
```bash
# Check database disk usage
kubectl exec deployment/database -- df -h

# Check database size
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
SELECT pg_size_pretty(pg_database_size('helpdesk'));
"

# Check table sizes
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

**Solutions:**
```bash
# Solution 1: Clean up old data
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
DELETE FROM django_session WHERE expire_date < NOW() - INTERVAL '30 days';
"

# Solution 2: Vacuum database
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
VACUUM ANALYZE;
"

# Solution 3: Check for large tables
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"

# Solution 4: Increase disk space
# This requires infrastructure changes - contact DevOps team
```

### **Redis Issues**

#### **Issue: Redis Connection Failed**

**Symptoms:**
- Cache errors in application logs
- Session management issues
- Celery tasks not working
- Cache misses

**Diagnosis:**
```bash
# Check Redis service
kubectl get service redis-service

# Check Redis pods
kubectl get pods -l app=redis

# Check Redis logs
kubectl logs -f deployment/redis

# Test Redis connectivity
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.core.cache import cache
cache.set('test', 'value', 10)
print('Cache test:', cache.get('test'))
"

# Check Redis memory usage
kubectl exec deployment/redis -- redis-cli info memory
```

**Common Causes:**
- **Redis Service Down**: Redis pods not running
- **Memory Issues**: Redis out of memory
- **Network Issues**: Can't reach Redis service
- **Configuration Errors**: Wrong Redis URL
- **Authentication Issues**: Redis password issues

**Solutions:**
```bash
# Solution 1: Restart Redis
kubectl rollout restart deployment/redis

# Solution 2: Check Redis configuration
kubectl get configmap redis-config -o yaml

# Solution 3: Clear Redis cache
kubectl exec deployment/redis -- redis-cli FLUSHALL

# Solution 4: Check Redis memory
kubectl exec deployment/redis -- redis-cli info memory | grep used_memory

# Solution 5: Restart application
kubectl rollout restart deployment/helpdesk-backend
```

---

## 🔐 **Authentication Issues**

### **JWT Token Issues**

#### **Issue: Token Expired**

**Symptoms:**
- 401 Unauthorized errors
- Users being logged out frequently
- Token validation failures
- Authentication errors in logs

**Diagnosis:**
```bash
# Check token expiration settings
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.conf import settings
print('JWT settings:', getattr(settings, 'JWT_AUTH', {}))
"

# Check token validation
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import jwt
from django.conf import settings
# Test token validation logic
"

# Check authentication logs
kubectl logs deployment/helpdesk-backend | grep -i "token\|auth"
```

**Common Causes:**
- **Token Expiration**: Tokens expiring too quickly
- **Clock Skew**: Server time differences
- **Token Validation Errors**: Invalid token format
- **Refresh Token Issues**: Refresh token not working
- **Session Management**: Session handling problems

**Solutions:**
```bash
# Solution 1: Check token expiration settings
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.conf import settings
print('JWT settings:', settings.JWT_AUTH)
"

# Solution 2: Restart application
kubectl rollout restart deployment/helpdesk-backend

# Solution 3: Check system time
kubectl exec deployment/helpdesk-backend -- date
kubectl exec deployment/redis -- date

# Solution 4: Clear invalid tokens
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.core.cache import cache
# Clear token cache if applicable
"
```

#### **Issue: Permission Denied**

**Symptoms:**
- 403 Forbidden errors
- Users can't access certain features
- Role-based access not working
- Permission errors in logs

**Diagnosis:**
```bash
# Check user permissions
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='test@example.com')
print('User roles:', user.roles.all())
print('User permissions:', user.get_all_permissions())
"

# Check permission logs
kubectl logs deployment/helpdesk-backend | grep -i "permission\|403"

# Check role configuration
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from apps.organizations.models import Role
roles = Role.objects.all()
for role in roles:
    print(f'Role: {role.name}, Permissions: {role.permissions.all()}')
"
```

**Solutions:**
```bash
# Solution 1: Check user roles
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='test@example.com')
user.roles.add(Role.objects.get(name='agent'))
"

# Solution 2: Check permission configuration
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.contrib.auth.models import Permission
permissions = Permission.objects.all()
for perm in permissions:
    print(f'{perm.content_type.app_label}.{perm.codename}')
"

# Solution 3: Restart application
kubectl rollout restart deployment/helpdesk-backend
```

---

## ⚡ **Performance Issues**

### **Slow Response Times**

#### **Issue: High Response Times**

**Symptoms:**
- Slow page loads
- API responses taking too long
- User complaints about performance
- High response time metrics

**Diagnosis:**
```bash
# Check response time metrics
curl -w "@curl-format.txt" -o /dev/null -s http://localhost/api/health/

# Check application metrics
kubectl exec deployment/helpdesk-backend -- curl http://localhost:8000/metrics/

# Check database query performance
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.db import connection
print('Query count:', len(connection.queries))
print('Total time:', sum(float(q['time']) for q in connection.queries))
"

# Check resource usage
kubectl top pods -l app=helpdesk
```

**Common Causes:**
- **Database Query Issues**: Slow or inefficient queries
- **Resource Constraints**: Insufficient CPU/memory
- **Network Latency**: Slow network connections
- **Caching Issues**: Cache not working properly
- **Code Performance**: Inefficient application code

**Solutions:**
```bash
# Solution 1: Check database query performance
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.db import connection
connection.queries_log.clear()
# Run a test query
from apps.tickets.models import Ticket
list(Ticket.objects.all()[:10])
print('Queries:', len(connection.queries))
for query in connection.queries:
    print(f'Time: {query[\"time\"]}s, SQL: {query[\"sql\"]}')
"

# Solution 2: Optimize database queries
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.db import connection
# Enable query logging
connection.queries_log.clear()
"

# Solution 3: Check cache performance
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.core.cache import cache
import time
start = time.time()
cache.get('test')
print(f'Cache response time: {time.time() - start}s')
"

# Solution 4: Scale up resources
kubectl patch deployment helpdesk-backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"helpdesk-backend","resources":{"limits":{"cpu":"2","memory":"4Gi"}}}]}}}}'
```

#### **Issue: High CPU Usage**

**Symptoms:**
- High CPU utilization
- Slow application performance
- CPU throttling
- High CPU metrics

**Diagnosis:**
```bash
# Check CPU usage
kubectl top pods -l app=helpdesk

# Check CPU limits
kubectl get deployment helpdesk-backend -o jsonpath='{.spec.template.spec.containers[0].resources}'

# Check for CPU-intensive processes
kubectl exec deployment/helpdesk-backend -- top -n 1

# Check application logs for CPU-intensive operations
kubectl logs deployment/helpdesk-backend | grep -i "cpu\|performance"
```

**Solutions:**
```bash
# Solution 1: Increase CPU limits
kubectl patch deployment helpdesk-backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"helpdesk-backend","resources":{"limits":{"cpu":"2"}}}]}}}}'

# Solution 2: Check for infinite loops
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import psutil
print('CPU usage:', psutil.cpu_percent())
print('Process count:', len(psutil.pids()))
"

# Solution 3: Restart application
kubectl rollout restart deployment/helpdesk-backend

# Solution 4: Check for memory leaks
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import psutil
print('Memory usage:', psutil.virtual_memory())
"
```

### **Memory Issues**

#### **Issue: Memory Leaks**

**Symptoms:**
- Memory usage continuously increasing
- Application pods being killed (OOMKilled)
- Slow performance over time
- Memory errors in logs

**Diagnosis:**
```bash
# Check memory usage over time
kubectl top pods -l app=helpdesk

# Check for memory leaks
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import psutil
import gc
print('Memory before GC:', psutil.virtual_memory().used)
gc.collect()
print('Memory after GC:', psutil.virtual_memory().used)
"

# Check pod events for OOMKilled
kubectl describe pod <pod-name>

# Check application logs for memory issues
kubectl logs deployment/helpdesk-backend | grep -i "memory\|oom"
```

**Solutions:**
```bash
# Solution 1: Increase memory limits
kubectl patch deployment helpdesk-backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"helpdesk-backend","resources":{"limits":{"memory":"4Gi"}}}]}}}}'

# Solution 2: Restart application to clear memory
kubectl rollout restart deployment/helpdesk-backend

# Solution 3: Check for memory leaks in code
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import gc
import sys
print('Object count:', len(gc.get_objects()))
print('Memory usage:', sys.getsizeof(gc.get_objects()))
"

# Solution 4: Monitor memory usage
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import psutil
import time
for i in range(10):
    print(f'Memory usage: {psutil.virtual_memory().used} bytes')
    time.sleep(10)
"
```

---

## 🚀 **Deployment Issues**

### **Deployment Failures**

#### **Issue: Deployment Stuck**

**Symptoms:**
- Deployment not completing
- Pods not starting
- Deployment status stuck
- Rollout not progressing

**Diagnosis:**
```bash
# Check deployment status
kubectl get deployment helpdesk-backend

# Check rollout status
kubectl rollout status deployment/helpdesk-backend

# Check pod events
kubectl describe pod <pod-name>

# Check resource quotas
kubectl describe quota

# Check node resources
kubectl describe nodes
```

**Common Causes:**
- **Resource Constraints**: Insufficient CPU/memory
- **Image Pull Issues**: Can't pull container image
- **Configuration Errors**: Invalid configuration
- **Network Issues**: Can't reach registry
- **Quota Limits**: Resource quotas exceeded

**Solutions:**
```bash
# Solution 1: Check resource quotas
kubectl describe quota

# Solution 2: Check node resources
kubectl describe nodes

# Solution 3: Check image pull secrets
kubectl get secret

# Solution 4: Restart deployment
kubectl rollout restart deployment/helpdesk-backend

# Solution 5: Check configuration
kubectl get deployment helpdesk-backend -o yaml
```

#### **Issue: Blue-Green Deployment Issues**

**Symptoms:**
- Blue-green switch not working
- Traffic not routing correctly
- Service selector issues
- Load balancer problems

**Diagnosis:**
```bash
# Check service selector
kubectl get service helpdesk-service -o yaml

# Check pod labels
kubectl get pods -l app=helpdesk --show-labels

# Check traffic routing
kubectl get ingress

# Check load balancer
kubectl get service helpdesk-service
```

**Solutions:**
```bash
# Solution 1: Fix service selector
kubectl patch service helpdesk-service -p '{"spec":{"selector":{"version":"blue"}}}'

# Solution 2: Check pod labels
kubectl label pods <pod-name> version=blue

# Solution 3: Restart service
kubectl delete service helpdesk-service
kubectl apply -f service.yml

# Solution 4: Check ingress configuration
kubectl get ingress helpdesk-ingress -o yaml
```

### **Rollback Issues**

#### **Issue: Rollback Failed**

**Symptoms:**
- Rollback not working
- Previous version not available
- Rollback stuck
- Application not responding after rollback

**Diagnosis:**
```bash
# Check rollout history
kubectl rollout history deployment/helpdesk-backend

# Check current deployment
kubectl get deployment helpdesk-backend -o yaml

# Check pod status
kubectl get pods -l app=helpdesk

# Check application logs
kubectl logs -f deployment/helpdesk-backend
```

**Solutions:**
```bash
# Solution 1: Check rollout history
kubectl rollout history deployment/helpdesk-backend

# Solution 2: Rollback to specific revision
kubectl rollout undo deployment/helpdesk-backend --to-revision=2

# Solution 3: Check image availability
kubectl get deployment helpdesk-backend -o jsonpath='{.spec.template.spec.containers[0].image}'

# Solution 4: Force rollback
kubectl patch deployment helpdesk-backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"helpdesk-backend","image":"helpdesk-backend:previous"}]}}}}'
```

---

## 📊 **Monitoring and Logging**

### **Log Analysis**

#### **Issue: Logs Not Appearing**

**Symptoms:**
- No logs in logging system
- Logs not being collected
- Log aggregation issues
- Log rotation problems

**Diagnosis:**
```bash
# Check application logs
kubectl logs -f deployment/helpdesk-backend

# Check log volume
kubectl exec deployment/helpdesk-backend -- ls -la /app/logs/

# Check log configuration
kubectl get configmap app-config -o yaml | grep -i log

# Check log aggregation
kubectl get pods -l app=log-aggregator
```

**Solutions:**
```bash
# Solution 1: Check log configuration
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import logging
print('Log level:', logging.getLogger().level)
print('Handlers:', logging.getLogger().handlers)
"

# Solution 2: Restart log aggregation
kubectl rollout restart deployment/log-aggregator

# Solution 3: Check log volume
kubectl exec deployment/helpdesk-backend -- df -h /app/logs/

# Solution 4: Test logging
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import logging
logging.info('Test log message')
"
```

#### **Issue: High Log Volume**

**Symptoms:**
- Too many logs being generated
- Log storage filling up
- Performance impact from logging
- Log rotation issues

**Diagnosis:**
```bash
# Check log volume
kubectl exec deployment/helpdesk-backend -- du -sh /app/logs/

# Check log rotation
kubectl exec deployment/helpdesk-backend -- ls -la /app/logs/

# Check log configuration
kubectl get configmap app-config -o yaml | grep -i log

# Check log level
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import logging
print('Log level:', logging.getLogger().level)
"
```

**Solutions:**
```bash
# Solution 1: Adjust log level
kubectl patch configmap app-config -p '{"data":{"LOG_LEVEL":"WARNING"}}'

# Solution 2: Configure log rotation
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import logging
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('/app/logs/django.log', maxBytes=10*1024*1024, backupCount=5)
logging.getLogger().addHandler(handler)
"

# Solution 3: Clean old logs
kubectl exec deployment/helpdesk-backend -- find /app/logs/ -name "*.log.*" -mtime +7 -delete

# Solution 4: Restart application
kubectl rollout restart deployment/helpdesk-backend
```

### **Metrics Issues**

#### **Issue: Metrics Not Collecting**

**Symptoms:**
- No metrics in monitoring system
- Metrics endpoints not responding
- Monitoring dashboards empty
- Alerting not working

**Diagnosis:**
```bash
# Check metrics endpoint
kubectl exec deployment/helpdesk-backend -- curl http://localhost:8000/metrics/

# Check metrics configuration
kubectl get configmap app-config -o yaml | grep -i metric

# Check monitoring system
kubectl get pods -l app=monitoring

# Check metrics collection
kubectl logs deployment/metrics-collector
```

**Solutions:**
```bash
# Solution 1: Check metrics endpoint
kubectl exec deployment/helpdesk-backend -- curl http://localhost:8000/metrics/

# Solution 2: Restart metrics collection
kubectl rollout restart deployment/metrics-collector

# Solution 3: Check monitoring configuration
kubectl get configmap monitoring-config -o yaml

# Solution 4: Test metrics collection
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from prometheus_client import generate_latest
print(generate_latest())
"
```

---

## 🛠️ **Debugging Tools**

### **Application Debugging**

#### **Django Debug Toolbar**
```bash
# Enable debug toolbar
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.conf import settings
print('DEBUG:', settings.DEBUG)
print('DEBUG_TOOLBAR:', 'debug_toolbar' in settings.INSTALLED_APPS)
"

# Check debug toolbar configuration
kubectl get configmap app-config -o yaml | grep -i debug
```

#### **Database Query Debugging**
```bash
# Enable query logging
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.db import connection
connection.queries_log.clear()
# Run a test query
from apps.tickets.models import Ticket
list(Ticket.objects.all()[:10])
print('Queries:', len(connection.queries))
for query in connection.queries:
    print(f'Time: {query[\"time\"]}s, SQL: {query[\"sql\"]}')
"
```

#### **Performance Profiling**
```bash
# Install profiling tools
kubectl exec deployment/helpdesk-backend -- pip install django-debug-toolbar

# Run performance profiling
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
import cProfile
import pstats
from io import StringIO

# Profile a function
pr = cProfile.Profile()
pr.enable()
# Run your code here
pr.disable()

s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats()
print(s.getvalue())
"
```

### **Network Debugging**

#### **Network Connectivity**
```bash
# Test network connectivity
kubectl exec deployment/helpdesk-backend -- nc -zv database-service 5432
kubectl exec deployment/helpdesk-backend -- nc -zv redis-service 6379

# Check DNS resolution
kubectl exec deployment/helpdesk-backend -- nslookup database-service
kubectl exec deployment/helpdesk-backend -- nslookup redis-service

# Check network policies
kubectl get networkpolicy
kubectl describe networkpolicy helpdesk-network-policy
```

#### **Load Balancer Debugging**
```bash
# Check load balancer status
kubectl get service helpdesk-service
kubectl describe service helpdesk-service

# Check ingress configuration
kubectl get ingress helpdesk-ingress
kubectl describe ingress helpdesk-ingress

# Test load balancer
curl -H "Host: api.helpdesk.com" http://localhost/health/
```

### **Container Debugging**

#### **Container Inspection**
```bash
# Inspect container
kubectl exec deployment/helpdesk-backend -- ps aux
kubectl exec deployment/helpdesk-backend -- netstat -tlnp
kubectl exec deployment/helpdesk-backend -- ss -tlnp

# Check container resources
kubectl exec deployment/helpdesk-backend -- free -h
kubectl exec deployment/helpdesk-backend -- df -h

# Check container environment
kubectl exec deployment/helpdesk-backend -- env
```

#### **Container Logs**
```bash
# Follow application logs
kubectl logs -f deployment/helpdesk-backend

# Check specific log files
kubectl exec deployment/helpdesk-backend -- tail -f /app/logs/django.log
kubectl exec deployment/helpdesk-backend -- tail -f /app/logs/error.log

# Check log rotation
kubectl exec deployment/helpdesk-backend -- ls -la /app/logs/
```

---

## 🚨 **Emergency Procedures**

### **Critical Issues**

#### **Complete System Down**
```bash
# 1. Check all services
kubectl get pods -l app=helpdesk
kubectl get pods -l app=database
kubectl get pods -l app=redis

# 2. Check service status
kubectl get services
kubectl get ingress

# 3. Check node status
kubectl get nodes

# 4. Restart all services
kubectl rollout restart deployment/helpdesk-backend
kubectl rollout restart deployment/database
kubectl rollout restart deployment/redis
kubectl rollout restart deployment/nginx

# 5. Check application health
kubectl exec deployment/helpdesk-backend -- curl http://localhost:8000/health/
```

#### **Database Corruption**
```bash
# 1. Stop application
kubectl scale deployment helpdesk-backend --replicas=0

# 2. Backup current database
kubectl exec deployment/database -- pg_dump -U helpdesk_user helpdesk > backup.sql

# 3. Check database integrity
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk -c "VACUUM ANALYZE;"

# 4. Restore from backup if needed
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk < backup.sql

# 5. Restart application
kubectl scale deployment helpdesk-backend --replicas=3
```

#### **Security Breach**
```bash
# 1. Isolate affected pods
kubectl delete pod <affected-pod>

# 2. Check for unauthorized access
kubectl logs deployment/helpdesk-backend | grep -i "unauthorized\|forbidden\|attack"

# 3. Check network traffic
kubectl exec deployment/helpdesk-backend -- netstat -an | grep ESTABLISHED

# 4. Rotate secrets
kubectl create secret generic app-secrets --from-literal=SECRET_KEY=$(openssl rand -base64 32)

# 5. Restart all services
kubectl rollout restart deployment/helpdesk-backend
kubectl rollout restart deployment/database
kubectl rollout restart deployment/redis
```

### **Data Recovery**

#### **Database Recovery**
```bash
# 1. Stop application
kubectl scale deployment helpdesk-backend --replicas=0

# 2. Restore from backup
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk < backup.sql

# 3. Run migrations
kubectl exec deployment/helpdesk-backend -- python manage.py migrate

# 4. Verify data integrity
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT COUNT(*) FROM django_migrations')
print('Migrations:', cursor.fetchone()[0])
"

# 5. Restart application
kubectl scale deployment helpdesk-backend --replicas=3
```

#### **File Recovery**
```bash
# 1. Check file system
kubectl exec deployment/helpdesk-backend -- df -h

# 2. Check file permissions
kubectl exec deployment/helpdesk-backend -- ls -la /app/

# 3. Restore from backup
kubectl exec deployment/helpdesk-backend -- cp -r /backup/staticfiles /app/

# 4. Fix permissions
kubectl exec deployment/helpdesk-backend -- chmod -R 755 /app/staticfiles

# 5. Restart application
kubectl rollout restart deployment/helpdesk-backend
```

---

## 🛡️ **Prevention Strategies**

### **Monitoring and Alerting**

#### **Health Checks**
```bash
# Implement comprehensive health checks
kubectl exec deployment/helpdesk-backend -- python manage.py shell -c "
from django.core.management import call_command
call_command('check', '--deploy')
"

# Set up automated health checks
kubectl apply -f health-check.yml
```

#### **Resource Monitoring**
```bash
# Monitor resource usage
kubectl top pods -l app=helpdesk

# Set up resource alerts
kubectl apply -f resource-alerts.yml
```

#### **Log Monitoring**
```bash
# Set up log aggregation
kubectl apply -f log-aggregation.yml

# Configure log alerts
kubectl apply -f log-alerts.yml
```

### **Backup and Recovery**

#### **Database Backups**
```bash
# Set up automated backups
kubectl apply -f database-backup.yml

# Test backup restoration
kubectl exec deployment/database -- psql -U helpdesk_user -d helpdesk < backup.sql
```

#### **File Backups**
```bash
# Set up file backups
kubectl apply -f file-backup.yml

# Test file restoration
kubectl exec deployment/helpdesk-backend -- cp -r /backup/staticfiles /app/
```

### **Security Measures**

#### **Security Scanning**
```bash
# Set up security scanning
kubectl apply -f security-scan.yml

# Configure security alerts
kubectl apply -f security-alerts.yml
```

#### **Access Control**
```bash
# Set up network policies
kubectl apply -f network-policy.yml

# Configure RBAC
kubectl apply -f rbac.yml
```

---

## 📚 **Best Practices**

### **1. Proactive Monitoring**

#### **Set Up Comprehensive Monitoring**
- Monitor application metrics
- Track business metrics
- Monitor system resources
- Set up alerting
- Use dashboards

#### **Regular Health Checks**
- Automated health checks
- Regular backup testing
- Security scanning
- Performance monitoring
- Log analysis

### **2. Documentation**

#### **Keep Documentation Updated**
- Update troubleshooting guides
- Document common issues
- Maintain runbooks
- Keep contact information current
- Update procedures

#### **Knowledge Sharing**
- Regular team meetings
- Share lessons learned
- Document solutions
- Train team members
- Maintain playbooks

### **3. Testing**

#### **Regular Testing**
- Test backup procedures
- Test rollback procedures
- Test emergency procedures
- Test monitoring systems
- Test alerting

#### **Simulation Exercises**
- Disaster recovery drills
- Security incident simulations
- Performance testing
- Load testing
- Stress testing

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: DevOps Team
