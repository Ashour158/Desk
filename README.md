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
- Docker & Docker Compose (recommended)

### Quick Start with Setup Script

The fastest way to get started is using our setup script:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/helpdesk-platform.git
cd helpdesk-platform

# 2. Run the setup script (installs everything automatically)
./scripts/setup.sh
```

The setup script will:
- ✅ Create and activate virtual environment
- ✅ Install all Python dependencies
- ✅ Install and configure pre-commit hooks
- ✅ Set up environment variables from env.example
- ✅ Install frontend dependencies
- ✅ Run database migrations
- ✅ Collect static files

### Manual Setup (Alternative)

If you prefer manual setup or the script doesn't work:

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

4. **Start with Docker Compose** (Recommended)
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

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality before commits. The hooks are automatically installed when you run the setup script.

**Manual Installation:**
```bash
pip install pre-commit
pre-commit install
```

**Pre-commit Checks Include:**
- ✅ Python code formatting (black, isort)
- ✅ Python linting (flake8)
- ✅ Python security scanning (bandit)
- ✅ JavaScript/TypeScript linting (eslint)
- ✅ JavaScript/TypeScript formatting (prettier)
- ✅ Secret detection (detect-secrets)
- ✅ YAML validation
- ✅ Django-specific checks
- ✅ Dockerfile linting

**Run Manually:**
```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

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

## 📚 Documentation

This project has comprehensive documentation organized by topic:

### Documentation Structure

- **[docs/deployment/](docs/deployment/)** - Deployment guides, infrastructure setup, and configuration
  - AWS, Azure, DigitalOcean deployment guides
  - Environment configuration and setup checklists
  - CI/CD pipeline documentation
  - Rollback procedures and operational documentation

- **[docs/security/](docs/security/)** - Security audits, compliance, and best practices
  - Security audit reports and scan results
  - Security implementation guides
  - API security documentation
  - Compliance reports

- **[docs/testing/](docs/testing/)** - Testing documentation and coverage reports
  - Test execution guides and results
  - Code quality reports
  - Test coverage analysis
  - Database and API testing documentation

- **[docs/api/](docs/api/)** - API documentation and endpoint references
  - Comprehensive API documentation
  - API endpoint inventory
  - API validation reports

- **[docs/architecture/](docs/architecture/)** - System architecture and design
  - Database schemas and ER diagrams
  - Frontend architecture and component structure
  - State management documentation

- **[docs/performance/](docs/performance/)** - Performance optimization and monitoring
  - Performance analysis reports
  - Database query optimization
  - Frontend performance optimization
  - Monitoring setup and best practices

### Quick Documentation Links

- **Getting Started**: [README.md](README.md) (this file)
- **Developer Guide**: [docs/DEVELOPER_ONBOARDING.md](docs/DEVELOPER_ONBOARDING.md)
- **API Reference**: [docs/api/COMPREHENSIVE_API_DOCUMENTATION.md](docs/api/COMPREHENSIVE_API_DOCUMENTATION.md)
- **Deployment Guide**: [docs/deployment/](docs/deployment/)
- **Testing Guide**: [docs/testing/TEST_EXECUTION_GUIDE.md](docs/testing/TEST_EXECUTION_GUIDE.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

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

### Test Organization

Tests are organized in the following structure:
- **tests/** - Integration and system-level tests
- **core/tests/** - Django unit tests
- **test_scripts/** - Specialized test scripts

### Run Tests

```bash
# Run all integration tests
pytest tests/

# Run Django unit tests
cd core
python manage.py test

# Run with coverage
pytest tests/ --cov=core --cov-report=html

# Run specific test file
pytest tests/test_health_checks.py

# API tests
pytest core/tests/test_apis.py

# Frontend tests
cd customer-portal
npm test

# E2E tests
npm run test:e2e
```

### Test Coverage

```bash
# Generate coverage report
cd core
coverage run --source='.' manage.py test
coverage report
coverage html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Continuous Testing

The CI/CD pipeline automatically runs:
- ✅ Unit tests
- ✅ Integration tests
- ✅ Linting (flake8, black, eslint)
- ✅ Security scans (bandit, Trivy)
- ✅ Dependency scanning
- ✅ Code quality checks

See [docs/testing/](docs/testing/) for detailed testing documentation.

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

### Security Scanning

The project includes comprehensive security scanning:
- **Dependency Scanning**: Automated vulnerability checks for Python and Node.js dependencies
- **SAST (Static Application Security Testing)**: Bandit for Python, CodeQL for multi-language analysis
- **Container Scanning**: Trivy for Docker image vulnerabilities
- **Secret Detection**: Pre-commit hooks to prevent committing secrets
- **Pre-commit Hooks**: Automated security checks before every commit

### Security Best Practices

**Environment Variables:**
- ✅ Never commit `.env` files or `env.production` to version control
- ✅ Use strong, unique secrets for each environment
- ✅ Rotate secrets regularly (every 90 days)
- ✅ Use secrets management services for production

**Development:**
- ✅ Run pre-commit hooks before committing code
- ✅ Keep dependencies up to date
- ✅ Review security scan results in CI/CD
- ✅ Follow secure coding practices

### Compliance
- GDPR compliance features
- SOC 2 Type II ready
- Data retention policies
- Audit logging

For detailed security information, see [docs/security/](docs/security/).
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
