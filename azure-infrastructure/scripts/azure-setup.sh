#!/bin/bash

# Azure Setup Script for Helpdesk Platform
# This script sets up all prerequisites and deploys the infrastructure

set -e

# Configuration
AZURE_REGION="East US"
RESOURCE_GROUP="helpdesk-production-rg"
CLUSTER_NAME="helpdesk-cluster"
ACR_NAME="helpdeskproductionacr"
NAMESPACE="helpdesk"

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
    
    # Install Azure CLI
    if ! command -v az &> /dev/null; then
        log_info "Installing Azure CLI..."
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    else
        log_info "Azure CLI already installed: $(az --version | head -n1)"
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

# Step 2: Azure Login and Setup
azure_login() {
    log_step "2. Azure login and setup..."
    
    # Check if already logged in
    if az account show &> /dev/null; then
        log_info "Already logged in to Azure"
        az account show
    else
        log_info "Please login to Azure..."
        az login
        
        # Set default subscription if multiple exist
        SUBSCRIPTIONS=$(az account list --query "[].{Name:name, Id:id}" -o table)
        if [ $(echo "$SUBSCRIPTIONS" | wc -l) -gt 2 ]; then
            log_info "Available subscriptions:"
            echo "$SUBSCRIPTIONS"
            read -p "Enter subscription ID: " SUBSCRIPTION_ID
            az account set --subscription "$SUBSCRIPTION_ID"
        fi
    fi
    
    # Get subscription info
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    TENANT_ID=$(az account show --query tenantId -o tsv)
    
    log_info "Subscription ID: $SUBSCRIPTION_ID"
    log_info "Tenant ID: $TENANT_ID"
}

# Step 3: Create Service Principal
create_service_principal() {
    log_step "3. Creating service principal..."
    
    # Check if service principal already exists
    SP_NAME="helpdesk-platform-sp"
    if az ad sp show --id "http://$SP_NAME" &> /dev/null; then
        log_info "Service principal already exists"
    else
        log_info "Creating service principal..."
        az ad sp create-for-rbac --name "$SP_NAME" --role Contributor --scopes "/subscriptions/$SUBSCRIPTION_ID"
    fi
    
    # Get service principal credentials
    SP_CREDENTIALS=$(az ad sp create-for-rbac --name "$SP_NAME" --role Contributor --scopes "/subscriptions/$SUBSCRIPTION_ID" --sdk-auth)
    
    log_info "Service principal created successfully!"
    log_warn "Please save these credentials securely:"
    echo "$SP_CREDENTIALS"
}

# Step 4: Deploy Infrastructure with Terraform
deploy_infrastructure() {
    log_step "4. Deploying Azure infrastructure with Terraform..."
    
    cd azure-infrastructure/terraform
    
    # Create terraform.tfvars if it doesn't exist
    if [ ! -f "terraform.tfvars" ]; then
        cat > terraform.tfvars << EOF
location = "$AZURE_REGION"
environment = "production"
cluster_name = "$CLUSTER_NAME"
node_count = 3
vm_size = "Standard_D2s_v3"
db_password = "$(openssl rand -base64 32)"
EOF
        log_warn "Created terraform.tfvars with random passwords. Please update with your actual values."
    fi
    
    # Initialize Terraform
    terraform init
    
    # Plan the infrastructure
    terraform plan
    
    # Apply the infrastructure
    terraform apply -auto-approve
    
    log_info "Infrastructure deployed successfully!"
}

# Step 5: Configure AKS
configure_aks() {
    log_step "5. Configuring AKS cluster..."
    
    # Get AKS credentials
    az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME
    
    # Verify cluster connection
    if kubectl cluster-info &> /dev/null; then
        log_info "Successfully connected to AKS cluster"
        kubectl get nodes
    else
        log_error "Failed to connect to AKS cluster"
        exit 1
    fi
}

# Step 6: Install Azure Load Balancer Controller
install_alb_controller() {
    log_step "6. Installing Azure Load Balancer Controller..."
    
    # Add Helm repositories
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # Install NGINX Ingress Controller
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
    
    log_info "Azure Load Balancer Controller installed!"
}

