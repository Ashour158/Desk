# Environment Setup Checklist

**Date:** October 13, 2025  
**Status:** COMPREHENSIVE CHECKLIST  
**Priority:** CRITICAL

## 🎯 **Quick Start Guide**

### **1. Copy Environment Files**
```bash
# Copy the appropriate environment file for your setup
cp env.example .env                    # Development
cp env.production.example .env        # Production
```

### **2. Configure Environment Variables**
```bash
# Edit the .env file with your actual values
nano .env
# or
vim .env
```

### **3. Validate Configuration**
```bash
# Run the environment validation script
python scripts/validate_environment.py
```

## 📋 **Complete Setup Checklist**

### **Phase 1: Basic Configuration**

#### **✅ Environment Files**
- [ ] **Copy environment file**
  ```bash
  cp env.example .env
  ```

- [ ] **Set Django settings**
  ```bash
  SECRET_KEY=your-secret-key-here
  DEBUG=True  # False for production
  ALLOWED_HOSTS=localhost,127.0.0.1
  ```

- [ ] **Configure database**
  ```bash
  DATABASE_URL=postgresql://user:password@host:port/database
  DB_HOST=localhost
  DB_NAME=helpdesk
  DB_USER=postgres
  DB_PASSWORD=your-password
  DB_PORT=5432
  ```

- [ ] **Configure Redis**
  ```bash
  REDIS_URL=redis://localhost:6379/0
  CELERY_BROKER_URL=redis://localhost:6379/0
  CELERY_RESULT_BACKEND=redis://localhost:6379/0
  ```

#### **✅ Email Configuration**
- [ ] **Set email backend**
  ```bash
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_USE_TLS=True
  EMAIL_HOST_USER=your-email@gmail.com
  EMAIL_HOST_PASSWORD=your-app-password
  DEFAULT_FROM_EMAIL=noreply@helpdesk.com
  ```

#### **✅ External Services**
- [ ] **Configure AI services**
  ```bash
  OPENAI_API_KEY=your-openai-api-key
  ANTHROPIC_API_KEY=your-anthropic-api-key
  ```

- [ ] **Configure communication services**
  ```bash
  TWILIO_ACCOUNT_SID=your-twilio-account-sid
  TWILIO_AUTH_TOKEN=your-twilio-auth-token
  SENDGRID_API_KEY=your-sendgrid-api-key
  ```

- [ ] **Configure mapping services**
  ```bash
  GOOGLE_MAPS_API_KEY=your-google-maps-api-key
  ```

### **Phase 2: Security Configuration**

#### **✅ Security Headers**
- [ ] **Configure SSL settings**
  ```bash
  SECURE_SSL_REDIRECT=True  # Production only
  SECURE_HSTS_SECONDS=31536000
  SECURE_HSTS_INCLUDE_SUBDOMAINS=True
  SECURE_HSTS_PRELOAD=True
  ```

- [ ] **Configure content security**
  ```bash
  SECURE_CONTENT_TYPE_NOSNIFF=True
  SECURE_BROWSER_XSS_FILTER=True
  SECURE_REFERRER_POLICY=strict-origin-when-cross-origin
  X_FRAME_OPTIONS=DENY
  ```

- [ ] **Configure session security**
  ```bash
  SESSION_COOKIE_SECURE=True  # Production only
  SESSION_COOKIE_HTTPONLY=True
  SESSION_COOKIE_SAMESITE=Strict
  CSRF_COOKIE_SECURE=True  # Production only
  CSRF_COOKIE_HTTPONLY=True
  CSRF_COOKIE_SAMESITE=Strict
  ```

#### **✅ CORS Configuration**
- [ ] **Set allowed origins**
  ```bash
  CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
  CORS_ALLOW_CREDENTIALS=True
  ```

#### **✅ JWT Configuration**
- [ ] **Set JWT settings**
  ```bash
  JWT_SECRET_KEY=your-jwt-secret-key
  JWT_ALGORITHM=HS256
  JWT_ACCESS_TOKEN_LIFETIME=15
  JWT_REFRESH_TOKEN_LIFETIME=7
  ```

### **Phase 3: File Storage Configuration**

#### **✅ AWS S3 Configuration**
- [ ] **Set AWS credentials**
  ```bash
  AWS_ACCESS_KEY_ID=your-aws-access-key
  AWS_SECRET_ACCESS_KEY=your-aws-secret-key
  AWS_STORAGE_BUCKET_NAME=your-bucket-name
  AWS_S3_REGION_NAME=us-east-1
  ```

