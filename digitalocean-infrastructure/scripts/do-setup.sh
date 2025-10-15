#!/bin/bash

# DigitalOcean Setup Script for Helpdesk Platform
# This script sets up all prerequisites and deploys the infrastructure

set -e

# Configuration
DO_REGION="nyc3"
CLUSTER_NAME="helpdesk-cluster"
NAMESPACE="helpdesk"
NODE_SIZE="s-2vcpu-4gb"
NODE_COUNT=3

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

# Step 1: Install Prerequisites
install_prerequisites() {
    log_step "1. Installing prerequisites..."
    
    # Update package list
    sudo apt-get update
    
    # Install doctl (DigitalOcean CLI)
    if ! command -v doctl &> /dev/null; then
        log_info "Installing doctl..."
        wget https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz
        tar xf doctl-1.94.0-linux-amd64.tar.gz
        sudo mv doctl /usr/local/bin/
        rm doctl-1.94.0-linux-amd64.tar.gz
    else
        log_info "doctl already installed: $(doctl version)"
    fi
    
    # Install kubectl
    if ! command -v kubectl &> /dev/null; then
        log_info "Installing kubectl..."
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    else
        log_info "kubectl already installed: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
    fi
    
    # Install Helm
    if ! command -v helm &> /dev/null; then
        log_info "Installing Helm..."
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    else
        log_info "Helm already installed: $(helm version --short)"
    fi
    
    # Install Terraform
    if ! command -v terraform &> /dev/null; then
        log_info "Installing Terraform..."
        wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
        unzip terraform_1.6.0_linux_amd64.zip
        sudo mv terraform /usr/local/bin/
        rm terraform_1.6.0_linux_amd64.zip
    else
        log_info "Terraform already installed: $(terraform version -json | jq -r '.terraform_version')"
    fi
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker..."
        sudo apt-get install -y docker.io
        sudo usermod -aG docker $USER
        log_warn "Please log out and log back in for Docker group changes to take effect"
    else
        log_info "Docker already installed: $(docker --version)"
    fi
    
    # Install jq
    if ! command -v jq &> /dev/null; then
        log_info "Installing jq..."
        sudo apt-get install -y jq
    else
        log_info "jq already installed: $(jq --version)"
    fi
    
    log_info "Prerequisites installation completed!"
}

# Step 2: DigitalOcean Authentication
do_auth() {
    log_step "2. DigitalOcean authentication..."
    
    # Check if already authenticated
    if doctl account get &> /dev/null; then
        log_info "Already authenticated to DigitalOcean"
        doctl account get
    else
        log_info "Please authenticate to DigitalOcean..."
        echo "You need a DigitalOcean API token. Get it from: https://cloud.digitalocean.com/account/api/tokens"
        read -p "Enter your DigitalOcean API token: " DO_TOKEN
        
        # Set the token
        doctl auth init -t "$DO_TOKEN"
        
        # Verify authentication
        if doctl account get &> /dev/null; then
            log_info "Successfully authenticated to DigitalOcean"
            doctl account get
        else
            log_error "Failed to authenticate to DigitalOcean"
            exit 1
        fi
    fi
}

# Step 3: Deploy Infrastructure with Terraform
deploy_infrastructure() {
    log_step "3. Deploying DigitalOcean infrastructure with Terraform..."
    
    cd digitalocean-infrastructure/terraform
    
    # Create terraform.tfvars if it doesn't exist
    if [ ! -f "terraform.tfvars" ]; then
        cat > terraform.tfvars << EOF
do_token = "$(doctl auth list -o json | jq -r '.[0].access_token')"
region = "$DO_REGION"
environment = "production"
cluster_name = "$CLUSTER_NAME"
node_count = $NODE_COUNT
node_size = "$NODE_SIZE"
alert_email = "admin@your-domain.com"
EOF
        log_warn "Created terraform.tfvars. Please update with your actual values."
    fi
    
    # Initialize Terraform
    terraform init
    
    # Plan the infrastructure
    terraform plan
    
    # Apply the infrastructure
    terraform apply -auto-approve
    
    log_info "Infrastructure deployed successfully!"
}

# Step 4: Configure Kubernetes
configure_k8s() {
    log_step "4. Configuring Kubernetes cluster..."
    
    # Get cluster credentials
    doctl kubernetes cluster kubeconfig save $CLUSTER_NAME
    
    # Verify cluster connection
    if kubectl cluster-info &> /dev/null; then
        log_info "Successfully connected to Kubernetes cluster"
        kubectl get nodes
    else
        log_error "Failed to connect to Kubernetes cluster"
        exit 1
    fi
}

# Step 5: Install NGINX Ingress Controller
install_ingress() {
    log_step "5. Installing NGINX Ingress Controller..."
    
    # Add Helm repository
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # Install NGINX Ingress Controller
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --set controller.service.annotations."service\.beta\.kubernetes\.io/do-loadbalancer-name"=helpdesk-ingress-lb
    
    log_info "NGINX Ingress Controller installed!"
}

# Step 6: Install Redis
install_redis() {
    log_step "6. Installing Redis..."
    
    # Add Bitnami Helm repository
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    
    # Install Redis
    helm install redis bitnami/redis \
        --namespace $NAMESPACE \
        --create-namespace \
        --set auth.enabled=false \
        --set master.persistence.size=1Gi \
        --set replica.persistence.size=1Gi
    
    log_info "Redis installed!"
}

