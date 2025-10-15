#!/bin/bash

# Quick AWS Deployment Script for Helpdesk Platform
# This script automates the entire deployment process

set -e

# Configuration
AWS_REGION="us-west-2"
CLUSTER_NAME="helpdesk-cluster"
NAMESPACE="helpdesk"
ACCOUNT_ID=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Get AWS Account ID
get_account_id() {
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_info "AWS Account ID: $ACCOUNT_ID"
}

# Step 1: Deploy Infrastructure
deploy_infrastructure() {
    log_step "1. Deploying AWS Infrastructure with Terraform..."
    
    cd aws-infrastructure/terraform
    
    # Create terraform.tfvars if it doesn't exist
    if [ ! -f "terraform.tfvars" ]; then
        cat > terraform.tfvars << EOF
aws_region = "$AWS_REGION"
environment = "production"
cluster_name = "$CLUSTER_NAME"
db_password = "$(openssl rand -base64 32)"
redis_auth_token = "$(openssl rand -base64 32)"
ssl_certificate_arn = ""
domain_name = ""
EOF
        log_warn "Created terraform.tfvars with random passwords. Please update with your actual values."
    fi
    
    terraform init
    terraform plan
    terraform apply -auto-approve
    
    log_info "Infrastructure deployed successfully!"
}

# Step 2: Configure kubectl
configure_kubectl() {
    log_step "2. Configuring kubectl for EKS cluster..."
    
    aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME
    
    # Verify cluster connection
    if kubectl cluster-info &> /dev/null; then
        log_info "Successfully connected to EKS cluster."
    else
        log_error "Failed to connect to EKS cluster."
        exit 1
    fi
}

# Step 3: Install AWS Load Balancer Controller
install_alb_controller() {
    log_step "3. Installing AWS Load Balancer Controller..."
    
    # Install using Helm
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    # Get VPC ID from Terraform output
    VPC_ID=$(cd aws-infrastructure/terraform && terraform output -raw vpc_id)
    
    # Install AWS Load Balancer Controller
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName=$CLUSTER_NAME \
        --set serviceAccount.create=false \
        --set region=$AWS_REGION \
        --set vpcId=$VPC_ID
    
    log_info "AWS Load Balancer Controller installed!"
}

# Step 4: Create ECR Repositories
create_ecr_repositories() {
    log_step "4. Creating ECR repositories..."
    
    # Create repositories
    aws ecr create-repository --repository-name helpdesk-django --region $AWS_REGION 2>/dev/null || true
    aws ecr create-repository --repository-name helpdesk-ai --region $AWS_REGION 2>/dev/null || true
    aws ecr create-repository --repository-name helpdesk-realtime --region $AWS_REGION 2>/dev/null || true
    
    # Get login token
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    log_info "ECR repositories created!"
}

# Step 5: Build and Push Docker Images
build_and_push_images() {
    log_step "5. Building and pushing Docker images..."
    
    ECR_REGISTRY="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Build Django application
    log_info "Building Django application..."
    cd core
    docker build -t helpdesk-django .
    docker tag helpdesk-django:latest $ECR_REGISTRY/helpdesk-django:latest
    docker push $ECR_REGISTRY/helpdesk-django:latest
    cd ..
    
    # Build AI service
    log_info "Building AI service..."
    cd ai-service
    docker build -t helpdesk-ai .
    docker tag helpdesk-ai:latest $ECR_REGISTRY/helpdesk-ai:latest
    docker push $ECR_REGISTRY/helpdesk-ai:latest
    cd ..
    
    # Build Realtime service
    log_info "Building Realtime service..."
    cd realtime-service
    docker build -t helpdesk-realtime .
    docker tag helpdesk-realtime:latest $ECR_REGISTRY/helpdesk-realtime:latest
    docker push $ECR_REGISTRY/helpdesk-realtime:latest
    cd ..
    
    log_info "All Docker images built and pushed!"
}

# Step 6: Update Kubernetes Manifests
update_k8s_manifests() {
    log_step "6. Updating Kubernetes manifests with ECR images..."
    
    ECR_REGISTRY="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Update image references in Kubernetes manifests
    find aws-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-django:latest|$ECR_REGISTRY/helpdesk-django:latest|g" {} \;
    find aws-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-ai:latest|$ECR_REGISTRY/helpdesk-ai:latest|g" {} \;
    find aws-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-realtime:latest|$ECR_REGISTRY/helpdesk-realtime:latest|g" {} \;
    
    log_info "Kubernetes manifests updated!"
}

