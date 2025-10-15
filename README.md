# Django Multi-Tenant Helpdesk & FSM Platform

A comprehensive, enterprise-grade helpdesk and field service management platform built with Django, featuring multi-tenancy, AI integration, real-time communication, and advanced automation.

## 🚀 Features

### Core Helpdesk Features
- **Multi-Channel Support**: Email, web, chat, phone, social media
- **Advanced Ticket Management**: Assignment, routing, SLA tracking, merging/splitting
- **Knowledge Base**: SEO-optimized articles, categories, feedback system
- **Customer Portal**: React-based self-service interface
- **Real-time Chat**: Live chat with typing indicators and file sharing

### Field Service Management
- **Work Order Management**: Complete lifecycle from creation to completion
- **Technician Scheduling**: GPS tracking, route optimization, skill matching
- **Asset Management**: Equipment tracking, maintenance scheduling
- **Inventory Control**: Parts tracking, reorder alerts, supplier management
- **Service Reports**: Digital signatures, photo capture, customer feedback

### AI & Automation
- **Smart Categorization**: AI-powered ticket classification
- **Sentiment Analysis**: Customer mood detection
- **Response Suggestions**: AI-generated reply recommendations
- **Workflow Automation**: Rule-based ticket routing and actions
- **Predictive Analytics**: SLA breach prediction, performance insights

### Advanced Features
- **Multi-Tenancy**: Complete organization isolation
- **Role-Based Access Control**: Granular permissions system
- **Real-time Notifications**: WebSocket-based live updates
- **Advanced Analytics**: Custom reports, dashboards, data export
- **Third-party Integrations**: Stripe, Twilio, SendGrid, webhooks
- **Mobile App**: React Native for technicians

## 🏗️ Architecture

### Hybrid Architecture
- **Django Monolith**: Core business logic, admin panel
- **AI Microservice**: FastAPI service for AI features
- **Real-time Service**: Node.js/Socket.io for live features
- **Celery Workers**: Background task processing
- **PostgreSQL**: Primary database with PostGIS
- **Redis**: Caching and message broker

### Technology Stack
- **Backend**: Django 4.2, Django REST Framework, Celery
- **Database**: PostgreSQL 15+ with PostGIS extension
- **Cache**: Redis 7+
- **AI/ML**: OpenAI GPT-4, Transformers, scikit-learn
- **Frontend**: React 18, Tailwind CSS, Socket.io
- **Mobile**: React Native
- **Infrastructure**: Docker, Digital Ocean, Nginx

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with PostGIS
- Redis 7+
- Docker & Docker Compose

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/your-username/helpdesk-platform.git
cd helpdesk-platform
```

2. **Validate your environment** (Recommended)
```bash
# Linux/macOS
./scripts/validate-setup.sh

# Windows PowerShell
.\scripts\validate-setup-fixed.ps1
```

3. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your configuration
```

4. **Start with Docker Compose**
```bash
docker-compose up -d
```

5. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

6. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

7. **Access the application**
- Django Admin: http://localhost:8000/admin/
- Customer Portal: http://localhost:3000
- API Documentation: http://localhost:8000/api/docs/

### Environment Setup

The environment validation script checks:
- ✅ **Prerequisites**: Python, Node.js, Docker, Docker Compose
- ✅ **System Resources**: Disk space, memory
- ✅ **Port Availability**: 8000, 3000, 5432, 6379, 80
- ✅ **Configuration Files**: docker-compose.yml, .env, requirements
- ✅ **Environment Variables**: Required and optional variables
- ✅ **Docker Service**: Running and accessible
- ✅ **Project Files**: All necessary files present

**Required Environment Variables:**
```bash
SECRET_KEY=your-secret-key-here
DB_PASSWORD=your-database-password
REDIS_URL=redis://localhost:6379/0
```

**Optional Environment Variables:**
```bash
OPENAI_API_KEY=your-openai-key          # For AI features
GOOGLE_MAPS_API_KEY=your-maps-key       # For location services
TWILIO_ACCOUNT_SID=your-twilio-sid      # For SMS notifications
SENDGRID_API_KEY=your-sendgrid-key      # For email services
```

### Manual Installation

1. **Validate Environment** (Recommended)
```bash
# Linux/macOS
./scripts/validate-setup.sh

# Windows PowerShell
.\scripts\validate-setup-fixed.ps1
```

2. **Backend Setup**
```bash
cd core
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py runserver
```

3. **AI Service Setup**
```bash
cd ai-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

4. **Real-time Service Setup**
```bash
cd realtime-service
npm install
npm start
```

5. **Customer Portal Setup**
```bash
cd customer-portal
npm install
npm start
```

### Troubleshooting

**Common Issues:**

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000  # Linux/macOS
   netstat -ano | findstr :8000  # Windows
   
   # Kill the process or use different ports
   ```