- [ ] **Configure CDN (optional)**
  ```bash
  AWS_S3_CUSTOM_DOMAIN=your-cdn-domain.com
  AWS_S3_USE_SSL=True
  AWS_S3_VERIFY=True
  ```

#### **✅ File Upload Security**
- [ ] **Set upload limits**
  ```bash
  MAX_UPLOAD_SIZE=10485760  # 10MB
  ALLOWED_FILE_TYPES=jpg,jpeg,png,gif,pdf,doc,docx,txt
  UPLOAD_PATH=uploads/
  ```

### **Phase 4: Performance Configuration**

#### **✅ Caching Configuration**
- [ ] **Set cache settings**
  ```bash
  CACHE_TTL=3600
  CACHE_MAX_ENTRIES=1000
  ```

#### **✅ Database Optimization**
- [ ] **Set connection pooling**
  ```bash
  DB_CONN_MAX_AGE=600
  DB_CONN_MAX_CONNS=20
  ```

#### **✅ Rate Limiting**
- [ ] **Configure rate limits**
  ```bash
  RATE_LIMIT_ENABLED=True
  RATE_LIMIT_REQUESTS_PER_MINUTE=60
  RATE_LIMIT_BURST=100
  ```

### **Phase 5: Monitoring Configuration**

#### **✅ Error Tracking**
- [ ] **Configure Sentry**
  ```bash
  SENTRY_DSN=your-sentry-dsn
  SENTRY_ENVIRONMENT=production
  ```

#### **✅ Logging Configuration**
- [ ] **Set logging settings**
  ```bash
  LOG_LEVEL=INFO
  LOG_FORMAT=json
  LOG_FILE_PATH=/app/logs/
  ```

#### **✅ Health Checks**
- [ ] **Configure health monitoring**
  ```bash
  HEALTH_CHECK_ENABLED=True
  HEALTH_CHECK_INTERVAL=30
  ```

#### **✅ Performance Monitoring**
- [ ] **Set up metrics**
  ```bash
  METRICS_ENABLED=True
  METRICS_PORT=9090
  PERFORMANCE_MONITORING=True
  ```

### **Phase 6: Application URLs**

#### **✅ Service URLs**
- [ ] **Configure service endpoints**
  ```bash
  DJANGO_API_URL=http://localhost:8000
  FRONTEND_URL=http://localhost:3000
  AI_SERVICE_URL=http://localhost:8001
  REALTIME_SERVICE_URL=http://localhost:3000
  ```

## 🔧 **Development Setup**

### **Local Development Environment**

#### **1. Python Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### **2. Node.js Environment**
```bash
# Install Node.js dependencies
cd customer-portal
npm install

cd ../realtime-service
npm install
```

#### **3. Database Setup**
```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

#### **4. Start Development Servers**
```bash
# Terminal 1: Django API
python manage.py runserver

# Terminal 2: AI Service
cd ai-service
uvicorn app.main:app --reload

# Terminal 3: Realtime Service
cd realtime-service
npm start

# Terminal 4: Customer Portal
cd customer-portal
npm run dev
```

## 🚀 **Production Setup**

### **Production Environment**

#### **1. Environment Variables**
```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=config.settings.production
export DEBUG=False
export SECRET_KEY=your-production-secret-key
```

#### **2. Database Setup**
```bash
# Create production database
createdb helpdesk_production

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

#### **3. Start Production Services**
```bash
# Start with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Start Celery worker
celery -A config worker -l info

# Start Celery beat
celery -A config beat -l info
```

## 🐳 **Docker Setup**

### **Docker Development**

#### **1. Build and Start Services**
```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### **2. Database Migrations**
```bash
# Run migrations in container
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### **Docker Production**

#### **1. Production Docker Compose**
```bash
# Use production environment
export COMPOSE_FILE=docker-compose.prod.yml

# Build production images
docker-compose build

# Start production services
docker-compose up -d
```

## 🔍 **Validation and Testing**

### **Environment Validation**

#### **1. Run Validation Script**
```bash
# Validate environment configuration
python scripts/validate_environment.py
```

#### **2. Test Database Connection**
```bash
# Test database connection
python manage.py dbshell
```

