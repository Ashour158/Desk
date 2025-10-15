#!/bin/bash
# Environment Setup Validation Script
# Validates prerequisites and environment configuration for the Helpdesk Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REQUIRED_PYTHON_VERSION="3.11"
REQUIRED_NODE_VERSION="18"
REQUIRED_DOCKER_VERSION="20"
REQUIRED_DOCKER_COMPOSE_VERSION="2.0"

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Helper functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Helpdesk Platform Setup Check${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_CHECKS++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_CHECKS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNING_CHECKS++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
    local cmd=$1
    local name=$2
    local required_version=$3
    
    ((TOTAL_CHECKS++))
    
    if command -v "$cmd" &> /dev/null; then
        if [ -n "$required_version" ]; then
            local version=$(get_version "$cmd")
            if version_compare "$version" "$required_version"; then
                print_success "$name is installed (version: $version)"
            else
                print_error "$name version $version is too old. Required: $required_version+"
            fi
        else
            print_success "$name is installed"
        fi
    else
        print_error "$name is not installed"
    fi
}

get_version() {
    local cmd=$1
    case $cmd in
        python|python3)
            python --version 2>&1 | cut -d' ' -f2
            ;;
        node)
            node --version | cut -d'v' -f2
            ;;
        docker)
            docker --version | cut -d' ' -f3 | cut -d',' -f1
            ;;
        docker-compose)
            docker-compose --version | cut -d' ' -f3 | cut -d',' -f1
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

version_compare() {
    local version1=$1
    local version2=$2
    
    # Simple version comparison (major.minor)
    local v1_major=$(echo "$version1" | cut -d'.' -f1)
    local v1_minor=$(echo "$version1" | cut -d'.' -f2)
    local v2_major=$(echo "$version2" | cut -d'.' -f1)
    local v2_minor=$(echo "$version2" | cut -d'.' -f2)
    
    if [ "$v1_major" -gt "$v2_major" ] || ([ "$v1_major" -eq "$v2_major" ] && [ "$v1_minor" -ge "$v2_minor" ]); then
        return 0
    else
        return 1
    fi
}

check_file() {
    local file=$1
    local name=$2
    local required=$3
    
    ((TOTAL_CHECKS++))
    
    if [ -f "$file" ]; then
        if [ "$required" = "true" ]; then
            print_success "$name exists"
        else
            print_success "$name exists (optional)"
        fi
    else
        if [ "$required" = "true" ]; then
            print_error "$name is missing"
        else
            print_warning "$name is missing (optional)"
        fi
    fi
}

check_environment_variable() {
    local var=$1
    local name=$2
    local required=$3
    
    ((TOTAL_CHECKS++))
    
    if [ -n "${!var}" ]; then
        print_success "$name is set"
    else
        if [ "$required" = "true" ]; then
            print_error "$name is not set"
        else
            print_warning "$name is not set (optional)"
        fi
    fi
}

check_port() {
    local port=$1
    local service=$2
    
    ((TOTAL_CHECKS++))
    
    if lsof -i :$port &> /dev/null || netstat -an | grep :$port &> /dev/null; then
        print_warning "Port $port is in use (may conflict with $service)"
    else
        print_success "Port $port is available"
    fi
}

check_docker_service() {
    ((TOTAL_CHECKS++))
    
    if docker info &> /dev/null; then
        print_success "Docker service is running"
    else
        print_error "Docker service is not running"
    fi
}

