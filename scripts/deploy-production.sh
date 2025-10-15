#!/bin/bash

# Production Deployment Script for Helpdesk Platform
# This script handles the complete production deployment process

set -e  # Exit on any error

echo "🚀 Starting Production Deployment for Helpdesk Platform"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required environment variables are set
check_environment() {
    print_status "Checking environment variables..."
    
    required_vars=(
        "SECRET_KEY"
        "DB_PASSWORD"
        "ALLOWED_HOSTS"
        "CORS_ALLOWED_ORIGINS"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables:"
        printf '%s\n' "${missing_vars[@]}"
        print_error "Please set these variables before deploying"
        exit 1
    fi
    
    print_success "Environment variables validated"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "Docker is running"
}

# Build production images
build_images() {
    print_status "Building production Docker images..."
    
    # Build all services
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    print_success "Docker images built successfully"
}

# Deploy services
deploy_services() {
    print_status "Deploying services..."
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Services deployed successfully"
}

# Wait for services to be healthy
wait_for_health() {
    print_status "Waiting for services to be healthy..."
    
    services=("db" "redis" "web" "ai-service" "realtime-service")
    max_attempts=30
    attempt=1
    
    for service in "${services[@]}"; do
        print_status "Checking health of $service..."
        
        while [ $attempt -le $max_attempts ]; do
            if docker-compose -f docker-compose.prod.yml ps $service | grep -q "healthy"; then
                print_success "$service is healthy"
                break
            elif [ $attempt -eq $max_attempts ]; then
                print_error "$service failed to become healthy after $max_attempts attempts"
                docker-compose -f docker-compose.prod.yml logs $service
                exit 1
            fi
            
            print_status "Waiting for $service... (attempt $attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        done
        
        attempt=1
    done
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput
    
    print_success "Database migrations completed"
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
    
    print_success "Static files collected"
}

# Create superuser (optional)
create_superuser() {
    print_status "Creating superuser..."
    
    # Check if superuser already exists
    if docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" | grep -q "Superuser exists"; then
        print_warning "Superuser already exists, skipping creation"
    else
        print_status "Please create a superuser manually:"
        echo "docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"
    fi
}

# Verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Check if all services are running
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_success "All services are running"
    else
        print_error "Some services are not running"
        docker-compose -f docker-compose.prod.yml ps
        exit 1
    fi
    
    # Test health endpoints
    print_status "Testing health endpoints..."
    
    # Test Django health
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        print_success "Django health check passed"
    else
        print_error "Django health check failed"
        exit 1
    fi
    
    # Test AI service health
    if curl -f http://localhost:8001/health/ > /dev/null 2>&1; then
        print_success "AI service health check passed"
    else
        print_error "AI service health check failed"
        exit 1
    fi
    
    # Test real-time service health
    if curl -f http://localhost:3000/health/ > /dev/null 2>&1; then
        print_success "Real-time service health check passed"
    else
        print_error "Real-time service health check failed"
        exit 1
    fi
}

# Show deployment summary
show_summary() {
    print_success "🎉 Production deployment completed successfully!"
    echo ""
    echo "📊 Deployment Summary:"
    echo "====================="
    echo "✅ All services deployed and healthy"
    echo "✅ Database migrations completed"
    echo "✅ Static files collected"
    echo "✅ Health checks passed"
    echo ""
    echo "🌐 Access Points:"
    echo "================="
    echo "• Django Admin: http://localhost:8000/admin/"
    echo "• API Documentation: http://localhost:8000/api/swagger/"
    echo "• Health Check: http://localhost:8000/health/"
    echo "• AI Service: http://localhost:8001/health/"
    echo "• Real-time Service: http://localhost:3000/health/"
    echo ""
    echo "📝 Next Steps:"
    echo "=============="
    echo "1. Create a superuser: docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"
    echo "2. Configure SSL certificates in ./nginx/ssl/"
    echo "3. Update DNS records to point to your server"
    echo "4. Set up monitoring and alerting"
    echo "5. Configure backup strategies"
    echo ""
    echo "🔧 Useful Commands:"
    echo "==================="
    echo "• View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "• Restart services: docker-compose -f docker-compose.prod.yml restart"
    echo "• Scale services: docker-compose -f docker-compose.prod.yml up -d --scale web=3"
    echo "• Stop services: docker-compose -f docker-compose.prod.yml down"
    echo ""
}

# Main deployment function
main() {
    echo "🚀 Helpdesk Platform Production Deployment"
    echo "=========================================="
    echo ""
    
    # Load environment variables
    if [ -f .env ]; then
        print_status "Loading environment variables from .env file..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        print_warning "No .env file found. Make sure environment variables are set."
    fi
    
    # Run deployment steps
    check_environment
    check_docker
    build_images
    deploy_services
    wait_for_health
    run_migrations
    collect_static
    create_superuser
    verify_deployment
    show_summary
    
    print_success "🎉 Production deployment completed successfully!"
}

# Run main function
main "$@"