#### **3. Test Redis Connection**
```bash
# Test Redis connection
python manage.py shell -c "import redis; r = redis.Redis.from_url('$REDIS_URL'); r.ping()"
```

#### **4. Test Email Configuration**
```bash
# Test email sending
python manage.py shell -c "from django.core.mail import send_mail; send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])"
```

### **Health Checks**

#### **1. Application Health**
```bash
# Test Django API
curl http://localhost:8000/health/

# Test AI Service
curl http://localhost:8001/health/

# Test Realtime Service
curl http://localhost:3000/health/
```

#### **2. Service Integration**
```bash
# Test API endpoints
curl http://localhost:8000/api/v1/tickets/
curl http://localhost:8001/api/v1/ai/analyze/
curl http://localhost:3000/api/v1/notifications/
```

## 📊 **Monitoring Setup**

### **Security Monitoring**

#### **1. Set Up Security Scanner**
```bash
# Configure monitoring
python monitoring/security_scanner.py
```

#### **2. Configure Alerts**
```bash
# Edit monitoring configuration
nano monitoring/config.json
```

### **Performance Monitoring**

#### **1. Start Performance Monitor**
```bash
# Start monitoring
python monitoring/performance_monitor.py
```

#### **2. View Dashboard**
```bash
# Open monitoring dashboard
open monitoring/dashboard.html
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Issues**
```bash
# Check database status
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
python manage.py dbshell
```

#### **2. Redis Connection Issues**
```bash
# Check Redis status
docker-compose ps redis

# Test Redis connection
redis-cli ping
```

#### **3. Environment Variable Issues**
```bash
# Check environment variables
python -c "import os; print(os.environ.get('SECRET_KEY'))"

# Validate configuration
python scripts/validate_environment.py
```

#### **4. Port Conflicts**
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Kill processes using ports
sudo kill -9 $(lsof -t -i:8000)
sudo kill -9 $(lsof -t -i:3000)
```

## 📋 **Pre-Deployment Checklist**

### **Security Checklist**
- [ ] **All secrets are in environment variables**
- [ ] **No hardcoded credentials in code**
- [ ] **SSL/TLS is properly configured**
- [ ] **Security headers are set**
- [ ] **CORS is properly configured**
- [ ] **Rate limiting is enabled**
- [ ] **File upload restrictions are set**

### **Performance Checklist**
- [ ] **Caching is configured**
- [ ] **Database connection pooling is set**
- [ ] **Static files are collected**
- [ ] **Media files are configured**
- [ ] **CDN is configured (if applicable)**

### **Monitoring Checklist**
- [ ] **Error tracking is configured**
- [ ] **Logging is set up**
- [ ] **Health checks are working**
- [ ] **Performance monitoring is active**
- [ ] **Alerting is configured**

### **Deployment Checklist**
- [ ] **Environment variables are set**
- [ ] **Database migrations are run**
- [ ] **Static files are collected**
- [ ] **Services are healthy**
- [ ] **Monitoring is active**
- [ ] **Backup is configured**

## 🎯 **Quick Commands**

### **Development Commands**
```bash
# Start development environment
docker-compose up -d

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### **Production Commands**
```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=config.settings.production

# Run production setup
python manage.py migrate
python manage.py collectstatic --noinput

# Start production services
gunicorn config.wsgi:application
celery -A config worker -l info
celery -A config beat -l info
```

### **Validation Commands**
```bash
# Validate environment
python scripts/validate_environment.py

# Test health endpoints
curl http://localhost:8000/health/
curl http://localhost:8001/health/
curl http://localhost:3000/health/

# Run security scan
python monitoring/security_scanner.py
```

## 📚 **Additional Resources**

### **Documentation**
- [Django Environment Variables](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Docker Compose Configuration](https://docs.docker.com/compose/)
- [Environment Security Best Practices](https://12factor.net/config)

### **Tools**
- [Environment Variable Validator](scripts/validate_environment.py)
- [Security Scanner](monitoring/security_scanner.py)
- [Performance Monitor](monitoring/performance_monitor.py)

### **Support**
- Check logs in `logs/` directory
- Run validation script for diagnostics
- Check monitoring dashboard for system status

---

**Status: READY FOR DEPLOYMENT** ✅  
**Security: CONFIGURED** ✅  
**Monitoring: ACTIVE** ✅  
**Performance: OPTIMIZED** ✅
