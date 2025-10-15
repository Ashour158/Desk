# Helpdesk Platform Documentation

## Overview

The Helpdesk Platform is a comprehensive, multi-tenant helpdesk and field service management system built with Django, FastAPI, and Node.js. It provides enterprise-grade features that surpass commercial platforms like Zoho Desk.

## Architecture

### Hybrid Architecture
- **Django Monolith**: Core business logic, user management, tickets, FSM
- **AI Microservice (FastAPI)**: Ticket categorization, sentiment analysis, chatbot
- **Real-time Service (Node.js)**: Live chat, notifications, GPS tracking
- **Background Workers (Celery)**: Email processing, scheduled tasks

### Multi-tenancy
- Shared PostgreSQL database with `organization_id` isolation
- Subdomain-based tenant routing
- Tenant-aware models and managers

## Features

### Core Features
- **Multi-tenant Architecture**: Complete organization isolation
- **Ticket Management**: Full CRUD with comments, attachments, history
- **Field Service Management**: Work orders, technicians, scheduling, route optimization
- **Knowledge Base**: Articles, categories, search, feedback
- **Automation Engine**: Workflows, SLA management, rules engine
- **Analytics Dashboard**: Reports, metrics, custom queries
- **API Framework**: RESTful APIs with authentication, permissions
- **Real-time Features**: WebSockets, live chat, notifications
- **Security**: Encryption, authentication, authorization, audit logging
- **Mobile Support**: Cross-platform mobile applications

### Advanced Features
- **AI-Powered Features**: NLP, sentiment analysis, chatbot, predictions
- **Customer Intelligence**: 360° customer view, personalization, success management
- **Advanced Analytics**: Data science platform, real-time analytics, BI tools
- **Integration Hub**: Enterprise integrations, API management, workflow automation
- **Mobile & IoT**: Cross-platform mobile, IoT edge computing, AR/VR support
- **Advanced Security**: Threat protection, security management, compliance
- **Workflow Automation**: Intelligent process automation, advanced workflow engine
- **Communication Platform**: Unified communication hub, video/audio, AI communication

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with PostGIS
- Redis 7+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/helpdesk-platform.git
cd helpdesk-platform
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start services with Docker Compose**
```bash
docker-compose up -d
```

4. **Run database migrations**
```bash
docker-compose exec web python manage.py migrate
```

5. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Load initial data**
```bash
docker-compose exec web python manage.py loaddata fixtures/initial_data.json
```

7. **Access the application**
- Main application: http://localhost
- Admin panel: http://localhost/admin
- API documentation: http://localhost/api/docs/

## Development

### Local Development Setup

1. **Set up Python virtual environment**
```bash
cd core
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/base.txt
```

2. **Set up Node.js for real-time service**
```bash
cd realtime-service
npm install
```

3. **Set up Python for AI service**
```bash
cd ai-service
pip install -r requirements.txt
```

4. **Run database migrations**
```bash
cd core
python manage.py migrate
```

5. **Start development servers**
```bash
# Terminal 1: Django web server
cd core
python manage.py runserver

# Terminal 2: AI service
cd ai-service
uvicorn app.main:app --reload --port 8001

# Terminal 3: Real-time service
cd realtime-service
npm run dev

# Terminal 4: Celery worker
cd core
celery -A config worker -l info
```

### Testing

```bash
# Run all tests
cd core
python manage.py test

# Run specific test modules
python manage.py test apps.tickets.tests

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Code Quality

```bash
# Linting
flake8 apps/
black apps/
isort apps/

# Type checking
mypy apps/
```

## Deployment

### Docker Deployment

1. **Production deployment**
```bash
# Build and start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run deployment script
./deploy/scripts/deploy.sh production
```

2. **Environment-specific configurations**
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Cloud Deployment

#### AWS Deployment
```bash
# Deploy using CloudFormation
aws cloudformation create-stack \
  --stack-name helpdesk-platform \
  --template-body file://deploy/aws/cloudformation.yaml \
  --capabilities CAPABILITY_IAM
```

#### Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

#### Render Deployment
```bash
# Connect GitHub repository to Render
# Render will automatically deploy from the repository
```

## API Documentation

### Authentication
All API endpoints require authentication using JWT tokens.

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/tickets/
```