# Step 7: Build and Push Docker Images
build_and_push_images() {
    log_step "7. Building and pushing Docker images to Azure Container Registry..."
    
    # Get ACR login server
    ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
    
    # Login to ACR
    az acr login --name $ACR_NAME
    
    # Build Django application
    log_info "Building Django application..."
    cd core
    docker build -t $ACR_LOGIN_SERVER/helpdesk-django:latest .
    docker push $ACR_LOGIN_SERVER/helpdesk-django:latest
    cd ..
    
    # Build AI service
    log_info "Building AI service..."
    cd ai-service
    docker build -t $ACR_LOGIN_SERVER/helpdesk-ai:latest .
    docker push $ACR_LOGIN_SERVER/helpdesk-ai:latest
    cd ..
    
    # Build Realtime service
    log_info "Building Realtime service..."
    cd realtime-service
    docker build -t $ACR_LOGIN_SERVER/helpdesk-realtime:latest .
    docker push $ACR_LOGIN_SERVER/helpdesk-realtime:latest
    cd ..
    
    log_info "All Docker images built and pushed to ACR!"
}

# Step 8: Update Kubernetes Manifests
update_k8s_manifests() {
    log_step "8. Updating Kubernetes manifests with ACR images..."
    
    ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
    
    # Update image references in Kubernetes manifests
    find azure-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-django:latest|$ACR_LOGIN_SERVER/helpdesk-django:latest|g" {} \;
    find azure-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-ai:latest|$ACR_LOGIN_SERVER/helpdesk-ai:latest|g" {} \;
    find azure-infrastructure/k8s -name "*.yaml" -exec sed -i "s|your-registry/helpdesk-realtime:latest|$ACR_LOGIN_SERVER/helpdesk-realtime:latest|g" {} \;
    
    log_info "Kubernetes manifests updated!"
}

# Step 9: Deploy Application
deploy_application() {
    log_step "9. Deploying application to AKS..."
    
    # Create namespace
    kubectl apply -f azure-infrastructure/k8s/namespace.yaml
    
    # Deploy configuration
    kubectl apply -f azure-infrastructure/k8s/azure-configmap.yaml
    
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
  MICROSOFT_GRAPH_CLIENT_ID: $(echo -n 'your-graph-client-id' | base64)
  MICROSOFT_GRAPH_CLIENT_SECRET: $(echo -n 'your-graph-client-secret' | base64)
  MICROSOFT_GRAPH_TENANT_ID: $(echo -n 'your-graph-tenant-id' | base64)
  APPLICATION_INSIGHTS_KEY: $(echo -n 'your-insights-key' | base64)
  TEAMS_WEBHOOK_URL: $(echo -n 'your-teams-webhook' | base64)
  AZURE_STORAGE_ACCOUNT_KEY: $(echo -n 'your-storage-key' | base64)
EOF
    
    kubectl apply -f temp-secrets.yaml
    rm temp-secrets.yaml
    
    # Deploy services
    kubectl apply -f azure-infrastructure/k8s/django-deployment.yaml
    kubectl apply -f azure-infrastructure/k8s/ai-service-deployment.yaml
    kubectl apply -f azure-infrastructure/k8s/realtime-service-deployment.yaml
    kubectl apply -f azure-infrastructure/k8s/celery-deployment.yaml
    
    # Deploy ingress
    kubectl apply -f azure-infrastructure/k8s/ingress.yaml
    
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
    echo "Resource Group: $RESOURCE_GROUP"
    echo "Cluster: $CLUSTER_NAME"
    echo "Namespace: $NAMESPACE"
    echo "Region: $AZURE_REGION"
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
    echo "5. Access Azure Portal:"
    echo "   https://portal.azure.com"
}

# Main execution
main() {
    echo "🚀 Starting Azure Helpdesk Platform Deployment..."
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_error "Please don't run this script as root"
        exit 1
    fi
    
    # Execute deployment steps
    install_prerequisites
    azure_login
    create_service_principal
    deploy_infrastructure
    configure_aks
    install_alb_controller
    build_and_push_images
    update_k8s_manifests
    deploy_application
    wait_for_deployments
    run_migrations
    show_deployment_info
    
    log_info "🎉 Azure deployment completed successfully!"
}

# Run main function
main "$@"
