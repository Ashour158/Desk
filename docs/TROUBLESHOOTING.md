# 🔧 **Troubleshooting Guide**

**Version:** 1.0.0  
**Last Updated:** October 13, 2025

---

## 📋 **Table of Contents**

- [Quick Start](#quick-start)
- [Environment Issues](#environment-issues)
- [Docker Issues](#docker-issues)
- [Database Issues](#database-issues)
- [API Issues](#api-issues)
- [Frontend Issues](#frontend-issues)
- [Authentication Issues](#authentication-issues)
- [Performance Issues](#performance-issues)
- [Deployment Issues](#deployment-issues)
- [Logging and Debugging](#logging-and-debugging)
- [Getting Help](#getting-help)

---

## 🚀 **Quick Start**

### **Before You Start**

1. **Run Environment Validation**:
   ```bash
   # Linux/macOS
   ./scripts/validate-setup.sh
   
   # Windows PowerShell
   .\scripts\validate-setup.ps1
   ```

2. **Check Prerequisites**:
   - Python 3.11+
   - Node.js 18+
   - Docker & Docker Compose
   - PostgreSQL 15+ (if not using Docker)

3. **Verify Environment**:
   ```bash
   # Check Docker
   docker --version
   docker-compose --version
   
   # Check Python
   python --version
   
   # Check Node.js
   node --version
   ```

---

## 🌍 **Environment Issues**

### **Python Version Issues**

#### **Problem**: Wrong Python version
```bash
# Error: Python 3.11+ required
python --version  # Shows Python 3.9
```

#### **Solution**:
```bash
# Install Python 3.11+
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS
brew install python@3.11

# Windows
# Download from python.org or use chocolatey
choco install python --version=3.11.0
```

#### **Verify Installation**:
```bash
python3.11 --version
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### **Node.js Version Issues**

#### **Problem**: Wrong Node.js version
```bash
# Error: Node.js 18+ required
node --version  # Shows v16.x
```

#### **Solution**:
```bash
# Install Node.js 18+
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Or download from nodejs.org
# Or use package manager
```

#### **Verify Installation**:
```bash
node --version  # Should show v18.x or higher
npm --version
```

### **Environment Variables Issues**

#### **Problem**: Missing environment variables
```bash
# Error: SECRET_KEY must be set
django.core.exceptions.ImproperlyConfigured: SECRET_KEY must be set
```

#### **Solution**:
```bash
# Check if .env file exists
ls -la .env

# Create from template if missing
cp env.example .env

# Edit .env file
nano .env  # or your preferred editor

# Add required variables
SECRET_KEY=your-secret-key-here
DB_PASSWORD=your-database-password
REDIS_URL=redis://localhost:6379/0
```

#### **Verify Environment Variables**:
```bash
# Check if variables are loaded
python -c "import os; print(os.environ.get('SECRET_KEY'))"

# Or use the validation script
./scripts/validate-setup.sh
```

---

## 🐳 **Docker Issues**

### **Docker Service Not Running**

#### **Problem**: Docker daemon not running
```bash
# Error: Cannot connect to Docker daemon
docker: Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

#### **Solution**:
```bash
# Start Docker service
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS/Windows
# Start Docker Desktop application

# Verify Docker is running
docker info
```

### **Docker Compose Issues**

#### **Problem**: Docker Compose not found
```bash
# Error: docker-compose: command not found
```

#### **Solution**:
```bash
# Install Docker Compose
# Linux
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# macOS
brew install docker-compose

# Windows
# Install with Docker Desktop

# Verify installation
docker-compose --version
```

### **Port Already in Use**

#### **Problem**: Port conflicts
```bash
# Error: Port 8000 is already in use
docker-compose up
# ERROR: for web  Cannot start service web: driver failed programming external connectivity
```

#### **Solution**:
```bash
# Check what's using the port
# Linux/macOS
lsof -i :8000

# Windows
netstat -ano | findstr :8000

# Kill the process
# Linux/macOS
sudo kill -9 <PID>

# Windows
taskkill /PID <PID> /F

# Or use different ports
# Edit docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### **Docker Build Issues**

#### **Problem**: Build failures
```bash
# Error: Build failed
docker-compose build
# ERROR: failed to solve: failed to compute cache key
```

#### **Solution**:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test ./core

# Check for syntax errors
docker-compose config
```

### **Docker Volume Issues**

#### **Problem**: Volume permission issues
```bash
# Error: Permission denied
docker-compose exec web python manage.py migrate
# PermissionError: [Errno 13] Permission denied
```

#### **Solution**:
```bash
# Fix volume permissions
sudo chown -R $USER:$USER .

# Or run with proper user
docker-compose exec --user root web chown -R appuser:appuser /app

# Check volume mounts
docker-compose exec web ls -la /app
```

---

## 🗄️ **Database Issues**

### **PostgreSQL Connection Issues**

#### **Problem**: Database connection failed
```bash
# Error: Connection refused
django.db.utils.OperationalError: could not connect to server
```

#### **Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Check connection string
echo $DATABASE_URL
# Should be: postgresql://helpdesk_user:helpdesk_password@db:5432/helpdesk
```

### **Migration Issues**

#### **Problem**: Migration conflicts
```bash
# Error: Migration conflicts
python manage.py migrate
# django.db.utils.ProgrammingError: relation "table_name" already exists
```

#### **Solution**:
```bash
# Check migration status
python manage.py showmigrations

# Reset migrations (development only)
python manage.py migrate --fake-initial

# Or reset database
docker-compose down -v
docker-compose up -d
python manage.py migrate
```

### **Database Performance Issues**

#### **Problem**: Slow database queries
```bash
# Error: Database timeout
django.db.utils.OperationalError: server closed the connection
```

#### **Solution**:
```bash
# Check database connections
docker-compose exec db psql -U helpdesk_user -d helpdesk -c "SELECT * FROM pg_stat_activity;"

# Optimize database settings
# Edit docker-compose.yml
environment:
  POSTGRES_SHARED_BUFFERS: 256MB
  POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
  POSTGRES_MAINTENANCE_WORK_MEM: 64MB
```

---

## 🔌 **API Issues**

### **API Endpoint Not Found**

#### **Problem**: 404 errors
```bash
# Error: 404 Not Found
curl http://localhost:8000/api/v1/tickets/
# HTTP 404 Not Found
```

#### **Solution**:
```bash
# Check if API is running
curl http://localhost:8000/health/

# Check URL patterns
python manage.py show_urls | grep tickets

# Check if endpoint exists
curl http://localhost:8000/api/v1/tickets/ -H "Authorization: Bearer <token>"
```

### **Authentication Issues**

#### **Problem**: 401 Unauthorized
```bash
# Error: Authentication failed
curl http://localhost:8000/api/v1/tickets/
# HTTP 401 Unauthorized
```

#### **Solution**:
```bash
# Get JWT token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  | jq -r '.access')

# Use token in requests
curl http://localhost:8000/api/v1/tickets/ \
  -H "Authorization: Bearer $TOKEN"
```

### **CORS Issues**

#### **Problem**: CORS errors in browser
```bash
# Error: CORS policy
Access to fetch at 'http://localhost:8000/api/v1/tickets/' from origin 'http://localhost:3000' has been blocked by CORS policy
```

#### **Solution**:
```bash
# Check CORS settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)

# Update CORS settings
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

---

## 🎨 **Frontend Issues**

### **Build Issues**

#### **Problem**: Build failures
```bash
# Error: Build failed
npm run build
# ERROR: Build failed with errors
```

#### **Solution**:
```bash
# Check Node.js version
node --version

# Clear cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for syntax errors
npm run lint
```

### **Dependency Issues**

#### **Problem**: Package conflicts
```bash
# Error: Package conflicts
npm install
# npm ERR! peer dep missing
```

#### **Solution**:
```bash
# Check for conflicts
npm ls

# Install with force
npm install --force

# Or use yarn
yarn install

# Check package.json
cat package.json
```

### **Development Server Issues**

#### **Problem**: Development server not starting
```bash
# Error: Port 3000 in use
npm start
# Error: listen EADDRINUSE: address already in use :::3000
```

#### **Solution**:
```bash
# Check what's using port 3000
lsof -i :3000

# Kill the process
sudo kill -9 <PID>

# Or use different port
PORT=3001 npm start
```

---

## 🔐 **Authentication Issues**

### **JWT Token Issues**

#### **Problem**: Token expired
```bash
# Error: Token expired
curl http://localhost:8000/api/v1/tickets/
# HTTP 401 Unauthorized: Token is expired
```

#### **Solution**:
```bash
# Refresh token
curl -X POST "http://localhost:8000/api/v1/auth/refresh/" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh-token>"}'

# Or login again
curl -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### **Permission Issues**

#### **Problem**: Insufficient permissions
```bash
# Error: Permission denied
curl http://localhost:8000/api/v1/admin/users/
# HTTP 403 Forbidden: You do not have permission to perform this action
```

#### **Solution**:
```bash
# Check user permissions
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> print(user.is_staff)
>>> print(user.is_superuser)

# Grant permissions
python manage.py shell
>>> user.is_staff = True
>>> user.is_superuser = True
>>> user.save()
```

---

## ⚡ **Performance Issues**

### **Slow API Responses**

#### **Problem**: API responses are slow
```bash
# Response time > 5 seconds
curl -w "@curl-format.txt" http://localhost:8000/api/v1/tickets/
```

#### **Solution**:
```bash
# Check database queries
python manage.py shell
>>> from django.db import connection
>>> from apps.tickets.models import Ticket
>>> Ticket.objects.all()
>>> print(connection.queries)

# Optimize queries
# Use select_related and prefetch_related
tickets = Ticket.objects.select_related('user', 'category').prefetch_related('comments')
```

### **Memory Issues**

#### **Problem**: High memory usage
```bash
# Error: Out of memory
docker stats
# Container using > 2GB memory
```

#### **Solution**:
```bash
# Check memory usage
docker stats

# Optimize Docker settings
# Edit docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
    reservations:
      memory: 512M

# Restart containers
docker-compose restart
```

---

## 🚀 **Deployment Issues**

### **Production Build Issues**

#### **Problem**: Production build fails
```bash
# Error: Build failed in production
docker-compose -f docker-compose.prod.yml build
# ERROR: Build failed
```

#### **Solution**:
```bash
# Check production configuration
docker-compose -f docker-compose.prod.yml config

# Check environment variables
cat .env.production

# Build with verbose output
docker-compose -f docker-compose.prod.yml build --no-cache --progress=plain
```

### **SSL Certificate Issues**

#### **Problem**: SSL certificate errors
```bash
# Error: SSL certificate verification failed
curl https://api.helpdesk-platform.com/api/v1/tickets/
# SSL: CERTIFICATE_VERIFY_FAILED
```

#### **Solution**:
```bash
# Check certificate
openssl s_client -connect api.helpdesk-platform.com:443

# Update certificate
# Use Let's Encrypt or your certificate provider
certbot renew --dry-run
```

---

## 📊 **Logging and Debugging**

### **Enable Debug Logging**

#### **Django Logging**:
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

#### **Frontend Logging**:
```javascript
// In development
console.log('Debug info:', data);

// In production
if (process.env.NODE_ENV === 'development') {
    console.log('Debug info:', data);
}
```

### **Check Logs**

#### **Docker Logs**:
```bash
# Check all logs
docker-compose logs

# Check specific service
docker-compose logs web
docker-compose logs db
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f web
```

#### **Application Logs**:
```bash
# Check Django logs
docker-compose exec web tail -f /app/logs/django.log

# Check error logs
docker-compose exec web tail -f /app/logs/error.log
```

---

## 🆘 **Getting Help**

### **Self-Help Resources**

1. **Documentation**: Check project documentation first
2. **Issues**: Search existing GitHub issues
3. **Discussions**: Use GitHub Discussions
4. **Community**: Join Discord server

### **Reporting Issues**

When reporting issues, include:

1. **Environment**: OS, Python version, Node version
2. **Steps**: Detailed steps to reproduce
3. **Expected**: What should happen
4. **Actual**: What actually happens
5. **Logs**: Relevant error logs
6. **Screenshots**: If applicable

### **Contact Information**

- **GitHub Issues**: [Create new issue](https://github.com/your-username/helpdesk-platform/issues)
- **Discord Server**: [Join our Discord](https://discord.gg/helpdesk-platform)
- **Email**: support@helpdesk-platform.com

---

## 📚 **Additional Resources**

### **Documentation**
- [README.md](../README.md) - Project overview
- [API Documentation](API_REFERENCE.md) - API reference
- [Architecture Documentation](ARCHITECTURE.md) - System architecture
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

### **Tools**
- **Docker**: [Docker Documentation](https://docs.docker.com/)
- **Django**: [Django Documentation](https://docs.djangoproject.com/)
- **React**: [React Documentation](https://reactjs.org/docs/)
- **PostgreSQL**: [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### **Community**
- **GitHub**: [Project Repository](https://github.com/your-username/helpdesk-platform)
- **Discord**: [Community Server](https://discord.gg/helpdesk-platform)
- **Stack Overflow**: [Helpdesk Platform Tag](https://stackoverflow.com/questions/tagged/helpdesk-platform)

---

**Last Updated**: October 13, 2025  
**Next Review**: November 13, 2025  
**Maintained By**: Development Team
