#!/bin/bash

# Helpdesk Platform Deployment Script
# This script deploys the helpdesk platform to production

set -e

# Configuration
ENVIRONMENT=${1:-production}
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="/backups"
LOG_FILE="/var/log/helpdesk-deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a $LOG_FILE
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a $LOG_FILE
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error "Docker is not installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed"
fi

log "Starting deployment for environment: $ENVIRONMENT"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database if it exists
if docker-compose ps db | grep -q "Up"; then
    log "Creating database backup..."
    docker-compose exec -T db pg_dump -U helpdesk_user helpdesk > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql
    log "Database backup created"
fi

# Pull latest images
log "Pulling latest Docker images..."
docker-compose pull

# Build new images
log "Building Docker images..."
docker-compose build --no-cache

# Stop existing services
log "Stopping existing services..."
docker-compose down

# Start services
log "Starting services..."
docker-compose up -d

# Wait for services to be healthy
log "Waiting for services to be healthy..."
sleep 30

# Check service health
check_service_health() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f $url > /dev/null 2>&1; then
            log "$service is healthy"
            return 0
        fi
        log "Waiting for $service to be healthy (attempt $attempt/$max_attempts)..."
        sleep 10
        ((attempt++))
    done
    
    error "$service failed to become healthy"
}

# Check Django service
check_service_health "Django" "http://localhost:8000/health/"

# Check AI service
check_service_health "AI Service" "http://localhost:8001/health/"

# Check Real-time service
check_service_health "Real-time Service" "http://localhost:3000/health/"

# Run database migrations
log "Running database migrations..."
docker-compose exec web python manage.py migrate

# Collect static files
log "Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
log "Creating superuser if needed..."
docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF

# Load initial data
log "Loading initial data..."
docker-compose exec web python manage.py loaddata fixtures/initial_data.json

# Run tests
log "Running tests..."
docker-compose exec web python manage.py test --verbosity=2

# Clean up old images
log "Cleaning up old Docker images..."
docker image prune -f

# Show service status
log "Deployment completed successfully!"
log "Service status:"
docker-compose ps

# Show logs
log "Recent logs:"
docker-compose logs --tail=50

log "Deployment completed successfully!"
log "Access the application at: http://localhost"
log "Admin panel: http://localhost/admin"
log "API documentation: http://localhost/api/docs/"

# Send notification (if configured)
if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Helpdesk platform deployed successfully!"}' \
        $SLACK_WEBHOOK_URL
fi