# Step 7: Deploy Application
deploy_application() {
    log_step "7. Deploying application to Kubernetes..."
    
    # Create namespace
    kubectl apply -f aws-infrastructure/k8s/namespace.yaml
    
    # Deploy configuration
    kubectl apply -f aws-infrastructure/k8s/configmap.yaml
    
    # Create secrets (you need to update these with your actual values)
    cat > temp-secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: helpdesk-secrets
  namespace: helpdesk
type: Opaque
data:
  SECRET_KEY: $(echo -n 'your-django-secret-key-change-this' | base64)
  DB_PASSWORD: $(echo -n 'your-db-password-change-this' | base64)
  REDIS_AUTH_TOKEN: $(echo -n 'your-redis-token-change-this' | base64)
  EMAIL_HOST_USER: $(echo -n 'your-email-user' | base64)
  EMAIL_HOST_PASSWORD: $(echo -n 'your-email-password' | base64)
  OPENAI_API_KEY: $(echo -n 'your-openai-key' | base64)
  ANTHROPIC_API_KEY: $(echo -n 'your-anthropic-key' | base64)
  AWS_ACCESS_KEY_ID: $(echo -n 'your-aws-access-key' | base64)
  AWS_SECRET_ACCESS_KEY: $(echo -n 'your-aws-secret-key' | base64)
  AWS_STORAGE_BUCKET_NAME: $(echo -n 'your-s3-bucket-name' | base64)
EOF
    
    kubectl apply -f temp-secrets.yaml
    rm temp-secrets.yaml
    
    # Deploy services
    kubectl apply -f aws-infrastructure/k8s/django-deployment.yaml
    kubectl apply -f aws-infrastructure/k8s/ai-service-deployment.yaml
    kubectl apply -f aws-infrastructure/k8s/realtime-service-deployment.yaml
    kubectl apply -f aws-infrastructure/k8s/celery-deployment.yaml
    
    # Deploy ingress
    kubectl apply -f aws-infrastructure/k8s/ingress.yaml
    
    log_info "Application deployed!"
}

# Step 8: Wait for Deployments
wait_for_deployments() {
    log_step "8. Waiting for deployments to be ready..."
    
    # Wait for all deployments
    kubectl rollout status deployment/django-app -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/ai-service -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/realtime-service -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/celery-worker -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/celery-beat -n $NAMESPACE --timeout=300s
    
    log_info "All deployments are ready!"
}

# Step 9: Run Database Migrations
run_migrations() {
    log_step "9. Running database migrations..."
    
    kubectl exec -n $NAMESPACE deployment/django-app -- python manage.py migrate
    kubectl exec -n $NAMESPACE deployment/django-app -- python manage.py collectstatic --noinput
    
    log_info "Database migrations completed!"
}

# Step 10: Show Deployment Information
show_deployment_info() {
    log_step "10. Deployment completed successfully!"
    
    echo ""
    echo "=== Deployment Information ==="
    echo "Cluster: $CLUSTER_NAME"
    echo "Namespace: $NAMESPACE"
    echo "Region: $AWS_REGION"
    echo ""
    
    # Get service information
    echo "=== Services ==="
    kubectl get services -n $NAMESPACE
    echo ""
    
    # Get pod information
    echo "=== Pods ==="
    kubectl get pods -n $NAMESPACE
    echo ""
    
    # Get ingress information
    echo "=== Ingress ==="
    kubectl get ingress -n $NAMESPACE
    echo ""
    
    # Get ALB DNS name
    ALB_DNS=$(kubectl get ingress helpdesk-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "Not ready yet")
    if [ "$ALB_DNS" != "Not ready yet" ] && [ ! -z "$ALB_DNS" ]; then
        echo "Application URL: http://$ALB_DNS"
        echo "Health Check: http://$ALB_DNS/health/"
    else
        echo "Load balancer is still being created. Check again in a few minutes."
    fi
    
    echo ""
    echo "=== Next Steps ==="
    echo "1. Update your secrets with actual values:"
    echo "   kubectl edit secret helpdesk-secrets -n $NAMESPACE"
    echo ""
    echo "2. Create a superuser:"
    echo "   kubectl exec -n $NAMESPACE deployment/django-app -- python manage.py createsuperuser"
    echo ""
    echo "3. Check application logs:"
    echo "   kubectl logs -n $NAMESPACE deployment/django-app"
    echo ""
    echo "4. Monitor your deployment:"
    echo "   kubectl get all -n $NAMESPACE"
}

# Main execution
main() {
    echo "🚀 Starting AWS Helpdesk Platform Deployment..."
    echo ""
    
    # Check prerequisites
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Execute deployment steps
    get_account_id
    deploy_infrastructure
    configure_kubectl
    install_alb_controller
    create_ecr_repositories
    build_and_push_images
    update_k8s_manifests
    deploy_application
    wait_for_deployments
    run_migrations
    show_deployment_info
    
    log_info "🎉 Deployment completed successfully!"
}

# Run main function
main "$@"