2. **Docker Service Not Running**
   ```bash
   # Start Docker service
   sudo systemctl start docker  # Linux
   # Or start Docker Desktop on Windows/macOS
   ```

3. **Environment Variables Missing**
   ```bash
   # Run validation script
   ./scripts/validate-setup.sh
   
   # Check .env file
   cat .env
   ```

4. **Database Connection Issues**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps db
   
   # Check database logs
   docker-compose logs db
   ```

5. **Permission Issues**
   ```bash
   # Make scripts executable
   chmod +x scripts/validate-setup.sh
   
   # Fix Docker permissions (Linux)
   sudo usermod -aG docker $USER
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_HOST=localhost
DB_NAME=helpdesk
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# External Services
GOOGLE_MAPS_API_KEY=your-maps-key
TWILIO_ACCOUNT_SID=your-twilio-sid
SENDGRID_API_KEY=your-sendgrid-key
```

### Database Setup

1. **Create PostgreSQL database with PostGIS**
```sql
CREATE DATABASE helpdesk;
CREATE EXTENSION postgis;
```

2. **Run migrations**
```bash
python manage.py migrate
```

3. **Create initial data**
```bash
python manage.py loaddata initial_data.json
```

## 📱 API Documentation

### Authentication
```bash
# Login
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "password"
}

# Register
POST /api/v1/auth/register/
{
  "email": "user@example.com",
  "password": "password",
  "full_name": "John Doe"
}
```

### Tickets
```bash
# List tickets
GET /api/v1/tickets/

# Create ticket
POST /api/v1/tickets/
{
  "subject": "Login issue",
  "description": "Cannot login to the system",
  "priority": "high"
}

# Assign ticket
POST /api/v1/tickets/{id}/assign/
{
  "agent_id": "uuid"
}
```

### Work Orders
```bash
# List work orders
GET /api/v1/work-orders/

# Create work order
POST /api/v1/work-orders/
{
  "title": "Installation",
  "description": "Install new equipment",
  "customer": "uuid",
  "scheduled_start": "2024-01-01T09:00:00Z"
}
```

## 🚀 Deployment

### Digital Ocean Deployment

1. **Create App Platform App**
```yaml
# deploy/app.yaml
name: helpdesk-platform
services:
- name: django
  source_dir: /core
  github:
    repo: your-username/helpdesk-platform
    branch: main
  run_command: gunicorn config.wsgi:application
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  envs:
  - key: DJANGO_SETTINGS_MODULE
    value: config.settings.production
```

2. **Set up managed databases**
- PostgreSQL with PostGIS
- Redis cluster
- Spaces for file storage

3. **Configure domains and SSL**
- Custom domain setup
- SSL certificate configuration
- CDN setup

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd core
python manage.py test

# API tests
pytest tests/api/

# Frontend tests
cd customer-portal
npm test

# E2E tests
npm run test:e2e
```

### Test Coverage
```bash
# Generate coverage report
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📊 Monitoring

### Health Checks
- Django: `/health/`
- AI Service: `/health/`
- Real-time Service: `/health/`

### Metrics
- Application metrics via Prometheus
- Database performance monitoring
- Redis cache hit rates
- API response times

### Logging
- Structured logging with Winston
- Error tracking with Sentry
- Audit logs for compliance

## 🔒 Security

### Security Features
- JWT authentication with refresh tokens
- Two-factor authentication (TOTP)
- Rate limiting and DDoS protection
- CORS and CSP headers
- SQL injection prevention
- XSS protection
- Data encryption at rest

### Compliance
- GDPR compliance features
- SOC 2 Type II ready
- Data retention policies
- Audit trail logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for React components
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [docs.helpdesk-platform.com](https://docs.helpdesk-platform.com)
- Issues: [GitHub Issues](https://github.com/your-username/helpdesk-platform/issues)
- Community: [Discord Server](https://discord.gg/helpdesk-platform)
- Email: support@helpdesk-platform.com

## 🎯 Roadmap

### Phase 1 (Completed)
- ✅ Core Django setup
- ✅ Multi-tenant architecture
- ✅ Basic ticket system
- ✅ User authentication

### Phase 2 (In Progress)
- 🔄 AI integration
- 🔄 Real-time features
- 🔄 Mobile app
- 🔄 Advanced analytics

### Phase 3 (Planned)
- 📋 Video chat integration
- 📋 IoT device support
- 📋 Advanced AI features
- 📋 White-label customization

---

**Built with ❤️ for modern support teams**
