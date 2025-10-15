#!/bin/bash

# AWS EKS Deployment Script for Helpdesk Platform
# This script deploys the helpdesk application to AWS EKS

set -e

# Configuration
AWS_REGION="us-west-2"
CLUSTER_NAME="helpdesk-cluster"
NAMESPACE="helpdesk"
ECR_REGISTRY=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install it first."
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_warn "Helm is not installed. Some features may not work."
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    log_info "Prerequisites check passed."
}

setup_aws_credentials() {
    log_info "Setting up AWS credentials..."
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    log_info "AWS Account ID: ${AWS_ACCOUNT_ID}"
    log_info "ECR Registry: ${ECR_REGISTRY}"
}

configure_kubectl() {
    log_info "Configuring kubectl for EKS cluster..."
    
    aws eks update-kubeconfig --region ${AWS_REGION} --name ${CLUSTER_NAME}
    
    # Verify cluster connection
    if kubectl cluster-info &> /dev/null; then
        log_info "Successfully connected to EKS cluster."
    else
        log_error "Failed to connect to EKS cluster."
        exit 1
    fi
}

create_namespace() {
    log_info "Creating namespace..."
    
    kubectl apply -f k8s/namespace.yaml
    log_info "Namespace '${NAMESPACE}' created."
}

deploy_configmap() {
    log_info "Deploying ConfigMap..."
    
    kubectl apply -f k8s/configmap.yaml
    log_info "ConfigMap deployed."
}

deploy_secrets() {
    log_info "Deploying secrets..."
    
    # Check if secrets file exists
    if [ ! -f "k8s/secrets.yaml" ]; then
        log_error "Secrets file not found. Please create k8s/secrets.yaml with your secrets."
        exit 1
    fi
    
    kubectl apply -f k8s/secrets.yaml
    log_info "Secrets deployed."
}

deploy_services() {
    log_info "Deploying services..."
    
    # Deploy Django application
    log_info "Deploying Django application..."
    kubectl apply -f k8s/django-deployment.yaml
    
    # Deploy AI service
    log_info "Deploying AI service..."
    kubectl apply -f k8s/ai-service-deployment.yaml
    
    # Deploy Realtime service
    log_info "Deploying Realtime service..."
    kubectl apply -f k8s/realtime-service-deployment.yaml
    
    # Deploy Celery workers
    log_info "Deploying Celery workers..."
    kubectl apply -f k8s/celery-deployment.yaml
    
    log_info "All services deployed."
}

deploy_ingress() {
    log_info "Deploying ingress..."
    
    kubectl apply -f k8s/ingress.yaml
    log_info "Ingress deployed."
}

wait_for_deployments() {
    log_info "Waiting for deployments to be ready..."
    
    # Wait for Django deployment
    kubectl rollout status deployment/django-app -n ${NAMESPACE} --timeout=300s
    log_info "Django deployment is ready."
    
    # Wait for AI service deployment
    kubectl rollout status deployment/ai-service -n ${NAMESPACE} --timeout=300s
    log_info "AI service deployment is ready."
    
    # Wait for Realtime service deployment
    kubectl rollout status deployment/realtime-service -n ${NAMESPACE} --timeout=300s
    log_info "Realtime service deployment is ready."
    
    # Wait for Celery worker deployment
    kubectl rollout status deployment/celery-worker -n ${NAMESPACE} --timeout=300s
    log_info "Celery worker deployment is ready."
    
    # Wait for Celery beat deployment
    kubectl rollout status deployment/celery-beat -n ${NAMESPACE} --timeout=300s
    log_info "Celery beat deployment is ready."
}

run_database_migrations() {
    log_info "Running database migrations..."
    
    kubectl exec -n ${NAMESPACE} deployment/django-app -- python manage.py migrate
    log_info "Database migrations completed."
}

collect_static_files() {
    log_info "Collecting static files..."
    
    kubectl exec -n ${NAMESPACE} deployment/django-app -- python manage.py collectstatic --noinput
    log_info "Static files collected."
}

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Add Prometheus Helm repository
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    # Install Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.adminPassword=admin123 \
        --set prometheus.prometheusSpec.retention=30d
    
    log_info "Monitoring setup completed."
}

show_deployment_info() {
    log_info "Deployment completed successfully!"
    echo ""
    echo "=== Deployment Information ==="
    echo "Cluster: ${CLUSTER_NAME}"
    echo "Namespace: ${NAMESPACE}"
    echo "Region: ${AWS_REGION}"
    echo ""
    
    # Get service information
    echo "=== Services ==="
    kubectl get services -n ${NAMESPACE}
    echo ""
    
    # Get pod information
    echo "=== Pods ==="
    kubectl get pods -n ${NAMESPACE}
    echo ""
    
    # Get ingress information
    echo "=== Ingress ==="
    kubectl get ingress -n ${NAMESPACE}
    echo ""
    
    # Get ALB DNS name
    ALB_DNS=$(kubectl get ingress helpdesk-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    if [ ! -z "$ALB_DNS" ]; then
        echo "Application URL: http://${ALB_DNS}"
    fi
}

cleanup() {
    log_info "Cleaning up resources..."
    
    kubectl delete -f k8s/ingress.yaml --ignore-not-found=true
    kubectl delete -f k8s/celery-deployment.yaml --ignore-not-found=true
    kubectl delete -f k8s/realtime-service-deployment.yaml --ignore-not-found=true
    kubectl delete -f k8s/ai-service-deployment.yaml --ignore-not-found=true
    kubectl delete -f k8s/django-deployment.yaml --ignore-not-found=true
    kubectl delete -f k8s/secrets.yaml --ignore-not-found=true
    kubectl delete -f k8s/configmap.yaml --ignore-not-found=true
    kubectl delete -f k8s/namespace.yaml --ignore-not-found=true
    
    log_info "Cleanup completed."
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            setup_aws_credentials
            configure_kubectl
            create_namespace
            deploy_configmap
            deploy_secrets
            deploy_services
            deploy_ingress
            wait_for_deployments
            run_database_migrations
            collect_static_files
            show_deployment_info
            ;;
        "cleanup")
            cleanup
            ;;
        "monitoring")
            setup_monitoring
            ;;
        "status")
            kubectl get all -n ${NAMESPACE}
            ;;
        *)
            echo "Usage: $0 {deploy|cleanup|monitoring|status}"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