### Core Endpoints

#### Tickets
- `GET /api/v1/tickets/` - List tickets
- `POST /api/v1/tickets/` - Create ticket
- `GET /api/v1/tickets/{id}/` - Get ticket details
- `PUT /api/v1/tickets/{id}/` - Update ticket
- `DELETE /api/v1/tickets/{id}/` - Delete ticket

#### Work Orders
- `GET /api/v1/work-orders/` - List work orders
- `POST /api/v1/work-orders/` - Create work order
- `GET /api/v1/work-orders/{id}/` - Get work order details
- `PUT /api/v1/work-orders/{id}/` - Update work order

#### Knowledge Base
- `GET /api/v1/kb/articles/` - List articles
- `POST /api/v1/kb/articles/` - Create article
- `GET /api/v1/kb/articles/{id}/` - Get article details
- `PUT /api/v1/kb/articles/{id}/` - Update article

### AI Service Endpoints

#### Ticket Categorization
```bash
curl -X POST http://localhost:8001/categorize \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Login issue",
    "description": "Cannot login to the system",
    "categories": ["Technical", "Billing", "General"]
  }'
```

#### Sentiment Analysis
```bash
curl -X POST http://localhost:8001/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "I am very frustrated with this service"}'
```

#### Response Suggestions
```bash
curl -X POST http://localhost:8001/suggest-response \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_content": "Cannot access my account",
    "kb_context": ["Password reset guide", "Account recovery steps"]
  }'
```

## Configuration

### Environment Variables

#### Django Settings
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/helpdesk

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
DEBUG=False

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Storage
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket
```

#### AI Service Settings
```bash
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379/1
```

#### Real-time Service Settings
```bash
REDIS_URL=redis://localhost:6379/2
DJANGO_API_URL=http://localhost:8000
```

### Database Configuration

#### PostgreSQL with PostGIS
```sql
-- Create database
CREATE DATABASE helpdesk;

-- Enable PostGIS extension
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```

#### Redis Configuration
```bash
# Redis configuration for production
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## Monitoring and Logging

### Health Checks
- Django: `http://localhost:8000/health/`
- AI Service: `http://localhost:8001/health/`
- Real-time Service: `http://localhost:3000/health/`

### Logging
Logs are stored in `/var/log/helpdesk/` and can be viewed with:
```bash
# View Django logs
docker-compose logs web

# View AI service logs
docker-compose logs ai-service

# View real-time service logs
docker-compose logs realtime-service
```

### Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Sentry**: Error tracking and performance monitoring

## Security

### Security Features
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: Data encryption at rest and in transit
- **Rate Limiting**: API rate limiting and DDoS protection
- **CORS**: Cross-origin resource sharing configuration
- **CSP**: Content Security Policy headers
- **Audit Logging**: Comprehensive audit trail

### Security Best Practices
1. **Use HTTPS** in production
2. **Regular security updates**
3. **Strong password policies**
4. **Two-factor authentication**
5. **Regular backups**
6. **Monitor access logs**

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
docker-compose exec web python manage.py dbshell

# Reset database
docker-compose down
docker volume rm helpdesk_postgres_data
docker-compose up -d
```

#### Redis Connection Issues
```bash
# Check Redis connectivity
docker-compose exec redis redis-cli ping

# Monitor Redis
docker-compose exec redis redis-cli monitor
```

#### Celery Worker Issues
```bash
# Check Celery status
docker-compose exec web celery -A config inspect active

# Restart Celery workers
docker-compose restart celery
```

### Performance Issues

#### Database Optimization
```bash
# Analyze slow queries
docker-compose exec db psql -U helpdesk_user -d helpdesk -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Update table statistics
docker-compose exec web python manage.py dbshell -c "ANALYZE;"
```

#### Cache Optimization
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Clear cache
docker-compose exec web python manage.py clear_cache
```

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Run the test suite
6. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use Black for code formatting
- Write comprehensive tests
- Document new features
- Follow semantic versioning

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- **Documentation**: [docs.helpdesk-platform.com](https://docs.helpdesk-platform.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/helpdesk-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/helpdesk-platform/discussions)
- **Email**: support@helpdesk-platform.com