# Step 7: Build and Push Docker Images
build_and_push_images() {
    log_step "7. Building and pushing Docker images to DigitalOcean Container Registry..."
    
    # Get registry endpoint
    REGISTRY_ENDPOINT=$(doctl registry get -o json | jq -r '.[0].endpoint')
    
    # Login to registry
    doctl registry login
    
    # Build Django application
    log_info "Building Django application..."
    cd core
    docker build -t $REGISTRY_ENDPOINT/helpdesk-django:latest .
    docker push $REGISTRY_ENDPOINT/helpdesk-django:latest
    cd ..
    
    # Build AI service
    log_info "Building AI service..."
    cd ai-service
    docker build -t $REGISTRY_ENDPOINT/helpdesk-ai:latest .
    docker push $REGISTRY_ENDPOINT/helpdesk-ai:latest
    cd ..
    
    # Build Realtime service
    log_info "Building Realtime service..."
    cd realtime-service
    docker build -t $REGISTRY_ENDPOINT/helpdesk-realtime:latest .
    docker push $REGISTRY_ENDPOINT/helpdesk-realtime:latest
    cd ..
    
    log_info "All Docker images built and pushed to DigitalOcean Container Registry!"
}

# Step 8: Update Kubernetes Manifests
update_k8s_manifests() {
    log_step "8. Updating Kubernetes manifests with registry images..."
    
    REGISTRY_ENDPOINT=$(doctl registry get -o json | jq -r '.[0].endpoint')
    
    # Update image references in Kubernetes manifests
    find digitalocean-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-django:latest|$REGISTRY_ENDPOINT/helpdesk-django:latest|g" {} \;
    find digitalocean-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-ai:latest|$REGISTRY_ENDPOINT/helpdesk-ai:latest|g" {} \;
    find digitalocean-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-realtime:latest|$REGISTRY_ENDPOINT/helpdesk-realtime:latest|g" {} \;
    
    log_info "Kubernetes manifests updated!"
}

# Step 9: Deploy Application
deploy_application() {
    log_step "9. Deploying application to Kubernetes..."
    
    # Create namespace
    kubectl apply -f digitalocean-infrastructure/k8s/namespace.yaml
    
    # Deploy configuration
    kubectl apply -f digitalocean-infrastructure/k8s/do-configmap.yaml
    
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
  EMAIL_HOST_USER: $(echo -n 'your-email-user' | base64)
  EMAIL_HOST_PASSWORD: $(echo -n 'your-email-password' | base64)
  AWS_ACCESS_KEY_ID: $(echo -n 'your-spaces-access-key' | base64)
  AWS_SECRET_ACCESS_KEY: $(echo -n 'your-spaces-secret-key' | base64)
  OPENAI_API_KEY: $(echo -n 'your-openai-key' | base64)
  ANTHROPIC_API_KEY: $(echo -n 'your-anthropic-key' | base64)
EOF
    
    kubectl apply -f temp-secrets.yaml
    rm temp-secrets.yaml
    
    # Deploy services
    kubectl apply -f digitalocean-infrastructure/k8s/django-deployment.yaml
    kubectl apply -f digitalocean-infrastructure/k8s/ai-service-deployment.yaml
    kubectl apply -f digitalocean-infrastructure/k8s/realtime-service-deployment.yaml
    kubectl apply -f digitalocean-infrastructure/k8s/celery-deployment.yaml
    
    # Deploy ingress
    kubectl apply -f digitalocean-infrastructure/k8s/ingress.yaml
    
    log_info "Application deployed!"
}

# Step 10: Wait for Deployments
wait_for_deployments() {
    log_step "10. Waiting for deployments to be ready..."
    
    # Wait for all deployments
    kubectl rollout status deployment/django-app -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/ai-service -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/realtime-service -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/celery-worker -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/celery-beat -n $NAMESPACE --timeout=300s
    
    log_info "All deployments are ready!"
}

# Step 11: Run Database Migrations
run_migrations() {
    log_step "11. Running database migrations..."
    
    kubectl exec -n $NAMESPACE deployment/django-app -- python manage.py migrate
    kubectl exec -n $NAMESPACE deployment/django-app -- python manage.py collectstatic --noinput
    
    log_info "Database migrations completed!"
}

# Step 12: Show Deployment Information
show_deployment_info() {
    log_step "12. Deployment completed successfully!"
    
    echo ""
    echo "=== Deployment Information ==="
    echo "Cluster: $CLUSTER_NAME"
    echo "Namespace: $NAMESPACE"
    echo "Region: $DO_REGION"
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
    
    # Get external IP
    EXTERNAL_IP=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Not ready yet")
    if [ "$EXTERNAL_IP" != "Not ready yet" ] && [ ! -z "$EXTERNAL_IP" ]; then
        echo "Application URL: http://$EXTERNAL_IP"
        echo "Health Check: http://$EXTERNAL_IP/health/"
    else
        echo "Load balancer is still being created. Check again in a few minutes."
    fi
    
    echo ""
    echo "=== Cost Information ==="
    echo "Estimated monthly cost: $140-200"
    echo "- Kubernetes cluster: ~$60 (3 nodes x $20)"
    echo "- Database: ~$60 (db-s-2vcpu-4gb)"
    echo "- Load balancer: ~$12"
    echo "- Spaces storage: ~$5-20"
    echo "- Container registry: ~$5"
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
    echo ""
    echo "5. Access DigitalOcean Dashboard:"
    echo "   https://cloud.digitalocean.com"
}

# Main execution
main() {
    echo "🚀 Starting DigitalOcean Helpdesk Platform Deployment..."
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_error "Please don't run this script as root"
        exit 1
    fi
    
    # Execute deployment steps
    install_prerequisites
    do_auth
    deploy_infrastructure
    configure_k8s
    install_ingress
    install_redis
    build_and_push_images
    update_k8s_manifests
    deploy_application
    wait_for_deployments
    run_migrations
    show_deployment_info
    
    log_info "🎉 DigitalOcean deployment completed successfully!"
}

# Run main function
main "$@"