check_disk_space() {
    local required_gb=$1
    local path=$2
    
    ((TOTAL_CHECKS++))
    
    local available_gb=$(df -BG "$path" | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [ "$available_gb" -ge "$required_gb" ]; then
        print_success "Sufficient disk space available (${available_gb}GB free)"
    else
        print_error "Insufficient disk space (${available_gb}GB free, need ${required_gb}GB)"
    fi
}

check_memory() {
    local required_gb=$1
    
    ((TOTAL_CHECKS++))
    
    local total_memory_gb=$(free -g | awk 'NR==2{print $2}')
    
    if [ "$total_memory_gb" -ge "$required_gb" ]; then
        print_success "Sufficient memory available (${total_memory_gb}GB total)"
    else
        print_warning "Low memory (${total_memory_gb}GB total, recommended ${required_gb}GB)"
    fi
}

# Main validation function
validate_setup() {
    print_header
    
    echo -e "${BLUE}Checking prerequisites...${NC}"
    echo ""
    
    # Check system requirements
    check_command "python" "Python" "$REQUIRED_PYTHON_VERSION"
    check_command "node" "Node.js" "$REQUIRED_NODE_VERSION"
    check_command "docker" "Docker" "$REQUIRED_DOCKER_VERSION"
    check_command "docker-compose" "Docker Compose" "$REQUIRED_DOCKER_COMPOSE_VERSION"
    
    echo ""
    echo -e "${BLUE}Checking Docker service...${NC}"
    check_docker_service
    
    echo ""
    echo -e "${BLUE}Checking system resources...${NC}"
    check_disk_space 5 "."
    check_memory 4
    
    echo ""
    echo -e "${BLUE}Checking project files...${NC}"
    check_file "docker-compose.yml" "Docker Compose configuration" "true"
    check_file "env.example" "Environment template" "true"
    check_file "README.md" "README documentation" "true"
    check_file "core/requirements/production.txt" "Python requirements" "true"
    check_file "customer-portal/package.json" "Node.js package.json" "true"
    
    echo ""
    echo -e "${BLUE}Checking environment configuration...${NC}"
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        print_success ".env file exists"
        source .env
        
        # Check required environment variables
        check_environment_variable "SECRET_KEY" "SECRET_KEY" "true"
        check_environment_variable "DB_PASSWORD" "DB_PASSWORD" "true"
        check_environment_variable "REDIS_URL" "REDIS_URL" "true"
        
        # Check optional but recommended variables
        check_environment_variable "OPENAI_API_KEY" "OPENAI_API_KEY" "false"
        check_environment_variable "GOOGLE_MAPS_API_KEY" "GOOGLE_MAPS_API_KEY" "false"
        check_environment_variable "TWILIO_ACCOUNT_SID" "TWILIO_ACCOUNT_SID" "false"
        check_environment_variable "SENDGRID_API_KEY" "SENDGRID_API_KEY" "false"
    else
        print_error ".env file not found"
        print_info "Creating .env file from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success ".env file created from template"
            print_warning "Please edit .env file with your configuration"
        else
            print_error "env.example file not found"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}Checking port availability...${NC}"
    check_port 8000 "Django application"
    check_port 3000 "React development server"
    check_port 5432 "PostgreSQL database"
    check_port 6379 "Redis cache"
    check_port 80 "Nginx web server"
    
    echo ""
    echo -e "${BLUE}Checking Docker images...${NC}"
    
    # Check if required Docker images exist
    if docker images | grep -q "postgis/postgis"; then
        print_success "PostGIS image available"
    else
        print_info "PostGIS image will be downloaded on first run"
    fi
    
    if docker images | grep -q "redis"; then
        print_success "Redis image available"
    else
        print_info "Redis image will be downloaded on first run"
    fi
    
    if docker images | grep -q "nginx"; then
        print_success "Nginx image available"
    else
        print_info "Nginx image will be downloaded on first run"
    fi
    
    echo ""
    echo -e "${BLUE}Checking network configuration...${NC}"
    
    # Check if Docker network exists
    if docker network ls | grep -q "desk_default"; then
        print_success "Docker network exists"
    else
        print_info "Docker network will be created on first run"
    fi
    
    echo ""
    print_summary
}

print_summary() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Validation Summary${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "Total checks: $TOTAL_CHECKS"
    echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}"
    echo -e "${YELLOW}Warnings: $WARNING_CHECKS${NC}"
    echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
    echo ""
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        if [ $WARNING_CHECKS -eq 0 ]; then
            echo -e "${GREEN}🎉 All checks passed! You're ready to start development.${NC}"
            echo ""
            echo -e "${BLUE}Next steps:${NC}"
            echo "1. Review and update .env file if needed"
            echo "2. Run: docker-compose up -d"
            echo "3. Run: docker-compose exec web python manage.py migrate"
            echo "4. Run: docker-compose exec web python manage.py createsuperuser"
            echo "5. Access the application at http://localhost:8000"
        else
            echo -e "${YELLOW}⚠️  Setup completed with warnings. Review the warnings above.${NC}"
            echo ""
            echo -e "${BLUE}Next steps:${NC}"
            echo "1. Address any warnings above"
            echo "2. Run: docker-compose up -d"
        fi
    else
        echo -e "${RED}❌ Setup validation failed. Please fix the errors above.${NC}"
        echo ""
        echo -e "${BLUE}Common solutions:${NC}"
        echo "1. Install missing prerequisites"
        echo "2. Start Docker service"
        echo "3. Create .env file from template"
        echo "4. Check port availability"
        exit 1
    fi
}

# Help function
show_help() {
    echo "Environment Setup Validation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Enable verbose output"
    echo "  -q, --quiet   Suppress output except errors"
    echo ""
    echo "This script validates your development environment for the Helpdesk Platform."
    echo "It checks prerequisites, configuration, and system requirements."
}

# Parse command line arguments
VERBOSE=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run validation
validate_setup
